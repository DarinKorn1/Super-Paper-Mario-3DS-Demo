# Remaining work: functions not yet decompiled (EU0)

Counted on 2026-11-12 from the EU0 config only (`spm-decomp` master at `d53393b`): read-only, nothing built.
Scope: `main.dol` and `relF`. Library code (SDK, NW4R, MSL, runtime) is excluded.

## Table

Size classes use the pilot's thresholds (small 32-128 bytes, medium 200-640, large 700-2,044 as the top of the
pilot's large bucket) plus a fourth class, **huge, over 2,044 bytes**. The pilot's buckets leave gaps, so
three extra rows (under 32, 129-199, 641-699) are shown so that every function is counted once. (The pilot's
own large bucket was written as 700-2,100; per your instruction everything above 2,044 is in "huge".)

| Size class | main.dol, split files | relF | **Firm total** | main.dol, unsplit gaps (unverified) | Total incl. unverified |
|---|---|---|---|---|---|
| under 32 | 339 | 37 | **376** | 250 | 626 |
| small 32-128 | 1,048 | 387 | **1,435** | 444 | 1,879 |
| between small and medium 129-199 | 482 | 192 | **674** | 269 | 943 |
| medium 200-640 | 957 | 288 | **1,245** | 720 | 1,965 |
| between medium and large 641-699 | 70 | 16 | **86** | 38 | 124 |
| large 700-2,044 | 438 | 87 | **525** | 218 | 743 |
| huge over 2,044 | 132 | 24 | **156** | 28 | 184 |
| **Total functions** | **3,466** | **1,031** | **4,497** | **1,967** | **6,464** |
| Total bytes | 1,536,576 | 409,964 | 1,946,540 | 696,908 | 2,643,448 |

- **Firm total** = game code that is in a source-file split of `main.dol` or in `relF` and is not decompiled yet.
  Total: **4,497 functions, 1,946,540 bytes**. The four named classes (small, medium, large, huge) make up
  3,361 of them.
- **Unverified column**: 1,967 functions sit in `main.dol` address gaps that have no split yet, inside the game-code
  address range, nearly all with placeholder `func_` names. They are probably game code but nothing in the config says so;
  some may be library code. Gaps: `0x80096D70-0x800D17C8` (545 functions), `0x801D25F4-0x8023697C` (1,219) and
  `0x8024AD48-0x80255334` (176); the last one sits just before the runtime code, so it is the likeliest to include library code.

## How it was counted

1. Functions = `type:function` symbols in `.text` of `config/EU0/symbols.txt` (main.dol, 9,183) and
   `config/EU0/relF/symbols.txt` (1,033); every one has a size.
2. Each function is put in a split unit by address (`splits.txt`).
3. **main.dol, split files:** a unit that is `Matching` in `configure.py` counts 0. A `NonStarted` unit (no source
   file): all its functions count (2,267 functions). A `NonMatching` unit: the
   functions marked `// NOT_DECOMPILED <name>` in its source file count (1,199 functions). Functions with a real
   body in a NonMatching file are counted as decompiled (99 of them), even if not yet matching.
4. **relF:** only `dan.c` is split (NonMatching, 25 not-decompiled functions); everything else in relF
   (1,006 functions) is unsplit. relF is treated as game code throughout (it is a game module, with no library
   splits), which is an assumption.

## Excluded as library or runtime

| What | Functions | Bytes |
|---|---|---|
| `main.dol` split library units (`Runtime.PPCEABI.H/*`, `DEMOInit.c`) | 2 | 112 |
| `main.dol` tail after the last split (`0x80256728` to the end of `.text`): OS, GX, VI, MEM, Bluetooth, USB, MSL and similar | 3,310 | 808,900 |
| `main.dol` `.init` section (14 functions: memcpy, TRK, start-up) | 14 | not counted |

The tail has 1,073 functions that still have placeholder names, so some of it may be game code or other libraries that
the names do not reveal; it was excluded as a whole, since nothing in the config separates it.

## Caveats

- The classification into game vs library for unsplit code is by address and symbol names only.
- Cross-check: this method gives 3,466 for split `main.dol` files; the pilot's start-of-pilot
  figure was 3,516 (a slightly different count, taken before the pilot's roughly 39 matches). The two agree within about 11
  functions, which I did not trace further.
- "Not decompiled" means no C body in the source. A function with a body that does not match yet counts as decompiled (see step 3).
