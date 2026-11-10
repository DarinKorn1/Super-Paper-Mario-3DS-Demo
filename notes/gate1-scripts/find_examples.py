"""Find the smallest generated functions containing given markers, and count functions using 64-bit casts.
Usage: python -I find_examples.py <func_index.json>"""
import json, re, sys
from collections import defaultdict

idx = json.load(open(sys.argv[1]))
by_file = defaultdict(list)
for name, (path, nl) in idx.items():
    by_file[path].append((name, nl))
markers = {
    'indirect_call (InvokeIndirectCpu)': 'InvokeIndirectCpu',
    'indirect_jump (InvokeIndirectJump)': 'InvokeIndirectJump',
    'jump table lowered to switch': 'switch (',
    'paired-single math (PPC_PsMaddInline)': 'PPC_PsMaddInline',
    'quantized load via GQR (PPC_PsqLGqrInline)': 'PPC_PsqLGqrInline',
    '64-bit cast (uint64_t / int64_t body)': 'uint64_t',
    'mulhw-style (>> 32)': '>> 32',
}
best = {k: [] for k in markers}
cnt = {k: 0 for k in markers}
sig = re.compile(r'^extern "C" \S+\s+(func_[0-9A-Fa-f]{8})\s*\(')
for path, funcs in by_file.items():
    lines = open(path, encoding='utf-8', errors='replace').readlines()
    pos = {}
    for i, l in enumerate(lines):
        m = sig.match(l)
        if m: pos[m.group(1)] = i
    for name, nl in funcs:
        i = pos.get(name)
        if i is None: continue
        body = ''.join(lines[i + 1:i + nl])      # skip the signature line, which itself mentions uint64_t for some ABIs
        for k, tok in markers.items():
            if tok in body:
                cnt[k] += 1
                best[k].append((nl, name))
for k in markers:
    best[k].sort()
    print(f'{k}: {cnt[k]} functions; smallest 5: {best[k][:5]}')
