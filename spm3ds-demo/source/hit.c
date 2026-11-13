#include "hit.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "gfx.h"

typedef struct {
	float v[3][3];
	float n[3];                 // unit normal, (b-a) x (c-a)
	float min[3], max[3];
	unsigned attr;              // the room's collision drawMode attr (0 / 4096 / 131072 / 557056)
} Tri;

static Tri* tris;
static int nTris;
static int blockIdx = -1;     // wall triangle that pushed Mario hardest since hit_block_reset()
static float blockAmt;

bool hit_load(const char* path)
{
	hit_free();
	FILE* f = fopen(path, "rb");
	if (!f) return false;
	char magic[4]; unsigned ver, n;
	if (fread(magic, 4, 1, f) != 1 || fread(&ver, 4, 1, f) != 1 || fread(&n, 4, 1, f) != 1 ||
	    memcmp(magic, "SPMH", 4) != 0 || ver != 1 || n == 0 || n > 200000) { fclose(f); return false; }
	tris = malloc(sizeof(Tri) * n);
	if (!tris) { fclose(f); return false; }
	for (unsigned i = 0; i < n; i++) {
		float raw[9]; unsigned attr;
		if (fread(raw, sizeof raw, 1, f) != 1 || fread(&attr, 4, 1, f) != 1) { fclose(f); hit_free(); return false; }
		Tri* t = &tris[i];
		memcpy(t->v, raw, sizeof raw);
		t->attr = attr;
		float e1[3], e2[3];
		for (int k = 0; k < 3; k++) { e1[k] = t->v[1][k] - t->v[0][k]; e2[k] = t->v[2][k] - t->v[0][k]; }
		float nx = e1[1]*e2[2] - e1[2]*e2[1], ny = e1[2]*e2[0] - e1[0]*e2[2], nz = e1[0]*e2[1] - e1[1]*e2[0];
		float l = sqrtf(nx*nx + ny*ny + nz*nz);
		if (l < 1e-6f) l = 1.0f;
		t->n[0] = nx / l; t->n[1] = ny / l; t->n[2] = nz / l;
		for (int k = 0; k < 3; k++) {
			t->min[k] = fminf(t->v[0][k], fminf(t->v[1][k], t->v[2][k]));
			t->max[k] = fmaxf(t->v[0][k], fmaxf(t->v[1][k], t->v[2][k]));
		}
	}
	fclose(f);
	nTris = (int)n;
	return true;
}

static Vertex* dbgVbo;
void hit_free(void) { free(tris); tris = NULL; nTris = 0; if (dbgVbo) { linearFree(dbgVbo); dbgVbo = NULL; } }
int hit_count(void) { return nTris; }

bool hit_floor(float x, float y, float z, float maxUp, float* outY)
{
	bool found = false;
	float best = -1e30f;
	for (int i = 0; i < nTris; i++) {
		const Tri* t = &tris[i];
		if (t->n[1] <= 0.5f) continue;
		if (x < t->min[0] || x > t->max[0] || z < t->min[2] || z > t->max[2]) continue;
		const float* a = t->v[0]; const float* b = t->v[1]; const float* c = t->v[2];
		float den = (b[2]-c[2])*(a[0]-c[0]) + (c[0]-b[0])*(a[2]-c[2]);
		if (fabsf(den) < 1e-9f) continue;
		float u = ((b[2]-c[2])*(x-c[0]) + (c[0]-b[0])*(z-c[2])) / den;
		float v = ((c[2]-a[2])*(x-c[0]) + (a[0]-c[0])*(z-c[2])) / den;
		if (u < -1e-4f || v < -1e-4f || u + v > 1.0001f) continue;
		float fy = a[1] - (t->n[0]*(x-a[0]) + t->n[2]*(z-a[2])) / t->n[1];
		if (fy <= y + maxUp && fy > best) { best = fy; found = true; }
	}
	if (found) *outY = best;
	return found;
}

static float dot3(const float* a, const float* b) { return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]; }

