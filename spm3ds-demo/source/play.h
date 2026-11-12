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
	float scale;       // Mario's draw scale (model is 23 units tall); adjustable with L + D-pad up/down in the debug screen
	int anim;          // 0 idle, 1 walk
	float camX, camY, camZ; bool camInit;   // smoothed camera target (see play_cam_update)
	float animTime;    // 60 Hz frames since the animation started
} Play;

bool play_load_camera(const char* dir);   // assets/camera.bin (optional; built-in defaults are the same numbers)
void play_cam_update(Play* p, float dt); // once per frame after play_update
void play_init(Play* p, bool hasHit);
void play_reset(Play* p);
void play_update(Play* p, float dt, u32 down, u32 held, bool debug);   // debug enables the L + D-pad scale control
// Camera for the current state: view matrix (world -> camera) and the yaw that turns the sprite to face it.
void play_camera(const Play* p, C3D_Mtx* view, float* yaw);
void play_projection(C3D_Mtx* proj);
// Per-eye projection for stereo 3D. eye = -1 left, +1 right; slider = 0..1 from osGet3DSliderState(). The convergence plane
// (zero parallax) is at Mario's distance, so he sits at screen depth and the room recedes/pops around him.
void play_projection_stereo(const Play* p, C3D_Mtx* proj, int eye, float slider);
float play_height(const Play* p);   // Mario's visual height in room units
