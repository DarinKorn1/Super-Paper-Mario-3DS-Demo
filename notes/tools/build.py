"""The only way a matching subagent builds a function: counts every build and refuses past the cap.

usage: python -I notes/tools/build.py <unit> <function> [--variants PREFIX] [--lines N]
Runs fdiff.py (compile + diff) once and counts it as one attempt, even if the compile fails.
Cap from the function's real size (symbols.txt): up to 128 B 4, 129-640 B 6, 641-2,044 B 8, bigger: refused.
Good-enough: once a build shows only register/label/pool differences and 3 builds are used, no more builds.
Counts live in notes/phase3-queue/attempts.json; finish.py and land.py read them for the log.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

proj = Path(__file__).resolve().parents[2]
dec = proj / 'spm-decomp'
store = proj / 'notes/phase3-queue/attempts.json'


def size_of(fn):
    for line in open(dec / 'config/EU0/symbols.txt', encoding='utf-8'):
        m = re.match(r'(\S+) = \.text:0x[0-9A-F]+; // type:function size:0x([0-9A-F]+)', line)
        if m and m.group(1) == fn:
            return int(m.group(2), 16)
    return None


def cap_of(size):
    return 4 if size <= 128 else 6 if size <= 640 else 8 if size <= 2044 else 0


def load():
    return json.loads(store.read_text(encoding='utf-8')) if store.exists() else {}


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 2 or args[0].startswith('-') or args[1].startswith('-'):
        sys.exit(__doc__)
    if any(x in args for x in ('--score', '--no-build', '--root')):
        sys.exit('REFUSED: --score/--no-build/--root are not allowed here (finish.py measures the result)')
    unit, fn = args[0][:-2] if args[0].endswith('.c') else args[0], args[1]
    size = size_of(fn)
    if size is None:
        sys.exit(f'REFUSED: {fn} is not a function in symbols.txt')
    cap = cap_of(size)
    data = load()
    rec = data.setdefault(f'{unit}:{fn}', {'builds': 0, 'size': size, 'cap': cap, 'good_enough': False, 'last': ''})
    if rec['builds'] >= rec['cap']:
        sys.exit(f'CAP REACHED: {fn} used {rec["builds"]}/{rec["cap"]} builds. No more builds: run finish.py now.')
    rec['builds'] += 1
    store.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    r = subprocess.run([sys.executable, '-I', str(proj / 'notes/tools/fdiff.py'), unit, fn, *args[2:]],
                       capture_output=True, text=True, errors='replace', timeout=900)
    out = (r.stdout + r.stderr).rstrip()
    m = re.search(rf'^{re.escape(fn)}: orig (\d+) lines, ours (\d+) lines, (\d+) differing', out, re.M)
    if m and m.group(3) == '0':
        rec['last'] = 'no differing lines'
    elif 'only numbering/labels/pool' in out and not re.search(r'^best variants', out, re.M):
        rec['last'] = 'only numbering/labels/pool'
        if rec['builds'] >= 3:
            rec['good_enough'] = True
            rec['cap'] = rec['builds']
    elif r.returncode:
        rec['last'] = 'build failed'
    else:
        rec['last'] = 'differs'
    store.write_text(json.dumps(data, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print(out)
    left = rec['cap'] - rec['builds']
    note = ' GOOD-ENOUGH reached: stop and run finish.py.' if rec['good_enough'] else ''
    print(f'[build {rec["builds"]}/{rec["cap"]} for {fn}; {left} left]{note}')
    sys.exit(r.returncode)
