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
- **Dead Vec3 makes the stack frame too big (0x70 vs 0x50) / frsp + psq_st stores to a Vec3 field**: build the Vec3 as an initialized local and store each field through a double: `Vec3 v = { x, y, z }; wp->pos.x = (f32)(f64) v.x;` (same for y, z). Member-wise `v.x = x` always gave the big frame. Origin: evt_guide_set_pos (evt_guide.c).
- `if (x == 0.0f)` with a plain literal can be correct when the compare chain is `==`/`>`/`<` on the same value (func_800e9e14); the local-zero trick is for lone `!=`/`==` compares that show the constant loaded first.
- **Test many variants per build**: append renamed copies of the function (with a prototype each, e.g. `void func_T0(MarioWork * wp);`) holding different variants to the same .c file, compile once, diff each copy against the original, keep the winner and delete the copies. Also: raw `*(f32 *)((u8 *)wp + off)` casts can make MWCC CSE an address into a spare register; named struct fields avoid it. Origin: func_80173d30 (mot_jump.c).

## More MWCC tricks (mot_swim.c / mario_motion.c / mario_hit.c, 2026-11-18/19)
- **Test 40-100 renamed variant copies of the function in ONE compile** (with prototypes), diff each; this found most hard fixes. Count it as one build.
- Header **overlay structs with named fields** (pad to exact sizes) beat raw `(u8*)wp+off` casts (raw casts make MWCC CSE addresses into spare regs). Real **float literals** (not extern floats) so MWCC hoists pool constants; exception: some zero compares need the extern zero constant.
- Polynomials: overlay struct on `&wp->jumpFallPara`, copy the polynomial verbatim from `marioJump` (src/mario_motion.c); `f32 t;` before `f32 lim;`; read fields again after updating; static inline helper for repeated polynomials; `#pragma dont_inline` around a callee (or its caller) when MWCC inlines what the original calls.
- `if (p == 0) q = 0; else q = ...;` instead of nested ternary; `i++, e++` in for header; declare pointers before loop counters; `Vec3 t = {...}; Vec3 v = t;` for stack copies; `Vec3 pos = obj->position;` for lwz/stw copies.
- Flag RMW: split into separate statements and try several orders (`flags |= a; flags &= ~b; miscFlags &= ~1; flags |= c;`); u32 temps declared disp then misc; `!(x & mask)` for cntlzw; `if ((attr & 0x80000000) == 0) return 0;`; ternary `(flags & 0x4000) ? h : h*scale.y`.
- Range checks: `== a || == b` vs `(u16)(x+0xFFB9) <= 2` vs goto forms; a switch that compiles to binary search -> plain `!=`/`==` if-chain on a u16 local; returning-1 cases `break` to one shared `return 1`; `if (hit != 0) {...} return 0;` nesting to share a return; `goto done` for early exits.
- Static inline helpers free a saved register (marioLandon). Manually inline small callees MWCC does not auto-inline (func_80144bbc). `SPM_ASSERT_` with varargs when the original passes extra args; assert/string-pool offset diffs disappear only once the whole file is defined (count as label-only).
- Missing includes/prototypes and `-W error` unused locals cost builds: add them before the first compile. Never run python except `python -I <script file>`; `python -`/`-c`/`python3` hang and leave strays.
