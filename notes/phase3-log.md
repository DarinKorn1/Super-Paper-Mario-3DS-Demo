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
| 885 | mario_status.c | func_80166968 | small | 68 | yes | 100 | 1 | 1226121 | early return then compare subMotionId |
| 886 | mario_status.c | func_8015eab8 | small | 72 | yes | 100 | 1 | 1226121 | 25 * (2n/4 + 1) |
| 887 | mario_status.c | func_8015eb00 | small | 72 | yes | 100 | 1 | 1226121 | same body as func_8015eab8 |
| 888 | mario_status.c | func_80163fe0 | small | 72 | yes | 100 | 1 | 1226121 | padded overlay struct; plain statements |
| 889 | mario_status.c | func_80164320 | small | 76 | yes | 100 | 1 | 1226121 | unused marioGetPtr call, three returns |
| 890 | mario_status.c | func_8016c648 | small | 76 | yes | 100 | 2 | c3cc7e7 | straight early returns; first build missing prototypes |
| 891 | mario_status.c | func_80157ab4 | small | 80 | yes | 100 | 2 | c3cc7e7 | overlay struct arg with work pointer at 0xc |
| 892 | mario_status.c | func_8016bba4 | small | 80 | yes | 100 | 2 | c3cc7e7 | return !(x > 30.0f) |
| 893 | mario_status.c | func_801576b4 | small | 84 | yes | 100 | 2 | c3cc7e7 | same shape as func_80157ab4 |
| 894 | mario_status.c | func_80166ae0 | small | 84 | yes | 100 | 2 | c3cc7e7 | range check with explicit return 1/0 |
| 895 | mario_status.c | func_801672cc | small | 84 | yes | 100 | 2 | 2a2b76e | straightforward; first build failed on missing prototypes |
| 896 | mario_status.c | func_80164514 | small | 88 | yes | 100 | 2 | 2a2b76e | straightforward; first build failed on missing prototypes |
| 897 | mario_status.c | func_80156660 | small | 92 | yes | 100 | 2 | 2a2b76e | straightforward; first build failed on missing prototypes |
| 898 | mario_status.c | func_80156894 | small | 92 | yes | 100 | 2 | 2a2b76e | straightforward; first build failed on missing prototypes |
| 899 | mario_status.c | func_80156ac8 | small | 92 | yes | 100 | 2 | 2a2b76e | straightforward; first build failed on missing prototypes |
| 900 | mario_status.c | func_80156cfc | small | 92 | yes | 100 | 1 | 6a6f403 | matched first build; status apply / status list lookup |
| 901 | mario_status.c | func_80156f30 | small | 92 | yes | 100 | 1 | 6a6f403 | matched first build; status apply / status list lookup |
| 902 | mario_status.c | func_80158c3c | small | 92 | yes | 100 | 1 | 6a6f403 | matched first build; status apply / status list lookup |
| 903 | mario_status.c | func_80158e70 | small | 92 | yes | 100 | 1 | 6a6f403 | matched first build; status apply / status list lookup |
| 904 | mario_status.c | func_8015ea1c | small | 92 | yes | 100 | 1 | 6a6f403 | matched first build; status apply / status list lookup |
| 905 | mario_status.c | func_80167320 | small | 92 | yes | 100 | 3 | 461391f | 2 shared compile fails (missing prototype, unused param), then matched |
| 906 | mario_status.c | func_80154c88 | small | 96 | yes | 100 | 3 | 461391f | 2 shared compile fails (missing prototype, unused param), then matched |
| 907 | mario_status.c | func_8015715c | small | 96 | yes | 100 | 3 | 461391f | 2 shared compile fails (missing prototype, unused param), then matched |
| 908 | mario_status.c | func_801573c0 | small | 96 | yes | 100 | 3 | 461391f | 2 shared compile fails (missing prototype, unused param), then matched |
| 909 | mario_status.c | func_80157bec | small | 96 | yes | 100 | 3 | 461391f | 2 shared compile fails (missing prototype, unused param); matched with getStatus inline |
| 910 | mario_status.c | func_80157c4c | small | 96 | yes | 100 | 1 | ceddc72 | getStatus(0x200) inline |
| 911 | mario_status.c | func_80157b04 | small | 100 | yes | 100 | 1 | ceddc72 | getStatus(0x100) inline |
| 912 | mario_status.c | func_80166904 | small | 100 | yes | 100 | 1 | ceddc72 | separate range ifs |
| 913 | mario_status.c | func_80166a7c | small | 100 | yes | 100 | 2 | ceddc72 | __fabsf avoids extra frsp |
| 914 | mario_status.c | func_80159070 | small | 100 | functional | 99.00 | 3 | wip/func_80159070 | only r30/r31 swapped between wp and saved id |
| 915 | mario_status.c | func_8015e598 | small | 108 | yes | 100 | 3 | f149fef | two compile errors (prototypes, unused param) then matched |
| 916 | mario_status.c | func_8015bd1c | small | 112 | yes | 100 | 4 | f149fef | static inline status lookup; if (status != NULL) return order |
| 917 | mario_status.c | func_8015eff4 | small | 112 | yes | 100 | 4 | f149fef | static inline status lookup; if (status != NULL) return order |
| 918 | mario_status.c | func_8015fe74 | small | 112 | yes | 100 | 3 | f149fef | two compile errors then matched |
| 919 | mario_status.c | func_80165240 | small | 112 | yes | 100 | 4 | f149fef | negated != chain with early return 0 avoids range merge |
| 920 | mario_status.c | func_8016a794 | small | 112 | yes | 100 | 3 | f961c1a | first compile failed on missing prototypes; branch sense fix |
| 921 | mario_status.c | func_80158814 | small | 116 | yes | 100 | 2 | f961c1a | first compile failed on missing prototype |
| 922 | mario_status.c | func_801589f0 | small | 116 | yes | 100 | 2 | f961c1a | getStatus inline helper |
| 923 | mario_status.c | func_80161b78 | small | 116 | yes | 100 | 2 | f961c1a | prototype for spsndSFX_chkName in header |
| 924 | mario_status.c | func_8015ad8c | small | 124 | yes | 100 | 3 | f961c1a | temp for flags OR before storing field 4 |
| 925 | mario_status.c | func_8015af7c | small | 128 | yes | 100 | 1 | 0ad6482 | inline status lookup helper returning userWork |
| 926 | mario_status.c | func_8016bb24 | small | 128 | yes | 100 | 2 | 0ad6482 | negated or-chain with early return 0 |
