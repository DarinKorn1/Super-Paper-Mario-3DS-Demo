#!/usr/bin/env python
"""Convert Mario's sprite model (a/p_mario + a/p_mario-) into a static standing pose for the 3DS demo.

Usage:  python -I tools/convert_mario.py [--disc-dir PATH] [--out DIR]

Input : <disc>/a/p_mario  (AnimPoseData, uncompressed)  and  <disc>/a/p_mario-  (TPL, 126 CMPR images)
Output: <out>/mario.spm, <out>/textures/mario_NNN.t3x, <out>/mario_report.txt   (<out> = assets/, git-ignored)

Format knowledge (header offsets from spm-headers animdrv.h, draw loop from the TTYD decomp's renderProc, which
the SPM format shares; checked by the model assembling into a sensible Mario, see notes/demo-plan.md section 9.3):
  * shapes (0x14C, 168 B each) -> draws (0x19C, 108 B each) -> draw calls (0x150, {first,count} = one triangle FAN)
  * vertex k of a call: pos = positions[shape.vtxPos.first + (posIndex[call.first + draw.firstIdPos + k] & 0xFFFF)]
    (indices are u32 on disc, only the low 16 bits matter); the same for colour (4 B) and tex0 (2 floats)
  * texture of a draw: texData[texDataIds[0]].bindId = image number in the TPL
  * groups (0x1A8, 0x58 B): tree via child / brother links, each with a 24-float node (translation first),
    a shape (or -1) and a visibility byte
NOT decoded: the animation deltas (keyframes), so this is only the rest pose with the costume-variant parts hidden.

The output reuses the room file layout (notes/demo-plan.md 8.2): header "SPMR", batches, vertices, u16 indices.
Positions are model units x 64 (Mario is about 23 units tall), x/z centred, feet on y = 0. The sprite looks towards -x
(screen left); its front is at +z. Nothing else is stored (no animation).
Only the Python standard library plus devkitPro's tex3ds is used.
"""
import argparse
import importlib.util
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(DEMO_DIR)

spec = importlib.util.spec_from_file_location("convert_room", os.path.join(HERE, "convert_room.py"))
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

