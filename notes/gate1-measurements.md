# Gate 1: PC port built from source, and measurements

Built on 2026-11-09 from `NewSuperPaperBros` (commit `1f961e7`, "v1.0.8") with the disc image in
`spm-decomp\orig\US0\` (Super Paper Mario USA, R8PE01 revision 0). The game was **not launched**: everything
below comes from the build, the generated files and the source code. Paths are relative to
`NewSuperPaperBros\` unless stated.

## 0. What was built, and how

| Item | Result |
|---|---|
| Build | **Succeeded.** `Play\engine_usa.dll` (61.56 MB) and `Play\SuperPaperMario.exe` (0.47 MB). |
| Translation quality | 0 unsupported instructions, 0 invalid-SSA functions (`wiicompiled\generated\base_translation_output.json`, `quality`). |
| Time (14 logical CPUs, 15.4 GB RAM, `-Jobs 8`) | translate 47 s, manifest + data-init + shards 7 s, configure 2 min 21 s, compile 14 min 22 s. About 17.5 min for `build-spm.ps1`; downloads and setup before it took about 25 more minutes. |
| Disc handling | The launcher opened the ISO read-only. SHA-256 before and after is identical (`A84D3777…434B`, 4,699,979,776 bytes, same last-write time). |
| Main program (DOL) | Extracted `sys\main.dol`: SHA-256 `0d7487bc…53b3` (the stock value in `tools\android\pipeline.py`), SHA-1 `4669c63d…a0c6` (matches `spm-decomp\config\US0\config.yml`). |
| Audio option | **Option 1, stock audio.** `game\main.dol` is the stock DOL; the one tracked-file edit is below. |

The edit to `wiicompiled\projects\spm\recomp.yml` line 22 (upstream pins the music-mod-patched DOL, which a stock disc doesn't have):

```diff
-    sha256: cd3b5662f61369d5ff946098033be69de8084a20b0dfd3c3d4f4819eed6d21ac  # HQ audio mod code patches at 0x802398D8, 0x80239C1C (original: game/main.dol.orig)
+    sha256: 0d7487bc387ee1e905be335acc1e25300eb28bb8949667f753f038dbd9cf53b3  # LOCAL EDIT: stock USA rev 0 DOL (stock audio). Upstream pins the HQ-audio-patched DOL cd3b5662…
```

Steps that differ from the README (the README leaves them out or runs more than needed):

1. Built the translator first (`dotnet build wiicompiled\translator\src\Translator.Cli\Translator.Cli.csproj -c Release`); `build-spm.ps1` needs it and the README never builds it.
2. Published only the Windows launcher (skipped the Linux Avalonia one).
3. Ran `Prepare-PortableTools.ps1` and `Prepare-Dependencies.ps1` myself, so archive hashes could be checked before compiling. `build-spm.ps1` then skipped them.
4. Redirected .NET, NuGet and temp folders into `toolchain\` with environment variables.

Disk used inside the project: `toolchain` 1,947 MB, downloaded archives 284 MB, `Dependencies` 239 MB, `native-build` 374 MB, `generated` 228 MB, extracted disc 384 MB, launcher outputs ~304 MB, `Play` 62 MB. About 3.8 GB in total.

Archive hashes: 10 of the 17 downloaded archives match a hash pinned in the repo (Dawn, fmt, FreeType, imgui, libpng, SQLite, tracy, xxHash, zlib, zstd). LLVM-MinGW, CMake and Ninja are checked by `Prepare-PortableTools.ps1` itself (it stops on a mismatch). **SDL 3.4.4, abseil, libusb and the C++/WinRT package have no hash pinned in the repo**, so they were not verified beyond HTTPS from the official release URLs.

## a. Size of the generated C++ and the compiled code

**Generated C++** (`wiicompiled\generated\`, git-ignored):

| Part | Files | Lines | Bytes |
|---|---|---|---|
| Translated game code, `build_shards\base_common\` (72 `.cpp` + 72 `.h`) | 144 | 3,988,224 | 107,711,386 (102.7 MiB) |
| Call dispatch + function registration (`base_dispatch`, `base_registration`) | 17 | 43,228 | 2,782,955 |
| Retro Rewind leftovers (`retro_rewind_*`), generated but **not compiled** | 17 | 43,228 | 2,782,963 |
| **Whole `generated\` folder** | 198 | 4,095,421 (text files only: 183 files) | 239,352,774 (228.3 MiB) |

The rest of the folder: `base_translation_sources.bin` 104.0 MB (a bundle of the same function sources), `data_sections_init_blobs` 7.9 MB (the game's initialised data), JSON metadata 7.9 MB, `guest_symbol_table.cpp` 0.38 MB. There are no per-function files (`--no-function-files`).

- **Functions:** 9,919 function definitions in `base_common` (`extern "C" void func_XXXXXXXX(CpuContext*)`).
- **Lines per function:** min 12, 25th percentile 69, median 167, mean 394, 75th percentile 381, 95th percentile 1,440, max 21,713 (`func_80C46E10`, in the relF module).
- **Expansion:** about 4.5 lines of C++ per original PowerPC instruction (3.99 M lines for 886,344 instructions).
- **Where the 10,181 translated functions went:** 9,863 are compiled from the translation (plus 56 interior entry points that get their own symbol, giving 9,919). **318 have no generated function** because the runtime replaces them with hand-written native code (312 are in `0x802xxxxx`: EXI, SI, `PPC*` CPU helpers, `__init_hardware`, `OSPanic`, `__memAlloc`, ...).

**Compiled code** (from the build's object files and the DLL, using `llvm-size`):

| Item | Size |
|---|---|
| 72 translated-game shard objects, `.text` | **41,463,017 bytes (39.54 MiB)**, holding 9,919 `func_` symbols |
| same objects, `.rdata` / `.xdata` (unwind) / `.pdata` | 0.58 / 0.47 / 0.18 MiB |
| `engine_usa.dll`, `.text` (translated game + runtime + Aurora) | 44,770,678 bytes (42.70 MiB) |
| `engine_usa.dll`, `.rdata` / `.data` | 12.6 MB / 3.4 MB |
| Original PowerPC code (spm-decomp US0 report) | 3,537,380 bytes |

So the translated game's machine code is about **11.7 times** the size of the original PowerPC code. The translator's own estimate is 2,336,886 IR instructions against 886,344 PowerPC instructions (2.6x).

## b. Examples of translated functions

All four show the original PowerPC (from `spm-decomp\build\US0\asm`) and the generated C++ (from `wiicompiled\generated\build_shards\base_common\`). Generated code keeps guest registers in local `uint32_t` variables, reads and writes guest memory through `MemoryInline::Flat*` helpers (byte-swapping), and finishes with a comment recording which registers it reads or writes. The size summaries are at the end of each function; some trailing comment lines are trimmed here.

**1. A typical tiny function: four instructions, a tail call** (`func_8001DE68`, 25 lines)

```
mr r4, r3 / li r3, 1 / lwz r4, 0xc(r4) / b fn_801A56B8
```

```cpp
extern "C" void func_8001DE68(CpuContext* MKW_RESTRICT ctx)
{
    uint32_t r3 = ctx->gpr[3];
    uint32_t r4 = ctx->gpr[4];
    goto loc_8001DE68;
loc_8001DE68:
{
    r4 = r3;
    r3 = 1;
    r4 = MemoryInline::FlatRead32((r4 + 12));
    ctx->gpr[3] = r3;
    ctx->gpr[4] = r4;
    MKW_STATIC_TRANSLATED_CALL(0x801A56B8u, func_801A56B8, ctx);   // direct call: a plain C++ call to another generated function
    r3 = ctx->gpr[3];
    r4 = ctx->gpr[4];
    ctx->gpr[3] = r3;
    ctx->gpr[4] = r4;
    return;
}
}
```

**2. A carry chain** (`func_80181930`, 10 PowerPC instructions become 48 lines): `subfc` / `subfe` use the XER carry bit, which the generated code rebuilds with 64-bit arithmetic.

```
subfc r3, r3, r5 / srwi r3, r5, 31 / subfe r3, r3, r4 / andc r3, r0, r3
```

```cpp
    r3_subfc_sub_0 = r3;
    r3 = (r5 - r3_subfc_sub_0);
    xer = (xer & 0xDFFFFFFFu) | ((static_cast<uint32_t>(r5) >= static_cast<uint32_t>(r3_subfc_sub_0) ? 1u : 0u) << 29);
    ...
    r3_ca_0 = (xer >> 29) & 1u;
    r3 = (r3_not_0 + r4);
    r3 = (r3 + r3_ca_0);
    {
        const uint64_t ppcCarryWide = static_cast<uint64_t>(static_cast<uint32_t>(r3_not_0)) + static_cast<uint64_t>(static_cast<uint32_t>(r4)) + (static_cast<uint64_t>(static_cast<uint32_t>(r3_ca_0)) & 1u);
        xer = (xer & 0xDFFFFFFFu) | (static_cast<uint32_t>((ppcCarryWide >> 32) & 1u) << 29);
    }
