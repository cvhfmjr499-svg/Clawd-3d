import numpy as np, wave, json
SR = 44100; DUR = 20.0; N = int(SR * DUR); B = 0.5; S = B / 4
rng = np.random.default_rng(5)
mus = np.zeros(N); send = np.zeros(N)
m2f = lambda m: 440 * 2 ** ((m - 69) / 12)
def add(t, sig, g=1.0, rev=0.0):
    i = int(round(t * SR)); j = min(N, i + len(sig))
    if i < N: mus[i:j] += sig[:j-i] * g; send[i:j] += sig[:j-i] * g * rev
def tt(d): return np.arange(int(d * SR)) / SR
def lp(x, a):
    y = np.zeros_like(x); p = 0
    for i, v in enumerate(x): p += a * (v - p); y[i] = p
    return y
def hp(x, a):
    y = np.zeros_like(x); p = px = 0
    for i, v in enumerate(x): p = a * (p + v - px); px = v; y[i] = p
    return y
def kick(g=1):
    x = tt(0.4); f = 48 + 90 * np.exp(-x * 28)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-x * 8) * g
def marimba(f, d=0.5):
    x = tt(d); return (np.sin(2*np.pi*f*x) + 0.25*np.sin(2*np.pi*4*f*x)*np.exp(-x*30)) * np.exp(-x*7) * (1-np.exp(-x*900))
def bass(f, d=0.24):
    x = tt(d); return np.tanh(1.8*np.sin(2*np.pi*f*x)) * np.minimum(1, x*300) * np.exp(-x*3)
def pad(fs, d):
    x = tt(d); env = np.minimum(1, x/0.3) * np.minimum(1, (d-x)/0.5)
    return sum(np.sin(2*np.pi*f*x) + np.sin(2*np.pi*f*1.005*x) for f in fs) / (2*len(fs)) * env
HAT = hp(rng.standard_normal(int(0.05*SR)) * np.exp(-tt(0.05)*90), 0.7)
CLAP = lp(hp(rng.standard_normal(int(0.2*SR)) * np.exp(-tt(0.2)*20), 0.85), 0.35)
CH = [[48,52,55],[45,48,52],[41,45,48],[43,47,50]]

# 0–1: quiet room, a soft UI tap at 1.0 lands on the downbeat
x = tt(0.06); add(1.0, np.sin(2*np.pi*m2f(84)*x)*np.exp(-x*60), 0.12, 0.4)
add(0.0, lp(rng.standard_normal(int(1.0*SR)), 0.02) * 0.6, 0.15)
kicks = []
for k in range(8):                      # bars from 1.0, 2 s each: C Am F G C Am F (G = break)
    t0 = 1.0 + 2 * k; ch = CH[k % 4]; brk = (k == 7)
    add(t0, pad([m2f(m+12) for m in ch], 2.3), 0.2 if not brk else 0.28, 0.6)
    for s in range(16):
        t = t0 + s * S * 2 / 2 * 1  # 16 eighth-ish? -> use 16ths over 2 s = 8 beats? keep 16ths of half-bar grid
    for s in range(32):                 # 16th grid across the 2 s bar
        t = t0 + s * S
        if brk:
            if s % 8 == 0: add(t, HAT, 0.08)
            continue
        if s % 4 == 0: add(t, kick(), 0.7); kicks.append(round(t, 3))
        if s % 4 == 2: add(t, HAT, 0.12)
        if s % 8 == 4: add(t, CLAP, 0.18, 0.3)
        if s % 2 == 0: add(t, bass(m2f(ch[0] - 12 + (12 if s % 8 == 6 else 0))), 0.32)
        if s % 32 in (0, 3, 6, 10, 12, 16, 19, 22, 26, 28):
            idx = [0,1,2,1,2,0,2,1,2,1][(0,3,6,10,12,16,19,22,26,28).index(s % 32)]
            add(t, marimba(m2f(ch[idx] + 24)), 0.22, 0.35)
# break riser 15–17
x = tt(2.0); add(15.0, lp(rng.standard_normal(len(x)), 0.04 + 0.0) * (x/2.0)**2.2, 0.55, 0.5)
for k in range(8): add(15.0 + k*0.25, marimba(m2f([67,72,76,79,84,88,91,96][k]), 0.3), 0.08 + 0.02*k, 0.6)
# drop at 17: C groove for one bar, final hit at 19
for s in range(16):
    t = 17.0 + s * S; ch = CH[0]
    if s % 4 == 0: add(t, kick(1.1 if s == 0 else 1), 0.75); kicks.append(round(t, 3))
    if s % 4 == 2: add(t, HAT, 0.12)
    if s % 8 == 4: add(t, CLAP, 0.18, 0.3)
    if s % 2 == 0: add(t, bass(m2f(36 + (12 if s % 8 == 6 else 0))), 0.32)
for k, m in enumerate([72, 76, 79, 84]): add(17.0 + k*S, marimba(m2f(m), 0.6), 0.2, 0.5)
add(17.0, pad([m2f(m) for m in [60,64,67,72]], 2.0), 0.25, 0.7)
add(19.0, kick(1.1), 0.75); kicks.append(19.0)
add(19.0, pad([m2f(m) for m in [48,60,64,67,72]], 1.0), 0.32, 0.8)
for k, m in enumerate([84, 88, 91, 96]): add(19.0 + k*S/2, marimba(m2f(m), 0.9), 0.14, 0.7)

ir = lp(rng.standard_normal(int(1.2*SR)) * np.exp(-tt(1.2)*4.5), 0.25); ir /= np.sqrt((ir**2).sum())
L = 1 << int(np.ceil(np.log2(N + len(ir))))
wet = np.fft.irfft(np.fft.rfft(send, L) * np.fft.rfft(ir, L), L)[:N]
mix = np.tanh((mus + 0.35*wet) * 1.05)
fade = np.ones(N); fade[-int(0.6*SR):] = np.linspace(1, 0, int(0.6*SR))**2
mix *= fade; mix *= 0.85 / np.abs(mix).max()
with wave.open('music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype('<i2').tobytes())

# spectrum per video frame, 16 log bands 40 Hz–12 kHz, mapped like AnalyserNode bytes (-100..-30 dB)
win = np.hanning(2048); hz = SR / 2048; bands = []
for f in range(600):
    c = int(f / 30 * SR); seg = mix[max(0, c-2048):c]
    seg = np.pad(seg, (2048 - len(seg), 0))
    mag = np.abs(np.fft.rfft(seg * win)) / 2048 * 4
    db = 20 * np.log10(mag + 1e-9); v = np.clip((db + 100) / 70, 0, 1)
    row = []
    for b in range(16):
        lo = int(40 * 300 ** (b/16) / hz); hi = max(lo+1, int(40 * 300 ** ((b+1)/16) / hz))
        row.append(round(float(v[lo:hi].mean()), 3))
    bands.append(row)
json.dump({'kicks': sorted(set(kicks)), 'bands': bands}, open('analysis.json', 'w'))
print(len(kicks), 'kicks; peak', np.abs(mix).max())
