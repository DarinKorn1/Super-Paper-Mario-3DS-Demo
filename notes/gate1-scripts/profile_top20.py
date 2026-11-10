"""Top-20 table (time in the function itself plus OS calls it makes directly) and who calls the big sleeps.
Usage: python -I profile_top20.py <llvm-nm.exe> <engine_usa.dll> <profile_stacks.txt> <MAP.txt>"""
import bisect, collections, re, subprocess, sys
nm_exe, dll, stacks_path, map_path = sys.argv[1:5]
BASE = 0x180000000
out = subprocess.run([nm_exe, '--defined-only', '-n', '-C', dll], capture_output=True, text=True, errors='replace').stdout
syms = []
for line in out.splitlines():
    p = line.split(' ', 2)
    if len(p) == 3 and p[1] in 'Tt':
        try: syms.append((int(p[0], 16) - BASE, p[2]))
        except ValueError: pass
syms.sort(); addrs = [a for a, _ in syms]
guest = {}
for line in open(map_path, encoding='utf-8', errors='replace'):
    p = line.split(None, 1)
    if len(p) == 2: guest[p[0].upper()] = p[1].strip()
def name(r):
    i = bisect.bisect_right(addrs, r) - 1
    return syms[i][1] if i >= 0 else '?'
def pretty(n):
    m = re.match(r'^func_([0-9A-Fa-f]{8})(_statefree)?$', n)
    if m: return f'{n} ({guest.get(m.group(1).upper(), "?")})'
    n = re.sub(r'std::__1::', 'std::', n)
    return n[:100]
samples = [l.split() for l in open(stacks_path) if l.split()]
N = len(samples)
excl = collections.Counter()
sleep_callers = collections.Counter(); cv_callers = collections.Counter(); mix_callers = collections.Counter()
for toks in samples:
    exe = [int(t, 16) for t in toks if t != '-']
    first = name(exe[0]) if exe else '(no engine frame)'
    excl[first] += 1
    names = [name(r) for r in exe]
    if first.startswith('(anonymous namespace)::SleepPreciselyUntil'):
        sleep_callers[' < '.join(pretty(n)[:48] for n in names[1:4])] += 1
    if first.startswith('std::__1::cv_status') or 'condition_variable::wait' in first:
        cv_callers[' < '.join(pretty(n)[:48] for n in names[1:5])] += 1
print(f'N={N}')
print('TOP 20 (self + OS calls made directly by the function):')
for k, (n, v) in enumerate(excl.most_common(20), 1):
    print(f'{k:2d}. {100*v/N:5.2f}%  {pretty(n)}')
print('\nSleepPreciselyUntil callers:')
for n, v in sleep_callers.most_common(4): print(f'  {100*v/N:5.1f}%  {n}')
print('\ncondition_variable wait callers:')
for n, v in cv_callers.most_common(5): print(f'  {100*v/N:5.1f}%  {n}')
