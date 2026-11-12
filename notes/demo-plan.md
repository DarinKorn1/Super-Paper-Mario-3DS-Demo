# Demo plan: Mario walking around Flipside `mac_02` on New 3DS XL

Status: 2026-11-12, week 1. Everything below was read from the extracted USA disc
(`NewSuperPaperBros/Disc/DATA/files`) with throw-away Python scripts kept outside the repo.
Nothing extracted from the disc is committed. "Confirmed" = I parsed the real file and the numbers
are self-consistent. "Guess" = plausible but not verified.

## 1. Toolchain (checked, nothing installed)

devkitARM (GCC 16.1.0), libctru, citro3d, citro2d, tex3ds, picasso, 3dsxtool, 3dslink, smdhtool:
all present in `C:\devkitPro`. The cube in `spm3ds-demo/` builds
cleanly. Build it from the devkitPro MSYS2 shell (plain Git Bash does not set `DEVKITARM`):

    C:\devkitPro\msys2\usr\bin\bash.exe -lc 'cd /c/Users/ender/SPM_N3DS_XL/spm3ds-demo && make'

Not yet tested: running the `.3dsx` on the console or in Azahar (Azahar is not installed).

## 2. File formats (with evidence)

### 2.1 Container: `map/mac_02.bin`
- Nintendo LZ10 (first byte `0x10`, 24-bit size `0x27E1E0`) wrapping a **U8 archive** (magic `55 AA 38 2D`).
  Decompressed size 2,613,728 = the size in the header (confirmed).
- U8 contents (confirmed):

  | File | Bytes | What |
  |---|---|---|
  | `dvd/map/mac_02/map.dat` | 1,451,642 | geometry, materials, collision, animations |
  | `dvd/map/mac_02/texture.tpl` | 1,043,808 | 89 textures |
  | `dvd/map/mac_02/camera_road.bin` | 8,872 | camera path ("SPMario_CameraRoadExport") |
  | `dvd/bg/mac_02_02..08.tpl` | 2 KB x5, 41 KB, 57 KB | backdrop layers (CMPR, one is 512x224) |

### 2.2 `map.dat` (big-endian)
Header 0x20 bytes: `fileSize, mainDataSize, relocCount, chunkCount`. For mac_02: `0x16267A` (equals file size,
confirmed), `0x1497B0`, `0x6380`, `8`. Then main data, a table of `relocCount` u32 offsets (all pointers inside
main data are stored as offsets from the start of main data), an 8-entry chunk table, and a string table. This
matches `MapFileHeader`/`MapFileChunk` in spm-decomp `mapdrv.h` and `_mapLoad` in the ttyd decomp.

Chunks: `information`, `texture_table` (89 names), `material_name_table` (118), `vcd_table`, `light_table`
(0 lights), `fog_table` (1 entry), `animation_table` (31), `curve_table` (0).

- **Scene tree.** `information` -> joint tree. Each joint (`MapFileJoint`, 0x60 bytes + parts) has name, type
  (`null`/`mesh`), parent/child/next/prev, scale, rotation (degrees), translation. Root `world_root` has children
  **`S`** (visible scenery, 1020 joints) and **`A`** (collision, 261 joints) plus 4 loose meshes. This matches
  the `mapName`/`hitName` fields of `MapFileInfo` (S = map model, A = hit model). Confirmed by structure; that
  the `A` tree is collision is an inference (names like `A2_dokan_01`, `A2_doa_in_01`, `..._yuka` = pipe, door,
  floor, and its meshes have no texture coordinates).
- **Mesh parts.** A mesh joint has `partTableCount` parts of `{material*, mesh*}`. Mesh = `{flag, packed=1,
  displayListCount, elementMask, vcd offset, [offset,size]...}`.
- **Geometry = GX display lists**, every one a triangle strip (opcode `0x98`, 16-bit count). All 12,324 lists in
  `S` parsed with zero errors. A vertex is a sequence of u16 indices, one per set bit of `elementMask`
  (bit0 position, bit1 normal, bit2 colour, bit4 tex0; masks seen: 3, 7, 19, 23).
- **Vertex arrays** (offsets from `vcd_table`; each starts with a u32 count): positions at `0x9E0`
  (24,157 x s16x3, **7 fractional bits**, i.e. value/128), normals at `0x24020` (1,135 x s8x3, 6 fractional bits),
  texcoords at `0x24D80` (8,308 x u16x2), colours at `0x2CF60` (404 x RGBA8). The counts equal the highest index
  used + 1 (confirmed), and the /128 scale reproduces plausible object sizes (a 22.5 x 2.5 x 29 box).
  Guess: the texcoord fractional scale (needs checking against a known texture).
- **Materials** (116 distinct in `S`): name, RGBA colour, texture-reference list (12-byte entries: pointer to a
  texture entry, wrap S/T bytes). Per-joint `drawMode` byte 1 = cull mode (1 or 3). **Not decoded:** which
  texture index a texture entry maps to, TEV/blend modes, UV transforms. The decomp's `mapSetMaterialTev`
  (ttyd) shows 4+ TEV set-ups (modulate, 2-texture blends) that I'd need to translate to 3DS TexEnv.
- **Animation table**: 31 entries `{name, ?, duration, meshTracks, materialTrack}` (confirmed names/durations).
  Mesh tracks are `{meshName, translation, rotation, scale, ... frameCount}`; keyframe layout not decoded.

