"""Coordinator: verify, push and log every function a subagent finished in one unit.

usage: python -I notes/tools/land.py <unit>
1. full `ninja`, then check_matches.py on the functions finish.py put on master: all must be exactly 100%
2. functions put on wip/ branches must still be stubs on master; master may hold only "Decompile <name>" commits
   of finished functions beyond origin/master
3. safe_push.py (both checksums OK, then push master)
4. one log row per function with the measured % and the counted builds; notes committed and pushed
Prints one line per function. Refuses (exit 1, nothing pushed or logged) if any check fails.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
dec = proj / 'spm-decomp'
tools = proj / 'notes/tools'
store = proj / 'notes/phase3-queue/attempts.json'


def run(cmd, cwd=dec, timeout=3600):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors='replace', timeout=timeout)


if len(sys.argv) != 2:
    sys.exit(__doc__)
unit = sys.argv[1][:-2] if sys.argv[1].endswith('.c') else sys.argv[1]
data = json.loads(store.read_text(encoding='utf-8'))
recs = {k.split(':', 1)[1]: v for k, v in data.items()
        if k.startswith(unit + ':') and v.get('result') and not v['result']['logged']}
if not recs:
    sys.exit(f'{unit}: nothing finished to land')
if run(['git', 'branch', '--show-current']).stdout.strip() != 'master' or run(['git', 'status', '--porcelain']).stdout.strip():
    sys.exit('REFUSED: spm-decomp must be on master and clean')
on_master = [n for n, v in recs.items() if not v['result']['ref'].startswith(('wip/', '-'))]
subjects = run(['git', 'log', '--format=%s', 'origin/master..master']).stdout.splitlines()
extra = [s for s in subjects if not (s.startswith('Decompile ') and s[10:].strip() in on_master)]
if extra:
    sys.exit(f'REFUSED: unexpected commits on master: {extra[:3]}')
src = (dec / f'src/{unit}.c').read_text(encoding='utf-8', errors='replace')
stubs = set(re.findall(r'^// NOT_DECOMPILED (\S+)', src, re.M))
not_stub = [n for n in recs if n not in on_master and n not in stubs]
if not_stub:
    sys.exit(f'REFUSED: not exactly 100% but not a stub on master: {not_stub}')
if on_master:
    b = run(['ninja'])
    if b.returncode:
        sys.exit('REFUSED: ninja failed on master')
    c = run([sys.executable, '-I', str(tools / 'check_matches.py'), *on_master])
    if c.returncode:
        print('\n'.join(c.stdout.splitlines()[:20]))
        sys.exit('REFUSED: functions on master are not exactly 100%')
    p = run([sys.executable, '-I', str(tools / 'safe_push.py')])
    print('\n'.join((p.stdout + p.stderr).strip().splitlines()[-3:]))
    if p.returncode:
        sys.exit('REFUSED: safe_push.py did not push')
names = list(recs)
for i, n in enumerate(names):
    v = recs[n]
    r = v['result']
    pct = 100.0 if n in on_master else r['pct']
    if pct == 100.0:
        matched = 'yes'
    elif pct is not None and pct >= 98 and v.get('last') == 'only numbering/labels/pool':
        matched = 'functionally complete'
    else:
        matched = 'incomplete'
    size = v['size']
    cls = 'tiny' if size <= 64 else 'small' if size <= 128 else 'medium' if size <= 640 else 'large'
    shown = '-' if pct is None else ('100' if pct == 100.0 else f'{pct:.2f}')
    cmd = [sys.executable, '-I', str(tools / 'log_row.py'), f'{unit}.c', n, cls, str(size), matched, shown,
           str(v['builds']), r['ref'], r['note']]
    if matched != 'yes' and (pct is None or pct < 98 or matched == 'incomplete'):
        cmd += ['--defer', 'retry']
    r['logged'] = True
    store.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    if i == len(names) - 1:
        cmd.append('--push')
    lr = run(cmd, cwd=proj)
    if lr.returncode:
        sys.exit(f'log_row failed for {n}: {(lr.stderr or lr.stdout).strip()[:300]}')
    print(f'{n}: {shown}% measured, {v["builds"]} builds, {r["ref"]}')
