"""Flipside-only frame statistics from a console.log written with NSMBW_LOG_FPS=1.
A window counts as Flipside when the game is in its `game` sequence and the last map file the game read starts with `mac_`.
Usage: python -I flipside_log.py <console.log> [out.json]
"""
import json, re, statistics, sys

lines = open(sys.argv[1], encoding='utf-8', errors='replace').read().splitlines()
FPS = re.compile(r'\] fps ([\d.]+): game ([\d.]+) ms \(gx ([\d.]+) ms, worker wait ([\d.]+) ms, lock wait ([\d.]+) ms, ([\d.]+) draws, ([\d.]+) copies, ([\d.]+) new copy textures\), end_frame ([\d.]+) ms, pace ([\d.]+) ms, worst frame ([\d.]+) ms, jitter ([\d.]+) ms, (\d+) over 20 ms')
GFX = re.compile(r'\] gfx: draw commands (\d+)/frame, merged into an earlier draw (\d+)/frame \(([\d.]+)% of GX primitives\), pipelines created (\d+) total, queued (\d+); uploads per frame: vertex (\d+) KB, uniform (\d+) KB, index (\d+) KB, storage (\d+) KB, texture (\d+) KB')
SEQ = re.compile(r'seq -> (\w+) \(next (\w+)\) stage (\d+) \(frame (\d+)\)')
MAP = re.compile(r'files\\map\\(\w+)\.bin')
phase, cur_map, frame = 'boot', '', 0
rows = []
idx = 0
for i, l in enumerate(lines):
    m = MAP.search(l)
    if m: cur_map = m.group(1)
    m = SEQ.search(l)
    if m: phase, frame = m.group(1), int(m.group(4))
    m = FPS.search(l)
    if m:
        v = [float(x) for x in m.groups()]
        row = dict(idx=idx, line=i, phase=phase, map=cur_map, frame=frame, fps=v[0], game=v[1], gx=v[2], draws=v[5], end_frame=v[8], pace=v[9], worst=v[10], jitter=v[11], over20=v[12])
        # the gfx line follows the fps line
        for j in range(i + 1, min(i + 4, len(lines))):
            g = GFX.search(lines[j])
            if g:
                gv = [float(x) for x in g.groups()]
                row.update(cmds=gv[0], merged=gv[1], merged_pct=gv[2], pipelines_created=gv[3], pipelines_queued=gv[4], vert_kb=gv[5], uniform_kb=gv[6], index_kb=gv[7], storage_kb=gv[8], texture_kb=gv[9])
                break
        rows.append(row); idx += 1
flip = [r for r in rows if r['phase'] == 'game' and r['map'].startswith('mac_')]
print('log:', sys.argv[1]); print('fps windows:', len(rows), '| Flipside windows:', len(flip))
maps = []
for l in lines:
    m = MAP.search(l)
    if m and (not maps or maps[-1] != m.group(1)): maps.append(m.group(1))
print('maps read, in order:', maps)
print('windows by (phase, map):')
from collections import Counter
for k, v in Counter((r['phase'], r['map']) for r in rows).items(): print('  ', k, v)
def stat(name, key, rs):
    v = [r[key] for r in rs if key in r]
    if not v: return
    print(f'  {name:22s} median {statistics.median(v):9.2f}  mean {statistics.mean(v):9.2f}  min {min(v):9.2f}  max {max(v):9.2f}')
if flip:
    print('Flipside windows (index range %d-%d):' % (flip[0]['idx'], flip[-1]['idx']))
    for n, k in [('fps', 'fps'), ('game ms', 'game'), ('gx ms', 'gx'), ('end_frame ms', 'end_frame'), ('pace ms', 'pace'), ('GX draws/frame', 'draws'), ('worst frame ms', 'worst'), ('jitter ms', 'jitter'), ('frames over 20 ms', 'over20'),
                 ('draw commands/frame', 'cmds'), ('merged/frame', 'merged'), ('merged %', 'merged_pct'), ('pipelines created', 'pipelines_created'), ('pipelines queued', 'pipelines_queued'),
                 ('vertex KB/frame', 'vert_kb'), ('uniform KB/frame', 'uniform_kb'), ('index KB/frame', 'index_kb'), ('storage KB/frame', 'storage_kb'), ('texture KB/frame', 'texture_kb')]:
        stat(n, k, flip)
    pc = [r['pipelines_created'] for r in flip if 'pipelines_created' in r]
    if pc: print('  pipelines created during Flipside windows:', int(pc[-1] - pc[0]), '(first %d, last %d)' % (pc[0], pc[-1]))
    fr = [r['fps'] for r in flip]
    print('  windows at >=59 fps: %d of %d; <30 fps: %d' % (sum(1 for x in fr if x >= 59), len(fr), sum(1 for x in fr if x < 30)))
json.dump(dict(rows=rows), open(sys.argv[2], 'w'), indent=1) if len(sys.argv) > 2 else None
