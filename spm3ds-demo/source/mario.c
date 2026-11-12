#include "mario.h"
#include <tex3ds.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MARIO_TEX 128

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

static bool loaded;
static Header h;
static Batch* batches;
static Vertex* vbo;
static u16* idx;
static C3D_Tex tex[MARIO_TEX];
static bool texOk[MARIO_TEX];

bool mario_loaded(void) { return loaded; }

void mario_free(void)
{
	for (int i = 0; i < MARIO_TEX; i++)
		if (texOk[i]) C3D_TexDelete(&tex[i]);
	memset(texOk, 0, sizeof texOk);
	free(batches); batches = NULL;
	if (vbo) linearFree(vbo);
	if (idx) linearFree(idx);
	vbo = NULL; idx = NULL;
	loaded = false;
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
	for (u32 i = 0; i < h.nTex && i < MARIO_TEX; i++) {
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
	loaded = true;
	return true;
}

DrawStats mario_draw(const C3D_Mtx* proj, const C3D_Mtx* camView, const float pos[3], float billboardYaw, float sx, float scale)
{
	DrawStats st = { 0, 0 };
	if (!loaded) return st;
	C3D_Mtx m = *camView;
	Mtx_Translate(&m, pos[0], pos[1], pos[2], true);
	Mtx_RotateY(&m, billboardYaw, true);
	Mtx_Scale(&m, sx * scale, scale, scale);
	gfx_set_matrices(proj, &m);
	gfx_bind_vbo(vbo);
	gfx_set_cull(CULL_NONE);          // paper: visible from both sides (also needed while mirrored)
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
