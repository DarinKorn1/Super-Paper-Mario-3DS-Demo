# Phase 3 log (EU0)

Rows 1-852 are in `notes/archive/phase3-results.md`. **Append only** (`python -I notes/tools/log_row.py`); never read this file whole.

| # | File | Function | Size class | Bytes | Matched | Match % | Attempts | Commit / branch | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 853 | mario_hit.c | func_80138b38 | huge | 4764 | deferred | 98.97 | - | wip/func_80138b38 4e08070 | huge: stub on master, WIP branch has 98.97% (committed 2026-11-20, logged 2026-11-25) |
| 854 | evt_npc.c | evt_npc_walk_to | huge | 2280 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 855 | evt_npc.c | func_8010ac50 | huge | 2304 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 856 | mario_status.c | func_80154f3c | huge | 4320 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 857 | mario_status.c | func_8015c43c | huge | 2068 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 858 | mario_status.c | func_8015f104 | huge | 3440 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 859 | mario_status.c | func_801624b8 | huge | 4636 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 860 | mario_status.c | func_8016571c | huge | 3560 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 861 | mario_status.c | func_80168378 | huge | 7712 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 862 | mario_status.c | func_80154c80 | tiny | 4 | yes | 100 | 1 | f2b5718 | matched first build |
| 863 | mario_status.c | func_80154c84 | tiny | 4 | yes | 100 | 1 | f2b5718 | matched first build |
| 864 | mario_status.c | func_80158644 | tiny | 4 | yes | 100 | 1 | f2b5718 | matched first build |
| 865 | mario_status.c | func_80161b74 | tiny | 4 | yes | 100 | 1 | f2b5718 | matched first build |
| 866 | mario_status.c | func_8016c0ac | tiny | 8 | yes | 100 | 1 | f2b5718 | matched first build |
| 867 | mario_status.c | func_80164028 | tiny | 16 | yes | 100 | 1 | f2b5718 | matched first build |
| 868 | mario_status.c | func_80164038 | tiny | 16 | yes | 100 | 1 | f2b5718 | matched first build |
| 869 | mario_status.c | func_80162014 | tiny | 24 | yes | 100 | 1 | f2b5718 | matched first build |
| 870 | mario_status.c | func_801599f8 | tiny | 28 | yes | 100 | 1 | f2b5718 | matched first build |
| 871 | mario_status.c | func_80158930 | tiny | 40 | yes | 100 | 1 | f2b5718 | matched first build |
| 872 | mario_status.c | func_8016a76c | tiny | 40 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 873 | mario_status.c | func_801571bc | tiny | 44 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 874 | mario_status.c | func_80157420 | tiny | 44 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 875 | mario_status.c | func_80157ff0 | tiny | 44 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 876 | mario_status.c | func_8016ccc0 | tiny | 44 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 877 | mario_status.c | func_80157cac | tiny | 48 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 878 | mario_status.c | func_80160914 | tiny | 48 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 879 | mario_status.c | func_801669ac | tiny | 52 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 880 | mario_status.c | func_80167298 | tiny | 52 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 881 | mario_status.c | func_80160010 | tiny | 56 | yes | 100 | 3 | 05b72e0 | two compile errors first (missing prototypes, unused param); then matched |
| 882 | mario_status.c | func_801644d8 | tiny | 60 | yes | 100 | 2 | cdbfdfb | separate early-return ifs gave bltlr/bgelr |
| 883 | mario_status.c | func_8015ea78 | tiny | 64 | yes | 100 | 4 | cdbfdfb | 2.0f * n / 4.0f + 1.0f gave fmadds operand order; one failed compile in variants |
| 884 | mario_status.c | func_8016c608 | tiny | 64 | yes | 100 | 1 | cdbfdfb | matched first try |
