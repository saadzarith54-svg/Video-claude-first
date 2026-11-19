"""PERAH LAB promo — synthesised upbeat score + SFX (royalty-free, generated from scratch).
Usage: python3 audio.py out.wav
Every cue time below matches an animation event in main.js."""
import sys, wave
import numpy as np

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)

def t_(d): return np.arange(int(SR * d)) / SR
def env(d, a=0.005, rel=None, curve=4.0):
    t = t_(d); e = np.minimum(1, t / max(a, 1e-4)); e *= np.exp(-curve * t / d) if rel is None else np.clip(1 - (t - (d - rel)) / rel, 0, 1)
    return e
def lp(x, fc):  # one-pole low-pass
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
def lp_fast(x, fc):
    # vectorised approximation via FFT brickwall-ish smooth filter
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (f / fc) ** 4); return np.fft.irfft(X, len(x))
def hp_fast(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / np.sqrt(1 + (fc / np.maximum(f, 1)) ** 4); return np.fft.irfft(X, len(x))
def bp_sweep(x, f0, f1):
    # time-varying band-pass by STFT bins
    n = len(x); hop = 512; win = np.hanning(2048); out = np.zeros(n + 2048)
    for i, s in enumerate(range(0, n, hop)):
        seg = np.zeros(2048); chunk = x[s:s + 2048]; seg[:len(chunk)] = chunk
        fc = f0 * (f1 / f0) ** (s / max(n, 1))
        X = np.fft.rfft(seg * win); f = np.fft.rfftfreq(2048, 1 / SR); X *= np.exp(-((np.log2(np.maximum(f, 1) / fc)) ** 2) / 0.5)
        out[s:s + 2048] += np.fft.irfft(X, 2048) * win
    return out[:n] / 1.5
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(N, i + len(sig)); sig = sig[:j - i] * gain
    L[i:j] += sig * np.sqrt((1 - pan) / 2) * 1.414; R[i:j] += sig * np.sqrt((1 + pan) / 2) * 1.414

# ---------- sound designers ----------
def boom(d=2.5, f0=70, f1=32, g=1.0):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t * 6); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * env(d, .004, curve=3.2); n = lp_fast(rng.standard_normal(len(t)), 900) * env(d, .002, curve=14) * .5
    return (s + n) * g
def clunk(g=1.0):  # floodlight contactor + hum
    d = 1.6; t = t_(d)
    thud = np.sin(2 * np.pi * (55 + 40 * np.exp(-t * 30)) * t) * env(d, .002, curve=9)
    click = hp_fast(rng.standard_normal(len(t)), 2500) * env(d, .0005, curve=180) * .8
    metal = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) for f, k in [(1180, 9), (1730, 12), (2410, 15)]) * .12
    hum = (np.sin(2 * np.pi * 100 * t) + .4 * np.sin(2 * np.pi * 200 * t) + .2 * np.sin(2 * np.pi * 300 * t)) * np.minimum(1, t / .05) * np.exp(-t * 1.4) * .07
    return (thud + click + metal + hum) * g
def whoosh(d=0.8, f0=300, f1=3000, g=1.0, peak=.6):
    t = t_(d); n = rng.standard_normal(len(t)); s = bp_sweep(n, f0, f1)
    e = np.where(t < d * peak, (t / (d * peak)) ** 2, np.exp(-(t - d * peak) / (d * .18)))
    return s * e * g * 3
def tick(g=1.0, f=3200):
    d = .09; t = t_(d); return (np.sin(2 * np.pi * f * t) * .5 + hp_fast(rng.standard_normal(len(t)), 4000) * .5) * np.exp(-t * 70) * g
def pop(g=1.0):
    d = .25; t = t_(d); f = 900 * np.exp(-t * 12) + 300; return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(d, .002, curve=16) * g
def chime(g=1.0, base=1318.5):
    d = 2.4; t = t_(d); s = np.zeros(len(t))
    for m, a, k in [(1, 1, 2.2), (2, .45, 3), (3, .25, 4.5), (4.2, .15, 6), (5.4, .08, 8)]: s += a * np.sin(2 * np.pi * base * m * t) * np.exp(-t * k)
    s += .5 * np.sin(2 * np.pi * base * 1.5 * t) * np.exp(-t * 2.8) * (t > .07)
    return s * np.minimum(1, t / .003) * g * .5
