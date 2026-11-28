# Brief for matching subagents (phase 3, EU0)

Unattended, no questions. This brief replaces any other instructions. Read nothing about project status.
Tools: `T=/c/Users/ender/SPM_N3DS_XL/notes/tools`, repo `/c/Users/ender/SPM_N3DS_XL/spm-decomp` (use absolute paths / `git -C`).

## Hard rules (breaking one = reply `BLOCKED`)
- Start: repo clean and on `master`, else `BLOCKED: ...`. Never touch `spm-decomp-ag`. Never push. No `checkout --`,
  `restore`, `reset`, `stash`, `clean`, no manual `git commit` / `switch` (finish.py does them).
- **Build only with** `python -I $T/build.py <file> <function> [--variants PREFIX]`. Never run `ninja`, `fdiff.py`,
  `objdiff-cli` or a compiler yourself. build.py counts every build (failed compiles too) and refuses at the cap; when it
  says `CAP REACHED` or `GOOD-ENOUGH`, stop that function.
- **No inline code:** never `python -`, `python -c`, `python3`, heredocs or pipes into an interpreter. Edit sources with
  Edit/Write. A helper script goes in `$TEMP/decomp-matcher/` (Write tool) and runs as `timeout 300 python -I <file>`.
- **Never stop any process** (`kill`, `taskkill`, `Stop-Process`, ...), even a stuck one: report it in your reply instead.
- Never commit anything from `build/` or `orig/` (finish.py refuses).

## Work, one function at a time
- Source `src/<file>.c` (stubs are `// NOT_DECOMPILED <name>`), headers `spm-headers/include/spm/`, original asm
  `build/EU0/asm/<file>.s` (Grep `\.fn <name>` and read only those lines). `src/mario*.c` may mix CRLF/LF: verify edits.
- Stop at no differing lines, at the cap, or at GOOD-ENOUGH (only register/label/pool differences after 3 builds).
- Then, with the edits uncommitted on master: `timeout 1200 python -I $T/finish.py <file> <function> "<short note: what was
  hard / what fixed it>"`. It measures the official % with a full build: exactly 100% is committed on master, anything else
  goes to its own pushed `wip/<function>` branch, and master is clean again for the next function. Run it even if you got
  nowhere. Do not log; the coordinator logs the measured result.
- Reply with **exactly one line**: per function the line finish.py printed (name, %, builds), or `BLOCKED: <reason>`.

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
- Testing 20-100 renamed variant copies in one build (`--variants`) finds register/order fixes fast; delete them before finish.py.
