// Play mode: Mario in the room, game-style camera (side-on 2D, flip to 3D), movement and collision.
#pragma once
#include "gfx.h"

typedef struct {
	float pos[3], vy;
	bool grounded;
	float face;        // -1 = looking left .. +1 = looking right, eased (a paper turn)
	float faceGoal;
	bool mode3d;       // target view
	float flipT;       // 0 = 2D view .. 1 = 3D view (animated)
	float z2d;         // the z plane Mario walks on in 2D
	bool hasHit;
	float scale;       // Mario's draw scale (model is 23 units tall); adjustable with L + D-pad up/down
} Play;

void play_init(Play* p, bool hasHit);
void play_reset(Play* p);
void play_update(Play* p, float dt, u32 down, u32 held);
// Camera for the current state: view matrix (world -> camera) and the yaw that turns the sprite to face it.
void play_camera(const Play* p, C3D_Mtx* view, float* yaw);
void play_projection(C3D_Mtx* proj);
float play_height(const Play* p);   // Mario's visual height in room units
