"""Static scan of the stock USA rev 0 disassembly (dtk output from the earlier spm-decomp build).

Usage: python -I ppc_features.py <asm root dir> <out json>
Counts, per guest function, the PowerPC features that are costly to imitate on a non-PPC host:
  paired single   : ps_* and psq_* mnemonics
  64-bit int maths: carry-chain ops (addc/adde/addze/addme/subfc/subfe/subfze/subfme), mulhw/mulhwu,
                    and calls to the CodeWarrior 64-bit helper routines (__shl2i, __div2u, ...)
  indirect control: bctr (jump tables / tail calls), conditional ctr branches, bctrl (indirect calls), blrl
"""
import json, os, re, sys
from collections import Counter, defaultdict

root, out = sys.argv[1], sys.argv[2]
LINE = re.compile(r'^/\*\s+([0-9A-Fa-f]{8})\s+[0-9A-Fa-f]{8}\s+(?:[0-9A-Fa-f]{2}\s+){4}\*/\s*(\S+)\s*(.*)$')
FN = re.compile(r'^\.fn\s+([^,\s]+)')
ENDFN = re.compile(r'^\.endfn\b')
CARRY = re.compile(r'^(addc|adde|addze|addme|subfc|subfe|subfze|subfme)o?\.?$')
MULH = re.compile(r'^mulhwu?\.?$')
PS = re.compile(r'^ps_')
PSQ = re.compile(r'^psq_')
# bctr / bctrl and the conditional forms (beqctr, bnectr, bltctr, ... ) but not bdnz/bdz (those use CTR as a counter)
CTR_JUMP = re.compile(r'^(b|b[a-z]{2,3})ctr$')
CTR_CALL = re.compile(r'^(b|b[a-z]{2,3})ctrl$')
LR_CALL = re.compile(r'^(b|b[a-z]{2,3})lrl$')
HELPERS64 = {'__shl2i', '__shr2u', '__shr2i', '__div2i', '__div2u', '__mod2i', '__mod2u',
             '__cvt_dbl_ull', '__cvt_ull_dbl', '__cvt_sll_dbl', '__cvt_dbl_usll', '__cvt_dbl_ll',
             '__cvt_fp2unsigned', '__mul2i', '__mul2u'}

funcs = {}
files = 0
for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith('.s'):
            continue
        files += 1
        path = os.path.join(dp, f)
        cur = None
        recent = []
        with open(path, encoding='utf-8', errors='replace') as fh:
            for line in fh:
                m = FN.match(line)
                if m:
                    cur = m.group(1)
                    funcs.setdefault(cur, {'file': os.path.relpath(path, root), 'addr': None, 'n': Counter(), 'mn': Counter()})
                    recent = []
                    continue
                if ENDFN.match(line):
                    cur = None
                    continue
                if cur is None:
                    continue
                m = LINE.match(line)
                if not m:
                    continue
                addr, mn, ops = m.group(1), m.group(2).lower(), m.group(3)
                d = funcs[cur]
                if d['addr'] is None:
                    d['addr'] = addr.upper()
                n = d['n']
                n['insns'] += 1
                if PS.match(mn): n['ps'] += 1
                elif PSQ.match(mn):
                    n['psq'] += 1
                    # MWCC saves/restores callee-saved FPRs in prologues/epilogues with psq_st/psq_l on the stack (r1)
                    if '(r1)' in ops: n['psq_stack'] += 1
                    else: n['psq_data'] += 1
                if CARRY.match(mn): n['carry'] += 1
                if MULH.match(mn): n['mulh'] += 1
                if CTR_JUMP.match(mn):
                    # jump table pattern: lwzx ... mtctr ... bctr
                    window = ' '.join(recent[-6:])
                    if 'lwzx' in window and 'mtctr' in window:
                        n['jumptable'] += 1
                    else:
                        n['ind_jump_other'] += 1
                elif CTR_CALL.match(mn) or LR_CALL.match(mn):
                    n['ind_call'] += 1
                elif mn in ('bl', 'bla'):
                    target = ops.split()[0] if ops.split() else ''
                    if target in HELPERS64:
                        n['call64'] += 1
                        d['mn'][target] += 1
                recent.append(mn)
                if len(recent) > 12:
                    recent.pop(0)

tot = Counter()
cats = ['ps', 'psq', 'psq_stack', 'psq_data', 'carry', 'mulh', 'call64', 'jumptable', 'ind_jump_other', 'ind_call']
users = {c: [] for c in cats}
for name, d in funcs.items():
    tot['functions'] += 1
    tot['insns'] += d['n']['insns']
    for c in cats:
        if d['n'][c]:
            users[c].append((name, d['addr'], d['n'][c], d['n']['insns']))
            tot[c + '_insns'] += d['n'][c]
            tot[c + '_funcs'] += 1
ps_any = {n for n, d in funcs.items() if d['n']['ps'] or d['n']['psq']}
ps_real = {n for n, d in funcs.items() if d['n']['ps'] or d['n']['psq_data']}
tot['paired_single_funcs_real'] = len(ps_real)
i64_any = {n for n, d in funcs.items() if d['n']['carry'] or d['n']['mulh'] or d['n']['call64']}
ind_any = {n for n, d in funcs.items() if d['n']['jumptable'] or d['n']['ind_jump_other'] or d['n']['ind_call']}
tot['paired_single_funcs_any'] = len(ps_any)
tot['int64_funcs_any'] = len(i64_any)
tot['indirect_funcs_any'] = len(ind_any)
tot['asm_files'] = files
summary = {
    'totals': dict(tot),
    'top': {c: sorted(users[c], key=lambda x: -x[2])[:15] for c in cats},
    'ps_funcs': sorted(((n, funcs[n]['addr'], funcs[n]['n']['ps'], funcs[n]['n']['psq_data'], funcs[n]['n']['psq_stack'], funcs[n]['n']['insns']) for n in ps_any), key=lambda x: -(x[2] + x[3])),
    'helpers64_called': Counter({k: sum(d['mn'][k] for d in funcs.values()) for k in HELPERS64 if any(d['mn'][k] for d in funcs.values())}),
    'i64_funcs': sorted(((n, funcs[n]['addr'], funcs[n]['n']['carry'], funcs[n]['n']['mulh'], funcs[n]['n']['call64']) for n in i64_any), key=lambda x: -(x[2] + x[3] + x[4])),
    'i64_small': sorted(((funcs[n]['n']['insns'], n, funcs[n]['addr'], funcs[n]['n']['carry'], funcs[n]['n']['mulh'], funcs[n]['n']['call64']) for n in i64_any if funcs[n]['n']['insns'] <= 40), key=lambda x: x[0])[:12],
    'ind_funcs': sorted(((n, funcs[n]['addr'], funcs[n]['n']['jumptable'], funcs[n]['n']['ind_jump_other'], funcs[n]['n']['ind_call']) for n in ind_any), key=lambda x: -(x[2] + x[3] + x[4])),
}
with open(out, 'w') as fh:
    json.dump(summary, fh, indent=1, default=dict)
print(json.dumps(summary['totals'], indent=1))
