#include "play.h"
#include "hit.h"
#include <math.h>
#include <string.h>

// Scale. The room is stored at about 1/8 of the game's units (a door is 8 x 8 here; see notes/demo-plan.md 10.1),
// and Mario's hitbox in the game is 20 x 39 units (characterProperties[0] in main.dol). His sprite is drawn at about
// 1.4x its model size (23 tall) in game units, i.e. 1.4 / 8 = 0.175 here. L + D-pad up/down changes it live.
// Everything below is derived from the visual height H = MARIO_MODEL_H * scale so it follows the scale.
#define MARIO_MODEL_H 23.0f
#define DEFAULT_SCALE 0.175f
#define SPAWN_X 0.0f
#define SPAWN_Z -10.0f
#define WALK_HEIGHTS_PER_S 2.8f    // game: 1.5 units/frame at 60 fps = 90 units/s, about 2.8 Mario heights per second
#define JUMP_HEIGHTS 1.6f          // guess: jump peak in Mario heights
#define JUMP_TIME 0.45f            // guess: seconds to the peak
#define BODY_R_HEIGHTS 0.30f       // hitbox width 20 of height 32 (visual) -> half width 0.31
#define STEP_HEIGHTS 0.15f
#define FOV_DEG 25.0f              // camera_road.bin
#define DIST_2D_HEIGHTS 16.0f      // makes Mario about 14 % of the screen height, as in the game (screenshot mac_02_cinematic)
#define DIST_3D_HEIGHTS 11.0f
#define PITCH_3D 0.20f
#define FLIP_TIME 0.6f
#define PI_F 3.14159265f

float play_height(const Play* p) { return MARIO_MODEL_H * p->scale; }

void play_reset(Play* p)
{
	bool hasHit = p->hasHit;
	float scale = p->scale > 0.0f ? p->scale : DEFAULT_SCALE;
	memset(p, 0, sizeof *p);
	p->hasHit = hasHit;
	p->scale = scale;
	p->pos[0] = SPAWN_X;
	p->pos[1] = hasHit ? 2.0f * play_height(p) : 0.0f;   // drop onto the floor
	p->pos[2] = SPAWN_Z;
	p->z2d = SPAWN_Z;
	p->face = p->faceGoal = 1.0f;
}

void play_init(Play* p, bool hasHit)
{
	memset(p, 0, sizeof *p);
	p->hasHit = hasHit;
	p->scale = DEFAULT_SCALE;
	play_reset(p);
}

static float ease(float t) { return t * t * (3.0f - 2.0f * t); }
static float cam_theta(const Play* p) { return -0.5f * PI_F * ease(p->flipT); }

static void keep_view_state(Play* p)
{
	bool m = p->mode3d; float f = p->flipT;
	play_reset(p);
	p->mode3d = m; p->flipT = f;
}

