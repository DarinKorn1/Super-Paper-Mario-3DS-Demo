"""Which runtime helpers / constructs do the generated functions call, and how many functions use each?
Usage: python -I gen_tokens.py <build_shards/base_common> <out json>
"""
import json, os, re, sys
from collections import Counter

root, out = sys.argv[1], sys.argv[2]
FUNC = re.compile(r'^extern "C" \S+\s+(func_[0-9A-Fa-f]{8})\s*\(')
CALL = re.compile(r'\b([A-Za-z_][A-Za-z0-9_:]*)\s*(?:<[^<>;()]*>)?\s*\(')
KEYWORDS = {'if', 'for', 'while', 'switch', 'return', 'sizeof', 'static_cast', 'reinterpret_cast', 'do', 'else', 'goto', 'case', 'uint32_t', 'int32_t'}
calls_total = Counter()
funcs_using = Counter()
nfuncs = 0
for f in sorted(os.listdir(root)):
    if not f.endswith('.cpp'):
        continue
    with open(os.path.join(root, f), encoding='utf-8', errors='replace') as fh:
        text = fh.read()
    # split into functions
    idx = [(m.start(), m.group(1)) for m in re.finditer(r'^extern "C" \S+\s+(func_[0-9A-Fa-f]{8})\s*\(', text, re.M)]
    for k, (pos, name) in enumerate(idx):
        end = idx[k + 1][0] if k + 1 < len(idx) else len(text)
        body = text[pos:end]
        nfuncs += 1
        seen = set()
        for m in CALL.finditer(body):
            t = m.group(1)
            if t in KEYWORDS or t.startswith('func_') or t.startswith('MemoryInline::'):
                continue
            calls_total[t] += 1
            seen.add(t)
        if 'switch (' in body: seen.add('<<switch>>'); calls_total['<<switch>>'] += body.count('switch (')
        if 'goto *' in body: seen.add('<<computed goto>>')
        for t in seen:
            funcs_using[t] += 1
res = {'functions': nfuncs,
       'top_calls_by_functions_using': [(t, funcs_using[t], calls_total[t]) for t, _ in funcs_using.most_common(120)]}
json.dump(res, open(out, 'w'), indent=1)
for t, nf, nc in res['top_calls_by_functions_using'][:80]:
    print(f'{nf:6d} funcs {nc:8d} uses  {t}')
