"""Per-thread CPU per frame, split by code category, for the sampler's window.

Inputs: a thread_sampler.ps1 output folder, the engine DLL that ran, the fps windows of the same run (from flipside_log.py's JSON),
llvm-nm, and projects\\spm\\MAP.txt (guest names).
CPU time per thread is exact (kernel+user time from the OS, interpolated to the window edges).
The category split of a thread's time uses its instruction-pointer samples: share of samples whose leaf is in translated game code,
the graphics layer, audio, other runtime code, or a system/driver DLL (the last is "running or waiting", so its running part is
estimated as CPU time minus the engine-code parts).

Usage: python -I flipside_threads.py <sampler dir> <engine_usa.dll> <llvm-nm.exe> <MAP.txt> <fps json> <first idx> <last idx> [out.json]
  first/last idx = the fps windows (2 s each) that cover the sampler window.
"""
import bisect, collections, csv, datetime as dt, json, re, statistics, subprocess, sys

sdir, dll, nm_exe, map_path, fps_json, i0, i1 = sys.argv[1:8]
i0, i1 = int(i0), int(i1)
out_json = sys.argv[8] if len(sys.argv) > 8 else None
BASE = 0x180000000

def parse_utc(s):
    s = s.strip()
    m = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?Z', s)
    frac = float(m.group(2)) if m.group(2) else 0.0
    return dt.datetime.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() + frac

meta = dict(l.strip().split('=', 1) for l in open(sdir + '\\meta.txt') if '=' in l)
w0, w1 = parse_utc(meta['window_start_utc']), parse_utc(meta['window_end_utc'])
wall_ms = (w1 - w0) * 1000.0
rows = json.load(open(fps_json))['rows']
sel = [r for r in rows if i0 <= r['idx'] <= i1]
fps_mean = statistics.mean(r['fps'] for r in sel)
frames = fps_mean * (w1 - w0)
ms_per_frame_wall = wall_ms / frames
print(f'window {meta["window_start_utc"]} .. {meta["window_end_utc"]} = {wall_ms/1000:.1f} s; fps windows {i0}-{i1}: mean {fps_mean:.2f} fps -> about {frames:.0f} frames ({ms_per_frame_wall:.2f} ms of wall time per frame)')

# ---- symbols ----
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
def symname(rva):
    i = bisect.bisect_right(addrs, rva) - 1
    return syms[i][1] if i >= 0 else '?'
CATS = [
    ('translated game code', re.compile(r'^func_[0-9A-Fa-f]{8}(_statefree)?$')),
    ('graphics layer', re.compile(r'(?i)^(aurora|gx|hlegxstate|gxstream|gxcp)|aurora::|GX_HLE|^GX_|GX__|gx_|wgpu|dawn|AuroraTake|aurora_|VI_HLE_Present|imgui|ImGui|XXH')),
    ('audio', re.compile(r'(?i)^ax|AxDsp|AXWii|audio|\bax_|DSP|PushAudio|mixer')),
    ('scheduler / fibers / OS emulation', re.compile(r'(?i)fiber|HostContext|^OS|OS_|os_|Scheduler|SelectThread|SwitchTo|SleepPrecisely|VIWait')),
    ('disc / save I/O', re.compile(r'(?i)dvd|nand|isfs|IOS_|ios_')),
]
def engine_cat(n):
    for c, rx in CATS:
        if rx.search(n): return c
    return 'other runtime'
SYS_MODS = {'ntdll.dll', 'kernelbase.dll', 'kernel32.dll', 'win32u.dll', 'user32.dll', 'gdi32.dll', 'combase.dll', 'rpcrt4.dll'}
DRIVER_HINT = re.compile(r'(?i)^(d3d|dxgi|igd|ig\w*icd|webgpu_dawn|dxcompiler|dxil|d3d12core|nvwgf|amdxx|dxgkrnl|ig9|ig11|igc)')
def mod_cat(m):
    ml = m.lower()
    if ml == 'engine_usa.dll': return None
    if ml in SYS_MODS: return 'Windows system DLLs'
    if DRIVER_HINT.search(m): return 'graphics driver / Dawn'
    if ml.startswith('sdl3'): return 'SDL'
    if ml in ('libc++.dll', 'ucrtbase.dll', 'msvcp140.dll', 'vcruntime140.dll', 'libunwind.dll', 'msvcrt.dll'): return 'C/C++ runtime'
    return 'other DLL: ' + m

# ---- timeline: exact CPU ms per thread in the window ----
tl = collections.defaultdict(list)
names = {}
for r in csv.DictReader(open(sdir + '\\threads_timeline.csv')):
    t = parse_utc(r['utc']); tl[int(r['tid'])].append((t, float(r['cpu_ms'])))
    if r['name']: names[int(r['tid'])] = r['name']
