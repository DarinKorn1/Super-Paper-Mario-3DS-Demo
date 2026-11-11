# How one function goes from assembly to matched C in spm-decomp

Sources: `spm-decomp/README.md`, `CONTRIBUTING.md`, `configure.py`, `tools/`, `spm-headers/CONTRIBUTING.md`,
and the generated `objdiff.json` / `build.ninja` from the earlier US0 build. Version numbers are
the ones pinned in `configure.py` today.

## The idea in one paragraph

"Matching" means writing C that, compiled with **the same compiler and flags Nintendo's
developers used** (Metrowerks CodeWarrior for GameCube 3.0a5.2, `mwcceppc`), produces **exactly
the same machine code** as the game. You never edit the game binary. Instead you write C, compile
it, and compare the compiler's output against the original function, instruction by instruction,
until there are no differences. When every function in a file matches, the file can be linked
into a rebuilt `main.dol` whose SHA-1 equals the original's.

## The tools and what each does

| Tool | Where it comes from | Job |
|---|---|---|
| **decomp-toolkit (dtk)** v1.8.0 | downloaded by the build into `build/tools/dtk.exe` | Reads `main.dol` / `relF.bin` from your disc, cuts them into per-file object files using `config/EU0/splits.txt`, names things using `symbols.txt`, and writes disassembly to `build/EU0/asm/`. |
| **mwcceppc** (GC/3.0a5.2) | downloaded into `build/compilers/` | The original compiler. Compiles `src/*.c` with the flags in `configure.py` (`cflags_dol`: `-O4,p -inline all -lang c++ -sdata 4 ...`). |
| **ninja** | installed on this PC (winget) | Runs the build that `configure.py` writes (`build.ninja`). |
| **objdiff** (GUI, separate download) and **objdiff-cli** v3.5.1 (downloaded into `build/tools/`) | github.com/encounter/objdiff | Shows the original function and your compiled function side by side, with a match %. Reads `objdiff.json`, rebuilds automatically when you save. The CLI makes the progress report. |
| **decomp.me** | website | Online "scratch" editor with the same compiler (preset 74 for the DOL, 75 for the REL; compiler `mwcc_41_60831`). objdiff can create a scratch for you. **This uploads the original function's code to a public site** (see Rules below). |
| `tools/decompctx.py` | in repo | Flattens a source file's `#include`s into one `ctx.c` "context" file (types and declarations) for decomp.me. |
| `tools/makectx_m2c.py` | in repo | Runs the preprocessor over all headers to make a context for **m2c** (a machine-code-to-C decompiler that gives a rough first draft). m2c itself is not in the repo. |
| `tools/changes_fmt.py` | in repo | Compares two progress reports (`report.json`) and lists which functions changed match %. Used by CI. |
| `.clang-format` | in repo | Formatting rules (4 spaces, etc.); VS Code with the clangd extension uses it. |

## Step by step

### 0. One-time setup (needs a PAL disc; ask before each download)

1. Put the disc image in `spm-decomp/orig/EU0/` (or `orig/EU1/`). ISO, RVZ, WIA, WBFS, CISO, NFS, GCZ
   and TGC all work.
2. `python configure.py` (EU0 is the default; `python configure.py --version EU1` for revision 1).
   This writes `build.ninja`, `objdiff.json` and `compile_commands.json`.
3. `ninja`. The first run downloads dtk, the compilers, binutils and objdiff-cli, then splits the
   game, builds every `Matching` source file, links a new `main.dol` and checks its SHA-1 against
   `config/EU0/build.sha1`. A file `build/EU0/ok` means the rebuilt game is byte-identical. If the
   disc is the wrong revision, dtk stops with a hash mismatch against `config/EU0/config.yml`.
4. Download the objdiff GUI from its GitHub releases page and, under Project settings, set
   *Project directory* to the `spm-decomp` folder. It loads `objdiff.json` by itself.

### 1. Choose a function, and say so

- Pick from `notes/pilot-functions.md` (or `config/EU0/symbols.txt`).
- `CONTRIBUTING.md` asks contributors to announce what they plan to decompile in the
  `#reverse-engineering` channel of the Flipside Tower Discord, to avoid duplicate work. For
  a private fork that's optional, but it's how you'd learn whether someone already has it.
  Upstream also has work-in-progress branches (`animdrv-test`, `wpadmgr`); avoid those files.

### 2. Find where it lives

- `config/EU0/symbols.txt`: one line per symbol, e.g.
  `winMgrSetSize = .text:0x8003BC2C; // type:function size:0x2C`. Names like `fn_8003BC2C` or
  `func_8003bc2c` mean nobody knows the real name yet.
- `config/EU0/splits.txt`: which source file each address range belongs to
  (`winmgr.c: .text start:0x8003B26C end:0x8003EB4C`). If the function isn't inside any range,
  it isn't split yet, and a split has to be added before it can be decompiled (out of scope for
  the pilot: all 30 pilot functions are already inside a split).
