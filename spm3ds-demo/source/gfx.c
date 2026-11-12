#include "gfx.h"
#include <tex3ds.h>
#include <string.h>
#include "vshader_shbin.h"
#include "checker_t3x.h"

static DVLB_s* vshader_dvlb;
static shaderProgram_s program;
static int uLoc_projection, uLoc_modelView;
static C3D_Tex checker;
static bool texturedState = true;

void gfx_init(void)
{
	vshader_dvlb = DVLB_ParseFile((u32*)vshader_shbin, vshader_shbin_size);
	shaderProgramInit(&program);
	shaderProgramSetVsh(&program, &vshader_dvlb->DVLE[0]);
	C3D_BindProgram(&program);

	uLoc_projection = shaderInstanceGetUniformLocation(program.vertexShader, "projection");
	uLoc_modelView  = shaderInstanceGetUniformLocation(program.vertexShader, "modelView");

	C3D_AttrInfo* attr = C3D_GetAttrInfo();
	AttrInfo_Init(attr);
	AttrInfo_AddLoader(attr, 0, GPU_SHORT, 4);          // v0 = position (+pad)
	AttrInfo_AddLoader(attr, 1, GPU_SHORT, 2);          // v1 = texcoord
	AttrInfo_AddLoader(attr, 2, GPU_UNSIGNED_BYTE, 4);  // v2 = colour

	Tex3DS_Texture t3x = Tex3DS_TextureImport(checker_t3x, checker_t3x_size, &checker, NULL, false);
	if (!t3x)
		svcBreak(USERBREAK_PANIC);
	Tex3DS_TextureFree(t3x);
	C3D_TexSetFilter(&checker, GPU_LINEAR, GPU_NEAREST);
	C3D_TexSetWrap(&checker, GPU_REPEAT, GPU_REPEAT);
}

void gfx_exit(void)
{
	C3D_TexDelete(&checker);
	shaderProgramFree(&program);
	DVLB_Free(vshader_dvlb);
}

C3D_Tex* gfx_checker(void) { return &checker; }

void gfx_bind_vbo(const void* vbo)
{
	C3D_BufInfo* buf = C3D_GetBufInfo();
	BufInfo_Init(buf);
	BufInfo_Add(buf, vbo, sizeof(Vertex), 3, 0x210);
}

void gfx_set_matrices(const C3D_Mtx* proj, const C3D_Mtx* view)
{
	C3D_Mtx mv = *view;
	Mtx_Scale(&mv, POS_SCALE, POS_SCALE, POS_SCALE);   // mv = view * scale(1/64)
	C3D_FVUnifMtx4x4(GPU_VERTEX_SHADER, uLoc_projection, proj);
	C3D_FVUnifMtx4x4(GPU_VERTEX_SHADER, uLoc_modelView, &mv);
}

void gfx_set_textured(bool textured)
{
	C3D_TexEnv* env = C3D_GetTexEnv(0);
	C3D_TexEnvInit(env);
	if (textured) {
		C3D_TexEnvSrc(env, C3D_Both, GPU_TEXTURE0, GPU_PRIMARY_COLOR, 0);
		C3D_TexEnvFunc(env, C3D_Both, GPU_MODULATE);
	} else {
		C3D_TexEnvSrc(env, C3D_Both, GPU_PRIMARY_COLOR, 0, 0);
		C3D_TexEnvFunc(env, C3D_Both, GPU_REPLACE);
	}
	texturedState = textured;
}

void gfx_set_cull(CullMode m)
{
	static const GPU_CULLMODE map[CULL_MODES] = { GPU_CULL_BACK_CCW, GPU_CULL_NONE, GPU_CULL_BACK_CCW, GPU_CULL_FRONT_CCW };
	C3D_CullFace(map[m]);
}

const char* gfx_cull_name(CullMode m)
{
	static const char* names[CULL_MODES] = { "auto", "none", "back", "front" };
	return names[m];
}
