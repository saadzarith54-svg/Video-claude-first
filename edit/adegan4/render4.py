"""Render ADEGAN 4 preview.
usage: python3 render4.py SRCDIR TRANSDIR TRACKDIR OUTDIR [--final]
  SRCDIR: c01.bin..c12.bin   TRANSDIR: c02.json c03.json c04.json (+ cNN.wav 16k)   TRACKDIR: trNN.json
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edl4 as L

SRCDIR, TRANSDIR, TRACKDIR, OUT = sys.argv[1:5]
FINAL = "--final" in sys.argv
W, H, FPS, SR = 1280, 720, 30, 48000
os.makedirs(OUT, exist_ok=True)

TEAL = (16, 143, 132); TEAL_D = (8, 70, 66); YEL = (255, 210, 63); WHITE = (255, 255, 255)
RED = (220, 60, 50); INK = (20, 20, 20); PANEL = (10, 30, 34)
FD = "/usr/share/fonts/opentype/inter/"
F_XB, F_B, F_SB, F_M = FD + "Inter-ExtraBold.otf", FD + "Inter-Bold.otf", FD + "Inter-SemiBold.otf", FD + "Inter-Medium.otf"
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]
def tw(t, f): return f.getlength(t)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def inout(t, t_in, t_out, d_in=0.35, d_out=0.25):
    if t_in is None or t_out is None or t < t_in or t > t_out: return 0.0, 0.0
    return (t - t_in) / d_in, 1 - clamp((t - (t_out - d_out)) / d_out)
def rrect(d, box, r, fill, outline=None, width=1): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)
def src(clip): return os.path.join(SRCDIR, L.CLIP[clip])

# ------------------------------------------------------------------ tracking
TRK = {}
def load_track(clip, sigma):
    num = L.CLIP[clip][1:3]
    r = json.load(open(os.path.join(TRACKDIR, f"tr{num}.json")))
    t = np.array([x[0] for x in r]); ok = np.array([x[1] is not None and x[3] is not None and x[3] > 120 and x[1] > 30 for x in r])
    if ok.sum() < 3: return None
    xs = np.interp(t, t[ok], np.array([x[1] if o else 0 for x, o in zip(r, ok)])[ok])
    ys = np.interp(t, t[ok], np.array([x[2] if o else 0 for x, o in zip(r, ok)])[ok])
    k = np.exp(-0.5 * (np.arange(-30, 31) / (sigma * 10)) ** 2); k /= k.sum()
    pad = lambda v: np.convolve(np.pad(v, 30, mode="edge"), k, mode="valid")
    return t, pad(xs), pad(ys)
def track_pos(clip, tt, sigma=0.6):
    key = (clip, sigma)
    if key not in TRK: TRK[key] = load_track(clip, sigma)
    tr = TRK[key]
    if tr is None: return 640, 360
    return float(np.interp(tt, tr[0], tr[1])), float(np.interp(tt, tr[0], tr[2]))

# ------------------------------------------------------------------ slow-mo sources (motion interpolated 120fps)
def mi_file(clip, a, b):
    p = os.path.join(OUT, f"mi_{clip}_{a:.2f}_{b:.2f}.mp4")
    if not os.path.exists(p):
        s0 = max(0, a - 0.2)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-t", f"{b - a + 0.5:.3f}", "-i", src(clip), "-an",
                        "-vf", "fps=30,minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", p], check=True)
    return p, max(0, a - 0.2)

def read_raw(path, a, n, fps=30, size=(W, H)):
    w, h = size
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(a, 0):.3f}", "-i", path, "-frames:v", str(n),
                          "-vf", f"fps={fps},scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: buf = last if last is not None else bytes(w * h * 3)
        last = buf
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.stdout.close(); p.wait()

def shot_frames(clip, a, b, rate):
    """yield (clip_time, frame) for output frames of [a,b] at rate."""
    n = int(round((b - a) / rate * FPS))
    if rate >= 0.999:
        for k, fr in enumerate(read_raw(src(clip), a, n)): yield a + k / FPS, fr
    else:
        path, s0 = mi_file(clip, a, b)
        need = int(math.ceil((b - s0) * 120)) + 2
        want = [int(round((a + k * rate / FPS - s0) * 120)) for k in range(n)]
        frames = {}
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", path, "-frames:v", str(need), "-vf", f"scale={W}:{H}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        idx, wi, last = 0, 0, None
        while wi < n:
            buf = p.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: buf = last
            last = buf
            while wi < n and want[wi] <= idx:
                yield a + wi * rate / FPS, np.frombuffer(buf, np.uint8).reshape(H, W, 3); wi += 1
            idx += 1
        p.stdout.close(); p.wait()

def crop(fr, cx, cy, z):
    if z <= 1.001: return Image.fromarray(fr)
    cw, ch = W / z, H / z
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    return Image.fromarray(fr).resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

# ------------------------------------------------------------------ timeline
TL = []   # (key, clip, a, b, rate, kind, zoom, f0, n)
f = 0
for i, (clip, a, b, r, z, trk) in enumerate(L.HOOK):
    n = int(round((b - a) / r * FPS)); TL.append((f"hook{i}", clip, a, b, r, "hook", z, f, n)); f += n
HOOK_FREEZE_N = int(round(L.HOOK_TITLE_HOLD * FPS)); HOOK_TITLE_T = f / FPS - 0.9; f += HOOK_FREEZE_N
HOOK_END = f / FPS
for key, clip, a, b, r, kind, z in L.ITEMS:
    n = int(round((b - a) / r * FPS)); TL.append((key, clip, a, b, r, kind, z, f, n)); f += n
MAIN_END = f / FPS
RECAP_N = int(round(L.RECAP_HOLD * FPS)); END_N = int(round(L.END_HOLD * FPS))
TOTAL = f + RECAP_N + END_N; DUR = TOTAL / FPS
RECAP_T0 = MAIN_END; END_T0 = MAIN_END + L.RECAP_HOLD
ITEM = {x[0]: x for x in TL}
def ostart(key): return ITEM[key][7] / FPS
def oend(key): return (ITEM[key][7] + ITEM[key][8]) / FPS
def lo(key, tl):
    it = ITEM[key]; return it[7] / FPS + (tl - it[2]) / it[4]
E = {k: lo(*v) for k, v in L.EV.items()}

# ------------------------------------------------------------------ captions (speech items)
cap = []
for key in ("4.2", "4.3", "4.4"):
    it = ITEM[key]; num = L.CLIP[it[1]][1:3]
    ws = []
    for s in json.load(open(os.path.join(TRANSDIR, f"c{num}.json"))):
        for w in s["words"]:
            txt = w["w"].strip(); bare = txt.strip(",.?!")
            if txt in L.CORRECTIONS: txt = L.CORRECTIONS[txt]
            elif bare in L.CORRECTIONS: txt = txt.replace(bare, L.CORRECTIONS[bare])
            if not txt: continue
            s0, e0 = w["s"], w["e"]
            if e0 <= it[2] + 0.05 or s0 >= it[3] - 0.05: continue
            s0, e0 = max(s0, it[2]), min(e0, it[3])
            if e0 - s0 > 0.9: s0 = e0 - 0.6
            ws.append((txt, lo(key, s0), lo(key, e0)))
    cur = []
    chunks = []
    for w in ws:
        if cur and w[1] - cur[-1][2] > 0.6: chunks.append(cur); cur = []
        cur.append(w)
        if len(cur) >= 4 or w[0][-1] in ",.?!": chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ci, c in enumerate(chunks):
        st, en = c[0][1], c[-1][2] + 0.25
        if ci + 1 < len(chunks) and chunks[ci + 1][0][1] > st: en = min(en, chunks[ci + 1][0][1])
        cap.append((st, en, c))

def caption(d, t):
    for st, en, c in cap:
        if st <= t < en:
            f = font(F_XB, 42); sp = f.getlength(" ")
            total = sum(f.getlength(x[0]) for x in c) + sp * (len(c) - 1)
            x = (W - total) / 2; y = 618 + (1 - eob((t - st) / 0.18)) * 14
            for wt, s, e in c:
                d.text((x, y), wt, font=f, fill=(YEL if s <= t < e + 0.05 else WHITE) + (255,), stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += f.getlength(wt) + sp
            return

def wrap(txt, f, width):
    lines, cur = [], ""
    for wd in txt.split():
        test = (cur + " " + wd).strip()
        if tw(test, f) <= width or not cur: cur = test
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def check(d, x, y, s, col):
    d.line([(x, y + s * 0.5), (x + s * 0.38, y + s * 0.85), (x + s, y + s * 0.1)], fill=col, width=max(3, int(s * 0.18)), joint="curve")

# ------------------------------------------------------------------ graphics
def lower_third(d, t, t_in, t_out, name, tag):
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); fN, fT = font(F_XB, 36), font(F_B, 19)
    wN = tw(name, fN) + 48; x0 = -wN + (wN + 40) * eo(p); y0 = 450; wT = tw(tag, fT) + 28
    rrect(d, (x0, y0, x0 + wT, y0 + 32), 8, YEL + (a,)); d.text((x0 + 14, y0 + 5), tag, font=fT, fill=INK + (a,))
    rrect(d, (x0, y0 + 38, x0 + wN, y0 + 98), 10, TEAL + (int(235 * q),))
    d.rectangle((x0, y0 + 38, x0 + 8, y0 + 98), fill=YEL + (a,))
    d.text((x0 + 26, y0 + 47), name, font=fN, fill=WHITE + (a,))

def tag(d, t, t_in, t_out, small, big, col=RED, y=32):
    p, q = inout(t, t_in, t_out, 0.35, 0.25)
    if q <= 0: return
    a = int(255 * q); f1, f2 = font(F_XB, 19), font(F_XB, 32)
    x = 32 - (1 - eo(p)) * 700
    rrect(d, (x, y, x + tw(small, f1) + 26, y + 32), 8, YEL + (a,)); d.text((x + 13, y + 6), small, font=f1, fill=INK + (a,))
    rrect(d, (x, y + 38, x + tw(big, f2) + 36, y + 90), 10, col + (int(235 * q),)); d.text((x + 18, y + 45), big, font=f2, fill=WHITE + (a,))

def checklist(d, t, t_in, t_out, title, items, x0=None, y0=140):
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 400; x0 = (W - pw - 32) if x0 is None else x0
    x0 += (1 - eo(p)) * (pw + 60)
    rrect(d, (x0, y0, x0 + pw, y0 + 44), 10, YEL + (a,)); d.text((x0 + 16, y0 + 9), title, font=font(F_XB, 22), fill=INK + (a,))
    y = y0 + 54
    for ti, txt in items:
        on = ti is not None and t >= ti
        pi = eob((t - ti) / 0.35) if on else 0
        rrect(d, (x0, y, x0 + pw, y + 54), 12, ((TEAL if on else PANEL) + (int(225 * q),)))
        if on:
            check(d, x0 + 14, y + 15, 26 * clamp(pi, 0.3, 1.1), YEL + (a,))
        else:
            d.ellipse((x0 + 16, y + 15, x0 + 40, y + 39), outline=(140, 170, 170, a), width=3)
        d.text((x0 + 54, y + 14), txt, font=font(F_B, 22), fill=(WHITE if on else (170, 190, 190)) + (a,))
        y += 62

def big_title(d, t, t_in, t_out, small, big, sub=None, y=230):
    p, q = inout(t, t_in, t_out, 0.4, 0.3)
    if q <= 0: return
    a = int(255 * q); f1 = font(F_XB, 28); w1 = tw(small, f1) + 34
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 46), 10, YEL + (a,)); d.text(((W - tw(small, f1)) / 2, y + 7), small, font=f1, fill=INK + (a,))
    sc = clamp(eob((t - t_in - 0.12) / 0.45), 0, 1.2)
    if sc > 0.02:
        f = font(F_XB, max(8, int(76 * sc)))
        d.text(((W - tw(big, f)) / 2, y + 112 - 38 * sc), big, font=f, fill=WHITE + (a,), stroke_width=7, stroke_fill=(0, 0, 0, a))
    if sub and t > t_in + 0.5:
        fs = font(F_XB, 30); aa = int(a * clamp((t - t_in - 0.5) / 0.3))
        d.text(((W - tw(sub, fs)) / 2, y + 170), sub, font=fs, fill=YEL + (aa,), stroke_width=4, stroke_fill=(0, 0, 0, aa))

def banner(d, t, t_in, dur, num, txt):
    p, q = inout(t, t_in, t_in + dur, 0.4, 0.35)
    if q <= 0: return
    a = int(255 * q); y = 250; hgt = 150
    xw = W * eo(p)
    d.rectangle((0, y, xw, y + hgt), fill=(8, 28, 32, int(225 * q)))
    d.rectangle((0, y, xw, y + 8), fill=YEL + (a,)); d.rectangle((0, y + hgt - 8, xw, y + hgt), fill=YEL + (a,))
    if p > 0.5:
        aa = int(a * clamp((p - 0.5) * 2))
        f1, f2 = font(F_XB, 26), font(F_XB, 64)
        lab = f"KOMPONEN {num}/4"
        d.text(((W - tw(lab, f1)) / 2, y + 22), lab, font=f1, fill=YEL + (aa,))
        d.text(((W - tw(txt, f2)) / 2, y + 56), txt, font=f2, fill=WHITE + (aa,))

COMP = [("Jogging ringan", "c1", [("c1_dose", "2 minit"), ("c1_goal", "Naikkan suhu badan")]),
        ("Regangan dinamik", "c2", [("c2_ex", "Ayunan kaki · lunges · putaran pinggul"), ("c2_dose", "10 kali setiap set"), ("c2_goal", "Lenturkan pinggul & kaki")]),
        ("Drill larian", "c3", [("c3_ex", "A-skip · B-skip · high knees"), ("c3_dose", "2 set × 30 m"), ("c3_goal", "Postur & ritma larian")]),
        ("Pecutan progresif", "c4", [("c4_ex", "Perlahan → hampir laju penuh"), ("c4_dose", "2 ulangan × 30 m"), ("c4_int", "Intensiti 60–70%")])]
def comp_panel(d, t):
    t_in, t_out = E["c1"] - 0.2, oend("4.4") + 0.1
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 400; x0 = 28 - (1 - eo(p)) * (pw + 60); y0 = 120
    rrect(d, (x0, y0, x0 + pw, y0 + 40), 10, YEL + (a,)); d.text((x0 + 14, y0 + 8), "PEMANASAN BADAN", font=font(F_XB, 21), fill=INK + (a,))
    y = y0 + 48
    active = max([k for k, (_, key, _) in enumerate(COMP) if t >= E[key]] or [-1])
    for k, (name, key, rows) in enumerate(COMP):
        if t < E[key]: continue
        pi = clamp(eob((t - E[key]) / 0.35)); aa = int(a * pi)
        if k == active:
            shown = [(E[rk], txt) for rk, txt in rows if t >= E[rk]]
            h = 48 + 30 * len(shown)
            rrect(d, (x0, y, x0 + pw, y + h), 12, TEAL + (int(235 * q * pi),))
            d.text((x0 + 16, y + 10), f"{k + 1}. {name}", font=font(F_XB, 24), fill=WHITE + (aa,))
            yy = y + 46
            for ti, txt in shown:
                ra = int(aa * clamp((t - ti) / 0.3))
                d.text((x0 + 20, yy), "• " + txt, font=font(F_SB, 19), fill=YEL + (ra,)); yy += 30
            y += h + 8
        else:
            rrect(d, (x0, y, x0 + pw, y + 40), 10, PANEL + (int(220 * q * pi),))
            check(d, x0 + 14, y + 11, 18, YEL + (aa,))
            d.text((x0 + 42, y + 9), f"{k + 1}. {name}", font=font(F_B, 20), fill=(190, 215, 212, aa))
            y += 48

def intensity_gauge(d, t, t_in, t_out, x0=None, y0=150, auto=None):
    p, q = inout(t, t_in, t_out, 0.4, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 330; x0 = (W - pw - 32) if x0 is None else x0
    rrect(d, (x0, y0, x0 + pw, y0 + 120), 14, PANEL + (int(225 * q),))
    d.text((x0 + 16, y0 + 12), "INTENSITI", font=font(F_XB, 20), fill=YEL + (a,))
    lvl = 0.7 * eo((t - t_in) / 5.0) if auto is None else auto
    bx0, bx1, by = x0 + 16, x0 + pw - 16, y0 + 56
    rrect(d, (bx0, by, bx1, by + 26), 13, (40, 70, 74, a))
    zx0, zx1 = bx0 + (bx1 - bx0) * 0.6, bx0 + (bx1 - bx0) * 0.7
    d.rectangle((zx0, by - 6, zx1, by + 32), outline=YEL + (a,), width=2)
    rrect(d, (bx0, by, bx0 + max(26, (bx1 - bx0) * lvl), by + 26), 13, (RED if lvl > 0.58 else TEAL) + (a,))
    lab = f"{int(round(lvl * 100))}%"; d.text((x0 + 16, y0 + 88), f"{lab}  ·  sasaran 60–70%", font=font(F_B, 19), fill=WHITE + (a,))

def demo_overlay(d, t, key):
    base = key[1:] if key.startswith("r") else key
    title, dose, goal, cue = L.DEMO[base]
    t0, t1 = ostart(key), oend(key)
    idx = list(L.DEMO).index(base) + 1
    small = ("SLOW-MO REPLAY" if key.startswith("r") else f"DEMONSTRASI {idx}/8 · {L.DEMO_GROUP[base]}")
    tag(d, t, t0 + 0.15, t1 - 0.05, small, title, col=(RED if not key.startswith("r") else TEAL))
    # info chips bottom-left
    p, q = inout(t, t0 + 0.6, t1 - 0.05, 0.35, 0.25)
    if q > 0:
        a = int(255 * q); f = font(F_XB, 22); x = 32 - (1 - eo(p)) * 600; y = 560
        for txt, col in ((dose, TEAL), (goal, PANEL)):
            w = tw(txt, f) + 34
            rrect(d, (x, y, x + w, y + 44), 22, col + (int(235 * q),)); d.text((x + 17, y + 9), txt, font=f, fill=WHITE + (a,))
            x += w + 10
    if cue:
        p2, q2 = inout(t, t0 + 1.5, t1 - 0.05, 0.35, 0.25)
        if q2 > 0:
            a = int(255 * q2); f = font(F_XB, 22); w = tw(cue, f) + 40; x = W - 32 - w + (1 - eo(p2)) * (w + 60)
            rrect(d, (x, 150, x + w, 196), 23, YEL + (a,)); d.text((x + 20, 160), cue, font=f, fill=INK + (a,))
    if base == "4.5" and not key.startswith("r"):
        p3, q3 = inout(t, t0 + 2.0, t1 - 0.05, 0.35, 0.25)
        if q3 > 0:
            a = int(255 * q3); f = font(F_B, 19); txt = "Dalam latihan sebenar: 2 minit berterusan"; w = tw(txt, f) + 30
            x = W - 32 - w; rrect(d, (x, 150, x + w, 190), 20, (0, 0, 0, int(150 * q3))); d.text((x + 15, 159), txt, font=f, fill=WHITE + (a,))
    if base == "4.12":
        intensity_gauge(d, t, t0 + 0.6, t1 - 0.05, auto=0.7 * eo((t - t0 - 0.6) / 6.5))
    if key.startswith("r"):
        d.ellipse((W - 160, 30, W - 144, 46), fill=RED + (255,)); d.text((W - 136, 26), "SLOW-MO", font=font(F_XB, 20), fill=WHITE + (255,))

def recap(d, t):
    p, q = inout(t, RECAP_T0, END_T0 + 0.2, 0.5, 0.35)
    if q <= 0: return
    a = int(255 * q)
    rrect(d, (40, 40, 380, 90), 12, YEL + (a,)); d.text((58, 49), "RINGKASAN PEMANASAN", font=font(F_XB, 25), fill=INK + (a,))
    cols = [260, 360, 250, 330]; heads = ["Komponen", "Contoh", "Dos", "Tujuan"]
    x0 = (W - sum(cols)) / 2; y = 110
    d.rectangle((x0, y, x0 + sum(cols), y + 46), fill=TEAL + (a,))
    x = x0
    for hd, cw in zip(heads, cols):
        d.text((x + 12, y + 11), hd, font=font(F_XB, 21), fill=WHITE + (a,)); x += cw
    y += 46
    for r, row in enumerate(L.RECAP):
        ti = RECAP_T0 + 0.5 + 0.35 * r; pr = clamp((t - ti) / 0.3)
        if pr <= 0: break
        aa = int(a * pr)
        cells = [wrap(c, font(F_XB if k == 0 else F_M, 21), cw - 24) for k, (c, cw) in enumerate(zip(row, cols))]
        rh = max(len(c) for c in cells) * 27 + 26
        d.rectangle((x0, y, x0 + sum(cols), y + rh), fill=((24, 52, 56) if r % 2 == 0 else (16, 40, 44)) + (int(240 * pr * q),))
        x = x0
        for k, (lines, cw) in enumerate(zip(cells, cols)):
            ly = y + 13
            for ln in lines:
                d.text((x + 12, ly), ln, font=font(F_XB if k == 0 else F_M, 21), fill=(YEL if k == 0 else WHITE) + (aa,)); ly += 27
            x += cw
        y += rh

def end_card(d, t):
    lt = t - END_T0
    if lt < 0: return
    p = eob(lt / 0.45); f1 = font(F_XB, 30); l1 = "SETERUSNYA"; w1 = tw(l1, f1) + 36; y = 250 + (1 - p) * 40
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 48), 10, YEL + (255,)); d.text(((W - tw(l1, f1)) / 2, y + 7), l1, font=f1, fill=INK + (255,))
    if lt > 0.15:
        sc = clamp(eob((lt - 0.15) / 0.4), 0, 1.2); f = font(F_XB, max(8, int(70 * sc))); l2 = "LATIHAN UTAMA →"
        d.text(((W - tw(l2, f)) / 2, y + 100 - 35 * sc), l2, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=(0, 0, 0, 255))

def overlays(t, key):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if t < HOOK_END + 0.1:
        big_title(d, t, HOOK_TITLE_T, HOOK_END + 0.05, "SEBELUM LATIHAN LOMPAT JAUH", "PEMANASAN BADAN", "Kurangkan risiko kecederaan")
    if key == "4.1":
        tag(d, t, E["a1_tag"], oend("4.1") - 0.1, "PERSEDIAAN", "PEMERIKSAAN KAWASAN")
        checklist(d, t, E["a1_tag"] + 0.8, oend("4.1") - 0.1, "SENARAI SEMAK", [(E["a1_kotak"], "Kotak / papan lonjakan stabil"),
                  (E["a1_pasir"], "Pasir digembur"), (E["a1_objek"], "Tiada objek keras")])
    if key == "4.2":
        lower_third(d, t, E["lt_hatim"], E["lt_hatim_out"], "Ahmad Hatim", "PEGAWAI KESELAMATAN")
        checklist(d, t, E["h_check"], oend("4.2") - 0.1, "KAWASAN SELAMAT", [(E["h_pasir"], "Pasir sudah digembur"),
                  (E["h_objek"], "Tiada objek keras"), (E["h_kotak"], "Kotak / papan lonjakan stabil")], y0=60)
    if key == "4.3":
        big_title(d, t, E["pem_title"], oend("4.3") + 0.05, "SEBELUM MULA", "PEMANASAN BADAN", "Jogging · Regangan · Drill · Pecutan")
    if key == "4.4":
        lower_third(d, t, E["lt_zarith"], E["lt_zarith_out"], "Muhammad Zarith Ridzuan", "JURULATIH LAPANGAN 1")
        p, q = inout(t, E["why"], E["why_out"], 0.4, 0.3)
        if q > 0:
            a = int(255 * q); f = font(F_XB, 34); txt = "KENAPA PERLU PEMANASAN?"; w = tw(txt, f) + 44
            rrect(d, ((W - w) / 2, 40 - (1 - eo(p)) * 120, (W + w) / 2, 100 - (1 - eo(p)) * 120), 14, RED + (a,))
            d.text(((W - tw(txt, f)) / 2, 50 - (1 - eo(p)) * 120), txt, font=f, fill=WHITE + (a,))
            for k, (ek, txt2) in enumerate((("why_otot", "Sediakan otot"), ("why_cedera", "Kurangkan risiko kecederaan"))):
                if t >= E[ek]:
                    pi = eob((t - E[ek]) / 0.35); f2 = font(F_XB, 26); w2 = (tw(txt2, f2) + 70) * clamp(pi, 0.3, 1.05)
                    x = 60 if k == 0 else W - 60 - (tw(txt2, f2) + 70); y = 150
                    rrect(d, (x, y, x + w2, y + 54), 27, TEAL + (a,))
                    if pi > 0.9: check(d, x + 18, y + 15, 24, YEL + (a,)); d.text((x + 54, y + 11), txt2, font=f2, fill=WHITE + (a,))
        comp_panel(d, t)
        for sk, num, txt, dur in L.SEC_BANNERS: banner(d, t, E[sk], dur, num, txt)
    if key and (key in L.DEMO or (key.startswith("r") and key[1:] in L.DEMO)): demo_overlay(d, t, key)
    recap(d, t); end_card(d, t)
    caption(d, t)
    if not FINAL: d.text((W - 100, 696), "PREVIEW", font=font(F_B, 16), fill=(255, 255, 255, 140))
    return img

# ------------------------------------------------------------------ PiP previews (preloaded small frames)
PW, PH = 400, 225
PIPF = []
for (lt0, lt1, clip, a, b, lab) in L.PIP:
    n = int(round((b - a) * FPS)); frs = []
    for k, fr in enumerate(read_raw(src(clip), a, n)):
        x, y = track_pos(clip, a + k / FPS) if clip in L.TRACKED else (640, 360)
        frs.append(crop(fr, x, y - 20, 1.5 if clip in L.TRACKED else 1.0).resize((PW, PH), Image.BILINEAR))
    PIPF.append((lo("4.4", lt0), lo("4.4", lt1), frs, lab))
def pip(base, t):
    for o0, o1, frs, lab in PIPF:
        if o0 <= t < o1:
            p = eo((t - o0) / 0.35) * (1 - clamp((t - (o1 - 0.25)) / 0.25))
            img = frs[int((t - o0) * FPS) % len(frs)]
            x, y = W - PW - 34 + (1 - p) * (PW + 60), 128
            sh = Image.new("RGBA", (PW + 16, PH + 56), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
            sd.rounded_rectangle((0, 0, PW + 16, PH + 56), 16, fill=PANEL + (235,))
            base.alpha_composite(sh, (int(x - 8), int(y - 8)))
            m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW, PH), 12, fill=255)
            base.paste(img, (int(x), int(y)), m)
            dd = ImageDraw.Draw(base); f = font(F_XB, 21)
            dd.ellipse((x + 6, y + PH + 14, x + 18, y + PH + 26), fill=RED + (255,))
            dd.text((x + 26, y + PH + 8), "DEMO: " + lab, font=f, fill=WHITE + (255,))
            return

# ------------------------------------------------------------------ video
vid = os.path.join(OUT, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18" if FINAL else "26",
                        "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
FLASHES = [ostart(k) for k in ("4.1", "4.2", "4.4", "4.5", "4.9", "4.12")] + [HOOK_TITLE_T] + \
          [ITEM[f"hook{i}"][7] / FPS for i in range(1, len(L.HOOK))]
fi = 0
def emit(img, key):
    global fi
    t = fi / FPS
    base = img.convert("RGBA")
    if key == "4.4": pip(base, t)
    base.alpha_composite(overlays(t, key)); out = base.convert("RGB")
    for ft in FLASHES:
        dt = t - ft
        if -0.02 <= dt < 0.14: out = Image.blend(out, Image.new("RGB", (W, H), WHITE), 0.7 * (1 - clamp(dt / 0.14)))
    if t > DUR - 0.5: out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (DUR - 0.5)) / 0.5))
    enc.stdin.write(out.tobytes()); fi += 1

last = None
for key, clip, a, b, r, kind, z, f0, n in TL:
    trk = clip in L.TRACKED and kind in ("demo", "replay", "hook")
    sig = 0.3 if kind in ("replay", "hook") else 0.7
    for k, (ct, fr) in enumerate(shot_frames(clip, a, b, r)):
        if trk:
            x, y = track_pos(clip, ct, sig); zz = z
            img = crop(fr, x, y - 20, zz)
        elif key == "4.4":
            zz = [zv for lt, zv in L.ZOOM_44 if ct - a >= lt][-1]; img = crop(fr, 640, 330, zz)
        elif kind == "speech":
            img = crop(fr, 640, 330, 1.0 + 0.06 * k / max(n - 1, 1))
        else:
            img = crop(fr, 640, 360, z + (0.04 * k / max(n - 1, 1) if z > 1 else 0))
        last = img
        emit(img, key)
    if key == f"hook{len(L.HOOK) - 1}":
        for _ in range(HOOK_FREEZE_N): emit(last, key)
    print("done", key, flush=True)
blur = last.filter(ImageFilter.GaussianBlur(16)); dark = Image.blend(blur, Image.new("RGB", (W, H), (6, 22, 26)), 0.62)
for k in range(RECAP_N + END_N):
    emit(Image.blend(last, dark, eo(k / 12)), None)
enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio
NS = int(DUR * SR)
voice = np.zeros((NS + SR, 2), np.float32); amb = np.zeros((NS + SR, 2), np.float32)
def load48(clip):
    p = os.path.join(OUT, f"a48_{clip}.wav")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src(clip), "-ac", "2", "-ar", str(SR), p], check=True)
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
fade = int(0.02 * SR)
music_gain = np.full(NS + SR, 0.32, np.float32)
for key, clip, a, b, r, kind, z, f0, n in TL:
    o = int(f0 / FPS * SR); Ln = int(n / FPS * SR)
    if kind in ("speech",):
        music_gain[o:o + Ln] = 0.085
    if r < 0.999 or kind == "hook": continue
    A = load48(clip); s0 = int(a * SR); c = A[s0:s0 + Ln].copy()
    env = np.ones(len(c), np.float32); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
    if kind == "speech": voice[o:o + len(c)] += c * env[:, None]
    else: amb[o:o + len(c)] += c * env[:, None] * (0.55 if kind == "broll" else 0.35)
# smooth the ducking
k = int(0.35 * SR); music_gain = np.convolve(music_gain, np.ones(k) / k, mode="same")[:NS]
music_gain[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
voice, amb = voice[:NS], amb[:NS]

rng = np.random.default_rng(7)
def tt(d): return np.arange(int(d * SR)) / SR
def onepole(x, fc):
    al = 1 - math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += al * (x[i] - acc); y[i] = acc
    return y
# --- original music loop: 100 BPM, Am - F - C - G, 4 bars
BPM = 100; BEAT = 60 / BPM; BAR = 4 * BEAT; LOOP = 4 * BAR; NL = int(LOOP * SR)
CH = [(110.0, [220.0, 261.63, 329.63]), (87.31, [174.61, 220.0, 261.63]), (130.81, [261.63, 329.63, 392.0]), (98.0, [196.0, 246.94, 293.66])]
loop = np.zeros(NL, np.float32); T = np.arange(NL) / SR
for bi, (root, triad) in enumerate(CH):
    s, e = int(bi * BAR * SR), int((bi + 1) * BAR * SR); tb = T[s:e] - bi * BAR
    pad = sum(np.sin(2 * np.pi * fq * tb) + 0.5 * np.sin(2 * np.pi * fq * 2.003 * tb) * 0.4 for fq in triad) / 3
    penv = np.minimum(1, tb / 0.25) * np.minimum(1, (BAR - tb) / 0.3)
    loop[s:e] += pad * penv * 0.16
    for q8 in range(8):  # bass 8ths
        bs = s + int(q8 * BEAT / 2 * SR); bl = int(BEAT / 2 * SR * 0.9); tq = np.arange(bl) / SR
        loop[bs:bs + bl] += np.tanh(2.2 * np.sin(2 * np.pi * root * tq)) * np.exp(-tq * 5) * 0.16
    for q8 in range(8):  # pluck arpeggio
        fq = triad[[0, 1, 2, 1, 0, 2, 1, 2][q8]] * 2; ps = s + int(q8 * BEAT / 2 * SR); pl = int(0.25 * SR); tq = np.arange(pl) / SR
        loop[ps:ps + pl] += np.sin(2 * np.pi * fq * tq) * np.exp(-tq * 14) * 0.06
for bt in range(16):
    ks = int(bt * BEAT * SR); kl = int(0.35 * SR); tq = np.arange(kl) / SR; fk = 50 + 90 * np.exp(-tq * 30)
    loop[ks:ks + kl] += np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tq * 9) * 0.5
    if bt % 2 == 1:
        cl = int(0.18 * SR); nz = rng.standard_normal(cl).astype(np.float32)
        loop[ks:ks + cl] += (nz - onepole(nz, 1500)) * np.exp(-np.arange(cl) / SR * 22) * 0.22
for h8 in range(32):
    hs = int(h8 * BEAT / 2 * SR) + (int(BEAT / 4 * SR) if h8 % 2 else 0); hl = int(0.05 * SR); nz = rng.standard_normal(hl).astype(np.float32)
    loop[hs:hs + hl] += np.diff(nz, prepend=0) * np.exp(-np.arange(hl) / SR * 80) * 0.07
loop /= np.max(np.abs(loop)) + 1e-6
music = np.tile(loop, NS // NL + 2)[:NS] * 0.55
music *= music_gain

def whoosh(d=0.55, up=True):
    x = rng.standard_normal(int(d * SR)).astype(np.float32); out = np.zeros_like(x); y = 0.0
    for i in range(len(x)):
        p = i / len(x); fc = 300 + 5000 * (p if up else 1 - p); al = 1 - math.exp(-2 * math.pi * fc / SR); y += al * (x[i] - y); out[i] = y
    return out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2 * 0.9
WH = whoosh(0.45); WHD = whoosh(0.55, up=False)
def pop():
    t_ = tt(0.09); f = 900 * np.exp(-t_ * 25) + 350
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 45) * 0.6).astype(np.float32)
def boom():
    t_ = tt(0.8); f = 90 * np.exp(-t_ * 4) + 40
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 5); s[:300] += rng.standard_normal(300) * np.linspace(0.5, 0, 300)
    return (s * 0.9).astype(np.float32)
def ding():
    t_ = tt(0.9); return ((np.sin(2 * np.pi * 1320 * t_) + 0.4 * np.sin(2 * np.pi * 2640 * t_)) * np.exp(-t_ * 5) * 0.25).astype(np.float32)
def riser(d=1.0):
    t_ = tt(d); f = 200 + 1200 * (t_ / d) ** 2
    return ((np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + rng.standard_normal(len(t_)) * 0.08) * (t_ / d) ** 2).astype(np.float32)
def swoop(d=0.8):
    t_ = tt(d); f = 600 * np.exp(-t_ * 3.5) + 60
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 2.5) * 0.35
    m = min(len(s), len(WHD)); s[:m] += WHD[:m] * 0.4
    return s.astype(np.float32)
POP, BOOM, DING = pop(), boom(), ding()
sfx = np.zeros(NS, np.float32); cues = []
def cue(name, sig, at, g):
    if at is None: return
    o = int(at * SR)
    if o < 0: sig = sig[-o:]; o = 0
    m = min(len(sig), NS - o)
    if m > 0: sfx[o:o + m] += sig[:m] * g
    cues.append((round(at, 2), name))
for i in range(len(L.HOOK)):
    t0 = ITEM[f"hook{i}"][7] / FPS
    cue(f"whoosh (hook shot {i + 1})", WH, t0 - 0.12, 0.35)
    if L.HOOK[i][3] < 1: cue(f"slow-mo swoop (hook {i + 1})", swoop(0.6), t0, 0.4)
cue("riser (hook title)", riser(0.9), HOOK_TITLE_T - 0.9, 0.5); cue("boom (hook title)", BOOM, HOOK_TITLE_T, 0.8)
for key, clip, a, b, r, kind, z, f0, n in TL:
    if kind == "hook": continue
    t0 = f0 / FPS
    if kind == "replay": cue(f"slow-mo swoop ({key})", swoop(0.8), t0, 0.5)
    else: cue(f"whoosh ({key})", WH, t0 - 0.12, 0.35)
for k in ("a1_kotak", "a1_pasir", "a1_objek", "h_pasir", "h_objek", "h_kotak"): cue(f"pop ({k})", POP, E[k], 0.8)
cue("boom (pemanasan title)", BOOM, E["pem_title"] + 0.1, 0.6)
cue("whoosh (kenapa)", WH, E["why"] - 0.1, 0.3)
for k in ("why_otot", "why_cedera"): cue(f"ding ({k})", DING, E[k], 0.5)
for sk, num, txt, dur in L.SEC_BANNERS: cue(f"whoosh + boom (banner {num})", WH, E[sk] - 0.1, 0.4); cue(f"boom (banner {num})", BOOM, E[sk] + 0.2, 0.45)
for k in ("c1", "c2", "c3", "c4"): cue(f"pop ({k})", POP, E[k], 0.7)
for k in ("c1_dose", "c2_dose", "c3_dose", "c4_dose", "c4_int"): cue(f"ding ({k})", DING, E[k], 0.4)
for o0, o1, frs, lab in PIPF: cue(f"whoosh (PiP {lab})", WH, o0 - 0.1, 0.22)
cue("whoosh (recap)", WHD, RECAP_T0 - 0.1, 0.4)
for r in range(len(L.RECAP)): cue(f"pop (recap row {r + 1})", POP, RECAP_T0 + 0.5 + 0.35 * r, 0.6)
cue("whoosh (end card)", WH, END_T0 - 0.1, 0.4); cue("boom (end card)", BOOM, END_T0 + 0.2, 0.6)

def wr(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    ww = wave.open(path, "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR)
    ww.writeframes((x * 32767).astype(np.int16).tobytes()); ww.close()
wr(os.path.join(OUT, "voice.wav"), voice); wr(os.path.join(OUT, "amb.wav"), amb)
wr(os.path.join(OUT, "sfx.wav"), sfx); wr(os.path.join(OUT, "music.wav"), music)
name = "FINAL_ADEGAN4.mp4" if FINAL else "PREVIEW_ADEGAN4.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", os.path.join(OUT, "voice.wav"), "-i", os.path.join(OUT, "amb.wav"),
                "-i", os.path.join(OUT, "sfx.wav"), "-i", os.path.join(OUT, "music.wav"), "-filter_complex",
                "[1]highpass=f=90,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                "loudnorm=I=-16:TP=-1.5:LRA=9[v];[2]highpass=f=120[am];[v][am][3][4]amix=inputs=4:normalize=0:duration=longest,"
                "alimiter=limit=0.95,apad[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{DUR:.3f}",
                os.path.join(OUT, name)], check=True)
json.dump({"duration": DUR, "hook_end": HOOK_END, "items": {x[0]: [round(x[7] / FPS, 2), round((x[7] + x[8]) / FPS, 2)] for x in TL},
           "recap": RECAP_T0, "end": END_T0, "events": {k: round(v, 2) for k, v in E.items()}, "sfx": cues},
          open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, name), f"{DUR:.2f}s")