// Closest point on triangle abc to p (Ericson, Real-Time Collision Detection).
static void closest_on_tri(const float* p, const float* a, const float* b, const float* c, float* out)
{
	float ab[3], ac[3], ap[3];
	for (int k = 0; k < 3; k++) { ab[k] = b[k]-a[k]; ac[k] = c[k]-a[k]; ap[k] = p[k]-a[k]; }
	float d1 = dot3(ab, ap), d2 = dot3(ac, ap);
	if (d1 <= 0 && d2 <= 0) { memcpy(out, a, 12); return; }
	float bp[3] = { p[0]-b[0], p[1]-b[1], p[2]-b[2] };
	float d3 = dot3(ab, bp), d4 = dot3(ac, bp);
	if (d3 >= 0 && d4 <= d3) { memcpy(out, b, 12); return; }
	float vc = d1*d4 - d3*d2;
	if (vc <= 0 && d1 >= 0 && d3 <= 0) { float v = d1/(d1-d3); for (int k = 0; k < 3; k++) out[k] = a[k] + v*ab[k]; return; }
	float cp[3] = { p[0]-c[0], p[1]-c[1], p[2]-c[2] };
	float d5 = dot3(ab, cp), d6 = dot3(ac, cp);
	if (d6 >= 0 && d5 <= d6) { memcpy(out, c, 12); return; }
	float vb = d5*d2 - d1*d6;
	if (vb <= 0 && d2 >= 0 && d6 <= 0) { float w = d2/(d2-d6); for (int k = 0; k < 3; k++) out[k] = a[k] + w*ac[k]; return; }
	float va = d3*d6 - d5*d4;
	if (va <= 0 && (d4-d3) >= 0 && (d5-d6) >= 0) {
		float w = (d4-d3)/((d4-d3)+(d5-d6));
		for (int k = 0; k < 3; k++) out[k] = b[k] + w*(c[k]-b[k]);
		return;
	}
	float den = 1.0f/(va+vb+vc), v = vb*den, w = vc*den;
	for (int k = 0; k < 3; k++) out[k] = a[k] + ab[k]*v + ac[k]*w;
}

void hit_push_sphere(float c[3], float r)
{
	for (int i = 0; i < nTris; i++) {
		const Tri* t = &tris[i];
		if (fabsf(t->n[1]) > 0.5f) continue;
		if (c[0]+r < t->min[0] || c[0]-r > t->max[0] || c[1]+r < t->min[1] || c[1]-r > t->max[1] ||
		    c[2]+r < t->min[2] || c[2]-r > t->max[2]) continue;
		float q[3];
		closest_on_tri(c, t->v[0], t->v[1], t->v[2], q);
		float dx = c[0]-q[0], dy = c[1]-q[1], dz = c[2]-q[2];
		float d2 = dx*dx + dy*dy + dz*dz;
		if (d2 >= r*r) continue;
		float hx = dx, hz = dz, hl = sqrtf(hx*hx + hz*hz);
		float push;
		if (hl < 1e-4f) {   // centre on the wall: use the wall normal
			hx = t->n[0]; hz = t->n[2]; hl = sqrtf(hx*hx + hz*hz);
			if (hl < 1e-4f) continue;
			push = r;
		} else {
			push = r - sqrtf(d2);
			if (push <= 0) continue;
		}
		c[0] += hx / hl * push;
		c[2] += hz / hl * push;
		if (push > blockAmt) { blockAmt = push; blockIdx = i; }
	}
}

// ---- debug view -------------------------------------------------------------------------------------------------

void hit_block_reset(void) { blockIdx = -1; blockAmt = 0.0f; }
int hit_block_get(float* push) { if (push) *push = blockAmt; return blockIdx; }

bool hit_tri_info(int i, float n[3], float mn[3], float mx[3], unsigned* attr)
{
	if (i < 0 || i >= nTris) return false;
	memcpy(n, tris[i].n, 12); memcpy(mn, tris[i].min, 12); memcpy(mx, tris[i].max, 12);
	*attr = tris[i].attr;
	return true;
}

#define DBG_MAX_TRIS 450
#define DBG_MAX_VERTS (DBG_MAX_TRIS * 18 + 64)

