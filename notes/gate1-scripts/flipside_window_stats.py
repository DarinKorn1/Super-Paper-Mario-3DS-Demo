import json, statistics as st, sys
sp = sys.argv[1]
for name, f in [('LOW', 'run_low.json'), ('FULL', 'run_full.json')]:
    R = json.load(open(sp + '\\' + f))['rows']
    for label, a, b in [('idx 45-54 (profiled 90-110 s)', 45, 54), ('idx 76-85 (153-173 s)', 76, 85)]:
        if name == 'FULL' and a == 76: continue
        w = [r for r in R if a <= r['idx'] <= b]
        g = lambda k: st.mean(r[k] for r in w)
        print(name, label, 'maps', set(r['map'] for r in w), 'phases', set(r['phase'] for r in w))
        print('   fps %.1f game %.2f gx %.2f end_frame %.2f pace %.2f worst(median) %.1f over20(mean) %.1f draws %.0f cmds %.0f merged %.0f uniform %.0fKB storage %.0fKB vert %.0fKB' % (
            g('fps'), g('game'), g('gx'), g('end_frame'), g('pace'), st.median(r['worst'] for r in w), g('over20'), g('draws'), g('cmds'), g('merged'), g('uniform_kb'), g('storage_kb'), g('vert_kb')))
