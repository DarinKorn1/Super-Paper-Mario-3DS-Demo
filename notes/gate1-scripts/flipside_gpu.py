"""Average GPU engine utilisation inside the sampler window. Usage: python -I flipside_gpu.py <sampler dir>"""
import csv, collections, datetime as dt, re, sys
sdir = sys.argv[1]
def parse_utc(s):
    m = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(\.\d+)?', s.strip())
    return dt.datetime.strptime(m.group(1), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() + (float(m.group(2)) if m.group(2) else 0)
meta = dict(l.strip().split('=', 1) for l in open(sdir + '\\meta.txt') if '=' in l)
w0, w1 = parse_utc(meta['window_start_utc']), parse_utc(meta['window_end_utc'])
inside = collections.defaultdict(list); outside = collections.defaultdict(list)
for r in csv.DictReader(open(sdir + '\\gpu_util.csv')):
    t = parse_utc(r['utc']); k = (r['scope'], r['engtype'])
    (inside if w0 <= t < w1 else outside)[k].append(float(r['util_percent']))
print('GPU engine utilisation, percent (mean over the window; samples in window = %d)' % max((len(v) for v in inside.values()), default=0))
print(f'{"scope":8s} {"engine":18s} {"mean":>7s} {"max":>7s}   (outside the window: mean)')
for k in sorted(inside, key=lambda k: -sum(inside[k]) / len(inside[k])):
    v = inside[k]
    if sum(v) / len(v) < 0.05 and max(v) < 1: continue
    o = outside.get(k, [])
    print(f'{k[0]:8s} {k[1]:18s} {sum(v)/len(v):7.1f} {max(v):7.1f}   ({(sum(o)/len(o)) if o else float("nan"):.1f})')
