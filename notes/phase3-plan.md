# Phase 3 plan: the rest of the game code in main.dol (EU0)

Counted 2026-11-13 from `config/EU0/splits.txt`, `symbols.txt`, `configure.py` and the `src/` stubs (read-only, nothing built).
Method as in `remaining-work.md`: a `NonStarted` file counts all its functions; a `NonMatching` file counts the functions
still marked `// NOT_DECOMPILED`; `Matching` files count 0. Bytes are summed from `symbols.txt`.
Phase 3 = every split game-code file of `main.dol` that phase 2 and Antigravity do not cover. Areas follow the port's need
(Mario first, then NPCs, scripts, items, HUD, map, boot, rendering, minigames). Within an area: `NonMatching` files first
(stubs exist), then `NonStarted`, each smallest total bytes first.

**Total remaining in this plan: 116 files, 3,086 functions, 1,344,028 bytes.**

## Exclusions

| What | Why |
|---|---|
| `camdrv.c`, `mapdrv.c` | phase 2 (`hitdrv.c` is already Matching) |
| `evt_pouch.c`, `evt_fairy.c`, `evt_map.c` | in `spm-decomp-ag/notes/ag-queue.md` (Antigravity) |
| `animdrv.c` (76 fns, 51,984 B, NonStarted) | upstream WIP branch `upstream/animdrv-test` adds `src/animdrv.c` |
| `system.c` (1 fn, 1,456 B) | `upstream/clang-format` edits `src/system.c`; leave until that is resolved |
| `upstream/wpadmgr` | no diff against master, so `wpadmgr.c` is kept in the plan |
| Already `Matching` files (14, e.g. `evtmgr.c`, `evtmgr_cmd.c`, `filemgr.c`, `seqdrv.c`, `hitdrv.c`) | done |
| Libraries: `Runtime.PPCEABI.H/*`, `DEMOInit.c`, the `main.dol` tail after `0x80256728` (OS, GX, VI, MEM, Bluetooth, USB, MSL), `.init` | library code; on the 3DS it is replaced by 3DS system calls, not decompiled |
| Unsplit `main.dol` gaps (1,967 fns) and unsplit `relF` (1,006 fns; only `dan.c` is split) | no splits yet, so no source files; relF holds the per-chapter enemy and map code, so it needs a split-first step later (not sensible to start blind) |

Known reusable branches on `origin`: see the notes column (`wip/hudMain`, `wip/itemEntry`, `wip/npcDelete`, `wip/parseGet1Next`).
`NonStarted` files need their stub source created first: a `src/<name>.c` with every function as `// NOT_DECOMPILED <name>`
stubs (as the other stubs look) and the `Object(...)` line in `configure.py` switched from `NonStarted` to `NonMatching`.
Check also each file's header under `spm-headers/include/spm/`.
"Huge" means over 2,044 bytes; do those last in each file.

## Table

