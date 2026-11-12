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
