# Phase 2 results

Log for the functions in `phase2-targets.md` (camdrv.c, hitdrv.c, mapdrv.c; EU0). Queues (smallest first) are in
`notes/phase2-queue/<file>.txt` (name, address, bytes). Small functions (up to 128 bytes) are given to the subagent in
batches of up to 5 to save start-up cost; each still gets its own row. Resume with "Read CLAUDE.md and continue phase 2."

## Status (2026-11-13, stopped for the weekly usage limit; resets 2026-11-17)

- **camdrv.c:** every function attempted. 32 matched at 100%. Eight are functionally complete on wip branches: `func_80057da0` 92.3%, `func_80055c10` 99.92%
  (float pool), `func_80056948` 99.0%, `func_80058404` 99.88%, `func_8005885c` 99.95%, `camInit` 99.06%, `func_80055ce0` 99.50%, `cam3dMain` 90.49%.
  `camMain` (99.84%) has its body on master. Not linked yet.
- **hitdrv.c:** every function attempted. The rest matched at 100%, or differ only by a string/float pool label (file-level: `_hitEnt` 98.7%, `hitObjGetPos` 97.1%, on master).
  Near-misses on wip branches: `hitGetName` 93.1% (string pool only), `func_8006f710` 99.15%, `hitEntryMOBJ` 99.98% (string pool), `func_8006debc` and `func_8006e160` 96.8%,
  `hitCalcVtxPosition` 93.97%, `hitCheckVecFilter2` 99.87%, `func_800710b4` 99.30%, `func_800717d8` 99.66%. Not linked yet.
- **mapdrv.c:** not started (107 functions left; queue in `phase2-queue/mapdrv.txt`).
- **Lessons:** a function needs its OWN 10 builds (sharing builds across functions left three of them under-attempted); the strongest model closed
  `func_8006e400` and `func_8006f128` (both had been labelled functionally complete at 85-89%); a diff that is only a struct offset is a header fix (closed two);
  literals for float constants; direct maths instead of inline helpers.
- **To resume** ("Read CLAUDE.md and continue phase 2"): (1) on a scratch branch of `spm-decomp`, merge the hitdrv wip branches and see which differences remain;
  (2) one strongest-model pass over the register-numbering near-misses (hitdrv first: `func_8006f710`, `func_8006debc`, `func_8006e160`, `hitCheckVecFilter2`, `func_800710b4`,
  `func_800717d8`, `hitCalcVtxPosition`); (3) try linking `hitdrv.c` as Matching (main.dol must stay byte-identical); (4) same for `camdrv.c`; (5) start `mapdrv.c`, smallest first.
