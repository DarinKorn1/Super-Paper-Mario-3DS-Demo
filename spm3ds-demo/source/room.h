// Loader and renderer for rooms converted by tools/convert_room.py.
#pragma once
#include "gfx.h"

typedef struct {
	u32 tris;      // triangles submitted this frame
	u32 calls;     // draw calls this frame
} DrawStats;

typedef struct {
	bool showMain, showOku, showBlended;
	CullMode cull;
} RoomOptions;

// Loads room_main.spm, room_oku.spm and textures/*.t3x from `dir` (e.g. "sdmc:/3ds/spm3ds-demo/").
// On failure returns false and writes a short reason into `err`.
bool room_load(const char* dir, char* err, size_t errSize);
void room_free(void);
void room_start_position(float pos[3]);
void room_counts(u32* mainTris, u32* okuTris, u32* textures, u32* texturesMissing);
DrawStats room_draw(const RoomOptions* opt);
