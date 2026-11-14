# Common brief for decomp-matcher subagents (phase 3, EU0, spm-decomp, master)

Unattended; no questions. Read the "Overnight run rules" and the "Diff method" bullet at the end of CLAUDE.md and obey them
(process safety, `dtk elf disasm` + `report.json` for diffs, no interactive python REPL - script files with `python -I` only).

- Function list (name, address, bytes, smallest first): `notes/phase3-queue/<file>.txt`. A function still marked `// NOT_DECOMPILED <name>` in `spm-decomp/src/<file>.c` is a stub; if a function is already decompiled and 100% in `build/EU0/report.json`, log it as "already matched" and make no change.
- Log one row per function in `notes/phase3-results.md` (Log table, columns `# | File | Function | Size class | Bytes | Matched | Match % | Attempts | Commit / branch | Notes`; numbering continues). Notes: what was hard / what fixed it.
- Each function gets its OWN 10 builds (12 if over 2,044 bytes). Do not share builds across functions. Functionally complete (all logic present, only register numbering/instruction order/pool labels differ) is acceptable; "incomplete" = logic missing or wrong. Label-only string/float-pool offset diffs count as a match only if report.json says >= 99% and the diff is only labels/offsets; say so in the row.
- First confirm `ninja` on master is fine (`main.dol: OK`, `relF.rel: OK`; if no OK lines print because nothing relinked, check `build/EU0/ok` exists).
- Commit a match to spm-decomp `master` only if ninja succeeds and main.dol/relF.rel stay OK; `git push origin master`. A near-miss goes on `wip/<function>`, pushed to origin. Never touch `spm-decomp-ag`; never push to `upstream`. No `git checkout`/`restore` to undo edits (keep a saved copy). Headers live in `spm-headers/`.
- Commit AND push the log in the outer repo (`C:\Users\ender\SPM_N3DS_XL`: `git pull --rebase`, `git push origin master`; commit only `notes/` files); verify the push succeeded.
- Before returning, make sure every objdiff-cli/ninja/python process you started has exited. Reply with at most 5 lines.

## Known MWCC tricks (add new ones here; found 2026-11-14)
- **Float compare against 0.0f shows zero loaded first (fcmpu operands swapped)**: a literal `0.0f` in the compare never works. Use a local for the zero:
  (1) `x == 0 && y == 0`: `f32 x = field; f32 z = 0.0f; if (x == z && y == z)`.
  (2) lone `field != 0`: `f32 z; f32 x; x = field; z = 0.0f; if (x != z)` (declaration order picks registers, assignment order picks load order).
  (3) zero also stored to another field: `f32 z2 = 0.0f; store z2; if (field != z2)` with the field read inline.
  Origin: func_80119d6c / func_8011a2fc (mot_crouch.c). Try this FIRST when the only diff is fcmpu f0/f1 order.
- Locals: declaration order sets saved-register numbering (try reordering); Vec3 locals declared in reverse of stack order.
- `#pragma dont_inline` on a callee when the original calls it but MWCC inlines it (func_80118e88 in mot_walk.c).
- Switch with identical case bodies: MWCC merges cases; write each case body separately in address order.
- `x ? a : b` vs early return, `(s32)` cast on bool-returning calls (camCheck3d) to get cmpwi, byte-offset table indexing (c*8+g*4) for register order.
- Never run `python -` / heredoc python (hangs, leaves strays); `src/mario.c` has mixed CRLF/LF line endings: verify each edit applied.
