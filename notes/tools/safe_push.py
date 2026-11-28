"""The only way master of spm-decomp is pushed: build, check both checksums, push only if both are OK.

usage: python -I notes/tools/safe_push.py
Needs spm-decomp on master with a clean tree. Runs `ninja`, then `dtk shasum -c config/EU0/build.sha1`,
prints the result and runs `git push origin master` only if main.dol and relF.rel are both OK.
"""
import re
import subprocess
import sys
from pathlib import Path

dec = Path(__file__).resolve().parents[2] / 'spm-decomp'


def run(cmd, timeout=3600):
    return subprocess.run(cmd, cwd=dec, capture_output=True, text=True, errors='replace', timeout=timeout)


if run(['git', 'branch', '--show-current']).stdout.strip() != 'master':
    sys.exit('REFUSED: spm-decomp is not on master')
if run(['git', 'status', '--porcelain']).stdout.strip():
    sys.exit('REFUSED: spm-decomp has uncommitted changes')
b = run(['ninja'])
if b.returncode:
    tail = [l for l in (b.stdout + b.stderr).splitlines() if l.strip() and not re.match(r'\[\d+/\d+\]', l)]
    print('\n'.join(tail[-15:]))
    sys.exit('REFUSED: ninja failed')
s = run([str(dec / 'build/tools/dtk.exe'), 'shasum', '-c', 'config/EU0/build.sha1'], timeout=600)
plain = re.sub(r'\x1b\[[0-9;]*m', '', s.stdout + s.stderr)
sums = dict(re.findall(r'(main\.dol|relF\.rel): (\w+)', plain))
print('checksums: ' + ', '.join(f'{k} {sums.get(k, "MISSING")}' for k in ('main.dol', 'relF.rel')))
if sums.get('main.dol') != 'OK' or sums.get('relF.rel') != 'OK' or s.returncode:
    sys.exit('REFUSED: checksums not both OK, nothing pushed')
p = run(['git', 'push', '-q', 'origin', 'master'], timeout=300)
if p.returncode:
    sys.exit(f'push failed: {(p.stderr or p.stdout).strip()[:400]}')
print('pushed master to origin')