def cpu_at(series, t):
    ts = [x[0] for x in series]
    i = bisect.bisect_left(ts, t)
    if i == 0: return series[0][1]
    if i >= len(series): return series[-1][1]
    (ta, ca), (tb, cb) = series[i - 1], series[i]
    return ca + (cb - ca) * (t - ta) / (tb - ta) if tb > ta else ca
thread_cpu = {}
for tid, s in tl.items():
    if len(s) < 2: continue
    thread_cpu[tid] = cpu_at(s, w1) - cpu_at(s, w0)

# ---- rip samples ----
S = collections.defaultdict(lambda: collections.Counter())
leaf_names = collections.defaultdict(collections.Counter)
tot = collections.Counter()
for r in csv.DictReader(open(sdir + '\\rip_samples.csv')):
    tid = int(r['tid']); mod = r['module']; tot[tid] += 1
    mc = mod_cat(mod)
    if mc is None:
        n = symname(int(r['rva_hex'], 16)) if r['rva_hex'] else '?'
        S[tid][engine_cat(n)] += 1; leaf_names[tid][n] += 1
    else:
        S[tid][mc] += 1; leaf_names[tid][mod] += 1

def role(tid):
    c = S[tid]; n = tot[tid]
    if n == 0: return '?'
    top = leaf_names[tid].most_common(6)
    topn = ' '.join(x[0] for x in top)
    if 'AXWii' in topn or 'MixWorker' in topn or 'AxDsp' in topn: return 'audio mix worker'
    if c['translated game code'] / n > 0.02: return 'game thread (guest code)'
    if re.search(r'frame_worker|aurora::', topn) and c['graphics layer'] / n > 0.05: return 'renderer frame worker'
    if re.search(r'(?i)SleepPrecisely|VBlank|vblank', topn): return 'vblank/timer thread'
    if re.search(r'(?i)igd|d3d|dawn', topn): return 'GPU driver / Dawn thread'
    if 'SDL' in topn: return 'SDL / audio output thread'
    return 'idle or unidentified'

result = []
print(f'\nprocess total: {sum(thread_cpu.values())/wall_ms*100:.0f}% of one core ({sum(thread_cpu.values())/wall_ms:.2f} cores busy), {sum(thread_cpu.values())/frames:.2f} CPU ms per frame, {len(thread_cpu)} threads')
hdr = ['tid', 'role', 'cpu ms/frame', 'busy %', 'translated', 'graphics', 'audio', 'sched/OS', 'disc', 'other rt', 'system+driver (running est.)']
print(' | '.join(hdr))
for tid, c in sorted(thread_cpu.items(), key=lambda kv: -kv[1]):
    cpu_pf = c / frames
    if cpu_pf < 0.02: continue
    n = tot[tid]
    share = lambda k: (S[tid][k] / n * ms_per_frame_wall) if n else 0.0
    eng = {k: share(k) for k in ['translated game code', 'graphics layer', 'audio', 'scheduler / fibers / OS emulation', 'disc / save I/O', 'other runtime']}
    sysrun = max(0.0, cpu_pf - sum(eng.values()))
    sysleaf = {k: share(k) for k in S[tid] if k not in eng}
    row = dict(tid=tid, role=role(tid), cpu_ms_per_frame=cpu_pf, busy_pct=c / wall_ms * 100, engine=eng, system_running_est=sysrun, system_leaf_wall_share=sysleaf, samples=n,
               top_leaf=leaf_names[tid].most_common(5))
    result.append(row)
    print(f'{tid} | {row["role"]} | {cpu_pf:6.2f} | {row["busy_pct"]:5.1f} | ' + ' | '.join(f'{eng[k]:5.2f}' for k in eng) + f' | {sysrun:5.2f}')
print('\nleaf detail for the busiest threads:')
for row in result[:8]:
    print(f'  tid {row["tid"]} ({row["role"]}): samples {row["samples"]}; top leaves: ' + '; '.join(f'{n[:60]} x{c}' for n, c in row['top_leaf']))
    print('     wall-share by leaf category (ms of wall per frame): ' + ', '.join(f'{k} {v:.2f}' for k, v in sorted(row['engine'].items(), key=lambda x: -x[1]) if v > 0.005) + ' | ' + ', '.join(f'{k} {v:.2f}' for k, v in sorted(row['system_leaf_wall_share'].items(), key=lambda x: -x[1]) if v > 0.005))
if out_json: json.dump(dict(frames=frames, wall_ms=wall_ms, fps_mean=fps_mean, threads=result), open(out_json, 'w'), indent=1)
