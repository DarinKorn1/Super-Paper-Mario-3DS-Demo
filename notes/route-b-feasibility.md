# Route B: NewSuperPaperBros (static recompilation) — fact-finding report

Source examined: <https://github.com/josiahg2502-glitch/NewSuperPaperBros>, cloned on 2026-11-09 at
commit `1f961e7` ("v1.0.8") into `NewSuperPaperBros/`. Nothing was built, run or downloaded
beyond the clone (no submodules, no Git LFS). All paths below are relative to `NewSuperPaperBros/`.

This report gives facts only. It doesn't judge whether a 3DS port is possible.

## Overview

- The project calls itself a native port of Super Paper Mario made by statically recompiling
  the game's PowerPC code to C++ with WiiCompiled, "No emulator" (`README.md`, lines 3-5).
- It is a fork of **WiiCompiled**, a Mario Kart Wii recompiler (`wiicompiled/docs/WiiCompiled-README.md`),
  adapted for Super Paper Mario. Much of the runtime still uses Mario Kart Wii (`MKW_…`) and
  New Super Mario Bros. Wii (NSMBW) names and comments. For example, `runtime/src/hle/storage/nand_internal.h:44`
  calls title ID `52385045` "NSMBW (SMNE01)", but `0x52385045` is ASCII `R8PE`, Super Paper Mario's USA code.
- Supported disc: USA `R8PE01` revision 0 (also EU `R8PP01` on desktop). Android and macOS are USA only
  (`README.md` line 31, `wiicompiled/docs/android-and-macos.md` lines 3-5).
- **The repository contains no translated game code.** The C++ is produced on the builder's machine
  from their own `main.dol` and `relF.bin` (`README.md` lines 66-76; output goes to `wiicompiled/generated/`).
  There are no generated sources to inspect.
- The USA manifest pins a **modified** `main.dol`: it includes two code patches from the HQ music mod
  (`wiicompiled/projects/spm/recomp.yml` line 22). The Android pipeline writes a separate
  `game/android-stock.yml` for stock audio (`docs/android-and-macos.md` line 28).

## a. What the recompiled code looks like

**Pipeline.** The translator is a C# (.NET 8) program. It parses the DOL, decodes PowerPC,
lifts to IR/SSA, runs type inference and emits C++. That C++ is compiled together with
`runtime/` into one executable (`wiicompiled/translator/README.md` lines 3-6, 14-26). Source
folders: `translator/src/Translator.Core/{Disassembly,Lifting,Ir,Analysis/Ssa,CodeGen}/`.

**One C++ function per original function: yes.** Discovery walks the call graph from the entry
point (`0x80006124`, `projects/spm/recomp.yml` line 31). Function boundaries are seeded from a
symbol map (`translator/README.md` lines 28-30):

- `projects/spm/MAP.txt`: 10,182 entries, one `address name` line each (e.g. `80004000 memcpy`).
- `projects/spm/MAP_rel.txt`: 1,031 entries for the `relF` module.

These counts are exactly the "10182 functions" and "1031 functions" spm-decomp's US0 build reported.
The emitted functions are declared `extern "C" void <name>(CpuContext* ctx);`
(`translator/src/Translator.Core/CodeGen/CxxLinearCodeGenerator.cs` line 193). Names combine the
symbol and its address, e.g. `GX__ClearVtxDesc_8016dc34` (`runtime/src/hle/gx/gx_vertex.cpp`).

**Unsupported instructions.** Translation fails on an unsupported instruction by default. An opt-in
mode emits runtime traps instead (`translator/README.md` lines 30, 57-58). Privileged or unmodelled
instructions end in `UNDEFINED(...)`, which aborts (`runtime/include/isa/ppc_isa_context.h` lines 122-139).

**PowerPC registers.**

- They live in a C++ struct, `CpuContext` (`runtime/include/isa/ppc_isa_context.h` lines 27-54):
  `uint32_t gpr[32]`; `cr`, `lr`, `ctr`, `xer`, `fpscr`, `pc`; 32 FPRs as a 64-bit union that also
  holds the two paired-single floats; 8 GQRs; `hid0-2`, `srr0/1` and `msr`.
- Generated code writes registers through `ctx` (`CxxLinearCodeGenerator.cs`, class summary). It
  marks `ctx` as `__restrict` so hot registers can stay in host registers
  (`CxxLinearCodeGenerator.cs` lines 22-24).