void play_update(Play* p, float dt, u32 down, u32 held, bool debug)
{
	// debug screen only: hold L, D-pad up/down = change Mario's scale (x1.8 per second), L + B resets it
	if (debug && (held & KEY_L)) {
		if (held & KEY_DUP)   p->scale *= expf(0.6f * dt);
		if (held & KEY_DDOWN) p->scale /= expf(0.6f * dt);
		if (p->scale < 0.02f) p->scale = 0.02f;
		if (p->scale > 2.0f) p->scale = 2.0f;
	}
	bool lDebug = debug && (held & KEY_L);
	if (!lDebug && (down & KEY_X)) p->mode3d = !p->mode3d;
	if (!lDebug && (down & KEY_B)) { keep_view_state(p); return; }
	if (lDebug && (down & KEY_B)) p->scale = DEFAULT_SCALE;

	const float H = play_height(p);
	const float R = BODY_R_HEIGHTS * H;
	const float STEP = STEP_HEIGHTS * H;

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

	// animation: walk while the stick is pushed (cycle rate follows the speed), idle otherwise
	float mag = fminf(1.0f, ml);
	int want = (mag > 0.2f && p->grounded) ? 1 : 0;
	if (want != p->anim) { p->anim = want; p->animTime = 0.0f; }
	p->animTime += dt * 60.0f * (want ? (0.4f + 0.6f * mag) : 1.0f);

	float speed = WALK_HEIGHTS_PER_S * H;
	p->pos[0] += mx * speed * dt;
	p->pos[2] += mz * speed * dt;
	if (!p->mode3d) {                              // glide back onto the 2D plane
		float d = p->z2d - p->pos[2];
		float s = 2.5f * speed * dt;
		p->pos[2] += fabsf(d) < s ? d : (d > 0 ? s : -s);
	}

	if (p->hasHit) {
		// walls: two spheres; the lower one starts above the step height so low edges can be climbed
		float c[3] = { p->pos[0], p->pos[1] + STEP + R + 0.02f * H, p->pos[2] };
		hit_push_sphere(c, R);
		p->pos[0] = c[0]; p->pos[2] = c[2];
		float c2[3] = { p->pos[0], p->pos[1] + H - R, p->pos[2] };
		hit_push_sphere(c2, R);
		p->pos[0] = c2[0]; p->pos[2] = c2[2];
	}

	const float jumpV = 2.0f * JUMP_HEIGHTS * H / JUMP_TIME;
	const float gravity = jumpV / JUMP_TIME;
	if ((down & KEY_A) && p->grounded) { p->vy = jumpV; p->grounded = false; }
	float oldY = p->pos[1];
	p->vy -= gravity * dt;
	p->pos[1] += p->vy * dt;
	float fy;
	bool have = p->hasHit ? hit_floor(p->pos[0], oldY, p->pos[2], STEP, &fy) : (fy = 0.0f, true);
	if (have && p->vy <= 0.0f && p->pos[1] <= fy) {
		p->pos[1] = fy; p->vy = 0.0f; p->grounded = true;
	} else {
		p->grounded = false;
	}
	if (p->pos[1] < -250.0f) keep_view_state(p);     // fell out of the world
}

void play_projection(C3D_Mtx* proj)
{
	Mtx_PerspTilt(proj, C3D_AngleFromDegrees(FOV_DEG), C3D_AspectRatioTop, 1.0f, 1500.0f, false);
}

static float cam_dist(const Play* p)
{
	return (DIST_2D_HEIGHTS + (DIST_3D_HEIGHTS - DIST_2D_HEIGHTS) * ease(p->flipT)) * play_height(p);
}

// Eye separation as a fraction of the viewing distance: 3 % at full slider (about a 1.9 m viewing distance and 6.5 cm eyes would be 3.4 %).
#define STEREO_IOD_FRACTION 0.03f

void play_projection_stereo(const Play* p, C3D_Mtx* proj, int eye, float slider)
{
	float dist = cam_dist(p);
	float iod = eye * slider * STEREO_IOD_FRACTION * dist;
	Mtx_PerspStereoTilt(proj, C3D_AngleFromDegrees(FOV_DEG), C3D_AspectRatioTop, 1.0f, 1500.0f, iod, dist, false);
}

void play_camera(const Play* p, C3D_Mtx* view, float* yaw)
{
	float H = play_height(p);
	float e = ease(p->flipT);
	float th = cam_theta(p);
	float dist = (DIST_2D_HEIGHTS + (DIST_3D_HEIGHTS - DIST_2D_HEIGHTS) * e) * H;
	float pitch = PITCH_3D * e;
	float tx = p->pos[0], ty = p->pos[1] + 0.5f * H, tz = p->pos[2];
	float cx = tx + dist * sinf(th) * cosf(pitch);
	float cy = ty + dist * sinf(pitch);
	float cz = tz + dist * cosf(th) * cosf(pitch);
	Mtx_Identity(view);
	Mtx_RotateX(view, pitch, true);          // looking down by `pitch`
	Mtx_RotateY(view, -th, true);
	Mtx_Translate(view, -cx, -cy, -cz, true);
	*yaw = th;
}
