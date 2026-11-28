# Resume (the only status file to read at the start of a session)

Continue: "Read CLAUDE.md and continue the overnight run". Rules and coordinator loop: `CLAUDE.md`.

## Current file
- `npcdrv.c` (#26): stubs pushed 2026-11-27; 230 queued in 145 batches, 24 huge deferred. Loop: `phase3_queue.py next`,
  subagent, then `land.py npcdrv`. Old partial work (read-only hint for subagents): `origin/wip/npcDelete`.
- `mario_status.c` (#24) finished 2026-11-26: 156 of 212 exactly 100%; not linkable.

## Script enforcement (since 2026-11-27, user-approved)
- `build.py` (caps, counts in `notes/phase3-queue/attempts.json`, one function at a time), `finish.py` (measures the official %,
  100% to master, else pushed `wip/<function>`), `land.py` (coordinator: re-check with check_matches, `safe_push.py`, log the
  measured % and real count), `to_wip.py`. Subagents never push, log or stop processes.
- 71 non-exact functions taken off master to `wip/<name>` (or `wip/<name>-master`); master now holds only exact matches
  of ours. 8 non-exact functions not from our work (upstream: `_hitEnt`, 7 in relF `dan`) left on master.
- Test on npcdrv batch 1 (10 tiny): caps counted (2-3 builds each), all 10 measured 100%, safe push OK, rows logged. Found:
  the subagent edited all 10 at once and finish.py committed them under one name; land.py refused (guard worked), records
  repaired by hand. Fixed: build.py and finish.py now refuse while another function's stub is removed but unfinished.
  Also finish.py refuses after a failed compile while builds are left (batches 2 and 5 gave up after one).
- Known limit: the official % can read 100% with a wrong float constant (pool values compared by label only); batch 7
  caught `npcFinishFlipInstant` 1.0f vs 270.0f itself. Linking (checksums) is the final proof.

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
