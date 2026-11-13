# Phase 2 targets (proposal, EU0)

Chosen 2026-11-12 from the EU0 config (`config/EU0/splits.txt`, `symbols.txt`) and `configure.py`. Nothing built.
Goal: take 3 source files to **Matching** (all functions matched, then linked in). All three are `NonMatching`
today, have a Thousand-Year Door counterpart (`ttyd/.../camdrv.c`, `hitdrv.c`, `mapdrv.c`) as a reference, and are
what the 3DS port needs first: camera, collision, map load/draw.

| File | Functions | Already done | Left | Bytes (all) | small / medium / large / huge (left) |
|---|---|---|---|---|---|
| `camdrv.c` | 42 | `getScreenPoint` | 41 | 17,748 | 19 / 16 / 5 / 2 (`func_80055ce0` 3,176; `cam3dMain` 4,688) |
| `hitdrv.c` | 54 | `hitObjGetNormal` | 53 | 29,376 | 5 / 31 / 18 / 0 (largest 1,900) |
| `mapdrv.c` | 109 | `mapGetWork`, `mapGetBoundingBox` | 107 | 76,320 | 21 / 52 / 33 / 3 (`mapLoad` 8,840; `mapDisp` 2,092; `mapSetMaterialTev` 10,212) |
| **Total** | **205** | 4 | **201** | **123,444** | |

(Size classes as in `remaining-work.md`; "large" here is 700-2,044, "huge" over 2,044; the 129-199 and 641-699 gaps are
folded into medium and large.)

## Existing work to reuse

- `wip/camMain` (camMain 99.84%, `cam3dMain` 89.5% functionally complete, `func_80055ce0`, `func_80055c10`,
  `func_80056948`) and `wip/cam2d` (camMain only): merge/cherry-pick these into `camdrv.c` first instead of redoing
  them. Both are my own branches, pushed to `origin`.
- `wip/hitCheckVecFilter` (99.70%, functionally complete): reuse for `hitdrv.c`.
- Pilot rows already show `camdrv`/`hitdrv`/`mapdrv` stubs exist, so no file creation is needed.

## Exclusions checked

- Upstream WIP branches (`upstream/animdrv-test`, `upstream/wpadmgr`, `clang-format`): none touch these files.
- `spm-decomp-ag/notes/ag-trial-functions.md`: only `evt_pouch.c` and `evt_sub.c`; no overlap.
- Other agent's folder `spm-decomp-ag` is not touched.

## Honest size warning

`mapdrv.c` alone is 76 KB, 62% of the total, with three huge functions (about 21 KB between them), so it is more than
the other two files together. Plan: do `camdrv.c` and `hitdrv.c` first (94 functions), `mapdrv.c` last and stop
cleanly at the usage limit; huge functions go last in each file. If you want a cheaper third file, the alternative is
a smaller map-adjacent unit, but `evt_map.c` (31 fns, 7.4 KB), `evt_hit.c` (16 fns, 6 KB) and `evt_cam.c` (21 fns,
4 KB) are all `NonStarted` (the source file would be created first) and are script glue rather than loading/drawing.

## Order of work

Per file, smallest function first; medium/large ending "incomplete" with Sonnet get one retry with the strongest
model; then try linking the whole file (Matching only if `main.dol` stays byte-identical).
