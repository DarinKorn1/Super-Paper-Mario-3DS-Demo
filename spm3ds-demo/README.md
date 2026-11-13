# Super Paper Mario 3DS demo (demo-v1)

A small homebrew demo for the New Nintendo 3DS (XL): Mario walks around Flipside (`mac_02`) with the game's camera,
a 2D/3D flip, stereo 3D, animated Mario, collision and the Flipside music. It reads data converted from **your own copy
of the USA disc** (`R8PE01`). No game data is in this repository and none must ever be published.

## What you need
- devkitPro with devkitARM, libctru, citro3d, tex3ds, picasso (Windows: `C:\devkitPro`).
- Python 3 (standard library only).
- The disc files extracted to `NewSuperPaperBros/Disc/DATA/files` (needs `map/mac_02.bin`, `a/p_mario`, `a/p_mario-`, `sound/map_town_omote1_44k_lp.brstm`).
- For `.cia` only: `makerom` and `bannertool` on PATH (not part of devkitPro).

## 1. Convert the assets
Run from `spm3ds-demo/`. Add devkitPro's `tex3ds` to PATH first (`C:\devkitPro\tools\bin`). Output goes to `assets/` (git-ignored).

    python -I tools/convert_room.py          # room_main.spm, room_oku.spm, room_hit.bin, textures/tex_*.t3x
    python -I tools/convert_mario.py         # mario.spm + textures/mario_*.t3x (static fallback)
    python -I tools/convert_mario_anim.py    # mario_anim.bin (idle + walk)
    python -I tools/convert_cam.py           # camera.bin (optional; defaults are built in)
    python -I tools/convert_bgm.py           # bgm_flipside.pcm (about 6 MB)

## 2. Build
Plain Git Bash does not set `DEVKITARM`; use the devkitPro MSYS2 shell:

    C:\devkitPro\msys2\usr\bin\bash.exe -lc 'cd /c/Users/ender/SPM_N3DS_XL/spm3ds-demo && make'

Result: `spm3ds-demo.3dsx` (and `.elf`, `.smdh`). The icon is `icon.png` (48x48); title and author are in the `Makefile`.

## 3. Install
The program and its data are separate. Copy the data to the SD card in both cases:

    sdmc:/3ds/spm3ds-demo/   room_main.spm, room_oku.spm, room_hit.bin, mario.spm, mario_anim.bin,
                             camera.bin, bgm_flipside.pcm, textures/ (tex_*.t3x and mario_*.t3x)

- **Homebrew Launcher (.3dsx):** copy `spm3ds-demo.3dsx` to `sdmc:/3ds/` and start it from the launcher.
- **Home Menu (.cia):** from `spm3ds-demo/` after `make`, in the devkitPro MSYS2 shell with makerom and bannertool on PATH: `sh tools/make_cia.sh`,
  then install `spm3ds-demo.cia` with FBI or similar. The CIA holds only the program, not the data.
- **Azahar (emulator):** its virtual SD card is `%APPDATA%\Azahar\sdmc\`; put the data in `3ds\spm3ds-demo\` there and load the `.3dsx`.
  Set Settings > Graphics > Stereoscopy to enable 3D.
- **Music on a real console** needs `sdmc:/3ds/dspfirm.cdc` (dumped with the DSP1 homebrew). If the file is missing the demo runs silent.

## Controls (play mode)
| Button | Action |
|---|---|
| Circle pad | walk (2D: left/right; 3D: relative to the camera) |
| A | jump |
| X | flip 2D / 3D |
| B | reset Mario |
| R | music on / off |
| Y | debug screen (stats; D-pad up = collision wireframe, L + D-pad up/down = Mario scale, D-pad left/right = music rate) |
| 3D slider | stereo 3D |
| SELECT | cycle play / free camera / stress test |
| START | quit |

## Known issues
- **Invisible wall in 3D:** Mario is sometimes stopped by something that is not drawn. Cause not found. Use the debug screen's collision view; contacts are logged to `sdmc:/3ds/spm3ds-demo/hitlog.txt`.
- **Jump** height and timing are guesses, not the game's values (the game's jump code is not decompiled yet).
- Only idle and walk animations; no run, hammer, etc. Costume-variant parts are hidden by name.
- Materials: only texture x vertex colour. No second texture layers, UV animation, fog, or alpha sorting; animated room parts (elevator doors) stay at rest.
- Collision ignores the game's attribute bits and ceilings; doors are solid.
- Camera: the 2D view is an emulated orthographic camera; the 3D view uses the road's values only (no per-map overrides).
- No sound effects (only the Flipside music). Music plays about 2x too fast in Azahar (workaround: `bgm_rate.txt` containing `0.5`).
- Not tested on real hardware; performance numbers from emulators do not count.

## Details
Formats, measurements and the reasoning behind the camera and scale are in `../notes/demo-plan.md`.