- A "state-free ABI" rewrite can pass registers as values instead
  (`CodeGen/CxxLinearCodeGenerator.StateFreeAbi.cs`; `runtime/include/isa/ppc_isa_config.h`
  lines 15-18, 38).
- Condition-register bits are set by helpers such as `SetCR` and `SetCRFloat`
  (`ppc_isa_context.h` lines 141-188).
- Paired-single and quantised load/store helpers are in `runtime/include/isa/ppc_isa_quantized.h`
  and `runtime/src/ppc_quantized.cpp`.
- FPU behaviour is mapped to the host's floating-point control register (x86 MXCSR or the AArch64
  equivalent) in `runtime/include/isa/ppc_isa_fpenv.h`.

**Indirect calls** (through `ctr`/`lr`) go to `InvokeIndirectCpu(target, ctx)`, which looks the
address up in static dispatch tables (`runtime/include/abi_bridge.h` lines 23, 108-154, 433-467;
emitted at `CodeGen/CxxLinearCodeGenerator.EmitInstruction.cs` line 422).

**Big-endian memory.**

- Memory is kept in the Wii's big-endian byte order. Every multi-byte access is byte-swapped by
  `MemoryInline::MaybeByteSwap`, which uses `__builtin_bswap16/32/64`
  (`runtime/include/memory_access.h` lines 249-270; `runtime/src/memory.cpp` lines 450-477).
- The translator emits one of two helper families
  (`CodeGen/CxxLinearCodeGenerator.FlatGuestMemory.cs`, summary):
  - **"Flat" helpers:** host pointer = fixed base + guest address, then a byte swap.
  - **"Checked" helpers:** go through a page table with 1 MiB pages (`memory_access.h` line 31,
    `kPageShift = 20`).

## b. How Wii memory is modelled, and host RAM

**The guest memory map** (`runtime/include/memory.h` lines 15-28; `runtime/src/memory.cpp` lines 497-558):

| Region | Guest address(es) | Size |
|---|---|---|
| MEM1 (physical, cached and uncached views of one store) | `0x00000000`, `0x80000000`, `0xC0000000` | 24 MiB |
| MEM2 (physical, cached and uncached views of one store) | `0x10000000`, `0x90000000`, `0xD0000000` | 128 MiB |
| Kamek mod overlay | `0x81800000` | 2 MiB |
| Locked cache (really 16 KiB, padded so it fits the 1 MiB page tables) | `0xE0000000` | 1 MiB + 4 KiB |
| MMIO window (no access) | `0xCC000000` | 32 MiB, reserved but not backed |

**How it is implemented** (`runtime/include/guest_flat_memory.h`; `runtime/src/guest_flat_memory.cpp`):

- The runtime reserves a **4 GiB virtual address range** for the guest (`kGuestSpaceSize = 0x1'0000'0000`)
  at a **fixed host address**:
  - `0x0000'1000'0000'0000` (16 TiB) on x86-64
  - `0x0000'0080'0000'0000` on Apple ARM64
  - `0x0000'0010'0000'0000` (64 GiB) on other AArch64
  - any other architecture: `#error` (`guest_flat_memory.h` lines 16-41)
- Each RAM store is one shared-memory section mapped twice:
  - a "guest view" inside the 4 GiB range, whose page protections catch MMIO access, executable-page
    writes and EFB reads;
  - a "host view" that native runtime code writes through without checks.
- The section is created with `CreateFileMappingW`/`MapViewOfFile` on Windows and `memfd_create`
  plus `mmap(MAP_SHARED)` elsewhere (`guest_flat_memory.cpp` lines 553-600). It needs Windows 10
  1803+ for `VirtualAlloc2`/`MapViewOfFile3` (line 227).
- Access faults are fixed up by a vectored exception handler or signal handler
  (`guest_flat_memory.h` lines 117-124).
- `Memory::Init` **always** calls `GuestFlat::Initialize`, so the page-table ("checked") path still
  gets its storage from the flat reservation (`memory.cpp` lines 566-603). No allocator independent
  of the 4 GiB reservation was found.
- On AArch64 kernels whose page size is larger than 4 KiB, a runtime flag forces the checked path
  for general accesses (`guest_flat_memory.h` lines 68-85).

**Host RAM.** The source doesn't state a total. These are the allocations I could find:

| Item | Size | Evidence |
|---|---|---|
| Guest virtual reservation | 4 GiB of address space (not RAM) | `guest_flat_memory.h` line 16 |
| Guest RAM backing (MEM1 + MEM2 + overlay + locked cache) | ~155 MiB at most, zero-filled on demand ("would fault in all 152 MiB at startup") | `memory.cpp` lines 497-558; `guest_flat_memory.cpp` lines 613-614 |
| Host stack per guest thread | 1 MiB each | `runtime/src/fiber_manager.cpp` lines 291, 798 |
| Boot context stack | 4 MiB | `fiber_manager.cpp` line 801; `runtime/src/frontend_runtime.cpp` line 330 |
| Display-list scan cache | up to 32 MiB, 65,536 entries | `runtime/src/hle/gx/gx_dl.cpp` (`kDlScanCacheMaxStoredBytes`) |
| Save-state buffer (libretro core, when used) | MEM1 + MEM2 + 1 MiB (~153 MiB) reserved | `frontend_runtime.cpp` line 436 |
| Translated code, Aurora/Dawn GPU objects, texture cache, HD texture pack, SDL, audio buffers | not determined | — |

## c. Graphics

**Graphics are emulated at the GX function level, plus decoding of the GPU command stream. There is
no hardware-level GPU emulation.** The runtime replaces the Wii SDK's GX functions with native
implementations (README table: "Runtime and Wii SDK HLE (… GX)").

- **Function-level replacement.** `runtime/src/hle/gx/` (24 files) defines functions such as
  `GX__Init_8016b850` ("This replaces the translated function that writes to MMIO addresses",
  `gx_init.cpp` lines 26-33) and `GX__ClearVtxDesc_8016dc34` (`gx_vertex.cpp`). These call Aurora's
  Dolphin-SDK-style GX API (the `#include <dolphin/gx/...>` headers in `gx_internal.h`).
  The translator is told to use these native versions through `native_abi_directories:
  runtime/src/hle/gx` (`projects/spm/recomp.yml` lines 36-39).
- **Command-stream decoding.** Writes to the GPU FIFO (gather pipe) are intercepted
  (`runtime/src/memory.cpp` lines 683-686, `GX_HLE_FIFO_Write8`). Display lists are parsed for
  CP/XF/BP register writes and vertex data, then sent to Aurora with `aurora::gx::fifo::submit_raw_draw`
  (`gx_fifo.cpp`, `gx_dl.cpp`, `gx_cp_decode.h`). The translator also has a FIFO "burst" mode
  (`CodeGen/CxxLinearCodeGenerator.GpuFifoBurst.cs`).
- **EFB-to-RAM copies** are deferred and materialised when the guest touches them, using page
  protection (`guest_flat_memory.h` lines 98-101; `aurora-main/lib/gfx/efb_ram_copy.cpp`).

**What the renderer depends on.**

- **Aurora** (`wiicompiled/aurora-main/`), a "source-level GameCube & Wii compatibility layer"
  built on **WebGPU through Google's Dawn** (`aurora-main/README.md` lines 6, 32-36).
  - It lists D3D12, Vulkan and Metal as graphics APIs (line 16).
  - Dawn backends named in code: D3D11, D3D12, Metal, Vulkan, OpenGL, OpenGLES, Null
    (`aurora-main/lib/webgpu/gpu.cpp` lines 593-607). Only D3D12/Vulkan/Metal are documented as
    supported; Android requires Vulkan (`docs/android-and-macos.md` line 37).
- **Shaders.** TEV/GX state is turned into **WGSL** shaders (`aurora-main/lib/gx/shader.cpp`).
  The generated vertex stage reads vertex and attribute data from **storage buffers**
  (`var<storage, read> vbuf`/`abuf`, `shader.cpp` lines 2166-2169). Depth readback uses a
  **compute shader** (`aurora-main/lib/gfx/depth_peek.cpp` lines 89-160). Pipeline creation asks for
  storage-buffer limits (`gpu.cpp` lines 731-751).
- **Other libraries:** SDL3 (window and input), Abseil, xxHash, Dear ImGui, plus a pipeline cache
  stored in SQLite (`THIRD-PARTY-NOTICES.md` lines 124-144; `aurora-main/lib/gfx/pipeline_cache.cpp`).
