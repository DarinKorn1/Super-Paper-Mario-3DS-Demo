"""Converts the Flipside theme (sound/map_town_omote1_44k_lp.brstm from the user's own disc dump) to a 3DS-ready file.

BRSTM = Wii streamed audio: DSP-ADPCM (4 bits/sample, 8-byte frames of 14 samples), 2 channels, 44.1 kHz, one loop point.
This script decodes the ADPCM to 16-bit PCM and writes assets/bgm_flipside.pcm for ndsp (libctru), little-endian:
    "SBGM"  u32 version(1)  u32 rate  u32 channels  u32 totalSamples(per channel)  u32 loopStart(samples)
    then totalSamples * channels interleaved s16 samples.
Run from spm3ds-demo/:   python -I tools/convert_bgm.py [path/to/sound/dir]
Output is derived from the game: git-ignored (assets/), never commit or share it."""
import math, struct, sys, os

SRC = (sys.argv[1] if len(sys.argv) > 1 else '../NewSuperPaperBros/Disc/DATA/files/sound') + '/map_town_omote1_44k_lp.brstm'
OUT = 'assets/bgm_flipside.pcm'

b = open(SRC, 'rb').read()
assert b[:4] == b'RSTM'
head_off = struct.unpack('>I', b[0x10:0x14])[0]
h = b[head_off + 8:]                                   # offsets in HEAD are relative to here
o_stream, o_track, o_chan = [struct.unpack('>I', b[head_off + 0x0c + 8 * i:head_off + 0x10 + 8 * i])[0] for i in range(3)]
(codec, loop, nch, _, rate, _, loop_start, total, data_off, nblocks, blocksize, spb, last_size, last_samples, last_padded,
 _, _) = struct.unpack('>BBBBHHIIIIIIIIIII', h[o_stream:o_stream + 0x30] + bytes(4))[:17]
assert codec == 2, 'expected DSP-ADPCM'
print('codec', codec, 'channels', nch, 'rate', rate, 'samples', total, 'loop start', loop_start, 'blocks', nblocks, 'blocksize', blocksize)

# channel info: table of {marker, offset} entries; each leads to {16 s16 coefs, gain, ps, yn1, yn2, loop ps, loop yn1, loop yn2, pad}
count = h[o_chan]
chan = []
for c in range(count):
    off = struct.unpack('>I', h[o_chan + 4 + 8 * c + 4:o_chan + 4 + 8 * c + 8])[0]
    ci_off = struct.unpack('>I', h[off + 4:off + 8])[0]                      # entry -> info struct
    ci = h[ci_off:ci_off + 0x30]
    chan.append(struct.unpack('>16h', ci[:32]) + struct.unpack('>HHhh', ci[32:40]))
    print('channel', c, 'coefs', chan[c][:4], '... ps', chan[c][17], 'yn1,yn2', chan[c][18], chan[c][19])

def decode_channel(c):
    coef = chan[c][:16]
    h1, h2 = chan[c][18], chan[c][19]
    out = []
    for blk in range(nblocks):
        size = last_size if blk == nblocks - 1 else blocksize
        base = data_off + (blk * nch) * blocksize + c * (last_padded if blk == nblocks - 1 else blocksize)
        data = b[base:base + size]
        want = last_samples if blk == nblocks - 1 else spb
        n = 0
        for f in range(0, size, 8):
            hdr = data[f]
            scale = 1 << (hdr & 15)
            c1 = coef[(hdr >> 4) * 2]; c2 = coef[(hdr >> 4) * 2 + 1]
            for i in range(14):
                if n >= want:
                    break
                v = data[f + 1 + (i >> 1)]
                nib = (v >> 4) if (i & 1) == 0 else (v & 15)
                if nib >= 8: nib -= 16
                s = ((nib * scale) << 11) + 1024 + c1 * h1 + c2 * h2 >> 11
                s = -32768 if s < -32768 else 32767 if s > 32767 else s
                h2 = h1; h1 = s
                out.append(s); n += 1
    return out

chans = [decode_channel(c) for c in range(nch)]

# Resample to 32728 Hz, the DSP's native mixing rate, so ndsp does no sample-rate conversion (the emulator played 44.1 kHz too fast).
# Windowed-sinc (Lanczos, 6 lobes, cutoff at the new Nyquist), 256 sub-sample phases.
OUT_RATE = 32728
def resample(x, r_in, r_out):
    ratio = r_in / r_out                       # source samples per output sample (> 1)
    fc = 1.0 / ratio                           # lowpass cutoff relative to the source rate's Nyquist
    A = 6; W = int(A * ratio) + 1; PH = 256
    tab = []
    for p in range(PH):
        fr = p / PH
        row = []
        for k in range(-W + 1, W + 1):
            t = (k - fr) * fc
            w = 1.0 if t == 0 else (math.sin(math.pi * t) / (math.pi * t)) * (math.sin(math.pi * t / A) / (math.pi * t / A)) if abs(t) < A else 0.0
            row.append(w * fc)
        sm = sum(row); tab.append([v / sm for v in row])
    n_out = int(len(x) / ratio)
    pad = [0] * W + list(x) + [0] * (W + 2)
    out = []
    for i in range(n_out):
        pos = i * ratio
        i0 = int(pos); ph = int((pos - i0) * PH)
        base = i0 + 1 - W + W                # index of source sample (i0 - W + 1) in pad
        row = tab[ph]
        acc = 0.0
        seg = pad[base:base + 2 * W]
        for a, b2 in zip(seg, row):
            acc += a * b2
        v = int(round(acc))
        out.append(-32768 if v < -32768 else 32767 if v > 32767 else v)
    return out
chans = [resample(c, rate, OUT_RATE) for c in chans]
loop_start = int(round(loop_start * OUT_RATE / rate))
total = len(chans[0]); rate = OUT_RATE
assert all(len(x) == total for x in chans), [len(x) for x in chans]
os.makedirs('assets', exist_ok=True)
inter = [0] * (total * nch)
for c in range(nch):
    inter[c::nch] = chans[c]
with open(OUT, 'wb') as f:
    f.write(b'SBGM' + struct.pack('<5I', 1, rate, nch, total, loop_start))
    f.write(struct.pack('<%dh' % len(inter), *inter))
print('wrote', OUT, os.path.getsize(OUT), 'bytes,', total / rate, 'seconds, loop from', loop_start / rate, 's')
