// spm3ds-demo: week-1 smoke test.
// A spinning textured cube on the top screen, frame rate and GPU/CPU timing on the bottom screen.
// Based on the devkitPro "textured_cube" example (public domain / zlib-style licence).
#include <3ds.h>
#include <citro3d.h>
#include <tex3ds.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include "vshader_shbin.h"
#include "checker_t3x.h"

#define CLEAR_COLOR 0x68B0D8FF

#define DISPLAY_TRANSFER_FLAGS \
	(GX_TRANSFER_FLIP_VERT(0) | GX_TRANSFER_OUT_TILED(0) | GX_TRANSFER_RAW_COPY(0) | \
	GX_TRANSFER_IN_FORMAT(GX_TRANSFER_FMT_RGBA8) | GX_TRANSFER_OUT_FORMAT(GX_TRANSFER_FMT_RGB8) | \
	GX_TRANSFER_SCALING(GX_TRANSFER_SCALE_NO))

typedef struct { float position[3]; float texcoord[2]; float normal[3]; } vertex;

// One face = 2 triangles. The cube is built from 6 faces below.
#define FACE(a, b, c, d, nx, ny, nz) \
	{ a, {0.0f, 0.0f}, {nx, ny, nz} }, { b, {1.0f, 0.0f}, {nx, ny, nz} }, { c, {1.0f, 1.0f}, {nx, ny, nz} }, \
	{ c, {1.0f, 1.0f}, {nx, ny, nz} }, { d, {0.0f, 1.0f}, {nx, ny, nz} }, { a, {0.0f, 0.0f}, {nx, ny, nz} }

#define P(x, y, z) {x * 0.5f, y * 0.5f, z * 0.5f}

static const vertex vertex_list[] = {
	FACE(P(-1,-1,+1), P(+1,-1,+1), P(+1,+1,+1), P(-1,+1,+1),  0,  0, +1), // +Z
	FACE(P(-1,-1,-1), P(-1,+1,-1), P(+1,+1,-1), P(+1,-1,-1),  0,  0, -1), // -Z
	FACE(P(+1,-1,-1), P(+1,+1,-1), P(+1,+1,+1), P(+1,-1,+1), +1,  0,  0), // +X
	FACE(P(-1,-1,-1), P(-1,-1,+1), P(-1,+1,+1), P(-1,+1,-1), -1,  0,  0), // -X
	FACE(P(-1,+1,-1), P(-1,+1,+1), P(+1,+1,+1), P(+1,+1,-1),  0, +1,  0), // +Y
	FACE(P(-1,-1,-1), P(+1,-1,-1), P(+1,-1,+1), P(-1,-1,+1),  0, -1,  0), // -Y
};
#define vertex_list_count (sizeof(vertex_list) / sizeof(vertex_list[0]))

static DVLB_s* vshader_dvlb;
static shaderProgram_s program;
static int uLoc_projection, uLoc_modelView;
static int uLoc_lightVec, uLoc_lightHalfVec, uLoc_lightClr, uLoc_material;
static C3D_Mtx projection;
static C3D_Mtx material = {
	{
	{ { 0.0f, 0.2f, 0.2f, 0.2f } }, // Ambient
	{ { 0.0f, 0.4f, 0.4f, 0.4f } }, // Diffuse
	{ { 0.0f, 0.8f, 0.8f, 0.8f } }, // Specular
	{ { 1.0f, 0.0f, 0.0f, 0.0f } }, // Emission
	}
};

static void* vbo_data;
static C3D_Tex tex;
static float angleX = 0.0f, angleY = 0.0f;

static bool loadTextureFromMem(C3D_Tex* t, const void* data, size_t size)
{
	Tex3DS_Texture t3x = Tex3DS_TextureImport(data, size, t, NULL, false);
	if (!t3x)
		return false;
	Tex3DS_TextureFree(t3x);
	return true;
}

static void sceneInit(void)
{
	vshader_dvlb = DVLB_ParseFile((u32*)vshader_shbin, vshader_shbin_size);
	shaderProgramInit(&program);
	shaderProgramSetVsh(&program, &vshader_dvlb->DVLE[0]);
	C3D_BindProgram(&program);

	uLoc_projection   = shaderInstanceGetUniformLocation(program.vertexShader, "projection");
	uLoc_modelView    = shaderInstanceGetUniformLocation(program.vertexShader, "modelView");
	uLoc_lightVec     = shaderInstanceGetUniformLocation(program.vertexShader, "lightVec");
	uLoc_lightHalfVec = shaderInstanceGetUniformLocation(program.vertexShader, "lightHalfVec");
	uLoc_lightClr     = shaderInstanceGetUniformLocation(program.vertexShader, "lightClr");
	uLoc_material     = shaderInstanceGetUniformLocation(program.vertexShader, "material");

	C3D_AttrInfo* attrInfo = C3D_GetAttrInfo();
	AttrInfo_Init(attrInfo);
	AttrInfo_AddLoader(attrInfo, 0, GPU_FLOAT, 3); // v0 = position
	AttrInfo_AddLoader(attrInfo, 1, GPU_FLOAT, 2); // v1 = texcoord
	AttrInfo_AddLoader(attrInfo, 2, GPU_FLOAT, 3); // v2 = normal

	Mtx_PerspTilt(&projection, C3D_AngleFromDegrees(80.0f), C3D_AspectRatioTop, 0.01f, 1000.0f, false);

	// Vertex data must live in "linear" memory so the GPU can read it.
	vbo_data = linearAlloc(sizeof(vertex_list));
	memcpy(vbo_data, vertex_list, sizeof(vertex_list));

	C3D_BufInfo* bufInfo = C3D_GetBufInfo();
	BufInfo_Init(bufInfo);
	BufInfo_Add(bufInfo, vbo_data, sizeof(vertex), 3, 0x210);

	if (!loadTextureFromMem(&tex, checker_t3x, checker_t3x_size))
		svcBreak(USERBREAK_PANIC);
	C3D_TexSetFilter(&tex, GPU_LINEAR, GPU_NEAREST);
	C3D_TexBind(0, &tex);

	C3D_TexEnv* env = C3D_GetTexEnv(0);
	C3D_TexEnvInit(env);
	C3D_TexEnvSrc(env, C3D_Both, GPU_TEXTURE0, GPU_PRIMARY_COLOR, 0);
	C3D_TexEnvFunc(env, C3D_Both, GPU_MODULATE);
}

