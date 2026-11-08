import numpy as np, wave
SR = 44100; DUR = 20.0; N = int(SR * DUR)
B = 0.5; S = B / 4                      # 120 BPM, 16th = 0.125 s, grid from frame 0
rng = np.random.default_rng(3)
music = np.zeros(N); sfx = np.zeros(N); send = np.zeros(N)
m2f = lambda m: 440 * 2 ** ((m - 69) / 12)

def add(buf, t, sig, g=1.0, rev=0.0):
    i = int(round(t * SR)); j = min(N, i + len(sig))
    if i >= N: return
    buf[i:j] += sig[:j - i] * g
    send[i:j] += sig[:j - i] * g * rev
def tt(d): return np.arange(int(d * SR)) / SR
def marimba(f, d=0.6):
    x = tt(d); env = np.exp(-x * 7) * (1 - np.exp(-x * 900))
    return (np.sin(2*np.pi*f*x) + 0.25*np.sin(2*np.pi*4*f*x)*np.exp(-x*30)) * env
def pop(f):
    x = tt(0.12); fr = f * (1 + 1.2*np.exp(-x*60))
    return np.sin(2*np.pi*np.cumsum(fr)/SR) * np.exp(-x*38) * (1 - np.exp(-x*2000))
def kick():
    x = tt(0.35); fr = 45 + 85*np.exp(-x*30)
    return np.sin(2*np.pi*np.cumsum(fr)/SR) * np.exp(-x*9)
def noise(d, k): x = tt(d); return rng.standard_normal(len(x)) * np.exp(-x*k)
def hp(sig, a=0.9):  # one-pole highpass
    y = np.zeros_like(sig); p = 0; px = 0
    for i, v in enumerate(sig): p = a*(p + v - px); px = v; y[i] = p
    return y
def lp(sig, a):
    y = np.zeros_like(sig); p = 0
    for i, v in enumerate(sig): p += a*(v - p); y[i] = p
    return y
HAT = hp(noise(0.05, 90), 0.75); CLAP = lp(hp(noise(0.18, 22), 0.85), 0.35)
def bass(f, d):
    x = tt(d); env = np.minimum(1, x*200) * np.exp(-x*2.2)
    return np.tanh(1.6*np.sin(2*np.pi*f*x)) * env
def pad(fs, d):
    x = tt(d); env = np.minimum(1, x/0.25) * np.minimum(1, (d - x)/0.4)
    return sum(np.sin(2*np.pi*f*x) + np.sin(2*np.pi*f*1.004*x) for f in fs) / (2*len(fs)) * env
def boing(f0, f1, d):
    x = tt(d); fr = f0 * (f1/f0) ** (x/d) * (1 + 0.03*np.sin(2*np.pi*18*x))
    return np.sin(2*np.pi*np.cumsum(fr)/SR) * np.sin(np.pi*x/d) ** 0.7

