# Brief for matching subagents (phase 3, EU0)

Unattended, no questions. This brief replaces any pilot instructions in your agent definition. Read nothing about project
status (no logs, no resume, no old notes).

## Paths and safety
- Work only in `/c/Users/ender/SPM_N3DS_XL/spm-decomp` (your shell may start elsewhere: use absolute paths / `git -C`).
  Never touch `spm-decomp-ag`. Never push to `upstream`. No `checkout --`, `restore`, `reset`, `stash`, `clean`.
- Start: that repo must be clean and on `master`, else reply `BLOCKED: ...`.
- Python only as `python -I <script file>`. Never `python -`, `-c`, `python3` or heredoc python (hangs). No objdiff-cli
  watch/interactive mode. Before replying, every process you started has exited. Never run anything that waits on stdin
  (bare `cat`, heredocs): create scripts with the Write tool and edit sources with Edit.
- Never commit anything from `build/` or `orig/`.

## Work
- Source `src/<file>.c` (stubs are `// NOT_DECOMPILED <name>`), headers `spm-headers/include/spm/`, original asm
  `build/EU0/asm/<file>.s` (Grep `\.fn <name>` and read only those lines). `src/mario*.c` may mix CRLF/LF: verify edits applied.
- Compile + diff: `python -I /c/Users/ender/SPM_N3DS_XL/notes/tools/fdiff.py <file> <function>`
  (`--variants func_T` ranks renamed test copies in one build; `--score` runs full ninja, prints official % and checksums).
- **Each build is one attempt, per function** (failed compiles count). Caps: up to 128 B: **4**; 129-640 B: **6**;
  641-2,044 B: **8**. Stop at 100%.
- **Good-enough:** at 98% or better with only register numbering, labels and string-pool offsets differing, stop after at most
  3 attempts (at once if 3 are used). Do not chase linkability.

## Finish each function
- Result: `yes` (exactly 100%), `functional` (all logic there; only registers / order / pool labels differ) or `incomplete`.
- Commit to `master`, message `Decompile <name>` (several names may share one commit, comma separated): functions at 100%, and
  functions at 99%+ whose only differences are labels/string-pool offsets. Run `fdiff.py ... --score` (or `ninja`) first:
  main.dol and relF.rel OK. Then `git push origin master`.
- Everything else: take the code out of master, commit it on `wip/<function>` (from master), `git push origin wip/<function>`,
  switch back to master, tree clean.
- One log row per function:
  `python -I /c/Users/ender/SPM_N3DS_XL/notes/tools/log_row.py <file>.c <function> <tiny|small|medium|large> <bytes> <yes|functional|incomplete> <percent> <attempts> "<commit or branch>" "<short note: what was hard / what fixed it>"`
  Add `--defer retry` if the result is below 98% or incomplete. Add `--push` to your **last** call only (commits and pushes notes).
- Reply with **exactly one line** (per function: name, %, attempts), or `BLOCKED: <reason>`.

## MWCC tricks (more detail: "Old BRIEF.md" in notes/reference.md)
- Declaration order of locals sets register numbering; Vec3 locals are declared in reverse stack order; declare pointers before
  loop counters; `i++, e++` in the for header.
- Float compare with zero loaded first (fcmpu operands swapped): `f32 z; f32 x; x = field; z = 0.0f; if (x != z)`
  (or two locals for `x == 0 && y == 0`). A plain `== 0.0f` can be right in `==`/`>`/`<` chains.
- Frame too big / odd Vec3 stores: initialised local `Vec3 v = {x, y, z};`, store with `(f32)(f64) v.x`. Copies: `Vec3 v = t;`.
- `#pragma dont_inline on/off` when MWCC inlines a call the original keeps; static inline helpers for repeated code or to
  free a saved register; inline small callees by hand when MWCC will not.
- Identical switch cases get merged: write each body separately. Binary-search switch in ours only: use an if-chain on a u16.
- Overlay structs with named padded fields beat raw `(u8 *)p + off` casts. Real float literals hoist pool constants.
- Flags: separate read-modify-write statements, try orders; `!(x & mask)` for cntlzw. `if (p == 0) q = 0; else q = ...;`
- Add includes and prototypes before the first compile (`-W error`: no unused locals).
- Testing 20-100 renamed variant copies in one compile finds register/order fixes fast.
