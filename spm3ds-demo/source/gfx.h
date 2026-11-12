// Shared graphics state: shader, vertex format, matrices, TexEnv helpers.
#pragma once
#include <3ds.h>
#include <citro3d.h>
#include <stdbool.h>

// 16-byte vertex used by both the room renderer and the stress test.
// Position is s16 = world units * 64 (the shader scale is folded into the view matrix).
typedef struct {
	s16 x, y, z, pad;
	s16 u, v;          // GX texcoord units: 128 = 1.0
	u8 r, g, b, a;
} Vertex;

#define POS_SCALE (1.0f / 64.0f)

typedef enum { CULL_NONE = 0, CULL_BACK, CULL_FRONT, CULL_MODES } CullMode;

void gfx_init(void);              // shader, attribute layout, checker texture
void gfx_exit(void);
C3D_Tex* gfx_checker(void);

void gfx_bind_vbo(const void* vbo);                                    // one VBO of Vertex
void gfx_set_matrices(const C3D_Mtx* proj, const C3D_Mtx* view);       // view is world->camera, no scale
void gfx_set_textured(bool textured);                                  // TexEnv: tex*colour, or colour only
void gfx_set_cull(CullMode m);
const char* gfx_cull_name(CullMode m);