```

**3. Paired-single maths** (`func_80278958`, 43 lines): a two-lane dot product. Loads go through the quantisation registers (GQR), and every operation is a helper call.

```cpp
    [[maybe_unused]] uint32_t mkw_gqr0 = ctx->gqr[0];
    ...
    r3_psq_tmp_0 = (r3 + 4);
    PpcSetPairedFprInline(f2, PPC_PsqLGqrInline<0u, 0u>(ctx, mkw_gqr0, r3_psq_tmp_0));   // psq_l
    r4_psq_tmp_0 = (r4 + 4);
    PpcSetPairedFprInline(f3, PPC_PsqLGqrInline<0u, 0u>(ctx, mkw_gqr0, r4_psq_tmp_0));
    PpcSetPairedFprInline(f2, PPC_PsMulInline(f2.d, f3.d));                              // ps_mul
    PpcSetPairedFprInline(f5, PPC_PsqLGqrInline<0u, 0u>(ctx, mkw_gqr0, r3));
    PpcSetPairedFprInline(f4, PPC_PsqLGqrInline<0u, 0u>(ctx, mkw_gqr0, r4));
    PpcSetPairedFprInline(f3, PPC_PsMaddInline(f5.d, f4.d, f2.d));                       // ps_madd
    PpcSetPairedFprInline(f1, PPC_PsSum0Inline(f3.d, f2.d, f2.d));                       // ps_sum0
