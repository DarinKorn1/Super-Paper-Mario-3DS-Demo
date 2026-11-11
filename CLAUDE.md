# Super Paper Mario → New Nintendo 3DS XL

A personal project to port Super Paper Mario (Wii, 2007) to the New Nintendo 3DS XL.

## History so far

- **Route B, static recompilation (dropped).** `NewSuperPaperBros` (a WiiCompiled fork that
  translates the game's PowerPC code to C++) was examined, built and profiled on a PC.
  Findings, in `notes/route-b-feasibility.md` and `notes/gate1-measurements.md`:
  - it is 64-bit only (x86-64/AArch64, a 4 GiB guest address reservation, `#error` on other CPUs)
    and its renderer needs WebGPU (D3D12/Vulkan/Metal);
  - the translated game code is about 11.7x the size of the original (39.5 MiB of machine code);
  - even on a desktop Core Ultra 7, Flipside's game thread uses about 13 ms of CPU per 16.7 ms frame.
  Conclusion: too big and too slow for the 3DS's 32-bit ARM11.
- **Current route: matching decompilation.** Rewrite the game's code as C that compiles back to
  the identical binary, building on [spm-decomp](https://github.com/SeekyCt/spm-decomp), so it can
  later be recompiled natively for the 3DS.

## Folder layout

| Path | What it is | Tracked by this repo? |
|---|---|---|
| `CLAUDE.md`, `.gitignore` | this file, ignore rules | yes |
| `notes/` | reports and plans (`route-b-feasibility.md`, `gate1-measurements.md`, `decomp-workflow.md`, `pilot-functions.md`) | yes |
| `notes/gate1-scripts/` | analysis scripts and raw results from the Route B measurements | yes |
| `notes/user-path-backup.txt` | backup of the user PATH (personal paths) | **no**, ignored |
| `spm-decomp/` | the decompilation; its **own git repository** | no, ignored |
| `spm-decomp/orig/US0/` | the USA disc image and files extracted from it | never (ignored by spm-decomp too) |
| `spm-decomp/build/` | build output, including disassembly of the game | never (ignored) |
| `ttyd/` | read-only reference clone of the Thousand-Year Door decomp (doldecomp/ttyd, MIT) | no, ignored |
| `NewSuperPaperBros/` | Route B clone and PC build (about 3.8 GB) | no, ignored |

## Rules for every session

1. **The user is a beginner.** Explain each step and why, in plain words.
2. **Ask first** before installing, downloading or deleting anything (including tools that
   `configure.py`/`ninja` download, git clones, and `git` commands that discard work).
3. **Stop on errors.** Report the error and what it means; don't work around it without asking.
4. **Never commit or upload disc images or anything extracted from them.** That includes
   `orig/`, `build/` (disassembly, `.o`, `.dol`, `.rel`, extracted assets), and the game's
   assembly pasted anywhere online. Note: creating a decomp.me scratch uploads the function's
   original code, so ask the user before ever doing that.
5. Show the user new or changed docs before committing; commit only when asked.
6. Run Python that reads downloaded or extracted data with `python -I`; put temporary scripts
   outside the project.

## Current plan

1. Set up a **private GitHub repository** for the user's spm-decomp work, with SeekyCt's
   repository as the `upstream` remote (spm-decomp is CC0; `spm-headers` is MIT, its `mod/`
   part GPL-3.0).
2. Learn the workflow (`notes/decomp-workflow.md`): dtk splits the binary, the original
   Metrowerks compiler rebuilds our C, objdiff compares function by function.
3. **Pilot**: decompile the 30 functions in `notes/pilot-functions.md` (10 small, 10 medium,
   10 large, all in `main.dol`, most with a Thousand-Year Door counterpart) to measure how long
   matching takes and how hard it is.
4. **Waiting on:** a PAL disc dump. spm-decomp's main target is EU0 (EU1 shares its `main.dol`).
   Only the USA disc (US0) is here now; the project advises against putting work into US0.

## Useful facts

- Build: `python configure.py` (EU0 by default, `--version EU1` etc.), then `ninja`. The first
  build downloads the compilers, dtk, objdiff-cli and binutils into `spm-decomp/build/`.
- spm-decomp's last build here was US0 (`build/US0/`), from the Route B work.
- On this PC: Python (Windows Store build), ninja (winget), git, GitHub Desktop. No `gh` CLI.
- Game ID: USA `R8PE01`, PAL `R8PP01` (EU0 = revision 0, EU1 = revision 1).
