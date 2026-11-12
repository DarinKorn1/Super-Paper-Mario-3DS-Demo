#include "mario.h"
#include <tex3ds.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>

#define MARIO_TEX 128

// ---- static pose (mario.spm, fallback) -------------------------------------------------------------------
typedef struct {
	s32 tex;
	u32 first, count;
	u8 cull, wrapS, wrapT, blend;
	u32 reserved;
} Batch;

typedef struct {
	char magic[4];
	u32 version, nTex, nVerts, nBatches, nIdx;
	float bbox[6];
} Header;

// ---- baked animations (mario_anim.bin, see tools/convert_mario_anim.py) ----------------------------------
typedef struct { s32 tex; u32 first, count, pad0, pad1; } ABatch;       // 20 bytes
typedef struct {
	u32 nBatches, nIdx;
	const ABatch* batches;
	const u16* idx;
	const s16* pos;               // nPool x {x, y, z, 0}, model units * 64
} AFrame;
typedef struct { char name[16]; u32 nFrames, loop; AFrame* frames; } AAnim;

#define MAX_ANIMS 4
static u8* animBuf;
static AAnim anims[MAX_ANIMS];
static u32 nAnims, nPool, maxIdx;
static float sampleStep = 2.0f;
static Vertex* poolVbo;           // linear: pool vertices, positions rewritten every frame
static u16* poolIdx;              // linear: index list of the frame being drawn

static bool loaded;
static Header h;
static Batch* batches;
static Vertex* vbo;
static u16* idx;
static C3D_Tex tex[MARIO_TEX];
static bool texOk[MARIO_TEX];

bool mario_loaded(void) { return loaded; }
int mario_anim_count(void) { return (int)nAnims; }

void mario_free(void)
{
	for (int i = 0; i < MARIO_TEX; i++)
		if (texOk[i]) C3D_TexDelete(&tex[i]);
	memset(texOk, 0, sizeof texOk);
	free(batches); batches = NULL;
	if (vbo) linearFree(vbo);
	if (idx) linearFree(idx);
	vbo = NULL; idx = NULL;
	for (u32 i = 0; i < nAnims; i++) free(anims[i].frames);
	free(animBuf); animBuf = NULL;
	if (poolVbo) linearFree(poolVbo);
	if (poolIdx) linearFree(poolIdx);
	poolVbo = NULL; poolIdx = NULL;
	nAnims = nPool = maxIdx = 0;
	loaded = false;
}

static bool load_anim(const char* path)
{
	FILE* f = fopen(path, "rb");
	if (!f) return false;
	fseek(f, 0, SEEK_END);
	long size = ftell(f);
	fseek(f, 0, SEEK_SET);
	if (size < 64 || size > 8 * 1024 * 1024) { fclose(f); return false; }
	animBuf = malloc(size + 4);
	if (!animBuf || fread(animBuf, 1, size, f) != (size_t)size) { fclose(f); free(animBuf); animBuf = NULL; return false; }
	fclose(f);
	const u8* p = animBuf;
	const u8* end = animBuf + size;
	u32 ver, na, nAlpha;
	memcpy(&ver, p + 4, 4); memcpy(&na, p + 8, 4); memcpy(&nPool, p + 12, 4);
	memcpy(&sampleStep, p + 16, 4); memcpy(&nAlpha, p + 20, 4);
	if (memcmp(p, "SPMA", 4) != 0 || ver != 1 || na == 0 || na > MAX_ANIMS || nPool == 0 || nPool > 4096) goto bad;
	p += 24 + 4 * nAlpha;
	poolVbo = linearAlloc(sizeof(Vertex) * nPool);
	if (!poolVbo) goto bad;
	for (u32 i = 0; i < nPool; i++, p += 8) {
		s16 uv[2];
		memcpy(uv, p, 4);
		poolVbo[i].x = poolVbo[i].y = poolVbo[i].z = poolVbo[i].pad = 0;
		poolVbo[i].u = uv[0]; poolVbo[i].v = uv[1];
		poolVbo[i].r = p[4]; poolVbo[i].g = p[5]; poolVbo[i].b = p[6]; poolVbo[i].a = p[7];
	}
	for (u32 a = 0; a < na; a++) {
		if (p + 24 > end) goto bad;
		AAnim* an = &anims[a];
		memcpy(an->name, p, 16);
		an->name[15] = 0;
		memcpy(&an->nFrames, p + 16, 4); memcpy(&an->loop, p + 20, 4);
		p += 24;
		if (an->nFrames == 0 || an->nFrames > 2000) goto bad;
		an->frames = calloc(an->nFrames, sizeof(AFrame));
		if (!an->frames) goto bad;
		nAnims = a + 1;
		for (u32 fr = 0; fr < an->nFrames; fr++) {
			AFrame* f2 = &an->frames[fr];
			if (p + 8 > end) goto bad;
			memcpy(&f2->nBatches, p, 4); memcpy(&f2->nIdx, p + 4, 4);
			p += 8;
			f2->batches = (const ABatch*)p;
			p += f2->nBatches * sizeof(ABatch);
			f2->idx = (const u16*)p;
			p += ((f2->nIdx + 1) & ~1u) * 2;
			f2->pos = (const s16*)p;
			p += nPool * 8;
			if (p > end) goto bad;
			if (f2->nIdx > maxIdx) maxIdx = f2->nIdx;
		}
	}
	poolIdx = linearAlloc(sizeof(u16) * (maxIdx ? maxIdx : 1));
	if (!poolIdx) goto bad;
	return true;
bad:
	for (u32 i = 0; i < nAnims; i++) { free(anims[i].frames); anims[i].frames = NULL; }
	nAnims = 0;
	free(animBuf); animBuf = NULL;
	if (poolVbo) linearFree(poolVbo);
	poolVbo = NULL;
	return false;
}

