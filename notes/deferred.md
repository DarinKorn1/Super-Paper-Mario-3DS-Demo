# Deferred work

Not worked during phase 3. Older near-misses from before 2026-11-25 are the rows below 100% in `archive/phase3-results.md` and `phase2-results.md`.

## Huge functions (over 2,044 bytes): stub left in place

| Function | File | Bytes | Why / state |
|---|---|---|---|
| func_80138b38 | mario_hit.c | 4764 | huge: stub on master, WIP branch has 98.97% (committed 2026-11-20, logged 2026-11-25) |
| evt_npc_walk_to | evt_npc.c | 2280 | huge (over 2,044 B): stub left |
| func_8010ac50 | evt_npc.c | 2304 | huge (over 2,044 B): stub left |
| func_80154f3c | mario_status.c | 4320 | huge (over 2,044 B): stub left |
| func_8015c43c | mario_status.c | 2068 | huge (over 2,044 B): stub left |
| func_8015f104 | mario_status.c | 3440 | huge (over 2,044 B): stub left |
| func_801624b8 | mario_status.c | 4636 | huge (over 2,044 B): stub left |
| func_8016571c | mario_status.c | 3560 | huge (over 2,044 B): stub left |
| func_80168378 | mario_status.c | 7712 | huge (over 2,044 B): stub left |
| func_800d6674 | evt_sub.c | 3628 | huge, left out of the Antigravity queue 2026-11-25 |
| evt_eff | evt_eff.c | 2444 | huge, left out of the Antigravity queue 2026-11-25 |
| func_800e9178 | evt_frame.c | 2620 | huge, left out of the Antigravity queue 2026-11-25 |
| npcMain | npcdrv.c | 4972 | huge (over 2,044 B): stub left |
| npcHitMain | npcdrv.c | 8628 | huge (over 2,044 B): stub left |
| func_801ad058 | npcdrv.c | 3404 | huge (over 2,044 B): stub left |
| npcDispMain | npcdrv.c | 4128 | huge (over 2,044 B): stub left |
| func_801af4fc | npcdrv.c | 2560 | huge (over 2,044 B): stub left |
| func_801b0480 | npcdrv.c | 2192 | huge (over 2,044 B): stub left |
| func_801b0ed4 | npcdrv.c | 2832 | huge (over 2,044 B): stub left |
| func_801b2928 | npcdrv.c | 2680 | huge (over 2,044 B): stub left |
| mtx_setup | npcdrv.c | 3172 | huge (over 2,044 B): stub left |
| func_801b4514 | npcdrv.c | 2744 | huge (over 2,044 B): stub left |
| npcHitboxDisp | npcdrv.c | 2876 | huge (over 2,044 B): stub left |
| npcEntry | npcdrv.c | 2740 | huge (over 2,044 B): stub left |
| func_801b84d4 | npcdrv.c | 7248 | huge (over 2,044 B): stub left |
| func_801ba124 | npcdrv.c | 5592 | huge (over 2,044 B): stub left |
| func_801bba3c | npcdrv.c | 2964 | huge (over 2,044 B): stub left |
| func_801c25d8 | npcdrv.c | 2680 | huge (over 2,044 B): stub left |
| func_801c3d94 | npcdrv.c | 2064 | huge (over 2,044 B): stub left |
| func_801c5140 | npcdrv.c | 5288 | huge (over 2,044 B): stub left |
| func_801c65e8 | npcdrv.c | 6528 | huge (over 2,044 B): stub left |
| func_801c8d70 | npcdrv.c | 2724 | huge (over 2,044 B): stub left |
| func_801cb754 | npcdrv.c | 2096 | huge (over 2,044 B): stub left |
| func_801cdb84 | npcdrv.c | 3972 | huge (over 2,044 B): stub left |
| func_801cf16c | npcdrv.c | 4364 | huge (over 2,044 B): stub left |
| func_801d0640 | npcdrv.c | 2584 | huge (over 2,044 B): stub left |
<!-- huge-end -->

## Cleanup retries (candidates for a strongest-model retry later)

