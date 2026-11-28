"""Take functions that are not exactly 100% off master: keep the code on wip/<function>, put the stub back on master.

usage: python -I notes/tools/to_wip.py LISTFILE        (lines "<unit> <function>", e.g. "mario_status func_8015cff4")
For each function: branch wip/<function> (wip/<function>-master if taken) at the current master, pushed to origin.
Then, per unit, the definition (from its first line to the closing "}" in column 0, with a pragma pair around it)
is replaced by "// NOT_DECOMPILED <function>" and committed on master. Build and check afterwards; not pushed here.
"""
import re
import subprocess
import sys
from pathlib import Path

dec = Path(__file__).resolve().parents[2] / 'spm-decomp'


def git(*c, check=True):
    r = subprocess.run(['git', *c], cwd=dec, capture_output=True, text=True, errors='replace', timeout=300)
    if check and r.returncode:
        sys.exit(f'git {c[0]} failed: {(r.stderr or r.stdout).strip()[:400]}')
    return r.stdout.strip()


def find(lines, fn):
    starts = []
    for i, l in enumerate(lines):
        if re.match(rf'^[A-Za-z_][^;/]*\b{re.escape(fn)}\s*\(', l) or \
                re.match(rf'^EVT_DEFINE_USER_FUNC\(\s*{re.escape(fn)}\s*\)', l):
            j = i
            while j < len(lines) and '{' not in lines[j] and ';' not in lines[j]:
                j += 1
            if j < len(lines) and '{' in lines[j]:
                starts.append(i)
    if len(starts) != 1:
        return None
    s = starts[0]
    e = next((k for k in range(s, len(lines)) if lines[k].rstrip('\r\n') == '}'), None)
    if e is None:
        return None
    while s > 0 and e + 1 < len(lines) and lines[s - 1].startswith('#pragma') and lines[s - 1].rstrip().endswith(' on') \
            and lines[e + 1].startswith('#pragma') and lines[e + 1].rstrip().endswith(' off'):
        s, e = s - 1, e + 1
    return s, e


if len(sys.argv) != 2:
    sys.exit(__doc__)
if git('branch', '--show-current') != 'master' or git('status', '--porcelain'):
    sys.exit('spm-decomp must be on master and clean')
todo = {}
for line in open(sys.argv[1], encoding='utf-8'):
    if line.strip():
        u, f = line.split()[:2]
        todo.setdefault(u, []).append(f)
for unit, fns in todo.items():
    path = dec / f'src/{unit}.c'
    lines = path.read_bytes().decode('utf-8').splitlines(keepends=True)
    spans = {}
    for fn in fns:
        sp = find(lines, fn)
        if sp is None:
            print(f'{unit} {fn}: definition not found uniquely, left as is')
        else:
            spans[fn] = sp
    if not spans:
        continue
    for fn in spans:
        b = f'wip/{fn}'
        if git('rev-parse', '--verify', '-q', b, check=False) or git('ls-remote', '--heads', 'origin', b, check=False):
            b = f'wip/{fn}-master'
        git('branch', b, 'master')
        git('push', '-q', 'origin', b)
        spans[fn] = spans[fn] + (b,)
    for fn, (s, e, b) in sorted(spans.items(), key=lambda kv: -kv[1][0]):
        eol = '\r\n' if lines[s].endswith('\r\n') else '\n'
        lines[s:e + 1] = [f'// NOT_DECOMPILED {fn}{eol}']
    path.write_bytes(''.join(lines).encode('utf-8'))
    git('add', f'src/{unit}.c')
    git('commit', '-q', '-m', f'Move {", ".join(spans)} to wip/ (not exactly 100%)')
    print(f'{unit}: moved {len(spans)} ({", ".join(b for *_, b in spans.values())})')