```

**4. An indirect jump** (`func_80253134`, 22 lines): `lwz r12, ...; mtctr r12; bctr`.

```cpp
    r12 = MemoryInline::FlatRead32((r13 + -32048));
    ctr = r12;
    ctx->gpr[12] = r12;
    ctx->ctr = ctr;
    InvokeIndirectJump(ctr, ctx);       // looks the address up in the runtime's dispatch tables
    return;
```

A typical bigger function (the median is 167 lines) additionally contains `goto loc_XXXXXXXX` blocks for each branch target, condition-register helpers such as `SetCRResident(cr, 0, ...)`, and code like `PpcRotl32Inline` for rotate instructions. Leaf functions are often **inlined** into callers (13,991 `// inline leaf 0x...` sites in the generated code).

## c. How the game's own memory heaps are configured

**What the game asks for.** Super Paper Mario's `memInit()` (`spm-decomp\src\memory.c` lines 150-277; table `size_table` lines 76-125; the USA rev 0 build uses `MEMORY_C_VERSION 1`, `spm-headers\include\spm\memory.h` lines 26-32) carves the system's memory arenas into nine expanding heaps. Fixed-size heaps are taken first, in order. Heaps marked "rest" then take 100% of what remains.

| Heap | Bank | Size |
|---|---|---|
| 0 `HEAP_MAIN` | MEM1 | 9,216 KB (9.00 MiB) |
| 1 `HEAP_MAP` | MEM1 | 6,144 KB (6.00 MiB) |
| 2 `HEAP_MEM1_UNUSED` | MEM1 | 256 KB |
| 3 `HEAP_EXT` | MEM1 | 256 KB |
| 4 `HEAP_EFFECT` | MEM1 | **rest of the MEM1 arena** |
| 5 `HEAP_WPAD` | MEM2 | 128 KB |
| 6 `HEAP_SOUND` | MEM2 | 17,408 KB (17.00 MiB) |
| 8 (unused) | MEM2 | 1 KB |
| 7 `HEAP_SMART` | MEM2 | **rest of the MEM2 arena** |