static void sceneRender(void)
{
	C3D_Mtx modelView;
	Mtx_Identity(&modelView);
	Mtx_Translate(&modelView, 0.0f, 0.0f, -2.0f + 0.5f * sinf(angleX), true);
	Mtx_RotateX(&modelView, angleX, true);
	Mtx_RotateY(&modelView, angleY, true);

	angleX += M_PI / 180;
	angleY += M_PI / 360;

	C3D_FVUnifMtx4x4(GPU_VERTEX_SHADER, uLoc_projection, &projection);
	C3D_FVUnifMtx4x4(GPU_VERTEX_SHADER, uLoc_modelView,  &modelView);
	C3D_FVUnifMtx4x4(GPU_VERTEX_SHADER, uLoc_material,   &material);
	C3D_FVUnifSet(GPU_VERTEX_SHADER, uLoc_lightVec,     0.0f, 0.0f, -1.0f, 0.0f);
	C3D_FVUnifSet(GPU_VERTEX_SHADER, uLoc_lightHalfVec, 0.0f, 0.0f, -1.0f, 0.0f);
	C3D_FVUnifSet(GPU_VERTEX_SHADER, uLoc_lightClr,     1.0f, 1.0f,  1.0f, 1.0f);

	C3D_DrawArrays(GPU_TRIANGLES, 0, vertex_list_count);
}

static void sceneExit(void)
{
	C3D_TexDelete(&tex);
	linearFree(vbo_data);
	shaderProgramFree(&program);
	DVLB_Free(vshader_dvlb);
}

int main(void)
{
	gfxInitDefault();
	C3D_Init(C3D_DEFAULT_CMDBUF_SIZE);

	// Bottom screen: plain text console for the frame rate. Top screen: citro3d.
	PrintConsole bottom;
	consoleInit(GFX_BOTTOM, &bottom);

	C3D_RenderTarget* target = C3D_RenderTargetCreate(240, 400, GPU_RB_RGBA8, GPU_RB_DEPTH24_STENCIL8);
	C3D_RenderTargetSetOutput(target, GFX_TOP, GFX_LEFT, DISPLAY_TRANSFER_FLAGS);

	// On a New 3DS this switches the CPU to 804 MHz and enables the extra L2 cache.
	// On an old 3DS (and in some emulators) it is a no-op.
	osSetSpeedupEnable(true);
	bool isNew = false;
	APT_CheckNew3DS(&isNew);

	sceneInit();

	u64 lastTime = osGetTime();
	int frames = 0;
	float fps = 0.0f;

	while (aptMainLoop()) {
		hidScanInput();
		if (hidKeysDown() & KEY_START)
			break; // back to the Homebrew Launcher

		C3D_FrameBegin(C3D_FRAME_SYNCDRAW);
			C3D_RenderTargetClear(target, C3D_CLEAR_ALL, CLEAR_COLOR, 0);
			C3D_FrameDrawOn(target);
			sceneRender();
		C3D_FrameEnd(0);

		frames++;
		u64 now = osGetTime();
		if (now - lastTime >= 500) { // update the text twice a second
			fps = frames * 1000.0f / (float)(now - lastTime);
			frames = 0;
			lastTime = now;

			consoleClear();
			printf("spm3ds-demo  (cube test)\n\n");
			printf("FPS:        %5.1f\n", fps);
			// citro3d reports milliseconds; x6 turns that into % of a 16.7 ms (60 fps) frame.
			printf("CPU time:   %5.2f ms (%3.0f %% of 60fps)\n", C3D_GetProcessingTime(), C3D_GetProcessingTime() * 6.0f);
			printf("GPU time:   %5.2f ms (%3.0f %% of 60fps)\n", C3D_GetDrawingTime(), C3D_GetDrawingTime() * 6.0f);
			printf("Cmd buffer: %5.1f %%\n", C3D_GetCmdBufUsage() * 100.0f);
			printf("\nNew 3DS:    %s\n", isNew ? "yes (804 MHz mode)" : "no");
			printf("Triangles:  %d\n", (int)(vertex_list_count / 3));
			printf("\nSTART = exit\n");
		}
	}

	sceneExit();
	C3D_Fini();
	gfxExit();
	return 0;
}
