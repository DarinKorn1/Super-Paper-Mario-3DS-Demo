#include "room.h"
#include <tex3ds.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_TEX 256

typedef struct {
	s32 tex;                 // texture number, or -1 = untextured
	u32 first, count;        // range in the index buffer
	u8 cull, wrapS, wrapT;   // cull = value from the game file (meaning not decoded yet, see notes)
	u8 blend;                // 1 = texture or material has alpha
	u32 reserved;
} Batch;                     // 20 bytes, same as the converter writes

typedef struct {
	char magic[4];
	u32 version, nTex, nVerts, nBatches, nIdx;
	float bbox[6];           // min xyz, max xyz in world units
} Header;                    // 48 bytes

typedef struct {
	bool loaded;
	Header h;
	Batch* batches;
	Vertex* vbo;             // linear memory (GPU readable)
	u16* idx;                // linear memory
} Part;

static Part parts[2];        // 0 = main, 1 = oku
static C3D_Tex tex[MAX_TEX];
static bool texOk[MAX_TEX];
static u32 texCount, texMissing;

static const GPU_TEXTURE_WRAP_PARAM wrapMap[3] = { GPU_CLAMP_TO_EDGE, GPU_REPEAT, GPU_MIRRORED_REPEAT };

static bool read_part(Part* p, const char* path, char* err, size_t errSize)
{
	FILE* f = fopen(path, "rb");
	if (!f) {
		snprintf(err, errSize, "cannot open %s", path);
		return false;
	}
	bool ok = fread(&p->h, sizeof(Header), 1, f) == 1 && memcmp(p->h.magic, "SPMR", 4) == 0 && p->h.version == 1;
	if (!ok) {
		snprintf(err, errSize, "bad header in %s", path);
		fclose(f);
		return false;
	}
	p->batches = malloc(sizeof(Batch) * (p->h.nBatches ? p->h.nBatches : 1));
	p->vbo = linearAlloc(sizeof(Vertex) * (p->h.nVerts ? p->h.nVerts : 1));
	p->idx = linearAlloc(sizeof(u16) * (p->h.nIdx ? p->h.nIdx : 1));
	if (!p->batches || !p->vbo || !p->idx) {
		snprintf(err, errSize, "out of memory for %s", path);
		fclose(f);
		return false;
	}
	ok = fread(p->batches, sizeof(Batch), p->h.nBatches, f) == p->h.nBatches &&
	     fread(p->vbo, sizeof(Vertex), p->h.nVerts, f) == p->h.nVerts &&
	     fread(p->idx, sizeof(u16), p->h.nIdx, f) == p->h.nIdx;
	fclose(f);
	if (!ok) {
		snprintf(err, errSize, "%s is truncated", path);
		return false;
	}
	GSPGPU_FlushDataCache(p->vbo, sizeof(Vertex) * p->h.nVerts);
	GSPGPU_FlushDataCache(p->idx, sizeof(u16) * p->h.nIdx);
	p->loaded = true;
	return true;
}

bool room_load(const char* dir, char* err, size_t errSize)
{
	char path[256];
	room_free();
	snprintf(path, sizeof path, "%sroom_main.spm", dir);
	if (!read_part(&parts[0], path, err, errSize))
		return false;
	snprintf(path, sizeof path, "%sroom_oku.spm", dir);
	if (!read_part(&parts[1], path, err, errSize))
		return false;

	texCount = parts[0].h.nTex < MAX_TEX ? parts[0].h.nTex : MAX_TEX;
	texMissing = 0;
	for (u32 i = 0; i < texCount; i++) {
		snprintf(path, sizeof path, "%stextures/tex_%03lu.t3x", dir, (unsigned long)i);
		FILE* f = fopen(path, "rb");
		texOk[i] = false;
		if (f) {
			Tex3DS_Texture t = Tex3DS_TextureImportStdio(f, &tex[i], NULL, false);
			fclose(f);
			if (t) {
				Tex3DS_TextureFree(t);
				C3D_TexSetFilter(&tex[i], GPU_LINEAR, GPU_LINEAR);
				texOk[i] = true;
			}
		}
		if (!texOk[i])
			texMissing++;   // unused textures are simply not converted; batches using them draw untextured
	}
	return true;
}

void room_free(void)
{
	for (u32 i = 0; i < texCount; i++)
		if (texOk[i])
			C3D_TexDelete(&tex[i]);
	texCount = texMissing = 0;
	memset(texOk, 0, sizeof texOk);
	for (int i = 0; i < 2; i++) {
		free(parts[i].batches);
		if (parts[i].vbo) linearFree(parts[i].vbo);
		if (parts[i].idx) linearFree(parts[i].idx);
		memset(&parts[i], 0, sizeof parts[i]);
	}
}

void room_start_position(float pos[3])
{
	// Look at the room from the front: centre in x, a little above the ground, in front of the nearest z.
	float zmax = parts[0].loaded ? parts[0].h.bbox[5] : 0.0f;
	pos[0] = 0.0f;
	pos[1] = 20.0f;
	pos[2] = zmax + 60.0f;
}

void room_counts(u32* mainTris, u32* okuTris, u32* textures, u32* texturesMissing)
{
	*mainTris = parts[0].h.nIdx / 3;
	*okuTris = parts[1].h.nIdx / 3;
	*textures = texCount;
	*texturesMissing = texMissing;
}

static void draw_pass(const Part* p, bool blendPass, CullMode cull, DrawStats* st)
{
	if (!p->loaded)
		return;
	gfx_bind_vbo(p->vbo);
	for (u32 i = 0; i < p->h.nBatches; i++) {
		const Batch* b = &p->batches[i];
		if ((b->blend != 0) != blendPass)
			continue;
		bool textured = b->tex >= 0 && (u32)b->tex < texCount && texOk[b->tex];
		gfx_set_textured(textured);
		gfx_set_cull(cull);
		if (textured) {
			C3D_Tex* t = &tex[b->tex];
			C3D_TexSetWrap(t, wrapMap[b->wrapS > 2 ? 1 : b->wrapS], wrapMap[b->wrapT > 2 ? 1 : b->wrapT]);
			C3D_TexBind(0, t);
		}
		C3D_DrawElements(GPU_TRIANGLES, b->count, C3D_UNSIGNED_SHORT, p->idx + b->first);
		st->calls++;
		st->tris += b->count / 3;
	}
}

DrawStats room_draw(const RoomOptions* opt)
{
	DrawStats st = { 0, 0 };
	C3D_AlphaTest(false, GPU_ALWAYS, 0);
	if (opt->showMain)
		draw_pass(&parts[0], false, opt->cull, &st);
	if (opt->showOku)
		draw_pass(&parts[1], false, opt->cull, &st);
	if (opt->showBlended) {
		C3D_AlphaTest(true, GPU_GREATER, 0x10);   // drop fully transparent texels, blend the rest
		if (opt->showMain)
			draw_pass(&parts[0], true, opt->cull, &st);
		if (opt->showOku)
			draw_pass(&parts[1], true, opt->cull, &st);
		C3D_AlphaTest(false, GPU_ALWAYS, 0);
	}
	return st;
}