def shimmer(d=1.2, g=1.0):
    t = t_(d); s = np.zeros(len(t))
    for _ in range(26):
        f = rng.uniform(2500, 7500); st = rng.uniform(0, d * .7); k = (t >= st)
        s += k * np.sin(2 * np.pi * f * (t - st)) * np.exp(-(t - st) * 9) * rng.uniform(.2, .6)
    return s * np.sin(np.pi * t / d) ** .5 * g * .25
def riser(d=1.0, g=1.0):
    t = t_(d); n = rng.standard_normal(len(t)); s = bp_sweep(n, 400, 6000) * 2
    tone = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (3 * t / d)) / SR) * .3
    return (s + tone) * (t / d) ** 2.5 * g
def hit(g=1.0):  # title slam: sub + snare-ish crack + boom tail
    d = 1.8; t = t_(d)
    sub = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-t * 18)) / SR) * env(d, .002, curve=3.5)
    crack = lp_fast(rng.standard_normal(len(t)), 5000) * np.exp(-t * 22) * .7
    body = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 16) * .4
    return (sub + crack + body) * g
def taiko(g=1.0):
    d = 1.0; t = t_(d); return (np.sin(2 * np.pi * np.cumsum(62 + 60 * np.exp(-t * 25)) / SR) * np.exp(-t * 6) + lp_fast(rng.standard_normal(len(t)), 600) * np.exp(-t * 30) * .4) * g


def splash(g=1.0):
    d = .9; t = t_(d); n = rng.standard_normal(len(t)); s = bp_sweep(n, 2500, 700) * np.exp(-t * 5) * 1.6
    for _ in range(34):
        st = rng.uniform(0, .5); f0 = rng.uniform(500, 1100); k = t >= st; tt = (t - st) * k
        s += k * np.sin(2 * np.pi * (f0 * tt + 4000 * tt * tt)) * np.exp(-tt * 60) * rng.uniform(.15, .4)
    return s * g
def clink(g=1.0):
    d = .6; t = t_(d); return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) * a for f, k, a in [(2350, 14, .5), (3710, 18, .35), (5120, 24, .25), (6630, 30, .15)]) * g
def kick(g=1.0):
    d = .35; t = t_(d); return np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-t * 32)) / SR) * np.exp(-t * 9) * g
def clap(g=1.0):
    d = .25; t = t_(d); n = hp_fast(rng.standard_normal(len(t)), 900); e = np.zeros(len(t))
    for o in (0, .011, .022): e += (t >= o) * np.exp(-np.maximum(t - o, 0) * (60 if o < .02 else 18))
    return lp_fast(n, 6000) * e * g * .6
def hat(g=1.0, open_=False):
    d = .2 if open_ else .05; t = t_(d); return hp_fast(rng.standard_normal(len(t)), 7000) * np.exp(-t * (14 if open_ else 80)) * g
def pluck(f, d=.28, g=1.0, bright=4000):
    t = t_(d); s = 2 * ((t * f) % 1) - 1 + .5 * (2 * ((t * f * 1.005) % 1) - 1); return lp_fast(s, bright) * np.exp(-t * 9) * np.minimum(1, t / .004) * g
def bassn(f, d, g=1.0):
    t = t_(d); s = 2 * ((t * f) % 1) - 1; return lp_fast(s, 700) * np.minimum(1, t / .005) * np.clip((d - t) / .03, 0, 1) * g