| # | file | status | functions | bytes | why needed (area) | notes |
|---|---|---|---|---|---|---|
| | **Area 1 Mario and companions**: Mario control, motion, hit and status; Tippi and Pixl companions | | | | | |
| 1 | `guide.c` | NonMatching | 26 | 8,720 | Mario and companions | huge fn `runMode2Main` 2,300 B |
| 2 | `fairy.c` | NonMatching | 42 | 14,252 | Mario and companions | huge fn `func_8011bc08` 2,256 B |
| 3 | `evt_mario.c` | NonMatching | 105 | 16,760 | Mario and companions | largest `func_800f119c` 1,256 B |
| 4 | `mario.c` | NonMatching | 141 | 47,516 | Mario and companions | huge fn `marioMain` 5,292 B |
| 5 | `mot_hit.c` | NonStarted | 2 | 924 | Mario and companions | create stub source + `configure.py` entry check first |
| 6 | `mot_peach_float.c` | NonStarted | 4 | 1,340 | Mario and companions | create stub source + `configure.py` entry check first |
| 7 | `mot_spring.c` | NonStarted | 4 | 1,740 | Mario and companions | largest `func_8011a92c` 1,200 B; create stub source + `configure.py` entry check first |
| 8 | `mario_fairy.c` | NonStarted | 15 | 2,616 | Mario and companions | create stub source + `configure.py` entry check first |
| 9 | `mot_stay.c` | NonStarted | 4 | 2,832 | Mario and companions | huge fn `func_80111fe8` 2,488 B; create stub source + `configure.py` entry check first |
| 10 | `mot_walk.c` | NonStarted | 7 | 3,128 | Mario and companions | largest `func_80119040` 1,348 B; create stub source + `configure.py` entry check first |
| 11 | `mot_crouch.c` | NonStarted | 6 | 3,316 | Mario and companions | largest `func_80119d6c` 1,424 B; create stub source + `configure.py` entry check first |
| 12 | `mot_ladder.c` | NonStarted | 5 | 3,464 | Mario and companions | largest `func_8011b67c` 1,420 B; create stub source + `configure.py` entry check first |
| 13 | `evt_guide.c` | NonStarted | 24 | 3,944 | Mario and companions | create stub source + `configure.py` entry check first |
| 14 | `mot_mega_star.c` | NonStarted | 5 | 4,456 | Mario and companions | huge fn `func_80117fec` 2,944 B; create stub source + `configure.py` entry check first |
| 15 | `mot_jabara.c` | NonStarted | 6 | 7,816 | Mario and companions | huge fn `func_80171f34` 6,400 B; create stub source + `configure.py` entry check first |
| 16 | `mot_jump.c` | NonStarted | 16 | 7,988 | Mario and companions | huge fn `func_80173d30` 2,628 B; create stub source + `configure.py` entry check first |
| 17 | `mot_slit.c` | NonStarted | 23 | 9,552 | Mario and companions | huge fn `func_80177330` 5,484 B; create stub source + `configure.py` entry check first |
| 18 | `mario_acrobat.c` | NonStarted | 19 | 12,172 | Mario and companions | huge fn `func_8012e3c0` 4,096 B; create stub source + `configure.py` entry check first |
| 19 | `mot_fairy_other.c` | NonStarted | 23 | 17,784 | Mario and companions | huge fn `func_8016ece4` 5,004 B; create stub source + `configure.py` entry check first |
| 20 | `mario_sbr.c` | NonStarted | 69 | 19,132 | Mario and companions | largest `func_80153978` 1,492 B; create stub source + `configure.py` entry check first |
| 21 | `mot_swim.c` | NonStarted | 54 | 21,032 | Mario and companions | huge fn `func_80112bc4` 2,216 B; create stub source + `configure.py` entry check first |
| 22 | `mario_motion.c` | NonStarted | 87 | 36,120 | Mario and companions | huge fn `func_80148c28` 2,648 B; create stub source + `configure.py` entry check first |
| 23 | `mario_hit.c` | NonStarted | 123 | 73,448 | Mario and companions | huge fn `func_80138b38` 4,764 B; create stub source + `configure.py` entry check first |
| 24 | `mario_status.c` | NonStarted | 212 | 101,400 | Mario and companions | huge fn `func_80168378` 7,712 B; create stub source + `configure.py` entry check first |
| | **Area 2 NPCs and enemies**: NPC/enemy engine and script commands (individual enemy AI is in unsplit relF) | | | | | |
| 25 | `evt_npc.c` | NonMatching | 246 | 59,044 | NPCs and enemies | huge fn `func_8010ac50` 2,304 B |
| 26 | `npcdrv.c` | NonStarted | 254 | 167,860 | NPCs and enemies | huge fn `npcHitMain` 8,628 B; create stub source + `configure.py` entry check first; reuse `origin/wip/npcDelete` (stub source must be created first) |
| | **Area 3 Event/script system**: script command glue used by every room script | | | | | |
| 27 | `evt_sub.c` | NonMatching | 63 | 19,316 | Event/script system | huge fn `func_800d6674` 3,628 B |
| 28 | `evt_paper.c` | NonStarted | 2 | 152 | Event/script system | create stub source + `configure.py` entry check first |
| 29 | `evt_ext.c` | NonStarted | 2 | 180 | Event/script system | create stub source + `configure.py` entry check first |
| 30 | `evt_ac.c` | NonStarted | 3 | 312 | Event/script system | create stub source + `configure.py` entry check first |
| 31 | `evt_offscreen.c` | NonStarted | 3 | 348 | Event/script system | create stub source + `configure.py` entry check first |
| 32 | `evt_seq.c` | NonStarted | 3 | 364 | Event/script system | create stub source + `configure.py` entry check first |
| 33 | `evt_bg.c` | NonStarted | 3 | 416 | Event/script system | create stub source + `configure.py` entry check first |
| 34 | `evt_fade.c` | NonStarted | 6 | 628 | Event/script system | create stub source + `configure.py` entry check first |
| 35 | `evt_case.c` | NonStarted | 7 | 780 | Event/script system | create stub source + `configure.py` entry check first |
| 36 | `evt_img.c` | NonStarted | 14 | 2,492 | Event/script system | create stub source + `configure.py` entry check first |
| 37 | `evt_env.c` | NonStarted | 7 | 2,576 | Event/script system | largest `func_800e6a94` 1,288 B; create stub source + `configure.py` entry check first |
| 38 | `evt_eff.c` | NonStarted | 7 | 3,536 | Event/script system | huge fn `evt_eff` 2,444 B; create stub source + `configure.py` entry check first |
| 39 | `evt_frame.c` | NonStarted | 16 | 4,960 | Event/script system | huge fn `func_800e9178` 2,620 B; create stub source + `configure.py` entry check first |
| | **Area 4 Items**: items, item events, shops | | | | | |
| 40 | `evt_item.c` | NonStarted | 13 | 2,620 | Items | create stub source + `configure.py` entry check first |
| 41 | `item_event_data.c` | NonStarted | 60 | 17,276 | Items | largest `func_80025e80` 1,252 B; create stub source + `configure.py` entry check first; mostly data tables, check it is code |
| 42 | `evt_shop.c` | NonStarted | 54 | 20,052 | Items | largest `evt_shop_init_flopside_cards` 1,932 B; create stub source + `configure.py` entry check first |
| 43 | `itemdrv.c` | NonStarted | 40 | 27,464 | Items | huge fn `func_8007a758` 3,700 B; create stub source + `configure.py` entry check first; reuse `origin/wip/itemEntry` |
| | **Area 5 HUD, menus, windows, text**: HUD, dialogue, pause menu, fonts | | | | | |
| 44 | `romfont.c` | NonMatching | 4 | 1,888 | HUD, menus, windows, text | largest `romFontPrintGX` 1,288 B |
| 45 | `windowdrv.c` | NonMatching | 10 | 8,624 | HUD, menus, windows, text | largest `func_80039d40` 1,792 B |
| 46 | `hud.c` | NonMatching | 22 | 11,416 | HUD, menus, windows, text | huge fn `hudDisp` 3,612 B; reuse `origin/wip/hudMain` |
| 47 | `winmgr.c` | NonMatching | 19 | 14,516 | HUD, menus, windows, text | huge fn `func_8003d2ac` 4,916 B |
| 48 | `charpixlitemwin.c` | NonMatching | 32 | 16,344 | HUD, menus, windows, text | huge fn `charPixlItemWinOpen` 3,392 B |
| 49 | `msgdrv.c` | NonMatching | 31 | 23,896 | HUD, menus, windows, text | huge fn `msgAnalize` 6,800 B |
| 50 | `pausewin.c` | NonMatching | 102 | 68,580 | HUD, menus, windows, text | huge fn `pluswinChapterCtrlMain` 5,856 B |
| 51 | `sptexture.c` | NonStarted | 5 | 336 | HUD, menus, windows, text | create stub source + `configure.py` entry check first |
| 52 | `treasuremap.c` | NonStarted | 4 | 1,276 | HUD, menus, windows, text | create stub source + `configure.py` entry check first |
| 53 | `levelupwindow.c` | NonStarted | 7 | 3,156 | HUD, menus, windows, text | largest `func_80181248` 1,392 B; create stub source + `configure.py` entry check first |
| 54 | `charmwindow.c` | NonStarted | 10 | 4,792 | HUD, menus, windows, text | largest `func_80181d28` 1,440 B; create stub source + `configure.py` entry check first |
| 55 | `nameent.c` | NonStarted | 5 | 5,076 | HUD, menus, windows, text | huge fn `func_80182cc8` 2,964 B; create stub source + `configure.py` entry check first |
| 56 | `evt_msg.c` | NonStarted | 18 | 10,820 | HUD, menus, windows, text | huge fn `evtMsgFmtStr` 3,920 B; create stub source + `configure.py` entry check first |
| 57 | `fontmgr.c` | NonStarted | 34 | 14,332 | HUD, menus, windows, text | huge fn `FontDrawMessage` 2,100 B; create stub source + `configure.py` entry check first |
| | **Area 6 Map and file adjacent**: map objects, doors, camera scripts, map data | | | | | |
| 58 | `casedrv.c` | NonMatching | 12 | 8,460 | Map and file adjacent | huge fn `caseMain` 5,640 B |
| 59 | `mobjdrv.c` | NonMatching | 48 | 21,908 | Map and file adjacent | huge fn `mobjMain` 4,104 B |
| 60 | `setup_data.c` | NonStarted | 2 | 320 | Map and file adjacent | create stub source + `configure.py` entry check first |
| 61 | `map_data.c` | NonStarted | 2 | 416 | Map and file adjacent | create stub source + `configure.py` entry check first |
| 62 | `parse.c` | NonStarted | 7 | 1,620 | Map and file adjacent | create stub source + `configure.py` entry check first; reuse `origin/wip/parseGet1Next` |
| 63 | `cam_shift.c` | NonStarted | 4 | 2,024 | Map and file adjacent | largest `func_80054080` 1,796 B; create stub source + `configure.py` entry check first |
| 64 | `himo.c` | NonStarted | 2 | 2,484 | Map and file adjacent | largest `func_801a5834` 1,432 B; create stub source + `configure.py` entry check first |
| 65 | `evt_cam.c` | NonStarted | 21 | 4,132 | Map and file adjacent | create stub source + `configure.py` entry check first |
| 66 | `evt_hit.c` | NonStarted | 16 | 6,060 | Map and file adjacent | largest `func_800ebd74` 1,364 B; create stub source + `configure.py` entry check first |
| 67 | `evt_door.c` | NonStarted | 55 | 18,444 | Map and file adjacent | huge fn `func_800e47a8` 3,852 B; create stub source + `configure.py` entry check first |
| 68 | `cam_road.c` | NonStarted | 19 | 18,888 | Map and file adjacent | huge fn `func_800513d0` 3,464 B; create stub source + `configure.py` entry check first |
| 69 | `evt_mobj.c` | NonStarted | 68 | 31,984 | Map and file adjacent | huge fn `mobj_blk` 2,384 B; create stub source + `configure.py` entry check first |
| | **Area 7 Core loop, sequences, OS wrappers**: boot, scene sequencing, input, sound, GX helpers | | | | | |
| 70 | `seq_game.c` | NonMatching | 6 | 2,288 | Core loop, sequences, OS wrappers |  |
| 71 | `wpadmgr.c` | NonMatching | 1 | 2,848 | Core loop, sequences, OS wrappers | huge fn `wpadMain` 2,848 B; upstream/wpadmgr has nothing beyond master |
| 72 | `seq_mapchange.c` | NonMatching | 3 | 3,280 | Core loop, sequences, OS wrappers | huge fn `seq_mapChangeMain` 2,868 B |
| 73 | `seq_logo.c` | NonMatching | 3 | 3,504 | Core loop, sequences, OS wrappers | huge fn `seq_logoDisp` 3,136 B |
| 74 | `spmario.c` | NonMatching | 5 | 4,576 | Core loop, sequences, OS wrappers | largest `spmarioInit` 1,788 B |
| 75 | `evt_nand.c` | NonStarted | 12 | 1,024 | Core loop, sequences, OS wrappers | create stub source + `configure.py` entry check first |
| 76 | `seq_load.c` | NonStarted | 4 | 1,404 | Core loop, sequences, OS wrappers | largest `seq_loadMain` 1,248 B; create stub source + `configure.py` entry check first |
| 77 | `seq_gameover.c` | NonStarted | 3 | 1,500 | Core loop, sequences, OS wrappers | largest `seq_gameOverMain` 1,128 B; create stub source + `configure.py` entry check first |
| 78 | `homebuttondrv.c` | NonStarted | 10 | 4,400 | Core loop, sequences, OS wrappers | huge fn `homebuttonMain` 2,180 B; create stub source + `configure.py` entry check first |
| 79 | `evt_snd.c` | NonStarted | 54 | 5,700 | Core loop, sequences, OS wrappers | create stub source + `configure.py` entry check first |
| 80 | `gxsub.c` | NonStarted | 17 | 7,268 | Core loop, sequences, OS wrappers | largest `gxsubDrawDottedLine` 1,168 B; create stub source + `configure.py` entry check first |
| 81 | `seq_load_sub.c` | NonStarted | 6 | 15,560 | Core loop, sequences, OS wrappers | huge fn `func_8017e880` 9,296 B; create stub source + `configure.py` entry check first |
| 82 | `spmario_snd.c` | NonStarted | 86 | 27,172 | Core loop, sequences, OS wrappers | huge fn `spsndSFXMain` 5,960 B; create stub source + `configure.py` entry check first |
| | **Area 8 Rendering and effects**: display, lights, shadows, particle effects | | | | | |
| 83 | `lightdrv.c` | NonMatching | 10 | 2,396 | Rendering and effects |  |
| 84 | `offscreen.c` | NonMatching | 14 | 2,636 | Rendering and effects |  |
| 85 | `dispdrv.c` | NonMatching | 15 | 3,520 | Rendering and effects | largest `func_8005b60c` 1,784 B |
| 86 | `envdrv.c` | NonMatching | 15 | 5,880 | Rendering and effects | largest `func_80064014` 1,700 B |
| 87 | `fadedrv.c` | NonMatching | 17 | 7,444 | Rendering and effects | huge fn `fadeMain` 2,272 B |
| 88 | `imgdrv.c` | NonMatching | 17 | 9,616 | Rendering and effects | huge fn `func_80075b40` 2,060 B |
| 89 | `icondrv.c` | NonMatching | 22 | 10,340 | Rendering and effects | huge fn `iconGX` 3,344 B |
| 90 | `eff_zunbaba.c` | NonStarted | 3 | 1,100 | Rendering and effects | create stub source + `configure.py` entry check first |
| 91 | `eff_spm_use.c` | NonStarted | 3 | 1,216 | Rendering and effects | create stub source + `configure.py` entry check first |
| 92 | `eff_cheri_shell.c` | NonStarted | 5 | 1,284 | Rendering and effects | create stub source + `configure.py` entry check first |
| 93 | `eff_map_bubble.c` | NonStarted | 4 | 1,628 | Rendering and effects | create stub source + `configure.py` entry check first |
| 94 | `eff_map_water.c` | NonStarted | 4 | 2,088 | Rendering and effects | largest `func_800949dc` 1,128 B; create stub source + `configure.py` entry check first |
| 95 | `eff_score.c` | NonStarted | 3 | 2,432 | Rendering and effects | largest `func_800d1c80` 1,224 B; create stub source + `configure.py` entry check first |
| 96 | `eff_spm_get.c` | NonStarted | 7 | 3,132 | Rendering and effects | largest `func_80093c34` 1,004 B; create stub source + `configure.py` entry check first |
| 97 | `extdrv.c` | NonStarted | 14 | 4,384 | Rendering and effects | largest `extMain` 1,064 B; create stub source + `configure.py` entry check first |
| 98 | `bgdrv.c` | NonStarted | 16 | 5,560 | Rendering and effects | huge fn `func_8004ec64` 2,264 B; create stub source + `configure.py` entry check first |
| 99 | `eff_pure_heart.c` | NonStarted | 17 | 6,352 | Rendering and effects | huge fn `func_80095cf0` 2,596 B; create stub source + `configure.py` entry check first |
| 100 | `eff_spm_recovery.c` | NonStarted | 16 | 6,784 | Rendering and effects | largest `func_80091dc4` 1,032 B; create stub source + `configure.py` entry check first |
| 101 | `effdrv.c` | NonStarted | 35 | 7,976 | Rendering and effects | huge fn `func_800623f8` 2,316 B; create stub source + `configure.py` entry check first |
| 102 | `shadowdrv.c` | NonStarted | 44 | 10,456 | Rendering and effects | largest `shadowDisp` 1,688 B; create stub source + `configure.py` entry check first |
| 103 | `framedrv.c` | NonStarted | 27 | 13,328 | Rendering and effects | huge fn `func_8006a3ac` 2,544 B; create stub source + `configure.py` entry check first |
| 104 | `eff_sub.c` | NonStarted | 31 | 21,848 | Rendering and effects | huge fn `func_8005c47c` 11,564 B; create stub source + `configure.py` entry check first |
| | **Area 9 Minigames and misc**: action-command minigames, search | | | | | |
| 105 | `ac_pendulum_crane_timing.c` | NonStarted | 4 | 916 | Minigames and misc | create stub source + `configure.py` entry check first |
| 106 | `ac_timing_hold.c` | NonStarted | 4 | 960 | Minigames and misc | create stub source + `configure.py` entry check first |
| 107 | `ac_crane_timing.c` | NonStarted | 4 | 1,572 | Minigames and misc | largest `func_80022590` 1,012 B; create stub source + `configure.py` entry check first |
| 108 | `evt_search.c` | NonStarted | 6 | 1,820 | Minigames and misc | largest `func_8024a7c4` 1,312 B; create stub source + `configure.py` entry check first |
| 109 | `ac_shake_timing.c` | NonStarted | 4 | 2,176 | Minigames and misc | largest `func_8001db20` 1,032 B; create stub source + `configure.py` entry check first |
| 110 | `ac_timing_button.c` | NonStarted | 3 | 2,236 | Minigames and misc | largest `func_800244e8` 1,560 B; create stub source + `configure.py` entry check first |
| 111 | `ac_signal_timing.c` | NonStarted | 4 | 2,936 | Minigames and misc | largest `func_800230ac` 1,536 B; create stub source + `configure.py` entry check first |
| 112 | `ac_shake.c` | NonStarted | 6 | 3,432 | Minigames and misc | largest `func_80240884` 1,648 B; create stub source + `configure.py` entry check first |
| 113 | `ac_target_row.c` | NonStarted | 8 | 3,644 | Minigames and misc | largest `func_80023d04` 1,048 B; create stub source + `configure.py` entry check first |
| 114 | `acdrv.c` | NonStarted | 18 | 10,816 | Minigames and misc | huge fn `func_8003f934` 3,656 B; create stub source + `configure.py` entry check first |
| 115 | `ac_scissor.c` | NonStarted | 16 | 15,988 | Minigames and misc | huge fn `func_8001f344` 5,468 B; create stub source + `configure.py` entry check first |
| 116 | `search.c` | NonStarted | 76 | 31,988 | Minigames and misc | huge fn `func_802473a8` 8,880 B; create stub source + `configure.py` entry check first |
