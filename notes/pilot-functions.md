# Pilot: 40 functions to decompile, in two groups

| Group | Functions | What it measures |
|---|---|---|
| **A: TTYD-assisted** | 30 (10 small, 10 medium, 10 large), IDs `A-S1` … `A-L10` | How fast matching goes when a Thousand-Year Door decompilation of the same function exists |
| **B: control, SPM-only** | 10 (3 small, 4 medium, 3 large), IDs `B-S1` … `B-L3` | How fast it goes without that help, on code that exists only in Super Paper Mario |

**Report the results for each group separately** (see "Recording results" at the end). Compare
A and B **within the same size bucket**: group B is smaller, so overall averages aren't comparable.

Group A was picked on 2026-11-10 and group B later the same day, both from spm-decomp's **EU0**
config only (`config/EU0/symbols.txt`, `config/EU0/splits.txt`, the object statuses in
`configure.py`, and the `// NOT_DECOMPILED` markers in `src/`). Addresses and sizes are EU0. All
40 are in `main.dol`, which is byte-identical in EU0 and EU1, so they are the same in both PAL
releases. The USA (US0) addresses are different.

## Rules shared by both groups

1. **Not yet decompiled**: the function is in a `NonStarted` file, or listed as
   `// NOT_DECOMPILED` in a `NonMatching` file. 3,516 such functions are inside split files
   (another 6,297 are in code that isn't split yet; skipped, because splitting is extra work).
2. **Game code only**: no SDK, NW4R, MSL or runtime code (`DEMOInit.c`, which is SDK demo code,
   is excluded too), and nothing outside the splits.
3. **Same size buckets**: small 32-128 bytes (8-32 instructions), medium 200-640 bytes (50-160),
   large 700-2,100 bytes (175-525). The median not-yet-decompiled function is 172 bytes.
4. **At most 2 functions per source file** within a group.
5. **Avoided** `animdrv.c` and `wpadmgr.c`: upstream has work-in-progress branches for them
   (`animdrv-test`, `wpadmgr`).
6. **Declarations**: 37 of the 40 already have a prototype in `spm-headers/include/spm/`, so
   neither group starts with an advantage there. The three without one are all in group A
   (`_ismbblead`, `romFontMake`, `toRearPose`).

"New file" means the file is `NonStarted`: you create `src/<file>.c` and set it to
`NonMatching` first (see `decomp-workflow.md`, step 4). Two group A functions are in files that
already exist; all group B functions are in new files.

---

# Group A: TTYD-assisted (30 functions)

**Extra rule:** a function with the same name has a real body in `doldecomp/ttyd` (cloned
read-only at `ttyd/`, commit `62131fc`). 301 candidates qualified; empty TTYD bodies (stubs)
were rejected. A TTYD comment `// 1:1` means its author marked it matching there; TTYD's
`camdrv.c` is a fully `Matching` file. Same name doesn't guarantee same code: SPM changed a lot,
so compare before relying on the TTYD version. Group A spans 25 source files.

## A, small (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| A-S1 | `marioChkInScreen` | `0x80126DCC` | 0x30 (48) | mario.c (new file) | `mario/mario.c`, marked 1:1 | Smallest pick: one range check on x/y; a gentle first function. |
| A-S2 | `winMgrSetSize` | `0x8003BC2C` | 0x2C (44) | winmgr.c (new file) | `manager/winmgr.c` | Index into the window table, test a flag, store four fields: teaches struct layout in spm-headers. |
| A-S3 | `caseReInit` | `0x80058DA8` | 0x40 (64) | casedrv.c (new file) | `driver/casedrv.c` | A single loop clearing a flag bit; good first loop. |
| A-S4 | `imgInit` | `0x80076B70` | 0x44 (68) | imgdrv.c (new file) | `driver/imgdrv.c`, marked 1:1 | Typical "allocate and clear the work area" init; the same pattern appears in dozens of drivers. |
| A-S5 | `offscreenInit` | `0x80034B44` | 0x44 (68) | offscreen.c (new file) | `driver/offscreendrv.c` (TTYD notes a register mismatch: "TODO: fix r31") | Same init pattern, but TTYD didn't match it: a small case of register-allocation tuning. |
| A-S6 | `mobjReset` | `0x8002A46C` | 0x4C (76) | mobjdrv.c (new file) | `driver/mobjdrv.c` | `memset` of the map-object table plus a global; checks how SPM's mobj work struct differs from TTYD's (TTYD has a battle flag). |
| A-S7 | `_ismbblead` | `0x800328B0` | 0x4C (76) | msgdrv.c (new file) | `driver/msgdrv.c` | Shift-JIS lead-byte test: pure logic, no structs; tests comparison and return-value codegen. |
| A-S8 | `dispInit` | `0x8005AEA4` | 0x50 (80) | dispdrv.c (new file) | `driver/dispdrv.c` | Two allocations and two `memset`s; the display-list driver is central to drawing. |
| A-S9 | `hitObjGetNormal` | `0x8007035C` | 0x54 (84) | hitdrv.c (new file) | `driver/hitdrv.c`, marked 1:1 | Look up a collision object by name and normalise its normal with `PSVECNormalize`: first SDK call. |
| A-S10 | `envDisp` | `0x80063754` | 0x58 (88) | envdrv.c (new file) | `driver/envdrv.c` | Reads the GX viewport/projection: a small graphics-side function, relevant to the 3DS renderer later. |

## A, medium (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| A-M1 | `getScreenPoint` | `0x80058294` | 0xD0 (208) | camdrv.c (new file) | `driver/camdrv.c`, **file fully Matching in TTYD** | World-to-screen projection with GX matrices; the best-verified TTYD source of the set. |
| A-M2 | `fadeInit` | `0x80065C78` | 0xE8 (232) | fadedrv.c (new file) | `driver/fadedrv.c` | Init with a loop over fade slots; a step up from the small inits. |
| A-M3 | `iconSetPos` | `0x80074720` | 0xF4 (244) | icondrv.c (new file) | `driver/icondrv.c` | Uses an inlined name lookup (TTYD notes `iconNameToPtr // inline`): practice recreating inlined helpers. |
| A-M4 | `seq_gameMain` | `0x8017CF08` | 0xFC (252) | seq_game.c (new file) | `sequence/seq_game.c` | The in-game sequence's per-frame state machine (`switch` on state): the game loop's top level. |
| A-M5 | `seq_mapChangeInit` | `0x8017A33C` | 0x124 (292) | seq_mapchange.c (new file) | `sequence/seq_mapchange.c` | String copies of the next area/map/door names; string literals test `.data`/`.rodata` placement. |
| A-M6 | `lightMain` | `0x8007E374` | 0x130 (304) | lightdrv.c (new file) | `driver/lightdrv.c` | Float maths on the camera matrix: tests float ordering and `fmadd` codegen (`-fp fmadd`). |
| A-M7 | `evtNpcNameToPtr` | `0x800FDE94` | 0x140 (320) | evt_npc.c (new file) | `event/evt_npc.c` | Script-side NPC lookup ("me", "party", ...): first look at the event (script) system. |
| A-M8 | `romFontMake` | `0x801A75B0` | 0x18C (396) | romfont.c (new file) | `romfont.c` (102 lines) | Builds glyph data from the console ROM font via SDK `OSFont` calls. |
| A-M9 | `qqsort` | `0x8019CF84` | 0x1CC (460) | system.c (**file exists**, NonMatching) | `system.c`, register comments per variable | Generic sort; file already set up, and TTYD lists the register of every local, a strong hint. |
| A-M10 | `mapGetBoundingBox` | `0x8007F778` | 0x1E4 (484) | mapdrv.c (new file) | `driver/mapdrv.c` (54 lines) | Walks map joints to compute min/max; map code is the biggest draw cost in the Route B profile. |

## A, large (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| A-L1 | `dispDraw` | `0x8005B1A0` | 0x2CC (716) | dispdrv.c (new file) | `driver/dispdrv.c` (58 lines) | Runs the sorted display list per camera. In the Route B Flipside profile it is inclusive of 59% of the game thread: the heart of drawing. |
| A-L2 | `toRearPose` | `0x80129438` | 0x2E0 (736) | mario.c (new file) | `mario/mario.c`, marked 1:1 | Long but simple chain of `strcmp`s mapping pose names: large size, low difficulty; tests string-pool ordering. |
| A-L3 | `parseGet1Next` | `0x801A7140` | 0x348 (840) | parse.c (new file) | `parse.c` | Recursive text-data parser; checks how the game reads its own data files. |
| A-L4 | `npcDelete` | `0x801B7064` | 0x368 (872) | npcdrv.c (new file) | `driver/npcdrv.c` | Unlinks and frees an NPC (slaves, animations, hit objects): touches many other systems' APIs. |
| A-L5 | `windowDispGX_System` | `0x800396E0` | 0x4A0 (1184) | windowdrv.c (**file exists**, NonMatching) | `driver/windowdrv.c` (215 lines) | Draws a system window with GX matrices; file already set up, and 9 of its functions are already decompiled (11 to go). |
| A-L6 | `camMain` | `0x80055208` | 0x4EC (1260) | camdrv.c (new file) | `driver/camdrv.c`, **file fully Matching in TTYD** | Per-frame camera update; a large function with a verified TTYD source to compare against. |
| A-L7 | `iconMain` | `0x800721F4` | 0x51C (1308) | icondrv.c (new file) | `driver/icondrv.c` (TTYD has a TODO about a missing `shadowEntry` call) | Per-frame icon update; TTYD's version is incomplete, so a realistic "TTYD is only a hint" case. |
| A-L8 | `seq_logoMain` | `0x80179140` | 0x5BC (1468) | seq_logo.c (new file) | `sequence/seq_logo.c` (132 lines) | Boot logo state machine with file loading and timing (`OSTime`): early-boot code a port needs first. |
| A-L9 | `hitCheckVecFilter` | `0x8006E780` | 0x6AC (1708) | hitdrv.c (new file) | `driver/hitdrv.c`, marked 1:1 (141 lines) | Ray-vs-collision test, float heavy. One of the top-10 translated functions by self time in the Route B Flipside profile. |
| A-L10 | `itemEntry` | `0x80078B3C` | 0x7FC (2044) | itemdrv.c (new file) | `driver/itemdrv.c` | Largest pick: creates an item with many parameters and string handling; tests stack layout of a big function. |

---

# Group B: control, SPM-only (10 functions)

**Extra rules:**

- **No TTYD counterpart**: the function's name appears **nowhere** in the ttyd repository
  (source, headers, symbol lists, config; checked with a whole-word search over every tracked
  file), and its source file has no same-named file in ttyd. 694 named candidates pass the name check; 376 of them are also in files TTYD doesn't have.
- **Game code specific to SPM**: it belongs to something TTYD doesn't have: Pixls (`fairy`),
  Tippi (`guide`), flipping to 3D, the flip timer, character switching, the character/Pixl/item
  menu and the chapter select in the pause menu. The "Why" descriptions below come from the
  function and file names; none of these functions has been read yet.
- **Only real names** (no `fn_`/`func_` placeholders), so each can be looked up in spm-headers
  like group A.
- **Spread**: 7 source files, none of them used by group A.

Caveat: "no counterpart" is name- and file-based. TTYD does have broadly similar systems under
other names (its own HUD, `statuswindow.c`, and pause menu, `win_main.c`), so the HUD and
pause-menu picks may share some structure with TTYD code. The Pixl, Tippi and 3D picks don't.
Don't consult TTYD for group B functions while doing the pilot, or the control is lost.

## B, small (3)

| # | Function | EU0 address | Size | File | Why |
|---|---|---|---|---|---|
| B-S1 | `hudTurnOffFlipTimeBox` | `0x8019B0B4` | 0x28 (40) | hud.c (new file) | By its name, hides the flip-timer box on the HUD; size close to A-S1/A-S2. |
| B-S2 | `evt_mario_check_3d` | `0x800F3364` | 0x4C (76) | evt_mario.c (new file) | By its name, the script command that checks whether the game is flipped to 3D: SPM's central mechanic, and the event-function calling convention. |
| B-S3 | `fairyIdToPtr` | `0x8011E8BC` | 0x50 (80) | fairy.c (new file) | By its name, looks up a Pixl by ID; probably the same shape as the small "find entry" functions in group A. |

## B, medium (4)

| # | Function | EU0 address | Size | File | Why |
|---|---|---|---|---|---|
| B-M1 | `evt_fairy_flag_onoff_all` | `0x800E8214` | 0xC8 (200) | evt_fairy.c (new file) | By its name, a script command that sets or clears a flag on all Pixls. |
| B-M2 | `pluswinCheckChapterUnlocked` | `0x80189BF0` | 0x100 (256) | pausewin.c (new file) | By its name, decides which chapters the pause menu's chapter select offers: game logic rather than graphics. |
| B-M3 | `initCharTab` | `0x8019605C` | 0x118 (280) | charpixlitemwin.c (new file) | By its name, sets up the character tab of the character/Pixl/item menu: SPM's playable-character system. |
| B-M4 | `guideMain` | `0x8011FCD4` | 0x1DC (476) | guide.c (new file) | Per-frame update of the guide (Tippi) system: a "Main" function, the same role as A-M4 `seq_gameMain`. |

## B, large (3)

| # | Function | EU0 address | Size | File | Why |
|---|---|---|---|---|---|
| B-L1 | `pausewinEntry` | `0x80184C18` | 0x470 (1136) | pausewin.c (new file) | Creates a pause-menu window entry; an "Entry" function like A-L10 `itemEntry`. |
| B-L2 | `fairyUpdate` | `0x8011D99C` | 0x4D0 (1232) | fairy.c (new file) | Per-frame Pixl update: game-object logic, close in size to A-L6/A-L7. |
| B-L3 | `hudMain` | `0x801994E0` | 0x594 (1428) | hud.c (new file) | Per-frame HUD update; close in size to A-L8 `seq_logoMain`. |

---

## Things to know before starting

- **Needs a PAL disc.** Nothing here can be built or diffed until `orig/EU0/` (or `EU1/`) has a dump.
- **Mix the order.** Don't do all of group A first: you'll get faster over time, and that would
  make group B look harder than it is. Alternate (for example one A, one B, in the same size
  bucket), or go bucket by bucket with both groups in each.
- **Most picks start a new file.** Creating it means listing every function in that file as
  `// NOT_DECOMPILED` and adding any missing declarations to spm-headers. Record the time for
  that setup separately from the time for the function itself, because group B has fewer
  files-per-function (7 files for 10 functions) than group A (25 for 30).
- **The Route B profile used USA addresses and names from NewSuperPaperBros's map.** spm-decomp's
  US0 config calls `dispDraw` and `hitCheckVecFilter` `fn_8005B088` and `fn_8006E668`; their
  sizes (0x2CC and 0x6AC) equal the EU0 ones, which supports them being the same functions.

## Recording results

Keep one row per function, with the group in its own column, so A and B can be summarised
separately:

| Field | Example |
|---|---|
| ID, group, size bucket | `B-M2`, B, medium |
| Time on the function itself (minutes) | 95 |
| Time on file and header setup (minutes, if this was the first function in its file) | 30 |
| Final match % (100 if matched) | 100 |
| Did TTYD help? (group A only: yes / partly / no) | partly |
| Main blocker | types / register allocation / inlining / missing headers / unknown structs / other |

Then report, **for each group and each size bucket**: number matched, median time per function,
median time per 100 bytes, and the most common blocker.

## How the lists were produced (reproducible)

Throwaway scripts (kept outside the project) read the EU0 config and the `src/`
`NOT_DECOMPILED` markers into a table of 9,813 not-yet-decompiled functions. For group A, names
were matched against function definitions in `ttyd/src`, recording the TTYD file, its status in
TTYD's `configure.py` and the body length. For group B, every identifier in every tracked ttyd
file was collected, and candidates whose names never occur there (and whose file has no
same-named TTYD file) were kept. Final selection by size bucket and topic was done by hand.
