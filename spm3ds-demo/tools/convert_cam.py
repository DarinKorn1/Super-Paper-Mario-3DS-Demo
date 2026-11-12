"""Decodes camera_road.bin from the room archive and writes assets/camera.bin (+ assets/camera_report.txt).
Run from spm3ds-demo/:  python -I tools/convert_cam.py   (needs the disc dump like convert_room.py; output is git-ignored).

camera_road.bin ("SPMario_CameraRoadExport" 1.02, big-endian) layout, worked out from the data and the game's code (notes/demo-plan.md 13):
  0x00 u32 fileSize, 0x04 magic string, 0x44 version, 0x84 date.
  0xC4.. header: counts and section offsets. Sections: 15 camera records x 184 bytes at 0x118, 15 x 104 bytes at 0xBE0, 37 x 8 at 0x11F8,
  180 points (3 x f32) at 0x1320, 102 vectors at 0x1B90, 148 words at 0x2058.
  Camera record (184 bytes): +0x00 name (64 bytes, "|MarioSt_CameraRoad|C2D_01"), +0x58 f32 distance (33.0 for C2D, 31.58 for C3D),
  +0x64 f32 pitch in degrees (17.87 for 2D cameras, 23.0 for 3D), +0x84 u32 1, +0x88 two points (x,y,z) = the path the camera target moves along.
  C2D_01: x -110..110 at z -10 (the plane Mario walks on in 2D). C3D_01: x -111.5..108 at z -30.
Not decoded (kept in the report): +0x50/+0x54 (2D: 0.066 / 0.935, probably screen-edge follow margins; 3D: 0.37/0.61), +0x70 (-17.87), +0x7C (20.0).
Projection (not in this file, from camInit in main.dol, USA 0x80054800..): 2D camera (id 11) = perspective, fovY 50, aspect 608/480, near 100, far 10000.
3D camera (id 5) = perspective, fovY 25, near 1. Game units; this demo's room is 1/8 of them."""
import os, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import convert_room as cr

DISC = '../NewSuperPaperBros/Disc/DATA/files/map/mac_02.bin'
arc = cr.parse_u8(cr.lz10(open(DISC, 'rb').read()))
road = arc['./dvd/map/mac_02/camera_road.bin']
assert struct.unpack('>I', road[:4])[0] == len(road) and road[4:28] == b'SPMario_CameraRoadExport'
cams = {}
lines = []
for i in range(15):
    o = 0x118 + i * 184
    name = road[o:o + 64].split(b'\0')[0].decode().split('|')[-1]
    f = struct.unpack('>46f', road[o + 0x40:o + 0x40 + 46 * 4][:184])
    dist, pitch = struct.unpack('>f', road[o + 0x58:o + 0x5C])[0], struct.unpack('>f', road[o + 0x64:o + 0x68])[0]
    n = struct.unpack('>I', road[o + 0x84:o + 0x88])[0]
    p = struct.unpack('>6f', road[o + 0x88:o + 0xA0])
    cams[name] = (dist, pitch, p)
    lines.append('%-14s dist %7.2f pitch %6.2f  points (%.1f %.1f %.1f) -> (%.1f %.1f %.1f)  [+0x50 %.4f +0x54 %.4f +0x70 %.2f +0x7C %.2f]' % (
        (name, dist, pitch) + p + tuple(struct.unpack('>f', road[o + k:o + k + 4])[0] for k in (0x50, 0x54, 0x70, 0x7C))))
os.makedirs('assets', exist_ok=True)
open('assets/camera_report.txt', 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))

def entry(name, fov, near, far):
    d, pitch, p = cams[name]
    return struct.pack('<10f', d, pitch, min(p[0], p[3]), max(p[0], p[3]), p[2], fov, near, far, 0.0, 0.0)
# SCAM, version 1, then 2D block and 3D block, each: dist, pitchDeg, xMin, xMax, z, fovY, near, far (+2 spare) in the road's units (room units);
# near/far are the game's (100/10000 and 1/32768, game units) divided by 8 for the room.
with open('assets/camera.bin', 'wb') as out:
    out.write(b'SCAM' + struct.pack('<I', 1))
    out.write(entry('C2D_01', 50.0, 100.0 / 8, 10000.0 / 8))
    out.write(entry('C3D_01', 25.0, 1.0 / 8, 10000.0 / 8))
print('wrote assets/camera.bin')
