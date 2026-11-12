# Pilot results

Log for the 40 functions in `pilot-functions.md`. One row per function, in the order worked.
Worked by Claude (AI assistant) in the `spm-decomp` clone, EU0, offline (no decomp.me).

## Status (updated 2026-11-11)

- **34 of 40 functions attempted: 32 matched, 2 not matched** (both parked on `wip/` branches).
  Group A (TTYD-assisted): 25 of 30 attempted, 23 matched. Group B (SPM-only control): 9 of 10
  attempted, 9 matched.
- **In progress:** A-L6 `camMain`. Analysis only so far, no code written, 0 of 10 attempts used
  (details in "In progress" below).
- **Not started:** A-L7 `iconMain`, A-L8 `seq_logoMain`, A-L9 `hitCheckVecFilter`, A-L10 `itemEntry`, and
  B-L3 `hudMain`. B-L3 goes straight after A-L6 so that group B is not left to the very end of the
  large bucket.
- **Build progress now** (`ninja`, EU0): code 97,672 / 3,550,036 bytes (**2.75%**, 428 / 10,216
  functions); data 124,477 / 4,636,761 bytes (**2.68%**). Before the pilot: 86,640 bytes (2.44%, 391
  functions) and 112,005 bytes (2.42%). The gain is +11,032 code bytes and +37 functions: 32 pilot
  matches, plus 5 by-products (below). Files linked into the rebuilt `main.dol` are unchanged at 14 of
  2,111 (2.07%), because no pilot file is fully matching yet.
- **By-product matches** (not pilot functions, each committed separately unless noted): `iconNameToPtr`
  (`7cd0f39`), `mapGetWork` (`fb4430a`), `fairySetAnim` and `fairyEnterRunMode` (`16e4cb6`), and
  upstream's `__assert2` went from 99.98% to exact (`bc91554`). `npcGetWorkPtr` also matches, but only on
  the `wip/npcDelete` branch.
- **Branches on `origin`:** `master` (all matches), `wip/parseGet1Next` (`45d8353`), `wip/npcDelete`
  (`fd39526`).

## Setup (2026-11-10)

- Disc in `orig/EU0` is **EU0** (PAL revision 0): `ninja` reported `build/EU0/main.dol: OK` and
  `build/EU0/relF/relF.rel: OK` against `config/EU0/build.sha1`.
- Progress before the pilot: code 86,640 / 3,550,036 bytes (**2.44%**, 391 / 10,216 functions);
  data 112,005 / 4,636,761 bytes (**2.42%**). DOL only: code 2.58%, data 3.96%.
- One download, approved: `sjiswrap.exe` v1.2.2 into `build/tools`.
- Remotes: `origin` = private repository, `upstream` push URL = `no_push` (a dry-run push to
  `upstream` fails).

## Method

- Order: bucket by bucket (small, medium, large), groups interleaved inside each bucket.
- **Attempt** = one edit-compile-diff cycle of the function. Limit 10, or earlier if stalled.
- **Diff**: `dtk elf disasm` of our object against `build/EU0/asm/<file>.s`, compared instruction
  by instruction (throwaway script). A match is then confirmed by `ninja`'s objdiff report
  (`fuzzy_match_percent` = 100 in `build/EU0/report.json`). "Match %" below is that figure.
- **Time** is wall-clock from starting the function to the commit, including file setup;
  setup is noted when the function was the first in its file.
- Matched functions: one commit each on `master`, pushed to `origin`.
  Unmatched: left on a `wip/<function>` branch.
- Group B rule kept: TTYD source not consulted for group B functions.
- **Times are my own rough estimates of working time per function, not stopwatch measurements.** The session clock has several multi-hour gaps where it sat waiting (between rows 25 and 26, inside row 32, and before this update); none of that is counted.
- **What the "main.dol: OK" check does and does not show.** Every file this pilot touched is still `NonMatching`, so none of it is linked into the rebuilt `main.dol`. The checksum therefore passes regardless of my code; it only shows the rest of the build is undisturbed. The check on my code is the per-function `fuzzy_match_percent` = 100 in `build/EU0/report.json`. Linking a file would need every function and all of its data to match, which no pilot file has reached.

