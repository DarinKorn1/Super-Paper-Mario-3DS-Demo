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
<!-- retry-end -->
