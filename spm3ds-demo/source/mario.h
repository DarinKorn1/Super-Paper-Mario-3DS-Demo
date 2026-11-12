// Mario's sprite model (static standing pose) from tools/convert_mario.py.
#pragma once
#include "room.h"

bool mario_load(const char* dir, char* err, size_t errSize);   // mario.spm + textures/mario_NNN.t3x
void mario_free(void);
bool mario_loaded(void);

// Draws Mario at pos. `camView` is the world->camera matrix, `billboardYaw` turns the sprite to face the camera,
// `sx` = +1 looks to the sprite's left, -1 mirrored (values in between squash it: a paper turn).
// `anim` = 0 idle, 1 walk (baked from mario_anim.bin; time60 in 60 Hz frames), -1 or missing data = static pose.
DrawStats mario_draw(const C3D_Mtx* proj, const C3D_Mtx* camView, const float pos[3], float billboardYaw, float sx,
                     float scale, int anim, float time60);
int mario_anim_count(void);