PENTA = [60, 62, 64, 67, 69]
# ── Hook: assembly pops climbing the pentatonic on 16ths, then a sparkle when the face pops
for k, t in enumerate(np.arange(0.25, 2.51, S)):
    m = PENTA[k % 5] + 12 * (k // 5)
    add(sfx, t, pop(m2f(m)), 0.32 + 0.1*rng.random(), 0.3)
for k, m in enumerate([84, 88, 91]): add(sfx, 2.625 + k*S/2, marimba(m2f(m), 0.5), 0.18, 0.5)

# ── Groove 3.0–17.5: chords change every 2 s on the beat grid
CH = {'C': [48, 52, 55], 'Am': [45, 48, 52], 'F': [41, 45, 48], 'G': [43, 47, 50]}
prog = [(3, 'C'), (5, 'Am'), (7, 'F'), (9, 'G'), (11, 'C'), (13, 'Am'), (15, 'F'), (17, 'G')]
mel = [0, 2, 1, 2, 0, 1]  # chord-tone index per hit
for start, c in prog:
    d = 0.5 if start == 17 else 2.0
    ch = CH[c]
    add(music, start, pad([m2f(m + 12) for m in ch], d + 0.3), 0.22, 0.6)
    for k in range(int(d / B) * 2):  # bass 8ths
        add(music, start + k*B/2, bass(m2f(ch[0] - 12 + (12 if k % 4 == 3 else 0)), 0.24), 0.30)
    if d == 2.0 and not (14 <= start < 17):
        for k, beat in enumerate([0, 0.5, 1.5, 2, 3, 3.5]):
            add(music, start + beat*B, marimba(m2f(ch[mel[k]] + 24)), 0.20, 0.35)
    elif d == 2.0:  # scene 5: lighter, airy arpeggio
        for k in range(8): add(music, start + k*B/2, marimba(m2f(ch[k % 3] + 36), 0.4), 0.10, 0.6)
for t in np.arange(3.0, 17.5, B):
    if not (14.0 <= t < 17.5): add(music, t, kick(), 0.55)
for t in np.arange(3.25, 17.5, B): add(music, t, HAT, 0.10)
for t in np.arange(3.5, 14.0, 1.0): add(music, t, CLAP, 0.16, 0.3)
# reveal hit
add(music, 3.0, pad([m2f(m) for m in [60, 64, 67, 72]], 1.6), 0.25, 0.7)

# ── SFX in key, on the grid
for t in [4.0, 9.75, 13.25, 16.0, 19.25]: add(sfx, t, marimba(m2f(96), 0.15), 0.05, 0.4)  # blinks
add(sfx, 7.0, pop(m2f(72)), 0.35, 0.3)                                                   # tap
for k, m in enumerate([84, 88, 91, 96]): add(sfx, 7.0 + k*S, marimba(m2f(m), 0.5), 0.14, 0.6)  # hearts
add(sfx, 7.0, boing(m2f(60), m2f(67), 0.3), 0.12, 0.2)                                   # little hop
add(sfx, 10.5, boing(m2f(48), m2f(79), 0.45), 0.2, 0.3)                                  # jump
add(sfx, 11.25, kick(), 0.35)                                                            # landing
for t in [12.0, 12.5, 13.0, 18.0, 18.5]: add(sfx, t, marimba(m2f(79), 0.5), 0.14, 0.5)  # waves
x = tt(1.0); riser = lp(rng.standard_normal(len(x)), 0.08) * (x/1.0)**2
add(sfx, 16.5, riser, 0.35, 0.4)
x = tt(0.5); add(sfx, 14.0, lp(rng.standard_normal(len(x)), 0.05) * np.sin(np.pi*x/0.5), 0.3, 0.4)

# ── Outro 17.5: resolve to C, ring out
add(music, 17.5, kick(), 0.6)
add(music, 17.5, pad([m2f(m) for m in [48, 60, 64, 67, 72]], 2.5), 0.3, 0.7)
add(music, 17.5, bass(m2f(36), 1.5), 0.3)
for k, m in enumerate([72, 76, 79, 84]): add(music, 17.5 + k*S, marimba(m2f(m), 1.0), 0.18, 0.6)

# ── Shared room reverb, mix, gentle master
ir = rng.standard_normal(int(1.3*SR)) * np.exp(-np.arange(int(1.3*SR))/SR * 4.5)
ir = lp(ir, 0.25); ir /= np.sqrt((ir**2).sum())
L = 1 << int(np.ceil(np.log2(N + len(ir))))
wet = np.fft.irfft(np.fft.rfft(send, L) * np.fft.rfft(ir, L), L)[:N]
mix = music + 0.8*sfx + 0.35*wet
mix = np.tanh(mix * 1.1)
fade = np.ones(N); fade[-int(0.8*SR):] = np.linspace(1, 0, int(0.8*SR)) ** 2
mix *= fade; mix *= 0.89 / np.abs(mix).max()
st = np.stack([mix, mix], 1)
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', np.abs(mix).max())
