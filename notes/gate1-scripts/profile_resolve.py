"""Resolve profile_stacks.txt (exe RVAs, '-' = other module) against engine_usa.dll's own symbols.
Usage: python -I profile_resolve.py <llvm-nm.exe> <engine_usa.dll> <profile_stacks.txt> <MAP.txt> [explore|report]
"""
import bisect, collections, re, subprocess, sys, json

nm_exe, dll, stacks_path, map_path = sys.argv[1:5]
mode = sys.argv[5] if len(sys.argv) > 5 else 'explore'
BASE = 0x180000000

out = subprocess.run([nm_exe, '--defined-only', '-n', '-C', dll], capture_output=True, text=True, errors='replace').stdout
syms = []
for line in out.splitlines():
    parts = line.split(' ', 2)
    if len(parts) == 3 and parts[1] in 'Tt':
        try: syms.append((int(parts[0], 16) - BASE, parts[2]))
        except ValueError: pass
syms.sort()
addrs = [a for a, _ in syms]
guest = {}
for line in open(map_path, encoding='utf-8', errors='replace'):
    p = line.split(None, 1)
    if len(p) == 2: guest[p[0].upper()] = p[1].strip()

def name(rva):
    i = bisect.bisect_right(addrs, rva) - 1
    return syms[i][1] if i >= 0 else '?'

def pretty(n):
    m = re.match(r'^func_([0-9A-Fa-f]{8})(_statefree)?$', n)
    if m:
        g = guest.get(m.group(1).upper(), '')
        return f'{n} [{g}]' if g else n
    return n[:90]

CATS = [
    ('translated game code', re.compile(r'^func_[0-9A-Fa-f]{8}(_statefree)?$')),
    ('graphics (GX layer, aurora, Dawn glue)', re.compile(r'(?i)^(aurora|gx|hlegxstate|gxstream|gxcp)|aurora::|GX_HLE|^GX_|GX__|gx_|wgpu|dawn|AuroraTake|aurora_|VI_HLE_Present|Present|imgui|ImGui')),
    ('audio (AX/DSP mixer, audio output)', re.compile(r'(?i)^ax|AxDsp|AXWii|audio|\bax_|DSP|PushAudio|mixer|SDL_.*Audio')),
    ('scheduler / fibers / OS', re.compile(r'(?i)fiber|HostContext|^OS|OS_|os_|Scheduler|SelectThread|SwitchTo|idle')),
    ('disc / save I/O', re.compile(r'(?i)dvd|nand|isfs|IOS_|ios_')),
    ('memory access slow path', re.compile(r'(?i)MemoryInline|Memory::|Read\d+Slow|Write\d+Slow|ByteSwap|GuestFlat')),
]
def cat(n):
    for c, rx in CATS:
        if rx.search(n): return c
    return 'other runtime'

samples = []
for line in open(stacks_path):
    toks = line.split()
    if toks: samples.append(toks)
N = len(samples)
leaf_sys = 0
selfc = collections.Counter(); incl = collections.Counter()
catc = collections.Counter(); catc_nonidle = collections.Counter()
wait_by = collections.Counter(); wait_cat = collections.Counter()
for toks in samples:
    frames = [None if t == '-' else int(t, 16) for t in toks]
    exe = [f for f in frames if f is not None]
    seen = set()
    for f in exe:
        n = name(f)
        if n not in seen: incl[n] += 1; seen.add(n)
    if frames[0] is None:
        leaf_sys += 1
        first = name(exe[0]) if exe else '(no exe frame)'
        wait_by[first] += 1
        wait_cat[cat(first)] += 1
    else:
        n = name(frames[0]); selfc[n] += 1; catc[cat(n)] += 1

print(f'samples: {N}; symbols: {len(syms)}')
print(f'leaf inside another DLL (ntdll, ucrt, SDL3, Dawn, D3D12...): {leaf_sys} = {100*leaf_sys/N:.1f}%')
print(f'leaf inside engine_usa.dll code: {N-leaf_sys} = {100*(N-leaf_sys)/N:.1f}%')
print('\nSELF time inside engine_usa.dll by category (percent of ALL samples):')
for c, v in catc.most_common(): print(f'  {100*v/N:5.1f}%  {c}')
print('\nOS-wait samples (leaf in another DLL), by the category of the engine function that called into the OS:')
for c, v in wait_cat.most_common(): print(f'  {100*v/N:5.1f}%  {c}')
print('\ntop 25 callers into the OS (first engine frame of a wait sample):')
for n, v in wait_by.most_common(25): print(f'  {100*v/N:5.1f}%  {pretty(n)}')
print('\ntop 40 SELF symbols inside engine_usa.dll:')
for n, v in selfc.most_common(40): print(f'  {100*v/N:5.2f}%  {cat(n)[:14]:14s} {pretty(n)}')
print('\ntop 40 INCLUSIVE symbols (any frame on the stack):')
for n, v in incl.most_common(40): print(f'  {100*v/N:5.1f}%  {cat(n)[:14]:14s} {pretty(n)}')
json.dump({'N': N, 'leaf_sys': leaf_sys, 'selfc': selfc.most_common(60), 'incl': incl.most_common(80), 'wait_by': wait_by.most_common(40),
           'catc': catc.most_common(), 'wait_cat': wait_cat.most_common()}, open(stacks_path + '.resolved.json', 'w'), indent=1)
