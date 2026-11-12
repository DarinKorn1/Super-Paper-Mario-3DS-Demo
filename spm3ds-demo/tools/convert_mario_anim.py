#!/usr/bin/env python
"""Bake Mario's idle (mario_S_1) and walk (mario_W_1) animations for the 3DS demo.

Usage:  python -I tools/convert_mario_anim.py [--disc-dir PATH] [--out DIR]
Output: <out>/mario_anim.bin (format "SPMA": header {magic, version, nAnims, nPool, sampleStep f32, nAlpha}, nAlpha image numbers,
        pool {s16 u, s16 v, u8 rgba}, then per animation {name[16], nFrames, loop} and per frame {nBatches, nIdx, batches {s32 tex, u32 first, u32 count, 2 pad},
        u16 indices (padded to 4 bytes), pool positions s16 x,y,z,0 in units/64}), <out>/textures/mario_NNN.t3x for every image the animations use.

The animation format was read from the game's own code (US0 disassembly of animPoseMain = fn_80045170,
evalProc = fn_8004CFB0, the two node-matrix builders fn_800465AC / fn_80046B14 and the table set-up in fn_800415B0).
Everything below is what those functions do; see notes/demo-plan.md section 11.

AnimData (at the offset stored in the anim table; its pointers are relative to its start):
  +0x08 keyframe count, +0x24 loop data {mode u32, loopStart f32, loopEnd f32}, +0x28 keyframes (0x2C bytes each),
  +0x2C vertex-position deltas, +0x34 texture-animation deltas, +0x38 visibility deltas, +0x3C group-transform deltas.
Keyframe (0x2C): f32 time (in 60 Hz frames), then {offset,length} pairs for pos (u32 units), normals, texture (12-byte
  units), visibility (u16 units), group transform (u32 units).
State at keyframe k = base data + the sum of the deltas of keyframes 0..k:
  pos record 4 B  : u8 skip (cumulative vertex index), s8 dx, dy, dz      -> pos[idx] += d / 16
  vis record 2 B  : u8 skip (cumulative), u8 add                          -> vis[idx] += add (mod 256)
  group record 4 B: u8 skip (cumulative float index), s8 v, s8 a, s8 b    -> node[idx] += v / 16
  tex record 12 B : u8 skip (cumulative 0x18-byte entries), u8 add to the entry's frame number, f32 +4, f32 +8
Between keyframes k and k+1 (fraction t): positions get + t * (delta of k+1) / 16 (linear); group values get a cubic
Hermite step: + h10(t)*dt*tan(a deg) + h01(t)*v/16 + h11(t)*dt*tan(b deg) (skipped when |b| >= 89).
Nodes (24 floats: T, S, rot1, rot2, rotCenter, scaleCenter, rotTranslate, scaleTranslate) become matrices as in
fn_800465AC (plain transform: T * R * S with pivots) or fn_80046B14 (joint with segment scale compensation:
T * Sinv * R * S); rotation angles are value * 2 degrees.
"""
import argparse
import importlib.util
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(DEMO_DIR)
spec = importlib.util.spec_from_file_location("convert_room", os.path.join(HERE, "convert_room.py"))
cr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cr)

# costume-variant parts the game's own code hides (the animation data does not); same list as convert_mario.py
HIDE = {"Kinome", "Sp_boushi", "zentai", "big_hammer", "hammer", "awate_foot", "hed_kae", "mouth", "namida",
        "nage_hammar", "big_hummer_line", "hummer_line"}
ANIMS = ["mario_S_1", "mario_W_1"]      # 0 = idle, 1 = walk
SAMPLE_STEP = 2.0                        # frames (60 Hz) between baked samples -> 30 Hz
IDENT = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
mm = cr.matmul


def trans(x, y, z):
    return [[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]]


def scale(x, y, z):
    return [[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]]


def rot(axis, rad):
    c, s = math.cos(rad), math.sin(rad)
    if axis == "x":
        return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]
    if axis == "y":
        return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def rotzyx(rx, ry, rz):
    return mm(rot("z", rz), mm(rot("y", ry), rot("x", rx)))


D2R = 0.017453292


