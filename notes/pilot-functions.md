# Pilot: 30 functions to decompile

Picked on 2026-11-10 from spm-decomp's **EU0** config only (`config/EU0/symbols.txt`,
`config/EU0/splits.txt`, the object statuses in `configure.py`, and the `// NOT_DECOMPILED`
markers in `src/`). Addresses and sizes are EU0. All 30 are in `main.dol`, which is byte-identical
in EU0 and EU1, so they're the same in both PAL releases. The USA (US0) addresses are different.

## How they were chosen

1. **Not yet decompiled**: the function is in a `NonStarted` file, or listed as
   `// NOT_DECOMPILED` in a `NonMatching` file. 3,516 such functions are inside split files
   (another 6,297 are in code that isn't split yet; skipped, because splitting is extra work).
2. **Game code only**: no SDK, NW4R, MSL or runtime code (excluded `DEMOInit.c` too, which is SDK
   demo code), and nothing outside the splits.
3. **Has a Thousand-Year Door counterpart**: a function with the same name has a real body in
   `doldecomp/ttyd` (cloned read-only at `ttyd/`, commit `62131fc`). 301 candidates qualified;
   empty TTYD bodies (stubs) were rejected. A TTYD comment `// 1:1` means its author marked it
   matching there; TTYD's `camdrv.c` is a fully `Matching` file. Same name doesn't guarantee
   same code: SPM changed a lot, so compare before relying on the TTYD version.
4. **Size buckets**: small 32-128 bytes (8-32 instructions), medium 200-640 bytes (50-160),
   large 700-2,100 bytes (175-525). The median not-yet-decompiled function is 172 bytes.
5. **Spread**: 25 different source files, at most 2 functions per file.
6. **Avoided** `animdrv.c` and `wpadmgr.c`: upstream has work-in-progress branches for them
   (`animdrv-test`, `wpadmgr`).

"New file" means the file is `NonStarted`: you create `src/<file>.c` and set it to
`NonMatching` first (see `decomp-workflow.md`, step 4). Two functions are in files that already exist.

## Small (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| S1 | `marioChkInScreen` | `0x80126DCC` | 0x30 (48) | mario.c (new file) | `mario/mario.c`, marked 1:1 | Smallest pick: one range check on x/y; a gentle first function. |
| S2 | `winMgrSetSize` | `0x8003BC2C` | 0x2C (44) | winmgr.c (new file) | `manager/winmgr.c` | Index into the window table, test a flag, store four fields: teaches struct layout in spm-headers. |
| S3 | `caseReInit` | `0x80058DA8` | 0x40 (64) | casedrv.c (new file) | `driver/casedrv.c` | A single loop clearing a flag bit; good first loop. |
| S4 | `imgInit` | `0x80076B70` | 0x44 (68) | imgdrv.c (new file) | `driver/imgdrv.c`, marked 1:1 | Typical "allocate and clear the work area" init; the same pattern appears in dozens of drivers. |
| S5 | `offscreenInit` | `0x80034B44` | 0x44 (68) | offscreen.c (new file) | `driver/offscreendrv.c` (TTYD notes a register mismatch: "TODO: fix r31") | Same init pattern, but TTYD didn't match it: a small case of register-allocation tuning. |
| S6 | `mobjReset` | `0x8002A46C` | 0x4C (76) | mobjdrv.c (new file) | `driver/mobjdrv.c` | `memset` of the map-object table plus a global; checks how SPM's mobj work struct differs from TTYD's (TTYD has a battle flag). |
| S7 | `_ismbblead` | `0x800328B0` | 0x4C (76) | msgdrv.c (new file) | `driver/msgdrv.c` | Shift-JIS lead-byte test: pure logic, no structs; tests comparison and return-value codegen. |
| S8 | `dispInit` | `0x8005AEA4` | 0x50 (80) | dispdrv.c (new file) | `driver/dispdrv.c` | Two allocations and two `memset`s; the display-list driver is central to drawing. |
| S9 | `hitObjGetNormal` | `0x8007035C` | 0x54 (84) | hitdrv.c (new file) | `driver/hitdrv.c`, marked 1:1 | Look up a collision object by name and normalise its normal with `PSVECNormalize`: first SDK call. |
| S10 | `envDisp` | `0x80063754` | 0x58 (88) | envdrv.c (new file) | `driver/envdrv.c` | Reads the GX viewport/projection: a small graphics-side function, relevant to the 3DS renderer later. |

## Medium (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| M1 | `getScreenPoint` | `0x80058294` | 0xD0 (208) | camdrv.c (new file) | `driver/camdrv.c`, **file fully Matching in TTYD** | World-to-screen projection with GX matrices; the best-verified TTYD source of the set. |
| M2 | `fadeInit` | `0x80065C78` | 0xE8 (232) | fadedrv.c (new file) | `driver/fadedrv.c` | Init with a loop over fade slots; a step up from the small inits. |
| M3 | `iconSetPos` | `0x80074720` | 0xF4 (244) | icondrv.c (new file) | `driver/icondrv.c` | Uses an inlined name lookup (TTYD notes `iconNameToPtr // inline`): practice recreating inlined helpers. |
| M4 | `seq_gameMain` | `0x8017CF08` | 0xFC (252) | seq_game.c (new file) | `sequence/seq_game.c` | The in-game sequence's per-frame state machine (`switch` on state): the game loop's top level. |
| M5 | `seq_mapChangeInit` | `0x8017A33C` | 0x124 (292) | seq_mapchange.c (new file) | `sequence/seq_mapchange.c` | String copies of the next area/map/door names; string literals test `.data`/`.rodata` placement. |
| M6 | `lightMain` | `0x8007E374` | 0x130 (304) | lightdrv.c (new file) | `driver/lightdrv.c` | Float maths on the camera matrix: tests float ordering and `fmadd` codegen (`-fp fmadd`). |
| M7 | `evtNpcNameToPtr` | `0x800FDE94` | 0x140 (320) | evt_npc.c (new file) | `event/evt_npc.c` | Script-side NPC lookup ("me", "party", ...): first look at the event (script) system. |
| M8 | `romFontMake` | `0x801A75B0` | 0x18C (396) | romfont.c (new file) | `romfont.c` (102 lines) | Builds glyph data from the console ROM font via SDK `OSFont` calls. |
| M9 | `qqsort` | `0x8019CF84` | 0x1CC (460) | system.c (**file exists**, NonMatching) | `system.c`, register comments per variable | Generic sort; file already set up, and TTYD lists the register of every local, a strong hint. |
| M10 | `mapGetBoundingBox` | `0x8007F778` | 0x1E4 (484) | mapdrv.c (new file) | `driver/mapdrv.c` (54 lines) | Walks map joints to compute min/max; map code is the biggest draw cost in the Route B profile. |

## Large (10)

| # | Function | EU0 address | Size | File | TTYD counterpart | Why |
|---|---|---|---|---|---|---|
| L1 | `dispDraw` | `0x8005B1A0` | 0x2CC (716) | dispdrv.c (new file) | `driver/dispdrv.c` (58 lines) | Runs the sorted display list per camera. In the Route B Flipside profile it is inclusive of 59% of the game thread: the heart of drawing. |
| L2 | `toRearPose` | `0x80129438` | 0x2E0 (736) | mario.c (new file) | `mario/mario.c`, marked 1:1 | Long but simple chain of `strcmp`s mapping pose names: large size, low difficulty; tests string-pool ordering. |
| L3 | `parseGet1Next` | `0x801A7140` | 0x348 (840) | parse.c (new file) | `parse.c` | Recursive text-data parser; checks how the game reads its own data files. |
| L4 | `npcDelete` | `0x801B7064` | 0x368 (872) | npcdrv.c (new file) | `driver/npcdrv.c` | Unlinks and frees an NPC (slaves, animations, hit objects): touches many other systems' APIs. |
| L5 | `windowDispGX_System` | `0x800396E0` | 0x4A0 (1184) | windowdrv.c (**file exists**, NonMatching) | `driver/windowdrv.c` (215 lines) | Draws a system window with GX matrices; file already set up, and 9 of its functions are already decompiled (11 to go). |
| L6 | `camMain` | `0x80055208` | 0x4EC (1260) | camdrv.c (new file) | `driver/camdrv.c`, **file fully Matching in TTYD** | Per-frame camera update; a large function with a verified TTYD source to compare against. |
| L7 | `iconMain` | `0x800721F4` | 0x51C (1308) | icondrv.c (new file) | `driver/icondrv.c` (TTYD has a TODO about a missing `shadowEntry` call) | Per-frame icon update; TTYD's version is incomplete, so a realistic "TTYD is only a hint" case. |
| L8 | `seq_logoMain` | `0x80179140` | 0x5BC (1468) | seq_logo.c (new file) | `sequence/seq_logo.c` (132 lines) | Boot logo state machine with file loading and timing (`OSTime`): early-boot code a port needs first. |
| L9 | `hitCheckVecFilter` | `0x8006E780` | 0x6AC (1708) | hitdrv.c (new file) | `driver/hitdrv.c`, marked 1:1 (141 lines) | Ray-vs-collision test, float heavy. One of the top-10 translated functions by self time in the Route B Flipside profile. |
| L10 | `itemEntry` | `0x80078B3C` | 0x7FC (2044) | itemdrv.c (new file) | `driver/itemdrv.c` | Largest pick: creates an item with many parameters and string handling; tests stack layout of a big function. |

## Things to know before starting

- **Needs a PAL disc.** Nothing here can be built or diffed until `orig/EU0/` (or `EU1/`) has a dump.
- **Pilot measurements to record** per function: time to 100%, final match % if not reached,
  whether the TTYD version helped, and what blocked (types, register allocation, inlining,
  missing headers).
- **Most picks start a new file.** Creating it means listing every function in that file as
  `// NOT_DECOMPILED` and adding the file's declarations to spm-headers; budget time for that the
  first time in each file.
- **The Route B profile used USA addresses and names from NewSuperPaperBros's map.** spm-decomp's
  US0 config calls those two functions `fn_8005B088` (`dispDraw`) and `fn_8006E668`
  (`hitCheckVecFilter`); their sizes (0x2CC and 0x6AC) equal the EU0 ones, which supports them
  being the same functions. The EU0 addresses above come from EU0's own symbols.

## How the list was produced (reproducible)

Two throwaway scripts (kept outside the project): one read the EU0 config and `src/`
`NOT_DECOMPILED` markers into a table of 9,813 not-yet-decompiled functions; the other matched
names against function definitions in `ttyd/src` and recorded the TTYD file, its status in TTYD's
`configure.py`, and the body length. Selection by size bucket and file spread was done by hand
from that table.
