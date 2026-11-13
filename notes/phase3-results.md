# Phase 3 results

## BLOCKED (2026-11-13, ~9:35 AM): stray objdiff-cli rewrites build.ninja

A stale `objdiff-cli.exe diff -p . -u main/mapdrv mapObjFlagOn` (PID 16768, started 4:22 AM, left behind by a phase 2 subagent) keeps
spawning `ninja`/`configure.py` in `spm-decomp`, so `build.ninja` is "still dirty after 100 tries" and no build can finish. Killing it
was denied by the permission classifier, so the run stopped here. **To resume: close that process** (Task Manager, or
`Stop-Process -Id 16768 -Force` in PowerShell), then tell Claude "Read CLAUDE.md and continue the overnight run".
Nothing is broken: spm-decomp master is clean, builds OK (last verified before the block) and is pushed.

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
