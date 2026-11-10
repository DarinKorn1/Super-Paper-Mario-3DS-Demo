"""Summarise a console.log from a profiled run. Usage: python -I log_summary.py <console.log>"""
import re, sys, statistics
from collections import Counter

lines = open(sys.argv[1], encoding='utf-8', errors='replace').read().splitlines()
print('lines:', len(lines))
tags = Counter(re.match(r'^\[([a-z0-9:_ -]+)\]', l).group(1) if re.match(r'^\[([a-z0-9:_ -]+)\]', l) else '(none)' for l in lines)
print('tag counts:', tags.most_common(15))

# fps lines
FPS = re.compile(r'\] fps ([\d.]+): game ([\d.]+) ms \(gx ([\d.]+) ms, worker wait ([\d.]+) ms, lock wait ([\d.]+) ms, ([\d.]+) draws, ([\d.]+) copies, ([\d.]+) new copy textures\), end_frame ([\d.]+) ms, pace ([\d.]+) ms, worst frame ([\d.]+) ms, jitter ([\d.]+) ms, (\d+) over 20 ms')
rows = []
for i, l in enumerate(lines):
    m = FPS.search(l)
    if m:
        rows.append((i,) + tuple(float(x) for x in m.groups()))
print('fps windows:', len(rows))
if rows:
    cols = ['fps', 'game_ms', 'gx_ms', 'worker_wait', 'lock_wait', 'draws', 'copies', 'new_copy_tex', 'end_frame_ms', 'pace_ms', 'worst_ms', 'jitter_ms', 'over20']
    for k, c in enumerate(cols, start=2):
        vals = [r[k - 1] for r in rows]
        print(f'  {c:13s} min {min(vals):8.2f}  median {statistics.median(vals):8.2f}  mean {statistics.mean(vals):8.2f}  max {max(vals):8.2f}')
    print('first 6 windows:'); [print('  ', r[1:]) for r in rows[:6]]
    print('worst-fps 5 windows:'); [print('  ', r[1:]) for r in sorted(rows, key=lambda r: r[1])[:5]]
    print('windows with fps>=59:', sum(1 for r in rows if r[1] >= 59), 'of', len(rows))
# seq changes
seq = [(l) for l in lines if '] seq ->' in l]
print('seq lines:', len(seq))
for l in seq:
    if re.search(r'seq -> (title|load|game|logo) \(', l) and 'stage' in l: pass
# the first time each sequence was reached
seen = {}
for l in lines:
    m = re.search(r'seq -> (\w+) \(next (\w+)\) stage (\d+) \(frame (\d+)\)', l)
    if m and m.group(1) not in seen: seen[m.group(1)] = m.group(4)
print('first frame of each sequence:', seen)
# warnings / oddities
odd = [l for l in lines if re.search(r'FAILED|failed|error|Error|warning|WARN|blocked|unmapped|MMIO|abort|assert|Exception|exception|MISMATCH|stall|watchdog', l) and '[dvdread]' not in l]
print('odd lines:', len(odd))
for l in odd[:40]: print('  ', l[:220])
# profile
prof = [l for l in lines if 'profile' in l.lower() and 'profile_stacks' not in l]
print('profile lines:', len(prof))
# heap related
heap = [l for l in lines if re.search(r'heap|Heap|HEAP|arena|MEM1|MEM2|memory\]', l)]
print('heap-ish lines:', len(heap))
for l in heap[:30]: print('  ', l[:220])
print('--- tail ---')
for l in lines[-12:]: print('  ', l[:220])
