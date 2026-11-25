"""Hand whole files from the phase 3 plan to Antigravity.

usage: python -I notes/tools/refill_ag_queue.py (--files a.c b.c ... | --from N [--target 250]) [--write]
  --files    the files, in the order Antigravity should work them
  --from N   take files from plan row N onwards until --target unfinished functions are collected
  --write    append to spm-decomp-ag/notes/ag-queue.md, mark the plan rows, list huge functions
             in notes/deferred.md. Without it, only print what would happen (dry run).
Functions over 2,044 bytes are never queued. Nothing is committed.
"""
import argparse
import datetime
import re
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
ag = proj / 'spm-decomp-ag'
plan_path = proj / 'notes/phase3-plan.md'
HUGE = 2044

ap = argparse.ArgumentParser()
ap.add_argument('--files', nargs='+')
ap.add_argument('--from', dest='start', type=int)
ap.add_argument('--target', type=int, default=250)
ap.add_argument('--write', action='store_true')
a = ap.parse_args()
if not a.files and a.start is None:
    sys.exit('give --files or --from')

splits, cur = {}, None
for line in open(ag / 'config/EU0/splits.txt', encoding='utf-8'):
    if line.rstrip().endswith(':') and not line.startswith('\t'):
        cur = line.strip()[:-1]
    else:
        m = re.search(r'\.text\s+start:0x([0-9A-F]+) end:0x([0-9A-F]+)', line)
        if m:
            splits[cur] = (int(m.group(1), 16), int(m.group(2), 16))
syms = []
for line in open(ag / 'config/EU0/symbols.txt', encoding='utf-8'):
    m = re.match(r'(\S+) = \.text:0x([0-9A-F]+); // type:function size:0x([0-9A-F]+)', line)
    if m:
        syms.append((int(m.group(2), 16), int(m.group(3), 16), m.group(1)))

plan = open(plan_path, encoding='utf-8').read().split('\n')
rows = {}
for i, line in enumerate(plan):
    m = re.match(r'\| (\d+) \| `([\w.]+)` \| ([^|]*)\|', line)
    if m:
        rows[m.group(2)] = (int(m.group(1)), i, m.group(3).strip())


def unfinished(f):
    lo, hi = splits[f]
    fns = [(size, addr, name) for addr, size, name in syms if lo <= addr < hi]
    src = ag / 'src' / f
    if src.exists():
        stubs = set(re.findall(r'^// NOT_DECOMPILED (\S+)', src.read_text(encoding='utf-8', errors='replace'), re.M))
        fns = [x for x in fns if x[2] in stubs]
    return sorted(x for x in fns if x[0] <= HUGE), sorted(x for x in fns if x[0] > HUGE)


queue = (ag / 'notes/ag-queue.md').read_text(encoding='utf-8')
if a.files:
    picked = a.files
else:
    picked, n = [], 0
    for f, (num, _, status) in sorted(rows.items(), key=lambda kv: kv[1][0]):
        if num < a.start or 'ANTIGRAVITY' in status or f'## {f}' in queue or f'### {f}' in queue:
            continue
        if n >= a.target:
            break
        picked.append(f)
        n += len(unfinished(f)[0])

data = []
for f in picked:
    if f not in splits:
        sys.exit(f'{f}: no split')
    if f'## {f}' in queue:
        sys.exit(f'{f}: already in the Antigravity queue')
    data.append((f, *unfinished(f)))

total = sum(len(q) for _, q, _ in data)
today = datetime.date.today().isoformat()
summary = ['| File | Status | Functions left | Bytes | Small (<=128) / medium (129-640) / large (641-2,044) |', '|---|---|---|---|---|']
for f, q, huge in data:
    s = sum(1 for x in q if x[0] <= 128)
    med = sum(1 for x in q if 128 < x[0] <= 640)
    status = rows[f][2] if f in rows else '?'
    summary.append(f'| `{f}` | {status} | {len(q)} | {sum(x[0] for x in q)} | {s} / {med} / {len(q) - s - med} |')
print('\n'.join(summary))
print(f'total queued functions: {total}; huge skipped: {sum(len(h) for _, _, h in data)}')
if not a.write:
    print('dry run (add --write)')
    sys.exit(0)

out = [f'\n## Refill {today} (added by Claude)\n',
       'Whole files, worked in this order, each from the smallest function to the largest. Functions over 2,044 bytes are left out on purpose: '
       'do NOT start them (leave their `// NOT_DECOMPILED` lines). A `NonStarted` file needs its stub source first (see `AGENTS.md`).\n',
       *summary, '']
for f, q, _ in data:
    out += [f'### {f}\n', f'Header: `spm-headers/include/spm/{f[:-2]}.h` (if it exists).\n',
            '| Done | # | Function | Bytes | Address |', '|---|---|---|---|---|']
    out += [f'| [ ] | {i} | `{name}` | {size} | 0x{addr:08X} |' for i, (size, addr, name) in enumerate(q, 1)]
    out.append('')
with open(ag / 'notes/ag-queue.md', 'a', encoding='utf-8', newline='\n') as fh:
    fh.write('\n'.join(out))

for f, _, _ in data:
    if f in rows:
        _, i, status = rows[f]
        cells = plan[i].split('|')
        cells[3] = f' ANTIGRAVITY ({today}) '
        plan[i] = '|'.join(cells)
open(plan_path, 'w', encoding='utf-8', newline='\n').write('\n'.join(plan))

huge_rows = [f'| {name} | {f} | {size} | huge, left out of the Antigravity queue {today} |' for f, _, h in data for size, _, name in h]
if huge_rows:
    d = proj / 'notes/deferred.md'
    text = d.read_text(encoding='utf-8')
    marker = '<!-- huge-end -->'
    text = text.replace(marker, '\n'.join(huge_rows) + '\n' + marker)
    d.write_text(text, encoding='utf-8', newline='\n')
print('written: ag-queue.md, phase3-plan.md, deferred.md (commit them yourself)')