def transform_node(n):
    """fn_800465AC"""
    t = trans(*n[0:3]) if any(n[0:3]) else None
    sc = n[3:6]
    scl_c, scl_t = n[15:18], n[21:24]
    rot_c, rot_t = n[12:15], n[18:21]
    # scale part
    S = None
    if tuple(sc) != (1, 1, 1):
        S = scale(*sc)
    if any(scl_c):
        if S is not None:
            S = mm(mm(mm(trans(*scl_t), trans(*scl_c)), S), trans(-scl_c[0], -scl_c[1], -scl_c[2]))
        elif any(scl_t):
            S = trans(*scl_t)
    # rotation part (angle = value * 2 degrees)
    R = None
    if any(n[6:9]):
        R = rotzyx(2 * n[6] * D2R, 2 * n[7] * D2R, 2 * n[8] * D2R)
    if any(rot_c):
        if R is not None:
            R = mm(mm(mm(trans(*rot_t), trans(*rot_c)), R), trans(-rot_c[0], -rot_c[1], -rot_c[2]))
        elif any(rot_t):
            R = trans(*rot_t)
    m = t or IDENT
    if R is not None:
        m = mm(m, R)
    if S is not None:
        m = mm(m, S)
    return m


def joint_node(n, ps):
    """fn_80046B14: T * Sinv(parent scale) * (orient * rot) * S"""
    t = trans(*n[0:3]) if any(n[0:3]) else None
    sinv = None
    if tuple(ps) != (1, 1, 1):
        sinv = scale(*[1.0 / p if p else 1.0 for p in ps]) if all(ps) else scale(1, 1, 1)
    s = scale(*n[3:6]) if tuple(n[3:6]) != (1, 1, 1) else None
    R = None
    if any(n[9:12]):                                  # rot2 (joint orient), applied first
        R = rotzyx(2 * n[9] * D2R, 2 * n[10] * D2R, 2 * n[11] * D2R)
    if any(n[6:9]):
        r1 = rotzyx(2 * n[6] * D2R, 2 * n[7] * D2R, 2 * n[8] * D2R)
        R = r1 if R is None else mm(R, r1)
    m = t or IDENT
    for part in (sinv, R, s):
        if part is not None:
            m = mm(m, part)
    return m


def s8(b):
    return b - 256 if b > 127 else b


class Model:
    def __init__(self, d):
        self.d = d
        u = self.u32
        self.n_groups = struct.unpack(">i", d[0x144:0x148])[0]
        self.shapes, self.calls, self.pos_arr, self.pos_idx = u(0x14C), u(0x150), u(0x154), u(0x158)
        self.clr_arr, self.clr_idx, self.tc_idx0, self.tc_arr = u(0x164), u(0x168), u(0x16C), u(0x18C)
        self.tex_xf, self.tex_data, self.draws = u(0x190), u(0x194), u(0x19C)
        self.vis, self.nodes, self.groups = u(0x1A0), u(0x1A4), u(0x1A8)
        self.n_pos = u(0xF0)
        self.n_tex = u(0x12C)
        self.n_nodes = u(0x140)
        self.n_vis = u(0x13C)
        self.G = []
        for i in range(self.n_groups):
            o = self.groups + i * 0x58
            br, ch, sh, vi, nd, ssc = struct.unpack(">6i", d[o + 0x40:o + 0x58])
            self.G.append(dict(name=d[o:o + 64].split(b"\0")[0].decode("latin1"), brother=br, child=ch, shape=sh,
                               vis=vi, node=nd, ssc=ssc, parent=-1))
        for i, g in enumerate(self.G):
            c = g["child"]
            while c >= 0:
                self.G[c]["parent"] = i
                c = self.G[c]["brother"]
        self.base_pos = list(struct.unpack(">%df" % (self.n_pos * 3), d[self.pos_arr:self.pos_arr + self.n_pos * 12]))
        self.base_vis = list(d[self.vis:self.vis + self.n_vis])
        self.base_nodes = list(struct.unpack(">%df" % self.n_nodes, d[self.nodes:self.nodes + 4 * self.n_nodes]))
        self.base_tex = [list(struct.unpack(">B3xfffff", d[self.tex_xf + i * 24:self.tex_xf + i * 24 + 24]))
                         for i in range(self.n_tex)]
        self.anims = {}
        A = u(0x1AC)
        for i in range(struct.unpack(">i", d[0x148:0x14C])[0]):
            o = A + i * 64
            self.anims[d[o:o + 60].split(b"\0")[0].decode()] = u(o + 60)

    def u32(self, o):
        return struct.unpack(">I", self.d[o:o + 4])[0]

    def f32(self, o):
        return struct.unpack(">f", self.d[o:o + 4])[0]


