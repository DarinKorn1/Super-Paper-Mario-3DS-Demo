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

- **MEM1 (24 MiB physical):** fixed heaps total 15.50 MiB; the effect heap gets whatever is left of the arena. With the arena the runtime seeds (`0x80576720-0x817EF720`, 18.47 MiB, `system_bridge.cpp` lines 408-409) that is 2.97 MiB. **The game's own start-up report (section 9.4) prints exactly this arena, so these are the values it sees** (they are New Super Mario Bros. Wii constants reused by the runtime). If the main heap began at the arena start it would end at `0x80E76720`, yet the relF module (`0x80BF6840` plus 3.1 MB, up to `0x80F1351C`) is allocated from it, so the arena's low end must have moved up by at least about 0.6 MiB before `memInit` ran (probably an earlier allocation such as a GX FIFO). That is an inference, not an observation; it makes the effect heap at most about 2.4 MiB instead of 2.97 MiB.
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
3. **relF bss address: now a measured mismatch, effect unknown** (updated after the first run, section 9.2). The game's own loader put relF's bss at `0x80F12640`; the README's `prelink_spm_rel.py` command (default arguments) put it at `0x80F12660` in `game\spm_rel_layout.json`, which the translation was linked against. I did not change it.
4. **The arena the game sees: now observed** (section 9.4: the game's own `MEM1 Arena` / `MEM2 Arena` lines). What is still inferred is how far the MEM1 arena's low end moved before `memInit` ran, so the exact MEM1 effect-heap size.
5. **How much of each heap the game really uses**, peak or at the title screen, and the process's real RAM use. Not measured (section c proposes how).
6. **Whether MEM2 can be 64 MiB.** Reasoned from the code only; nothing was built or run with that change, and what a dev-console type (`0x10000012`) changes in SPM is unknown.
7. **Performance**: no frame times, CPU or GPU load, and no check that the Intel integrated GPU is adequate. No dynamic (executed) counts of paired-single, 64-bit or indirect operations, only static counts and generated-code helper use.
8. **Compile resource use**: peak memory and whether `-Jobs 8` was best. Free RAM dropped to about 3 GB during compilation.
9. **Small count differences I did not chase**: 10,183 `.fn` entries in the disassembly against 10,182 map entries; the generated-code marker counts for 64-bit work (discarded as unreliable); `InvokeIndirectJump` (324 uses) against the static `bctr` count (333).
10. **Hashes for SDL, abseil, libusb and C++/WinRT** (no pin in the repo), and the third-party origin of the Dawn build (a GitHub account that is not Google; its hash does match the repo's pin).
11. **Not examined:** the Retro Rewind shards (generated, not compiled), the PAL build (`-Pal`), and whether the HQ music mod could be obtained and used (option 3).

## 8. Files the build leaves out of `Play\` (found while trying to start the game)

`build-spm.ps1` copies only `SuperPaperMario.exe` and `engine_usa.dll` into `Play\`. The release packager `tools\package-spm.ps1` (lines 32-72) adds the rest next to the exe. First launches failed on missing DLLs and then on `dsp_coef.bin` (`runtime\src\hle\audio\ax_mix.cpp` lines 34-55 looks in the exe's folder, then upwards from the current directory for `runtime\assets\dsp\dsp_coef.bin`, and otherwise throws "Missing bundled Wii DSP coefficient ROM"). Copied into `Play\`:

| Files | Copied from | Notes |
|---|---|---|
| `libc++.dll`, `libunwind.dll` | `toolchain\llvm-mingw\x86_64-w64-mingw32\bin\` | byte-identical to the copies in `native-build\` |
| `libz.dll`, `libpng16.dll`, `SDL3.dll`, `webgpu_dawn.dll` | `wiicompiled\native-build\` | imported by `engine_usa.dll` |
| `dxcompiler.dll`, `dxil.dll` | `wiicompiled\native-build\` | loaded on demand by Dawn for Direct3D 12 |
| `dsp_coef.bin` (4,096 bytes) | `wiicompiled\native-build\` (the build copies it from `runtime\assets\dsp\`) | SHA-256 `D7741279…8179`, equal to the value pinned in `THIRD-PARTY-NOTICES.md` |
| `initial_pipeline_cache.db` (4.6 MB) | `wiicompiled\native-build\` | identical to `runtime\assets\pipeline\`; merged into the user's shader pipeline cache at start (`main.cpp` lines 1561-1568) |
| `wii_bootstrap\` (12 files) | `wiicompiled\native-build\wii_bootstrap\` | same files as `runtime\assets\wii\`; seeds the virtual Wii NAND (`nand_path.h` lines 133-154) |
| `msvcp140.dll`, `msvcp140_atomic_wait.dll`, `vcruntime140.dll`, `vcruntime140_1.dll` | `C:\Windows\System32\` (version 14.51.36247.0) | the packager ships these app-local; this PC already has them, so they only matter on a PC without the VC++ Redistributable |
| `UserData\mods\` (empty) | created | the packager creates it |
| `game\` (junction) | -> `Disc\DATA` | created with `New-Item -ItemType Junction`; the game uses a `game` folder next to the exe without asking (`game_folder.cpp` lines 247-258) |

**Not found in the repo, so taken from the installed release instead** (a copy of the released port at `C:\Users\ender\Downloads\NewSuperPaperBros\NewSuperPaperBros\engine\`, which was only read). Every copied file was checked identical to its source; nothing in `Play\` was overwritten:

| Files | Copied to | Notes |
|---|---|---|
| `startup\*.png` (9 files, 0.9 MB) | `Play\startup\` | The cover-screen sprites `bowser`, `luigi`, `mario`, `peach`, `pixl`, `sparkle`, `tippi` (`settings_overlay.cpp` lines 1658-1673) plus `button2` and `merlon`. Nintendo character art, not tracked in the repo; the dev tree's `Play\startup` is git-ignored. |
| `UserData\button_icons\` (91 files, 1.9 MB) | `Play\UserData\button_icons\` | Controller pictures for the xbox, playstation and nintendo styles. `tools\make-button-icons.py` generates them but needs Python's Pillow, ImageMagick and the HD texture pack's artwork, so the repo alone cannot rebuild them. The Controls screen uses them. |

**Offered from the release but not copied (your choice):**

- `UserData\texture_replacements\SPM_HD_4x_BC3` (1,910 files, 696.6 MB): the third-party HD texture pack (optional, visuals only).
- `game_files\sound\` (115 files, 187.7 MB): the third-party HQ music mod. The release's `engine_usa.dll` is built from the music-patched game program and ours from the stock one, so these files probably play at the wrong pitch or speed with our build.

Also noted in that release folder: its `engine_usa.dll`, `libz.dll`, `libpng16.dll` and `SDL3.dll` differ from ours (kept ours); the other 11 same-named files checked are byte-identical; two stray files in its `engine\` have corrupted names.

**Deliberately not created:** `version.txt`. The built-in updater (`updater.cpp` lines 205-213) treats a missing `version.txt` as a development build and never checks GitHub. `engine_pal.dll` (the PAL build, not built) and `cacert.pem` (Windows uses Schannel) are not needed.

## 9. First profiled run, started Flipside (2026-11-09)

Source: `Play\UserData\Logs\base_1794289813_pid14108\console.log` (2,052 lines) and `Play\profile_stacks.txt` (20,000 samples, written 54 s after the run started, so the same run). The run lasted more than 15,300 presented guest frames. Settings in the log: 1920x1094 window, Direct3D 12 on "Intel(R) Graphics" (integrated; the log also lists "Microsoft Basic Render Driver"), game thread on the 4 performance cores of the 14 threads, `texture_replacements` on but 0 replacements indexed (no HD pack installed), stock audio. Scripts and raw summaries are in `notes\gate1-scripts\` (`run1-*.txt`).

### 9.1 Title screen: reached

Sequence lines (`seq -> ...`, frame number in brackets): logo (1), intro book via `mapchange`/`game` (417-473), **title screen first shown at frame 495**, the intro and title again at 2,477, file select `load` (2,526), then the first in-game map at frame 2,785. Maps loaded, in order: `aa4_01`, `aa1_01`, `mac_01`, `mac_02`, `mac_06`, `mac_05`, `mac_12`; `[spmwarp] mac_01 A2d_dokan_1`; a save ("save anywhere: saved"). The last scene change in the log is at frame 15,300.

### 9.2 relF module line

```
[os] REL module 1 (relF) linked at image 0x80BF6840 bss 0x80F12640: MATCH
```

MATCH is against the runtime's own constants (`vi.cpp` line 573). It also shows that the game's real bss is `0x80F12640`, whereas our translation was linked for `0x80F12660` (`game\spm_rel_layout.json`, from the README's prelink command). The translated relF code has 22 direct references (7 distinct addresses, `0x80F127A8` to `0x80F131B8`) built from the `...660` base, so they point 0x20 bytes past the variables the game's own relocations use. The game ran 15,000+ frames without a visible fault, so the effect, if any, is unknown. Re-running `prelink_spm_rel.py` with `0x80F12640` as the bss argument and re-translating (about 17 min of build time) would remove the difference; not done.

### 9.3 Frame timing (`NSMBW_LOG_FPS`, 200 two-second windows)

All windows: fps median 46.9 (min 10.3, max 92.3); `game` median 21.2 ms (mean 24.1); `gx` median 5.3 ms; `end_frame` median 0.11 ms (mean 0.18, max 1.77); `pace` median 0.0 ms; **worst frame** median 38.8 ms (max 603.1 ms); "over 20 ms" median 30 frames per window; 37 of 200 windows were at 59 fps or more. Split by game phase (the phase is the last `seq ->` line before each window, so a window that spans a change is credited to the earlier phase):

| Phase | Windows | fps median (min-max) | game ms | gx ms | draws per frame | end_frame ms | worst frame median / max |
|---|---|---|---|---|---|---|---|
| logo | 3 | 58.1 (41.8-60.0) | 16.96 | 0.26 | 5 | 0.24 | 76.3 / 419.1 |
| title | 16 | 60.0 (51.9-60.1) | 16.66 | 0.18 | 27 | 0.05 | 23.4 / 102.3 |
| load (file select) | 1 | 74.3 | 13.45 | 0.64 | 303 | 0.01 | 66.5 / 66.5 |
| mapchange | 8 | 38.1 (10.3-50.2) | 26.72 | 5.15 | 2,462 | 0.18 | 122.7 / 603.1 |
| **game (Flipside and the other maps)** | 172 | **46.1** (12.4-92.3) | **21.47** | 5.38 | **3,364** | 0.11 | **39.0 / 495.1** |

(Windows above 60 fps are probably catch-up after a stall; I did not check.) `end_frame` stays near 0.1 ms in every phase, so by this metric the time is not in submitting frames. The renderer also logged 196 "Slow render frame" lines (a rate-limited sample: at most 30 a minute, only when the frame worker was busy 16.7 ms or more): total median 20.7 ms (max 191.2), of which seal 0.1, encode median 2.5 (max 34.3), publish 0.0, **"prepare next" median 17.5 ms (max 187.5)**. What the frame worker's "prepare next" step does was not examined.

### 9.4 Heap usage

**Peak usage of the game heaps is not exposed**: the log has no heap statistics and the runtime has no heap counter (sections c and d describe how to measure it). What the game itself printed at start-up:

```
[OSReport] Console Type : NDEV 1.2
[OSReport] Memory 152 MB
[OSReport] MEM1 Arena : 0x80576720 - 0x817ef720
[OSReport] MEM2 Arena : 0x90000800 - 0x97dc0000
```

So the game believes it runs on a development console with 152 MB (24 + 128). Using `memInit` (section c) on those arenas: **MEM2 smart heap 108.62 MiB** (arena 125.75 MiB minus 17.13 MiB of fixed heaps); MEM1 fixed heaps 15.5 MiB plus the effect heap, at most 2.4 MiB. Host side, the log shows `[dvd] read cache: 2630 file(s), 383 MiB in 20018 ms`: the runtime reads the whole disc (383 MiB) into host memory, which took 20 s from start-up.

### 9.5 Profile

The profiler window ran from 30 s to 50 s after the first presented frame, which was **mostly the title screen, file select and loading, with only the first seconds of Flipside** (the fps windows in that span are title 16.7 ms/frame at 27 draws, then the load and the first map). It does not describe Flipside gameplay, where the fps lines show 46 fps (section 9.3). Only the game thread is sampled (not the audio mix worker, the renderer's frame worker or the GPU driver threads).

The log's own `profile:` list names runtime code after the nearest translated function in memory (it reports the idle wait as "NANDDelete < SelectThread < OSSleepThread"), so I re-resolved the raw samples against the DLL's own symbols (`llvm-nm`, 28,484 text symbols): the log's "[ntdll.dll] 75.9%" matches my 78.7% for all system DLLs together. Guest names below come from `projects\spm\MAP.txt`; `spm-decomp` calls those addresses `fn_802881C0`, `fn_801A1B28` and `fn_802874F8`, so treat the three names as hints.

**Top 20 by time in the function itself plus OS calls it makes directly** (share of the 20,000 samples):

| # | Share | Function |
|---|---|---|
| 1 | 61.13% | `SleepPreciselyUntil` (pacing sleep; 58.4% from `OS__ReceiveMessage` -> `OSSleepThread` -> `SelectThreadSwitch`, 2.8% from `VIWaitForRetrace`) |
| 2 | 11.19% | `condition_variable::wait_until`, all from `GXDrawDone` -> `aurora::gx::fifo::drain` -> `wait_for_frame_worker_sealed` (waiting for the renderer's frame worker) |
| 3 | 3.06% | translated `func_802881C0` (MAP name `AXFXReverbHiExpCallback`) |
| 4 | 2.15% | `AxDspHle::AXWii::JoinMix()` (waiting for the audio mix worker) |
| 5 | 1.18% | `aurora::gx::fifo::process` |
| 6 | 0.51% | `GXSetVtxDesc` |
| 7 | 0.50% | `ModHooks::Run` (the per-call hook check) |
| 8 | 0.47% | `GX__CallDisplayList_80172f64` |
| 9 | 0.45% | `aurora::window::poll_events()` |
| 10 | 0.42% | `HleFifoWrite` |
| 11 | 0.38% | translated `func_801A1B28` (MAP name `HSV2RGB`) |
| 12 | 0.34% | `Fiber::GuestFiberManager::SwitchToThread` |
| 13 | 0.34% | `aurora::gfx::texture_replacement::take_button_icon_style_change()` |
| 14 | 0.32% | translated `func_802874F8` (MAP name `__AXSyncPBs`) |
| 15 | 0.28% | `TryDispatchRawCpuTarget` |
| 16 | 0.26% | `aurora::webgpu::create_copy_bind_group` |
| 17 | 0.24% | `AxDspHle::SendMailToDSP` |
| 18 | 0.23% | `aurora::gx::fifo::gx_vertex_ndc` |
| 19 | 0.20% | `InvokeIndirectCpu` |
| 20 | 0.19% | `aurora::gx::fifo::resolve_pipeline_state` |

Rows 1, 2 and 4 are waiting, not computing: **78.7% of all samples had the instruction pointer inside a system DLL** (waiting in the OS), 21.3% inside `engine_usa.dll`.

**Split between translated game code and runtime code:**

| | Share of all samples | Share of the 21.3% that is running |
|---|---|---|
| Waiting in the OS | 78.7% (pacing sleep 61.1%, frame-worker wait 11.2%, audio-mix join 2.1%, other 4.3%) | - |
| Translated game code | 9.9% (3.06% of it in `func_802881C0`) | 46.5% |
| Graphics (GX layer, aurora, Dawn glue) | 4.8% | 22.5% |
| Other runtime (call dispatch, hooks, FIFO writes, hashing) | 5.2% | 24.4% |
| Scheduler / fibers / OS emulation | 0.9% | 4.2% |
| Audio (AX/DSP) | 0.3% | 1.4% |
| Memory slow path | 0.1% | 0.5% |
| Disc / save I/O | 0.1% | 0.5% |

For the main thread, in this mostly-idle window, the game is not CPU-bound: it spends about 72% of its time asleep or waiting for the renderer (pacing sleep plus frame-worker wait) and another 2% waiting for the audio mixer, and 15% of samples (inclusive) sit under `GXDrawDone` waiting for the frame worker. Audio mixing runs on a worker thread, so almost none of it appears here.

**For a useful Flipside profile**, start the sampler after you are walking around in Flipside. The clock starts at the first presented frame, and the game reached its first map at about 48 s in this run, so something like `$env:NSMBW_PROFILE = '90:20'` samples seconds 90-110.

### 9.6 Could not determine from this run

1. Peak (or any) usage of each game heap, including the MEM2 smart heap: not logged and not exposed by the runtime.
2. Where Flipside's 21.5 ms per frame goes: the profile window did not cover gameplay, and only one thread was sampled.
3. Whether the game is limited by the CPU or the GPU in Flipside on this machine (hybrid CPU, integrated graphics): `end_frame` is tiny, but the frame worker's "prepare next" (median 17.5 ms in logged slow frames) was not decomposed, and the log lines are a rate-limited sample.
4. The effect of the relF bss mismatch (section 9.2) on play.
5. The exact MEM1 effect-heap size (the arena's low end moved before `memInit`; section c).
6. Host process memory use: not in the log (only the 383 MiB disc cache preload).
7. Two log lines I can't explain: `[vi] [watchdog] nothing visible yet; guest threads:` printed at 30 s although 1,664 frames had been presented and `VI black=0`, and the repeated alternation of `Present mode Mailbox (V-Sync on)` and `Immediate (V-Sync off)`. Also `[nand] NANDOpen: FAILED ... /shared2/sys/SYSCONF` (a missing console settings file; the game carried on) and `OSLoadFont: no console ROM font available` at start-up.
8. Whether the MAP names for the hot translated functions are right (see 9.5).

## Side effects on this machine outside the project folder

- The .NET SDK's first-run setup added `...\toolchain\dotnet-home\.dotnet\tools` to your **user PATH**. I removed that one entry at your request; the previous value is saved in `notes\user-path-backup.txt`. (`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH=false` is now set for later build commands.)
- NuGet created an empty marker folder `%LOCALAPPDATA%\NuGet\Migrations\1`. I left it; it is harmless and NuGet recreates it.
- Early on, my size-check requests accidentally downloaded six small GitHub archives into a stray file `NewSuperPaperBros\NUL`; I deleted it at your request.
- Nothing else was found outside the project folder (no `.nuget`, `.dotnet` or other registry changes).

## Reproducing the numbers

`notes\gate1-scripts\` holds the scripts and raw results: `ppc_features.py` (static scan), `gen_stats.py` (generated-code size and function sizes), `gen_tokens.py` (helpers used by the generated code), `obj_sizes.py` (compiled sizes), `find_examples.py` and `extract_func.py` (examples). For the first run (section 9): `log_summary.py` and `phase_summary.py` (fps windows, phases, heap and OSReport lines), `profile_resolve.py` and `profile_top20.py` (raw samples resolved against the DLL's symbols), `bss_check.py` (relF bss references); their outputs are the `run1-*.txt` files. Run the scripts with `python -I`.
