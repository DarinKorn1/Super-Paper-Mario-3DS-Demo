"""Print generated C++ for a function. Usage: python -I extract_func.py <func_index.json> <func_XXXXXXXX> [max_lines]"""
import json, re, sys
idx = json.load(open(sys.argv[1]))
name = sys.argv[2]
maxl = int(sys.argv[3]) if len(sys.argv) > 3 else 120
if name not in idx:
    print('not in generated base_common:', name); sys.exit(1)
path, nl = idx[name]
lines = open(path, encoding='utf-8', errors='replace').readlines()
for i, l in enumerate(lines):
    if re.match(r'^extern "C" \S+\s+' + re.escape(name) + r'\s*\(', l):
        body = lines[i:i + nl]
        print(f'// {name}: {nl} generated lines (showing up to {maxl})')
        print(''.join(body[:maxl]), end='')
        if nl > maxl: print(f'// ... {nl - maxl} more lines')
        break
