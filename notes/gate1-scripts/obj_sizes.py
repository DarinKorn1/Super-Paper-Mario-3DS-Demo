"""Sum code size of the compiled translated-game shard objects. Usage: python -I obj_sizes.py <native-build dir> <llvm-size.exe> <llvm-nm.exe>"""
import os, re, subprocess, sys
from collections import Counter

nb, size_exe, nm_exe = sys.argv[1], sys.argv[2], sys.argv[3]
objs = []
for dp, dn, fn in os.walk(nb):
    for f in fn:
        if re.match(r'^shard_.*\.cpp\.obj$', f):
            objs.append(os.path.join(dp, f))
sec = Counter()
n_funcs = 0
for o in objs:
    out = subprocess.run([size_exe, '-A', o], capture_output=True, text=True).stdout
    for line in out.splitlines():
        m = re.match(r'^(\.\S+)\s+(\d+)\s+\d+\s*$', line)
        if m:
            name = m.group(1)
            key = '.text' if name.startswith('.text') else name.split('$')[0] if name.startswith(('.xdata', '.pdata', '.rdata')) else name
            sec[key] += int(m.group(2))
    nm = subprocess.run([nm_exe, '--defined-only', '--extern-only', o], capture_output=True, text=True).stdout
    n_funcs += sum(1 for l in nm.splitlines() if re.search(r'\s[Tt]\s+func_[0-9A-Fa-f]{8}$', l))
print('shard objects:', len(objs))
print('defined func_ symbols (external text) across them:', n_funcs)
for k, v in sorted(sec.items(), key=lambda kv: -kv[1])[:12]:
    print(f'{k:12s} {v:12,d} bytes  {v / 1048576:8.2f} MiB')