### 2.3 `texture.tpl`
Standard Wii TPL (magic `0x0020AF30`), 89 images, no palettes, no mipmaps (sum of base levels 1,039,872 B ~ file
size). Formats: CMPR (DXT1-like, 71), IA4 (8), RGB5A3 (6), RGB565 (3), IA8 (1). Sizes: all power-of-two
(128x128 x23, 64x64 x17, 32x32 x11, 128x256 x10, 256x256 x7, ...).

### 2.4 Collision
No separate hit file: collision is the `A` tree in `map.dat`. spm-decomp `hitdrv.h`: `HitObj` per joint with
`attr` bitflags (from `drawMode`), `tris[totalTri]` each with a computed normal. `A` has 192 mesh joints, 2,246
triangles, 3,889 unique vertices. `drawMode` attr values seen: 0 (180 joints), 4096, 131072, 557056 (meaning
unknown; probably pipe/door/ceiling-type flags). Hit-test code (`hitCheckFilter`, etc.) is not decompiled yet;
for the demo I will write my own: floor = triangles whose normal points up.

### 2.5 Mario (sprite animations)
`a/p_mario` (291,528 B, uncompressed `AnimPoseData`, header size `0x15F5C`, model name `p_mario`, build
"Mon Jan 29 10:31:59 2007") + `a/p_mario-` (TPL, 598,464 B). Header matches `animdrv.h` exactly (confirmed):
90 shapes, 96 polygons, 324 vertex positions, 126 textures (all CMPR, mostly NOT power-of-two: 72x72, 88x88,
112x104, 184x216...), 4,224 group-transform records, 176 groups, **94 animations** (`mario_W_1` walk,
`mario_S_1` idle, `mario_R_1` run, `mario_J_1A..C` jump, ...). So "paper Mario" is a tiny 3D model of flat textured
parts. Each animation has keyframes plus per-keyframe deltas for vertex positions, group transforms and
visibility groups (`mario_W_1`: 17 keyframes, 528 vertex-position deltas, 240 group-transform deltas). The delta
encoding is **not decoded**; `filemgr.c` only shows pointer relocation for it.

## 3. `mac_02` measurements (from the real files)

| Item | Value |
|---|---|
| Scene joints | 1,286 (798 + 192 mesh joints, `S` and `A`) |
| Visible triangles (`S`) | **30,894** in 992 mesh parts / 12,324 strips (55,542 strip vertices) |
| Unique vertices (`S`) | 45,353 (fits 16-bit indices) |
| Where: | `oku` 17,762 (57%), `sima` 4,431, `tou` 4,334, `mae` 3,975, rest < 110 each |
| Collision triangles (`A`) | 2,246 (3,889 unique vertices) |
| Textures | **89**, 1,039,872 B on Wii (CMPR 4 bpp) |
| Textures after ETC1/ETC1A4 | about 1.0-1.5 MB (CMPR is 4 bpp, ETC1 is 4 bpp; alpha textures 8 bpp) |
| World extent (`S`) | x -115..139, y -120..168, z -70..170 (world units; Mario is about 27 tall) |
| Draw batches | **118** distinct (material, cull) pairs in `S` if all static geometry is merged by material; about 150 once animated parts (below) are kept apart |
| Fog | 1 entry (type 1), no lights |
| Backdrops | 7 TPLs: 5 tiny, 41 KB, 57 KB (512x224) |

Animated / special (31 animations, confirmed from the table): elevator sets `ereve1..4` (doors `*_doa_l/_r`,
`del_01/02`, `ere3_hon`, `ere3_sui`) = 18 animated joints; `heart_iwa_01/02` (heart rock);
7 coloured door material animations (`doa_red`...`doa_purple`, material tracks only = colour/UV change);
`kirakira` (sparkle, material track), `ereve_botan_01..04` (elevator buttons), `fun` (a group, probably a fan
or fountain). No water seen in the animation names; the `oku` hall may hold hidden or interior geometry I have not
classified. Visible-vs-hidden objects (SPM toggles them with event scripts) are not stored in `map.dat`; they
come from the room's `setup/` script, which I did not read. For the demo: render everything, drop interiors by name
if it looks wrong.

## 4. Converter design (Python, runs on the PC)

Input: the extracted `map/mac_02.bin`. Output: `spm3ds-demo/assets/` (git-ignored) copied to SD (`sdmc:/spm3ds/`).

1. LZ10 + U8 unpack (done as scratch code; about 60 lines).
2. Parse `map.dat` (header, relocs not needed: pointers are offsets), joint tree with full world matrices.
3. Static bake: transform every `S` vertex to world space, de-strip to triangles, group by (material, cull).
   Output one `.vbo` (interleaved: s16x3 position, s16x2 UV, u8x4 colour = 14-16 B), one u16 index buffer and a
   batch table `{texture id, cull, index range}`. Keep animated joints as separate batches with their matrix.
4. Textures: decode CMPR/IA4/IA8/RGB565/RGB5A3 to RGBA, write PNG, run `tex3ds` (ETC1/ETC1A4 for CMPR,
   RGBA4/LA8 for the rest) into one `.t3x` per texture (or one atlas file). Mario's non-power-of-two textures
   get padded to the next power of two.