- **2026-11-13 strongest-model pass on local `scratch/hitdrv-link` (hitdrv.c Matching, 33 builds):** now 100%: `func_8006e400`, `func_8006f710`, `hitCheckVecFilter2`, `func_800717d8`, `func_8006debc`, `func_8006e160`, `hitObjGetPos`; still below: `func_800710b4` 99.68%, `_hitEnt` 99.03%, `hitCalcVtxPosition` 93.97% (all register numbering only), so main.dol still FAILED.
- **Stopped 2026-11-13 by the user.** Local branch `spm-decomp:scratch/hitdrv-link` (not pushed) holds hitdrv.c with every function and `Matching` in configure.py; all but `func_800710b4`, `_hitEnt` and `hitCalcVtxPosition` (93.97%) match at 100% there, last commit `b645a6a` is a WIP that did not compile (unused variables `idx`/`off`: remove them first). master is checked out and clean. relF.rel FAILED on that branch: cause not yet determined.
- **2026-11-13 overnight link attempt (hitdrv.c): not linked.** The WIP compiled as it was. Cause of the relF.rel failure found and fixed: `hitdrv.c` had no data splits, so its strings and floats were linked twice; `config/EU0/splits.txt` now gives it `.rodata 0x80328578-0x80328718` and `.sdata2 0x805AFFB0-0x805AFFD8` (bytes identical to the original). With `Matching`, relF.rel is now OK and extab/extabindex are 100%; main.dol still FAILED, only because of register numbering in two functions: `_hitEnt` 99.03% (packed-count loop: counter/temporaries use r5/r6/r9/r11 in a different order; about 35 source forms tried, none better) and `hitCalcVtxPosition` 94.16% (callee-saved registers r15-r31 assigned in a different order; about 110 compiles, far over the 12-build budget). `func_800710b4` is 100%. Findings for a later try at `hitCalcVtxPosition`: comparing against a `f32 zero` variable instead of the literal `0.0f` fixes the `fcmpu` operand order (in the body now); in the packed branch the declaration order `stride2, n, pj, pk, stride, plist` and `base, ia, ib, ic` before `peven, pva, pvb, pvc` reproduces the original's relative register order; `tri` must end up as ONE register (r28) for both branches, right after `i, count, mesh` (r31-r29), then `hit` (r27), which no form tried achieves. State: `spm-decomp` master `5307e91` (pushed) has every hitdrv.c function body and the data splits, hitdrv.c still `NonMatching`, main.dol and relF.rel OK; branch `scratch/hitdrv-link` (`2d5981d`, pushed) is the same with `Matching`.

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
| 50 | hitdrv.c | func_8006f884 | small | 156 | yes | 100 | 11 | e98999b | HitObj Mtx34 localMtx split at 0x9c fixed it |
| 51 | hitdrv.c | hitReinit | small | 160 | yes | 100 | 5 | 3e1134c | declare map before group, j before i, `j++, hit++` fixed regs |
| 52 | hitdrv.c | hitNameToPtr | small | 172 | yes | 100 | 10 | 3e1134c | needed explicit mapCount/hitCount locals to fix reg order |
| 53 | hitdrv.c | hitSubNameToPtr | small | 172 | yes | 100 | 10 | 3e1134c | same shape as hitNameToPtr (strstr) |
| 54 | hitdrv.c | func_8006f7cc | small | 184 | yes | 100 | 11 | e98999b | translate by x/10; HitObj Mtx34 at 0x9c fixed it |
| 55 | hitdrv.c | hitRecalcMatrices | small | 184 | yes | 100 | 4 | 3e1134c | declare map before group, `j++, hit++` |
| 56 | hitdrv.c | func_8006f710 | small | 188 | no, functionally complete | 99.15 | 10 | wip/func_8006f710 | builds active HitObj list (lbl_805ae830); only r4/r5 swap between map copy and joint temp |

