"""Writes a short original banner jingle (cia/banner.wav): a rising 5-note arpeggio of decaying sine tones, 16-bit mono 22.05 kHz, 1.9 s.
(The Home Menu plays it when the banner is shown; bannertool wants a WAV of 3 seconds or less.) Pure Python, no Nintendo audio."""
import math, struct, sys, wave
RATE = 22050
notes = [(523.25, 0.00), (659.25, 0.18), (783.99, 0.36), (1046.5, 0.54), (1318.5, 0.78)]   # C5 E5 G5 C6 E6
N = int(RATE * 1.9)
buf = [0.0] * N
for f, t0 in notes:
    for i in range(int((N / RATE - t0) * RATE)):
        t = i / RATE
        env = min(1.0, t / 0.01) * math.exp(-t * 3.2)
        v = env * (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(4 * math.pi * f * t))
        buf[int(t0 * RATE) + i] += 0.28 * v
fade = int(RATE * 0.15)
for i in range(fade):
    buf[N - 1 - i] *= i / fade
out = sys.argv[1] if len(sys.argv) > 1 else 'cia/banner.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
    w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, x)) * 32000)) for x in buf))
print('wrote', out)
