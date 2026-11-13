# Phase 3 results

## Block resolved (2026-11-13 10:15)
A stray `objdiff-cli diff` (4:22 AM) plus later forced kills of ninja corrupted `.ninja_deps`/`.ninja_log` in `spm-decomp`, making `build.ninja`
regenerate forever ("still dirty after 100 tries"; `ninja -d explain` showed "stored deps info out of date for build/EU0/config.json").
Fix: moved the two (git-ignored) files out of the way into the scratchpad (`.../scratchpad/ninjabak/`), ran `ninja` once (full rebuild, exit 0, main.dol OK, relF.rel OK).
If it recurs: stop ninja/objdiff-cli running in spm-decomp only, move `.ninja_deps` and `.ninja_log` aside, re-run ninja. Never force-kill ninja mid-build.

## Resume state (updated 2026-11-13, after phase 2)
- Phase 2 is finished except optional retries. hitdrv.c and mapdrv.c are NOT linked (hitdrv: `_hitEnt` 99.03%, `hitCalcVtxPosition` 94.16%; mapdrv: 50 of 109 functions below 100%, 11 data labels still extern and section sizes off; see Status in phase2-results.md). `scratch/mapdrv-link` and `scratch/hitdrv-link` are pushed to origin; master holds all 100% bodies and splits and builds OK.
- Optional strongest-model retries (once each) if time remains: `mapSetMaterialFog` 62.6%, `func_80084098` 75.3% (only 1 build used), `func_80083eb4` 73.5%, `mapInit` 81.9%, `spline_getvalue` 86.9%, `func_80084274` 88.5%, `mapCalcAnimMatrix` 89.8%, `_mapEnt` 88.9%, `mapDisp` 88.9%.
- Phase 3 follows `notes/phase3-plan.md` (116 files; first guide.c, fairy.c, evt_mario.c, mario.c ...). Generate a file's queue with `python -I notes/phase3-queue/make_queue.py <file>.c` (writes notes/phase3-queue/<file>.txt, smallest first). Small (<=128 B) functions go 5 per subagent; others one per subagent. Log below.
- Decision to review: in phase 2 mediums were (mistakenly) batched 5 per subagent before the user's rule change; phase 3 follows the rule.

## Log

| # | File | Function | Size class | Bytes | Matched | Match % | Attempts | Commit / branch | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | guide.c | func_80121bc8 | small | 4 | yes | 100 | 1 | 9530a24 | tail call to func_8012167c |
| 2 | guide.c | guideGetWork | small | 12 | yes | 100 | 1 | 9530a24 | returns &work |
| 3 | guide.c | func_80121ba4 | small | 36 | yes | 100 | 1 | 9530a24 | copies Vec3 at 0x58 (header field typed) |
| 4 | guide.c | func_80121d84 | small | 48 | no, functionally complete | 82.08 | 10 | wip/func_80121d84 | same as inline guideIsActive; branch layout/rlwinm differs, objdiff-cli has no one-shot output so could not see diff |
| 5 | guide.c | guideEnterRunMode1 | small | 56 | yes | 100 | 1 | 9530a24 | straightforward |
| 6 | guide.c | guideInit | small | 68 | yes | 100 | 1 | 290f6d4 | memset + animPoseId=-1 |
| 7 | guide.c | func_80121900 | small | 72 | yes | 100 | 2 | 290f6d4 | 25.0f * field, *0.4f if mario flag; constants read from sdata2; call marioGetPtr first |
| 8 | guide.c | func_80121948 | small | 72 | yes | 100 | 1 | 290f6d4 | same as func_80121900 with field y |
| 9 | guide.c | guideEnterRunMode2 | small | 76 | yes | 100 | 1 | 290f6d4 | matched first try (dead-looking runMode checks kept) |
| 10 | guide.c | guideCanSearch | small | 80 | yes | 100 | 1 | 290f6d4 | reuses guideIsActive inline |
| 11 | guide.c | func_80121db4 | small | 100 | yes | 100 | 3 | 6af1bca | needed a second ternary-form inline (active && !(flag0&0x100)); calling guideCanSearch gave wrong branch shape |
| 12 | guide.c | guideEnterRunMode5 | small | 124 | yes | 100 | 1 | 6af1bca | header fix: split unknown_0x28 to expose 0x30 f32 and 0x34 Vec3; dead runMode!=5 check kept |
| 13 | guide.c | guideSetAnim | small | 124 | yes | 100 | 1 | 6af1bca | header fix: curAnimName is const char *, not char[4]; same logic as fairy |
| 14 | guide.c | func_801215f0 | small | 140 | no, functionally complete | 99.43 | 7 | wip/func_801215f0 | only f0/f1 register swap on the 1.0f + table[character] add (const load scheduled before lfsx in original); header declaration changed UNKNOWN_FUNCTION to f32 |
| 15 | guide.c | guideEnterRunMode | medium | 152 | no, functionally complete | 96.68 | 1 | wip/guideEnterRunMode | only diff: string pool base (original uses a shared @stringBase with __FILE__ at +0x30; our file has no earlier strings yet, so base differs); should resolve once earlier guide.c functions are decompiled |
| 16 | guide.c | runMode0Main | small | 156 | no, functionally complete | 97.05 | 1 | wip/runMode0Main | only diff: string pool base ("Z_1" is @stringBase+0x18, our file has no earlier strings yet); logic: clear flag3 bit0, guideSetAnim("Z_1") |
| 17 | guide.c | func_80121d84 | small | 48 | yes (retry, strongest model: Fable 5.2) | 100 | 2 | 2f621a1 | it is the non-inlined guideIsActive check: `return guideIsActive(wp);` with `wp = &work`; an if/return form gave the same instructions with the two return blocks swapped, the ternary inline form matched; no string-pool refs so no label diffs; main.dol OK, relF.rel OK |
| 18 | guide.c | runMode1Main | small | 172 | no, functionally complete | 87.49 | 6 | wip/runMode1Main | logic: marioGetPtr() (unused), if flag3&1 { clear, unknown_0x70=0, guideSetAnim("S_2") inlined }; remaining diff only register allocation (ours uses r29/r30/r31 with larger frame, original reuses wp reg r31 for name); string-pool label diffs also present |

Splits for guide.c (spm-decomp master): added .rodata 0x803335B8-0x80333648, .data 0x80426590-0x804265E8, .bss 0x80510398-0x80510450, .sdata2 0x805B2330-0x805B23C8 (derived from referenced symbols, fairy.c refs below, mario.c start above). main.dol OK, relF.rel OK. Measured on scratch branches (deleted): guideEnterRunMode 96.68 (unchanged), runMode0Main 97.05 (unchanged), func_801215f0 99.43 (unchanged), func_80121d84 82.08 (no real body on its wip branch; wip/func_80121d84 is stale and conflicts with master). Remaining string-pool diff is not fixed by these splits: guide.c's strings do not appear to be in the 0x803334A8 block (which holds fairy.c strings incl. "fairy.c"); location of guide.c's strings still unknown.
