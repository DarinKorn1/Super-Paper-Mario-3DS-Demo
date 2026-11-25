# Resume (the only status file to read at the start of a session)

Continue: "Read CLAUDE.md and continue the overnight run". Rules and coordinator loop: `CLAUDE.md`.

## Current file
- `mario_status.c` (#24, 212 functions, NonStarted): start with `phase3_queue.py make mario_status.c --stub`, then
  `phase3_queue.py next mario_status.c` for each batch.
- `mario_hit.c` finished (row 853: huge `func_80138b38` deferred).

## Next files, in plan order
`npcdrv.c` (#26, reuse `origin/wip/npcDelete`), `itemdrv.c` (#43, reuse `origin/wip/itemEntry`), `hud.c` (#46,
reuse `origin/wip/hudMain`), `winmgr.c`, `charpixlitemwin.c`, `msgdrv.c`, `pausewin.c`, then #51 onwards.
Skip rows marked ANTIGRAVITY. **Reserved for Antigravity** (do not work): `evt_sub, evt_paper, evt_ext, evt_ac,
evt_offscreen, evt_seq, evt_bg, evt_fade, evt_case, evt_img, evt_env, evt_eff, evt_frame, evt_item, item_event_data,
evt_shop` (plan #27-42, 260 functions).

## Linked files (2)
`evt_guide.c`, `evt_pouch.c`.

## Antigravity: step 5 PENDING (not ready)
- 2026-11-25 15:40: Antigravity is **active** (building `evt_npc.c`, log edited 15:26, agy.exe running), so no WIP commit,
  no merge, folder untouched. Re-check after each batch of work: if `ag-results.md` and its sources are unchanged for over
  an hour, commit its uncommitted changes as WIP on `ag/work` (note it in `ag-results.md`; one-off), then:
  merge routine in `CLAUDE.md`, then
  `python -I notes/tools/refill_ag_queue.py --files evt_sub.c evt_paper.c evt_ext.c evt_ac.c evt_offscreen.c evt_seq.c evt_bg.c evt_fade.c evt_case.c evt_img.c evt_env.c evt_eff.c evt_frame.c evt_item.c item_event_data.c evt_shop.c --write`,
  commit on `ag/work`, push `ag/work`, and write "ANTIGRAVITY READY <time>" here.

## Deferred (full list: `notes/deferred.md`)
Huge: `func_80138b38` (mario_hit, WIP 98.97%), `evt_npc_walk_to`, `func_8010ac50`; later huge ones are added by the queue script.
Older near-misses: rows below 100% in `archive/phase3-results.md` and `phase2-results.md`.

## Leftovers (harmless, keep)
- spm-decomp branch `wip/leftover-20261125`: unfinished edits to mario_hit.c / mario_motion.c found uncommitted today.
- `wip/mot_jabara-partial`. Old idle `python -` processes from 11/18-20 cannot be attributed: do not stop them.

## Blockers
None.
