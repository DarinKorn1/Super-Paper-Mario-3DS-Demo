"""fps windows split by game phase; maps loaded; OSReport lines; slow render frames. Usage: python -I phase_summary.py <console.log>"""
import re, statistics, sys
from collections import Counter, defaultdict
lines = open(sys.argv[1], encoding='utf-8', errors='replace').read().splitlines()
FPS = re.compile(r'\] fps ([\d.]+): game ([\d.]+) ms \(gx ([\d.]+) ms.*?([\d.]+) draws.*?end_frame ([\d.]+) ms, pace ([\d.]+) ms, worst frame ([\d.]+) ms, jitter ([\d.]+) ms, (\d+) over 20 ms')
SEQ = re.compile(r'seq -> (\w+) \(next (\w+)\) stage (\d+) \(frame (\d+)\)')
phase = 'boot'; frame = 0
rows = []          # (index_in_fps_series, line_no, phase, frame, fps, game, gx, draws, endf, pace, worst, jitter, over20)
for i, l in enumerate(lines):
    m = SEQ.search(l)
    if m: phase = m.group(1); frame = int(m.group(4))
    m = FPS.search(l)
    if m:
        v = [float(x) for x in m.groups()]
        rows.append((len(rows), i, phase, frame) + tuple(v))
print('fps windows:', len(rows))
prof_line = next(i for i, l in enumerate(lines) if 'profile: 20000 samples' in l)
before = [r for r in rows if r[1] < prof_line]
print('fps windows before the profiler report:', len(before), '(each ~2 s => ~%d s from first presented frame)' % (2 * len(before)))
print('phase at the profiler report line:', [r[2] for r in rows if r[1] < prof_line][-1], 'frame', [r[3] for r in rows if r[1] < prof_line][-1])
print('\nwindows by phase (phase = last "seq ->" before the window):')
by = defaultdict(list)
for r in rows: by[r[2]].append(r)
def med(x): return statistics.median(x) if x else float('nan')
for ph, rs in by.items():
    print(f'  {ph:10s} windows {len(rs):3d}  fps median {med([r[4] for r in rs]):5.1f} (min {min(r[4] for r in rs):5.1f}, max {max(r[4] for r in rs):5.1f})  game ms median {med([r[5] for r in rs]):5.2f}  gx ms median {med([r[6] for r in rs]):4.2f}  draws median {med([r[7] for r in rs]):6.0f}  end_frame median {med([r[8] for r in rs]):4.2f}  worst median {med([r[10] for r in rs]):6.1f} max {max(r[10] for r in rs):6.1f}')
# windows inside the profile (approx 30-50 s = windows 15..25) and after it in game phase
def summ(label, rs):
    if not rs: print(label, 'none'); return
    print(f'  {label}: {len(rs)} windows, fps median {med([r[4] for r in rs]):.1f} (min {min(r[4] for r in rs):.1f}), game {med([r[5] for r in rs]):.2f} ms, gx {med([r[6] for r in rs]):.2f} ms, end_frame {med([r[8] for r in rs]):.2f} ms, pace {med([r[9] for r in rs]):.2f} ms, worst frame median {med([r[10] for r in rs]):.1f} ms (max {max(r[10] for r in rs):.1f}), draws median {med([r[7] for r in rs]):.0f}')
print('\nProfiler window (about fps windows 15-25 by time):')
summ('windows 15-25', rows[15:26])
for r in rows[15:26]: print('    ', r[2:], )
# seq timeline: first load->game
print('\nsequence timeline (frame numbers):')
last = None
for l in lines:
    m = SEQ.search(l)
    if m and (m.group(1), m.group(2)) != last and m.group(1) in ('title', 'load', 'game', 'logo') :
        last = (m.group(1), m.group(2)); print('  ', l.strip()[:120])
maps = [m.group(1) for l in lines for m in [re.search(r'files\\map\\(\w+)\.bin', l)] if m]
print('\nmaps loaded in order:', maps)
print('spmwarp lines:', [l.strip() for l in lines if 'spmwarp' in l])
print('\nOSReport lines:')
for l in lines:
    if '[OSReport]' in l: print('  ', l[:200])
slow = [re.search(r'Slow render frame: ([\d.]+) ms \(seal ([\d.]+), encode ([\d.]+), publish ([\d.]+), prepare next ([\d.]+)', l) for l in lines]
slow = [tuple(float(x) for x in m.groups()) for m in slow if m]
print('\nslow render frame lines:', len(slow))
if slow:
    for k, nm in enumerate(['total', 'seal', 'encode', 'publish', 'prepare_next'])  :
        v = [s[k] for s in slow]; print(f'  {nm:13s} median {statistics.median(v):6.2f}  max {max(v):6.2f}')
print('\nother notable lines:')
for l in lines:
    if re.search(r'read cache|watchdog|Present mode|save anywhere|Compiling shaders|pipelines queued\)\s*$|texture replac|button icon|Adapter|GPU compat', l) and 'Slow render' not in l:
        print('  ', l.strip()[:200])
