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
| 15 | camdrv.c | func_800583b4 | small | 80 | yes | 100 | 2 | ce2cca4 | call func_80053198 must be hoisted before the camPtrTbl load; placeholder name kept |
| 16 | camdrv.c | func_80055b58 | small | 92 | yes | 100 | 2 | ce2cca4 | flag tests on arg2->4; final test needed explicit if/return true/false; placeholder name kept |
| 17 | camdrv.c | func_80055bb4 | small | 92 | yes | 100 | 2 | ce2cca4 | second flag mask is 0x80000000 (clrrwi), then !(f & 0x2000); placeholder name kept |
| 18 | camdrv.c | func_800587a0 | small | 96 | yes | 100 | 1 | ce2cca4 | shake setup using gp->time (OSTime) twice; placeholder name kept |
| 19 | camdrv.c | func_80057e4c | small | 120 | yes | 100 | 1 | ce2cca4 | zoom start copy; new header fields 0x248/0x24c/0x250; placeholder name kept |
| 20 | camdrv.c | func_80058700 | small | 160 | yes | 100 | 1 | 131e77e | like func_800587a0 but duration = (s32)(a * gp->gameSpeed), rumbleState 0; placeholder name kept |
| 21 | camdrv.c | camLoadRoadNoRead | small | 180 | yes | 100 | 3 | 131e77e | assert strings recovered from main.dol (cond text is "!flag(cp->flag, CAMFLAG_LoadBin)", SJIS message; source must be UTF-8 for sjiswrap); macro stringify expanded the condition so call __assert2 directly; float literals 0.0f/1.0f |
| 22 | camdrv.c | func_80057ce0 | small | 192 | yes | 100 | 3 | 131e77e | tan(0.21816615760326385) double literal; 0.5 needs extern lbl_805afc00 (literal swaps fmuls operands) |
| 23 | camdrv.c | func_80057da0 | small | 172 | no, functionally complete | 92.3 | 8 | wip/func_80057da0 | scheduler hoists the 6 dest-vector loads above the start copies with descending f5..f0; could not reproduce register/load order |
| 24 | camdrv.c | camUnloadRoad | small | 196 | yes | 100 | 1 | 726cc78 | flag-mask clears decoded from rlwinm; straightforward |
| 25 | camdrv.c | func_80055c10 | small | 208 | no, functionally complete | 99.9 | 1 | wip/func_80055c10 | HitObj attr to height table; same 99.9 as old wip (likely sdata2 constant symbol pooling, not fixable per-function) |
| 26 | camdrv.c | func_80058c80 | small | 216 | yes | 100 | 1 | 726cc78 | needed bool return types in acdrv.h/evt_door.h for callee stubs; local struct for lbl_805adf78 |
| 27 | camdrv.c | func_800550f8 | medium | 272 | yes | 100 | 3 | 2f02f3a | viewport/scissor setup; float zero must be a literal (not the lbl_ extern) to pool correctly; store order of chained assign mattered |
| 28 | camdrv.c | func_80056948 | medium | 280 | no, functionally complete | 99.0 | 5 | wip/func_80056948 | map-name table clamp; only f0/f1 swap in clamp compare plus sdata2 literal names left; no TTYD counterpart |
| 29 | camdrv.c | camDraw | medium | 328 | yes | 100 | 4 | 2f02f3a | float constants (1.0, 32767.0) must be literals, and the `if (cp != NULL && ...)` block form (not continue) made the compiler hoist them to f30/f31 |
| 30 | camdrv.c | camLoadRoadAsync | medium | 368 | yes | 100 | 1 | f6ac878 | fileAsyncf/fileAllocf with "%s/%s/camera_road.bin" (format decoded from rodata); `(s32) file == -1` compare needed |
| 31 | camdrv.c | func_80058128 | medium | 364 | yes | 100 | 1 | f6ac878 | per-field copies between camPtrTbl[b] and [a]; made PSMTX44Copy a real prototype |
| 32 | camdrv.c | func_80058b14 | medium | 364 | yes | 100 | 1 | f6ac878 | fade-state update; split unknown_0x2b8 into three s32 fields in camdrv.h |
| 33 | camdrv.c | camEntryPersp | large | 608 | yes | 100 | 1 | 68975b0 | TTYD inline gave the shape; widescreen flag + aspect scale; typed DEMOGetRenderModeObj/SCGetAspectRatio/PSVECDistance in spm-headers |
| 34 | camdrv.c | camEntryOrtho | large | 664 | yes | 100 | 1 | 68975b0 | same pattern; fabsf for aspect (fabs is double, error 10317); ortho widens left/right by 1.3684211 for cams other than 0, 1, 13 |
| 35 | camdrv.c | func_80057ee8 | large | 576 | yes | 100 | 9 | 6ea882c | `(f32)(f64)x` forced the stray frsp; `(Vec3){x,y,z}` compound literal fixed stack temp order; local cp2d pointer fixed register choice; split chained 1.0f assignments |
| 36 | camdrv.c | func_80058404 | large | 664 | no, functionally complete | 99.88 | 4 | wip/func_80058404 (254a956) | only two fmuls differ in operand order (fov*0.5 constant/register swap); both orders of the C produce the same code; split lbl_80407d88 field 0x20 and CamEntry 0x1d0..0x204 fields in the headers |
| 37 | camdrv.c | func_8005885c | large | 696 | no, functionally complete | 99.95 | 10 | wip/func_8005885c (f764b9b) | TTYD camLetterBoxDraw gave the shape; only the stack slots of the fog GXColor and the mat-colour temp are swapped; needed a GXGetScissor prototype and an inline GX FIFO s16 write helper |
| 38 | camdrv.c | camInit | large | 1020 | no, functionally complete | 99.06 | 10 | wip/camInit (aab4cf8) | TTYD gave the call list; the pos Vec3 temps only matched with a local `f32 zero = 0.0f` declared after the tan() call (constant zero in a compound literal becomes integer stores); remaining diff is register numbering plus float-pool names |
| 39 | camdrv.c | func_80055ce0 | huge | 3176 | no, functionally complete | 99.50 | 12 | wip/func_80055ce0 (b0090b7) | started from 43b6592 (98.2%); stack layout fixed by making the hitCheckFilter outputs 7 separate f32 locals declared after the Vec3 dir (array put them above dir); ternary store, `(f32)(double)tgt`, pp/i decl order and `pp++, i++` fixed more; left: float reg numbering (f30/f31/f25/f27), one li/stw order at entry, and f0/f1 swap in one followY clamp; rodata pool offsets are file-level |
| 40 | camdrv.c | cam3dMain | huge | 4688 | no, functionally complete | 90.49 | 10 | wip/cam3dMain (c16b441) | Rebased wip 64bc56c (89.5%) onto current master header/names; frame size now matches (0x110) after loading place->target before place->pos and assigning pos/target locals once then destTarget/destPos; Vec3 pos/target stay scalarised (orig keeps them contiguous on stack) and the two up-vector literals schedule differently; remaining diff is mostly the stack slot order, load order and float register numbering |
| 41 | hitdrv.c | hitInit | tiny | 4 | yes | 100 | 1 | b6f3ce1 | TTYD gave logic; added worldMtx/centerWorld/radius to HitObj |
| 42 | hitdrv.c | chkFilterAttr | tiny | 24 | yes | 100 | 1 | b6f3ce1 | TTYD gave logic; added worldMtx/centerWorld/radius to HitObj |
| 43 | hitdrv.c | hitGetAttr | tiny | 24 | yes | 100 | 1 | b6f3ce1 | TTYD gave logic; added worldMtx/centerWorld/radius to HitObj |
| 44 | hitdrv.c | hitReCalcMatrix | small | 96 | yes | 100 | 1 | b6f3ce1 | TTYD gave logic; added worldMtx/centerWorld/radius to HitObj |
| 45 | hitdrv.c | hitObjAttrOff | small | 136 | yes | 100 | 6 | b6f3ce1 | TTYD gave logic; shared batch; `allowSubName == false` test + if/else block form fixed branch order |
| 46 | hitdrv.c | hitObjAttrOn | small | 136 | yes | 100 | 6 | b6f3ce1 | TTYD gave logic; shared batch; `allowSubName == false` test + if/else block form fixed branch order |
| 47 | hitdrv.c | hitObjFlagOff | small | 136 | yes | 100 | 6 | b6f3ce1 | TTYD gave logic; shared batch; `allowSubName == false` test + if/else block form fixed branch order |
| 48 | hitdrv.c | hitObjFlagOn | small | 136 | yes | 100 | 6 | b6f3ce1 | TTYD gave logic; shared batch; `allowSubName == false` test + if/else block form fixed branch order |
| 49 | hitdrv.c | hitBindMapObj | small | 140 | yes | 100 | 1 | 3e1134c | TTYD gave logic; matched first build |
| 50 | hitdrv.c | func_8006f884 | small | 156 | no, functionally complete | 99.95 | 10 | wip/func_8006f884 | scale of a HitObj matrix; only diff is matrix offset (target 0x9c; HitObj needs a Mtx34 at 0x9c splitting unknown_0x3c) - not rebuilt, build limit hit |
| 51 | hitdrv.c | hitReinit | small | 160 | yes | 100 | 5 | 3e1134c | declare map before group, j before i, `j++, hit++` fixed regs |
| 52 | hitdrv.c | hitNameToPtr | small | 172 | yes | 100 | 10 | 3e1134c | needed explicit mapCount/hitCount locals to fix reg order |
| 53 | hitdrv.c | hitSubNameToPtr | small | 172 | yes | 100 | 10 | 3e1134c | same shape as hitNameToPtr (strstr) |
| 54 | hitdrv.c | func_8006f7cc | small | 184 | no, functionally complete | 99.96 | 10 | wip/func_8006f7cc | translate by x/10; diffs: matrix offset 0x9c vs 0xc (needs Mtx34 at 0x9c) + float pool name (file-level) |
| 55 | hitdrv.c | hitRecalcMatrices | small | 184 | yes | 100 | 4 | 3e1134c | declare map before group, `j++, hit++` |
| 56 | hitdrv.c | func_8006f710 | small | 188 | no, functionally complete | 99.15 | 10 | wip/func_8006f710 | builds active HitObj list (lbl_805ae830); only r4/r5 swap between map copy and joint temp |
