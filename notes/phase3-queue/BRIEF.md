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
