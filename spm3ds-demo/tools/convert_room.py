#!/usr/bin/env python
"""Convert a Super Paper Mario map (map/<name>.bin) into files the 3DS demo can load.

Usage:  python -I tools/convert_room.py [--disc-file PATH] [--out DIR] [--name mac_02]

Input : the extracted disc file  files/map/mac_02.bin  (LZ10-compressed U8 archive)
Output: <out>/room_main.spm, <out>/room_oku.spm, <out>/textures/tex_NNN.t3x, <out>/report.txt
        (default <out> = spm3ds-demo/assets/, which is git-ignored: never commit it)

What it does (input format: notes/demo-plan.md section 2; output format: notes/demo-plan.md section 8):
  1. LZ10-decompress and unpack the U8 archive in memory.
  2. Parse map.dat: joint tree -> world matrices; the "S" subtree is the visible scenery.
  3. Bake every mesh into world space, turn triangle strips into triangle lists, merge everything that
     shares (texture, wrap, cull, blend) into ONE batch = one draw call. Vertex colour is multiplied by the
     material colour at conversion time, so materials that differ only in colour share a batch.
  4. Split the output in two parts: "oku" (the biggest hall, 57 % of the triangles) and "main" (the rest),
     so the 3DS can switch "oku" off.
  5. Decode the TPL textures (CMPR/IA4/IA8/RGB565/RGB5A3), resize non-power-of-two ones, and run the
     devkitPro `tex3ds` tool (ETC1, or ETC1A4 if the texture has alpha).

Only the Python standard library is used. Run with `python -I` (isolated mode).
"""
import argparse
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO_DIR = os.path.dirname(HERE)
REPO = os.path.dirname(DEMO_DIR)

POS_FRAC = 64.0        # vertex positions are stored as s16 = world * 64 (range +-512 world units)
UV_ONE = 128           # GX texcoords are s16 with 7 fractional bits (guess, see report)


# ----------------------------------------------------------------------------------------------
# containers
# ----------------------------------------------------------------------------------------------
def lz10(data):
    assert data[0] == 0x10, "not Nintendo LZ10"
    size = data[1] | (data[2] << 8) | (data[3] << 16)
    out = bytearray()
    i = 4
    while len(out) < size:
        flags = data[i]
        i += 1
        for b in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> b):
                x = (data[i] << 8) | data[i + 1]
                i += 2
                n = (x >> 12) + 3
                d = (x & 0xFFF) + 1
                for _ in range(n):
                    out.append(out[-d])
            else:
                out.append(data[i])
                i += 1
    return bytes(out[:size])


def parse_u8(d):
    magic, root_off, _hdr, _data = struct.unpack(">4sIII", d[:16])
    assert magic == b"\x55\xaa\x38\x2d", "not a U8 archive"
    count = struct.unpack(">I", d[root_off + 8:root_off + 12])[0]
    strtab = root_off + count * 12
    nodes = []
    for i in range(count):
        w, a, b = struct.unpack(">III", d[root_off + i * 12:root_off + i * 12 + 12])
        noff = w & 0xFFFFFF
        e = d.index(b"\0", strtab + noff)
        nodes.append((w >> 24, d[strtab + noff:e].decode("latin1"), a, b))
    files = {}
    stack = []
    for i, (typ, name, a, b) in enumerate(nodes):
        while stack and i >= stack[-1][0]:
            stack.pop()
        if i == 0:
            stack.append((b, ""))
            continue
        base = stack[-1][1] if stack else ""
        path = base + "/" + name if base else name
        if typ == 1:
            stack.append((b, path))
        else:
            files[path] = d[a:a + b]
    return files


