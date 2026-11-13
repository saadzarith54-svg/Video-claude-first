"""Render ADEGAN 2 preview.
usage: python3 render2.py TALK.mp4 JUMP.mp4 JUMP120.mp4 TALK_TRANSCRIPT.json TALK16k.wav OUTDIR [--final]
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import edl2 as L
from track import pos as runner_pos
import longjump

TALK, JUMP, JUMP120, TRANSCRIPT, TALK16, OUT = sys.argv[1:7]
FINAL = "--final" in sys.argv
W, H, FPS, SR = 1280, 720, 30, 48000
os.makedirs(OUT, exist_ok=True)

TEAL = (16, 143, 132); TEAL_D = (8, 70, 66); YEL = (255, 210, 63); WHITE = (255, 255, 255)
RED = (220, 60, 50); INK = (20, 20, 20)
F_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
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

# ------------------------------------------------------------------ talk regions (pause tightening)
wf = wave.open(TALK16); a16 = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
hop = 800
db = np.array([20 * np.log10(np.sqrt(np.mean(a16[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(a16) - hop, hop)])
thr = np.percentile(db, 20) + 5
low = db < thr
gaps, i = [], 0
while i < len(low):
    if low[i]:
        j = i
        while j < len(low) and low[j]: j += 1
        if (j - i) * 0.05 >= L.GAP_MIN: gaps.append((i * 0.05, j * 0.05))
        i = j
    else: i += 1
regions, cur = [], L.TALK_IN
pad = L.GAP_KEEP / 2
for g0, g1 in gaps:
    if g1 <= L.TALK_IN or g0 >= L.TALK_OUT: continue
    a, b = max(cur, L.TALK_IN), min(g0 + pad, L.TALK_OUT)
    if b - a > 0.15: regions.append((a, b))
    cur = g1 - pad
if L.TALK_OUT - cur > 0.15: regions.append((cur, L.TALK_OUT))
for c0, c1 in L.CUTS:
    nr = []
    for a, b in regions:
        if c1 <= a or c0 >= b: nr.append((a, b)); continue
        if c0 - a > 0.15: nr.append((a, c0))
        if b - c1 > 0.15: nr.append((c1, b))
    regions = nr
regions.append(L.TAIL)

# ------------------------------------------------------------------ jump programs -> frame lists
def program_frames(prog):
    """list of (kind, jump_t, zoom, local_freeze_time) for each output frame."""
    out = []
    for p in prog:
        if p[0] == "play":
            _, a, b, rate, z = p
            n = int(round((b - a) / rate * FPS))
            out += [("play", a + k * rate / FPS, z, 0.0) for k in range(n)]
        else:
            _, t, d, z = p
            n = int(round(d * FPS))
            out += [("freeze", t, z, k / FPS) for k in range(n)]
    return out

HOOK_F = program_frames(L.HOOK)
HOOK_N = len(HOOK_F)
HOOK_DUR = HOOK_N / FPS

seg_frames, t = [], HOOK_N
for (a, b) in regions:
    n = int(round((b - a) * FPS)); seg_frames.append((t, n)); t += n
TALK_END_F = t
END_N = int(round(L.END_HOLD * FPS))
TOTAL = t + END_N
DUR = TOTAL / FPS
END_T0 = TALK_END_F / FPS

def s2o(ts):
    """talk source time -> output seconds (times inside a removed pause snap to the next region)."""
    for (a, b), (f0, n) in zip(regions, seg_frames):
        if ts < a: return f0 / FPS
        if ts <= b: return f0 / FPS + (ts - a)
    return END_T0

E = {k: s2o(v) for k, v in L.EV.items()}
SPEECH_END = s2o(L.TALK_OUT)
CARD_T0 = END_T0 - L.CARD_LEAD
BR = []
for key, at, prog in L.BROLL:
    fr = program_frames(prog)
    o0 = int(round(s2o(at) * FPS))
    BR.append((key, o0, o0 + len(fr), fr))
BRD = {k: (o0 / FPS, o1 / FPS) for k, o0, o1, _ in BR}

# ------------------------------------------------------------------ captions
words = []
for s in json.load(open(TRANSCRIPT)):
    for w in s["words"]:
        if L.DROP_WORDS[0] <= w["s"] <= L.DROP_WORDS[1]: continue
        words.append((w["w"].strip(), w["s"], w["e"]))
words += L.INSERT_WORDS
words.sort(key=lambda x: x[1])
fixed = []
for txt, s, e in words:
    bare = txt.strip(",.?!")
    if bare in L.CORRECTIONS: txt = txt.replace(bare, L.CORRECTIONS[bare])
    fixed.append((txt, s, e))
chunks = []
for (a, b), (f0, n) in zip(regions, seg_frames):
    pass
ws = []
for txt, s, e in fixed:
    best = None
    for (a, b), (f0, n) in zip(regions, seg_frames):
        ov = min(e, b) - max(s, a)
        if ov > 0.06 and s < b - 0.1:
            s2, e2 = max(s, a), min(e, b)
            if e2 - s2 > 0.7: s2 = e2 - 0.55
            best = (txt, f0 / FPS + s2 - a, f0 / FPS + e2 - a); break
    if best: ws.append(best)
cur = []
for w in ws:
    if cur and w[1] - cur[-1][2] > 0.6:
        chunks.append(cur); cur = []
    cur.append(w)
    if len(cur) >= 4 or w[0][-1] in ",.?!":
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
cap = []
for ci, c in enumerate(chunks):
    st, en = c[0][1], c[-1][2] + 0.25
    if ci + 1 < len(chunks) and chunks[ci + 1][0][1] > st: en = min(en, chunks[ci + 1][0][1])
    cap.append((st, en, c))

# ------------------------------------------------------------------ drawing
def rrect(d, box, r, fill): d.rounded_rectangle(box, r, fill=fill)

def caption(d, t):
    for st, en, c in cap:
        if st <= t < en:
            f = font(F_XB, 44); sp = f.getlength(" ")
            total = sum(f.getlength(x[0]) for x in c) + sp * (len(c) - 1)
            x = (W - total) / 2; y = 610 + (1 - eob((t - st) / 0.18)) * 14
            for wt, s, e in c:
                d.text((x, y), wt, font=f, fill=(YEL if s <= t < e + 0.05 else WHITE) + (255,),
                       stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += f.getlength(wt) + sp
            return

def lower_third(d, t, t_in, t_out, name, tag):
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); fN, fT = font(F_XB, 38), font(F_B, 20)
    wN = tw(name, fN) + 48; x0 = -wN + (wN + 40) * eo(p); y0 = 430
    wT = tw(tag, fT) + 28
    rrect(d, (x0, y0, x0 + wT, y0 + 34), 8, YEL + (a,)); d.text((x0 + 14, y0 + 5), tag, font=fT, fill=INK + (a,))
    rrect(d, (x0, y0 + 40, x0 + wN, y0 + 102), 10, TEAL + (int(235 * q),))
    d.rectangle((x0, y0 + 40, x0 + 8, y0 + 102), fill=YEL + (a,))
    d.text((x0 + 26, y0 + 49), name, font=fN, fill=WHITE + (a,))

PHASES = [("Larian landas", 0.75), ("Lompatan", 1.30), ("Layangan", 1.62), ("Pendaratan", 2.6)]

def fasa_panel(d, t):
    p, q = inout(t, E["fasa_header"], E["fasa_out"], 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 430; x0 = 36 - (1 - eo(p)) * (pw + 60); y0 = 60
    fH, fN, fT = font(F_XB, 28), font(F_XB, 30), font(F_XB, 26)
    rrect(d, (x0, y0, x0 + pw, y0 + 54), 12, YEL + (a,))
    d.text((x0 + 20, y0 + 11), "4 FASA LOMPAT JAUH", font=fH, fill=INK + (a,))
    y = y0 + 68
    times = [E["fasa_1"], E["fasa_2"], E["fasa_3"], E["fasa_4"]]
    shown = [ti for ti in times if t >= ti]
    for k, ((name, lt), ti) in enumerate(zip(PHASES, times)):
        if t < ti: continue
        pi = eob((t - ti) / 0.35); aa = int(a * clamp(pi))
        active = (k == len(shown) - 1); h = 100
        rrect(d, (x0, y, x0 + pw, y + h), 12, (TEAL if active else TEAL_D) + (int(235 * q * clamp(pi)),))
        # mini scene of that phase
        rrect(d, (x0 + 10, y + 10, x0 + 190, y + h - 10), 8, (10, 30, 34, aa))
        longjump.draw_longjump(d, lt, (x0 + 12, y + 12, 176, h - 24), aa, None)
        d.ellipse((x0 + 202, y + h / 2 - 20, x0 + 242, y + h / 2 + 20), fill=YEL + (aa,))
        num = str(k + 1); d.text((x0 + 222 - tw(num, fN) / 2, y + h / 2 - 19), num, font=fN, fill=INK + (aa,))
        d.text((x0 + 254, y + h / 2 - 16), name, font=fT, fill=WHITE + (aa,))
        y += h + 10

PHASE_TAGS = [("p1", "b1_run", 0), ("p2", "b2_takeoff", 1), ("p3", "b3_flight", 2), ("p4", None, 3)]

def phase_tag(d, t):
    starts = [E["p1"], E["p2"], E["p3"], E["p4"]]
    ends = [E["p2"] - 0.05, E["p3"] - 0.05, E["p4"] - 0.05, E["phase_out"]]
    for k in range(4):
        p, q = inout(t, starts[k], ends[k], 0.35, 0.25)
        if q <= 0: continue
        a = int(255 * q)
        name = PHASES[k][0].upper()
        if k == 2: name = "LAYANGAN (PENERBANGAN)"
        f1, f2 = font(F_XB, 20), font(F_XB, 34)
        x = 36 - (1 - eo(p)) * 600; y = 36
        lab = f"FASA {k + 1}/4"
        rrect(d, (x, y, x + tw(lab, f1) + 28, y + 34), 8, YEL + (a,)); d.text((x + 14, y + 6), lab, font=f1, fill=INK + (a,))
        rrect(d, (x, y + 40, x + tw(name, f2) + 40, y + 96), 10, RED + (int(235 * q),))
        d.text((x + 20, y + 47), name, font=f2, fill=WHITE + (a,))
        for j in range(4):  # progress pills
            px = x + j * 46
            d.rounded_rectangle((px, y + 106, px + 38, y + 114), 4,
                                fill=(YEL if j <= k else (255, 255, 255)) + (a if j <= k else int(a * 0.4),))

def chip(d, t, t_in, t_out, txt, x, y, col=TEAL):
    p, q = inout(t, t_in, t_out, 0.3, 0.25)
    if q <= 0: return
    a = int(255 * q * clamp(p * 2)); sc = eob(p); f = font(F_XB, 28)
    w = (tw(txt, f) + 36) * sc
    rrect(d, (x, y, x + w, y + 50), 25, col + (a,))
    if sc > 0.9: d.text((x + 18, y + 9), txt, font=f, fill=WHITE + (a,))

def arrow(d, p0, p1, col, width, a, prog=1.0):
    x0, y0 = p0; x1 = x0 + (p1[0] - x0) * prog; y1 = y0 + (p1[1] - y0) * prog
    d.line([(x0, y0), (x1, y1)], fill=col + (a,), width=width)
    ang = math.atan2(y1 - y0, x1 - x0); hs = width * 2.6
    pts = [(x1 + math.cos(ang) * hs * 0.6, y1 + math.sin(ang) * hs * 0.6),
           (x1 + math.cos(ang + 2.5) * hs, y1 + math.sin(ang + 2.5) * hs),
           (x1 + math.cos(ang - 2.5) * hs, y1 + math.sin(ang - 2.5) * hs)]
    d.polygon(pts, fill=col + (a,))

def label(d, xy, txt, a, size=26, col=YEL):
    f = font(F_XB, size)
    d.text(xy, txt, font=f, fill=col + (a,), stroke_width=4, stroke_fill=(0, 0, 0, a))

def broll_graphics(d, key, fr_kind, ft, t):
    """graphics drawn on top of B-roll freezes (coords in output frame, runner near centre)."""
    if key == "b2_takeoff" and fr_kind == "freeze":
        a = 255
        arrow(d, (330, 470), (600, 470), YEL, 10, a, eo(ft / 0.4));
        if ft > 0.2: label(d, (330, 418), "KELAJUAN", a)
        if ft > 0.8:
            arrow(d, (690, 640), (690, 420), WHITE, 10, a, eo((ft - 0.8) / 0.4))
            label(d, (712, 560), "DAYA TOLAKAN", a, col=WHITE)
        if ft > 1.6:
            arrow(d, (640, 470), (930, 250), RED, 12, a, eo((ft - 1.6) / 0.5))
            if ft > 2.0: label(d, (880, 200), "KE HADAPAN + ATAS", a, col=WHITE)
    if key == "b4_landing" and fr_kind == "freeze":
        a = 255
        arrow(d, (560, 470), (840, 500), YEL, 10, a, eo(ft / 0.45))
        if ft > 0.35: label(d, (600, 520), "KAKI KE HADAPAN", a)

def needs_panel(d, t):
    p, q = inout(t, E["need_header"], SPEECH_END + 0.2, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 430; x0 = 36 - (1 - eo(p)) * (pw + 60); y0 = 60
    fH, fN, fT, fS = font(F_XB, 28), font(F_XB, 28), font(F_B, 27), font(F_SB, 21)
    rrect(d, (x0, y0, x0 + pw, y0 + 54), 12, YEL + (a,))
    d.text((x0 + 20, y0 + 11), "5 KEPERLUAN FIZIKAL", font=fH, fill=INK + (a,))
    items = [("need_1", "Kelajuan"), ("need_2", "Kuasa letusan kaki"), ("need_3", "Kekuatan kaki"),
             ("need_4", "Koordinasi"), ("need_5", "Keseimbangan")]
    shown = [k for k, _ in items if t >= E[k]]
    y = y0 + 66
    for k, (key, name) in enumerate(items):
        ti = E[key]
        if t < ti: continue
        pi = eob((t - ti) / 0.35); aa = int(a * clamp(pi))
        sub = (k == 4 and t >= E["need_5b"])
        h = 90 if sub else 62
        active = (k == len(shown) - 1) and t < E["closing_chip"]
        rrect(d, (x0, y, x0 + pw, y + h), 12, (TEAL if active else TEAL_D) + (int(235 * q * clamp(pi)),))
        d.ellipse((x0 + 12, y + 11, x0 + 52, y + 51), fill=YEL + (aa,))
        num = str(k + 1); d.text((x0 + 32 - tw(num, fN) / 2, y + 13), num, font=fN, fill=INK + (aa,))
        d.text((x0 + 66, y + 14), name, font=fT, fill=WHITE + (aa,))
        if sub:
            sa = int(aa * clamp((t - E["need_5b"]) / 0.3))
            d.text((x0 + 66, y + 54), "& kelenturan pinggul", font=fS, fill=YEL + (sa,))
        y += h + 8

def hook_title(d, t):
    # appears at the freeze in the hook, stays to the end of the hook
    t_in = sum(1 for f in HOOK_F if f[0] == "play" and f[1] < 3.85) / FPS
    p, q = inout(t, t_in, HOOK_DUR, 0.4, 0.2)
    if q <= 0: return
    a = int(255 * q)
    f1, f3 = font(F_XB, 30), font(F_XB, 46)
    l1 = "ANALISIS"
    w1 = tw(l1, f1) + 36
    rrect(d, ((W - w1) / 2, 150, (W + w1) / 2, 198), 10, YEL + (a,))
    d.text(((W - tw(l1, f1)) / 2, 157), l1, font=f1, fill=INK + (a,))
    sc = clamp(eob(p), 0, 1.3)
    f2 = font(F_XB, max(8, int(150 * sc)))
    txt = "4 FASA"
    d.text(((W - tw(txt, f2)) / 2, 300 - 75 * sc), txt, font=f2, fill=WHITE + (a,), stroke_width=8, stroke_fill=(0, 0, 0, a))
    if p > 0.5:
        l3 = "LOMPAT JAUH"; d.text(((W - tw(l3, f3)) / 2, 400), l3, font=f3, fill=YEL + (a,), stroke_width=5, stroke_fill=(0, 0, 0, a))

def slowmo_badge(d, t, on):
    if not on: return
    f = font(F_XB, 22); txt = "SLOW-MO"
    rrect(d, (W - 170, 60, W - 36, 96), 8, (0, 0, 0, 150))
    d.ellipse((W - 160, 71, W - 146, 85), fill=RED + (255,))
    d.text((W - 138, 66), txt, font=f, fill=WHITE + (255,))

def end_card(d, t):
    lt = t - CARD_T0
    if lt < 0: return
    p = eob(lt / 0.45)
    f1, f2 = font(F_XB, 32), font(F_XB, 80)
    l1 = "SETERUSNYA"; w1 = tw(l1, f1) + 36
    y = 70 + (1 - p) * 40
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 50), 10, YEL + (255,))
    d.text(((W - tw(l1, f1)) / 2, y + 7), l1, font=f1, fill=INK + (255,))
    if lt > 0.15:
        sc = clamp(eob((lt - 0.15) / 0.4), 0, 1.2); f = font(F_XB, max(8, int(80 * sc)))
        l2 = "LATIHAN →"; d.text(((W - tw(l2, f)) / 2, y + 110 - 40 * sc), l2, font=f, fill=WHITE + (255,),
                                 stroke_width=6, stroke_fill=(0, 0, 0, 255))

def overlays(t, broll_state=None):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if t < HOOK_DUR:
        hook_title(d, t)
    lower_third(d, t, E["lt_amsyar"], E["lt_out"], "Muhammad Amsyar Rasif", "PENGANALISIS")
    fasa_panel(d, t)
    phase_tag(d, t)
    chip(d, t, E["p1_chip"], E["p2"] - 0.05, "Laju, tapi terkawal", 36, 170)
    chip(d, t, E["p4_chip"], E["p4_safe"], "Badan seimbang", 36, 170)
    chip(d, t, E["p4_safe"], E["phase_out"], "Mendarat dengan selamat", 36, 170, RED)
    needs_panel(d, t)
    chip(d, t, E["closing_chip"], SPEECH_END + 0.2, "Setiap latihan = sekurang-kurangnya 1 keperluan", 490, 520, RED)
    if broll_state:
        key, kind, ft = broll_state
        broll_graphics(d, key, kind, ft, t)
    slowmo_badge(d, t, broll_state is not None and broll_state[1] in ("slow", "freeze") or
                 (t < HOOK_DUR and broll_state is None and False))
    end_card(d, t)
    if t < SPEECH_END + 0.3: caption(d, t)
    if not FINAL: d.text((W - 110, 14), "PREVIEW", font=font(F_B, 18), fill=(255, 255, 255, 140))
    return img

# ------------------------------------------------------------------ frame sources
def read_frames(src, a, n, fps_filter=None):
    vf = f"scale={W}:{H}" if fps_filter is None else f"fps={fps_filter},scale={W}:{H}"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(a, 0):.3f}", "-i", src, "-frames:v", str(n),
                          "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: buf = last
        last = buf
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.stdout.close(); p.wait()

_j120 = {}
def jump_frame(jt):
    """frame from 120fps interpolated clip, cached per index."""
    idx = int(round(jt * 120))
    if idx not in _j120:
        if len(_j120) > 400: _j120.clear()
        start = idx / 120
        for k, fr in enumerate(read_frames(JUMP120, start, 120)):
            _j120[idx + k] = fr
    return _j120[idx]

def crop(fr, cx, cy, z):
    if z <= 1.001: return Image.fromarray(fr)
    cw, ch = W / z, H / z
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    return Image.fromarray(fr).resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

def jump_image(kind, jt, z):
    x, y = runner_pos(jt)
    return crop(jump_frame(jt), x, y - 20, z)

# ------------------------------------------------------------------ render video
vid = os.path.join(OUT, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "18" if FINAL else "26", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
fi = 0
def emit(img_rgb, t, state):
    global fi
    base = img_rgb.convert("RGBA"); base.alpha_composite(overlays(t, state)); out = base.convert("RGB")
    for ft in FLASHES:
        dt = t - ft
        if -0.02 <= dt < 0.16: out = Image.blend(out, Image.new("RGB", (W, H), WHITE), 0.8 * (1 - clamp(dt / 0.16)))
    if t > DUR - 0.4: out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (DUR - 0.4)) / 0.4))
    enc.stdin.write(out.tobytes()); fi += 1

hook_freeze_t = None
for k, f in enumerate(HOOK_F):
    if f[0] == "freeze": hook_freeze_t = k / FPS; break
FLASHES = [hook_freeze_t, HOOK_DUR] + [o0 / FPS for _, o0, _, _ in BR]

# hook
for kind, jt, z, ft in HOOK_F:
    t = fi / FPS
    emit(jump_image(kind, jt, z), t, ("hook", "slow" if kind == "play" and jt >= 3.55 else kind, ft))
print("hook done", flush=True)

# talk with B-roll windows
br_at = {}
for key, o0, o1, fr in BR:
    for k in range(o1 - o0): br_at[o0 + k] = (key, fr[k])
for ri, ((a, b), (f0, n)) in enumerate(zip(regions, seg_frames)):
    z0 = 1.0 if (a, b) == L.TAIL else L.TALK_ZOOMS[ri % 2]
    for k, fr in enumerate(read_frames(TALK, a, n)):
        t = fi / FPS
        if fi in br_at:
            key, (kind, jt, z, ft) = br_at[fi]
            st = "freeze" if kind == "freeze" else ("slow" if True else "play")
            emit(jump_image(kind, jt, z), t, (key, st, ft))
        else:
            z = z0 + 0.02 * k / max(n - 1, 1)
            last = crop(fr, L.TALK_FOCUS[0], L.TALK_FOCUS[1], z)
            emit(last, t, None)
print(f"talk done ({len(regions)} cuts)", flush=True)
blur = last.filter(ImageFilter.GaussianBlur(14))
dark = Image.blend(blur, Image.new("RGB", (W, H), (8, 28, 30)), 0.6)
for k in range(END_N):
    t = fi / FPS; m = eo((t - END_T0) / 0.4)
    emit(Image.blend(last, dark, m), t, None)

enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio
def load(src, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-ac", "2", "-ar", str(SR), path], check=True)
    w = wave.open(path)
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
A = load(TALK, os.path.join(OUT, "talk48.wav"))
J = load(JUMP, os.path.join(OUT, "jump48.wav"))
NS = int(DUR * SR)
voice = np.zeros((NS + SR, 2), np.float32); amb = np.zeros((NS + SR, 2), np.float32)
fade = int(0.012 * SR)
for (a, b), (f0, n) in zip(regions, seg_frames):
    s0 = int(a * SR); Ln = int(n / FPS * SR); c = A[s0:s0 + Ln].copy()
    env = np.ones(len(c), np.float32); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
    o = int(f0 / FPS * SR); voice[o:o + len(c)] += c * env[:, None]
# natural jump ambience during the real-time part of the hook
p0 = L.HOOK[0]; s0 = int(p0[1] * SR); Ln = int((p0[2] - p0[1]) * SR)
c = J[s0:s0 + Ln].copy(); env = np.ones(len(c), np.float32); env[-int(0.3 * SR):] = np.linspace(1, 0, int(0.3 * SR))
amb[:len(c)] += c * env[:, None] * 0.6
voice, amb = voice[:NS], amb[:NS]

rng = np.random.default_rng(7)
def tt(d): return np.arange(int(d * SR)) / SR
def whoosh(d=0.55, up=True):
    x = rng.standard_normal(int(d * SR)).astype(np.float32); out = np.zeros_like(x); y = 0.0
    for i in range(len(x)):
        p = i / len(x); fc = 300 + 5000 * (p if up else 1 - p); al = 1 - math.exp(-2 * math.pi * fc / SR)
        y += al * (x[i] - y); out[i] = y
    return out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2 * 0.9
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
def slowdown(d=0.9):
    """'tape stop' swoop used when entering slow-mo"""
    t_ = tt(d); f = 600 * np.exp(-t_ * 3.5) + 60
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 2.5) * 0.35
    return (s + whoosh(d, up=False)[:len(s)] * 0.5).astype(np.float32)
def thud():
    b = boom()[:int(0.4 * SR)]; n = int(0.35 * SR); x = rng.standard_normal(n).astype(np.float32)
    sand = np.convolve(x, np.ones(6) / 6, mode="same") * np.exp(-np.arange(n) / SR * 9) * 0.5
    out = np.zeros(max(len(b), n), np.float32); out[:len(b)] += b; out[:n] += sand; return out
def tick():
    t_ = tt(0.05); return (np.sin(2 * np.pi * 2200 * t_) * np.exp(-t_ * 90) * 0.4).astype(np.float32)

sfx = np.zeros(NS, np.float32); cues = []
def cue(name, sig, at, g):
    if at is None: return
    o = int(at * SR)
    if o < 0: sig = sig[-o:]; o = 0
    m = min(len(sig), NS - o)
    if m > 0: sfx[o:o + m] += sig[:m] * g
    cues.append((round(at, 2), name))

def jt_out(frames, target, start_t, kind="play"):
    for k, f in enumerate(frames):
        if f[0] == kind and f[1] >= target: return start_t + k / FPS
    return None
# hook
cue("slow-mo swoop", slowdown(), jt_out(HOOK_F, 3.55, 0) - 0.05, 0.8)
cue("boom (4 FASA freeze)", boom(), hook_freeze_t, 0.9)
cue("thud + sand (landing)", thud(), jt_out(HOOK_F, 4.27, 0), 0.6)
cue("riser into talk", riser(0.8), HOOK_DUR - 0.8, 0.5)
cue("whoosh (cut to Amsyar)", whoosh(0.45), HOOK_DUR - 0.15, 0.4)
cue("whoosh (lower third)", whoosh(0.4), E["lt_amsyar"] - 0.1, 0.3)
cue("whoosh (4 fasa panel)", whoosh(0.5), E["fasa_header"] - 0.1, 0.35)
for k in ("fasa_1", "fasa_2", "fasa_3", "fasa_4"): cue(f"pop ({k})", pop(), E[k], 0.8)
for k in ("p1", "p2", "p3", "p4"): cue(f"whoosh ({k} tag)", whoosh(0.4), E[k] - 0.1, 0.3)
for key, o0, o1, fr in BR:
    t0 = o0 / FPS
    cue(f"whoosh in ({key})", whoosh(0.4), t0 - 0.15, 0.35)
    if any(f[0] == "play" and f[1] < 3.6 and key != "b1_run" for f in fr) or key != "b1_run":
        cue(f"slow-mo swoop ({key})", slowdown(0.7), t0, 0.5)
    fz = next((k for k, f in enumerate(fr) if f[0] == "freeze"), None)
    if fz is not None: cue(f"freeze hit ({key})", boom()[:int(0.5 * SR)], t0 + fz / FPS, 0.5)
    lt = jt_out(fr, 4.27, t0)
    if lt is not None and key in ("b3_flight", "b4_landing"): cue(f"thud ({key})", thud(), lt, 0.45)
fz2 = next(k for k, f in enumerate(BR[1][3]) if f[0] == "freeze") / FPS + BR[1][1] / FPS
for d_, nm in ((0.0, "KELAJUAN"), (0.8, "DAYA TOLAKAN"), (1.6, "KE HADAPAN")): cue(f"tick (arrow {nm})", tick(), fz2 + d_, 0.8)
cue("ding (laju tapi terkawal)", ding(), E["p1_chip"], 0.6)
cue("ding (badan seimbang)", ding(), E["p4_chip"], 0.6)
cue("ding (mendarat selamat)", ding(), E["p4_safe"], 0.6)
cue("whoosh (5 keperluan panel)", whoosh(0.5), E["need_header"] - 0.1, 0.35)
for k in ("need_1", "need_2", "need_3", "need_4", "need_5"): cue(f"pop ({k})", pop(), E[k], 0.8)
cue("ding (kelenturan pinggul)", ding(), E["need_5b"], 0.5)
cue("ding (closing chip)", ding(), E["closing_chip"], 0.6)
cue("whoosh (end card)", whoosh(0.5), CARD_T0 - 0.1, 0.4)
cue("boom (SETERUSNYA)", boom(), CARD_T0 + 0.2, 0.7)

def wr(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wr(os.path.join(OUT, "voice.wav"), voice); wr(os.path.join(OUT, "amb.wav"), amb); wr(os.path.join(OUT, "sfx.wav"), sfx)
name = "FINAL_ADEGAN2.mp4" if FINAL else "PREVIEW_ADEGAN2.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", os.path.join(OUT, "voice.wav"),
                "-i", os.path.join(OUT, "amb.wav"), "-i", os.path.join(OUT, "sfx.wav"), "-filter_complex",
                "[1]highpass=f=90,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                "loudnorm=I=-16:TP=-1.5:LRA=9[v];[v][2][3]amix=inputs=3:normalize=0:duration=longest,apad[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{DUR:.3f}",
                os.path.join(OUT, name)], check=True)
json.dump({"duration": DUR, "hook": HOOK_DUR, "regions": regions, "broll": {k: v for k, v in BRD.items()},
           "events": {k: round(v, 2) for k, v in E.items()}, "sfx": cues}, open(os.path.join(OUT, "timeline.json"), "w"),
          indent=1)
print("wrote", os.path.join(OUT, name), f"{DUR:.2f}s")
