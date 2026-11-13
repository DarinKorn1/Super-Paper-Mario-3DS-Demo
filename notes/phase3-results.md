# Phase 3 results

## Block resolved (2026-11-13 10:15)
A stray `objdiff-cli diff` (4:22 AM) plus later forced kills of ninja corrupted `.ninja_deps`/`.ninja_log` in `spm-decomp`, making `build.ninja`
regenerate forever ("still dirty after 100 tries"; `ninja -d explain` showed "stored deps info out of date for build/EU0/config.json").
Fix: moved the two (git-ignored) files out of the way into the scratchpad (`.../scratchpad/ninjabak/`), ran `ninja` once (full rebuild, exit 0, main.dol OK, relF.rel OK).
If it recurs: stop ninja/objdiff-cli running in spm-decomp only, move `.ninja_deps` and `.ninja_log` aside, re-run ninja. Never force-kill ninja mid-build.

## Resume state
- Phase 2 hitdrv.c: NOT linked (main.dol fails; `_hitEnt` 99.03%, `hitCalcVtxPosition` 94.16%), master has all bodies + rodata/sdata2 splits.
- Phase 2 mapdrv.c: queue done through `_mapDispMapObj`, `mapSetPolygon` (log rows 90-187 in phase2-results.md). Left unattempted:
  `mapSetMaterial` (1800), `mapDisp` (2092, huge, 12 builds), `mapLoad` (8840, huge), `mapSetMaterialTev` (10212, huge).
- Then: one strongest-model retry (once each) for the "incomplete"/low ones: `mapEntrySub` 0%, `mapSearchDmdJointSub` 48.4% (both: recursion inlines
  one level off), `mapSetMaterialFog` 62.6%, `func_80084098` 75.3% (only 1 build used), `func_80083eb4` 73.5%, `mapInit` 81.9%,
  `spline_getvalue` 86.9%, `func_80084274` 88.5%, `mapCalcAnimMatrix` 89.8%, `_mapEnt` 88.9%, `mapSetMaterialFogMapObj` 88.9%.
- Then try linking mapdrv.c (add `.rodata`/`.sdata2` splits in config/EU0/splits.txt like hitdrv; several wip functions differ only by string-pool offsets).
- Then phase 3 from `notes/phase3-plan.md` (116 files; first: guide.c, fairy.c, evt_mario.c, mario.c ...).
- Decision to review: mediums were batched 5 per subagent (not only <=128 B) to save start-up cost.

## Overnight summary

| Item | Count |
|---|---|
| Functions attempted | 0 |
| Matched | 0 |
| Functionally complete | 0 |
| Incomplete | 0 |
| Files finished or linked | none |
| Decisions to review | none yet |

## Log

| # | File | Function | Size class | Bytes | Matched | Match % | Attempts | Commit / branch | Notes |
|---|---|---|---|---|---|---|---|---|---|