- **Minimum desktop GPU** (WiiCompiled's figures): GTX 1650 / RX 6400 / Arc A310, "set by driver
  support and D3D12/Vulkan feature requirements, not by the game's actual demands"
  (`docs/WiiCompiled-README.md` lines 100-109).

## d. Audio, input, file loading and saves

**Audio** (`runtime/src/hle/audio/`, `runtime/src/audio_backend.cpp`)

- The game's audio DSP isn't emulated. Instead the AX/AI layer is reimplemented natively: a native
  mixer walks the game's AX command lists and parameter blocks, picking the layout from the
  microcode CRC (`ax_mix.cpp` lines 81-83, 185-190, 562-563).
- It resamples using Dolphin's free DSP coefficient ROM (`runtime/assets/dsp/dsp_coef.bin`).
- It delivers 3 ms blocks of 32 kHz stereo and runs the game's AI DMA callbacks in hardware order
  (`audio.cpp` lines 32-48, 399-400, 567-568). Mixing runs on a worker thread (`ax_mix.cpp` lines 67-68).
- Output goes to SDL3 (`audio_backend.cpp` includes `<SDL3/...>`). The libretro core resamples to
  48 kHz for RetroArch (`docs/android-and-macos.md` lines 81-82).
- An optional AVX2 mix kernel exists (`ax_mix_kernels.h` lines 12-13).

**Input** (`runtime/src/hle/input/{wpad,kpad,pad}.cpp`)

- The Wii Remote libraries' read functions (`KPADRead`, WPAD) are replaced and fed from host input
  (`kpad.cpp` comments).
- The gamepad acts as a sideways Wii Remote. The pointer comes from the right stick, mouse or touch
  (`README.md` lines 42-44; `docs/android-and-macos.md` lines 83-86).
- Real Bluetooth Wii Remotes are supported (`runtime/src/wii_remote_input.cpp`;
  `docs/WiiCompiled-README.md` lines 83-95). Bindings use Dolphin-style input expressions
  (`runtime/src/input_expr.cpp`, `input_bindings.cpp`).

**File loading** (`runtime/src/hle/storage/dvd.cpp`)

- The game's disc reads are served from an **extracted disc folder** set by `[paths] dvd_root` in
  `Config.toml`: `<dvd_root>/files` is mapped to `/` and `<dvd_root>/sys` to `/sys/` (`dvd.cpp`
  lines 256-265, 966-969).
- Disc images are unpacked once, ahead of time:
  - desktop: the launcher's `--extract` (`README.md` lines 36-37, 68-69);
  - Android core: `.wbfs` only, into `<system>/spm-r8pe01/disc/` (`runtime/frontend/disc_image.cpp`;
    `docs/android-and-macos.md` lines 68-71).
- Riivolution-style file replacement (mods) is supported (`runtime/src/hle/storage/riivolution.cpp`).
- `dvd.cpp` includes `<windows.h>` only inside an `#if defined(_WIN32)` block (line 23).

**Saves** (`runtime/src/hle/storage/nand_*.cpp`)

- NAND/ISFS calls are redirected to a host folder:
  `<nand_root>\title\00010000\<title id>\data\...` (`nand_fs.cpp` lines 1-2;
  `nand_internal.h` lines 44-47).
- Wii and Dolphin saves (`data.bin` or `wiimario00`) can be imported (`README.md` lines 50-52).
- Crypto++ provides SHA-1 and ECDSA for console identity and signing (`runtime/include/wii_es_crypto.h`;
  `THIRD-PARTY-NOTICES.md` lines 81-87). Dolphin's default WiiConnect24 files seed a new NAND
  (`runtime/assets/wii/shared2/wc24/`).
- Whole-machine save states exist for the libretro core (`docs/android-and-macos.md` lines 92-100;
  `runtime/src/save_state.cpp`).

## e. Runtime vs build-time dependencies; 64-bit and desktop assumptions

**Build time only**

- .NET 8 SDK (runs the translator) and YamlDotNet
- CMake ≥ 3.25 and Ninja
- Clang/LLVM: LLVM-MinGW on Windows, Apple Clang, or the Android NDK
- Python 3 (with `cryptography` for Android)
- nodtool (disc extraction)
- For the Android APK: JDK 17, the Android SDK and Gradle

Sources: `translator/README.md` lines 34-40; `docs/android-and-macos.md` lines 9-11, 114-117;
`THIRD-PARTY-NOTICES.md` lines 158-190.

**Linked into or shipped with the runtime**

- Vendored in the repo: Aurora, magic_enum, pugixml, Crypto++, toml11, libco
- Downloaded at build time (pinned, SHA-256 checked): Dawn/Tint, SDL 3.4.4, Abseil, Dear ImGui,
  {fmt}, xxHash, zlib, libpng, FreeType, Zstandard, SQLite, Mbed TLS, Tracy
- Windows only: DirectXShaderCompiler, `dxil.dll`, libusb inside SDL, the MSVC runtime DLLs, C++/WinRT
- Runtime data files: Dolphin's DSP coefficient ROM and WiiConnect24 tree

Source: `THIRD-PARTY-NOTICES.md` lines 12-144.

**Hard 64-bit requirements in the code**

- `runtime/CMakeLists.txt` lines 13-15: `FATAL_ERROR "WiiCompiled requires a 64-bit Clang toolchain"`
  unless `CMAKE_SIZEOF_VOID_P EQUAL 8`.
- `runtime/CMakeLists.txt` lines 29-48 accept only these platforms, otherwise `FATAL_ERROR`:
  - Windows x86-64 (MinGW)
  - macOS x86-64 or arm64
  - Android `arm64-v8a`
  - Linux x86-64 or aarch64
- `#error` on any architecture other than x86-64 or AArch64:
  - `runtime/include/guest_flat_memory.h` line 40 (fixed 4 GiB guest base)
  - `runtime/include/isa/ppc_isa_config.h` line 12 (SIMD header)
  - `runtime/include/isa/ppc_isa_fpenv.h` line 25 (FP control register mapping)
  - `runtime/src/host_context.cpp` line 29 (coroutine backend)
- A 4 GiB guest range inside the host address space is impossible on a 32-bit host
  (`guest_flat_memory.h` line 16).
- x86 builds target `-march=x86-64-v3` (Haswell or newer) and check for it at startup
  (`runtime/cmake/PublicProducts.cmake` line 410; `runtime/src/host_cpu_baseline.cpp`).

**Desktop-class assumptions**

- A GPU with D3D12, Vulkan or Metal through Dawn/WebGPU, using storage buffers and compute shaders
  (see section c).
- OS virtual-memory features: shared-memory sections mapped at a fixed address, page-protection
  changes, and fault handlers that resume execution (`guest_flat_memory.cpp`).
- Stated desktop minimums: 4-core/6-thread ~3.5 GHz CPU (i5-8400 / Ryzen 5 2600); ~20 GB free disk
  while installing, ~5 GB installed (`docs/WiiCompiled-README.md` lines 99-102). These figures come
  from the Mario Kart Wii project; Super Paper Mario's own README asks for 64-bit Windows 10/11 and
  DX12 or Vulkan (`README.md` line 30).

## f. The Android build, and 32-bit ARM

**What Android changes**

- **Two products** from the same translated code (`docs/android-and-macos.md`):
  1. A **libretro core** for RetroArch, `spm_libretro.so` (lines 35-110). Aurora renders without a
     window on its own Vulkan Dawn device, and frames reach RetroArch through `AHardwareBuffer` and
     sync file descriptors (`runtime/frontend/bridge.cpp`; lines 75-77). Each `retro_run` advances
     one VI retrace (line 79).
  2. A **standalone SDL app** in `wiicompiled/android/` (lines 112-130). Its Java package is
     `com.wither.nsmbw` (`android/app/src/main/java/com/wither/nsmbw/`).
- **Platform-specific pieces:**
  - its own coroutine switch in assembly (`runtime/src/platform/android/co_switch.S`)
  - `runtime/src/android/android_bridge.cpp`
  - a 64 GiB fixed guest base for AArch64 (`guest_flat_memory.h` lines 28-38)
  - big.LITTLE core pinning (`docs/android-and-macos.md` line 89)
  - a 30 fps option that runs two retraces per frame (line 106)
  - a check for 16 KB segment alignment (line 48)
- **Requirements:** Vulkan and an ARM64 device; the default CPU floor is ARMv8-A, with an optional
  ARMv8.2-A build (lines 37, 53).

**32-bit ARM: nothing supports it.**

- The APK's `abiFilters 'arm64-v8a'` (`wiicompiled/android/app/build.gradle` line 18).
- `CMakeLists.txt` accepts only `arm64-v8a` on Android (line 38) and stops on any 32-bit pointer
  size (lines 13-15).
- The `#error` guards listed in section e have no 32-bit ARM branch.
- libco's `arm.c` is present (`runtime/third_party/libco/arm.c`), but `THIRD-PARTY-NOTICES.md`
  (lines 102-111) says only `amd64.c` is ever compiled, and `host_context.cpp` stops with `#error`
  for unsupported backends.

## g. Licences

| Part | Licence | Evidence |
|---|---|---|
| WiiCompiled translator, runtime, project files (and so this port, per its README) | GPL-3.0 | `wiicompiled/LICENSE`; `README.md` lines 118-120; `docs/WiiCompiled-README.md` lines 248-257 ("Any mkwii distribution making use of WiiCompiled must be licensed under GPL v3.0") |
| Riivolution parser/patcher port, `ppc_isa_float.h`, `wii_es_crypto.h` | GPL-2.0-or-later (SPDX tags) | `runtime/src/hle/storage/riivolution.{h,cpp}`, `runtime/include/hle/riivolution_contract.h`, `runtime/include/isa/ppc_isa_float.h`, `runtime/include/wii_es_crypto.h` |
| Dolphin data files (DSP ROM, WiiConnect24 tree) | GPL-2.0-or-later | `THIRD-PARTY-NOTICES.md` lines 29-60 |
| Aurora | MIT | `aurora-main/LICENSE` |
| magic_enum | MIT | `aurora-main/include/magic_enum.hpp` |
| libogc-derived SRAM structures | zlib-style | `aurora-main/lib/card/SRAM.hpp`; `THIRD-PARTY-NOTICES.md` lines 25-27 |
| libco | ISC (`valgrind.h` BSD-style) | `runtime/third_party/libco/LICENSE` |
| Crypto++ 8.9.0 | Boost Software License 1.0 / public domain | `runtime/third_party/cryptopp/License.txt` |
| pugixml | MIT | `runtime/third_party/pugixml/LICENSE.md` |
| toml11 | MIT | `runtime/third_party/toml11/LICENSE` |
| Gradle wrapper | Apache-2.0 | `wiicompiled/android/gradlew` |
| SDL3 zlib; Dawn/Tint BSD-3-Clause; DXC NCSA; libusb LGPL-2.1+; Abseil Apache-2.0; ImGui MIT; {fmt} MIT; xxHash BSD-2; zlib; libpng; FreeType FTL (chosen over GPL-2.0); Zstandard BSD-3 (chosen over GPL-2.0); SQLite public domain; Mbed TLS Apache-2.0/GPL-2.0+; Tracy BSD-3; nodtool MIT/Apache-2.0 | as listed | `THIRD-PARTY-NOTICES.md` lines 115-156 |
| Controller button art | CC0 (Kenney) | `tools/button-art/Kenney-License.txt` |
| Launcher background, HQ music mod, HD texture pack | credited, no licence text found | `README.md` lines 108-111; `tools/CREDITS.txt` |
| Nintendo character artwork used by the launcher and window icon | Nintendo's; no licence | `tools/CREDITS.txt` ("Character artwork … are Nintendo's") |
| The translated game code (generated on the user's machine) | not stated | — |

There is no `LICENSE` file at the repository root. The README points to `wiicompiled/LICENSE`.

## What I could not determine

1. **What the generated C++ actually looks like.** No translated output is committed, and producing
   it means building the translator and translating your disc, which I was told not to do. Section a
   describes the code generator, not real output. The generated code's size (lines, compiled binary
   size) is also unknown.
2. **Total host RAM at runtime.** Section b lists the allocations I could find. The translated code,
   Dawn/Aurora GPU memory, texture and pipeline caches, SDL and audio buffers aren't quantified in the
   source, and nothing was measured.
3. **Whether the runtime works without the 4 GiB flat reservation.** The page-table helpers exist, but
   `Memory::Init` always calls `GuestFlat::Initialize`, and I found no other allocator. I didn't check
   whether a build could be configured another way.
4. **How much of the GX/Aurora path depends on WebGPU-only features** (storage buffers, compute) versus
   features a fixed-function or older GPU could provide. I found storage buffers in the main vertex
   shader and compute in depth readback, but didn't audit every pipeline.
5. **Performance.** No CPU or GPU figures specific to Super Paper Mario were found. The desktop
   minimums above come from the Mario Kart Wii project. Android performance options are documented,
   but no device figures are given.
6. **Accuracy and completeness for Super Paper Mario.** The repo's map-sweep regression tooling
   (`tools/sweep-spm-maps.py`) wasn't run, and I didn't review open issues.
7. **Code provenance.** WiiCompiled's README says AI coding tools were used
   (`docs/WiiCompiled-README.md` lines 225-227). I didn't check how much of the Super Paper Mario
   adaptation is original versus inherited from the Mario Kart Wii / NSMBW runtimes, beyond the
   naming leftovers noted in the overview.
8. **Licensing of translated output.** The repo doesn't say how the GPL applies to C++ machine-translated
   from Nintendo's binary, or whether that output can be distributed. This report doesn't answer it.
9. **Whether the Linux, macOS and Android build scripts work as documented.** Nothing was built.