5. Collision: `A` tree triangles in world space, pre-bucketed into a 2-D grid for the walker (floors, walls).
6. Mario: decode `mario_W_1` / `mario_S_1` first (keyframe -> group transforms, visibility, vertex deltas),
   then bake each keyframe into a vertex buffer or a bone-style transform list.
7. Report: converter prints the same measurements as section 3 so they can be re-checked.

## 5. Fit with the New 3DS at 30 fps (estimate, not measured)

- Geometry: 30.9k triangles total, far fewer in view. PICA200 can push this easily; the cube test already prints
  CPU and GPU ms per frame so we can measure. Vertex data as indexed u16: about 45k x 16 B = 0.7 MB.
- Draw calls: about 150 per frame is fine for citro3d; the 992-mesh-part version (without merging) probably
  is also fine but wastes CPU, so merge.
- Memory: textures about 1-1.5 MB, geometry < 1 MB: trivial against the New 3DS app memory.
- Fill rate: 400x240 top screen, small; fog and multi-texture materials need TexEnv work but are cheap.
- Likely cost centres: Mario's per-frame vertex deltas (CPU, small: 324 vertices) and alpha-blended layers.
- So the budget looks comfortable on paper; the unknowns are in material fidelity, not performance.

## 6. Main risks

1. **Material/TEV semantics** are undecoded (texture index mapping, blend modes, UV scroll). Mitigation: start
   with "first texture x vertex colour" and compare screenshots against `NewSuperPaperBros/screenshots/`.
2. **Mario animation encoding** undecoded; spm-decomp has structs but no decoder. Mitigation: first demo uses the
   static bind-pose model; add animation once the keyframe layout is reverse-engineered (compare with the
   Route B `NewSuperPaperBros` source, which already renders it).
3. **Texture quality**: CMPR to ETC1 re-encoding is lossy and ETC1 has no alpha; alpha-tested textures need ETC1A4.
4. **Unclassified geometry**: 57% of triangles are in `oku`; hidden interiors may show through.
5. **No console testing yet**; Azahar frame rates do not count (user rule).
6. **Licensing/safety**: converted assets stay git-ignored; do not upload the converter's output.
7. spm-docs repo not consulted (needs permission to clone). It may document the material and animation formats
   and would cut risks 1-2.

## 7. Week-2 proposal
Converter steps 1-5 (static room + collision), a free camera with the d-pad, then Mario's bind-pose model and
`mario_W_1`.

## 8. Week 2: room viewer, converter and stress test (2026-11-12)

Status: everything builds without warnings; **nothing has been run** (the build is checked, but I could not run Azahar from here
and there is no console yet). The picture-quality notes below come from reading the data, not from looking at the screen.

### 8.1 What was built (all under `spm3ds-demo/`)
- `tools/convert_room.py` (Python, standard library + the devkitPro `tex3ds` tool). Run from `spm3ds-demo/`:
  `python -I tools/convert_room.py` (reads `NewSuperPaperBros/Disc/DATA/files/map/mac_02.bin`, writes `assets/`, about 7 s).
- `source/`: `main.c` (loop, camera, bottom-screen stats), `room.c` (loader and renderer), `stress.c` (stress mode),
  `gfx.c` (shader setup, vertex format, TexEnv helpers), `vshader.v.pica` (new shader; the old lit-cube shader is gone).
- Room mode: circle pad = move, C-stick = look, L/R = down/up, D-pad up/down = speed x1.5 or /1.5, X = oku on/off,
  A = alpha-blended batches on/off, Y = cull mode (none/back/front), B = reset camera, SELECT = stress mode, START = quit.
- Stress mode: D-pad up/right = more triangles, down/left = fewer (12 levels, 5,000 to 60,000), SELECT = room mode.

### 8.2 Converter output (measured by the converter; also in `assets/report.txt`)
| Part | Triangles | Unique vertices | Draw calls (blended) |
|---|---|---|---|
| `room_main.spm` (everything except oku) | 12,942 | 13,567 | 44 (18) |
| `room_oku.spm` | 16,781 | 19,277 | 67 (28) |
| total | 29,723 | 32,844 | 111 (46) |

- 29,723 instead of the 30,894 in section 3: zero-area triangles inside the strips are dropped.
- Batches are merged by (texture, wrap S/T, cull byte, has-alpha), not by material, because the material colour is baked into the
  vertex colour. 116 materials became 111 draw calls.
- Textures: 89 converted, 269 KB of `.t3x` (ETC1 for 55, ETC1A4 for the 34 that have alpha). None needed resizing (all are
  power-of-two); the resize code is in the converter for Mario's textures later.
- Vertex = 16 bytes (s16 x,y,z,pad; s16 u,v; u8 r,g,b,a); positions are world units x 64 (nothing was clamped). About 0.5 MB of
  vertices and 0.18 MB of indices in total.
- File format (little-endian): header `"SPMR", version, nTex, nVerts, nBatches, nIdx, bbox[6 floats]` (48 bytes), then `nBatches` x 20 bytes
  `{s32 tex (-1 = none), u32 firstIndex, u32 indexCount, u8 cull, u8 wrapS, u8 wrapT, u8 blend, u32 reserved}`, then the vertices,
  then u16 indices. Blended batches come after the opaque ones. `room_oku.spm` has the same layout.