| Function | File | Bytes | State |
|---|---|---|---|
| evt_read_setup_file | evt_npc.c | 916 | 99.90% (string/label offsets only); stub on master, code on wip/ag-labelonly-20261125 |
| evt_npc_teleport_effect | evt_npc.c | 460 | 99.98% (string/label offsets only); stub on master, code on wip/ag-labelonly-20261125 |
| func_8010a5ec | evt_npc.c | 412 | 99.98% (string/label offsets only); stub on master, code on wip/ag-labelonly-20261125 |
| func_800fe92c | evt_npc.c | 324 | 99.98% (string/label offsets only); stub on master, code on wip/ag-labelonly-20261125 |
| evt_npc_check_3d | evt_npc.c | 312 | 99.99% (string/label offsets only); stub on master, code on wip/ag-labelonly-20261125 |
| func_8016af90 | mario_status.c | 356 | 96.08%, wip/func_8016af90 |
| func_8015801c | mario_status.c | 392 | 49.9%, wip/func_8015801c |
| func_80162328 | mario_status.c | 400 | 94%, wip/func_80162328 |
| func_8015ce30 | mario_status.c | 452 | 98%, wip/func_8015ce30 |
| func_8016456c | mario_status.c | 452 | 98%, wip/func_8016456c |
| func_80167ca0 | mario_status.c | 512 | 88%, wip/func_80167ca0 |
| func_80159a14 | mario_status.c | 560 | 98%, wip/func_80159a14 |
| func_801620f8 | mario_status.c | 560 | 89.7%, wip/func_801620f8 |
| func_80157cdc | mario_status.c | 592 | 98.55%, wip/func_80157cdc |
| func_80154ce8 | mario_status.c | 596 | 80%, wip/func_80154ce8 |
| func_8016c944 | mario_status.c | 616 | 88%, wip/func_8016c944 |
| func_8015778c | mario_status.c | 676 | 99.85%, wip/func_8015778c |
| func_80160350 | mario_status.c | 700 | 98%, wip/func_80160350 |
| func_80166618 | mario_status.c | 748 | 95%, wip/func_80166618 |
| func_80160048 | mario_status.c | 776 | 85%, wip/func_80160048 |
| func_80163a74 | mario_status.c | 864 | 94%, wip/func_80163a74 |
| func_8016bbf4 | mario_status.c | 1012 | 98.7%, wip/func_8016bbf4 |
| func_8016ccec | mario_status.c | 1452 | 99%, wip/func_8016ccec |
| func_8015d424 | mario_status.c | 1532 | 99.74%, wip/func_8015d424 |
| func_8015b264 | mario_status.c | 1556 | 90%, wip/func_8015b264 |
| func_80160944 | mario_status.c | 1580 | 0%, wip/func_80160944 |
| func_80164a74 | mario_status.c | 1740 | 85%, wip/func_80164a74 |
| func_8015a2f4 | mario_status.c | 1964 | 86.26%, wip/func_8015a2f4 9c78f18 |
| (71 functions) | many | - | moved off master 2026-11-27 (not exactly 100%): `git -C spm-decomp log --grep "to wip/"`, branches `wip/<name>` or `wip/<name>-master` |
| func_801ca198 | npcdrv.c | 12 | -%, wip/func_801ca198 d66d467 |
| npcSetAnim | npcdrv.c | 20 | 76.00%, wip/npcSetAnim 1d70030 |
| func_801c018c | npcdrv.c | 28 | -%, wip/func_801c018c ff41d6a |
| func_801c01c0 | npcdrv.c | 28 | -%, wip/func_801c01c0 7948787 |
| func_801c8d54 | npcdrv.c | 28 | 70.43%, wip/func_801c8d54 2d8596d |
| npcDisp | npcdrv.c | 28 | 34.29%, wip/npcDisp 3b3118f |
| npcDisp_xlu | npcdrv.c | 28 | 34.29%, wip/npcDisp_xlu 601b425 |
| func_801d25b8 | npcdrv.c | 60 | 92.67%, wip/func_801d25b8 3a80850 |
| func_801cc0cc | npcdrv.c | 76 | 87.58%, wip/func_801cc0cc a90e05d |
| func_801a96a4 | npcdrv.c | 88 | 81.36%, wip/func_801a96a4 f3e22c1 |
| func_801b2460 | npcdrv.c | 96 | 99.38%, wip/func_801b2460 9a3baac |
| func_801c99b0 | npcdrv.c | 116 | -%, wip/func_801c99b0 fc58a1e |
| npcGetDefense | npcdrv.c | 120 | 31.07%, wip/npcGetDefense 4fcc8f1 |
| func_801c360c | npcdrv.c | 136 | 95.97%, wip/func_801c360c 4e7450d |
| func_801c9a24 | npcdrv.c | 164 | 85.00%, wip/func_801c9a24 deeea99 |
| npcDisp_general | npcdrv.c | 164 | 89.76%, wip/npcDisp_general 85e1669 |
| func_801ca310 | npcdrv.c | 168 | 64.14%, wip/func_801ca310 518fe45 |
| npcNameToPtr | npcdrv.c | 168 | 94.00%, wip/npcNameToPtr 81eaf82 |
| npcUpdateSetupFile | npcdrv.c | 176 | 97.50%, wip/npcUpdateSetupFile c927965 |
| func_801aabe4 | npcdrv.c | 192 | 97.92%, wip/func_801aabe4 e3794d7 |
| func_801c3720 | npcdrv.c | 196 | 94.96%, wip/func_801c3720 6cf1a18 |
<!-- retry-end -->
