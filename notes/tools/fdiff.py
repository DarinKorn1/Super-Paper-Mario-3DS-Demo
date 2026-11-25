"""Compile one source file and show how one function differs from the original.

usage: python -I notes/tools/fdiff.py <unit> <function> [options]
  <unit>              source name without .c, e.g. mario_status
  --variants PREFIX   also rank every function in our object whose name starts with PREFIX
                      (renamed test copies) and show the diff of the best one
  --score             run the full `ninja`, then print the official % and the checksum state
  --no-build          reuse the existing object file
  --lines N           maximum diff lines to print (default 40)
  --root DIR          decomp checkout (default <project>/spm-decomp)
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('unit')
ap.add_argument('function')
ap.add_argument('--variants')
ap.add_argument('--score', action='store_true')
ap.add_argument('--no-build', action='store_true')
ap.add_argument('--lines', type=int, default=40)
ap.add_argument('--root', default=str(Path(__file__).resolve().parents[2] / 'spm-decomp'))
a = ap.parse_args()
root = Path(a.root)
unit = a.unit[:-2] if a.unit.endswith('.c') else a.unit
obj = f'build/EU0/src/{unit}.o'


def run(cmd):
    return subprocess.run(cmd, cwd=root, capture_output=True, text=True, errors='replace')


def fail(res, what):
    lines = [l for l in (res.stdout + res.stderr).splitlines() if l.strip()]
    keep = [l for l in lines if not re.match(r'\[\d+/\d+\]', l)]
    print(f'{what} FAILED')
    print('\n'.join(keep[:30]))
    sys.exit(1)


if not a.no_build:
    r = run(['ninja', obj])
    if r.returncode:
        fail(r, 'compile')

tmp = Path(tempfile.gettempdir()) / 'decomp-matcher'
tmp.mkdir(exist_ok=True)
ours_s = tmp / f'{unit}.ours.s'
r = run([str(root / 'build/tools/dtk.exe'), 'elf', 'disasm', obj, str(ours_s)])
if r.returncode:
    fail(r, 'disassemble')


def functions(path):
    out, name, body = {}, None, []
    for line in open(path, encoding='utf-8', errors='replace'):
        s = line.strip()
        if s.startswith('.fn '):
            name, body = s[4:].split(',')[0].strip().strip('"'), []
        elif s.startswith('.endfn'):
            if name:
                out[name] = body
            name = None
        elif name and s:
            s = re.sub(r'^/\*.*?\*/\s*', '', s)
            if s and not s.startswith('#'):
                body.append(re.sub(r'\s+', ' ', s))
    return out


def normalise(body):
    """Rename local branch labels by order of definition so their addresses do not count."""
    names = {}
    for l in body:
        m = re.match(r'(\.L_\w+):', l)
        if m:
            names[m.group(1)] = f'.L{len(names)}'
    return [re.sub(r'\.L_\w+', lambda m: names.get(m.group(0), m.group(0)), l) for l in body]


def shape(line):
    """The line with registers and symbol names blanked."""
    line = re.sub(r'"[^"]*"@\w+|@\d+@?\w*|\b\S+@(sda21|ha|l)\b', 'SYM', line)
    line = re.sub(r'\bbl \S+', 'bl SYM', line)
    return re.sub(r'\b(r|f|cr)\d+\b', r'\1N', line)


def pool_shape(line):
    return re.sub(r'^(addi \S+ \S+) -?(0x)?[0-9a-fA-F]+$', r'\1 IMM', shape(line))


orig_file = root / f'build/EU0/asm/{unit}.s'
orig_all = functions(orig_file)
if a.function not in orig_all:
    sys.exit(f'{a.function} not found in {orig_file}')
orig = normalise(orig_all[a.function])
ours_all = functions(ours_s)


def diff_of(name):
    mine = normalise(ours_all[name])
    sm = difflib.SequenceMatcher(None, orig, mine, autojunk=False)
    hunks = [op for op in sm.get_opcodes() if op[0] != 'equal']
    n = sum(max(i2 - i1, j2 - j1) for _, i1, i2, j1, j2 in hunks)
    return n, hunks, mine


target = a.function
if a.variants:
    names = [n for n in ours_all if n.startswith(a.variants) or n == a.function]
    if not names:
        sys.exit(f'no function starting with {a.variants} in our object')
    ranked = sorted(names, key=lambda n: (diff_of(n)[0], len(n)))
    print('best variants (differing lines):', ', '.join(f'{n}={diff_of(n)[0]}' for n in ranked[:8]))
    target = ranked[0]

if target not in ours_all:
    print(f'{target} is not in our object (still a stub, or inlined away)')
else:
    n, hunks, mine = diff_of(target)
    same_len = len(orig) == len(mine)
    reg = sum(1 for o, m in zip(orig, mine) if o != m and shape(o) == shape(m)) if same_len else 0
    pool = sum(1 for o, m in zip(orig, mine) if o != m and shape(o) != shape(m) and pool_shape(o) == pool_shape(m)) if same_len else 0
    other = sum(1 for o, m in zip(orig, mine) if o != m) - reg - pool if same_len else None
    print(f'{target}: orig {len(orig)} lines, ours {len(mine)} lines, {n} differing')
    if same_len:
        print(f'  line by line: register/label-only {reg}, pool-offset {pool}, other {other}'
              + ('  -> only numbering/labels/pool' if other == 0 and n else ''))
    shown = 0
    for tag, i1, i2, j1, j2 in hunks:
        block = [f'@@ line {i1} {tag}'] + [f'- {l}' for l in orig[i1:i2]] + [f'+ {l}' for l in mine[j1:j2]]
        room = a.lines - shown
        if room <= 0:
            print('... (more differences not shown)')
            break
        print('\n'.join(block[:room]))
        shown += min(len(block), room)

if a.score:
    r = run(['ninja'])
    if r.returncode:
        fail(r, 'ninja')
    out = r.stdout + r.stderr
    sums = re.findall(r'(main\.dol|relF\.rel): (\w+)', out)
    if sums:
        print('checksums:', ', '.join(f'{k} {v}' for k, v in sums))
    else:
        print('checksums: nothing relinked; build/EU0/ok', 'exists' if (root / 'build/EU0/ok').exists() else 'MISSING')
    rep = json.load(open(root / 'build/EU0/report.json', encoding='utf-8'))
    for u in rep['units']:
        if u['name'] == f'main/{unit}':
            for f in u.get('functions', []):
                if f['name'] == a.function:
                    print(f'report.json: {a.function} {f.get("fuzzy_match_percent", 0.0):.2f}%')
                    break
            else:
                print(f'report.json: {a.function} not listed')
