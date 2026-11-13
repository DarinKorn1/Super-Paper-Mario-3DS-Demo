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
