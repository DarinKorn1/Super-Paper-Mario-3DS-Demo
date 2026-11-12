#include "stress.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>

// 118 patches laid out on an 11-column grid. Each patch is a w x h grid of quads (2 triangles each),
// all patches share one vertex buffer and one index buffer; every patch is its own draw call.
#define COLS 11
#define MAX_TRIS (STRESS_STEPS * STRESS_STEP_TRIS)
#define MAX_VERTS 45000          // 60,000 triangles need ~34,000 vertices; 16-bit indices allow 65,535

static Vertex* vbo;
static u16* ibo;
static struct { u32 first, count; } draws[STRESS_DRAWS];
static int level = 0;
static u32 nVerts, nIdx;

int stress_level(void) { return level; }
int stress_target(void) { return (level + 1) * STRESS_STEP_TRIS; }

bool stress_init(void)
{
	vbo = linearAlloc(sizeof(Vertex) * MAX_VERTS);
	ibo = linearAlloc(sizeof(u16) * MAX_TRIS * 3);
	if (!vbo || !ibo)
		return false;
	stress_set_level(0);
	return true;
}

void stress_exit(void)
{
	if (vbo) linearFree(vbo);
	if (ibo) linearFree(ibo);
	vbo = NULL;
	ibo = NULL;
}

static s16 clamp16(int v) { return (s16)(v > 32767 ? 32767 : v < -32768 ? -32768 : v); }

void stress_set_level(int newLevel)
{
	if (newLevel < 0) newLevel = 0;
	if (newLevel >= STRESS_STEPS) newLevel = STRESS_STEPS - 1;
	level = newLevel;

	int quadsTotal = stress_target() / 2;
	int base = quadsTotal / STRESS_DRAWS, extra = quadsTotal % STRESS_DRAWS;
	nVerts = nIdx = 0;

	for (int p = 0; p < STRESS_DRAWS; p++) {
		int q = base + (p < extra ? 1 : 0);
		int w = (int)ceilf(sqrtf((float)q));
		int h = (q + w - 1) / w;
		float ox = (float)(p % COLS) * 12.0f - (COLS * 12.0f) / 2.0f;
		float oy = (float)(p / COLS) * 12.0f - (COLS * 12.0f) / 2.0f;
		u32 v0 = nVerts;

		for (int j = 0; j <= h; j++) {
			for (int i = 0; i <= w; i++) {
				float x = ox + 10.0f * i / w, y = oy + 10.0f * j / h;
				float z = 1.5f * sinf(x * 0.5f) * cosf(y * 0.5f);   // gentle waves so it is not a flat wall
				Vertex* v = &vbo[nVerts++];
				v->x = clamp16((int)lrintf(x * 64.0f));
				v->y = clamp16((int)lrintf(y * 64.0f));
				v->z = clamp16((int)lrintf(z * 64.0f));
				v->pad = 0;
				v->u = (s16)(i * 4 * 128 / w);       // checker repeated 4x across the patch
				v->v = (s16)(j * 4 * 128 / h);
				v->r = (u8)(128 + (p * 37) % 128);
				v->g = (u8)(128 + (p * 61) % 128);
				v->b = (u8)(128 + (p * 89) % 128);
				v->a = 255;
			}
		}
		draws[p].first = nIdx;
		int made = 0;
		for (int j = 0; j < h && made < q; j++) {
			for (int i = 0; i < w && made < q; i++, made++) {
				u16 a = (u16)(v0 + j * (w + 1) + i), b = (u16)(a + 1), c = (u16)(a + (w + 1)), d = (u16)(c + 1);
				ibo[nIdx++] = a; ibo[nIdx++] = b; ibo[nIdx++] = d;
				ibo[nIdx++] = a; ibo[nIdx++] = d; ibo[nIdx++] = c;
			}
		}
		draws[p].count = nIdx - draws[p].first;
	}
	GSPGPU_FlushDataCache(vbo, sizeof(Vertex) * nVerts);
	GSPGPU_FlushDataCache(ibo, sizeof(u16) * nIdx);
}

DrawStats stress_draw(const C3D_Mtx* proj, float t)
{
	// Camera in front of the grid, the grid slowly swings so the picture is not static.
	C3D_Mtx view;
	Mtx_Identity(&view);
	Mtx_Translate(&view, 0.0f, 0.0f, -150.0f, true);
	Mtx_RotateX(&view, -0.5f, true);
	Mtx_RotateZ(&view, 0.4f * sinf(t * 0.5f), true);
	gfx_set_matrices(proj, &view);

	gfx_bind_vbo(vbo);
	gfx_set_textured(true);
	gfx_set_cull(CULL_NONE);
	C3D_TexBind(0, gfx_checker());
	C3D_AlphaTest(false, GPU_ALWAYS, 0);

	DrawStats st = { 0, 0 };
	for (int p = 0; p < STRESS_DRAWS; p++) {
		C3D_DrawElements(GPU_TRIANGLES, draws[p].count, C3D_UNSIGNED_SHORT, ibo + draws[p].first);
		st.calls++;
		st.tris += draws[p].count / 3;
	}
	return st;
}