static void put(Vertex* v, const float* p, u8 r, u8 g, u8 b)
{
	v->x = (s16)lrintf(p[0] * 64.0f); v->y = (s16)lrintf(p[1] * 64.0f); v->z = (s16)lrintf(p[2] * 64.0f); v->pad = 0;
	v->u = v->v = 0; v->r = r; v->g = g; v->b = b; v->a = 255;
}

// Thin quad (2 triangles) lying in the triangle's plane, along the edge a->b, inside the triangle.
static int edge_quad(Vertex* out, const float* a, const float* b, const float* c, const float* n, float w, u8 r, u8 g, u8 bl)
{
	float e[3] = { b[0]-a[0], b[1]-a[1], b[2]-a[2] };
	float d[3] = { n[1]*e[2] - n[2]*e[1], n[2]*e[0] - n[0]*e[2], n[0]*e[1] - n[1]*e[0] };
	float l = sqrtf(dot3(d, d));
	if (l < 1e-6f) return 0;
	float ac[3] = { c[0]-a[0], c[1]-a[1], c[2]-a[2] };
	float s = dot3(d, ac) >= 0.0f ? w / l : -w / l;
	float a2[3] = { a[0] + d[0]*s, a[1] + d[1]*s, a[2] + d[2]*s };
	float b2[3] = { b[0] + d[0]*s, b[1] + d[1]*s, b[2] + d[2]*s };
	put(out + 0, a, r, g, bl); put(out + 1, b, r, g, bl); put(out + 2, b2, r, g, bl);
	put(out + 3, a, r, g, bl); put(out + 4, b2, r, g, bl); put(out + 5, a2, r, g, bl);
	return 6;
}

// Draws the collision triangles within `radius` of `center` as wireframe: walls red, floors green, ceilings blue,
// walls with a non-zero attr magenta. The triangle `highlight` is filled yellow. Drawn without depth test (x-ray).
// Build once per frame (eye 0), draw for each eye.
static int dbgCount;
void hit_debug_build(const float center[3], float radius, int highlight)
{
	if (!tris) { dbgCount = 0; return; }
	if (!dbgVbo) {
		dbgVbo = linearAlloc(sizeof(Vertex) * DBG_MAX_VERTS);
		if (!dbgVbo) { dbgCount = 0; return; }
	}
	int n = 0, shown = 0;
	for (int i = 0; i < nTris && shown < DBG_MAX_TRIS; i++) {
		const Tri* t = &tris[i];
		if (i != highlight &&
		    (center[0]+radius < t->min[0] || center[0]-radius > t->max[0] || center[1]+radius < t->min[1] || center[1]-radius > t->max[1] ||
		     center[2]+radius < t->min[2] || center[2]-radius > t->max[2])) continue;
		shown++;
		u8 r, g, b;
		if (t->n[1] > 0.5f) { r = 60; g = 230; b = 60; }
		else if (t->n[1] < -0.5f) { r = 90; g = 130; b = 255; }
		else if (t->attr) { r = 255; g = 60; b = 255; }
		else { r = 255; g = 60; b = 60; }
		if (i == highlight) {
			for (int k = 0; k < 3; k++) put(dbgVbo + n + k, t->v[k], 255, 255, 0);
			n += 3;
			r = 255; g = 255; b = 255;
		}
		for (int k = 0; k < 3; k++)
			n += edge_quad(dbgVbo + n, t->v[k], t->v[(k + 1) % 3], t->v[(k + 2) % 3], t->n, 0.25f, r, g, b);
	}
	dbgCount = n;
	GSPGPU_FlushDataCache(dbgVbo, sizeof(Vertex) * (n ? n : 1));
}

int hit_debug_draw(void)
{
	if (!dbgCount || !dbgVbo) return 0;
	gfx_bind_vbo(dbgVbo);
	gfx_set_textured(false);
	gfx_set_cull(CULL_NONE);
	C3D_AlphaTest(false, GPU_ALWAYS, 0);
	C3D_DepthTest(false, GPU_ALWAYS, GPU_WRITE_COLOR);
	C3D_DrawArrays(GPU_TRIANGLES, 0, dbgCount);
	C3D_DepthTest(true, GPU_GREATER, GPU_WRITE_ALL);
	return dbgCount / 3;
}