- **MEM1 (24 MiB physical):** fixed heaps total 15.50 MiB; the effect heap gets whatever is left of the arena. With the arena the runtime seeds (`0x80576720-0x817EF720`, 18.47 MiB, `system_bridge.cpp` lines 408-409) that is 2.97 MiB. **That seed looks wrong for this game**: the relF module is pinned at `0x80BF6840` plus 3.1 MB of image and bss (up to `0x80F1351C`), which would run past the end of a 9 MiB main heap starting at `0x80576720`. The seed values are leftovers from New Super Mario Bros. Wii (`system_bridge.cpp` comments), so the arena the SPM guest actually computes for itself is unknown (see section 7).
- **MEM2 (the runtime gives it 128 MiB):** the runtime derives the arena from the region size: `0x90000800 - 0x97DC0000` = 125.75 MiB (it reserves 128 KiB for IOS, 128 KiB for IPC and 2 MiB for the disc file table at the top, `system_bridge.cpp` lines 419-426, 476-497). The game then uses 17.13 MiB for fixed heaps and gives **all the rest, about 108.6 MiB, to the smart heap**.

| MEM2 size | Arena | Smart heap |
|---|---|---|
| 128 MiB (runtime today) | 125.75 MiB | 108.62 MiB |
| 64 MiB (retail Wii) | 61.75 MiB | 44.62 MiB |

