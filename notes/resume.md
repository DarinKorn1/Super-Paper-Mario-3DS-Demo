# Resume (the only status file to read at the start of a session)

Continue: "Read CLAUDE.md and continue the overnight run". Rules and coordinator loop: `CLAUDE.md`.

## Current file
- Paused 2026-11-26 (user restarting laptop). Batch 76 `func_80158c98` was interrupted mid-work: its edit is on
  spm-decomp branch `wip/leftover-20261126` (local, not pushed); master clean at `64bf68d`, pushed.
- `mario_status.c` (#24, 212 functions, 6 huge deferred): stubs and queue exist (do not run `make` again); continue with
  `phase3_queue.py next mario_status.c` (next: batch 76 of 153, `func_80158c98`, redo it).
- Done 128 of 206: 126 exactly 100%, 2 functional (`func_80159070` 99.00%, `wip/func_80159070`;
  `func_8015980c` ~99% r30/r31 swap, `wip/func_8015980c`). Left: 78. Not linkable yet.
- `mario_hit.c` finished (row 853: huge `func_80138b38` deferred).

## Next files, in plan order
`npcdrv.c` (#26, reuse `origin/wip/npcDelete`), `itemdrv.c` (#43, reuse `origin/wip/itemEntry`), `hud.c` (#46,
reuse `origin/wip/hudMain`), `winmgr.c`, `charpixlitemwin.c`, `msgdrv.c`, `pausewin.c`, then #51 onwards.
Skip rows marked ANTIGRAVITY. **Reserved for Antigravity** (do not work): `evt_sub, evt_paper, evt_ext, evt_ac,
evt_offscreen, evt_seq, evt_bg, evt_fade, evt_case, evt_img, evt_env, evt_eff, evt_frame, evt_item, item_event_data,
evt_shop` (plan #27-42, 260 functions).

## Linked files (2)
`evt_guide.c`, `evt_pouch.c`.

## ANTIGRAVITY READY 2026-11-25 16:38
- Merge #4 done (master 87f0a51, both checksums OK, pushed); `ag/work` = master, pushed; queue refilled with 260 functions
  (266 unticked with the older leftovers). The one-off WIP commit was not needed (user confirmed it had finished).
- 36 new "Decompile" claims: 31 exactly 100%. 5 (99.90-99.99%, string-offset differences) are stubs on master; code on
  `wip/ag-labelonly-20261125`; listed in `deferred.md`. `evt_npc_flip`, `func_80108cc0` stay stubbed (merge #3).
- `evt_npc_get_hp` / `get_max_hp` now show 99.96% (string order shifted by the new code; kept). Same cause expected above.

## Deferred (full list: `notes/deferred.md`)
Huge: `func_80138b38` (mario_hit, WIP 98.97%), `evt_npc_walk_to`, `func_8010ac50`; later huge ones are added by the queue script.
Older near-misses: rows below 100% in `archive/phase3-results.md` and `phase2-results.md`.

## Leftovers (harmless, keep)
- spm-decomp branch `wip/leftover-20261125`: unfinished edits to mario_hit.c / mario_motion.c found uncommitted today.
- `wip/mot_jabara-partial`. Old idle `python -` processes from 11/18-20 cannot be attributed: do not stop them.
- A stuck `cat.exe` (PID 38036, started 2026-11-25 16:46 by a subagent shell) is still open; stopping it was denied to the
  subagent, so it is left for the user. It does not block builds.
- `CLAUDE.md` and `.claude/agents/decomp-matcher.md` (restructured 2026-11-25) are uncommitted until the user has seen them.

## Blockers
None.
