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
| 927 | mario_status.c | func_80157630 | medium | 132 | yes | 100 | 2 | 1f70fd2 | switch with fallthrough 2/8 into 7/9; first attempt failed on missing prototype |
| 928 | mario_status.c | func_80157708 | medium | 132 | yes | 100 | 1 | 70182fc | Status lookup for electrified effect via inline getStatus; matched first try |
| 929 | mario_status.c | func_80157a30 | medium | 132 | yes | 100 | 1 | f887aed | status event handler; copied the switch shape of func_80157630 with HP_REGEN flag |
| 930 | mario_status.c | func_80157b68 | medium | 132 | yes | 100 | 3 | 38826bf | two failed compiles first (offscreendrv.h clashes with local prototype, missing own prototype); then matched using getStatus(0x200) inline helper |
| 931 | mario_status.c | func_8016c774 | medium | 132 | yes | 100 | 2 | 63ac0ca | motionId != chain like func_80165240, miscFlags 0x800000 check; first compile failed for missing prototype |
| 932 | mario_status.c | func_8015ad00 | medium | 140 | yes | 100 | 1 | 3c81751 | pose range assert written as (cond) == false with __assert and rodata base offsets; matched first try |
| 933 | mario_status.c | func_8015ae08 | medium | 140 | yes | 100 | 2 | 63cee56 | inline getWork helper over getStatus(0x4000) plus early return; first compile failed on missing prototype |
| 934 | mario_status.c | func_8016a3bc | medium | 140 | yes | 100 | 4 | 91c9592 | neg/or/srwi test needed a static inline bool helper; register order fixed by declaring fairy before wp |
| 935 | mario_status.c | func_801565d0 | medium | 144 | yes | 100 | 2 | f592d91 | Switch with fallthrough (cases 2,8 delete effect, then 7,9 clear); matched first compiling try (attempt 1 failed to compile: missing prototype) |
| 936 | mario_status.c | func_80156804 | medium | 144 | yes | 100 | 2 | 26697bf | switch like func_801565d0; first build failed only for missing prototype |
| 937 | mario_status.c | func_80156a38 | medium | 144 | yes | 100 | 1 | 722d6a8 | same switch pattern as func_801565d0 with flag 0x4; first try |
| 938 | mario_status.c | func_80156c6c | medium | 144 | yes | 100 | 1 | 1cb2d54 | same switch shape as sibling status command handlers; clears STATUS_NO_JUMP |
| 939 | mario_status.c | func_80156ea0 | medium | 144 | yes | 100 | 1 | 94d6195 | same switch shape as sibling status end funcs (func_801565d0); matched first try |
| 940 | mario_status.c | func_80158648 | medium | 148 | yes | 100 | 3 | 77b0667 | first two builds were header setup (offscreendrv.h conflicts with local prototypes; missing prototype); code matched first compile |
| 941 | mario_status.c | func_8016a448 | medium | 148 | yes | 100 | 4 | f4b0d35 | u16 // chain merged 0x45/0x46 into a range check; fixed with negated && chain and early return 0 (attempts: 1 missing-prototype fail, 1 first try, 1 variants, 1 final score) |
| 942 | mario_status.c | func_801562a8 | medium | 152 | yes | 100 | 2 | adabc74 | motionId or-chain in asm order; first build failed on missing prototype |
| 943 | mario_status.c | func_80158958 | medium | 152 | yes | 100 | 2 | 576b722 | barrier status event check; inline getStatus; attempt 1 was a missing prototype |
| 944 | mario_status.c | func_80158fd4 | medium | 156 | yes | 100 | 2 | 56f88bb | first try failed only on missing prototype; same status switch pattern as siblings, with extra case 3 and a func_8007dd50 call |
| 945 | mario_status.c | func_80163f44 | medium | 156 | yes | 100 | 5 | 8d50307 | flag set before the state store, then flag clear, fixed r0/r3 swap; added animPoseGetCurrentAnim prototype; 2 of 5 builds were compile errors |
| 946 | mario_status.c | func_801669e0 | medium | 156 | yes | 100 | 3 | ed754ca | static inline helper for the 2D-camera 120/0.75 base value; uses framebufferWidth and right-left; first compile failed on missing prototype |
| 947 | mario_status.c | func_8015f064 | medium | 160 | yes | 100 | 2 | c20a720 | First compile failed only for a missing prototype; static inline random-index helper with if/return chain gave the branchless last step |
| 948 | mario_status.c | func_8016c568 | medium | 160 | yes | 100 | 3 | dda403b | flag clears on miscFlags/dispFlags; u32 compare with 0xffffffff gives addis/cmplwi |
| 949 | mario_status.c | func_8016d298 | medium | 160 | yes | 100 | 6 | a473d17 | zero Vec3 copy via (f32)(f64); flags read-modify-write must precede the Vec3 declaration; 2 builds lost to variant compile errors |
| 950 | mario_status.c | func_80163ea0 | medium | 164 | yes | 100 | 2 | c813f1d | needed real prototype for func_80144e44 in header; flags &= ~0x10 before the 0x800 test |
| 951 | mario_status.c | func_80158888 | medium | 168 | yes | 100 | 1 | a9c4a00 | local 4-float table copied from rodata via extern const struct; matched first try |
| 952 | mario_status.c | func_8015e4f0 | medium | 168 | yes | 100 | 1 | 8edf171 | status command switch; matched first try |
| 953 | mario_status.c | func_801636d4 | medium | 180 | yes | 100 | 3 | 59005d5 | prototype needed; == 0x14 // == 0x15 (not >=/<=) for inner range check |
| 954 | mario_status.c | func_80158b84 | medium | 184 | yes | 100 | 2 | 8edb86c | switch with fallthrough like sibling flower handlers; first build failed only on missing prototype |
| 955 | mario_status.c | func_80158db8 | medium | 184 | yes | 100 | 1 | 274a81d | Same shape as sibling func_80158b84 (slow flower flag, effect flag 8); matched first try |
| 956 | mario_status.c | func_80160f70 | medium | 184 | yes | 100 | 1 | e2c86c0 | static inline setter for offscreen id keeps li -1 before marioGetPtr; casts for UNKNOWN_FUNCTION callees |
| 957 | mario_status.c | func_80161700 | medium | 184 | yes | 100 | 1 | ce6aff7 | matched first try: static inline bool name check for neg/or/srwi; only diff in object is the float pool label |
| 958 | mario_status.c | func_8015affc | medium | 192 | yes | 100 | 2 | be30e2c | first compile failed for missing prototype; shared inline userWork getter and 0xb8 entry struct matched directly |
| 959 | mario_status.c | func_80157f2c | medium | 196 | yes | 100 | 1 | ccc1698 | switch on command with shared case bodies; matched first try |
| 960 | mario_status.c | func_8015edf8 | medium | 196 | yes | 100 | 1 | d06d98d | inline status lookup helper getGhostFlags reused as work pointer; matched first try |
| 961 | mario_status.c | func_8016bfe8 | medium | 196 | yes | 100 | 3 | 161e246 | statement order of flag clears (misc 0x20, flags 0x80, misc, misc) then block-scoped zero Vec3 copied per member; one failed compile from variant generator |
| 962 | mario_status.c | func_8015b0bc | medium | 200 | yes | 100 | 1 | 20e345a | matched first try with inline getWork8015ae08 and entry pointer loop |
| 963 | mario_status.c | func_80156340 | medium | 204 | yes | 100 | 2 | 953c56e | callee func_80166904 was auto-inlined; fixed with pragma dont_inline |
| 964 | mario_status.c | func_80161cf8 | medium | 204 | yes | 100 | 6 | aa46fda | switch needed explicit 'case 1: case 2: default:' to get the blt/b compare tree; found with variant copies |
| 965 | mario_status.c | func_8016202c | medium | 204 | yes | 100 | 1 | 2a9a839 | matched first try; unused first arg, caught read as s32 |
| 966 | mario_status.c | func_80163dd4 | medium | 204 | yes | 100 | 3 | 040e929 | void* callback param with local cast fixed r30/r31 swap; separate z *= -1.0f fixed fmuls operand order |
| 967 | mario_status.c | func_8015601c | medium | 212 | yes | 100 | 2 | d8693e2 | status list add: loop over statusTbl, link to list, __assert2 with string offsets; attempt 1 failed to compile (missing prototype), attempt 2 matched |
| 968 | mario_status.c | func_801561d4 | medium | 212 | yes | 100 | 2 | 872ce74 | status list removal loop; first build failed only on missing prototype |
| 969 | mario_status.c | func_8015991c | medium | 220 | yes | 100 | 2 | d21063b | matched first compiled build (one earlier failed compile: unused parameters, left unnamed); moved the 0x4000 status work typedefs and getter inline above it |
| 970 | mario_status.c | func_8016d7bc | medium | 220 | yes | 100 | 2 | 726ddc6 | marioChgMotSub needed a function-pointer cast (first compile failed); matched on the first successful compile |
| 971 | mario_status.c | func_8015b184 | medium | 224 | yes | 100 | 3 | e80bd5f | State switch with early returns; default case needed flags clear written before the 0xd4 store |
| 972 | mario_status.c | func_8016c694 | medium | 224 | yes | 100 | 1 | c929883 | matched first try: chained early returns; miscFlags & 0x10002 gives rlwinm+rlwimi |
| 973 | mario_status.c | func_801560f0 | medium | 228 | yes | 100 | 1 | d834e65 | same shape as func_801561d4 (delete-all variant); matched first try |
| 974 | mario_status.c | func_8015ae94 | medium | 232 | yes | 100 | 4 | 9b32f22 | beq+b early exit needed switch (flags & 0x6) with case 0 break; prototype for func_80144de4 added to mario_motion.h; attempt 1 was a compile fail |
| 975 | mario_status.c | func_8016a4dc | medium | 236 | yes | 100 | 1 | a83b858 | Matched first try; timer arg is a Vec2 and the 0x1c4 field is hitObjs1[2] |
| 976 | mario_status.c | func_8015a0f8 | medium | 240 | yes | 100 | 3 | 3991c8b | count cached in local; declare count before i but assign i=0 first; one compile failed on missing prototype |
| 977 | mario_status.c | func_801671a8 | medium | 240 | yes | 100 | 2 | 144e21f | first build failed on missing prototype; matched with static inline fairy check, if-chain on motionId, func_80166c54 returns s32 |
| 978 | mario_status.c | func_8016a804 | medium | 244 | yes | 100 | 4 | 4f3fc52 | register order: separate y = 240 - y statement before storing y (ranked in a variant build) |
| 979 | mario_status.c | func_8015e920 | medium | 252 | yes | 100 | 1 | 6318380 | disp function: ghost visibility flag, projected z clamp then dispEntry; matched first try |
| 980 | mario_status.c | func_80165140 | medium | 256 | yes | 100.00 | 1 | 36ee127 | matched first try: local Vec3 initialisers for scale (1,1,1) and zero rotation, per-field float stores; only pool label differs |
| 981 | mario_status.c | func_80158ecc | medium | 264 | yes | 100 | 3 | 4eacdd7 | straightforward; two failed compiles (missing prototype, unused param name) |
| 982 | mario_status.c | func_8015aaa0 | medium | 264 | yes | 100 | 5 | 3ae5d7f | two flag clears merged into one and: separate compound assignments (&= ~0x30; &= ~0x1; /= 2) kept both rlwinm; load userWork after marioGetPtr |
| 983 | mario_status.c | func_8015a1e8 | medium | 268 | yes | 100 | 1 | 6ec67b4 | matched first build; static inline state setter reproduces the repeated flags&1 test |
| 984 | mario_status.c | func_80161bec | medium | 268 | yes | 100 | 3 | 8678aec | Two zeroed Vec3 locals: declaring the second after storing the first fixed one stw order; gave spsndBGMOff and marioChgMot2 s32 prototypes in headers |
| 985 | mario_status.c | func_8015980c | medium | 272 | functional | 99 | 4 | wip/func_8015980c | only r30/r31 swap between flag and work pointer |
| 986 | mario_status.c | func_80166504 | medium | 276 | yes | 100 | 2 | 69a54ca | mask 0xff6fffff literal and bool inline helper for != NULL |
| 987 | mario_status.c | func_8016cbac | medium | 276 | yes | 100 | 3 | a21c50f | jumptable switch; arg0 holds fairy at +4, mario ptr separate |
| 988 | mario_status.c | func_8015bc00 | medium | 284 | yes | 100 | 3 | master | pool labels only; fixed Vec3 order and s32 cast on marioCheck3d |
| 989 | mario_status.c | func_80158a64 | medium | 288 | yes | 100 | 4 | HEAD | 3-arg signature (middle unused), plain float timer |
| 990 | mario_status.c | func_80158c98 | medium | 288 | yes | 100 | 1 | 221503e | slow flower twin of func_80158a64 |
| 991 | mario_status.c | func_80166b34 | medium | 288 | yes | 100 | 1 | f90938d | needed fn-pointer casts for header decls |
| 992 | mario_status.c | func_8015b878 | medium | 292 | yes | 100 | 1 | 9ca9610 | straightforward; struct overlay, cast for existing callee type |
| 993 | mario_status.c | func_8015c310 | medium | 300 | yes | 100 | 1 | 574dcb8 | QUATSlerp prototype added; straightforward |
| 994 | mario_status.c | func_8015fee4 | medium | 300 | yes | 100 | 5 | 69642ec | per-case block-local Vec3 with initialiser fixed frame |
| 995 | mario_status.c | func_801586dc | medium | 312 | yes | 100 | 2 | 05311b4 | pool labels only; dispFlags/position field names |
| 996 | mario_status.c | func_8015eebc | medium | 312 | yes | 100 | 2 | d78fc45 | stack order fixed by swapping Vec3 decls |
| 997 | mario_status.c | func_801641e4 | medium | 316 | yes | 100 | 3 | cd86d37 | struct overlay; swapped Vec3 local order for stack |
| 998 | mario_status.c | func_801566bc | medium | 328 | yes | 100 | 1 | 9a61710 | pool labels only differ |
| 999 | mario_status.c | func_801568f0 | medium | 328 | yes | 100 | 1 | 604b825 | copy of func_801566bc with effect id 4 and flag 0x4 |
| 1000 | mario_status.c | func_80156b24 | medium | 328 | yes | 100 | 1 | fc65fad | copy of func_801568f0 with effect id 2 and flag 0x8 |
| 1001 | mario_status.c | func_80156d58 | medium | 328 | yes | 100 | 2 | master | clone of func_80156b24 with id 1, flag 0x10 |
| 1002 | mario_status.c | func_8016c7f8 | medium | 332 | yes | 100 | 1 | 5190213 | matched first try |
| 1003 | mario_status.c | func_8015aba8 | medium | 344 | yes | 100 | 2 | b82e137 | state switch with assert; entry flags reset; struct state field typed |
| 1004 | mario_status.c | func_80159c44 | medium | 352 | functional | 99 | 3 | wip/func_80159c44 | only register numbering of dz/dx temps differs |
| 1005 | mario_status.c | func_8016af90 | medium | 356 | functional | 96.08 | 6 | wip/func_8016af90 | register allocation only (wp r30/fairy r31 vs ours r31/r28); decl order did not help |
| 1006 | mario_status.c | func_8016436c | medium | 364 | functional | 99 | 6 | wip/func_8016436c | only one fcmpu operand order after PSVecMag differs; rest matches |
| 1007 | mario_status.c | func_8015801c | medium | 392 | incomplete | 49.9 | 5 | wip/func_8015801c | two-vertex HSV color GX immediate; logic done, register/instruction order differs (separate offset+ptr regs); 2 compile failures |
| 1008 | mario_status.c | func_80162328 | medium | 400 | incomplete | 94 | 6 | wip/func_80162328 | all logic present; only lha/extrwi arg load order differs, not fixable by locals |
| 1009 | mario_status.c | func_80164048 | medium | 412 | yes | 100 | 1 | master | Mislabeled stub; sibling of func_801641e4 with two float limits |
| 1010 | mario_status.c | func_8016a5c8 | medium | 420 | functional | 98 | 6 | wip/func_8016a5c8 | only reg numbering in loop (n/i swapped in 2nd case) and pool label; limit arg of func_8012c188/c0f8 not passed (cast) |
| 1011 | mario_status.c | func_8015d268 | medium | 444 | yes | 100 | 5 | 736422a | needed bool temp, spd/zero locals, f32 decl in fairy.h |
| 1012 | mario_status.c | func_8015640c | medium | 452 | yes | 100 | 3 | a6fad51 | sibling of func_801566bc; double fctiwz needed (s32)work->timer twice |
| 1013 | mario_status.c | func_8015ce30 | medium | 452 | functional | 98 | 7 | wip/func_8015ce30 | only fcmpu operand order on mag != 0 differs; tried literal, local z, !(==), swapped branches |
| 1014 | mario_status.c | func_8016456c | medium | 452 | functional | 98 | 6 | wip/func_8016456c | only register numbering differs (early li r0); inline scale helper + late Vec3 init fixed rest |
| 1015 | mario_status.c | func_801652b0 | medium | 460 | yes | 100 | 1 | 69dcc98 | matched first try; only pool labels differ |
| 1016 | mario_status.c | func_80156f8c | medium | 464 | yes | 100 | 3 | master | two switches on type with case 5 merged into default; unnamed 2nd param |
| 1017 | mario_status.c | func_801571e8 | medium | 472 | yes | 100 | 1 | 9eb28a9 | copy of func_80156f8c pattern, pool labels only |
| 1018 | mario_status.c | func_8015cc50 | medium | 480 | functional | 98 | 6 | wip/func_8015cc50 | only f0/f1 reg numbering + fmr order differ; branch layout fixed via t=t if-chain |
| 1019 | mario_status.c | func_8015744c | medium | 484 | yes | 100 | 2 | 1ef5fa2 | duplicated switch template of func_80156f8c |
| 1020 | mario_status.c | func_80167790 | medium | 504 | yes | 100 | 3 | 5a965ef | overlay structs, Vec3 decl order, state=res |
| 1021 | mario_status.c | func_80167ca0 | medium | 512 | incomplete | 88 | 6 | wip/func_80167ca0 | logic done; MWCC emits add+lfs d(r3) instead of addi base,0x20 + lfsx per case |
| 1022 | mario_status.c | func_8016a198 | medium | 548 | functional | 99 | 6 | wip/func_8016a198 | only r29/r30 swap between catch target and name; flag mask order fixed by grouping flags then miscFlags |
| 1023 | mario_status.c | func_80159a14 | medium | 560 | functional | 98 | 4 | wip/func_80159a14 | only FPR constant numbering differs (reversed order); decl order did not help |
| 1024 | mario_status.c | func_801620f8 | medium | 560 | incomplete | 89.7 | 6 | wip/func_801620f8 | hitcheck arg scheduling (lha order), f32 reg numbering after hit branch, flags mask |
| 1025 | mario_status.c | func_8016b8e0 | medium | 580 | functional | 99 | 6 | wip/func_8016b8e0 | only n/i register swap (r28/r31) and pool label; fairyGetNum order tried |
| 1026 | mario_status.c | func_80157cdc | medium | 592 | functional | 98.55 | 4 | wip/func_80157cdc | switch needed explicit case 3 with default for tree shape; only pool/label diffs |
| 1027 | mario_status.c | func_80161dc4 | medium | 592 | functional | 99.7 | 4 | wip/func_80161dc4 | only r6/r7 swap for li 0 / clrrwi in prologue |
| 1028 | mario_status.c | func_80154ce8 | medium | 596 | incomplete | 80 | 7 | wip/func_80154ce8 | stack layout shifted 0xc, zero-vec address not hoisted to r26, saved gpr 26 vs 25 |
| 1029 | mario_status.c | func_8015b99c | medium | 612 | yes | 100 | 2 | 71ed0d6 | screen-bounds check then reposition; Vec3 locals at function level, -a <= x form |
| 1030 | mario_status.c | func_8016c944 | medium | 616 | incomplete | 88 | 7 | wip/func_8016c944 | motion-id chain merged into range compare by MWCC, operand order of fmuls/fadds, wp+0x8c CSE; attempt cap exceeded by compile errors |
| 1031 | mario_status.c | func_8015cff4 | medium | 628 | yes | 100 | 3 | master | pool-label only; Vec3 decl order + PSVecMag hoisted to local |
| 1032 | mario_status.c | func_8015bd8c | large | 652 | functional | 99 | 8 | wip/func_8015bd8c | Inlined min/clamp helper with early returns and inRange bool inline needed; remaining diff is f0/f1 reg swap on final !=0 compare |
| 1033 | mario_status.c | func_8016547c | large | 672 | functional | 99.94 | 5 | a90a3df | only sdata2 pool labels differ; Vec3 copy after func call, const-first operand order |
| 1034 | mario_status.c | func_8015778c | large | 676 | functional | 99.85 | 5 | wip/func_8015778c | only fp reg numbering (f1/f2) and pool labels differ; 0x100 flag, Vec3 order fixed |
| 1035 | mario_status.c | func_8015eb48 | large | 688 | functional | 99.73 | 9 | master | t Vec3 copy stack slot and fmadds operand order differ; PSMTXInverse prototype added |
| 1036 | mario_status.c | func_80160350 | large | 700 | functional | 98 | 8 | wip/func_80160350 | all logic present; only register numbering (r29/r30 and f29/f30 swaps) and pool labels differ |
| 1037 | mario_status.c | func_80163788 | large | 748 | yes | 100 | 8 | 399ac5b | switch jumptable; separate wp/fairy locals per case and Vec3 decl order fixed regs/stack |
| 1038 | mario_status.c | func_80166618 | large | 748 | incomplete | 95 | 8 | wip/func_80166618 | float reg numbering (const hoist order) and one inverted branch on flag8&1 check unresolved |
| 1039 | mario_status.c | func_8015c018 | large | 760 | functional | 99 | 7 | wip/func_8015c018 | Dead Vec3 stack stores needed f32 L[29] frame array; only fneg/store order after sin differs |
| 1040 | mario_status.c | func_80160048 | large | 776 | incomplete | 85 | 8 | wip/func_80160048 | stack layout (query alignment) fixed via wrapper struct; remaining frame size 0x10 too big and scheduling differ |
| 1041 | mario_status.c | func_8016060c | large | 776 | functional | 98.78 | 6 | wip/func_8016060c | reg numbering/scheduling only; vec3 const copy via local init, decl order fixed stack |
| 1042 | mario_status.c | func_80167988 | large | 792 | yes | 100 | 7 | 6cebcdb | overlay structs; min/max Vec3 decl order, screen-pos local order, inline Vec3 copy in block |
| 1043 | mario_status.c | func_8015e604 | large | 796 | yes | 100 | 7 | 5477c1f | Needed PSMTXQuat prototype; local order trans/tmp/rot/axis; gravity switch 0/1 for branch layout; int flag for range check |
| 1044 | mario_status.c | func_8015da20 | large | 812 | yes | 100 | 5 | 2eb4f1d | goto-shared li 0 for moveMode switch; extern consts; fn ptr cast for func_801be14c |
| 1045 | mario_status.c | func_80164730 | large | 836 | functional | 96 | 8 | wip/func_80164730 950ce2c | all logic present; f-reg numbering of hitHeight temp (f1/f2/f3 order) and extra cmpwi r28 differ; used literal 0.0f to fix f29/f30 swap |
| 1046 | mario_status.c | func_80159da4 | large | 852 | yes | 100 | 6 | 8ddbe77 | Needed Vec3* as 2nd arg of func_8013f020; <= 0 conditions; decl order of state/moved |
| 1047 | mario_status.c | func_80163a74 | large | 864 | functional | 94 | 6 | wip/func_80163a74 | only r30/r31 swap (param vs MarioWork ptr) remains; declaration order and switch did not fix |
| 1048 | mario_status.c | func_8015948c | large | 896 | functional | 99 | 4 | wip/func_8015948c | unrolled loop; one addi r4 scheduled differently, tried loop-increment forms |
| 1049 | mario_status.c | func_801590d4 | large | 952 | yes | 100 | 4 | master | int-to-float pool label only; decl order fixed regs, j++,k++ in for header |
| 1050 | mario_status.c | func_801617b8 | large | 956 | functional | 99.83 | 5 | wip/func_801617b8 c1d4ff5 | only register numbering in final cam y-500 compare differs; switch needed case 99 for binary search, (s32) cast on marioCheck3d |
| 1051 | mario_status.c | func_8016bbf4 | large | 1012 | incomplete | 98.7 | 8 | wip/func_8016bbf4 | only reg numbering, fmadds operand order, 1 duplicated bne/beq branch pair (2 insns) missing; pool labels |
| 1052 | mario_status.c | func_8016737c | large | 1044 | yes | 100 | 4 | ea1db8e | casts for unknown callee protos; local decl order fixed regs and stack floats |
| 1053 | mario_status.c | func_8016d338 | large | 1156 | functional | 99 | 6 | wip/func_8016d338 | only register numbering differs in first block (trigFlags r4/r5, zero r0/r4); 2 compile errors, Vec3 zero declared after PSVECAdd |
| 1054 | mario_status.c | func_801581a4 | large | 1184 | functional | 99.7 | 8 | wip/func_801581a4 | only srwi vs extrwi on GXSetChanCtrl ambsrc arg differs; needed dont_inline on callees, frame local declared first |
| 1055 | mario_status.c | func_8016c0b4 | large | 1204 | functional | 99.9 | 5 | wip/func_8016c0b4 | only r0/r3 swap on dispFlags/prevMotionId temp at start; rest matches |
| 1056 | mario_status.c | func_80167ea0 | large | 1240 | yes | 100 | 4 | master | fairy follow; prototype needed, mv vec store order fixed regs |
| 1057 | mario_status.c | func_80166c54 | large | 1364 | functional | 99 | 8 | wip/func_80166c54 | only 3 lfs load-order swaps (f14/f18 pair); needed opt_common_subs off to avoid npc+0x2a0 CSE |
| 1058 | mario_status.c | func_8016ccec | large | 1452 | functional | 99 | 5 | wip/func_8016ccec | opt_common_subs off needed to stop CSE of &wp->0x8c; only r4/r5 and r0/r3 numbering differ |
| 1059 | mario_status.c | func_8015d424 | large | 1532 | functional | 99.74 | 9 | wip/func_8015d424 | sibling of func_8015da20; stack Vec3 and float local order fixed; left with one fadds/fsubs register swap near hi/lo center calc; used 9 builds (cap 8 exceeded by one on a compile error) |
| 1060 | mario_status.c | func_8015b264 | large | 1556 | incomplete | 90 | 8 | wip/func_8015b264 | all logic done, regs match; switch(idx) compiles with different compare-tree/case order, ~213 diff lines |
| 1061 | mario_status.c | func_80160944 | large | 1580 | incomplete | 0 | 8 | wip/func_80160944 | All logic written (switch state machine); MWCC folds &wp->jumpFallPara instead of keeping r31, fewer saved f-regs than original; diff not measured exactly |
| 1062 | mario_status.c | func_8016a8f8 | large | 1688 | functional | 98 | 7 | wip/func_8016a8f8 | All logic present; only FPR numbering and scheduling of frame float loads differ. Needed dont_inline on func_8016a804, case 20 fallthrough, overlay structs |
| 1063 | mario_status.c | func_80164a74 | large | 1740 | incomplete | 85 | 8 | wip/func_80164a74 | frame 0x10 too big, Vec3 local stack order and f30/f31 numbering not matched; ~175 differing lines |
| 1064 | mario_status.c | func_80161028 | large | 1752 | functional | 99.98 | 8 | wip/func_80161028 | switch state machine with fallthrough cases; hoisted Vec3/int locals fixed frame; only fnmsubs operand order differs |
| 1065 | mario_status.c | func_8015dd4c | large | 1956 | yes | 100 | 4 | 3f21d93 | ghost shroom status main; fmadds operand order fixed via split temp; pool label only |
| 1066 | mario_status.c | func_8015a2f4 | large | 1964 | incomplete | 86.26 | 8 | wip/func_8015a2f4 9c78f18 | 4 of 8 builds lost to compile errors; reg allocation and 0.0 const handling differ; Vec3 brace init + by-value ray helper fixed frame size |
| 1067 | mario_status.c | func_8016b0f4 | large | 2028 | functional | 98.2 | 8 | wip/func_8016b0f4 | switch state machine; fixed inlining of func_8016a804 via dont_inline; left: float load/reg numbering in frame calc, store order |
| 1068 | npcdrv.c | npcMain | huge | 4972 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1069 | npcdrv.c | npcHitMain | huge | 8628 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1070 | npcdrv.c | func_801ad058 | huge | 3404 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1071 | npcdrv.c | npcDispMain | huge | 4128 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1072 | npcdrv.c | func_801af4fc | huge | 2560 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1073 | npcdrv.c | func_801b0480 | huge | 2192 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1074 | npcdrv.c | func_801b0ed4 | huge | 2832 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1075 | npcdrv.c | func_801b2928 | huge | 2680 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1076 | npcdrv.c | mtx_setup | huge | 3172 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1077 | npcdrv.c | func_801b4514 | huge | 2744 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1078 | npcdrv.c | npcHitboxDisp | huge | 2876 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1079 | npcdrv.c | npcEntry | huge | 2740 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1080 | npcdrv.c | func_801b84d4 | huge | 7248 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1081 | npcdrv.c | func_801ba124 | huge | 5592 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1082 | npcdrv.c | func_801bba3c | huge | 2964 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1083 | npcdrv.c | func_801c25d8 | huge | 2680 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1084 | npcdrv.c | func_801c3d94 | huge | 2064 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1085 | npcdrv.c | func_801c5140 | huge | 5288 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1086 | npcdrv.c | func_801c65e8 | huge | 6528 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1087 | npcdrv.c | func_801c8d70 | huge | 2724 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1088 | npcdrv.c | func_801cb754 | huge | 2096 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1089 | npcdrv.c | func_801cdb84 | huge | 3972 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1090 | npcdrv.c | func_801cf16c | huge | 4364 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1091 | npcdrv.c | func_801d0640 | huge | 2584 | deferred | - | 0 | - | huge (over 2,044 B): stub left |
| 1092 | npcdrv.c | func_801c0454 | tiny | 8 | yes | 100 | 3 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1093 | npcdrv.c | func_801c213c | tiny | 12 | yes | 100 | 3 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1094 | npcdrv.c | func_801c3bb8 | tiny | 12 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1095 | npcdrv.c | func_801c85e4 | tiny | 8 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1096 | npcdrv.c | func_801c8d48 | tiny | 12 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1097 | npcdrv.c | func_801cccdc | tiny | 4 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1098 | npcdrv.c | func_801cd82c | tiny | 8 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1099 | npcdrv.c | func_801d23cc | tiny | 8 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1100 | npcdrv.c | func_801d23d4 | tiny | 8 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1101 | npcdrv.c | npcGetWorkPtr | tiny | 8 | yes | 100 | 2 | bda0aa9 | batch edited together (finish.py committed all 10 at once, measured 100% each); one wasted build each before first compile |
| 1102 | npcdrv.c | func_801c35fc | tiny | 16 | yes | 100 | 1 | fb11c9c | x |
| 1103 | npcdrv.c | func_801c38a4 | tiny | 16 | yes | 100 | 1 | dbf310f | header proto |
| 1104 | npcdrv.c | func_801c38b4 | tiny | 16 | yes | 100 | 1 | 5ec94ad | x |
| 1105 | npcdrv.c | func_801ca198 | tiny | 12 | incomplete | - | 1 | wip/func_801ca198 d66d467 | trivial |
| 1106 | npcdrv.c | func_801cab20 | tiny | 12 | yes | 100 | 2 | 84adfa5 | header proto must match |
| 1107 | npcdrv.c | func_801cb268 | tiny | 12 | yes | 100 | 2 | 3778c17 | needs msl/string.h |
| 1108 | npcdrv.c | func_801d1058 | tiny | 12 | yes | 100 | 1 | bdbcce7 | x |
| 1109 | npcdrv.c | npcGetEntries | tiny | 12 | yes | 100 | 1 | f96f1ca | x |
| 1110 | npcdrv.c | npcGetMaxEntries | tiny | 12 | yes | 100 | 1 | b42e85b | x |
| 1111 | npcdrv.c | npcGetNextTemplateNpcId | tiny | 12 | yes | 100 | 1 | aac5e98 | wp label |
| 1112 | npcdrv.c | func_801c38c4 | tiny | 16 | yes | 100 | 2 | ad66a9f | header type needed |
| 1113 | npcdrv.c | func_801c3a74 | tiny | 16 | yes | 100 | 1 | e7da43d | trivial |
| 1114 | npcdrv.c | func_801c3ba8 | tiny | 16 | yes | 100 | 1 | 746c434 | trivial |
| 1115 | npcdrv.c | func_801c7fe0 | tiny | 16 | yes | 100 | 1 | 35027a9 | trivial |
| 1116 | npcdrv.c | func_801c7ff0 | tiny | 16 | yes | 100 | 1 | c5211e6 | trivial |
| 1117 | npcdrv.c | func_801ca300 | tiny | 16 | yes | 100 | 1 | fbfbc90 | trivial |
| 1118 | npcdrv.c | func_801d029c | tiny | 16 | yes | 100 | 1 | 6d75271 | trivial |
| 1119 | npcdrv.c | func_801d1064 | tiny | 16 | yes | 100 | 1 | 38faa79 | trivial |
| 1120 | npcdrv.c | func_801d1074 | tiny | 16 | yes | 100 | 1 | b99a036 | trivial |
| 1121 | npcdrv.c | func_801d1084 | tiny | 16 | yes | 100 | 1 | 46e4685 | trivial |
| 1122 | npcdrv.c | func_801c01a8 | tiny | 24 | yes | 100 | 1 | be22695 |  |
| 1123 | npcdrv.c | func_801c3b6c | tiny | 20 | yes | 100 | 2 | 311bdaf | header proto needed |
| 1124 | npcdrv.c | func_801c3b80 | tiny | 20 | yes | 100 | 1 | 1aaefc3 |  |
| 1125 | npcdrv.c | func_801c3b94 | tiny | 20 | yes | 100 | 1 | 64f6b1a |  |
| 1126 | npcdrv.c | func_801cab08 | tiny | 24 | yes | 100 | 1 | c9fa093 |  |
| 1127 | npcdrv.c | func_801d0610 | tiny | 20 | yes | 100 | 1 | ebbc1e6 |  |
| 1128 | npcdrv.c | func_801d1094 | tiny | 16 | yes | 100 | 1 | 56467de | trivial |
| 1129 | npcdrv.c | npcFlag2On | tiny | 20 | yes | 100 | 1 | b3eb05a |  |
| 1130 | npcdrv.c | npcGetTribe | tiny | 20 | yes | 100 | 1 | 206fa5d |  |
| 1131 | npcdrv.c | npcSetAnim | tiny | 20 | incomplete | 76.00 | 4 | wip/npcSetAnim 1d70030 | extra mr r0 shuffle |
| 1132 | npcdrv.c | func_801c018c | tiny | 28 | incomplete | - | 1 | wip/func_801c018c ff41d6a | easy |
| 1133 | npcdrv.c | func_801c01c0 | tiny | 28 | incomplete | - | 1 | wip/func_801c01c0 7948787 | easy |
| 1134 | npcdrv.c | func_801c8b7c | tiny | 28 | yes | 100 | 1 | 97ff7f7 | pool label only |
| 1135 | npcdrv.c | func_801c8d54 | tiny | 28 | incomplete | 70.43 | 4 | wip/func_801c8d54 2d8596d | reg swap |
| 1136 | npcdrv.c | func_801cbf84 | tiny | 24 | yes | 100 | 1 | cc8f558 | easy |
| 1137 | npcdrv.c | func_801cc134 | tiny | 28 | yes | 100 | 1 | 2aedf14 | easy |
| 1138 | npcdrv.c | func_801d0624 | tiny | 28 | yes | 100 | 1 | fc71376 | easy |
| 1139 | npcdrv.c | npcDisp | tiny | 28 | incomplete | 34.29 | 4 | wip/npcDisp 3b3118f | arg scheduling |
| 1140 | npcdrv.c | npcDisp_xlu | tiny | 28 | incomplete | 34.29 | 1 | wip/npcDisp_xlu 601b425 | same mr r9 scheduling as npcDisp |
| 1141 | npcdrv.c | npcGetKillXp | tiny | 28 | yes | 100 | 1 | e807f6c | easy |
| 1142 | npcdrv.c | func_801ca2d8 | tiny | 40 | yes | 100 | 1 | f8723da | ok |
| 1143 | npcdrv.c | func_801ca3b8 | tiny | 40 | yes | 100 | 1 | 7a98367 | ok |
| 1144 | npcdrv.c | func_801ca748 | tiny | 32 | yes | 100 | 2 | d5f4849 | pool label only |
| 1145 | npcdrv.c | func_801ccb40 | tiny | 40 | yes | 100 | 4 | 53e6cb3 | cap used by header/sed mistakes |
| 1146 | npcdrv.c | func_801ccf4c | tiny | 40 | yes | 100 | 1 | ce11af8 | ok |
| 1147 | npcdrv.c | func_801cd394 | tiny | 40 | yes | 100 | 1 | e8357b9 | ok |
| 1148 | npcdrv.c | func_801cd3bc | tiny | 32 | yes | 100 | 2 | 97f3ecf | store order |
| 1149 | npcdrv.c | func_801d0278 | tiny | 36 | yes | 100 | 1 | 0889077 | ok |
| 1150 | npcdrv.c | npcPartDisp | tiny | 32 | yes | 100 | 2 | a35c300 | tail call via cast |
| 1151 | npcdrv.c | npcPartDisp_xlu | tiny | 32 | yes | 100 | 1 | ad0a8a9 | same |
| 1152 | npcdrv.c | func_801bfc14 | tiny | 52 | yes | 100 | 1 | 79f4fd6 | easy |
| 1153 | npcdrv.c | func_801c3930 | tiny | 56 | yes | 100 | 2 | 2636070 | inlined npcGetPartById; u32 id |
| 1154 | npcdrv.c | func_801c8b44 | tiny | 56 | yes | 100 | 3 | f8ffe3d | separate ifs; also corrected npcFinishFlipInstant const to 270.0f |
| 1155 | npcdrv.c | func_801cc0a0 | tiny | 44 | yes | 100 | 1 | 1457612 | easy |
| 1156 | npcdrv.c | func_801cd3dc | tiny | 40 | yes | 100 | 2 | 5eb77c8 | pool label only |
| 1157 | npcdrv.c | func_801cd804 | tiny | 40 | yes | 100 | 1 | c27b021 | same as 3dc |
| 1158 | npcdrv.c | func_801d10a4 | tiny | 40 | yes | 100 | 2 | cd05ba2 | symbol names only |
| 1159 | npcdrv.c | func_801d2304 | tiny | 56 | yes | 100 | 1 | 554a76d | easy |
| 1160 | npcdrv.c | npcFinishFlipInstant | tiny | 44 | yes | 100 | 1 | a679c46 | 1.0f guess |
| 1161 | npcdrv.c | npcGetPartById | tiny | 40 | yes | 100 | 2 | 827e1fb | s32 cast for cmpw |
| 1162 | npcdrv.c | func_801bf5cc | tiny | 64 | yes | 100 | 1 | 167c3eb | label-only diff |
| 1163 | npcdrv.c | func_801d25b8 | tiny | 60 | incomplete | 92.67 | 4 | wip/func_801d25b8 3a80850 | branch layout (beq/b) not reproduced |
| 1164 | npcdrv.c | npcSearchAnimDefs | tiny | 60 | yes | 100 | 1 | 009ea23 | straightforward |
| 1165 | npcdrv.c | func_801be14c | small | 76 | yes | 100 | 4 | 1adce6d | mask 0x80000 |
| 1166 | npcdrv.c | func_801ca150 | small | 72 | yes | 100 | 1 | 632b7c9 | same as npcIdToPtr |
| 1167 | npcdrv.c | func_801d2384 | small | 72 | yes | 100 | 1 | f56f65e | ok |
| 1168 | npcdrv.c | npcFreezeAll | small | 72 | yes | 100 | 1 | c166916 | ok |
| 1169 | npcdrv.c | npcIdToPtr | small | 72 | yes | 100 | 1 | 17b24f2 | simple loop |
| 1170 | npcdrv.c | func_801b3860 | small | 80 | yes | 100 | 4 | 468fc26 | 3rd-arg signature |
| 1171 | npcdrv.c | func_801c2480 | small | 76 | functionally complete | 98.16 | 3 | wip/func_801c2480 1b32fdb | only reg numbering r4/r5 swap |
| 1172 | npcdrv.c | func_801caab4 | small | 84 | yes | 100 | 4 | e4196b9 | u32 id compare |
| 1173 | npcdrv.c | func_801cbf9c | small | 76 | yes | 100 | 2 | 3404c74 | header sig, setupFileIndex |
| 1174 | npcdrv.c | func_801cc0cc | small | 76 | incomplete | 87.58 | 3 | wip/func_801cc0cc a90e05d | string pool offsets; assert 0 / おかしい |
| 1175 | npcdrv.c | func_801a96a4 | small | 88 | incomplete | 81.36 | 4 | wip/func_801a96a4 f3e22c1 | x<10 signed idiom found; branch layout of bool ternary not matched |
| 1176 | npcdrv.c | func_801b2460 | small | 96 | incomplete | 99.38 | 1 | wip/func_801b2460 9a3baac | switch |
| 1177 | npcdrv.c | func_801c3848 | small | 92 | yes | 100 | 2 | b7235ec | i declared before npc |
| 1178 | npcdrv.c | func_801c38d4 | small | 92 | yes | 100 | 1 | 40c7b46 | straightforward |
| 1179 | npcdrv.c | func_801d1b9c | small | 88 | yes | 100 | 1 | 0cfa7aa | easy |
| 1180 | npcdrv.c | func_801c37e4 | small | 100 | yes | 100 | 2 | 4de1252 | u32 read of flags |
| 1181 | npcdrv.c | func_801ca3e0 | small | 104 | yes | 100 | 2 | 6a14637 | decl order |
| 1182 | npcdrv.c | func_801d2554 | small | 100 | yes | 100 | 1 | 966edd3 | simple |
| 1183 | npcdrv.c | npcCheckFlipFinished | small | 96 | yes | 100 | 1 | b810bac | simple |
| 1184 | npcdrv.c | npcSfxOn | small | 100 | yes | 100 | 1 | 79f03dc | header ret s32 |
| 1185 | npcdrv.c | func_801bf554 | small | 120 | yes | 100 | 2 | 4c08077 | easy; header signature fixed |
| 1186 | npcdrv.c | func_801c7f68 | small | 120 | yes | 100 | 1 | 6ac2a90 | easy; header signature fixed |
| 1187 | npcdrv.c | func_801c9874 | small | 124 | yes | 100 | 1 | 092fa94 | easy |
| 1188 | npcdrv.c | func_801c99b0 | small | 116 | incomplete | - | 4 | wip/func_801c99b0 fc58a1e | branch layout (bne;b) and fabs reg not matched; tried nested/do-while/goto |
| 1189 | npcdrv.c | npcGetDefense | small | 120 | incomplete | 31.07 | 4 | wip/npcGetDefense 4fcc8f1 | assert2 tail call b vs bl, frame saved regs; needs else-structure |
| 1190 | npcdrv.c | func_801c2558 | small | 128 | functionally complete | 99.22 | 4 | wip/func_801c2558 1d6bc1e | register numbering only; locals x,y,z |
| 1191 | npcdrv.c | func_801c360c | medium | 136 | incomplete | 95.97 | 2 | wip/func_801c360c 4e7450d | assert string pool base reg only differs |
| 1192 | npcdrv.c | func_801bcc00 | medium | 140 | yes | 100 | 2 | 08baaa0 | simple; header prototype typed |
| 1193 | npcdrv.c | func_801c24cc | medium | 140 | yes | 100 | 1 | 41f1018 | straightforward part list loop |
| 1194 | npcdrv.c | func_801c3694 | medium | 140 | functionally complete | 99.14 | 5 | wip/func_801c3694 172d71c | inline find-by-name helper fixed structure; reg numbering only left |
| 1195 | npcdrv.c | npcGetScript | medium | 140 | yes | 100 | 2 | 9a5876c | switch case order matters; jumptable label only diff |
| 1196 | npcdrv.c | func_801bd7dc | medium | 144 | yes | 100 | 2 | c959742 | casts for fields beyond header; header prototype changed |
| 1197 | npcdrv.c | npcNameToPtr_NoAssert | medium | 144 | yes | 100 | 3 | 8c53462 | load order fixed via decl order; only sda label differs |
| 1198 | npcdrv.c | func_801c98f0 | medium | 148 | yes | 100 | 1 | 48fa751 | matched first try, pool labels only |
| 1199 | npcdrv.c | func_801ca1a4 | medium | 148 | yes | 100 | 1 | c216090 | matched first try; part anim at +0x54 via cast |
| 1200 | npcdrv.c | npcAreOnSpawnEvtsDone | medium | 148 | yes | 100 | 1 | ebeca6e | matched first try |
| 1201 | npcdrv.c | func_801bf60c | medium | 152 | yes | 100 | 1 | 6128852 | easy; 0.5/1.0 clamps |
| 1202 | npcdrv.c | npcDisp_offscreen | medium | 156 | yes | 100 | 3 | 4b66aa7 | needed header prototype, raw offsets |
| 1203 | npcdrv.c | npcDisp_offscreen_xlu | medium | 156 | yes | 100 | 1 | f6f06e4 | copy of npcDisp_offscreen with flag 1 |
| 1204 | npcdrv.c | func_801ca238 | medium | 160 | yes | 100 | 1 | 20966e3 | mirror of func_801ca1a4 with poseId checks, clear flag |
| 1205 | npcdrv.c | func_801c9a24 | medium | 164 | incomplete | 85.00 | 6 | wip/func_801c9a24 deeea99 | early-return structure and fabs/frsp regalloc differ |
| 1206 | npcdrv.c | npcDisp_general | medium | 164 | incomplete | 89.76 | 6 | wip/npcDisp_general 85e1669 | only r30/r31 swap (pose vs npc) remained; header changed to real prototype |
| 1207 | npcdrv.c | npcPartDisp_general | medium | 164 | yes | 100 | 3 | da7070f | needed owner loaded before pose local; header signature changed |
| 1208 | npcdrv.c | func_801c01dc | medium | 168 | yes | 100 | 3 | 45e8b79 | header changed to bool(npc,part,flags); only pool labels differ |
| 1209 | npcdrv.c | func_801c23b0 | medium | 168 | yes | 100 | 6 | cfb0af8 | inlined npcGetPartById plus extra parts==0 early return |
| 1210 | npcdrv.c | func_801ca310 | medium | 168 | incomplete | 64.14 | 6 | wip/func_801ca310 518fe45 | float mul and reg numbering hard; no exact match |
| 1211 | npcdrv.c | npcNameToPtr | medium | 168 | incomplete | 94.00 | 6 | wip/npcNameToPtr 81eaf82 | num/wp register swap and string pool offsets remain |
| 1212 | npcdrv.c | npcReset | medium | 172 | yes | 100 | 1 | c2b45cf | label-only diffs; float assumed 0.0 |
| 1213 | npcdrv.c | npcUpdateSetupFile | medium | 176 | incomplete | 97.50 | 6 | wip/npcUpdateSetupFile c927965 | table copy inside loop matched; branch layout of pre-check ==6 not reproduced |
| 1214 | npcdrv.c | func_801b24c0 | medium | 180 | yes | 100 | 4 | f94bd1e | float pool label only; result var with 0 init fixed branches |
| 1215 | npcdrv.c | func_801cbfe8 | medium | 184 | yes | 100 | 1 | 54fffcc | pool labels only; casts on raw offsets |
| 1216 | npcdrv.c | func_801d23dc | medium | 188 | yes | 100 | 2 | e12b29f | return type void (header changed for 4 fns); raw offsets |
| 1217 | npcdrv.c | func_801d2498 | medium | 188 | yes | 100 | 1 | e4374e5 | copy of func_801d23dc with func_80043ca4 |
| 1218 | npcdrv.c | npcInit | medium | 188 | yes | 100 | 1 | ab5f928 | straightforward |
| 1219 | npcdrv.c | func_801aabe4 | medium | 192 | incomplete | 97.92 | 5 | wip/func_801aabe4 e3794d7 | only redundant bne after beq differs; tried else-if, switch |
| 1220 | npcdrv.c | func_801aef10 | medium | 192 | yes | 100 | 4 | 083ae99 | needed NPC overlay struct with name field so strcmp arg is not hoisted |
| 1221 | npcdrv.c | func_801c3720 | medium | 196 | incomplete | 94.96 | 4 | wip/func_801c3720 6cf1a18 | regs fixed by decl order; only bne+b branch shape and string pool differ |
| 1222 | npcdrv.c | func_801b2574 | medium | 204 | yes | 100 | 3 | fcb597a | calls func_801b24c0 (inlined) then func_801b20dc; header sig changed |
| 1223 | npcdrv.c | func_801b285c | medium | 204 | yes | 100 | 2 | deefd35 | inlined func_801b24c0 body; header sig changed |
| 1224 | npcdrv.c | func_801c0284 | medium | 204 | incomplete | 83.41 | 6 | wip/func_801c0284 6278f35 | register alloc: part in r3 vs r8, string pool offsets; assert tail-calls needed else-less returns |
| 1225 | npcdrv.c | func_801cf0a0 | medium | 204 | yes | 100 | 5 | 62a03d7 | needed inline helper with explicit r=0/1 branches |
| 1226 | npcdrv.c | func_801b4fcc | medium | 212 | functionally complete | 99.43 | 3 | wip/func_801b4fcc 84ee4b1 | register numbering only; int copy of Vec3, pose-relative offsets |
| 1227 | npcdrv.c | func_801bd4ac | medium | 216 | yes | 100 | 2 | ddad12a | only float pool label differs |
| 1228 | npcdrv.c | func_801c8000 | medium | 216 | functionally complete | 98.80 | 3 | wip/func_801c8000 dc5e762 | register numbering only; a1 unnamed param |
| 1229 | npcdrv.c | func_801c3cb4 | medium | 224 | yes | 100 | 3 | 16b62ef | id at +4 raw s32, init order of locals |
| 1230 | npcdrv.c | npcSetStayPose | medium | 228 | yes | 100 | 1 | 848c70f | inlined npcNameToPtr_NoAssert, first try |
| 1231 | npcdrv.c | npcSetTalkPose | medium | 228 | yes | 100 | 2 | e3fdf79 | twin of npcSetStayPose with pose 3; header decl added |
| 1232 | npcdrv.c | func_801c3a84 | medium | 232 | incomplete | 97.64 | 3 | wip/func_801c3a84 2ad19be | assert2 with 3 strings; local order for f2/f3; only pool diffs |
| 1233 | npcdrv.c | func_801cd124 | medium | 236 | incomplete | 79.19 | 6 | wip/func_801cd124 8ba0695 | scheduling/reg alloc of 0.35 const and old value differ; header changed to NPCEntry* sig |
| 1234 | npcdrv.c | func_801cd5e8 | medium | 236 | incomplete | 96.86 | 3 | wip/func_801cd5e8 4fddd86 | only register numbering diffs; header changed to real prototype |
| 1235 | npcdrv.c | func_801c3bc4 | medium | 240 | incomplete | 94.25 | 6 | wip/func_801c3bc4 a4c166d | npc+0x5c arg hoisted by MWCC, extra reg |
| 1236 | npcdrv.c | npcSetAnimSub | medium | 248 | yes | 100 | 3 | f0d9240 | locals order result,part,mask,p |
| 1237 | npcdrv.c | func_801aada8 | medium | 252 | incomplete | 97.62 | 6 | wip/func_801aada8 8224840 | gravity branch layout and float compare order not matched |
| 1238 | npcdrv.c | func_801b5118 | medium | 252 | yes | 100 | 3 | a0962bf | pool labels only; header prototype changed |
| 1239 | npcdrv.c | func_801be6cc | medium | 252 | yes | 100 | 3 | 009559c | only symbol-name diff |
| 1240 | npcdrv.c | func_801bf6a4 | medium | 252 | functionally complete | 99.44 | 3 | wip/func_801bf6a4 0f794d9 | register numbering only (i vs name regs swapped); changed header sig |
| 1241 | npcdrv.c | func_801d2208 | medium | 252 | yes | 100 | 3 | b96a519 | return type s32 in header; cast call to void(*)(args) |
| 1242 | npcdrv.c | func_801aaca4 | medium | 260 | yes | 100 | 2 | 31be7db | needed 3-level manual unroll of recursion |
| 1243 | npcdrv.c | func_801c3968 | medium | 268 | incomplete | 97.96 | 6 | wip/func_801c3968 bd3ab44 | inline part lookup helper with return; string pool offsets only |
| 1244 | npcdrv.c | func_801cc8d0 | medium | 268 | yes | 100 | 3 | 366872a | pool-only diffs; header proto changed to take NPCEntry* |
| 1245 | npcdrv.c | func_801afefc | medium | 272 | incomplete | 96.60 | 4 | wip/func_801afefc cec00bf | gave up at 4/6: only string-pool addressing differs (r30 base vs r3 offset in assert call) |
| 1246 | npcdrv.c | func_801b0154 | medium | 272 | yes | 100 | 3 | d15ee84 | only sda label name differs |
| 1247 | npcdrv.c | func_801cd834 | medium | 296 | yes | 100 | 3 | ad2334d | pool labels only |
| 1248 | npcdrv.c | func_801ccce0 | medium | 304 | incomplete | 81.50 | 5 | wip/func_801ccce0 4057d0b | gave up at 5/6: frame too large, Vec3 locals/stack layout not matched |
| 1249 | npcdrv.c | func_801cd6d4 | medium | 304 | incomplete | 96.11 | 6 | wip/func_801cd6d4 7ce0660 | dead Vec3 stack stores, frame size and reg order unmatched |
