"""Finish one function: measure it with a full build and file it where the measurement says.

usage: python -I notes/tools/finish.py <unit> <function> "<short note: what was hard / what fixed it>"
Run once per function, on master, with that function's edits uncommitted in the working tree.
- runs the full `ninja` and reads the official % from build/EU0/report.json (not counted as an attempt)
- exactly 100%: commits "Decompile <function>" on master (local only; the coordinator pushes master)
- anything else: commits on a new branch wip/<function>, pushes that branch, switches back to master
- no edits at all: records "incomplete"
Afterwards no more builds of the function are possible. Prints one line.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
dec = proj / 'spm-decomp'
store = proj / 'notes/phase3-queue/attempts.json'
BAD = re.compile(r'^(build|orig)/|\.(o|dol|rel|elf|s|iso|rvz|wbfs)$')


def git(*c, check=True):
    r = subprocess.run(['git', *c], cwd=dec, capture_output=True, text=True, errors='replace', timeout=300)
    if check and r.returncode:
        sys.exit(f'BLOCKED: git {c[0]} failed: {(r.stderr or r.stdout).strip()[:400]}')
    return r.stdout.strip()


def official(unit, fn):
    rep = json.load(open(dec / 'build/EU0/report.json', encoding='utf-8'))
    for u in rep['units']:
        if u['name'] == f'main/{unit}':
            for f in u.get('functions', []):
                if f['name'] == fn:
                    return f.get('fuzzy_match_percent', 0.0)
    return None


if len(sys.argv) != 4:
    sys.exit(__doc__)
unit, fn, note = sys.argv[1][:-2] if sys.argv[1].endswith('.c') else sys.argv[1], sys.argv[2], sys.argv[3]
if git('branch', '--show-current') != 'master':
    sys.exit('BLOCKED: spm-decomp is not on master')
data = json.loads(store.read_text(encoding='utf-8')) if store.exists() else {}
rec = data.get(f'{unit}:{fn}')
if rec is None:
    sys.exit(f'BLOCKED: no builds recorded for {fn}; build only with build.py')
if rec.get('result'):
    sys.exit(f'BLOCKED: {fn} is already finished ({rec["result"]["ref"]})')
pat = r'^// NOT_DECOMPILED (\S+)'
src_now = (dec / f'src/{unit}.c').read_text(encoding='utf-8', errors='replace')
others = sorted(set(re.findall(pat, git('show', f'HEAD:src/{unit}.c'), re.M)) - set(re.findall(pat, src_now, re.M)) - {fn})
if others:
    sys.exit(f'BLOCKED: other functions are also edited ({others[:5]}); finish works on one function at a time')
changed = [l[3:].strip('"') for l in git('status', '--porcelain', '-uall').splitlines()]
bad = [p for p in changed if BAD.search(p)]
if bad:
    sys.exit(f'BLOCKED: refusing to commit {bad[:3]}')

pct, ref = None, '-'
if changed:
    r = subprocess.run(['ninja'], cwd=dec, capture_output=True, text=True, errors='replace', timeout=3600)
    if r.returncode == 0:
        pct = official(unit, fn)
    if pct == 100.0:
        git('add', '-A')
        git('commit', '-q', '-m', f'Decompile {fn}')
        ref = git('rev-parse', '--short', 'HEAD')
    else:
        branch = f'wip/{fn}'
        n = 2
        while git('rev-parse', '--verify', '-q', branch, check=False) or \
                git('ls-remote', '--heads', 'origin', branch, check=False):
            branch, n = f'wip/{fn}-{n}', n + 1
        git('switch', '-q', '-c', branch)
        git('add', '-A')
        what = 'does not build' if pct is None else f'measured {pct:.2f}%'
        git('commit', '-q', '-m', f'WIP {fn} ({what})')
        ref = f'{branch} {git("rev-parse", "--short", "HEAD")}'
        pushed = subprocess.run(['git', 'push', '-q', 'origin', branch], cwd=dec, capture_output=True, text=True,
                                timeout=300).returncode == 0
        git('switch', '-q', 'master')
        if not pushed:
            ref += ' (push failed)'
rec['result'] = {'pct': pct, 'ref': ref, 'note': note, 'logged': False}
rec['cap'] = rec['builds']
data[f'{unit}:{fn}'] = rec
store.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
shown = 'no edits' if not changed else 'does not build' if pct is None else f'{pct:.2f}%'
print(f'{fn}: {shown}, {rec["builds"]} builds, {ref}')
