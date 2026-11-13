# Phase 2 results

Log for the functions in `phase2-targets.md` (camdrv.c, hitdrv.c, mapdrv.c; EU0). Queues (smallest first) are in
`notes/phase2-queue/<file>.txt` (name, address, bytes). Small functions (up to 128 bytes) are given to the subagent in
batches of up to 5 to save start-up cost; each still gets its own row. Resume with "Read CLAUDE.md and continue phase 2."

## Log

| # | File | Function | Size class | Bytes | Matched | Match % | Attempts | Commit / branch | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | camdrv.c | camGetCurNo | tiny | 8 | yes | 100 | 1 | 4488ac3 | one shared commit for all 5; extern s32 lbl_805ae7b8 (current cam no) |
| 2 | camdrv.c | camUnusedCheck | tiny | 8 | yes | 100 | 1 | 4488ac3 | returns false |
| 3 | camdrv.c | camGetPtr | tiny | 20 | yes | 100 | 1 | 4488ac3 | camPtrTbl[id] |
| 4 | camdrv.c | func_80058840 | tiny | 20 | yes | 100 | 1 | 4488ac3 | no TTYD name; sets camPtrTbl[CAM_ID_3D] f32 at 0x2e4 (new CamEntry field unknown_0x2e4); kept name |
| 5 | camdrv.c | camGetCurPtr | tiny | 24 | yes | 100 | 1 | 4488ac3 | camPtrTbl[curNo] |