- One sanity check done: a front-view dot plot of the converted vertices shows the street of buildings, the elevator shafts and the
  upper row of structures in sensible places (picture kept outside the repo).

### 8.3 Materials: what is used, what is a guess
Decoded from the real data and used:
- Material colour (RGBA at +4), multiplied into the vertex colour at conversion time.
- First texture of a material: the pointer at `material+0xC` leads to `{texture info*, 0, wrapS, wrapT}`; the texture info's first word
  points to the texture name, which is looked up in the `texture_table` chunk (= TPL image index). All 116 materials resolve.
- Wrap bytes (0 clamp, 1 repeat, 2 mirror; only 1 was seen in the first rows of the report).
- Vertex colour (element bit 2) and texcoords (bit 4, s16 with 7 fractional bits: a guess, but the common values 0/32/64/96/128 fit it).
- Alpha: a texture "has alpha" if any decoded texel has alpha below 250. Those batches are drawn after the opaque ones with alpha test
  (> 0x10) and normal alpha blending. The material flag byte `+0xA == 2` (7 materials, e.g. `lambert1_v_x`) is also treated as blended.

Not decoded, likely to look wrong (**to check on screen; not yet seen**):
1. **TEV modes.** `mapSetMaterialTev` (ttyd decomp) has several modes (modulate, two-texture blends, alpha as mask). I apply only
   "texture 0 x vertex colour". Materials with a second texture lose that layer (the converter ignores texture 2), and the joint's
   `drawMode` is not read.
2. **Cull mode.** Every joint has a cull byte (1 or 3) whose meaning is unknown. The viewer starts with no culling; Y cycles
   back/front, so you can see which one looks right. Strip winding is kept consistent.
3. **Blend ordering.** Blended batches are not depth-sorted; semi-transparent overlaps (glass, fades, `kage` shadow planes) may be
   in the wrong order. Cut-out textures (leaves, fences) should be fine.
4. **UV animation** (the seven coloured doors, `kirakira` sparkle) and **fog** (1 fog entry) are ignored. Animated joints (elevator
   doors etc.) are drawn at their rest pose.
5. **Visibility.** Everything under `S` is drawn, including interiors the game hides with event scripts; `oku` is the most likely place
   for this, hence the X toggle.
6. **ETC1 quality.** Re-encoding CMPR as ETC1 is lossy; small text and signs may look soft.
7. **Lighting.** The map has no lights and the shader does none; colours should be vertex colour x texture, as on the Wii.

### 8.4 Stress-test mode (built, not acted on)
- One mesh of 118 patches on an 11-column grid, each patch a grid of quads, all in one vertex and one index buffer; each patch is
  one `C3D_DrawElements` call, so every level is exactly 118 draw calls. Level n has about 5,000 x n triangles (the screen shows the
  real count, e.g. 4,956 for level 1). Checker texture, no culling, waves in z. The whole mesh is drawn every frame (no frustum
  culling), which is the worst case.
- The bottom screen shows triangles, draw calls, FPS, CPU ms (`C3D_GetProcessingTime`), GPU ms (`C3D_GetDrawingTime`) and command
  buffer use.
- It runs with vsync (`C3D_FRAME_SYNCDRAW`), so FPS is capped at 60; the GPU ms figure shows the headroom.
- **No results yet. On the console, note the highest level that holds 30 fps and 60 fps. Emulator numbers do not count.**

