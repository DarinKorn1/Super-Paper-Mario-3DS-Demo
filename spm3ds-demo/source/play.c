#include "play.h"
#include "hit.h"
#include <math.h>
#include <string.h>
#include <stdio.h>

// Scale. The room is stored at about 1/8 of the game's units (a door is 8 x 8 here; see notes/demo-plan.md 10.1),
// and Mario's hitbox in the game is 20 x 39 units (characterProperties[0] in main.dol). His sprite is drawn at about
// 1.4x its model size (23 tall) in game units, i.e. 1.4 / 8 = 0.175 here. L + D-pad up/down changes it live.
// Everything below is derived from the visual height H = MARIO_MODEL_H * scale so it follows the scale.
#define MARIO_MODEL_H 23.0f
#define DEFAULT_SCALE 0.2087f   // Mario 4.8 room units tall (38.5 game units: measured in the reference screenshot, matches the 20 x 39 hitbox)
#define SPAWN_X 7.94f              // the reference spot: game (63.49, 198.96) / 8
#define SPAWN_Z 24.87f
#define WALK_HEIGHTS_PER_S 2.35f    // game: 1.5 units/frame at 60 fps = 90 units/s, about 2.8 Mario heights per second
#define JUMP_HEIGHTS 1.34f         // guess: jump peak in Mario heights
#define JUMP_TIME 0.45f            // guess: seconds to the peak
#define BODY_R_HEIGHTS 0.25f       // hitbox width 20 of height 32 (visual) -> half width 0.31
#define STEP_HEIGHTS 0.126f
#define FLIP_TIME 0.6f
#define STEREO_IOD_FRACTION 0.03f
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
	p->blockTri = -1; p->blockAge = 99.0f;
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
		hit_block_reset();
		float c[3] = { p->pos[0], p->pos[1] + STEP + R + 0.02f * H, p->pos[2] };
		hit_push_sphere(c, R);
		p->pos[0] = c[0]; p->pos[2] = c[2];
		float c2[3] = { p->pos[0], p->pos[1] + H - R, p->pos[2] };
		hit_push_sphere(c2, R);
		p->pos[0] = c2[0]; p->pos[2] = c2[2];
		float bp; int bt = hit_block_get(&bp);
		if (bt >= 0) { p->blockTri = bt; p->blockPush = bp; p->blockAge = 0.0f; }
		else p->blockAge += dt;
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

// ---- Camera (ground truth: camlog.txt from the PC build + the decompiled cam3dMain; notes/demo-plan.md sections 14-15) ----
// All numbers below are game units / 8 = room units, measured with Mario at game (63.49, 0, 198.96) on road C2D_02 / C3D_02 (room z = 25).
// The game draws with ONE camera (camera 5) in both modes:
//   2D: ORTHOGRAPHIC, fovY 25 at distance 660 (so the view is 2 * 660 * tan(12.5 deg) = 292.6 game units = 36.6 room units tall),
//       looking straight along -z (pitch 0), eye 101.26 above Mario's feet, 695 in front of him.
//   3D: perspective, fovY 50, eye (-290.7, +123.4, +52.2) and target (+23.8, +95.2, +52.2) relative to Mario (looks along +x, pitched 5.1 down),
//       near 1, far 5000.
// Flip: the game blends target, distance, yaw and pitch between the two (cam3dMain), which this does too. The 2D "orthographic" camera is
// emulated by a very distant perspective camera (dolly-zoom, ORTHO_K times further, narrower fov) so stereo 3D and the flip need no special case.
#define CAM_FOLLOW 0.08f          // x/z follow Mario 8 % of the way per 60 Hz frame (func_80055ce0)
#define GAME_ASPECT 1.68889f      // the game's 16:9 aspect (cam5 aspect in the log); the 3DS top screen is 400 x 240 = 1.6667
#define ORTHO_K 24.0f
// 2D (relative to the follow point F = Mario's x/y/z)
#define C2_EYE_Y   12.658f        // 101.263 / 8
#define C2_EYE_Z   86.890f        // (894.079 - 198.958) / 8
#define C2_DIST    82.5f          // 660 / 8
#define C2_FOV     25.0f
// 3D
#define C3_EYE_X  (-36.337f)      // -290.695 / 8
#define C3_EYE_Y   15.424f
#define C3_TGT_X     2.980f
#define C3_TGT_Y    11.894f
#define C3_Z         6.521f       // 52.17 / 8: the 3D road line is a bit off Mario's z (C3D_02 runs z 10..40)
#define C3_FOV     50.0f
#define C_NEAR3     0.125f
#define C_FAR       625.0f        // 5000 / 8
#define X_MARGIN    7.25f         // the road x clamp is widened by 58 game units

static float cam_xMin = -110.0f, cam_xMax = 110.0f;   // road C2D x range (assets/camera.bin overrides)