bool mario_load(const char* dir, char* err, size_t errSize)
{
	char path[256];
	mario_free();
	snprintf(path, sizeof path, "%smario.spm", dir);
	FILE* f = fopen(path, "rb");
	if (!f) { snprintf(err, errSize, "cannot open %s", path); return false; }
	if (fread(&h, sizeof h, 1, f) != 1 || memcmp(h.magic, "SPMR", 4) != 0 || h.version != 1) {
		snprintf(err, errSize, "bad header in %s", path); fclose(f); return false;
	}
	batches = malloc(sizeof(Batch) * (h.nBatches ? h.nBatches : 1));
	vbo = linearAlloc(sizeof(Vertex) * (h.nVerts ? h.nVerts : 1));
	idx = linearAlloc(sizeof(u16) * (h.nIdx ? h.nIdx : 1));
	if (!batches || !vbo || !idx) { snprintf(err, errSize, "out of memory"); fclose(f); mario_free(); return false; }
	bool ok = fread(batches, sizeof(Batch), h.nBatches, f) == h.nBatches &&
	          fread(vbo, sizeof(Vertex), h.nVerts, f) == h.nVerts &&
	          fread(idx, sizeof(u16), h.nIdx, f) == h.nIdx;
	fclose(f);
	if (!ok) { snprintf(err, errSize, "%s is truncated", path); mario_free(); return false; }
	GSPGPU_FlushDataCache(vbo, sizeof(Vertex) * h.nVerts);
	GSPGPU_FlushDataCache(idx, sizeof(u16) * h.nIdx);
	for (u32 i = 0; i < MARIO_TEX; i++) {
		snprintf(path, sizeof path, "%stextures/mario_%03lu.t3x", dir, (unsigned long)i);
		FILE* tf = fopen(path, "rb");
		if (!tf) continue;
		Tex3DS_Texture t = Tex3DS_TextureImportStdio(tf, &tex[i], NULL, false);
		fclose(tf);
		if (t) {
			Tex3DS_TextureFree(t);
			C3D_TexSetFilter(&tex[i], GPU_LINEAR, GPU_LINEAR);   // the TPL says bilinear
			C3D_TexSetWrap(&tex[i], GPU_CLAMP_TO_EDGE, GPU_CLAMP_TO_EDGE);
			texOk[i] = true;
		}
	}
	snprintf(path, sizeof path, "%smario_anim.bin", dir);
	if (!load_anim(path))
		snprintf(err, errSize, "no animations (mario_anim.bin)");
	loaded = true;
	return true;
}