### 8.5 Running it
**Azahar.** Its virtual SD card is `C:\Users\ender\AppData\Roaming\Azahar\sdmc\` (the `sdmc_directory` line in
`Azahar\config\qt-config.ini`).
1. Copy `room_main.spm`, `room_oku.spm` and the `textures` folder from `spm3ds-demo\assets\` into
   `C:\Users\ender\AppData\Roaming\Azahar\sdmc\3ds\spm3ds-demo\` so that
   `...\sdmc\3ds\spm3ds-demo\room_main.spm` and `...\sdmc\3ds\spm3ds-demo\textures\tex_000.t3x` exist.
2. In Azahar use File > Load File and pick `spm3ds-demo\spm3ds-demo.3dsx`.
3. If the room files are missing, the app starts in stress mode and prints the reason on the bottom screen.

**Real console (later).** On the SD card: the `.3dsx` (e.g. `/3ds/spm3ds-demo.3dsx`, started from the Homebrew Launcher), plus
`/3ds/spm3ds-demo/room_main.spm`, `/3ds/spm3ds-demo/room_oku.spm` and `/3ds/spm3ds-demo/textures/tex_000.t3x` to `tex_088.t3x`
(about 1.2 MB). Never publish the converted files; they are derived from the game.

## 9. Week 3: fixes, Mario, game camera, movement, collision (2026-11-12)

Status: everything builds without warnings (devkitARM). The room was reported correct in Azahar by the user; **the new play mode has not
been run** (neither in Azahar nor on a console). I could not see the user's screenshots (`notes-screens/` did not exist on this PC), so the
black wedge was found with a small software renderer instead (scratch code outside the repo).

### 9.1 Fixes
- **Winding and the cull byte (converter, renderer).** The user found that "front" culling looked right, so GX strips come out clockwise in
  PICA200 terms. The converter now swaps two vertices of every triangle, so front faces are counter-clockwise and `GPU_CULL_BACK_CCW`
  is right. The viewer default is `auto` (Y cycles auto/none/back/front).
  **Meaning of the cull byte** (`drawMode` byte 1, only 1 and 3 occur): it is the same code as the Mario shapes' `cullMode`, whose TTYD table
  `{2,1,3,0}` maps 0 = back, 1 = front, 2 = all, 3 = none (GX names). So **1 = one-sided, 3 = double-sided** (the street-lamp poles, 340
  triangles each, are the cull-3 joints). In `auto` mode cull 1 is culled as back faces, cull 3 is not culled.
  `drawMode` byte 0 (0..3) is probably the blend/draw layer: the `kage` shadow planes and the poles use 3 and 2. Not used yet.
- **The black wedge** is joint `pCube9_q00659` (section `sima`, material `lambert1_v`, 10 triangles, x -25..-15, y -120..0, z 140..170):
  an open-topped box sunk 120 units into the ground. It is **real geometry, not an undecoded material, a missing texture or a hole**: its
  material has no texture and its vertex colours are authored (0,0,0), so black is what the data says. It sits in the foreground strip
  (`sima`, z 140..170), which the game camera probably never shows from this side; the free camera looks into it. Left in as is.
  Other `lambert1_v` batches (lamp poles, `kui` stakes, outlines) are black the same way.
- **Filtering.** All 89 room textures (and Mario's) have min and mag filter = GX_LINEAR in their TPL headers, no mipmaps, so bilinear
  `GPU_LINEAR` is what the code already did. Confirmed, nothing to change.

### 9.2 Collision (`room_hit.bin`, `source/hit.c`)
- Converter writes the A tree (2,165 non-degenerate triangles, world space, CCW order). Floors = normal.y > 0.5, walls = |normal.y| <= 0.5.
  The street floor is y = 0 over z -30..10, with solid walls at x = +-114. The collision `drawMode` attr (0 / 4096 / 131072 / 557056) is stored but ignored.
- Runtime: floor = highest floor at (x,z) not more than 4.5 above Mario's feet (so he climbs steps up to 4.5 and falls off edges); walls =
  two spheres (radius 4) pushed out horizontally, the lower one starting above the step height. Brute force over all triangles with
  bounding-box rejection. **Not measured on a console; check CPU ms in play mode.** Ceilings are ignored (he can jump through them).

### 9.3 Mario (`tools/convert_mario.py`, `source/mario.c`)
- Parsed `a/p_mario` using spm-headers `animdrv.h` for the header and the TTYD decomp's `renderProc` for the draw loop (spm-docs is not on
  this PC and cloning needs the user's OK). Shape (168 B) -> draw (108 B) -> draw call (`{first,count}` = triangle fan); u32 index arrays
  (low 16 bits); vertex colour, tex0 coordinates; texture = `texData[texDataIds[0]].bindId` = TPL image number. 55 triangles, 10 textures
  (resized to power of two, ETC1/ETC1A4). The result looks right in a software render: textures, UVs and proportions.
- **Static standing pose only.** Each group's node is 24 floats; in the rest pose only the translation is non-zero (checked on all 176
  groups) so group matrices are summed translations. Costume-variant groups (Kinome, Sp_boushi, hammers, `zentai`, mouth, tear) are hidden by name.
- **Missing: the animations.** `mario_S_1` / `mario_W_1` keyframes, the per-frame deltas for group transforms, visibility and the arm skin
  vertices. TTYD's C source has no evaluator for them (only `animPoseMain` stubs); the decoder would have to come from the disassembly of
  SPM's `evalProc` in `spm-decomp/build/US0/asm` (or from spm-docs). Mario therefore slides without moving his legs.
- The sprite looks towards screen-left by default; walking right mirrors it (eased over about 0.1 s, a paper turn). It is a billboard:
  rotated to face the camera, including in 3D. Size 23 units tall (the plan's earlier "27" was a guess).

### 9.4 Play mode (`source/play.c`)
- **Camera**: `camera_road.bin` is mostly names (`C2D_01`, `C3D_01`, `G2D_ie_01`...: 2D and 3D camera paths per area) and I could not
  decode its records beyond a field of view of **25** and near/far 0.01/1000 before the first name; the float 178.267 I first read as a
  distance is ASCII text ("C2D_"). So the camera is a fixed-distance guess: 190 units (2D, looking straight along -z at Mario + 11 up), 120 units
  in 3D with a 0.2 rad downward pitch. The area-specific camera paths are not used.
- **Flip (X)**: the camera swings 90 degrees (camera ends up at -x of Mario looking along +x, i.e. behind him when he faces right) in 0.6 s with easing.
- **Movement**: circle pad. 2D: left/right only, z glides back to the 2D plane (z = -10). 3D: stick relative to the camera. 60 units/s, A
  jumps (150 units/s, gravity 330, about 34 high), B resets. The numbers are guesses, not the game's.
- SELECT cycles PLAY -> ROOM (free camera, as before) -> STRESS.
- To run: copy `mario.spm`, `room_hit.bin` and the new `textures/mario_*.t3x` (plus the re-converted room files, whose winding changed) into the same
  SD folder as in section 8.5.

## 10. Week 3b: Mario's scale, black areas, animation status (2026-11-12)

Status: builds without warnings; **not run** (no Azahar here). The user's screenshots (`notes-screens/`) are not on this PC.

### 10.1 Scale (the 23-unit Mario was about 6x too big)
- **Hitbox from the game**: `characterProperties[0]` (spm-headers `mario.h`) is a table of `{hitboxWidth, hitboxHeight, walkSpeed, dashSpeed, ?}`.
  Found in `main.dol` (US0) at file offset 0x3E2DE8 by pattern search: Mario = **20 x 39**, walk **1.5**/frame, dash 3.0 (the next rows, 24 x 48 and 47 x 54, are
  the other characters). Mario's sprite model has a header bbox of 26.9 tall (23 with the hidden variant parts removed).
- **The room is smaller than the game units.** The doors of the coloured-door hall (`doa2_l/_r`, `doa3`, `doa4`) are 8 x 8 in my units. In the game
  screenshot `NewSuperPaperBros/screenshots/mac_02_cinematic.png` Mario is about 0.5 door heights tall (115 px against 225 px). With Mario drawn at roughly
  1.4x his model size (about 32 game units, hitbox 39) that makes a door about 64 game units, so **the room's units are about 1/8 of game units**
  (positions would have 4 fractional bits, not the 7 I assumed). Supporting hints: wall insets of exactly 0.125 = 1 game unit; floors at 1360/-1360 etc. fit s16.
  This is derived, not read from code (the vertex format set-up was not found in the disassembly); the ratio could be 6-10.
- Applied: **Mario draw scale 0.175** (= 1.4 / 8; 4.0 room units tall, about 32 game units). Hitbox, walk speed (1.5 x 60 / 8 = 11 units/s, i.e. 2.8 Mario
  heights/s), jump, step height and the camera distance (16 Mario heights, which makes Mario about 14 % of the screen height as in the screenshot)
  are all derived from the current height, so they follow the scale.
- **Live adjust (temporary)**: hold L and press D-pad up/down (x1.8 per second), L + B resets; the bottom screen shows scale, height in room units and in game units.
- Feet: the model's feet are at y = 0 and the collision floor is flat y = 0 under the street, so they stand on the floor at any scale. Collision radius
  0.30 H, lower sphere above a 0.15 H step.
- Not done: the room itself is still drawn in its own units; the free camera speeds are unchanged.

### 10.2 Black areas
- (b) from before: the wedge is `pCube9_q00659` (see 9.1): an open-topped box sunk 120 units, material `lambert1_v` (no texture, vertex colours authored black).
- The two new ones could not be identified from a screenshot. Candidates in the same `sima` foreground strip (z 140..170), all `lambert1_v` or the
  translucent shadow planes `*_kage` (`lambert1_v_x`, vertex colour (29,19,6), alpha 0..204: they come out almost black in my conversion because the material
  colour 102 is multiplied in): tree-base shapes `polySurface623..625` and `pCylinder*` (luminance 0.04..0.07), `kui_*` stakes, `sekihi_kage_*`, `dokan_kage_*`.
  **With the corrected scale the play camera is at z = about 54, so the whole `sima` strip (z >= 140) is behind the camera and none of it can be seen**;
  a software render from the new camera shows only the lamp posts (correctly black), the shop wall and the floor. If black areas remain on screen, send the new screenshot.
- Likely truth for the shadows: the game draws `_x` materials differently (flag byte 2 = 2, `drawMode` byte 0 = 3). Not decoded.

### 10.3 Animation status
- Decoded: the whole static model (header, shapes, draws, fan polygons, vertices, UVs, textures, group tree with translations, visibility bytes).
- Not decoded: the per-animation data, `AnimPoseData_AnimData` (94 of them; `mario_S_1` idle, `mario_W_1` walk): its header (keyframe count, counts of vertex-position,
  vertex-normal, texture-transform, visibility and group-transform deltas, and the pointers) is known from spm-headers, but not the **layout and interpolation of
  the delta records**. TTYD's C has no evaluator (`animPoseMain` is a stub there). The evaluator is `evalProc` (EU0 0x8004D0C8, 0x1BC bytes) and `animPoseMain`
  (0x80045288, 0x143C bytes), reachable in the spm-decomp disassembly for EU0 (US0 has no names for them) — **that is the blocker: it needs reading about 6 KB of PowerPC
  assembly to learn the record layout, and I have not started.** Without it Mario has no walk cycle, blinking or hand changes. spm-docs may shortcut this.

## 11. Week 3c: Mario's idle and walk animations decoded (2026-11-12)

Status: decoded, baked and checked with a software renderer (contact sheets of `mario_W_1` and `mario_S_1` show a proper walk cycle with swinging
legs and arms, and the idle breathing/blinking-free sway). The 3DS code builds without warnings but **has not been run** (no Azahar here).

### 11.1 Sources checked
- **spm-docs** (SeekyCt/spm-docs, read through the web, not cloned): has headers and writeups for many systems but **nothing on the AnimPose / `a/` format**.
- **ttyd decomp**: `animdrv.c` only has stubs for `animPoseMain` and the evaluators.
- **spm-decomp upstream `animdrv-test`** (fetched with `git fetch upstream`, read only, nothing merged): 78 lines of buffer allocation (`animPose_AllocBuffer`), which
  confirms the pose buffer layout (positions, normals, visibility bytes, `4 * groupTransformDataCount` bytes of nodes, `0x18 * textureCoordinateTransformCount` of tex entries)
  but contains no keyframe code.
- **The game's own code** (US0 disassembly in `spm-decomp/build/US0/asm`, which is EU0 minus 0x118): `animPoseMain` = `fn_80045170`, `evalProc` = `fn_8004CFB0`,
  node matrices `fn_800465AC` (plain transform) and `fn_80046B14` (joint), tangent table set-up in `fn_800415B0`. That is where the format below comes from.

### 11.2 The format (also in the header comment of `tools/convert_mario_anim.py`)
- AnimData: pointers are relative to its own start. Keyframes are 0x2C bytes: time (60 Hz frames) + offset/length pairs into four delta streams.
  State at keyframe k = base data + sum of the deltas of keyframes 0..k; between k and k+1 the next keyframe's deltas are added scaled by the fraction.
  Positions: record `{u8 skip, s8 x, y, z}` x 1/16, linear. Group node floats: `{u8 skip, s8 v, s8 a, s8 b}`: v/16 with a cubic Hermite step whose end tangents are
  `tan(a degrees)` and `tan(b degrees)` per frame (the runtime table `lbl_804C7130` is `tan` of -89..88 degrees). Visibility: `{u8 skip, u8 add}`. Texture animation: `{skip, add, f32, f32}`.
- Nodes are 24 floats (T, S, rot1, rot2, rot centre, scale centre, rot translate, scale translate); transform nodes are T * R * S with pivots, joint nodes
  (segment-scale-compensated) T * Sinv * R * S; **angles are the stored value x 2 degrees** (the code multiplies by 2.0 before degrees to radians).
- `evalProc` walks the group tree: a group whose visibility byte is 0 hides its whole subtree; the walk continues with the brother.
- Idle `mario_S_1`: 62 keyframes over 280 frames (looping). Walk `mario_W_1`: 17 keyframes over 40 frames (looping). Run `mario_R_1` has the same layout (not baked yet).
- Baked at 30 Hz (every 2nd game frame) into `assets/mario_anim.bin` (196 KB); the 3DS interpolates positions between samples. Textures: 12 images (19 converted).

### 11.3 What is still missing or guessed
- Costume-variant parts (the space-helmet hat, `Kinome`, hammer effect planes, mouth/tear shapes) are hidden **by name**, because the animation data does not hide them: the
  game's own code must do that elsewhere (not found). Same list as the static pose.
- Not applied: normals (no lighting), texture UV transforms (none changed in idle or walk), the "type 8" event list, the loop-wrap blend quirk (the game blends the last key
  towards keyframe 0's deltas; for these two animations the last key sits on the loop end so it does not matter).
- The vertex positions of the arm "skin" shapes (`R_Arm_skin`, `L_Arm_skin`) come out of the position deltas and look right in the renders.
- Only idle and walk are baked; the other 92 animations (jump `mario_J_1A..`, run, hammer...) use the same decoder, so adding them is a list change in `ANIMS` (the runtime
  currently allows 4).

### 11.4 Play mode (this step)
- Walking (stick pushed and on the ground) plays `mario_W_1`, otherwise `mario_S_1`; the cycle rate follows the stick magnitude. Turning keeps the eased paper flip
  (the sprite squashes through zero width and mirrors in about 0.2 s). Since the real animation works, the "slight bob" fallback was not needed.
- **Bottom screen**: by default only a controls list. Y toggles the debug screen (stats, scale, collision state); the L + D-pad up/down scale control only works there.
  The default scale stays 0.175 (confirmed right by the user in Azahar).
- To run: copy the new `spm3ds-demo.3dsx`, `mario_anim.bin` and the `textures/mario_*.t3x` files (19) into the Azahar SD folder. Nothing else changed.

## 12. Week 4: stereo 3D, icon, music, .cia (2026-11-12)

Status: all of it builds (devkitARM, no warnings after the last fix). **Nothing was run** (no Azahar/console here); the user tests in Azahar.

### 12.1 Stereo 3D (done)
- Play mode only. `main.c` makes a second render target (`GFX_RIGHT`) and draws the scene twice with `Mtx_PerspStereoTilt` projections
  (`play_projection_stereo` in `play.c`). Zero-parallax plane = Mario's distance from the camera (he sits "in the screen"); eye separation
  = slider x 3 % of that distance (eyes at -/+ iod, left/right). The Mario billboard uses the same per-eye projection.
- Slider at 0 (or room/stress modes): `gfxSet3D(false)`, one eye only, identical to before (and half the GPU work). The bottom-screen console is always flat.
- The debug screen shows "stereo on/off (slider x.xx)". The 3 % factor is a guess; adjust `STEREO_IOD_FRACTION` in `play.c` if the depth is too weak or tiring.
  Azahar needs Settings > Graphics > Stereoscopy set to something other than Off for the slider to do anything (the emulator's slider can be dragged in the toolbar).

### 12.2 Icon and title (done)
- Title "Super Paper Mario 3DS Demo", author "DarinKorn1" (the git user name; change `APP_AUTHOR` in the `Makefile` to your real name), description in the `Makefile`.
- `icon.png` (48x48, original: a sheet of paper with a folded corner and a star) is made by `tools/make_icon.py` (pure Python). The Makefile picks up `spm3ds-demo/icon.png` automatically.
  To use your own: replace `icon.png` with any 48x48 PNG (a transparent background is fine) and run `make` again (delete `spm3ds-demo.smdh` first if it does not refresh).

### 12.3 Flipside music
**Where it is on the disc.** `sound/*.brstm` (137 files, about 170 MB, uncompressed on the disc), plus `wiimario_snd.brsar` (the sound-archive index) and `.dat`.
Names follow `map_<stage>...` for area themes, `btl_` battles, `evt_` events, `sys_`, `ff_` fanfares. Flipside is `map_town_omote1_44k_lp.brstm` and Flopside
(the other side of the same town) `map_town_ura1_44k_lp.brstm`: both 2,445,408 bytes, different contents. "omote" = front, "ura" = back, and the
game's own place names for Flopside are `place_town_ura_*`. **Inference from the names, not read from a script:** `setup/mac_02.dat` does not exist (the
setup scripts are not stored per room) and I did not find the bgm table; listening is the quick check (if it is the wrong tune, use `map_town_ura1`).

**Format (confirmed from the file):** BRSTM `RSTM`, big-endian, codec 2 = Nintendo DSP-ADPCM (4 bits/sample, 8-byte frame = 14 samples), 2 channels, 44,100 Hz,
2,131,080 samples = **48.3 s**, one loop starting at sample **14,336 (0.33 s)** and running to the end, ADPCM data in 0x2000-byte blocks interleaved per channel,
per-channel coefficient tables in the header.

**What the 3DS can play (libctru `ndsp`):** 8/16-bit PCM and a DSP-ADPCM mode (the same family as the Wii's), mono or stereo, per-channel sample rate
(the DSP mixes at about 32 kHz and resamples), up to 24 voices. Wave buffers must be in linear memory (`linearAlloc`); a buffer can loop. Two ways:
RAM (decode on the PC, read the whole file) or streaming from SD (refill 2 buffers from a thread). It needs the DSP firmware: Azahar has its own, a real
console running homebrew needs `sdmc:/3ds/dspfirm.cdc` (dumped once with the "DSP1" homebrew app).

**Chosen:** decode on the PC to 16-bit stereo PCM and hold it in RAM. 2,131,080 x 4 B = **8.5 MB** of linear memory (a New 3DS has 124 MB for apps; even an
Old 3DS has 64 MB; textures + geometry are under 3 MB) and load time is about 1 s from SD. No streaming code, no runtime ADPCM, no sample-rate conversion.
(ADPCM kept as-is would be 2.4 MB, but loop-point history bookkeeping and per-channel buffers cost more code for no gain at this size.)
Estimate was "moderate: about a day", so it was done:
- `tools/convert_bgm.py`: parses the BRSTM header, decodes both channels (the last block has its own padded size), writes `assets/bgm_flipside.pcm` (git-ignored with the rest of `assets/`):
  header `"SBGM", version 1, rate, channels, samples, loopStart`, then interleaved s16. Check: no clipping, peak 31,920, per-second RMS 2,400-4,700 (steady music, not noise).
- `source/audio.c`: `ndspInit`, one stereo-PCM16 channel with two wave buffers: intro (0..loop start) then the loop body (`looping = true`), volume 0.8.
- R in play mode mutes (pauses) and resumes the music. If the file or the DSP is missing the demo just runs silent and says why on the debug screen.
- Not heard yet; sync of the loop seam is by sample number from the file, so it should be seamless.

### 12.4 Home Menu install (.cia)
- **Tools on this PC:** `makerom` and `bannertool` are **not installed** (not in devkitPro; `smdhtool` and the 3dsx tools are). I did not download anything.
  `makerom` is from 3DSGuy/Project_CTR (open source, MIT); `bannertool` is from carstene1ns/3ds-bannertool (a maintained fork of Steveice10/bannertool), both on GitHub as prebuilt Windows
  releases (or buildable from source).
- **Prepared without them:** `cia/banner.png` (256x128, original), `cia/banner.wav` (1.9 s original arpeggio, `tools/make_banner_audio.py`), `cia/spm3ds-demo.rsf`
  (makerom spec; unique ID `0xF7A31` = title ID `000400000F7A3100`; DirectSdmc access so the app reads `sdmc:/3ds/spm3ds-demo/`; New 3DS 804 MHz and 124 MB mode) and
  `tools/make_cia.sh` (bannertool banner + icon, then makerom). **The .rsf and the script are untested**: makerom may reject a field and need a tweak.
- The CIA contains only the program; room, collision, Mario, textures and the music file stay on the SD card in `sdmc:/3ds/spm3ds-demo/`.

### 12.5 .cia built (2026-11-12)
- Downloaded with the user's OK into `C:\Users\ender\3ds-tools\` (outside the repo): makerom v0.19.0 (3DSGuy/Project_CTR, win_x86_64) and bannertool 1.2.3
  (carstene1ns/3ds-bannertool, windows). Add both folders to PATH, then run `sh tools/make_cia.sh` from `spm3ds-demo/` after `make`.
- makerom rejected two RSF keys (`MediaFootPrint`, `ExtendedDataSize`); removed. Result: `spm3ds-demo.cia`, 257 KB (git-ignored). **Built but not installed or run anywhere.**
