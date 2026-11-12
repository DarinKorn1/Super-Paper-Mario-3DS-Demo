// spm3ds-demo, week 3: Flipside room (mac_02) with Mario, game camera, movement and collision (PLAY),
// a free-fly viewer (ROOM) and a stress test (STRESS).
// Top screen: 3D. Bottom screen: statistics and the button list.
// SELECT cycles PLAY -> ROOM -> STRESS, START quits.
// Timings are only meaningful on a real console; emulator numbers must not drive decisions.
#include <3ds.h>
#include <citro3d.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "gfx.h"
#include "room.h"
#include "stress.h"
#include "mario.h"
#include "play.h"
#include "hit.h"
#include "audio.h"

#define ASSET_DIR "sdmc:/3ds/spm3ds-demo/"
#define CLEAR_COLOR 0x68B0D8FF

#define DISPLAY_TRANSFER_FLAGS \
	(GX_TRANSFER_FLIP_VERT(0) | GX_TRANSFER_OUT_TILED(0) | GX_TRANSFER_RAW_COPY(0) | \
	GX_TRANSFER_IN_FORMAT(GX_TRANSFER_FMT_RGBA8) | GX_TRANSFER_OUT_FORMAT(GX_TRANSFER_FMT_RGB8) | \
	GX_TRANSFER_SCALING(GX_TRANSFER_SCALE_NO))

typedef enum { MODE_PLAY, MODE_ROOM, MODE_STRESS } Mode;

typedef struct {
	float pos[3];
	float yaw, pitch;      // radians; yaw 0 looks along -z
	float speed;           // world units per second
} Camera;

static void camera_reset(Camera* c, bool haveRoom)
{
	memset(c, 0, sizeof *c);
	c->speed = 80.0f;
	if (haveRoom)
		room_start_position(c->pos);
}

static void camera_update(Camera* c, float dt, u32 held)
{
	circlePosition cp, cs;
	hidCircleRead(&cp);
	hidCstickRead(&cs);
	float mx = fabsf((float)cp.dx) > 15.0f ? cp.dx / 156.0f : 0.0f;   // dead zones
	float my = fabsf((float)cp.dy) > 15.0f ? cp.dy / 156.0f : 0.0f;
	float lx = fabsf((float)cs.dx) > 15.0f ? cs.dx / 146.0f : 0.0f;
	float ly = fabsf((float)cs.dy) > 15.0f ? cs.dy / 146.0f : 0.0f;

	c->yaw   -= lx * 1.8f * dt;
	c->pitch += ly * 1.8f * dt;
	if (c->pitch >  1.55f) c->pitch =  1.55f;
	if (c->pitch < -1.55f) c->pitch = -1.55f;

	float cy = cosf(c->yaw), sy = sinf(c->yaw), cp_ = cosf(c->pitch), sp = sinf(c->pitch);
	float fwd[3] = { -cp_ * sy, sp, -cp_ * cy };
	float right[3] = { cy, 0.0f, -sy };
	for (int i = 0; i < 3; i++)
		c->pos[i] += (fwd[i] * my + right[i] * mx) * c->speed * dt;
	if (held & KEY_R) c->pos[1] += c->speed * dt;
	if (held & KEY_L) c->pos[1] -= c->speed * dt;
}

static void camera_view(const Camera* c, C3D_Mtx* view)
{
	Mtx_Identity(view);
	Mtx_RotateX(view, -c->pitch, true);
	Mtx_RotateY(view, -c->yaw, true);
	Mtx_Translate(view, -c->pos[0], -c->pos[1], -c->pos[2], true);
}

