// Stress-test mode: a textured wavy mesh split into 118 draw calls with an adjustable triangle count.
// Built to be run later on the real console; do not draw conclusions from emulator timings.
#pragma once
#include "room.h"

#define STRESS_STEPS 12          // 5,000 .. 60,000 triangles in steps of 5,000
#define STRESS_STEP_TRIS 5000
#define STRESS_DRAWS 118

bool stress_init(void);          // allocates buffers for the largest level
void stress_exit(void);
void stress_set_level(int level);   // 0 .. STRESS_STEPS-1
int  stress_level(void);
int  stress_target(void);        // requested triangle count of the level
DrawStats stress_draw(const C3D_Mtx* proj, float timeSeconds);
