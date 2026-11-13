// Collision against the room's A tree (room_hit.bin from tools/convert_room.py).
#pragma once
#include <stdbool.h>

bool hit_load(const char* path);
void hit_free(void);
int  hit_count(void);

// Highest floor under (x,z) whose height is <= y + maxUp. Returns false if there is none.
bool hit_floor(float x, float y, float z, float maxUp, float* outY);

// Pushes a sphere (centre c, radius r) out of every wall triangle (|normal.y| <= 0.5), horizontally only.
void hit_push_sphere(float c[3], float r);

// Debug: which wall triangle pushed Mario hardest since the last reset (-1 = none) and by how much (room units).
void hit_block_reset(void);
int  hit_block_get(float* push);
bool hit_tri_info(int i, float n[3], float mn[3], float mx[3], unsigned* attr);
// Wireframe of the collision triangles around `center` (see hit.c). Build once per frame, draw per eye.
void hit_debug_build(const float center[3], float radius, int highlight);
int  hit_debug_draw(void);   // returns the number of triangles drawn
