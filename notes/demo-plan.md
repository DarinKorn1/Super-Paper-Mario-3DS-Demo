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