| 57 | hitdrv.c | hitDelete | small | 204 | yes | 100 | 1 | 1c29606 | same loop shape as hitNameToPtr, first try |
| 58 | hitdrv.c | hitGetName | small | 232 | no, functionally complete | 93.1 | 2 | wip/hitGetName | separate `return ""` ifs fixed branches; only diff is string pool base+0xbe (file-level) |
| 59 | hitdrv.c | hitCheckFilter | small | 240 | yes | 100 | 4 | 1c29606 | new HitCheckQuery struct (size 0x50), keep old header param order, `query = &temp` pointer form |
| 60 | hitdrv.c | hitBindUpdate | small | 248 | yes | 100 | 1 | 1c29606 | TTYD shape + flag set before hitReCalcMatrix2; first try |
| 61 | hitdrv.c | hitCheckAttr | small | 248 | yes | 100 | 3 | 1c29606 | like hitCheckFilter; query->attr after distance |
| 62 | hitdrv.c | func_8006ef1c | small | 252 | yes | 100 | 3 | 1c29606 | per-tri single-sided check; block if/else for cullMode, `s32 i` declared before tri |
| 63 | hitdrv.c | func_80070790 | small | 264 | yes | 100 | 1 | 1c29606 | bbox init (+-10000.0f) via (Vec3){} literals, then func_8007058c |
| 64 | hitdrv.c | hitMain | medium | 316 | yes | 100 | 2 | 1c29606 | split HitObj mtx fields at 0x3c/0x6c; MapFileMeshTracks needed pointer array; local decl order fixed regs |
| 65 | hitdrv.c | hitReCalcMatrix2 | medium | 352 | yes | 100 | 2 | 5b66a69 | TTYD shape plus 0x2000 localMtx concat; a first `flags &= ~0x40` before the 0x20 test (besides the one after hitCalcVtxPosition) fixed the only diff |
| 66 | hitdrv.c | hitEntry | medium | 416 | yes | 100 | 9 | 5b66a69 | needs hitEntrySub written too (also 100) so it inlines; inline depth is cost-driven: a dead `s32 idx = mapEntryIdx` copy in hitEntrySub cut unrolling from 4 to 3 levels (inline_depth pragma has no effect); no `map` local in hitEntry fixed regs; mapGetJoints header now returns s32 |
| 67 | hitdrv.c | hitGetMapEntryBbox | medium | 476 | yes | 100 | 2 | 5b66a69 | copy of mapGetBoundingBox shape on HitObj; dropping the `joint` local (use hit->joint) fixed save-register count |
| 68 | hitdrv.c | hitGrpAttrOff | medium | 484 | yes | 100 | 1 | 5b66a69 | thin wrapper over recursive hitAtrOff(hit, mask, false), which self-inlines 3 levels; wrote hitAtrOff too (100) |
| 69 | hitdrv.c | hitGrpFlagOff | medium | 484 | yes | 100 | 1 | 5b66a69 | same with hitFlgOff (100); builds 1 to 5 shared one ninja run |
| 70 | hitdrv.c | hitEntryMOBJ | medium | 500 | no, functionally complete | 99.98 | 9 | wip/hitEntryMOBJ | only diff is string pool base/offsets (assert strings at +0x61/+0xb5 of the shared rodata); assert text recovered from rodata (SJIS message "あふれた"), line 0x134 |
| 71 | hitdrv.c | hitFlgOn | medium | 784 | yes | 100 | 1 | 6594b7f | twin of hitFlgOff, copied structure (batch of 4 twins built together) |
| 72 | hitdrv.c | hitGrpFlagOn | medium | 504 | yes | 100 | 1 | 6594b7f | twin of hitGrpFlagOff |
| 73 | hitdrv.c | hitAtrOn | medium | 784 | yes | 100 | 1 | 6594b7f | twin of hitAtrOff |
| 74 | hitdrv.c | hitGrpAttrOn | medium | 504 | yes | 100 | 1 | 6594b7f | twin of hitGrpAttrOff |
| 75 | hitdrv.c | func_8007058c | medium | 516 | yes | 100 | 2 | 6594b7f | bbox min/max recursion; only needed local order (out before in) for stack layout |
| 76 | hitdrv.c | func_80071f44 | medium | 580 | yes | 100 | 10 | 6594b7f | spheres-near-point query; needed local decl order for regs, `dist > r {} else` for branch, orig omits z^2 in bbox sqrt, map++ before i++; added HitQueryFilterCallback typedef |
| 77 | hitdrv.c | func_8006f47c | medium | 660 | yes | 100 | 7 | 6594b7f | nearest-hit variant of func_80071f44; query local sized 0x48 (not HitCheckQuery 0x50) to fix frame size; attr select via temp local with `if (param)`; float pool label diff only |
| 78 | hitdrv.c | func_8006debc | medium | 676 | no, functionally complete | 96.8 | 10 | wip/func_8006debc | ray-vs-tri XZ test (TTYD tempfunc); needs inline scalar vec helpers (PSVEC* would call); only FP reg numbering differs (normal.y kept in f5) |
| 79 | hitdrv.c | func_8006e160 | medium | 672 | no, functionally complete | 96.8 | 10 | wip/func_8006e160 | upward variant (TTYD tempfunc2); same reg-numbering diff as func_8006debc |
| 80 | hitdrv.c | func_8006f128 | medium | 852 | yes (retried with strongest model) | 100 | 10 + 7 retry | d251b49 | retried with strongest model: real `for (i = 0; i < 3; i++)` loop with `break` (not for(;;)), query via pointer, `maxDist = query->targetDistance = 10000.0f` chained (hoists const), `PSVecMag(param_3) * PSVecMag(&tri->normal)` without local, best declared before maxDist, and a 0x48-byte local buffer for the query (GPR save area overlaps a 0x50 HitCheckQuery) |
| 81 | hitdrv.c | hitObjGetPos | medium | 888 | yes (label-only diff) | 97.1 | 10 | 27415f8 | needed hitObjGetPosSub defined first (inlined 3 deep; Sub itself 100%); remaining diff is float pool label name only |
| 82 | hitdrv.c | func_8006e400 | medium | 896 | yes (retried with strongest model) | 100 | 10 + 5 retry | fbfb68f | retried with strongest model: TTYD checkTriVec_xz written out in full; key fix was the dot product written directly (not an inline helper) so normal.x/z stay in registers; first builds of the retry broke on a shell path-conversion slip |
| 83 | hitdrv.c | func_8006da4c | medium | 1136 | yes | 100 | 3 | 0ed0dde | full 3D variant of TTYD checkTriVec_xz (PSVECCrossProduct of targetDir with each edge); locals ordered v1,v2,v3,x0,x1,x2,scaled for stack; dist declared before cosAngle fixes f30/f31 |
| 84 | hitdrv.c | hitCalcVtxPosition | large | 1260 | no, functionally complete (retried with strongest model) | 93.97 | 10 + 10 retry | wip/hitCalcVtxPosition (7f1ddcc) | retried with strongest model: 83.9 -> 93.97; explicit `idx`/`off` and `o1`/`o2` offset variables updated before `k++` (letting the compiler derive them folds everything into one pointer IV), the packed-path vcd/GQR load written after the index selects, s32 return (caller casts to s16); remaining diff is register numbering only (callee-saved assignment, e.g. hit r27/i r31) plus volatile-register order in the packed block
| 85 | hitdrv.c | _hitEnt | large | 1360 | yes (label-only diff) | 98.7 | 3 | d9b0997 | TTYD version used as skeleton; asserts via __assert2 with strings read from rodata; remaining diff is string-pool label only; added HitObj field s16 at 0xe0 and s16 return type for hitCalcVtxPosition; first build error was s32->s16 cast, second was `hit++, i++` order |
| 86 | hitdrv.c | hitCheckVecFilter | large | 1708 | yes (retried with strongest model; label-only diff) | 100 | 8 | 00089ac | pilot row 39 had 99.70 on wip/hitCheckVecFilter; ported onto current master (callback is now `(HitObj *, HitObj *)`, added HitObj::nextActive at 0x110); last fix: `half = query->targetDistance / 2.0f` (dist loaded first, multiply operands dist*0.5); first build failed on CRLF line endings in the edit script
| 87 | hitdrv.c | hitCheckVecFilter2 | large | 1432 | no, functionally complete | 99.87 | 10 | wip/hitCheckVecFilter2 | multi-query sibling of hitCheckVecFilter (up to 50 queries, plane-distance cull on the target dir and a second axis); HitCheckQuery is really 0x48 with the result HitObj at 0x44; asserts via __assert/__assert2 with literal strings; `distance[j] = best[j] = ...` chained store and found[] stored last fixed IV order; `s32 singleSided` local and reusing `hit` as the result fixed registers; remaining diff: tri-loop and query-loop counters swap r18/r19 (declaration order and names had no effect)
| 88 | hitdrv.c | func_800710b4 | large | 1828 | no, functionally complete | 99.30 | 10 | wip/func_800710b4 (a0e21fe) | multi-query (stride 0x48, 1..50 queries) sibling of hitCheckVecFilter; no TTYD counterpart; HitCheckQuery shrunk to 0x48 with hitObj at 0x44 (no regressions); `q` pointer loop with `q++, j++`, `/ 2.0f`, found stored last, declaring `j` before `hit` fixed register numbering; remaining diff: block-1 load order (dist/radius) and string-pool offsets |
| 89 | hitdrv.c | func_800717d8 | large | 1900 | no, functionally complete | 99.66 | 10 (shared builds with func_800710b4) | wip/func_800717d8 (a0e21fe) | single-query sibling of hitCheckVecFilter with HitQueryFilterCallback and `*triOut = *foundTri`; only diff is tri/i register swap in the non-first blocks plus float-pool names; scoping i/tri per block just moved the swap between blocks |
