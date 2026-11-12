"""Draws the original 48x48 Homebrew Launcher icon (icon.png) and a 256x128 banner image (banner.png).
Pure Python (zlib only). Everything is drawn from simple shapes; no Nintendo artwork.
To use your own icon: replace spm3ds-demo/icon.png with any 48x48 PNG and run `make` again."""
import math, struct, sys, zlib

def png(path, w, h, px):
    raw = b''.join(b'\x00' + bytes(c for p in px[y*w:(y+1)*w] for c in p) for y in range(h))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    open(path, 'wb').write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

def inside_poly(x, y, pts):
    c = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]; xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c

def star(cx, cy, ro, ri):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = ro if i % 2 == 0 else ri
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def scene(u, v):
    """u, v in 0..1; returns RGBA or None. Blue rounded tile, a white sheet of paper with a folded corner, a yellow star."""
    # rounded square tile
    dx = max(abs(u - 0.5) - 0.40, 0); dy = max(abs(v - 0.5) - 0.40, 0)
    if math.hypot(dx, dy) > 0.10:
        return None
    c = (40 + int(40 * v), 110 + int(50 * v), 200 + int(30 * v), 255)          # blue gradient
    sheet = [(0.24, 0.14), (0.62, 0.14), (0.78, 0.30), (0.78, 0.86), (0.24, 0.86)]
    shadow = [(x + 0.03, y + 0.03) for x, y in sheet]
    if inside_poly(u, v, shadow):
        c = (20, 60, 130, 255)
    if inside_poly(u, v, sheet):
        c = (250, 248, 238, 255)
        if inside_poly(u, v, [(0.62, 0.14), (0.78, 0.30), (0.62, 0.30)]):
            c = (205, 200, 185, 255)                                          # folded corner
        if inside_poly(u, v, star(0.51, 0.55, 0.20, 0.085)):
            c = (245, 190, 30, 255)
            if inside_poly(u, v, star(0.51, 0.55, 0.20, 0.085)) and not inside_poly(u, v, star(0.51, 0.55, 0.16, 0.066)):
                c = (225, 140, 20, 255)                                       # outline
    return c

def render(w, h, ss=4, fn=scene, aspect=1.0):
    out = []
    for y in range(h):
        for x in range(w):
            acc = [0, 0, 0, 0]
            for sy in range(ss):
                for sx in range(ss):
                    r = fn((x + (sx + .5) / ss) / w, (y + (sy + .5) / ss) / h)
                    if r:
                        a = r[3]
                        acc[0] += r[0] * a; acc[1] += r[1] * a; acc[2] += r[2] * a; acc[3] += a
            n = ss * ss
            if acc[3] == 0:
                out.append((0, 0, 0, 0))
            else:
                out.append((int(acc[0] / acc[3]), int(acc[1] / acc[3]), int(acc[2] / acc[3]), int(acc[3] / n)))
    return out

def banner_scene(u, v):
    # 256x128: gradient sky, the paper-star tile on the left (4:1 scaled to the height), simple stripes on the right
    if u < 0.5:
        r = scene(u * 2 * 0.5 + 0.0, v) if u < 0.5 else None
    base = (30 + int(30 * v), 80 + int(60 * v), 170 + int(40 * v), 255)
    x = (u - 0.5) * 2.0
    if 0.10 < u < 0.10 + 0.5 * 0.5 and False:
        pass
    # tile in the middle, 128x128 square -> u in 0.25..0.75
    if 0.25 <= u <= 0.75:
        t = scene((u - 0.25) * 2.0, v)
        if t:
            return t
    return base

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    png(out + '/icon.png', 48, 48, render(48, 48, 8))
    png(out + '/banner.png', 256, 128, render(256, 128, 2, banner_scene))
    print('wrote icon.png (48x48) and banner.png (256x128) to', out)
