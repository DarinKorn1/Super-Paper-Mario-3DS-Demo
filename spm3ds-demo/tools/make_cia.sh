#!/bin/sh
# Builds spm3ds-demo.cia next to the .3dsx. Run from spm3ds-demo/ AFTER `make`, in the devkitPro MSYS2 shell.
# Needs makerom and bannertool on PATH (not part of devkitPro; see notes/demo-plan.md section 12). UNTESTED until those are installed.
set -e
bannertool makebanner -i cia/banner.png -a cia/banner.wav -o cia/banner.bnr
bannertool makesmdh -s "Super Paper Mario 3DS Demo" -l "Flipside demo: stereo 3D, Mario, music" -p "DarinKorn1" -i icon.png -o cia/icon.icn
makerom -f cia -o spm3ds-demo.cia -elf spm3ds-demo.elf -rsf cia/spm3ds-demo.rsf -icon cia/icon.icn -banner cia/banner.bnr -exefslogo -target t
echo "built spm3ds-demo.cia"