class Anim:
    def __init__(self, m, p):
        d, u = m.d, m.u32
        self.m = m
        self.p = p
        self.n_keys = u(p + 8)
        lp = p + u(p + 0x24)
        self.loop, self.loop_start, self.loop_end = u(lp), m.f32(lp + 4), m.f32(lp + 8)
        self.kbase = p + u(p + 0x28)
        self.pos_s, self.tex_s, self.vis_s, self.grp_s = p + u(p + 0x2C), p + u(p + 0x34), p + u(p + 0x38), p + u(p + 0x3C)
        self.keys = []
        for k in range(self.n_keys):
            o = self.kbase + k * 0x2C
            self.keys.append((m.f32(o), [u(o + 4 + 4 * j) for j in range(10)]))
        # cumulative states
        self.states = []
        pos, vis, nodes = list(m.base_pos), list(m.base_vis), list(m.base_nodes)
        tex = [list(t) for t in m.base_tex]
        for k in range(self.n_keys):
            _, w = self.keys[k]
            o = self.pos_s + w[0] * 4
            idx = 0
            for r in range(w[1]):
                b = d[o + r * 4:o + r * 4 + 4]
                idx += b[0]
                for a in range(3):
                    pos[idx * 3 + a] += s8(b[1 + a]) * 0.0625
            o = self.vis_s + w[6] * 2
            idx = 0
            # visibility: length is counted in u16 units, 2 bytes per record -> one record per unit
            for r in range(w[7]):
                b = d[o + r * 2:o + r * 2 + 2]
                idx += b[0]
                vis[idx] = (vis[idx] + b[1]) & 0xFF
            o = self.grp_s + w[8] * 4
            idx = 0
            for r in range(w[9]):
                b = d[o + r * 4:o + r * 4 + 4]
                idx += b[0]
                nodes[idx] += s8(b[1]) * 0.0625
            o = self.tex_s + w[4] * 12
            idx = 0
            for r in range(w[5]):
                b = d[o + r * 12:o + r * 12 + 12]
                idx += b[0]
                tex[idx][0] = (tex[idx][0] + b[1]) & 0xFF
                tex[idx][1] += struct.unpack(">f", b[4:8])[0]
                tex[idx][2] += struct.unpack(">f", b[8:12])[0]
            self.states.append((list(pos), list(vis), list(nodes), [list(t) for t in tex]))

    def evaluate(self, t):
        """Returns (pos, vis, nodes, tex) at time t (60 Hz frames)."""
        m, d = self.m, self.m.d
        if self.loop:
            span = self.loop_end - self.loop_start
            if span > 0:
                t = self.loop_start + ((t - self.loop_start) % span)
        cur = 0
        for i, (kt, _) in enumerate(self.keys):
            if kt <= t:
                cur = i
        nxt = cur + 1
        if nxt >= self.n_keys:
            nxt = 0 if self.loop else cur
        if self.loop and nxt == 0 and cur == self.n_keys - 1:
            den = self.loop_end - self.keys[cur][0]
        else:
            den = self.keys[nxt][0] - self.keys[cur][0]
        frac = 0.0 if den == 0 else (t - self.keys[cur][0]) / den
        pos, vis, nodes, tex = (list(x) if not isinstance(x[0], list) else [list(y) for y in x] for x in self.states[cur])
        if nxt != cur:
            w = self.keys[nxt][1]
            o = self.pos_s + w[0] * 4
            idx = 0
            for r in range(w[1]):
                b = d[o + r * 4:o + r * 4 + 4]
                idx += b[0]
                for a in range(3):
                    pos[idx * 3 + a] += frac * 0.0625 * s8(b[1 + a])
            dt = self.keys[nxt][0] - self.keys[cur][0]
            o = self.grp_s + w[8] * 4
            idx = 0
            t1, t2, t3 = frac, frac * frac, frac ** 3
            h10, h01, h11 = t3 - 2 * t2 + t1, -2 * t3 + 3 * t2, t3 - t2
            for r in range(w[9]):
                b = d[o + r * 4:o + r * 4 + 4]
                idx += b[0]
                v, a, bb = s8(b[1]), s8(b[2]), s8(b[3])
                if bb >= 89 or bb <= -89:
                    continue
                nodes[idx] += (h10 * dt * math.tan(a * D2R) + h01 * v * 0.0625 + h11 * dt * math.tan(bb * D2R))
        return pos, vis, nodes, tex


def world_matrices(m, vis, nodes):
    """evalProc: returns {group: world matrix} for visible groups (a hidden group hides its subtree)."""
    out = {}

    def visit(gi, parent_world, parent_i):
        while gi >= 0:
            g = m.G[gi]
            if g["name"] in HIDE or (g["vis"] >= 0 and (vis[g["vis"]] & 0xFF) == 0):
                gi = g["brother"]
                continue
            n = nodes[g["node"]:g["node"] + 24]
            if g["ssc"]:
                ps = (1, 1, 1)
                if parent_i >= 0 and m.G[parent_i]["ssc"]:
                    pn = nodes[m.G[parent_i]["node"]:m.G[parent_i]["node"] + 24]
                    ps = tuple(pn[3:6])
                local = joint_node(n, ps)
            else:
                local = transform_node(n)
            w = mm(parent_world, local)
            out[gi] = w
            if g["child"] >= 0:
                visit(g["child"], w, gi)
            gi = g["brother"]

    # roots: groups without a parent, visited in brother order starting from the last group
    visit(m.n_groups - 1, IDENT, -1)
    return out