static void setup_draw(const C3D_Mtx* proj, const C3D_Mtx* camView, const float pos[3], float billboardYaw, float sx, float scale)
{
	C3D_Mtx m = *camView;
	Mtx_Translate(&m, pos[0], pos[1], pos[2], true);
	Mtx_RotateY(&m, billboardYaw, true);
	Mtx_Scale(&m, sx * scale, scale, scale);
	gfx_set_matrices(proj, &m);
	gfx_set_cull(CULL_NONE);          // paper: visible from both sides (also needed while mirrored)
}

static DrawStats draw_static(void)
{
	DrawStats st = { 0, 0 };
	gfx_bind_vbo(vbo);
	for (int pass = 0; pass < 2; pass++) {
		C3D_AlphaTest(true, GPU_GREATER, pass ? 0x10 : 0x80);
		for (u32 i = 0; i < h.nBatches; i++) {
			const Batch* b = &batches[i];
			if ((b->blend != 0) != (pass == 1)) continue;
			bool textured = b->tex >= 0 && b->tex < MARIO_TEX && texOk[b->tex];
			gfx_set_textured(textured);
			if (textured) C3D_TexBind(0, &tex[b->tex]);
			C3D_DrawElements(GPU_TRIANGLES, b->count, C3D_UNSIGNED_SHORT, idx + b->first);
			st.calls++;
			st.tris += b->count / 3;
		}
	}
	C3D_AlphaTest(false, GPU_ALWAYS, 0);
	return st;
}

DrawStats mario_draw(const C3D_Mtx* proj, const C3D_Mtx* camView, const float pos[3], float billboardYaw, float sx,
                     float scale, int anim, float time60)
{
	DrawStats st = { 0, 0 };
	if (!loaded) return st;
	setup_draw(proj, camView, pos, billboardYaw, sx, scale);
	if (anim < 0 || anim >= (int)nAnims || !poolVbo)
		return draw_static();

	const AAnim* an = &anims[anim];
	float fpos = time60 / sampleStep;
	if (an->loop) {
		fpos = fmodf(fpos, (float)an->nFrames);
		if (fpos < 0) fpos += (float)an->nFrames;
	} else if (fpos > (float)(an->nFrames - 1)) {
		fpos = (float)(an->nFrames - 1);
	}
	u32 f0 = (u32)fpos;
	if (f0 >= an->nFrames) f0 = an->nFrames - 1;
	u32 f1 = f0 + 1;
	if (f1 >= an->nFrames) f1 = an->loop ? 0 : f0;
	float t = fpos - (float)f0;
	const AFrame* a = &an->frames[f0];
	const AFrame* b = &an->frames[f1];
	for (u32 i = 0; i < nPool; i++) {
		poolVbo[i].x = (s16)(a->pos[i * 4 + 0] + (b->pos[i * 4 + 0] - a->pos[i * 4 + 0]) * t);
		poolVbo[i].y = (s16)(a->pos[i * 4 + 1] + (b->pos[i * 4 + 1] - a->pos[i * 4 + 1]) * t);
		poolVbo[i].z = (s16)(a->pos[i * 4 + 2] + (b->pos[i * 4 + 2] - a->pos[i * 4 + 2]) * t);
	}
	GSPGPU_FlushDataCache(poolVbo, sizeof(Vertex) * nPool);
	memcpy(poolIdx, a->idx, sizeof(u16) * a->nIdx);
	GSPGPU_FlushDataCache(poolIdx, sizeof(u16) * a->nIdx);

	gfx_bind_vbo(poolVbo);
	C3D_AlphaTest(true, GPU_GREATER, 0x60);       // all of Mario's textures are cut-outs with soft edges
	for (u32 i = 0; i < a->nBatches; i++) {
		const ABatch* bt = &a->batches[i];
		bool textured = bt->tex >= 0 && bt->tex < MARIO_TEX && texOk[bt->tex];
		gfx_set_textured(textured);
		if (textured) C3D_TexBind(0, &tex[bt->tex]);
		C3D_DrawElements(GPU_TRIANGLES, bt->count, C3D_UNSIGNED_SHORT, poolIdx + bt->first);
		st.calls++;
		st.tris += bt->count / 3;
	}
	C3D_AlphaTest(false, GPU_ALWAYS, 0);
	return st;
}