int main(void)
{
	gfxInitDefault();
	C3D_Init(0x80000);   // 512 KB command buffer: ~120 draw calls with state changes fit easily

	PrintConsole bottom;
	consoleInit(GFX_BOTTOM, &bottom);

	C3D_RenderTarget* target = C3D_RenderTargetCreate(240, 400, GPU_RB_RGBA8, GPU_RB_DEPTH24_STENCIL8);
	C3D_RenderTargetSetOutput(target, GFX_TOP, GFX_LEFT, DISPLAY_TRANSFER_FLAGS);
	C3D_RenderTarget* targetR = C3D_RenderTargetCreate(240, 400, GPU_RB_RGBA8, GPU_RB_DEPTH24_STENCIL8);   // right eye
	C3D_RenderTargetSetOutput(targetR, GFX_TOP, GFX_RIGHT, DISPLAY_TRANSFER_FLAGS);

	osSetSpeedupEnable(true);   // New 3DS: 804 MHz + L2 cache. No-op elsewhere.
	bool isNew = false;
	APT_CheckNew3DS(&isNew);

	gfx_init();
	if (!stress_init())
		svcBreak(USERBREAK_PANIC);

	char err[160] = "";
	bool haveRoom = room_load(ASSET_DIR, err, sizeof err);
	u32 mainTris = 0, okuTris = 0, texTotal = 0, texMissing = 0;
	if (haveRoom)
		room_counts(&mainTris, &okuTris, &texTotal, &texMissing);

	char err2[160] = "";
	bool haveMario = haveRoom && mario_load(ASSET_DIR, err2, sizeof err2);
	bool haveHit = haveRoom && hit_load(ASSET_DIR "room_hit.bin");
	char err3[160] = "";
	bool haveMusic = haveRoom && audio_init(ASSET_DIR, err3, sizeof err3);
	Play play;
	play_init(&play, haveHit);
	C3D_Mtx projPlay;
	play_projection(&projPlay);

	bool showDebug = false;   // play mode: Y toggles the debug stats (and enables the Mario scale control)
	Mode mode = haveRoom ? MODE_PLAY : MODE_STRESS;
	Camera cam;
	camera_reset(&cam, haveRoom);
	RoomOptions opt = { true, true, true, CULL_AUTO };

	C3D_Mtx proj;
	Mtx_PerspTilt(&proj, C3D_AngleFromDegrees(60.0f), C3D_AspectRatioTop, 1.0f, 2000.0f, false);

	u64 startTime = osGetTime(), lastFrame = startTime, lastText = startTime;
	int frames = 0;
	float fps = 0.0f;
	DrawStats st = { 0, 0 };
	bool dirty = true;

	while (aptMainLoop()) {
		hidScanInput();
		u32 down = hidKeysDown(), held = hidKeysHeld();
		if (down & KEY_START)
			break;
		if ((down & KEY_SELECT) && haveRoom) {
			mode = (mode == MODE_PLAY) ? MODE_ROOM : (mode == MODE_ROOM) ? MODE_STRESS : MODE_PLAY;
			dirty = true;
		} else if (down & KEY_SELECT) {
			dirty = true;   // no room loaded: stay in stress mode but refresh the message
		}

		u64 now = osGetTime();
		float dt = (now - lastFrame) / 1000.0f;
		if (dt > 0.1f) dt = 0.1f;
		lastFrame = now;

		if (mode == MODE_PLAY) {
			if (down & KEY_Y) { showDebug = !showDebug; dirty = true; }
			if (down & KEY_R) { audio_toggle_mute(); dirty = true; }
			play_update(&play, dt, down, held, showDebug);
		} else if (mode == MODE_ROOM) {
			camera_update(&cam, dt, held);
			if (down & KEY_X) opt.showOku = !opt.showOku;
			if (down & KEY_A) opt.showBlended = !opt.showBlended;
			if (down & KEY_Y) opt.cull = (opt.cull + 1) % CULL_MODES;
			if (down & KEY_B) camera_reset(&cam, haveRoom);
			if (down & KEY_DUP)   cam.speed *= 1.5f;
			if (down & KEY_DDOWN) cam.speed /= 1.5f;
			if (cam.speed < 5.0f) cam.speed = 5.0f;
			if (cam.speed > 1000.0f) cam.speed = 1000.0f;
		} else {
			if (down & (KEY_DUP | KEY_DRIGHT))   { stress_set_level(stress_level() + 1); dirty = true; }
			if (down & (KEY_DDOWN | KEY_DLEFT))  { stress_set_level(stress_level() - 1); dirty = true; }
		}

		// Stereo 3D only in play mode and only while the 3D slider is up; otherwise one flat image (the right eye is not drawn,
		// which also saves half the GPU work). gfxSet3D must change before the frame is drawn.
		float slider = osGet3DSliderState();
		bool stereo = (mode == MODE_PLAY) && slider > 0.02f;
		gfxSet3D(stereo);

		C3D_FrameBegin(C3D_FRAME_SYNCDRAW);
			for (int eye = 0; eye < (stereo ? 2 : 1); eye++) {
				C3D_RenderTarget* t = eye ? targetR : target;
				C3D_RenderTargetClear(t, C3D_CLEAR_ALL, CLEAR_COLOR, 0);
				C3D_FrameDrawOn(t);
				if (mode == MODE_PLAY) {
					C3D_Mtx view, projEye;
					float yaw;
					play_camera(&play, &view, &yaw);
					if (stereo) play_projection_stereo(&play, &projEye, eye ? 1 : -1, slider);
					else projEye = projPlay;
					gfx_set_matrices(&projEye, &view);
					DrawStats rs = room_draw(&opt);
					DrawStats ms = mario_draw(&projEye, &view, play.pos, yaw, -play.face, play.scale, play.anim, play.animTime);
					if (eye == 0) { st.tris = rs.tris + ms.tris; st.calls = rs.calls + ms.calls; }
				} else if (mode == MODE_ROOM) {
					C3D_Mtx view;
					camera_view(&cam, &view);
					gfx_set_matrices(&proj, &view);
					st = room_draw(&opt);
				} else {
					st = stress_draw(&proj, (now - startTime) / 1000.0f);
				}
			}
		C3D_FrameEnd(0);

		frames++;
		now = osGetTime();
		if (now - lastText >= 500 || dirty) {
			if (now - lastText >= 500) {
				fps = frames * 1000.0f / (float)(now - lastText);
				frames = 0;
				lastText = now;
			}
			dirty = false;
			consoleClear();
			if (mode == MODE_PLAY && !showDebug) {
				printf("SUPER PAPER MARIO - Flipside\n\n");
				printf("Circle pad  walk\n");
				printf("A           jump\n");
				printf("X           flip 2D / 3D\n");
				printf("B           reset Mario\n");
				printf("R           music on / off (%s)\n", !haveMusic ? "not loaded" : audio_muted() ? "off" : "on");
				printf("Y           debug screen\n");
				printf("SELECT      free camera / stress\n");
				printf("START       quit\n");
			} else if (mode == MODE_PLAY) {
				printf("DEBUG  %s view\n\n", play.mode3d ? "3D" : "2D");
				printf("Triangles: %lu   Draws: %lu\n", st.tris, st.calls);
				printf("FPS:%5.1f CPU%5.1f GPU%5.1f ms\n", fps, C3D_GetProcessingTime(), C3D_GetDrawingTime());
				printf("Mario %.1f %.1f %.1f %s\n", play.pos[0], play.pos[1], play.pos[2], play.grounded ? "ground" : "air");
				printf("Model: %s, %d anims, %s\n", haveMario ? "ok" : err2, mario_anim_count(), play.anim ? "walk" : "idle");
				printf("Scale %.3f  height %.2f units (%.0f game)\n", play.scale, play_height(&play), play_height(&play) * 8.0f);
				printf("Music: %s\n", haveMusic ? (audio_muted() ? "muted" : "playing") : err3);
				printf("Collision: %d tris%s\n", hit_count(), haveHit ? "" : " (NOT loaded: flat y=0)");
				printf("\nL + D-pad up/down: Mario scale (L+B reset)\n");
				printf("Y back to controls\n");
			} else if (mode == MODE_ROOM) {
				printf("ROOM  mac_02 (Flipside)\n\n");
				printf("Triangles: %lu   Draws: %lu\n", st.tris, st.calls);
				printf("FPS:  %5.1f\n", fps);
				printf("CPU:  %5.2f ms\n", C3D_GetProcessingTime());
				printf("GPU:  %5.2f ms\n", C3D_GetDrawingTime());
				printf("Cmd buffer: %3.0f %%\n", C3D_GetCmdBufUsage() * 100.0f);
				printf("\noku: %s  blended: %s  cull: %s\n", opt.showOku ? "ON" : "off",
				       opt.showBlended ? "ON" : "off", gfx_cull_name(opt.cull));
				printf("Pos %.0f %.0f %.0f  speed %.0f\n", cam.pos[0], cam.pos[1], cam.pos[2], cam.speed);
				printf("Tex: %lu loaded, %lu missing\n", texTotal - texMissing, texMissing);
				printf("\nCircle pad move  C-stick look\n");
				printf("L/R down/up  D-pad U/D speed\n");
				printf("X oku  A blended  Y cull  B reset\n");
				printf("SELECT stress mode  START quit\n");
			} else {
				printf("STRESS TEST\n\n");
				printf("Triangles: %lu (level %d/%d)\n", st.tris, stress_level() + 1, STRESS_STEPS);
				printf("Draw calls: %lu\n", st.calls);
				printf("FPS:  %5.1f\n", fps);
				printf("CPU:  %5.2f ms\n", C3D_GetProcessingTime());
				printf("GPU:  %5.2f ms\n", C3D_GetDrawingTime());
				printf("Cmd buffer: %3.0f %%\n", C3D_GetCmdBufUsage() * 100.0f);
				printf("\nNew 3DS: %s\n", isNew ? "yes" : "no");
				printf("\nD-pad up/right: more triangles\n");
				printf("D-pad down/left: fewer (5k steps)\n");
				if (haveRoom)
					printf("SELECT room mode  START quit\n");
				else
					printf("START quit\n\nRoom not loaded:\n%s\n", err);
			}
		}
	}

	audio_exit();
	mario_free();
	hit_free();
	room_free();
	stress_exit();
	gfx_exit();
	C3D_Fini();
	gfxExit();
	return 0;
}