## Log

| # | ID | Function | Group | Size class | Bytes | Matched | Match % | Attempts | Time | Commit / branch | What made it easy or hard |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | A-S1 | `marioChkInScreen` | A (TTYD) | small | 48 | yes | 100 | 1 | ~2 min (incl. creating `mario.c`, 143 stubs) | `43ba09a` | Pure range check, prototype already in spm-headers. TTYD showed the "flag variable, then return it" shape, which is what makes the compiler emit `li r0,0` early; bounds differ from TTYD (600x480 here, 600x535 there). |
| 2 | A-S2 | `winMgrSetSize` | A (TTYD) | small | 44 | yes | 100 | 1 | ~2 min (incl. creating `winmgr.c`, 20 stubs) | `b641ed3` | Struct layout (`WinmgrEntry`, `WinmgrWork`) was already complete in spm-headers, so the code was four stores. Only wrinkle: the work pointer is an unnamed symbol in the config; objdiff still scores 100. TTYD body had the same shape. |
| 3 | B-S1 | `hudTurnOffFlipTimeBox` | B (SPM-only) | small | 40 | yes | 100 | 1 | ~3 min (incl. creating `hud.c`, 23 stubs, and a header change) | `d2c2327` | Code is two stores, but `HudWork` in spm-headers had the target fields inside an "unknown" gap, so I had to add a 0x18-byte per-box struct (array at 0x88; its length of 10 is an assumption from the gap size). The repeated reload of the work pointer in the original confirmed the first field is a byte. No TTYD needed. |
| 4 | A-S3 | `caseReInit` | A (TTYD) | small | 64 | yes | 100 | 1 | ~2 min (incl. creating `casedrv.c`, 13 stubs) | `222f7c3` | One loop clearing a flag bit. The original walks a pointer and re-reads the count each pass, so a "pointer plus counter" loop matched first time. SPM adds a store TTYD doesn't have (a byte at work+8 is zeroed after the loop), which needed a one-field header edit. |
| 5 | A-S4 | `imgInit` | A (TTYD) | small | 68 | yes | 100 | 1 | ~1 min (incl. creating `imgdrv.c`, 18 stubs) | `e96f16a` | Allocate-the-table init. spm-headers had no structs for imgdrv at all, so I added minimal `ImgEntry` (size 0x160 from the multiply) and `ImgWork`. Unlike TTYD there is no `memset`. |
| 6 | A-S5 | `offscreenInit` | A (TTYD) | small | 68 | yes | 100 | 1 | ~1 min (incl. creating `offscreen.c`, 15 stubs) | `2ac5bee` | Same shape as `imgInit` (entry size 0x54), and again no structs in the header. SPM has one work table where TTYD has two, so the register problem TTYD's author noted doesn't arise here. |
| 7 | B-S2 | `evt_mario_check_3d` | B (SPM-only) | small | 76 | yes | 100 | 2 | ~1 min (incl. creating `evt_mario.c`, 106 stubs) | `a85d3a2` | Script command: read the argument list, call `marioCheck3d`, store the result, return 2. Every piece (macro, `EvtEntry`, `evtSetValue`) was already in spm-headers. Attempt 1 failed to compile: the project treats warnings as errors and the unused `isFirstCall` argument needs a `(void)` line. |
| 8 | A-S6 | `mobjReset` | A (TTYD) | small | 76 | yes | 100 | 1 | ~1 min (incl. creating `mobjdrv.c`, 49 stubs) | `27a6237` | `memset` of the entry table plus two stores. Differs from TTYD (no battle argument; SPM also zeroes a 16-bit field I had to add to the header), so TTYD only confirmed the general shape. |
| 9 | A-S7 | `_ismbblead` | A (TTYD) | small | 76 | yes | 100 | 3 | ~2 min (incl. creating `msgdrv.c`, 32 stubs) | `faf47d5` | The logic matched as soon as it compiled, and SPM adds an early exit when the language isn't Japanese (not in TTYD). Two failed attempts were about the build, not the code: a `static` function with no caller is dropped from the object, and a non-static one needs a prototype. It is left non-static with a TODO until a caller is decompiled. |
| 10 | A-S8 | `dispInit` | A (TTYD) | small | 80 | yes | 100 | 1 | ~1 min (incl. creating `dispdrv.c`, 17 stubs) | `27add8d` | Two allocations and three zero stores; variable names were already in the symbol list. SPM has no `memset` here, unlike TTYD, and zeroes two extra unnamed variables. |
| 11 | B-S3 | `fairyIdToPtr` | B (SPM-only) | small | 80 | yes | 100 | 2 | ~3 min (incl. creating `fairy.c`, 46 stubs) | `483bce1` | Bounds-checked table lookup; `FairyWork` was fully described in spm-headers. Attempt 1 had the right logic but computed the table address late; taking a local pointer to the work struct first (`wp = &work`) reproduced the original's early address computation. |
| 12 | A-S9 | `hitObjGetNormal` | A (TTYD) | small | 84 | yes | 100 | 1 | ~3 min (incl. creating `hitdrv.c`, 54 stubs) | `8104e95` | Name lookup, a count check, one SDK call. The TTYD body gave the condition directly. The triangle record type was only a placeholder in spm-headers, so I added a minimal `HitTri` with the normal at 0x48 (total size unknown). |
| 13 | A-S10 | `envDisp` | A (TTYD) | small | 88 | yes | 100 | 2 | ~3 min (incl. creating `envdrv.c`, 16 stubs) | `443b3ff` | Save viewport/projection, call two draw helpers, restore. TTYD gave the two local arrays and their order, which fixes the stack layout. Attempt 1 failed to compile: four GX functions and one local function had no usable prototypes in spm-headers, so I added them. |
| 14 | A-M1 | `getScreenPoint` | A (TTYD) | medium | 208 | yes | 100 | 1 | ~3 min (incl. creating `camdrv.c`, 42 stubs) | `4ad7e5f` | World-to-screen projection. `CamEntry` was well described in spm-headers. TTYD gave the two closing lines (subtract 304, flip around 240); the rest differs: SPM projects with the camera's stored matrices instead of re-reading GX state, and adds an aspect-ratio scale. Had to add a `GXProject` prototype and read two float constants out of the built DOL. |
| 15 | A-M2 | `fadeInit` | A (TTYD) | medium | 232 | yes | 100 | 2 | ~3 min (incl. creating `fadedrv.c`, 18 stubs) | `08d4715` | Allocate, clear, set defaults, loop over 4 fade entries (unrolled by the compiler). Attempt 1 indexed `wp->entries[i]` on every line and reloaded the work pointer before each store; taking a local entry pointer per pass fixed it. Two fields needed adding to the header. TTYD's version has 5 entries and different fields, so it only suggested the overall shape. |
| 16 | B-M1 | `evt_fairy_flag_onoff_all` | B (SPM-only) | medium | 200 | yes | 100 | 5 | ~2 min (incl. creating `evt_fairy.c`, 35 stubs) | `9ea8143` | Script command looping over all Pixls to set or clear flag bits. Logic was right from the start and all helpers were declared. Attempt 1: compile error (signed-to-unsigned needs an explicit cast). Attempts 2-4: one `add` had its operands swapped or was placed after the null check; only "count in its own variable, then sum into a second variable before the check" reproduced the original. Pure trial and error on how the expression is written. |
| 17 | A-M3 | `iconSetPos` | A (TTYD) | medium | 244 | yes | 100 | 3 | ~4 min for this and `iconNameToPtr` (incl. creating `icondrv.c`, 25 stubs) | `7cd0f39` (see note 1) | TTYD's hint that the name lookup is an inlined helper was the key. In SPM that helper, `iconNameToPtr`, is also a real function directly before this one, so decompiling it once produced both (bonus match, not a pilot function). Attempt 1: compile error (I had declared the helper `static`, the header declares it extern). Attempt 2: two registers swapped in the loop; fixed by holding the work pointer in a local and reading the count from it each pass. |
| 18 | A-M4 | `seq_gameMain` | A (TTYD) | medium | 252 | yes | 100 | 2 | ~4 min (incl. creating `seq_game.c`, 7 stubs) | `0097f68` | Two-state `switch`. TTYD supplied the skeleton and the "colour literal passed straight into `fadeEntry`" idiom; a named local colour (attempt 1) added a copy and shifted the stack. Extra work: three fade helpers have names in spm-headers but were still `func_...` in `symbols.txt`; I checked each one's code and renamed five of them, and gave `spsndSetPosDirListener` a prototype. |
| 19 | B-M2 | `pluswinCheckChapterUnlocked` | B (SPM-only) | medium | 256 | yes | 100 | 2 | ~3 min (incl. creating `pausewin.c`, 104 stubs) | `c5afdc0` | Table lookup, then a chain of five cases each reading a saved-game value. Readable straight from the assembly once the script-variable constants were decoded (`GSWF`/`GSW` macros exist in the headers). Attempt 1 had the exact structure but I mis-decoded the four flag numbers by 1024. The table itself is an unnamed data symbol, referenced by its placeholder name for now. |
| 20 | A-M5 | `seq_mapChangeInit` | A (TTYD) | medium | 292 | yes | 100 | 2 | ~5 min for rows 20-22 together (incl. creating `seq_mapchange.c`, 4 stubs) | `7be743c` | Clear the work area, copy the area/map/door names with length asserts, three sound calls, one camera-flag check. The work struct was already in spm-headers. The assert strings give away the original parameter name and line numbers; the two Japanese messages had to be read out of the DOL and written into the source (the string pool layout depends on their length). Attempt 1 called `camGetPtr` twice; the original reads the flags once. I only saw the first lines of TTYD's version (the same name copying); I did not read the rest, so I can't say how much of the function it covers. |
| 21 | A-M6 | `lightMain` | A (TTYD) | medium | 304 | yes | 100 | 1 | (see row 20; incl. creating `lightdrv.c`, 11 stubs) | `fb0b0de` | Float maths on the 3D camera's matrix. TTYD gave the formula and its operand order, which is what decides the multiply-add sequence. The original copies three matrix rows as structs and builds the result in a temporary before storing it; writing it that way matched first time. No light structs exist in spm-headers, so a local placeholder struct stands in. |
| 22 | A-M7 | `evtNpcNameToPtr` | A (TTYD) | medium | 320 | yes | 100 | 1 | (see row 20; incl. creating `evt_npc.c`, 247 stubs) | `4c2de57` | Chain of `strcmp`s on special names; the names were readable from the DOL and the structure from the assembly. SPM's list ("me", "target", "master", "slave_0".."slave_3", "mario") differs from the first cases I saw in TTYD ("me", "party"), so TTYD only confirmed the pattern. Added the four slave pointers to `NPCEntry`. |
| 23 | B-M3 | `initCharTab` | B (SPM-only) | medium | 280 | yes | 100 | 1 | ~2 min (incl. creating `charpixlitemwin.c`, 33 stubs) | `2e91ffc` | Builds the list of owned characters for the menu. spm-headers has no structs for this file at all, so the three structs (work area, tab, tab entry) had to be worked out from the offsets in the assembly; the pouch and Mario accessors it calls were already declared. Once the structs existed, the straightforward C matched first time. |
| 24 | A-M9 | `qqsort` | A (TTYD) | medium | 460 | yes | 100 | 10 | ~8 min (file already existed) | `bc91554` | Hardest so far, and only just inside the limit. TTYD's body, with a register noted for every local, gave correct instructions on attempt 1-2, but SPM's version allocates registers differently and the hints did not transfer. Attempts 2-7 (loop form, direct use of the global buffers, declaration order, `register`, copying parameters) left the callee-saved registers permuted. Attempt 8 found the cause: the sorting body is a separate helper that the compiler inlines, which ranks the two buffer pointers above the parameters; attempt 9 reversed the helper's local declarations. Attempt 10 fixed a 4-byte string-pool shift: a function that was stripped from the final game still leaves its string (`"./a"`) in the pool, so it has to exist in the source. That last fix also made upstream's `__assert2` exact (was 99.98%). SPM also adds two asserts TTYD lacks. |
| 25 | A-M8 | `romFontMake` | A (TTYD) | medium | 396 | yes | 100 | 4 | ~3 min (incl. creating `romfont.c`, 5 stubs) | `97c339f` | Loads the console ROM font and renders 135 glyphs. SPM's version is much simpler than TTYD's (a fixed character table instead of scanning message strings), so TTYD contributed only the local-variable names and the SDK call sequence. The table (135 values) was read out of the DOL. Structs were already in spm-headers. Attempt 1 had every instruction right; attempts 2-4 fixed the stack slot of a string buffer (8 bytes, not 4), the declaration order of five locals, the order of two loop increments, and a signed-vs-unsigned load. Left non-static with a TODO (its caller isn't decompiled). |
| 26 | B-M4 | `guideMain` | B (SPM-only) | medium | 476 | yes | 100 | 7 | ~3 min of work, after a pause between sessions (incl. creating `guide.c`, 27 stubs) | `cd589f6` | Tippi's per-frame update: two guard checks, a run-mode function table, an angle that eases towards 0 or 180. Logic was correct from attempt 1; `GuideWork` needed five new fields. Attempt 1: missing prototype (`marioGameGetSpeedScale` is in the symbol list but not in spm-headers). Attempts 2-4: read one flag from the global and the rest through a pointer, write a float test as `if (x)` rather than `x != 0.0f`, use single-precision `fabsf`. Attempts 5-7: one branch was laid out the other way round whatever the if/else order or helper shape; only writing the check as a `?:` expression matched. No reference source to compare against, so each of these was found by trial. |
| 27 | A-M10 | `mapGetBoundingBox` | A (TTYD) | medium | 484 | yes | 100 | 5 | ~3 min (incl. creating `mapdrv.c`, 109 stubs) | `d897f69` | Min/max over the bounding boxes of a map entry's objects. TTYD's body was nearly a template (SPM adds an entry index and returns through pointers), and every struct was already in spm-headers, so attempt 1 had all 121 instructions. Attempt 2: the scratch vector has to be declared inside the inner block (fixes its stack slot) and two pointers declared in the other order. Attempts 3-5: one address addition had swapped operands; it matched only when the code calls `mapGetWork()` (a real 20-byte function just before this one, which the compiler inlines; matched as a bonus in `fb4430a`) and indexes `entries[entryId]` directly instead of keeping an entry pointer. |
| 28 | A-L1 | `dispDraw` | A (TTYD) | large | 716 | yes | 100 | 2 | ~2 min (file already existed from A-S8) | `816afb7` | Walks the sorted draw list for one camera, sets GX state per render mode and calls each entry's callback. TTYD's body was a close template: the two `switch` statements and the GX call lists carried over with renumbered cases, and SPM adds a per-entry scissor rectangle before and after the callback. Four GX prototypes and the scissor struct fields had to be added, and two `DispEntry` fields are really unsigned. Attempt 1 was 95.6%; the only miss was reading the scissor record through a local pointer instead of indexing the array for each field. |
| 29 | A-L2 | `toRearPose` | A (TTYD) | large | 736 | yes | 100 | 2 | ~2 min (file already existed from A-S1) | `932e8f5` | Chain of 24 `strcmp`s mapping a pose name to its "rear" variant: large but simple, as expected. TTYD gave the shape (a result variable set in an `if`/`else if` chain); SPM drops TTYD's character check and has a different list, read from the DOL's string pool. The real work was the pool: the strings sit at offsets fixed by 30 earlier literals that belong to functions not yet decompiled. A data array of those literals (attempt 1) does not affect the pool; a clearly-marked temporary function that references them in order (attempt 2) does. It is left non-static with a TODO. |
| 30 | B-L1 | `pausewinEntry` | B (SPM-only) | large | 1136 | yes | 100 | 3 | ~4 min (file already existed from B-M2) | `971b186` | Finds a free pause-menu window slot, loads its texture file on first use, fills in the entry, then rebuilds a priority-sorted queue of active entries. Long, but each part is ordinary, and `PausewinEntry`/`PausewinWork` were already well described in spm-headers (two fixes needed: the count is signed, and the function-pointer offsets in the comments were wrong). Attempt 1: compile error (signed-to-unsigned cast). Attempt 2 had the whole structure; attempt 3 fixed declaration order of two locals, removed a struct temporary the original doesn't have, and wrote the sort comparison directly on the queue. One oddity kept as found: the "original position" is stored through a float-to-double-to-float conversion. |
| 31 | A-L3 | `parseGet1Next` | A (TTYD) | large | 840 | **no** | 99.71 | 10 (limit) | ~7 min (incl. creating `parse.c`, 7 stubs) | branch `wip/parseGet1Next` (`45d8353`) | First miss. TTYD's version is a stub beyond the three-line vector case, so this was effectively done without a reference: a hand-written tokenizer (skip whitespace and `//` comments, then copy a quoted string or `sscanf` a number). All 210 instructions are present and the logic is certainly right. Attempts 1-5 got there quickly (integer return type instead of the header's `bool`, a `switch` form, reading the nesting depth once, declaration order, indexed reads). Attempts 6-10 could not make one pair of callee-saved registers (output pointer and counter) come out the right way round in both string cases at once: fixing one case broke the other, and neither declaration order, block scoping, merging the counter with the result variable nor statement order settled it. Stalled on register allocation, not on understanding. Side finding: the original compares against the two-character constant `'/n'` where a newline was meant, so `//` comments are never terminated early. |
| 32 | A-L4 | `npcDelete` | A (TTYD) | large | 872 | **no** | 99.86 | 10 (limit) | ~8 min (incl. creating `npcdrv.c`, 254 stubs) | branch `wip/npcDelete` (`fd39526`) | Second miss, again on register allocation only. SPM's version takes a name instead of an entry and does far more than TTYD's (stops sounds, releases a caught NPC, runs a definition-table callback, deletes effects, parts, script and poses); TTYD supplied just the slave and linked-list sections. About ten `NPCEntry` fields had to be added, and 59 earlier string literals reproduced for the pool. Attempt 1 was already 89.9% with all the logic right. What moved it forward was discovering that three blocks are helpers the compiler inlines (pose release, sound-player loop, name search), each of which numbers its locals differently from the enclosing function: attempts 6-8 took it from 93% to 97.7%. The last difference, two registers swapped inside the inlined name search, did not respond to declaration order or to moving the loop back into the function. By-product on the branch: `npcGetWorkPtr` matches. |
| 33 | A-L5 | `windowDispGX_System` | A (TTYD) | large | 1184 | yes | 100 | 3 | ~5 min (file already existed, 9 of its functions done upstream) | `ede7078` | Draws a system window: advance a scrolling background once per frame, set up four fixed TEV stages, load a matrix, then four helper calls for the corners/edges per window type. Long but flat, and the existing file already had the includes and neighbours. I did not open TTYD's version of this function: I worked from the assembly alone, so this row says nothing about whether TTYD would have helped. Six SDK prototypes were missing from spm-headers. Attempt 1 was 95.9%; attempt 2 fixed statement order and the colour initialiser; attempt 3 passed the colour as a literal in the call, which is what puts the temporary and its copy in the original stack slots. |
| 34 | B-L2 | `fairyUpdate` | B (SPM-only) | large | 1232 | yes | 100 | 2 | ~5 min (file already existed from B-S3) | `f646bb2` | Per-frame Pixl update: a guard for paused states, a seven-way run-mode `switch`, then animation and angle easing. It went quickly for its size because of things learned earlier in the pilot: the angle-easing tail is the same code as `guideMain` (B-M4), so its three idioms were already known; and the two repeated blocks were recognised as real neighbouring functions that the compiler inlines (`fairySetAnim`, `fairyEnterRunMode`), so I decompiled those and called them (both match too, committed separately). Nine `FairyEntry` fields and five prototypes had to be added, plus the string-order helper for this file. Attempt 1 scored 99.98%; the only fix was the declaration order of two local vectors. Most of the time went on decoding the assembly and the jump table, not on matching. |

