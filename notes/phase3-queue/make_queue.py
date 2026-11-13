# usage: python -I notes/phase3-queue/make_queue.py <file.c>   -> writes notes/phase3-queue/<file>.txt (name addr bytes, smallest first)
import re, sys
f = sys.argv[1]
root = 'spm-decomp/config/EU0/'
lo = hi = None; cur = None
for line in open(root + 'splits.txt', encoding='utf-8'):
    if line.rstrip().endswith(':') and not line.startswith('\t'):
        cur = line.strip()[:-1]
    elif cur == f:
        m = re.search(r'\.text\s+start:0x([0-9A-F]+) end:0x([0-9A-F]+)', line)
        if m: lo, hi = int(m.group(1), 16), int(m.group(2), 16)
fns = []
for line in open(root + 'symbols.txt', encoding='utf-8'):
    m = re.match(r'(\S+) = \.text:0x([0-9A-F]+); // type:function size:0x([0-9A-F]+)', line)
    if m and lo <= int(m.group(2), 16) < hi:
        fns.append((int(m.group(3), 16), m.group(1), m.group(2)))
fns.sort()
open(f'notes/phase3-queue/{f[:-2]}.txt', 'w').write(''.join(f'{n} {a} {s}\n' for s, n, a in fns))
print(f, len(fns), 'functions')
