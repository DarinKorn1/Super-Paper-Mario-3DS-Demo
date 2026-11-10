"""Size statistics and sample extraction for the translator's generated C++ (wiicompiled/generated/build_shards).

Usage: python -I gen_stats.py <build_shards dir> <out json> <samples dir>
"""
import json, os, re, sys
from collections import Counter

root, out, samples = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(samples, exist_ok=True)
FUNC = re.compile(r'^extern "C" (?:void|uint64_t|MkwStateFreeResult2|\w+)\s+(func_[0-9A-Fa-f]{8})\s*\(')
by_dir = {}
funcs = {}            # name -> (file, start_line_in_file, nlines)
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        ext = os.path.splitext(f)[1].lower()
        sub = os.path.relpath(dp, root)
        d = by_dir.setdefault(sub, {'files': 0, 'lines': 0, 'bytes': 0, 'cpp': 0, 'h': 0})
        size = os.path.getsize(p)
        d['files'] += 1
        d['bytes'] += size
        if ext == '.cpp': d['cpp'] += 1
        if ext == '.h': d['h'] += 1
        if ext in ('.cpp', '.h', '.inc'):
            with open(p, encoding='utf-8', errors='replace') as fh:
                lines = fh.readlines()
            d['lines'] += len(lines)
            if ext == '.cpp' and sub == 'base_common':
                starts = []
                for i, line in enumerate(lines):
                    m = FUNC.match(line)
                    if m:
                        starts.append((m.group(1), i))
                for k, (name, i) in enumerate(starts):
                    j = starts[k + 1][1] if k + 1 < len(starts) else len(lines)
                    # trim the '#line' directive/includes that precede the next function
                    body = lines[i:j]
                    while body and (body[-1].startswith('#') or not body[-1].strip()):
                        body.pop()
                    funcs[name] = (p, i, len(body))

sizes = sorted((v[2], k) for k, v in funcs.items())
n = len(sizes)
def pct(q): return sizes[min(n - 1, int(q * n))]
summary = {
    'by_dir': by_dir,
    'function_definitions_in_base_common': n,
    'lines_per_function': {'min': sizes[0], 'p25': pct(.25), 'median': pct(.5), 'p75': pct(.75), 'p95': pct(.95), 'max': sizes[-1],
                           'mean': sum(s for s, _ in sizes) / n},
}
json.dump(summary, open(out, 'w'), indent=1)
print(json.dumps(summary, indent=1))

def dump(label, name):
    p, i, ln = funcs[name]
    with open(p, encoding='utf-8', errors='replace') as fh:
        lines = fh.readlines()
    with open(os.path.join(samples, f'{label}_{name}.cpp.txt'), 'w') as fh:
        fh.write(f'// {label}: {name}, {ln} lines, from {os.path.basename(p)}\n')
        fh.writelines(lines[i:i + ln])

# pick samples: a small one, a median one, and (separately, by feature) found with grep in a later step
want = {'small': 25, 'median': sizes[n // 2][0], 'p90': pct(.9)[0]}
for label, target in want.items():
    best = min(sizes, key=lambda t: abs(t[0] - target))
    dump(label, best[1])
json.dump({k: [v[0], v[2]] for k, v in funcs.items()}, open(os.path.join(samples, 'func_index.json'), 'w'))