BPM = 112; b = 60 / BPM
def nf(m): return 440 * 2 ** ((m - 69) / 12)
# progression (C major, bright): C  G  Am F   (one chord per bar)
CH = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
BASS = [36, 43, 45, 41]
MEL = [76, 79, 81, 79, 76, 74, 72, 74, 76, 79, 76, 74, 72, 69, 72, 74]  # pentatonic hook (16ths in pairs)
def groove(t0, t1, lead=True, full=True):
    beat = 0; x = t0
    while x < t1 - 1e-6:
        bar = int(beat // 4) % 4; pos = beat % 4
        add(kick(.9 if full else .6), x)
        if pos in (1, 3): add(clap(.55 if full else .35), x, pan=.05)
        add(hat(.18), x + b / 2, pan=.35); add(hat(.1), x, pan=.35)
        if full and pos == 3: add(hat(.12, True), x + b / 2, pan=.35)
        # bass (off-beat bounce)
        add(bassn(nf(BASS[bar]), b * .45, .55), x); add(bassn(nf(BASS[bar] + 12), b * .4, .3), x + b / 2)
        # chord stabs on the off-beat
        if full and pos in (0, 2): [add(pluck(nf(m), .22, .14, 3500), x + b / 2, pan=-.3 + .3 * i) for i, m in enumerate(CH[bar])]
        if not full and pos == 0: [add(pluck(nf(m), .5, .1, 2200), x, pan=-.3 + .3 * i) for i, m in enumerate(CH[bar])]
        if lead: add(pluck(nf(MEL[(int(beat * 2)) % 16]), .2, .16, 5000), x, pan=.2); add(pluck(nf(MEL[(int(beat * 2) + 1) % 16]), .2, .12, 5000), x + b / 2, pan=.2)
        beat += 1; x += b
# ---------- arrangement ----------
# HOOK 0–3.0 : stadium tension (no beat)
add(boom(3.0, 50, 28, .8), 0.0)
for tt, pn in [(.20, -.5), (.45, .5), (.72, -.3), (.90, .3)]: add(clunk(.85), tt, pan=pn)
add(whoosh(1.1, 200, 2500, .5, .8), 1.05, pan=-.3)
add(riser(1.0, .25), 1.2)
add(splash(1.0), 2.15); add(hit(.7), 2.16); add(clink(.4), 2.3)
add(whoosh(.45, 400, 5000, .7, .7), 2.7)
# BRAND reveal 3.0–6.6 : beat drop
add(hit(.9), 3.0); add(boom(1.5, 80, 40, .6), 3.0)
groove(3.0, 6.55, lead=True, full=True)
add(pop(.5), 3.08); add(whoosh(.5, 300, 3000, .35), 3.85); add(whoosh(.55, 200, 2000, .4, .7), 4.0); add(clink(.5), 4.35); add(clink(.35), 4.5)
add(hit(.6), 4.47); add(whoosh(.4, 1500, 6000, .25), 5.0)
add(whoosh(.5, 400, 5000, .55, .6), 6.3)
# BOARD 6.6–15.2 : lighter groove
groove(6.6, 15.0, lead=False, full=False)
for i in range(4): add(pop(.28), 6.65 + i * .12, pan=-.3 + i * .2)
add(whoosh(.85, 250, 1800, .3, .55), 7.2)
for i in range(6): add(tick(.10 + .02 * i), 7.85 + i * .06, pan=-.4 + i * .15)
add(tick(.22, 2400), 8.3); add(chime(.8, 1568), 8.55); add(shimmer(1.3, .9), 8.6); add(whoosh(.4, 1200, 5000, .22), 9.0); add(shimmer(.6, .5), 9.45)
add(whoosh(.7, 220, 2600, .4, .6), 9.85); add(tick(.2, 2800), 10.2); add(pop(.45), 10.45); add(pop(.45), 10.9); add(tick(.18), 11.3); add(shimmer(.6, .5), 11.55)
add(whoosh(.7, 220, 2600, .4, .6), 11.9); add(riser(.85, .14), 12.75); add(pop(.5), 13.55); add(chime(.4, 2093), 13.62)
add(whoosh(.9, 200, 2200, .4, .6), 14.1); add(pop(.4), 14.35); add(riser(.8, .3), 14.4)
add(whoosh(.5, 400, 5000, .55, .6), 14.95)
# END 15.3–20 : full groove + tag
add(hit(.85), 15.3); groove(15.3, 19.6, lead=True, full=True)
add(pop(.5), 15.42); add(whoosh(.55, 200, 2000, .4, .7), 15.55); add(splash(.6), 15.7); add(clink(.4), 15.9)
add(pop(.35), 16.0); add(hit(.55), 16.27); add(pop(.45), 16.82)
add(hit(.9), 19.6); [add(pluck(nf(m), 1.4, .16, 3000), 19.6) for m in (60, 64, 67, 72)]; add(shimmer(1.0, .6), 19.0)
t = np.arange(N) / SR
# ---------- simple stereo reverb + master ----------
ir_len = int(SR * 1.6); ir = rng.standard_normal(ir_len) * np.exp(-np.arange(ir_len) / SR * 3.2); ir = lp_fast(ir, 5000); ir /= np.sqrt(np.sum(ir ** 2))
def conv(x, h): n = len(x) + len(h); F = np.fft.rfft(x, n) * np.fft.rfft(h, n); return np.fft.irfft(F, n)[:len(x)]
L = L + .22 * conv(L, ir); R = R + .22 * conv(R, np.roll(ir, 331))
L = hp_fast(L, 28); R = hp_fast(R, 28)
fade = np.clip((DUR - t) / .35, 0, 1); L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); L = np.tanh(L / pk * 1.6) / np.tanh(1.6) * .89; R = np.tanh(R / pk * 1.6) / np.tanh(1.6) * .89
out = (np.stack([L, R], 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok', sys.argv[1])