# ----------------------------------------------------------------------------------------------
# map.dat
# ----------------------------------------------------------------------------------------------
class MapDat:
    def __init__(self, m):
        self.m = m
        size, dsize, relcount, chunkcount = struct.unpack(">4I", m[:16])
        assert size == len(m), "map.dat size mismatch"
        self.D = m[0x20:0x20 + dsize]
        chk = 0x20 + dsize + relcount * 4
        strs = chk + chunkcount * 8
        self.chunks = {}
        for i in range(chunkcount):
            off, noff = struct.unpack(">II", m[chk + i * 8:chk + i * 8 + 8])
            e = m.index(b"\0", strs + noff)
            self.chunks[m[strs + noff:e].decode()] = off

    def u32(self, o):
        return struct.unpack(">I", self.D[o:o + 4])[0]

    def s32(self, o):
        return struct.unpack(">i", self.D[o:o + 4])[0]

    def u16(self, o):
        return struct.unpack(">H", self.D[o:o + 2])[0]

    def f32(self, o):
        return struct.unpack(">f", self.D[o:o + 4])[0]

    def vec(self, o):
        return struct.unpack(">3f", self.D[o:o + 12])

    def cstr(self, o):
        e = self.D.index(b"\0", o)
        return self.D[o:e].decode("latin1")

    def kids(self, j):
        c = self.u32(j + 0xC)
        out = []
        while c:
            out.append(c)
            c = self.u32(c + 0x10)
        return out


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def local_matrix(mp, j):
    sx, sy, sz = mp.vec(j + 0x18)
    rx, ry, rz = [math.radians(x) for x in mp.vec(j + 0x24)]
    tx, ty, tz = mp.vec(j + 0x30)
    cx, sx_ = math.cos(rx), math.sin(rx)
    cy, sy_ = math.cos(ry), math.sin(ry)
    cz, sz_ = math.cos(rz), math.sin(rz)
    Rx = [[1, 0, 0, 0], [0, cx, -sx_, 0], [0, sx_, cx, 0], [0, 0, 0, 1]]
    Ry = [[cy, 0, sy_, 0], [0, 1, 0, 0], [-sy_, 0, cy, 0], [0, 0, 0, 1]]
    Rz = [[cz, -sz_, 0, 0], [sz_, cz, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    S = [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, sz, 0], [0, 0, 0, 1]]
    T = [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]]
    return matmul(T, matmul(Rz, matmul(Ry, matmul(Rx, S))))


def walk_with_matrices(mp, j, parent, section, depth=0):
    """Yield (joint, world matrix, section name). `section` = name of the child of S that contains it."""
    m = matmul(parent, local_matrix(mp, j))
    yield j, m, section
    for c in mp.kids(j):
        sec = section
        if depth == 0:                       # j is the S root: its children name the sections
            sec = mp.cstr(mp.u32(c))
        yield from walk_with_matrices(mp, c, m, sec, depth + 1)


IDENT = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]


def mesh_lists(mp, mesh):
    """Return (elementMask, [display list offsets])."""
    packed = mp.D[mesh + 3]
    n = mp.s32(mesh + 4)
    mask = mp.u32(mesh + 8)
    lists = []
    for i in range(n):
        lists.append(mp.u32(mesh + 0x10 + i * (8 if packed else 4)))
    return mask, lists