def shape_triangles(m, g, pos, tex_state, group_world):
    """Yield (tex image, cull, [(pool key, x, y, z, u, v, colour)] triangles) for the shape of group g."""
    d, u32 = m.d, m.u32
    so = m.shapes + g["shape"] * 168
    pos_first, clr_first, tc_first = struct.unpack(">i", d[so + 0x40:so + 0x44])[0], \
        struct.unpack(">i", d[so + 0x50:so + 0x54])[0], struct.unpack(">i", d[so + 0x58:so + 0x5C])[0]
    cull = struct.unpack(">i", d[so + 0xA4:so + 0xA8])[0]
    d_start, d_count = struct.unpack(">ii", d[so + 0x98:so + 0xA0])
    res = []
    for di in range(d_count):
        do = m.draws + (d_start + di) * 108
        tex_count = struct.unpack(">i", d[do:do + 4])[0]
        img = -1
        if tex_count > 0:
            data_id = struct.unpack(">i", d[do + 0x10:do + 0x14])[0]
            bind = struct.unpack(">i", d[m.tex_data + data_id * 8:m.tex_data + data_id * 8 + 4])[0]
            img = bind + tex_state[data_id][0]
        first_call, call_count = struct.unpack(">ii", d[do + 0x38:do + 0x40])
        id_pos, id_clr, id_tc = (struct.unpack(">i", d[do + o:do + o + 4])[0] for o in (0x40, 0x48, 0x4C))
        for ci in range(call_count):
            first, count = struct.unpack(">ii", d[m.calls + (first_call + ci) * 8:m.calls + (first_call + ci) * 8 + 8])
            verts = []
            for k in range(count):
                pi = pos_first + (u32(m.pos_idx + (first + id_pos + k) * 4) & 0xFFFF)
                ci_ = clr_first + (u32(m.clr_idx + (first + id_clr + k) * 4) & 0xFFFF)
                ti = tc_first + (u32(m.tc_idx0 + (first + id_tc + k) * 4) & 0xFFFF)
                col = tuple(d[m.clr_arr + ci_ * 4:m.clr_arr + ci_ * 4 + 4])
                uu, vv = struct.unpack(">2f", d[m.tc_arr + ti * 8:m.tc_arr + ti * 8 + 8])
                verts.append((pi, uu, vv, col))
            for k in range(1, count - 1):
                res.append((img, 3 if cull == 3 else 1, (verts[0], verts[k + 1], verts[k])))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disc-dir", default=os.path.join(REPO, "NewSuperPaperBros", "Disc", "DATA", "files"))
    ap.add_argument("--out", default=os.path.join(DEMO_DIR, "assets"))
    args = ap.parse_args()
    d = open(os.path.join(args.disc_dir, "a", "p_mario"), "rb").read()
    tpl = open(os.path.join(args.disc_dir, "a", "p_mario-"), "rb").read()
    m = Model(d)
    anims = [Anim(m, m.anims[n]) for n in ANIMS]

    # ---- sample every animation
    frames_by_anim = []
    pool = {}                    # (group, pos index, u, v, colour) -> pool index
    pool_list = []
    uv_anim = 0
    img_used = set()
    for a in anims:
        n_frames = int(round((a.loop_end if a.loop else a.keys[-1][0]) / SAMPLE_STEP)) or 1
        frames = []
        for fi in range(n_frames):
            pos, vis, nodes, tex = a.evaluate(fi * SAMPLE_STEP)
            if any(abs(t[1]) > 1e-6 or abs(t[2]) > 1e-6 for t in tex):
                uv_anim += 1
            W = world_matrices(m, vis, nodes)
            tris = []
            for gi, w in W.items():
                g = m.G[gi]
                if g["shape"] < 0:
                    continue
                for img, cull, tri in shape_triangles(m, g, pos, tex, w):
                    ids = []
                    for (pi, uu, vv, col) in tri:
                        key = (gi, pi, round(uu, 4), round(vv, 4), col)
                        pid = pool.get(key)
                        if pid is None:
                            pid = pool[key] = len(pool_list)
                            pool_list.append(key)
                        ids.append(pid)
                    tris.append((img, ids))
                    if img >= 0:
                        img_used.add(img)
            frames.append((pos, W, tris))
        frames_by_anim.append(frames)

    # ---- model space -> 3DS space: feet at y = 0, x/z centred on the idle frame 0 bounding box
    def world_pos(pos, W, key):
        gi, pi = key[0], key[1]
        w = W.get(gi)
        if w is None:
            return (0.0, 0.0, 0.0)
        x, y, z = pos[pi * 3:pi * 3 + 3]
        return tuple(w[r][0] * x + w[r][1] * y + w[r][2] * z + w[r][3] for r in range(3))

    f0 = frames_by_anim[0][0]
    used0 = sorted({i for _, ids in f0[2] for i in ids})
    pts = [world_pos(f0[0], f0[1], pool_list[i]) for i in used0]
    ox = (min(p[0] for p in pts) + max(p[0] for p in pts)) / 2
    oy = min(p[1] for p in pts)
    oz = (min(p[2] for p in pts) + max(p[2] for p in pts)) / 2

    def q(v):
        return max(-32768, min(32767, int(round(v * 64))))

    out = args.out
    os.makedirs(os.path.join(out, "textures"), exist_ok=True)
    # ---- textures: blend flag per image is decided at load time from a small table, written here
    tmp = tempfile.mkdtemp(prefix="spm3ds_mario_anim_")
    t3 = cr.find_tex3ds()
    tpl_n, tpl_tab = struct.unpack(">II", tpl[4:12])
    alpha_imgs = []
    for img in sorted(img_used):
        w, h, fmt, px = cr.decode_tpl_image(tpl, struct.unpack(">II", tpl[tpl_tab + img * 8:tpl_tab + img * 8 + 8])[0])
        w2, h2, px2 = cr.resize_pow2(w, h, px)
        png = os.path.join(tmp, "mario_%03d.png" % img)
        cr.write_png(png, w2, h2, px2)
        alpha = any(p[3] < 250 for p in px)
        if alpha:
            alpha_imgs.append(img)
        r = subprocess.run([t3, "-f", "etc1a4" if alpha else "etc1", "-o",
                            os.path.join(out, "textures", "mario_%03d.t3x" % img), png], capture_output=True, text=True)
        if r.returncode:
            sys.exit("tex3ds failed on image %d: %s" % (img, r.stderr[:300]))
    shutil.rmtree(tmp, ignore_errors=True)

    with open(os.path.join(out, "mario_anim.bin"), "wb") as f:
        f.write(struct.pack("<4sIIIfI", b"SPMA", 1, len(anims), len(pool_list), SAMPLE_STEP, len(alpha_imgs)))
        f.write(struct.pack("<%dI" % len(alpha_imgs), *alpha_imgs))
        for (gi, pi, uu, vv, col) in pool_list:
            f.write(struct.pack("<2h4B", int(round(uu * 128)), int(round((1.0 - vv) * 128)), *col))
        for name, a, frames in zip(ANIMS, anims, frames_by_anim):
            f.write(struct.pack("<16sII", name.encode(), len(frames), 1 if a.loop else 0))
            for pos, W, tris in frames:
                alpha = {}
                batches = {}
                for img, ids in tris:
                    batches.setdefault(img, []).extend(ids)
                order = sorted(batches, key=lambda i: i)
                idx_all, btab = [], []
                for img in order:
                    first = len(idx_all)
                    idx_all += batches[img]
                    btab.append((img, first, len(idx_all) - first))
                f.write(struct.pack("<II", len(btab), len(idx_all)))
                for img, first, cnt in btab:
                    f.write(struct.pack("<iIIII", img, first, cnt, 0, 0))   # blend flag filled in below by tex alpha
                f.write(struct.pack("<%dH" % len(idx_all), *idx_all))
                if len(idx_all) % 2:
                    f.write(b"\0\0")
                for key in pool_list:
                    x, y, z = world_pos(pos, W, key)
                    f.write(struct.pack("<4h", q(x - ox), q(y - oy), q(z - oz), 0))

    rep = ["Mario animations: %s" % ", ".join("%s (%d keys, loop %s %.0f..%.0f, %d samples)" % (
        n, a.n_keys, bool(a.loop), a.loop_start, a.loop_end, len(fr)) for n, a, fr in zip(ANIMS, anims, frames_by_anim)),
        "pool vertices %d, images %d (%d with alpha), samples with UV animation: %d (ignored)" % (
            len(pool_list), len(img_used), len(alpha_imgs), uv_anim),
        "offset (model units) x %.3f y %.3f z %.3f" % (ox, oy, oz)]
    open(os.path.join(out, "mario_anim_report.txt"), "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