**Note 1 (commit slip):** a temp-file path failed while I was splitting `icondrv.c` into two commits. Result: `b3a0672` ("Decompile iconNameToPtr, start icondrv.c") only switches the file on in `configure.py`, and `7cd0f39` ("Decompile iconSetPos") contains both functions. Both were already pushed, so I did not rewrite history.

## Interim tally (computed from the table above; the large bucket is incomplete)

| Group | Size class | Done of planned | Matched | Attempts (all) | Attempts per function | Attempts per matched function |
|---|---|---|---|---|---|---|
| A | small | 10 of 10 | 10 | 13 | 1.3 | 1.3 |
| A | medium | 10 of 10 | 10 | 31 | 3.1 | 3.1 |
| A | large | 5 of 10 | 3 | 27 | 5.4 | 2.3 |
| B | small | 3 of 3 | 3 | 5 | 1.7 | 1.7 |
| B | medium | 4 of 4 | 4 | 15 | 3.8 | 3.8 |
| B | large | 2 of 3 | 2 | 5 | 2.5 | 2.5 |

These are counts for the functions done so far, not a conclusion. Group B is 10 functions against group
A's 30, so a single miss moves a B percentage by ten points. The large bucket is also the least
complete: 5 of 10 group A and 2 of 3 group B functions are done, and both misses are in it. The final
comparison waits until all 40 are attempted.

