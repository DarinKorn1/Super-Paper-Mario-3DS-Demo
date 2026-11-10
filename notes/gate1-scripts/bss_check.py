"""Do translated relF functions use absolute addresses inside relF's bss (0x80F12640/0x80F12660 .. 0x80F1351C)?
Usage: python -I bss_check.py <build_shards/base_common>"""
import os, re, sys
from collections import Counter
root = sys.argv[1]
pat = re.compile(r'r(\d+) = 0x80F[01]0000u;\s*\n(?:[^\n]*\n){0,3}?\s*r\1 = \(r\1 \+ (-?\d+)\);')
direct = re.compile(r'0x80F1[2-3][0-9A-F]{3}u')
offs = Counter(); dcount = 0; funcs_with = set()
for f in os.listdir(root):
    if not f.endswith('.cpp'): continue
    text = open(os.path.join(root, f), encoding='utf-8', errors='replace').read()
    for m in pat.finditer(text):
        base = 0x80F10000 if '0x80F10000u' in text[m.start():m.end()] else 0x80F00000
        addr = base + int(m.group(2))
        if 0x80F12600 <= addr < 0x80F13560: offs[addr] += 1
    dcount += len(direct.findall(text))
print('addresses built as 0x80F10000 + imm in [0x80F12600, 0x80F13560):', sum(offs.values()), 'distinct', len(offs))
lo = sorted(offs)[:12]; print('lowest 12:', [hex(a) + 'x' + str(offs[a]) for a in lo])
print('direct 0x80F12xxx/0x80F13xxx literals:', dcount)
print('refs below 0x80F12660 (would be the first 0x20 bytes of an actual 0x80F12640 bss):', sum(c for a, c in offs.items() if a < 0x80F12660))
print('refs at/above 0x80F13500 (past the end of an actual 0x80F12640 bss, end 0x80F1351C-0x20=0x80F134FC):', sum(c for a, c in offs.items() if a >= 0x80F134FC))
