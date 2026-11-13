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

| 6 | camdrv.c | func_80057cb0 | small | 24 | yes | 100 | 1 | 5dd9be3 | C_MTXPerspective(projMtx, fovY, aspect, near, far) tail call; placeholder name kept |
| 7 | camdrv.c | func_80057cc8 | small | 24 | yes | 100 | 1 | 5dd9be3 | calls func_80058128(cam_no, 3D cam_no); param types guessed; placeholder name kept |
| 8 | camdrv.c | func_80058800 | small | 28 | yes | 100 | 1 | 5dd9be3 | returns flag bit 0x80000; new header proto; placeholder name kept |
| 9 | camdrv.c | camCheck3d | small | 36 | yes | 100 | 1 | 5dd9be3 | rollAxisMode != 0; placeholder name kept |
| 10 | camdrv.c | func_80057ec4 | small | 36 | yes | 100 | 1 | 5dd9be3 | cameraMode == 2; placeholder name kept |
| 11 | camdrv.c | func_8005881c | small | 36 | yes | 100 | 2 | 5dd9be3 | 3D cam f32 at 0x2e0 > lbl_805afbb0; 2nd attempt (< gave wrong cr bit); placeholder name kept |
| 12 | camdrv.c | func_80058388 | small | 44 | yes | 100 | 1 | 5dd9be3 | returns one of two sdata floats by rollAxisMode; placeholder name kept |
| 13 | camdrv.c | func_8005869c | small | 44 | yes | 100 | 1 | 5dd9be3 | signed compare of new fields 0xe0/0xe4; placeholder name kept |
| 14 | camdrv.c | func_800586c8 | small | 56 | yes | 100 | 1 | 5dd9be3 | stores Vec3 + 3 floats into new fields 0x2c8-0x2dc; placeholder name kept |
