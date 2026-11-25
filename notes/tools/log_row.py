"""Append one row to notes/phase3-log.md (never needs the log to be read).

usage: python -I notes/tools/log_row.py FILE FUNCTION SIZE BYTES MATCHED PERCENT ATTEMPTS REF "NOTES"
  SIZE: small | medium | large | huge
  MATCHED: yes | "functionally complete" | incomplete | deferred
Options (may be given with a row, or alone):
  --defer huge|retry   also record the function in notes/deferred.md
  --push               commit notes/ in the outer repo, pull --rebase and push
"""
import re
import subprocess
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
log = proj / 'notes/phase3-log.md'
args = sys.argv[1:]
push = '--push' in args
if push:
    args.remove('--push')
defer = None
if '--defer' in args:
    i = args.index('--defer')
    defer = args[i + 1]
    del args[i:i + 2]

if args:
    if len(args) != 9:
        sys.exit(f'need 9 values, got {len(args)} (see the usage at the top of this script)')
    f, fn, size, nbytes, matched, pct, attempts, ref, notes = [x.replace('|', '/').replace('\n', ' ') for x in args]
    with open(log, 'rb') as fh:
        fh.seek(0, 2)
        fh.seek(max(0, fh.tell() - 8000))
        tail = fh.read().decode('utf-8', errors='replace')
    nums = re.findall(r'^\| (\d+) \|', tail, re.M)
    n = int(nums[-1]) + 1 if nums else 853
    prefix = '' if tail.endswith('\n') else '\n'
    with open(log, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(f'{prefix}| {n} | {f} | {fn} | {size} | {nbytes} | {matched} | {pct} | {attempts} | {ref} | {notes} |\n')
    print(f'row {n}')
    if defer:
        marker = {'huge': '<!-- huge-end -->', 'retry': '<!-- retry-end -->'}[defer]
        d = proj / 'notes/deferred.md'
        text = d.read_text(encoding='utf-8')
        why = notes if defer == 'huge' else f'{pct}%, {ref}'
        d.write_text(text.replace(marker, f'| {fn} | {f} | {nbytes} | {why} |\n{marker}'), encoding='utf-8', newline='\n')
        print('recorded in deferred.md')

if push:
    def git(*c, check=True):
        r = subprocess.run(['git', *c], cwd=proj, capture_output=True, text=True)
        if check and r.returncode:
            sys.exit(f'git {c[0]} failed: {(r.stderr or r.stdout).strip()[:600]}')
        return r
    paths = ['notes/phase3-log.md', 'notes/deferred.md', 'notes/resume.md', 'notes/phase3-queue', 'notes/phase3-plan.md']
    git('add', '--', *[p for p in paths if (proj / p).exists()])
    if git('diff', '--cached', '--quiet', check=False).returncode:
        git('commit', '-q', '-m', 'Phase 3 log update\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>')
    if git('push', '-q', 'origin', 'master', check=False).returncode:
        git('pull', '-q', '--rebase', '--autostash', 'origin', 'master')
        git('push', '-q', 'origin', 'master')
    print('outer repo pushed')
