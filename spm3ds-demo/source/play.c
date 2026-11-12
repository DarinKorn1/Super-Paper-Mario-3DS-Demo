#include "play.h"
#include "hit.h"
#include <math.h>
#include <string.h>

// Tunables (world units; Mario is 23 tall; the room's street floor is y = 0, z from -30 to 10).
#define SPAWN_X 0.0f
#define SPAWN_Z -10.0f
#define WALK_SPEED 60.0f
#define GRAVITY 330.0f
#define JUMP_SPEED 150.0f
#define STEP_UP 4.5f
#define BODY_R 4.0f
#define FOV_DEG 25.0f          // camera_road.bin: field of view 25 (the only camera number found in it)
#define DIST_2D 190.0f         // guesses: the file's distances are not decoded
#define DIST_3D 120.0f
#define PITCH_3D 0.20f
#define FLIP_TIME 0.6f
#define PI_F 3.14159265f

void play_reset(Play* p)
{
	bool hasHit = p->hasHit;
	memset(p, 0, sizeof *p);
	p->hasHit = hasHit;
	p->pos[0] = SPAWN_X;
	p->pos[1] = p->hasHit ? 30.0f : 0.0f;   // drop onto the floor
	p->pos[2] = SPAWN_Z;
	p->z2d = SPAWN_Z;
	p->face = p->faceGoal = 1.0f;
}

void play_init(Play* p, bool hasHit)
{
	memset(p, 0, sizeof *p);
	p->hasHit = hasHit;
	play_reset(p);
}

static float ease(float t) { return t * t * (3.0f - 2.0f * t); }

static float cam_theta(const Play* p) { return -0.5f * PI_F * ease(p->flipT); }

void play_update(Play* p, float dt, u32 down, u32 held)
{
	(void)held;
	if (down & KEY_X) p->mode3d = !p->mode3d;
	if (down & KEY_B) { bool h = p->hasHit; bool m = p->mode3d; float f = p->flipT; play_reset(p); p->hasHit = h; p->mode3d = m; p->flipT = f; return; }
	float goal = p->mode3d ? 1.0f : 0.0f;
	float step = dt / FLIP_TIME;
	if (p->flipT < goal) p->flipT = fminf(goal, p->flipT + step);
	else if (p->flipT > goal) p->flipT = fmaxf(goal, p->flipT - step);

	circlePosition cp;
	hidCircleRead(&cp);
	float sx = fabsf((float)cp.dx) > 15.0f ? cp.dx / 156.0f : 0.0f;
	float sy = fabsf((float)cp.dy) > 15.0f ? cp.dy / 156.0f : 0.0f;
	sx = fmaxf(-1.0f, fminf(1.0f, sx));
	sy = fmaxf(-1.0f, fminf(1.0f, sy));

	float th = cam_theta(p);
	float rx = cosf(th), rz = -sinf(th);          // camera right on the ground plane
	float fx = -sinf(th), fz = -cosf(th);         // camera forward
	float mx, mz;
	if (p->mode3d) { mx = rx * sx + fx * sy; mz = rz * sx + fz * sy; }
	else { mx = sx; mz = 0.0f; }
	float ml = sqrtf(mx * mx + mz * mz);
	if (ml > 1.0f) { mx /= ml; mz /= ml; }

	// face the way we walk, as seen from the camera (right on screen = +1)
	float screenX = mx * rx + mz * rz;
	if (screenX > 0.1f) p->faceGoal = 1.0f;
	else if (screenX < -0.1f) p->faceGoal = -1.0f;
	float tf = 9.0f * dt;
	if (p->face < p->faceGoal) p->face = fminf(p->faceGoal, p->face + tf);
	else if (p->face > p->faceGoal) p->face = fmaxf(p->faceGoal, p->face - tf);

	p->pos[0] += mx * WALK_SPEED * dt;
	p->pos[2] += mz * WALK_SPEED * dt;
	if (!p->mode3d) {                              // glide back onto the 2D plane
		float d = p->z2d - p->pos[2];
		float s = 80.0f * dt;
		p->pos[2] += fabsf(d) < s ? d : (d > 0 ? s : -s);
	}

	if (p->hasHit) {
		// walls: two spheres, the lower one clears stair risers up to STEP_UP
		float c[3] = { p->pos[0], p->pos[1] + STEP_UP + BODY_R + 1.0f, p->pos[2] };
		hit_push_sphere(c, BODY_R);
		p->pos[0] = c[0]; p->pos[2] = c[2];
		float c2[3] = { p->pos[0], p->pos[1] + 19.0f, p->pos[2] };
		hit_push_sphere(c2, BODY_R);
		p->pos[0] = c2[0]; p->pos[2] = c2[2];
	}

	if ((down & KEY_A) && p->grounded) { p->vy = JUMP_SPEED; p->grounded = false; }
	float oldY = p->pos[1];
	p->vy -= GRAVITY * dt;
	p->pos[1] += p->vy * dt;
	float fy;
	bool have = p->hasHit ? hit_floor(p->pos[0], oldY, p->pos[2], STEP_UP, &fy) : (fy = 0.0f, true);
	if (have && p->vy <= 0.0f && p->pos[1] <= fy) {
		p->pos[1] = fy; p->vy = 0.0f; p->grounded = true;
	} else {
		p->grounded = false;
	}
	if (p->pos[1] < -250.0f) {                       // fell out of the world
		bool h = p->hasHit, m = p->mode3d; float f = p->flipT;
		play_reset(p); p->hasHit = h; p->mode3d = m; p->flipT = f;
	}
}

void play_projection(C3D_Mtx* proj)
{
	Mtx_PerspTilt(proj, C3D_AngleFromDegrees(FOV_DEG), C3D_AspectRatioTop, 5.0f, 1500.0f, false);
}

void play_camera(const Play* p, C3D_Mtx* view, float* yaw)
{
	float e = ease(p->flipT);
	float th = cam_theta(p);
	float dist = DIST_2D + (DIST_3D - DIST_2D) * e;
	float pitch = PITCH_3D * e;
	float tx = p->pos[0], ty = p->pos[1] + 11.0f, tz = p->pos[2];
	float cx = tx + dist * sinf(th) * cosf(pitch);
	float cy = ty + dist * sinf(pitch);
	float cz = tz + dist * cosf(th) * cosf(pitch);
	Mtx_Identity(view);
	Mtx_RotateX(view, pitch, true);          // looking down by `pitch`
	Mtx_RotateY(view, -th, true);
	Mtx_Translate(view, -cx, -cy, -cz, true);
	*yaw = th;
}
