"""Work queue for one phase 3 source file.

usage: python -I notes/tools/phase3_queue.py make FILE.c [--stub]   write notes/phase3-queue/FILE.txt (one batch per line)
       python -I notes/tools/phase3_queue.py next FILE.c            print the first batch not yet in notes/phase3-log.md
`make` queues every function still marked NOT_DECOMPILED, defers those over 2,044 bytes (log row + deferred.md),
and with --stub creates the stub source of a NonStarted file and switches its configure.py line to NonMatching
(check the build and commit it afterwards).
Batches: up to 64 bytes: 10 per subagent; 65-128: 5; medium (129-640) and large (641-2,044): 1.
"""
import re
import subprocess
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
dec = proj / 'spm-decomp'
cmd, f = sys.argv[1], sys.argv[2]
f = f if f.endswith('.c') else f + '.c'
qpath = proj / f'notes/phase3-queue/{f[:-2]}.txt'
log = proj / 'notes/phase3-log.md'


def logged():
    out = set()
    for line in open(log, encoding='utf-8'):
        c = [x.strip() for x in line.split('|')]
        if len(c) > 4 and c[2] == f:
            out.add(c[3].strip('`'))
    return out


if cmd == 'next':
    done = logged()
    lines = qpath.read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines, 1):
        num, size, *fns = line.split()
        left = [x for x in fns if x.split(':')[0] not in done]
        if left:
            print(f'{f} batch {i}/{len(lines)} ({size}): ' + ' '.join(left))
            break
    else:
        print(f'{f}: all batches logged')
    sys.exit()

if cmd != 'make':
    sys.exit(__doc__)
lo = hi = cur = None
for line in open(dec / 'config/EU0/splits.txt', encoding='utf-8'):
    if line.rstrip().endswith(':') and not line.startswith('\t'):
        cur = line.strip()[:-1]
    elif cur == f:
        m = re.search(r'\.text\s+start:0x([0-9A-F]+) end:0x([0-9A-F]+)', line)
        if m:
            lo, hi = int(m.group(1), 16), int(m.group(2), 16)
if lo is None:
    sys.exit(f'{f}: no split')
fns = []
for line in open(dec / 'config/EU0/symbols.txt', encoding='utf-8'):
    m = re.match(r'(\S+) = \.text:0x([0-9A-F]+); // type:function size:0x([0-9A-F]+)', line)
    if m and lo <= int(m.group(2), 16) < hi:
        fns.append((int(m.group(2), 16), int(m.group(3), 16), m.group(1)))
fns.sort()

src = dec / 'src' / f
if not src.exists():
    if '--stub' not in sys.argv:
        sys.exit(f'{f} has no source file; run again with --stub')
    branch = subprocess.run(['git', 'branch', '--show-current'], cwd=dec, capture_output=True, text=True).stdout.strip()
    if branch != 'master':
        sys.exit(f'spm-decomp is on {branch}, not master')
    cfg = dec / 'configure.py'
    text = cfg.read_bytes()
    old = f'Object(NonStarted, "{f}")'.encode()
    if text.count(old) != 1:
        sys.exit(f'configure.py: expected exactly one NonStarted entry for {f}')
    header = f'#include <spm/{f[:-2]}.h>\n' if (dec / f'spm-headers/include/spm/{f[:-2]}.h').exists() else ''
    body = ('/*\n    WARNING: Not fully decompiled\n    This file is currently not linked into the final dol\n*/\n\n'
            f'#include <common.h>\n{header}\nextern "C" {{\n\n'
            + ''.join(f'// NOT_DECOMPILED {n}\n' for _, _, n in fns) + '\n}\n')
    src.write_text(body, encoding='utf-8', newline='\n')
    cfg.write_bytes(text.replace(old, f'Object(NonMatching, "{f}")'.encode()))
    print(f'stub src/{f} created, configure.py updated')

stubs = set(re.findall(r'^// NOT_DECOMPILED (\S+)', src.read_text(encoding='utf-8', errors='replace'), re.M))
done = logged()
todo = [(size, n) for _, size, n in fns if n in stubs and n not in done]
huge = [(s, n) for s, n in todo if s > 2044]
todo = sorted((s, n) for s, n in todo if s <= 2044)
batches = []
for label, low, high, per in (('tiny', 0, 64, 10), ('small', 65, 128, 5), ('medium', 129, 640, 1), ('large', 641, 2044, 1)):
    group = [(s, n) for s, n in todo if low <= s <= high]
    batches += [(label, group[i:i + per]) for i in range(0, len(group), per)]
qpath.write_text(''.join(f'{i} {label} ' + ' '.join(f'{n}:{s}' for s, n in g) + '\n' for i, (label, g) in enumerate(batches, 1)),
                 encoding='utf-8', newline='\n')
for s, n in huge:
    subprocess.run([sys.executable, '-I', str(proj / 'notes/tools/log_row.py'), f, n, 'huge', str(s), 'deferred', '-', '0', '-',
                    'huge (over 2,044 B): stub left', '--defer', 'huge'], check=True, capture_output=True)
counts = {k: sum(len(g) for lab, g in batches if lab == k) for k in ('tiny', 'small', 'medium', 'large')}
print(f'{f}: {len(todo)} queued in {len(batches)} batches {counts}; {len(huge)} huge deferred')