# parts of the sprite that belong to costume variants / other animations, hidden in the standing pose
HIDE_SUBTREES = {"Kinome", "Sp_boushi", "zentai", "big_hammer", "hammer", "awate_foot", "hed_kae", "mouth", "namida",
                 "nage_hammar", "big_hummer_line", "hummer_line"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disc-dir", default=os.path.join(REPO, "NewSuperPaperBros", "Disc", "DATA", "files"))
    ap.add_argument("--out", default=os.path.join(DEMO_DIR, "assets"))
    args = ap.parse_args()
    d = open(os.path.join(args.disc_dir, "a", "p_mario"), "rb").read()
    tpl = open(os.path.join(args.disc_dir, "a", "p_mario-"), "rb").read()

    u32 = lambda o: struct.unpack(">I", d[o:o + 4])[0]
    s32 = lambda o: struct.unpack(">i", d[o:o + 4])[0]
    cstr = lambda o: d[o:o + 64].split(b"\0")[0].decode("latin1")
    assert d[4:11] == b"p_mario", "not p_mario"

    n_shapes, n_groups = s32(0xE8), s32(0x144)
    shapes, calls, pos_arr, pos_idx = u32(0x14C), u32(0x150), u32(0x154), u32(0x158)
    clr_arr, clr_idx, tc_idx0, tc_arr = u32(0x164), u32(0x168), u32(0x16C), u32(0x18C)
    tex_data, draws, vis, nodes, groups = u32(0x194), u32(0x19C), u32(0x1A0), u32(0x1A4), u32(0x1A8)

    # ---- group tree -> parents, world matrices, visibility
    G = []
    for i in range(n_groups):
        o = groups + i * 0x58
        brother, child, shape, visi, node = (s32(o + 0x40 + 4 * k) for k in range(5))
        G.append(dict(name=cstr(o), brother=brother, child=child, shape=shape, vis=visi, node=node, parent=-1))
    for i, g in enumerate(G):
        c = g["child"]
        while c >= 0:
            G[c]["parent"] = i
            c = G[c]["brother"]

    def node_matrix(g):
        v = struct.unpack(">24f", d[nodes + g["node"] * 4:nodes + g["node"] * 4 + 96])
        # translation only: in the rest pose all rotations are 0 and all scales 1 (checked for every group below)
        return v

    world = {}

    def world_t(i):
        if i in world:
            return world[i]
        g = G[i]
        v = node_matrix(g)
        t = v[0:3]
        p = world_t(g["parent"]) if g["parent"] >= 0 else (0.0, 0.0, 0.0)
        world[i] = (p[0] + t[0], p[1] + t[1], p[2] + t[2])
        return world[i]

    def visible(i):
        while i >= 0:
            g = G[i]
            if g["vis"] >= 0 and d[vis + g["vis"]] == 0:
                return False
            if g["name"] in HIDE_SUBTREES:
                return False
            i = g["parent"]
        return True

    odd = 0
    for g in G:
        v = node_matrix(g)
        if any(abs(x) > 1e-4 for x in v[6:9] + v[9:12]) or any(abs(x - 1) > 1e-4 for x in v[3:6]):
            odd += 1

    # ---- textures
    tpl_n, tpl_tab = struct.unpack(">II", tpl[4:12])
    tex_cache = {}

    def tpl_image(idx):
        if idx not in tex_cache:
            tex_cache[idx] = cr.decode_tpl_image(tpl, struct.unpack(">II", tpl[tpl_tab + idx * 8:tpl_tab + idx * 8 + 8])[0])
        return tex_cache[idx]

    # ---- geometry: batches keyed by (tex image, cull, blend)
    batches = OrderedDict()
    shown = []
    for gi, g in enumerate(G):
        if g["shape"] < 0 or not visible(gi):
            continue
        shown.append(g["name"])
        so = shapes + g["shape"] * 168
        pos_first = s32(so + 0x40)
        clr_first = s32(so + 0x50)
        tc_first = s32(so + 0x58)
        cull_mode = s32(so + 0xA4)
        d_start, d_count = s32(so + 0x98), s32(so + 0x9C)
        wt = world_t(gi)
        for di in range(d_count):
            do = draws + (d_start + di) * 108
            tex_count = s32(do)
            tex_id = s32(tex_data + s32(do + 0x10) * 8) if tex_count > 0 else -1
            first_call, call_count = s32(do + 0x38), s32(do + 0x3C)
            id_pos, id_clr, id_tc = s32(do + 0x40), s32(do + 0x48), s32(do + 0x4C)
            w, h, fmt, px = tpl_image(tex_id) if tex_id >= 0 else (0, 0, 0, None)
            alpha = px is not None and any(p[3] < 250 for p in px)
            key = (tex_id, 3 if cull_mode == 3 else 1, alpha)
            tris = batches.setdefault(key, [])
            for ci in range(call_count):
                first, count = s32(calls + (first_call + ci) * 8), s32(calls + (first_call + ci) * 8 + 4)
                verts = []
                for k in range(count):
                    pi = u32(pos_idx + (first + id_pos + k) * 4) & 0xFFFF
                    x, y, z = struct.unpack(">3f", d[pos_arr + (pos_first + pi) * 12:pos_arr + (pos_first + pi) * 12 + 12])
                    ci_ = u32(clr_idx + (first + id_clr + k) * 4) & 0xFFFF
                    col = tuple(d[clr_arr + (clr_first + ci_) * 4:clr_arr + (clr_first + ci_) * 4 + 4])
                    ti = u32(tc_idx0 + (first + id_tc + k) * 4) & 0xFFFF
                    u, v = struct.unpack(">2f", d[tc_arr + (tc_first + ti) * 8:tc_arr + (tc_first + ti) * 8 + 8])
                    verts.append(((x + wt[0]), (y + wt[1]), (z + wt[2]), u, v, col))
                for k in range(1, count - 1):          # triangle fan; swapped to CCW like the room (see convert_room.py)
                    tris.append((verts[0], verts[k + 1], verts[k]))

    # ---- write
    out = args.out
    os.makedirs(os.path.join(out, "textures"), exist_ok=True)
    order = sorted(batches, key=lambda k: (k[2], k[0]))
    allv = [v for tl in batches.values() for t in tl for v in t]
    ox = (min(v[0] for v in allv) + max(v[0] for v in allv)) / 2      # centre x, feet on y = 0, centre z
    oy = min(v[1] for v in allv)
    oz = (min(v[2] for v in allv) + max(v[2] for v in allv)) / 2
    vlist, vmap, idx_all, btab = [], {}, [], []
    lo, hi = [1e9] * 3, [-1e9] * 3
    for key in order:
        first = len(idx_all)
        for tri in batches[key]:
            for v in tri:
                q = (int(round((v[0] - ox) * 64)), int(round((v[1] - oy) * 64)), int(round((v[2] - oz) * 64)),
                     int(round(v[3] * 128)), int(round((1.0 - v[4]) * 128)), v[5])
                vi = vmap.get(q)
                if vi is None:
                    vi = vmap[q] = len(vlist)
                    vlist.append(q)
                idx_all.append(vi)
                for a, off in enumerate((ox, oy, oz)):
                    lo[a] = min(lo[a], v[a] - off)
                    hi[a] = max(hi[a], v[a] - off)
        btab.append((key, first, len(idx_all) - first))
    with open(os.path.join(out, "mario.spm"), "wb") as f:
        f.write(struct.pack("<4sIIIII6f", b"SPMR", 1, tpl_n, len(vlist), len(btab), len(idx_all), *(lo + hi)))
        for (tex, cull, blend), first, count in btab:
            f.write(struct.pack("<iIIBBBBI", tex, first, count, cull, 0, 0, 1 if blend else 0, 0))
        for (x, y, z, u, v, c) in vlist:
            f.write(struct.pack("<4h2h4B", x, y, z, 0, u, v, *c))
        f.write(struct.pack("<%dH" % len(idx_all), *idx_all))

    tmp = tempfile.mkdtemp(prefix="spm3ds_mario_")
    t3 = cr.find_tex3ds()
    used = sorted({k[0] for k in batches if k[0] >= 0})
    for idx in used:
        w, h, fmt, px = tpl_image(idx)
        w2, h2, px2 = cr.resize_pow2(w, h, px)
        png = os.path.join(tmp, "mario_%03d.png" % idx)
        cr.write_png(png, w2, h2, px2)
        alpha = any(p[3] < 250 for p in px)
        r = subprocess.run([t3, "-f", "etc1a4" if alpha else "etc1", "-o",
                            os.path.join(out, "textures", "mario_%03d.t3x" % idx), png], capture_output=True, text=True)
        if r.returncode:
            sys.exit("tex3ds failed on image %d: %s" % (idx, r.stderr[:300]))
    shutil.rmtree(tmp, ignore_errors=True)

    rep = ["Mario (static rest pose, animations NOT decoded)",
           "groups %d, shapes %d, shown shape groups %d, triangles %d, vertices %d, batches %d, textures %d" % (
               n_groups, n_shapes, len(shown), len(idx_all) // 3, len(vlist), len(btab), len(used)),
           "groups with non-identity rotation/scale in the rest nodes: %d (ignored)" % odd,
           "bbox x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f" % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]),
           "shown: " + ", ".join(shown)]
    open(os.path.join(out, "mario_report.txt"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep[:4]))


if __name__ == "__main__":
    main()
