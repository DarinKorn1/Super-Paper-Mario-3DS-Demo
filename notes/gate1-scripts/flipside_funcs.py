"""Top translated functions (func_XXXXXXXX) by time in the game thread, from NSMBW_PROFILE's raw stacks.
self = the function was the innermost engine frame and the sample was inside it (not in a callee, not in a system DLL);
inclusive = the function was anywhere on the stack. ms/frame = share x wall time per frame of the profiled window.
Usage: python -I flipside_funcs.py <llvm-nm.exe> <engine_usa.dll> <profile_stacks.txt> <MAP.txt> <wall ms per frame>
"""
import bisect, collections, re, subprocess, sys
nm_exe, dll, stacks_path, map_path, ms_frame = sys.argv[1:6]
ms_frame = float(ms_frame)
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
FN = re.compile(r'^func_([0-9A-Fa-f]{8})(_statefree)?$')
def name(r):
    i = bisect.bisect_right(addrs, r) - 1
    return syms[i][1] if i >= 0 else '?'
samples = [l.split() for l in open(stacks_path) if l.split()]
N = len(samples)
selfc = collections.Counter(); incl = collections.Counter()
trans_self = 0; trans_incl_any = 0
for toks in samples:
    frames = [None if t == '-' else int(t, 16) for t in toks]
    exe = [f for f in frames if f is not None]
    seen = set()
    for f in exe:
        m = FN.match(name(f))
        if m and m.group(1) not in seen:
            incl[m.group(1).upper()] += 1; seen.add(m.group(1).upper())
    if seen: trans_incl_any += 1
    if frames[0] is not None:
        m = FN.match(name(frames[0]))
        if m: selfc[m.group(1).upper()] += 1; trans_self += 1
print(f'samples {N}; wall {ms_frame:.2f} ms per frame')
print(f'time with the innermost frame in translated game code: {100*trans_self/N:.1f}% = {trans_self/N*ms_frame:.2f} ms/frame')
print(f'samples with any translated function on the stack: {100*trans_incl_any/N:.1f}%')
def row(k, c): return f'{100*c/N:5.2f}% {c/N*ms_frame:5.2f} ms  func_{k}  {guest.get(k, "?")}'
print('\nTOP 20 translated functions by SELF time:')
for k, c in selfc.most_common(20): print('  ' + row(k, c))
print('\nTOP 20 translated functions by INCLUSIVE time (callees included):')
for k, c in incl.most_common(20): print('  ' + row(k, c))
cum = 0
print('\ncumulative self share of the top N translated functions:')
tops = [c for _, c in selfc.most_common()]
for n in (1, 5, 10, 20, 50, 100):
    print(f'  top {n:3d}: {100*sum(tops[:n])/max(trans_self,1):5.1f}% of translated-code self time ({len(tops)} distinct functions seen)')