- `configure.py`, `config.libs`: the file's status.
  - `Matching`: done and linked; its functions are already decompiled.
  - `NonMatching`: a source file exists but isn't linked yet. Functions still to do are marked
    `// NOT_DECOMPILED name`.
  - `NonStarted`: no source file yet.

### 3. Read the original assembly

- After a build, `build/EU0/asm/<file>.s` holds the whole split file's disassembly
  (non-split code is in `auto_...` files).
- In objdiff, select the file (e.g. `main/winmgr`) in the left sidebar; the right column is the
  original ("target"). Clicking a function shows its instructions.

### 4. Create or open the source file

For a `NonStarted` file:

1. Create `src/<file>.c` (REL files go in `rel/`). Start with the warning comment, then the
   includes, then `extern "C" {` (the game was compiled as C++; the `extern "C"` block avoids
   C++ name mangling):

   ```c
   /*
       WARNING: Not fully decompiled
       This file is currently not linked into the final dol
   */

   #include <common.h>
   #include <spm/winmgr.h>

   extern "C" {

   // NOT_DECOMPILED winMgrInit
   // NOT_DECOMPILED winMgrReInit
   // ... one line per function in the file, in address order ...

   }
   ```

2. In `configure.py`, change the file's `Object(NonStarted, "winmgr.c")` to `NonMatching`.
   It is now compiled (so objdiff can compare it) but not linked into `main.dol`.
3. Re-run `python configure.py` (objdiff also notices changes to `configure.py` and rebuilds).

### 5. Declarations go in spm-headers

- Function prototypes, structs and global variables live in `spm-headers/include/spm/<file>.h`
  (game code), with SDK/NW4R/MSL declarations in other folders there. `spm-headers` is a
  git-subrepo inside spm-decomp: edit its files normally, but never edit `spm-headers/.gitrepo`.
- Headers are shared between versions, so version differences are written with
  `#ifdef SPM_EU0`-style macros or version numbers such as `MEMORY_C_VERSION` (see `src/memory.c`).

### 6. Write a first draft

Pick whichever is easiest:

- **From the Thousand-Year Door decomp** (`../ttyd/src/...`, read-only clone): many SPM engine
  functions have a TTYD counterpart with the same name. Copy the logic, then adapt types and
  struct field names to spm-headers. TTYD's version may differ, and most of its files are
  themselves `NonMatching`, so treat it as a hint, not an answer.
- **By hand** from the assembly: work out arguments (`r3`, `r4`, ... and `f1`, ...), loads/stores
  (struct fields), calls (`bl`) and branches (if/loops).
- **m2c** (would need installing; ask first) for a mechanical first draft.

Replace the function's `// NOT_DECOMPILED` line with the C.

### 7. Iterate in objdiff until it says 100%

Save the file; objdiff rebuilds and shows the match %. Typical fixes, in rough order of
frequency: wrong types (signed/unsigned, `s16` vs `s32`, float vs double), the order of
statements or of variable declarations (changes register allocation), a temporary variable
the original used or didn't use, a missing `inline` helper, loops written as `for` vs `while`,
constants that should come from `.sdata2`. "Equivalent but not matching" is not done yet.

With `-inline all`, small static helpers get inlined; if the original calls a function that
doesn't exist in the symbol list, it was probably inlined from a helper you have to recreate.

### 8. When the function matches

1. Make sure the `// NOT_DECOMPILED` line for it is gone.
2. Format with clang-format (VS Code + clangd extension, or `clang-format -i src/<file>.c`).
3. Run `ninja`. The normal build still has to end with `build/EU0/ok`; your file isn't linked
   until it is `Matching`, so this checks you didn't break anything else.
4. `python configure.py progress` (or plain `ninja`, whose default target is `progress`)
   prints overall progress; `build/EU0/report.json` holds per-function match %.
5. Commit to your branch.

### 9. When the whole file matches

1. Every function and the file's data (`.data`, `.rodata`, `.sdata`, strings, ...) must match.
   objdiff shows data sections too.
2. Change the file to `Object(Matching, ...)` in `configure.py` and delete the WARNING comment.
3. `ninja` must still finish with `build/EU0/ok`: the rebuilt `main.dol` is now partly produced
   from your C and is still byte-identical.
4. Optionally check other versions: `python configure.py --version EU1` then `ninja`
   (`MatchingFor("EU0", "EU1")` marks files matching only in some versions).

## Rules that apply to this project

- Never commit `orig/` or `build/`. spm-decomp's `.gitignore` already excludes them, plus
  `*.dol`, `*.rel`, `*.elf`, `*.o`, `*.map`, `ctx.*` and `*.ctx`.
- **decomp.me**: the community uses it a lot, but a scratch contains the original function's
  compiled code, which is extracted from the disc. Under this project's rule ("never upload
  anything extracted from the disc") don't create scratches unless the user decides otherwise.
  objdiff works fully offline.
