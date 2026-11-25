"""Print only the functions that are NOT exactly 100% in build/EU0/report.json.

usage: python -I notes/tools/check_matches.py [--root DIR] [sources of names]
  name ...             function names on the command line
  --list FILE          names (first word of each line)
  --commits RANGE      names from "Decompile <name>" commit subjects, e.g. master..ag/work
  --ag-results         names of rows marked matched (Yes) in <root>/notes/ag-results.md
  --unit UNIT          every function of one source file (to see if it can be linked)
Exit code 0 = all exactly 100%. Run `ninja` in the same checkout first.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('names', nargs='*')
ap.add_argument('--root', default=str(Path(__file__).resolve().parents[2] / 'spm-decomp'))
ap.add_argument('--list')
ap.add_argument('--commits')
ap.add_argument('--ag-results', action='store_true')
ap.add_argument('--unit')
a = ap.parse_args()
root = Path(a.root)

rep = json.load(open(root / 'build/EU0/report.json', encoding='utf-8'))
pct = {}
for u in rep['units']:
    for f in u.get('functions', []):
        pct.setdefault(f['name'], []).append((u['name'], f.get('fuzzy_match_percent', 0.0)))

names = list(a.names)
if a.list:
    names += [l.split()[0] for l in open(a.list, encoding='utf-8') if l.strip()]
if a.commits:
    log = subprocess.run(['git', 'log', '--format=%s', a.commits], cwd=root, capture_output=True, text=True, check=True).stdout
    for s in log.splitlines():
        m = re.match(r'Decompile (.+)', s)
        if m:
            names += [w for w in re.split(r'[,\s]+', m.group(1)) if re.match(r'^(func_\w+|\w+_\w+|[a-z]+[A-Z]\w*)$', w)]
if a.ag_results:
    for line in open(root / 'notes/ag-results.md', encoding='utf-8'):
        c = [x.strip() for x in line.split('|')]
        if len(c) > 8 and any(x.lower().startswith('yes') for x in c[6:8]):
            names.append(c[3].strip('`'))
if a.unit:
    unit = a.unit[:-2] if a.unit.endswith('.c') else a.unit
    names += [f['name'] for u in rep['units'] if u['name'] == f'main/{unit}' for f in u.get('functions', [])]

names = list(dict.fromkeys(names))
if not names:
    sys.exit('no function names to check')
bad = 0
for n in names:
    found = pct.get(n)
    if not found:
        print(f'{n}: NOT IN REPORT')
        bad += 1
        continue
    low = [(u, p) for u, p in found if p != 100.0]
    if low:
        bad += 1
        print(f'{n}: ' + ', '.join(f'{p:.2f}% ({u})' for u, p in low))
print(f'checked {len(names)}, not exactly 100%: {bad}')
sys.exit(1 if bad else 0)
