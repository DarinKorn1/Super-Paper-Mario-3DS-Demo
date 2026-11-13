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