## In progress: A-L6 `camMain` (`0x80055208`, 1,260 bytes, group A, large)

**State: analysis only. No code written, 0 of 10 attempts used.** `src/camdrv.c` still lists
`// NOT_DECOMPILED camMain`, and the `spm-decomp` working tree is clean at `f646bb2` (nothing
uncommitted there).

Done so far:

- Read the whole target (327 lines of assembly) and TTYD's `camMain` (`ttyd/src/driver/camdrv.c`).
- SPM's function is much bigger than TTYD's. The opening of the per-camera loop looks the same (call the
  camera's callback, `LookAt`, roll rotation, view offset). After that SPM's has features TTYD's lacks:
  controller rumble (`wpadRumbleOn`/`wpadRumbleOff`, driven by a vector length via `sqrt` and a
  timing check that uses 64-bit division), a shake translation built from three floats, and an
  orthographic projection rebuild (`tan`, `cos`, `C_MTXOrtho`). TTYD's version has none of these, so
  I expect TTYD to help with the first part only.
- Nine float constants read from the DOL (deliberately not copied into this note; they go into the
  source when it is written, and one of them is the degrees-to-radians factor). The function also
  starts by computing one float from two values in a data table
  (`lbl_80407d88` +0x38 and +0x3c) into a `.sdata` variable (`lbl_805adf80`) and calling
  `func_80058b14`.
- From the offsets, `CamEntry` appears to have a roll angle at 0x84, a view offset at 0x88 to 0x90,
  and rumble and shake state between 0x290 and 0x2b4 (including two 64-bit values), none of which the
  header names yet. These are my reading of the assembly, not verified against anything.

Still to do: add those fields and prototypes (`C_MTXLookAt`, `PSMTXRotRad`, `func_80058b14`, `tan`,
and a way to write the 64-bit division that compiles to `__div2i`) to spm-headers, write the C, and
iterate. Because the function is large and float-heavy, I expect register allocation to be the hard
part, as in the other large functions.