(The 64 MiB row is arithmetic using the runtime's own reserved sizes, not a measurement.)

**What the game actually uses** can't be read from the source: the smart heap takes whatever it is offered, and how full it gets depends on the map. Host memory is only committed as pages are touched (section objects are demand-zero: "would fault in all 152 MiB at startup", `guest_flat_memory.cpp` line 613). Windows still counts the full section size against the commit limit.

**Could the 128 MiB bank be 64 MiB?** What the code shows:

- **One constant:** the size is `Memory::kMem2Size` (`runtime\include\memory.h` line 16). `system_bridge.cpp` derives the guest-visible MEM2 size, end and arena from the region size, so the game's own `memInit` would adapt by itself.
- **Console type:** `OSGetConsoleType` (`hle\os\os_init.cpp` lines 162-178) reports an **NDEV development console (`0x10000012`) for any MEM2 size other than exactly 64 MiB**, and a retail console (`0x12`) at 64 MiB. So at 64 MiB the game would see the same hardware type it shipped for. What SPM does differently on a dev console, if anything, is unknown.
- **Other users of the constant:** audio memory masks addresses with `kMem2Size - 1` (`hle\audio\ax_memory.cpp` line 136, fine for 64 MiB), save states copy `kMem2Size` bytes (`frontend_runtime.cpp` lines 436-508), and a mod-patch bounds check (`recomp_mod_loader.cpp` line 153).
- **Not tested.** The code review found nothing that forces 128 MiB, but only running the game would show whether any translated code or HLE assumes an address above `0x94000000`.

**Proposed way to measure real use** (not implemented): at the title screen and in a few maps, ask the runtime for the number of resident pages in the MEM1 and MEM2 host views (`QueryWorkingSetEx` on the section views), and read each heap's free size with the game's own `MEMGetAllocatableSizeForExpHeap` through `Memory::Read32` of `wp->heapHandle[]` (`kMemoryWp = 0x8056D188`, `spm_rel_pin.cpp` line 13).

## d. Existing profiling and per-frame timing, and a counting proposal

**What exists** (no instruction counter or function-call counter exists; `FunctionTranslator.cs` only counts PowerPC instructions at translation time):

1. **Frame timing, `NSMBW_LOG_FPS`** (`runtime\src\hle\vi.cpp` lines 956-1000). Every two seconds it logs frames presented and where each frame's time went: the game (guest code plus GX command building), `aurora_end_frame` (encode, submit, wait on the GPU) and pacing to the retrace, plus the worst frame time and a slow-frame count. A game share near the frame budget means CPU-bound; a large `end_frame` share means GPU-bound. Turn it on with an environment variable before launching: `$env:NSMBW_LOG_FPS = '1'`.
2. **Sampling profiler, `NSMBW_PROFILE=<start s>:<length s>`** (`runtime\src\guest_profiler.cpp`; Windows only). From `<start>` seconds after the first presented frame, for `<length>` seconds, it suspends the game thread about 1,000 times a second, records the instruction pointer, maps samples back to the **translated guest function** and logs the top entries with their guest address. It also writes `profile_stacks.txt` (current directory). Instead of the environment variable you can put `20:30` in a file `profile.txt` next to `SuperPaperMario.exe`. `tools\profile-resolve.py` summarises `profile_stacks.txt` by host function, but its `nm` path is hard-coded to `C:\msys64\mingw64\bin\nm.exe`, which doesn't exist here (`toolchain\llvm-mingw\bin\llvm-nm.exe` does); the profiler's own report already names guest functions.
3. **On-screen FPS counter:** F10 settings menu, "Show FPS" (`settings_overlay.cpp` line 1496).
4. **Other diagnostics:** `drawdump.txt`, `SPM_DRAW_LIMIT`, `SPM_CULL_TEST`, a map sweep tool (`tools\sweep-spm-maps.py`) and a per-scene log line `seq -> <logo|title|game|...>` written on every scene change.
5. **Where output goes:** `Play\UserData\Logs\<run folder>\console.log` (portable mode; `Play\portable.txt` is present).

**Proposal for counting calls and instructions per frame (not implemented):**

*Step 1, function calls per frame (smallest change).* Every translated call, direct, indirect or static, already goes through `ApplyRuntimeCallOptions(target, ctx)` (`runtime\include\abi_bridge.h` line 35; reached from the macro `MKW_STATIC_TRANSLATED_CALL` that the translator emits at `TranslatedBuildShardEmitter.cs` line 639, from `InvokeDirectCpu` line 556 and from `InvokeIndirectCpu` line 652). Under a new `#ifdef MKW_COUNT_CALLS`, add one indexed increment there: `g_callCount[(target - 0x80004000) >> 2]++` over a flat array covering the text range. Then, in `VI_HLE_PresentFrame` (`vi.cpp` line 978, which already keeps per-window `FrameTimes` and logs every two seconds under `NSMBW_LOG_FPS`), print calls per frame and the top 20 callee addresses (names from `kGuestMapSymbolNames`, as `guest_profiler.cpp` does) and clear the array.
Cost: a header edit plus about 20 lines in `vi.cpp`; because the header is included by every shard, it needs a full recompile (about 14 minutes). Limits: it counts calls, not instructions, and misses leaf functions the translator inlined.

*Step 2, instructions per frame (more accurate).* Have the code generator emit `MKW_COUNT_INSNS(n)` at each `loc_XXXXXXXX:` basic-block label, with `n` the block's PowerPC instruction count (the translator already computes instruction counts per function, `FunctionTranslator.cs` line 91). The macro adds to a thread-local counter that is flushed at the same per-frame hook. Cost: re-translate (47 s) plus full recompile; one add per basic block at run time. It counts executed guest instructions except inside the 318 natively replaced functions.

*No-code alternative:* the sampling profiler gives time per guest function (relative cost) and the static counts in section e give frequency of features; neither gives executed counts.

## e. PowerPC features that are costly to imitate

Two views. **Static** = the original game's PowerPC (disassembly from the earlier spm-decomp build: 10,183 functions, 886,344 instructions; script `notes\gate1-scripts\ppc_features.py`, full per-function lists in `ppc_features_us0.json`; functions in the relF module are listed by module-relative offsets, `fn_1_XXXX`). **Generated** = which runtime helpers appear in the translated C++ (`generated_helper_usage.json`). The two differ for paired singles because the translator inlines small leaf functions into their callers.

**Paired-single floating point**

| | Static (original code) | Generated C++ |
|---|---|---|
| Real paired-single work (`ps_*` arithmetic, or `psq_l/psq_st` on data) | **46 functions** (25 with `ps_*`: 309 instructions; 46 with `psq_*` on data: 474 instructions) | `PPC_PsMaddInline` in 305 functions, `PPC_PsMulInline` 307, `PPC_PsSum0Inline` 301, `PPC_PsqLGqrInline` (GQR-dependent loads) 386, `PPC_PsqStGqrInline` 210 |
| `psq_st` / `psq_l` on the stack (compiler saving callee-saved float registers in prologues/epilogues) | 1,425 functions, 10,008 instructions | `PPC_PsqStStackInline` 1,673 functions |

So paired singles are used for real in a small set of vector/matrix routines (mostly around `0x80277xxx-0x80278xxx`; top: `fn_80277A00` 39 `ps_*` + 14 `psq` in 62 instructions, `fn_80278764`, `fn_80277AF8`, `fn_80277934`, `fn_80277F18`, plus the OS FPU context routines `__OSLoadFPUContext`, `__OSSaveFPUContext`, `__OSFPRInit`). They reach ~300 callers in the generated code through inlining.

**64-bit integer maths** (PowerPC 32-bit has no 64-bit integer registers; 64-bit work is built from carry chains and high-multiply, so this counts those):

| Pattern | Functions | Instructions |
|---|---|---|
| Carry chains (`addc/adde/addze/addme/subfc/subfe/subfze/subfme`) | 225 | 985 |
| High multiply (`mulhw`, `mulhwu`) | 333 | 729 |
| Calls to the compiler's 64-bit helpers (`__div2u` 19 call sites, `__mod2u` 2) | 17 | 21 |
| **Any of the above** | **493** | |

The functions with the most carry instructions: `fn_80053F68` (54), `fn_80282970` (40), `InsertAlarm` (31, OS timer code), `fn_802825BC` and `fn_8017851C` (25 each); the 64-bit division helpers are called from `fn_8025DC44`, `longlong2str_80258D30`, `fn_801A5194` and 14 others. The generated code handles carries with `uint64_t` widening (example 2 above), and I don't have a reliable count of functions using it (the marker counts in the generated code were contaminated by neighbouring declarations and discarded).

**Indirect jumps and calls**

| Pattern | Static (original) | Generated C++ |
|---|---|---|
| Indirect **calls** (`bctrl`, `blrl`) | 601 functions, 1,403 instructions | `InvokeIndirectCpu`: 594 functions, 1,397 uses |
| Jump tables (`lwzx` + `mtctr` + `bctr`) | 240 functions, 279 instructions | `switch` in 230 functions (268 switches) |
| Other indirect jumps (`bctr` tail calls and similar) | 53 functions, 54 instructions | `InvokeIndirectJump`: 285 functions, 324 uses (includes some jump-table sites) |

Functions with the most indirect calls: `fn_8030063C` and `fn_8025C420` (34 each), `fn_8030F1CC` and `fn_80314798` (27 each), `fn_8030DDA0` (23). How an indirect call runs (`abi_bridge.h` lines 314-378): a 512-entry (12 KiB) direct-mapped **thread-local memo** keyed by the guest address, in front of a sorted-registry binary search; a miss re-runs the search.

## 6. How to run it (you run it; I did not launch it)

`Play\SuperPaperMario.exe` is a small loader that starts `engine_usa.dll`. `Play\portable.txt` makes it keep settings, saves and logs in `Play\UserData\`.

1. Open PowerShell and start it from its own folder (optionally with frame timing on):

```powershell
cd C:\Users\ender\SPM_N3DS_XL\NewSuperPaperBros\Play
```

```powershell
$env:NSMBW_LOG_FPS = '1'; .\SuperPaperMario.exe
```

2. **First start:** it finds no game folder (`game_folder.cpp` lines 245-310), shows a message with OK / Cancel, and asks you to pick a disc image. Pick `C:\Users\ender\SPM_N3DS_XL\spm-decomp\orig\US0\Super Paper Mario (USA).iso` (it only reads it). It unpacks the files into `Play\Disc\DATA` (about 0.4 GB, took 10 s for the launcher) and restarts into the game. If you'd rather reuse the files already extracted at `NewSuperPaperBros\Disc\DATA`, a folder named `Play\game` pointing at them is picked up without questions (one command: `cmd /c mklink /J "<Play>\game" "<project>\Disc\DATA"`; say if you want me to run it).
3. **Title screen check, on screen:** Nintendo/logo screens, then the Super Paper Mario title screen. F10 opens the settings menu, F11 toggles fullscreen; "Show FPS" is in the F10 menu.
4. **Title screen check, in the log** (`Play\UserData\Logs\<newest folder>\console.log`), look for:
   - `seq -> title` (then `seq -> game` once you start a game) from `vi.cpp` `LogSceneChanges`;
   - `REL module 1 (relF) linked at image 0x80BF6840 bss 0x........: MATCH` (see section 7, item 3: it may say MISMATCH);
   - `[relpin] relF block padded to 0x80BF6840 (pinned)` or a `FAILED` line;
   - `OSGetConsoleType: MEM2=128 MB, returning 0x10000012` and `MEM2 defaults active -> size=128 MB, arena ...`;
   - with `NSMBW_LOG_FPS` on, a line every two seconds with the per-frame time split.
5. Requirements met on this machine: CPU Intel Core Ultra 7 155U (AVX2 present, which the build requires), Windows 11. The graphics adapter is "Intel Graphics"; the repo's stated minimum is a GTX 1650 / RX 6400 / Arc A310 class GPU, so a window that fails to open or a very low frame rate would point there.

## 7. Could not determine

1. **Whether the game runs and reaches the title screen**: not launched, as instructed. Section 6 is how to check.
2. **Stock audio on Windows is untested upstream.** The Android pipeline uses the stock DOL with the same translator and function map, but the Windows build normally uses the music-mod-patched DOL. Music pitch or speed with the stock DOL is unverified.
3. **REL bss address.** The README's `prelink_spm_rel.py` command (default arguments) put relF's bss at `0x80F12660`; `vi.cpp` line 573 and the `recomp.yml` comment both expect `0x80F12640`. By my reading of the expanding-heap allocator it should be `...640`, so the script default may be 0x20 too high. Every caller in the repo uses the default and it all landed in one upstream commit, so I can't tell which is right. The `REL module 1 ... MATCH/MISMATCH` log line will say. I did not change it.
4. **The arena the game actually sees.** The runtime seeds New Super Mario Bros. Wii constants (`system_bridge.cpp` lines 408-419) and forces them into the low-memory globals; whether SPM's own OS start-up code overwrites the MEM1 values is not visible in the source. So the effect-heap size, and the exact smart-heap size, are derived, not observed.
5. **How much of each heap the game really uses**, peak or at the title screen, and the process's real RAM use. Not measured (section c proposes how).
6. **Whether MEM2 can be 64 MiB.** Reasoned from the code only; nothing was built or run with that change, and what a dev-console type (`0x10000012`) changes in SPM is unknown.
7. **Performance**: no frame times, CPU or GPU load, and no check that the Intel integrated GPU is adequate. No dynamic (executed) counts of paired-single, 64-bit or indirect operations, only static counts and generated-code helper use.
8. **Compile resource use**: peak memory and whether `-Jobs 8` was best. Free RAM dropped to about 3 GB during compilation.
9. **Small count differences I did not chase**: 10,183 `.fn` entries in the disassembly against 10,182 map entries; the generated-code marker counts for 64-bit work (discarded as unreliable); `InvokeIndirectJump` (324 uses) against the static `bctr` count (333).
10. **Hashes for SDL, abseil, libusb and C++/WinRT** (no pin in the repo), and the third-party origin of the Dawn build (a GitHub account that is not Google; its hash does match the repo's pin).
11. **Not examined:** the Retro Rewind shards (generated, not compiled), the PAL build (`-Pal`), and whether the HQ music mod could be obtained and used (option 3).

## Side effects on this machine outside the project folder

- The .NET SDK's first-run setup added `...\toolchain\dotnet-home\.dotnet\tools` to your **user PATH**. I removed that one entry at your request; the previous value is saved in `notes\user-path-backup.txt`. (`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH=false` is now set for later build commands.)
- NuGet created an empty marker folder `%LOCALAPPDATA%\NuGet\Migrations\1`. I left it; it is harmless and NuGet recreates it.
- Early on, my size-check requests accidentally downloaded six small GitHub archives into a stray file `NewSuperPaperBros\NUL`; I deleted it at your request.
- Nothing else was found outside the project folder (no `.nuget`, `.dotnet` or other registry changes).

## Reproducing the numbers

`notes\gate1-scripts\` holds the scripts and raw results: `ppc_features.py` (static scan), `gen_stats.py` (generated-code size and function sizes), `gen_tokens.py` (helpers used by the generated code), `obj_sizes.py` (compiled sizes), `find_examples.py` and `extract_func.py` (examples). Run them with `python -I`.