# ----------------------------------------------------------------------------------------------
# textures
# ----------------------------------------------------------------------------------------------
def rgb565(v):
    return (((v >> 11) & 31) * 255 // 31, ((v >> 5) & 63) * 255 // 63, (v & 31) * 255 // 31)


def decode_tpl_image(t, ih):
    h, w, fmt, doff, wrap_s, wrap_t = struct.unpack(">HHIIII", t[ih:ih + 20])
    px = [(0, 0, 0, 255)] * (w * h)

    def put(bx, by, x, y, c):
        X, Y = bx + x, by + y
        if X < w and Y < h:
            px[Y * w + X] = c

    pos = doff
    if fmt == 14:  # CMPR: 8x8 tiles of four 4x4 DXT1 blocks
        for ty in range(0, h, 8):
            for tx in range(0, w, 8):
                for sub in range(4):
                    bx, by = tx + (sub & 1) * 4, ty + (sub >> 1) * 4
                    c0, c1 = struct.unpack(">HH", t[pos:pos + 4])
                    bits = struct.unpack(">I", t[pos + 4:pos + 8])[0]
                    pos += 8
                    r0, g0, b0 = rgb565(c0)
                    r1, g1, b1 = rgb565(c1)
                    pal = [(r0, g0, b0, 255), (r1, g1, b1, 255)]
                    if c0 > c1:
                        pal.append(((2 * r0 + r1) // 3, (2 * g0 + g1) // 3, (2 * b0 + b1) // 3, 255))
                        pal.append(((r0 + 2 * r1) // 3, (g0 + 2 * g1) // 3, (b0 + 2 * b1) // 3, 255))
                    else:
                        pal.append(((r0 + r1) // 2, (g0 + g1) // 2, (b0 + b1) // 2, 255))
                        pal.append((0, 0, 0, 0))
                    for y in range(4):
                        for x in range(4):
                            idx = (bits >> (30 - 2 * (y * 4 + x))) & 3
                            put(bx, by, x, y, pal[idx])
    elif fmt == 2:  # IA4: 8x4 tiles
        for by in range(0, h, 4):
            for bx in range(0, w, 8):
                for y in range(4):
                    for x in range(8):
                        v = t[pos]
                        pos += 1
                        a, i = (v >> 4) * 17, (v & 15) * 17
                        put(bx, by, x, y, (i, i, i, a))
    elif fmt == 3:  # IA8: 4x4 tiles
        for by in range(0, h, 4):
            for bx in range(0, w, 4):
                for y in range(4):
                    for x in range(4):
                        a, i = t[pos], t[pos + 1]
                        pos += 2
                        put(bx, by, x, y, (i, i, i, a))
    elif fmt in (4, 5):  # RGB565 / RGB5A3: 4x4 tiles
        for by in range(0, h, 4):
            for bx in range(0, w, 4):
                for y in range(4):
                    for x in range(4):
                        v = (t[pos] << 8) | t[pos + 1]
                        pos += 2
                        if fmt == 4:
                            r, g, b = rgb565(v)
                            c = (r, g, b, 255)
                        elif v & 0x8000:
                            c = (((v >> 10) & 31) * 255 // 31, ((v >> 5) & 31) * 255 // 31, (v & 31) * 255 // 31, 255)
                        else:
                            c = (((v >> 8) & 15) * 17, ((v >> 4) & 15) * 17, (v & 15) * 17, ((v >> 12) & 7) * 255 // 7)
                        put(bx, by, x, y, c)
    else:
        raise ValueError("unsupported TPL format %d" % fmt)
    return w, h, fmt, px


def next_pow2(n):
    p = 8
    while p < n:
        p *= 2
    return p


def resize_pow2(w, h, px):
    """Resize to power-of-two (min 8) with bilinear filtering; returns (w2, h2, px2)."""
    w2, h2 = next_pow2(w), next_pow2(h)
    if (w2, h2) == (w, h):
        return w, h, px
    out = []
    for y in range(h2):
        fy = (y + 0.5) * h / h2 - 0.5
        y0 = max(0, min(h - 1, int(math.floor(fy))))
        y1 = min(h - 1, y0 + 1)
        ty = min(1.0, max(0.0, fy - y0))
        for x in range(w2):
            fx = (x + 0.5) * w / w2 - 0.5
            x0 = max(0, min(w - 1, int(math.floor(fx))))
            x1 = min(w - 1, x0 + 1)
            tx = min(1.0, max(0.0, fx - x0))
            p00, p10, p01, p11 = px[y0 * w + x0], px[y0 * w + x1], px[y1 * w + x0], px[y1 * w + x1]
            out.append(tuple(int(round((p00[k] * (1 - tx) + p10[k] * tx) * (1 - ty) +
                                       (p01[k] * (1 - tx) + p11[k] * tx) * ty)) for k in range(4)))
    return w2, h2, out


def write_png(path, w, h, px):
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            raw += bytes(px[y * w + x])

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
                chunk(b"IDAT", zlib.compress(bytes(raw), 6)) + chunk(b"IEND", b""))


def find_tex3ds():
    for cand in (shutil.which("tex3ds"),
                 os.path.join(os.environ.get("DEVKITPRO", ""), "tools", "bin", "tex3ds.exe"),
                 r"C:\devkitPro\tools\bin\tex3ds.exe", "/opt/devkitpro/tools/bin/tex3ds"):
        if cand and os.path.exists(cand):
            return cand
    sys.exit("tex3ds not found (it is part of devkitPro)")


# ----------------------------------------------------------------------------------------------
# main conversion
# ----------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="mac_02")
    ap.add_argument("--disc-file", default=None)
    ap.add_argument("--out", default=os.path.join(DEMO_DIR, "assets"))
    args = ap.parse_args()
    disc = args.disc_file or os.path.join(REPO, "NewSuperPaperBros", "Disc", "DATA", "files", "map", args.name + ".bin")
    print("reading", disc)
    arc = parse_u8(lz10(open(disc, "rb").read()))
    base = "./dvd/map/%s/" % args.name
    mp = MapDat(arc[base + "map.dat"])
    tpl = arc[base + "texture.tpl"]
    report = []

    def say(s):
        print(s)
        report.append(s)

    # ---- tables
    tt = mp.chunks["texture_table"]
    tex_names = [mp.cstr(mp.u32(tt + 4 + i * 4)) for i in range(mp.u32(tt))]
    tex_index = {n: i for i, n in enumerate(tex_names)}
    vt = mp.chunks["vcd_table"]
    pos_arr, nrm_arr, col_arr, uv_arr = (mp.u32(vt + k) + 4 for k in (0, 4, 12, 24))  # skip the u32 count
    info = mp.u32(mp.chunks["information"] + 4)   # world_root joint
    s_root = [k for k in mp.kids(info) if mp.cstr(mp.u32(k)) == "S"][0]

    # ---- textures: decode only what is needed, later
    tpl_magic, tpl_n, tpl_tab = struct.unpack(">III", tpl[:12])
    assert tpl_magic == 0x0020AF30 and tpl_n == len(tex_names)

    tex_info = {}   # tex index -> dict(has_alpha, w, h, fmt)

    def tex_has_alpha(idx):
        if idx in tex_info:
            return tex_info[idx]["alpha"]
        w, h, fmt, px = decode_tpl_image(tpl, struct.unpack(">II", tpl[tpl_tab + idx * 8:tpl_tab + idx * 8 + 8])[0])
        tex_info[idx] = dict(alpha=any(p[3] < 250 for p in px), w=w, h=h, fmt=fmt, px=px)
        return tex_info[idx]["alpha"]

    # ---- materials
    def material_state(mat):
        name = mp.cstr(mp.u32(mat))
        color = tuple(mp.D[mat + 4:mat + 8])
        flags = tuple(mp.D[mat + 8:mat + 12])        # byte 3 = texture count; byte 2 = 2 on "..._x" shadow-like mats
        tcount = flags[3]
        tex = -1
        wrap = (1, 1)
        if tcount > 0:
            entry = mp.u32(mat + 0xC)
            tinfo = mp.u32(entry)
            tname = mp.cstr(mp.u32(tinfo))
            tex = tex_index[tname]
            wrap = (mp.D[entry + 8], mp.D[entry + 9])
        blend = flags[2] == 2 or color[3] < 255 or (tex >= 0 and tex_has_alpha(tex))
        return name, color, flags, tex, wrap, blend

    # ---- bake geometry
    # section "oku" separate, everything else "main"
    parts = {"main": OrderedDict(), "oku": OrderedDict()}     # part -> batch key -> list of triangles (vertex tuples)
    mat_report = {}
    stats = Counter()
    lo = {"main": [1e9] * 3, "oku": [1e9] * 3}
    hi = {"main": [-1e9] * 3, "oku": [-1e9] * 3}
    section_tris = Counter()
    frac = 1.0 / UV_ONE
    clip = 0
    for j, m, section in walk_with_matrices(mp, s_root, IDENT, ""):
        pc = mp.s32(j + 0x5C)
        if pc <= 0:
            continue
        dm = mp.u32(j + 0x58)
        cull = mp.D[dm + 1]
        part = "oku" if section == "oku" else "main"
        for p in range(pc):
            mat = mp.u32(j + 0x60 + p * 8)
            mesh = mp.u32(j + 0x64 + p * 8)
            if not mesh:
                continue
            name, color, flags, tex, wrap, blend = material_state(mat)
            mat_report[mat] = (name, color, flags, tex, wrap, blend)
            key = (tex, wrap[0], wrap[1], cull, blend)
            mask, lists = mesh_lists(mp, mesh)
            bits = [b for b in range(16) if mask >> b & 1]
            stride = len(bits) * 2
            tris = parts[part].setdefault(key, [])
            for off in lists:
                op = mp.D[off]
                cnt = mp.u16(off + 1)
                verts = []
                for v in range(cnt):
                    o = off + 3 + v * stride
                    idx = {b: mp.u16(o + k * 2) for k, b in enumerate(bits)}
                    x, y, z = struct.unpack(">3h", mp.D[pos_arr + idx[0] * 6:pos_arr + idx[0] * 6 + 6])
                    x, y, z = x / 128.0, y / 128.0, z / 128.0
                    wx = m[0][0] * x + m[0][1] * y + m[0][2] * z + m[0][3]
                    wy = m[1][0] * x + m[1][1] * y + m[1][2] * z + m[1][3]
                    wz = m[2][0] * x + m[2][1] * y + m[2][2] * z + m[2][3]
                    for a, w_ in enumerate((wx, wy, wz)):
                        lo[part][a] = min(lo[part][a], w_)
                        hi[part][a] = max(hi[part][a], w_)
                    px_, py_, pz_ = (int(round(c * POS_FRAC)) for c in (wx, wy, wz))
                    if max(abs(px_), abs(py_), abs(pz_)) > 32767:
                        clip += 1
                    px_, py_, pz_ = (max(-32768, min(32767, c)) for c in (px_, py_, pz_))
                    if 4 in idx:
                        u, vv = struct.unpack(">2h", mp.D[uv_arr + idx[4] * 4:uv_arr + idx[4] * 4 + 4])
                        vv = UV_ONE - vv                       # GX v runs downwards, PICA200 v upwards
                        u = max(-32768, min(32767, u))
                        vv = max(-32768, min(32767, vv))
                    else:
                        u = vv = 0
                    if 2 in idx:
                        c = tuple(mp.D[col_arr + idx[2] * 4:col_arr + idx[2] * 4 + 4])
                    else:
                        c = (255, 255, 255, 255)
                    c = tuple(c[k] * color[k] // 255 for k in range(4))
                    verts.append((px_, py_, pz_, u, vv, c))
                if op == 0x98:                                 # triangle strip
                    for i in range(cnt - 2):
                        tri = (verts[i], verts[i + 1], verts[i + 2]) if i % 2 == 0 else (verts[i + 1], verts[i], verts[i + 2])
                        if tri[0][:3] != tri[1][:3] and tri[1][:3] != tri[2][:3] and tri[0][:3] != tri[2][:3]:
                            tris.append(tri)
                elif op == 0x90:                               # plain triangles
                    for i in range(0, cnt - 2, 3):
                        tris.append((verts[i], verts[i + 1], verts[i + 2]))
                elif op == 0xA0:                               # triangle fan
                    for i in range(1, cnt - 1):
                        tris.append((verts[0], verts[i], verts[i + 1]))
                else:
                    stats["unknown opcode %#x" % op] += 1
                section_tris[part] += 0
    for part in parts:
        section_tris[part] = sum(len(t) for t in parts[part].values())
    if clip:
        say("WARNING: %d vertex coordinates exceeded the s16 range and were clamped" % clip)

    # ---- write outputs
    out = args.out
    os.makedirs(os.path.join(out, "textures"), exist_ok=True)
    used_tex = sorted({k[0] for p in parts.values() for k in p if k[0] >= 0})

    for part, batches in parts.items():
        # opaque batches first, blended ones after (the renderer draws in file order)
        order = sorted(batches.keys(), key=lambda k: (k[4], k[0]))
        vlist, vmap, idx_all, btab = [], {}, [], []
        for key in order:
            first = len(idx_all)
            for tri in batches[key]:
                for v in tri:
                    vi = vmap.get(v)
                    if vi is None:
                        vi = vmap[v] = len(vlist)
                        vlist.append(v)
                    idx_all.append(vi)
            btab.append((key, first, len(idx_all) - first))
        if len(vlist) > 65535:
            sys.exit("part %s has %d vertices: more than 16-bit indices can address (needs splitting)" % (part, len(vlist)))
        bb = lo[part] + hi[part] if vlist else [0] * 6
        with open(os.path.join(out, "room_%s.spm" % part), "wb") as f:
            f.write(struct.pack("<4sIIIII6f", b"SPMR", 1, len(tex_names), len(vlist), len(btab), len(idx_all), *bb))
            for (tex, ws, wt, cull, blend), first, count in btab:
                f.write(struct.pack("<iIIBBBBI", tex, first, count, cull, ws, wt, 1 if blend else 0, 0))
            for (x, y, z, u, v, c) in vlist:
                f.write(struct.pack("<4h2h4B", x, y, z, 0, u, v, *c))
            f.write(struct.pack("<%dH" % len(idx_all), *idx_all))
        say("part %-4s: %6d triangles, %6d unique vertices, %3d draw calls (%d blended)" %
            (part, len(idx_all) // 3, len(vlist), len(btab), sum(1 for k, _, _ in btab if k[4])))

    # ---- textures
    tmp = tempfile.mkdtemp(prefix="spm3ds_tex_")
    t3 = find_tex3ds()
    alpha_count = 0
    for idx in used_tex:
        tex_has_alpha(idx)
        ti = tex_info[idx]
        w, h, px = resize_pow2(ti["w"], ti["h"], ti["px"])
        png = os.path.join(tmp, "tex_%03d.png" % idx)
        write_png(png, w, h, px)
        fmt = "etc1a4" if ti["alpha"] else "etc1"
        alpha_count += ti["alpha"]
        dst = os.path.join(out, "textures", "tex_%03d.t3x" % idx)
        r = subprocess.run([t3, "-f", fmt, "-o", dst, png], capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit("tex3ds failed on texture %d: %s" % (idx, r.stderr.strip()[:300]))
    shutil.rmtree(tmp, ignore_errors=True)
    tbytes = sum(os.path.getsize(os.path.join(out, "textures", f)) for f in os.listdir(os.path.join(out, "textures")))
    say("textures: %d of %d used (%d with alpha), %d KB of .t3x" % (len(used_tex), len(tex_names), alpha_count, tbytes // 1024))
    npot = [i for i in used_tex if (tex_info[i]["w"] & (tex_info[i]["w"] - 1)) or (tex_info[i]["h"] & (tex_info[i]["h"] - 1))]
    say("non-power-of-two textures resized: %d" % len(npot))
    for part in parts:
        if section_tris[part]:
            say("bbox %-4s: x %.0f..%.0f  y %.0f..%.0f  z %.0f..%.0f" % (
                part, lo[part][0], hi[part][0], lo[part][1], hi[part][1], lo[part][2], hi[part][2]))
    for k, v in stats.items():
        say("note: " + k + " x%d" % v)

    # ---- material report (which material fields are decoded)
    say("")
    say("materials used in S: %d  | flag bytes seen (b8,b9,b10,texCount): %s" % (
        len(mat_report), sorted(Counter(v[2] for v in mat_report.values()).items())))
    with open(os.path.join(out, "report.txt"), "w") as f:
        f.write("\n".join(report) + "\n\nmaterial  name  rgba  flags  tex  wrap  blend\n")
        for mat, (name, color, flags, tex, wrap, blend) in sorted(mat_report.items()):
            f.write("%#x %-40s %s %s tex=%s(%s) wrap=%s blend=%d\n" % (
                mat, name, color, flags, tex, tex_names[tex] if tex >= 0 else "-", wrap, blend))
    print("wrote", out)


if __name__ == "__main__":
    main()
