# Resume (the only status file to read at the start of a session)

Continue: "Read CLAUDE.md and continue the overnight run". Rules and coordinator loop: `CLAUDE.md`.

## Current file
- `mario_status.c` (#24) **finished 2026-11-26** (all 153 batches). Master builds, `main.dol: OK`, `relF.rel: OK`, pushed.
  `check_matches.py --unit`: 212 checked, 156 exactly 100%, 56 not: 51 still stubs (6 huge deferred + 45 near-misses /
  functional, each on its own `wip/<function>` branch, see log), 5 on master at 99.73-99.94% (label/string-pool only):
  `func_8015cff4`, `func_8015eb48`, `func_80164048`, `func_801641e4`, `func_8016547c`. **Not linkable.**
- Next: `npcdrv.c` (start with `phase3_queue.py make npcdrv.c --stub`).
- `wip/leftover-20261126` (local): interrupted first try of `func_80158c98`; since redone at 100%, so obsolete (ask before deleting).

## Subagent problems seen 2026-11-26 (fix BRIEF / agent file; needs the user's OK)
- Repeated `python -` / `python -I -` (heredoc piped to python to edit files) despite BRIEF and prompt: left hung python.exe
  processes; one subagent killed two it had not started (PIDs 35780, 13548).
- Attempt cap overrun several times (7/6, 9/8, ~10/8); some log rows give a lower count than the real one
  (`func_80163788` ~10 not 8, `func_8016737c` 5 not 4).
- Some reported "100% yes" are 99.9% (`func_8015cff4`, `func_801641e4`); two functional ones were put on master
  (`func_8016547c`, `func_8015eb48`) while others went to `wip/` branches. Percent often "estimated, not measured".
- Twice pushed without seeing the checksum lines (coordinator re-checked: OK). Prompt now adds
  `build/tools/dtk.exe shasum -c config/EU0/build.sha1`.

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
