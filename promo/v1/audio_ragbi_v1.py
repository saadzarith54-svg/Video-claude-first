"""Synthesised score + SFX for the 20 s promo (royalty-free, generated from scratch).
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

# ---------- music bed ----------
t = np.arange(N) / SR
def saw(f): return 2 * ((t * f) % 1) - 1
drone = (saw(55) + saw(55.4) * .8 + saw(82.4) * .5 + saw(110.1) * .25)
drone = lp_fast(drone, 380) * .12
dr_env = np.clip(t / 1.5, 0, 1) * np.where(t < 16.95, 1, np.clip(1 - (t - 16.95) / .08, 0, 1))
dr_env += np.where(t >= 17.05, np.clip((t - 17.05) / .4, 0, 1) * np.clip((20 - t) / 1.6, 0, 1) * 1.15, 0)
L += drone * dr_env; R += np.roll(drone, 240) * dr_env
# final chord (D major-ish, warm) from the title hits
for f, a in [(73.4, .7), (110, .5), (146.8, .35), (185, .22), (220, .2), (293.7, .12)]:
    c = (np.sin(2 * np.pi * f * t) + .3 * np.sin(2 * np.pi * 2 * f * t)) * a * .1 * np.where(t > 17.45, np.clip((t - 17.45) / .6, 0, 1) * np.clip((20 - t) / 1.4, 0, 1), 0)
    L += c; R += c
# pulse: 100 BPM taiko from 3.2 → 16.9, denser in the trophy section
beat = 60 / 100
b = 3.24
while b < 16.9:
    big = 10.6 <= b < 14.2
    add(taiko(.55 if big else .38), b, pan=-.1)
    if big or b > 14.2: add(taiko(.22), b + beat / 2, pan=.15)
    b += beat
# soft 8th-note hi tick in the info section for momentum
x = 7.4
while x < 10.4: add(tick(.05, 6000), x, pan=.3); x += beat / 2

# ---------- SFX cues (seconds) ----------
add(boom(3.0, 50, 28, .8), 0.0)                       # dark open rumble
for tt, pn in [(.20, -.5), (.45, .5), (.72, -.3), (.90, .3)]: add(clunk(.9), tt, pan=pn)   # floodlights ignite
add(whoosh(1.25, 200, 2500, .55, .8), 1.2, pan=-.3)    # ball launched from the dark
add(boom(1.6, 90, 45, .55), 2.42)                       # ball lands in hero position
add(shimmer(1.0, .8), 2.4)
add(whoosh(.55, 400, 5000, .8, .7), 2.82)              # ball into camera → transition
for i in range(4): add(pop(.25), 3.28 + i * .13, pan=-.3 + i * .2)   # cards build
add(whoosh(.95, 250, 1800, .35, .55), 3.9)              # push-in to calendar
for i in range(6): add(tick(.10 + .02 * i), 4.5 + i * .07, pan=-.4 + i * .15)   # dates cascade
add(tick(.22, 2400), 5.18)                              # Sabtu column
add(chime(.9), 5.47); add(shimmer(1.4, 1.0), 5.5)       # 21 NOVEMBER highlight
add(whoosh(.4, 1200, 5000, .25), 5.93)                  # pill
add(shimmer(.7, .6), 6.5)                               # card shine
add(whoosh(.8, 220, 2600, .45, .6), 7.35)               # camera arc → info card
add(hit(.55), 7.86)                                     # "HTK"
for tt in (8.2, 8.45, 8.65): add(tick(.22, 2800), tt)
add(shimmer(.7, .6), 9.45)
add(whoosh(.6, 300, 4500, .7, .6), 10.25)               # whip to trophy
add(boom(2.6, 75, 34, .9), 10.62); add(shimmer(2.2, .9), 10.7)   # trophy reveal
add(whoosh(.55, 300, 4500, .6, .6), 13.85)              # back to board
add(riser(.95, .12), 14.8)                              # route drawing
add(pop(.45), 15.72); add(chime(.45, 1760), 15.78)      # pin drop + ping
add(whoosh(.9, 200, 2200, .4, .6), 16.2)                # pull-out
add(riser(.8, .35), 16.25)
add(boom(2.0, 60, 30, .9), 17.05)                       # cut to finale
for tt in (17.45, 17.85, 18.3): add(hit(.95), tt)       # SATU PADANG / SEMANGAT / KEBANGGAAN
add(shimmer(1.4, .8), 18.75)

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