bool play_load_camera(const char* dir)
{
	char path[256];
	snprintf(path, sizeof path, "%scamera.bin", dir);
	FILE* f = fopen(path, "rb");
	if (!f) return false;
	char magic[4]; u32 ver; float v[10];
	bool ok = fread(magic, 1, 4, f) == 4 && memcmp(magic, "SCAM", 4) == 0 && fread(&ver, 4, 1, f) == 1 && ver == 1 && fread(v, 4, 10, f) == 10;
	fclose(f);
	if (ok) { cam_xMin = v[2]; cam_xMax = v[3]; }
	return ok;
}

static float lerpf(float a, float b, float t) { return a + (b - a) * t; }

typedef struct { float eye[3], yaw, pitch, dist, fov, nearP, farP; } CamPose;

// Pose for the follow point (camX, camY, camZ) and the eased flip e (0 = 2D, 1 = 3D).
static void cam_pose(const Play* p, CamPose* c)
{
	const float e = ease(p->flipT);
	const float kA = GAME_ASPECT / ((float)400 / 240);   // keep the game's horizontal extent on the 3DS's narrower 400 x 240 screen
	const float fx = p->camX, fy = p->camY, fz = p->camZ;

	// 2D: target straight ahead of the eye at distance 82.5; visible half-height H2 stays fixed
	float t2[3] = { fx, fy + C2_EYE_Y, fz + C2_EYE_Z - C2_DIST };
	float H2 = C2_DIST * tanf(C2_FOV * 0.5f * (PI_F / 180.0f)) * kA;
	float d2 = C2_DIST * ORTHO_K;
	// 3D
	float e3[3] = { fx + C3_EYE_X, fy + C3_EYE_Y, fz + C3_Z };
	float t3[3] = { fx + C3_TGT_X, fy + C3_TGT_Y, fz + C3_Z };
	float dx = e3[0] - t3[0], dy = e3[1] - t3[1], dz = e3[2] - t3[2];
	float d3 = sqrtf(dx * dx + dy * dy + dz * dz);
	float pitch3 = atan2f(dy, sqrtf(dx * dx + dz * dz));
	float H3 = d3 * tanf(C3_FOV * 0.5f * (PI_F / 180.0f)) * kA;

	float tgt[3];
	for (int i = 0; i < 3; i++) tgt[i] = lerpf(t2[i], t3[i], e);
	float d = expf(lerpf(logf(d2), logf(d3), e));        // geometric blend = a smooth dolly
	float H = lerpf(H2, H3, e);
	c->yaw = -0.5f * PI_F * e;                           // eye at +z (2D) swings to -x (3D)
	c->pitch = pitch3 * e;
	c->dist = d;
	c->fov = 2.0f * atanf(H / d) * (180.0f / PI_F);
	float cp = cosf(c->pitch);
	c->eye[0] = tgt[0] + d * sinf(c->yaw) * cp;
	c->eye[1] = tgt[1] + d * sinf(c->pitch);
	c->eye[2] = tgt[2] + d * cosf(c->yaw) * cp;
	// planes: measured from the game's own (real) eye position, which is dr in front of the target; the emulated eye is d - dr further back
	float dr = lerpf(C2_DIST, d3, e);
	c->nearP = fmaxf(C_NEAR3, d - dr + C_NEAR3);
	c->farP = d - dr + lerpf(1024.0f, C_FAR, e);
}

void play_cam_update(Play* p, float dt)
{
	// x/z follow Mario with the game's 8 %-per-frame smoothing (x limited to the road range), y follows the ground (not jumps)
	float k = 1.0f - powf(1.0f - CAM_FOLLOW, dt * 60.0f);
	float gx = fmaxf(cam_xMin - X_MARGIN, fminf(cam_xMax + X_MARGIN, p->pos[0]));
	if (!p->camInit) {
		p->camX = gx; p->camY = p->pos[1]; p->camZ = p->pos[2]; p->camInit = true;
	}
	p->camX += (gx - p->camX) * k;
	p->camZ += (p->pos[2] - p->camZ) * k;
	if (p->grounded) p->camY += (p->pos[1] - p->camY) * k;
}

void play_projection(C3D_Mtx* proj)
{
	Play dummy; memset(&dummy, 0, sizeof dummy);
	dummy.camInit = true;
	play_projection_stereo(&dummy, proj, 0, 0.0f);
}

void play_projection_stereo(const Play* p, C3D_Mtx* proj, int eye, float slider)
{
	CamPose c; cam_pose(p, &c);
	// zero parallax at the look-at point; separation = slider x 3 % of the (real, not emulated) viewing distance
	float realDist = fminf(c.dist, 60.0f);
	float iod = eye * slider * STEREO_IOD_FRACTION * realDist;
	Mtx_PerspStereoTilt(proj, C3D_AngleFromDegrees(c.fov), C3D_AspectRatioTop, c.nearP, c.farP, iod, c.dist, false);
}

void play_camera(const Play* p, C3D_Mtx* view, float* yaw)
{
	CamPose c; cam_pose(p, &c);
	Mtx_Identity(view);
	Mtx_RotateX(view, c.pitch, true);          // looking down by `pitch`
	Mtx_RotateY(view, -c.yaw, true);
	Mtx_Translate(view, -c.eye[0], -c.eye[1], -c.eye[2], true);
	*yaw = c.yaw;
}
