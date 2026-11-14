"""Render ADEGAN 3 preview.
usage: python3 render3.py SRC.mp4 TRANSCRIPT.json SRC16k.wav OUTDIR [--final]
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import edl3 as L

SRC, TRANSCRIPT, SRC16, OUT = sys.argv[1:5]
FINAL = "--final" in sys.argv
W, H, FPS, SR = 1280, 720, 30, 48000
os.makedirs(OUT, exist_ok=True)

TEAL = (16, 143, 132); TEAL_D = (8, 70, 66); YEL = (255, 210, 63); WHITE = (255, 255, 255)
RED = (220, 60, 50); INK = (20, 20, 20); PANEL = (10, 30, 34)
F_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
if not os.path.exists(F_M): F_M = F_SB
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

# ------------------------------------------------------------------ regions
wf = wave.open(SRC16); a16 = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
hop = 800
db = np.array([20 * np.log10(np.sqrt(np.mean(a16[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(a16) - hop, hop)])
thr = np.percentile(db, 20) + 5
low = db < thr; GAPS = []; i = 0
while i < len(low):
    if low[i]:
        j = i
        while j < len(low) and low[j]: j += 1
        if (j - i) * 0.05 >= L.GAP_MIN: GAPS.append((i * 0.05, j * 0.05))
        i = j
    else: i += 1

def make_regions(a0, b0):
    regs, cur, pad = [], a0, L.GAP_KEEP / 2
    for g0, g1 in GAPS:
        if g1 <= a0 or g0 >= b0: continue
        a, b = max(cur, a0), min(g0 + pad, b0)
        if b - a > 0.15: regs.append((a, b))
        cur = max(g1 - pad, a0)
    if b0 - cur > 0.15: regs.append((cur, b0))
    for c0, c1 in L.CUTS:
        nr = []
        for a, b in regs:
            if c1 <= a or c0 >= b: nr.append((a, b)); continue
            if c0 - a > 0.15: nr.append((a, c0))
            if b - c1 > 0.15: nr.append((c1, b))
        regs = nr
    return regs

HOOK_REGS = make_regions(*L.HOOK_RANGE) if L.HOOK_RANGE else []
BODY_REGS = [r for rng in L.BODY_RANGES for r in make_regions(*rng)]
# segment list: (src_a, src_b, rate, kind)
SEGS = [(a, b, 1.0, "hook") for a, b in HOOK_REGS] + [(a, b, 1.0, "body") for a, b in BODY_REGS] + \
       [(L.TAIL[0], L.TAIL[1], L.TAIL[2], "tail")]
seg_f, t = [], 0
for a, b, r, k in SEGS:
    n = int(round((b - a) / r * FPS)); seg_f.append((t, n)); t += n
HOOK_END = (seg_f[len(HOOK_REGS) - 1][0] + seg_f[len(HOOK_REGS) - 1][1]) / FPS if HOOK_REGS else 0.0
TAIL_T0 = seg_f[-1][0] / FPS
TALK_END_F = t
END_N = int(round(L.END_HOLD * FPS))
TOTAL = t + END_N; DUR = TOTAL / FPS; END_T0 = TALK_END_F / FPS
CARD_T0 = END_T0 - L.CARD_LEAD

def s2o(ts):
    best = None
    for (a, b, r, k), (f0, n) in zip(SEGS, seg_f):
        if a <= ts <= b: return f0 / FPS + (ts - a) / r
        if ts < a and (best is None):
            best = f0 / FPS
    return best
E = {k: s2o(v) for k, v in L.EV.items()}
missing = [k for k, v in E.items() if v is None]
if missing: print("WARN events outside kept ranges:", missing)

# ------------------------------------------------------------------ captions
words = []
for s in json.load(open(TRANSCRIPT)):
    for w in s["words"]:
        if any(d0 <= w["s"] <= d1 for d0, d1 in L.DROP): continue
        words.append((w["w"].strip(), w["s"], w["e"]))
words += L.INSERT; words.sort(key=lambda x: x[1])
ws = []
for txt, s, e in words:
    bare = txt.strip(",.?!")
    if bare in L.CORRECTIONS: txt = txt.replace(bare, L.CORRECTIONS[bare])
    for (a, b, r, k), (f0, n) in zip(SEGS, seg_f):
        if k == "tail": continue
        ov = min(e, b) - max(s, a)
        if ov > 0.06 and s < b - 0.1:
            s2, e2 = max(s, a), min(e, b)
            if e2 - s2 > 0.7: s2 = e2 - 0.55
            ws.append((txt, f0 / FPS + s2 - a, f0 / FPS + e2 - a)); break
chunks, cur = [], []
for w in ws:
    if cur and (w[1] - cur[-1][2] > 0.6 or (cur[-1][2] <= HOOK_END < w[1] + 0.01 and cur[-1][2] <= HOOK_END)):
        chunks.append(cur); cur = []
    cur.append(w)
    if len(cur) >= 4 or w[0][-1] in ",.?!": chunks.append(cur); cur = []
if cur: chunks.append(cur)
cap = []
for ci, c in enumerate(chunks):
    st, en = c[0][1], c[-1][2] + 0.25
    if ci + 1 < len(chunks) and chunks[ci + 1][0][1] > st: en = min(en, chunks[ci + 1][0][1])
    cap.append((st, en, c))

def caption(d, t, y=610):
    for st, en, c in cap:
        if st <= t < en:
            f = font(F_XB, 44); sp = f.getlength(" ")
            total = sum(f.getlength(x[0]) for x in c) + sp * (len(c) - 1)
            x = (W - total) / 2; yy = y + (1 - eob((t - st) / 0.18)) * 14
            for wt, s, e in c:
                d.text((x, yy), wt, font=f, fill=(YEL if s <= t < e + 0.05 else WHITE) + (255,),
                       stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += f.getlength(wt) + sp
            return

def wrap(txt, f, width):
    lines, cur = [], ""
    toks = []
    for wd in txt.split():
        parts = wd.replace("–", "–\x00").split("\x00")
        toks += [(pt, k > 0) for k, pt in enumerate(parts) if pt]
    for wd, glued in toks:
        test = (cur + ("" if glued else " ") + wd).strip()
        if tw(test, f) <= width or not cur: cur = test
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

# ------------------------------------------------------------------ graphics
def lower_third(d, t, t_in, t_out, name, tag):
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); fN, fT = font(F_XB, 36), font(F_B, 19)
    wN = tw(name, fN) + 48; x0 = -wN + (wN + 40) * eo(p); y0 = 440
    wT = tw(tag, fT) + 28
    rrect(d, (x0, y0, x0 + wT, y0 + 32), 8, YEL + (a,)); d.text((x0 + 14, y0 + 5), tag, font=fT, fill=INK + (a,))
    rrect(d, (x0, y0 + 38, x0 + wN, y0 + 98), 10, TEAL + (int(235 * q),))
    d.rectangle((x0, y0 + 38, x0 + 8, y0 + 98), fill=YEL + (a,))
    d.text((x0 + 26, y0 + 47), name, font=fN, fill=WHITE + (a,))

def check(d, x, y, s, col):
    d.line([(x, y + s * 0.5), (x + s * 0.38, y + s * 0.85), (x + s, y + s * 0.1)], fill=col, width=max(3, int(s * 0.18)), joint="curve")

# --- equipment icons (hook)
def icon(d, kind, cx, cy, s, a):
    if kind == "kon":
        d.polygon([(cx, cy - s * 0.45), (cx - s * 0.3, cy + s * 0.35), (cx + s * 0.3, cy + s * 0.35)], fill=(245, 120, 30, a))
        d.polygon([(cx - s * 0.13, cy - s * 0.08), (cx + s * 0.13, cy - s * 0.08), (cx + s * 0.18, cy + s * 0.08), (cx - s * 0.18, cy + s * 0.08)], fill=WHITE + (a,))
        d.rectangle((cx - s * 0.42, cy + s * 0.35, cx + s * 0.42, cy + s * 0.43), fill=(245, 120, 30, a))
    elif kind == "kotak":
        d.polygon([(cx - s * 0.4, cy - s * 0.05), (cx - s * 0.2, cy - s * 0.25), (cx + s * 0.45, cy - s * 0.25), (cx + s * 0.25, cy - s * 0.05)], fill=(200, 150, 90, a))
        d.rectangle((cx - s * 0.4, cy - s * 0.05, cx + s * 0.25, cy + s * 0.35), fill=(160, 110, 60, a))
        d.polygon([(cx + s * 0.25, cy - s * 0.05), (cx + s * 0.45, cy - s * 0.25), (cx + s * 0.45, cy + s * 0.15), (cx + s * 0.25, cy + s * 0.35)], fill=(120, 80, 45, a))
    elif kind == "tali":
        for x in (cx - s * 0.38, cx + s * 0.38):
            d.rectangle((x - s * 0.04, cy - s * 0.35, x + s * 0.04, cy + s * 0.4), fill=(230, 230, 230, a))
        d.line([(cx - s * 0.38, cy - s * 0.05), (cx, cy + s * 0.02), (cx + s * 0.38, cy - s * 0.05)], fill=RED + (a,), width=max(3, int(s * 0.06)), joint="curve")
    elif kind == "pasir":
        d.rounded_rectangle((cx - s * 0.45, cy - s * 0.12, cx + s * 0.45, cy + s * 0.32), int(s * 0.08), fill=(233, 200, 140, a))
        rng = np.random.default_rng(1)
        for _ in range(18):
            px, py = rng.uniform(-0.4, 0.4) * s + cx, rng.uniform(-0.05, 0.28) * s + cy
            d.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(190, 150, 90, a))

EQ_OUT = (HOOK_END + 0.2) if HOOK_REGS else (E["eq_pasir"] + 2.2)
def hook_gfx(d, t):
    if t > EQ_OUT: return
    p, q = inout(t, E["hook_title"], EQ_OUT, 0.4, 0.25)
    if q > 0:
        a = int(255 * q)
        f1, f2 = font(F_XB, 30), font(F_XB, 64)
        l1 = "5 LATIHAN"; w1 = tw(l1, f1) + 36
        rrect(d, ((W - w1) / 2, 34, (W + w1) / 2, 80), 10, YEL + (a,))
        d.text(((W - tw(l1, f1)) / 2, 40), l1, font=f1, fill=INK + (a,))
        sc = clamp(eob(p), 0, 1.2); f = font(F_XB, max(8, int(64 * sc)))
        l2 = "TANPA PERALATAN MAHAL"
        d.text(((W - tw(l2, f)) / 2, 128 - 32 * sc), l2, font=f, fill=WHITE + (a,), stroke_width=6, stroke_fill=(0, 0, 0, a))
    items = [("kon", "Kon", E["eq_kon"]), ("kotak", "Kotak rendah", E["eq_kotak"]),
             ("tali", "Tali getah", E["eq_tali"]), ("pasir", "Kotak pasir", E["eq_pasir"])]
    cw, gap = 200, 22; x = (W - (4 * cw + 3 * gap)) / 2
    for k, (kind, lab, ti) in enumerate(items):
        if ti is None or t < ti: x += cw + gap; continue
        pi = eob((t - ti) / 0.35); sc = 0.6 + 0.4 * clamp(pi, 0, 1.1)
        aa = int(255 * q * clamp((t - ti) / 0.15))
        y0 = 418
        bx0, bx1 = x + cw / 2 - cw / 2 * sc, x + cw / 2 + cw / 2 * sc
        rrect(d, (bx0, y0 + (1 - sc) * 90, bx1, y0 + 180 - (1 - sc) * 90), 18, PANEL + (int(aa * 0.9),))
        icon(d, kind, x + cw / 2, y0 + 70, 120 * sc, aa)
        f = font(F_XB, 24); d.text((x + cw / 2 - tw(lab, f) / 2, y0 + 136), lab, font=f, fill=WHITE + (aa,))
        x += cw + gap

PRINSIP = [("Boleh dilaksanakan", "pr_laksana"), ("Sistematik", "pr_sistematik"), ("Sesuai tahap", "pr_tahap"), ("Selamat", "pr_selamat")]
def prinsip(d, t):
    hide = (E["week"] - 0.2 <= t <= E["table_out"] + 0.2) or (E["hook_title"] - 0.2 <= t <= EQ_OUT + 0.1) or t < E["prinsip"] or t > E["safe_out"] + 0.2
    if hide: return
    p = eo((t - E["prinsip"]) / 0.45); a = 255
    x0 = W - 436 + (1 - p) * 470; y0 = 22
    fH, fI = font(F_XB, 19), font(F_B, 17)
    rrect(d, (x0, y0, x0 + 410, y0 + 32), 8, YEL + (a,)); d.text((x0 + 12, y0 + 6), "PRINSIP REKA BENTUK", font=fH, fill=INK + (a,))
    for k, (lab, key) in enumerate(PRINSIP):
        cx = x0 + (k % 2) * 206; cy = y0 + 40 + (k // 2) * 42
        on = t >= E[key]; flash = clamp(1 - (t - E[key]) / 0.6) if on else 0
        rrect(d, (cx, cy, cx + 202, cy + 36), 18, ((TEAL if on else PANEL) + (230,)))
        if flash > 0: rrect(d, (cx - 3, cy - 3, cx + 205, cy + 39), 20, None, YEL + (int(255 * flash),), 3)
        if on: check(d, cx + 10, cy + 9, 18, YEL + (255,))
        d.text((cx + (32 if on else 14), cy + 8), lab, font=fI, fill=(WHITE if on else (170, 190, 190)) + (255,))

def five_strip(d, t):
    p, q = inout(t, E["five"], E["five_out"] + 0.6, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); cw, gap = 222, 22; x = (W - (5 * cw + 4 * gap)) / 2; y0 = 418
    fN, fT, fS = font(F_XB, 22), font(F_XB, 21), font(F_SB, 16)
    for k, (name, jenis) in enumerate(L.EXERCISES):
        ti = E["five"] + 0.18 * k
        pi = eob((t - ti) / 0.35)
        if pi <= 0: x += cw + gap; continue
        aa = int(a * clamp(pi)); yy = y0 + (1 - clamp(pi, 0, 1)) * 30
        hl = (k == 0 and E["five_1"] <= t < E["five_5"]) or (k == 4 and t >= E["five_5"])
        rrect(d, (x, yy, x + cw, yy + 150), 14, ((TEAL if hl else PANEL) + (int(235 * clamp(pi) * q),)))
        d.ellipse((x + 12, yy + 12, x + 46, yy + 46), fill=YEL + (aa,))
        n = str(k + 1); d.text((x + 29 - tw(n, fN) / 2, yy + 14), n, font=fN, fill=INK + (aa,))
        ly = yy + 56
        for ln in wrap(name, fT, cw - 24)[:2]:
            d.text((x + 12, ly), ln, font=fT, fill=WHITE + (aa,)); ly += 26
        d.text((x + 12, yy + 118), jenis, font=fS, fill=YEL + (aa,))
        if k < 4:
            ax = x + cw + 2
            d.polygon([(ax + 4, yy + 66), (ax + 18, yy + 75), (ax + 4, yy + 84)], fill=YEL + (aa,))
        x += cw + gap
    # phase arrow label
    if t >= E["five_1"]:
        f = font(F_XB, 20); qq = int(a * clamp((t - E["five_1"]) / 0.3))
        d.text((W / 2 - tw("URUTAN FASA TEKNIK: PECUTAN → PENDARATAN", f) / 2, y0 - 34), "URUTAN FASA TEKNIK: PECUTAN → PENDARATAN",
               font=f, fill=YEL + (qq,), stroke_width=3, stroke_fill=(0, 0, 0, qq))

def load_chart(d, t):
    p, q = inout(t, E["load"], E["load_out"], 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); x0 = 20 - (1 - eo(p)) * 340; y0 = 150; pw, ph = 290, 310
    rrect(d, (x0, y0, x0 + pw, y0 + ph), 16, PANEL + (int(225 * q),))
    rrect(d, (x0 + 12, y0 + 12, x0 + pw - 12, y0 + 46), 8, YEL + (a,))
    d.text((x0 + 22, y0 + 18), "BEBAN BERANSUR-ANSUR", font=font(F_XB, 17), fill=INK + (a,))
    base = y0 + ph - 50; hs = [45, 75, 105, 135]
    grow = eo((t - E["load_naik"] + 1.2) / 1.6) if t >= E["load_ringan"] else 0
    for k in range(4):
        bx = x0 + 24 + k * 64
        hk = hs[0] if k == 0 else hs[0] + (hs[k] - hs[0]) * grow
        if t < E["load_ringan"]: hk = 0
        else: hk *= eo((t - E["load_ringan"]) / 0.5)
        col = YEL if k == 0 else TEAL
        rrect(d, (bx, base - hk, bx + 50, base), 8, col + (a,))
        lab = f"M{k + 1}"; f = font(F_XB, 20)
        d.text((bx + 25 - tw(lab, f) / 2, base + 10), lab, font=f, fill=WHITE + (a,))
    if t >= E["load_ringan"]:
        d.text((x0 + 24, y0 + 58), "Mula: beban ringan", font=font(F_B, 20), fill=YEL + (a,))
    if grow > 0.2:
        f = font(F_B, 20); d.text((x0 + 24, y0 + 86), "→ naik berangsur-angsur", font=f, fill=WHITE + (int(a * clamp(grow)),))

DAYS = ["ISN", "SEL", "RAB", "KHA", "JUM", "SAB", "AHD"]
def week(d, t):
    p, q = inout(t, E["week"], E["week_out"], 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); bw, gap = 112, 10; x0 = (W - (7 * bw + 6 * gap)) / 2; y0 = 30 + (1 - eo(p)) * -200
    f1 = font(F_XB, 22); f2 = font(F_B, 17)
    title = "2× SEMINGGU SAHAJA"; wt = tw(title, font(F_XB, 26)) + 30
    rrect(d, ((W - wt) / 2, y0, (W + wt) / 2, y0 + 42), 10, YEL + (a,))
    d.text(((W - tw(title, font(F_XB, 26))) / 2, y0 + 6), title, font=font(F_XB, 26), fill=INK + (a,))
    for k, dn in enumerate(DAYS):
        x = x0 + k * (bw + gap); y = y0 + 54
        train = k in (0, 3) and t >= E["week_2x"] + 0.2 * (k == 3)
        rest = (k in (1, 2)) and t >= E["week_rest"]
        col = RED if train else (TEAL if rest else PANEL)
        rrect(d, (x, y, x + bw, y + 86), 12, col + (int(230 * q),))
        d.text((x + bw / 2 - tw(dn, f1) / 2, y + 10), dn, font=f1, fill=WHITE + (a,))
        lab = "LATIHAN" if train else ("REHAT" if rest else "")
        if lab: d.text((x + bw / 2 - tw(lab, f2) / 2, y + 50), lab, font=f2, fill=(YEL if train else WHITE) + (a,))
    if t >= E["week_rest"]:
        aa = int(a * clamp((t - E["week_rest"]) / 0.3)); txt = "≥ 1 hari rehat antara sesi"
        f = font(F_XB, 22); d.text(((W - tw(txt, f)) / 2, y0 + 150), txt, font=f, fill=WHITE + (aa,), stroke_width=3, stroke_fill=(0, 0, 0, aa))

COLW = [172, 140, 152, 172, 182, 134, 272]
def table(d, t):
    p, q = inout(t, E["table"], E["table_out"], 0.4, 0.3)
    if q <= 0: return
    a = int(255 * q)
    d.rectangle((0, 0, W, H), fill=(6, 20, 24, int(215 * q)))
    x0 = (W - sum(COLW)) / 2; y0 = 28 + (1 - eo(p)) * 30
    rrect(d, (x0, y0, x0 + 300, y0 + 40), 10, YEL + (a,))
    d.text((x0 + 14, y0 + 6), "PARAMETER LATIHAN", font=font(F_XB, 24), fill=INK + (a,))
    fh, fc, fb = font(F_XB, 17), font(F_M, 17), font(F_XB, 17)
    y = y0 + 52
    # header
    hh = 50
    d.rectangle((x0, y, x0 + sum(COLW), y + hh), fill=TEAL + (a,))
    x = x0
    for k, (hd, cw) in enumerate(zip(L.TABLE_HEAD, COLW)):
        ly = y + 6
        for ln in wrap(hd, fh, cw - 14)[:2]:
            d.text((x + 7, ly), ln, font=fh, fill=WHITE + (a,)); ly += 20
        x += cw
    y += hh
    hl_col = 6 if t >= E["table_m12"] else None
    for r, row in enumerate(L.TABLE):
        ti = E["table"] + 0.25 + 0.22 * r
        pr = clamp((t - ti) / 0.3)
        if pr <= 0: break
        aa = int(a * pr)
        cells = [wrap(c, fb if k == 0 else fc, cw - 14) for k, (c, cw) in enumerate(zip(row, COLW))]
        rh = max(len(c) for c in cells) * 21 + 14
        d.rectangle((x0, y, x0 + sum(COLW), y + rh), fill=((24, 52, 56) if r % 2 == 0 else (16, 40, 44)) + (int(240 * pr * q),))
        x = x0
        for k, (lines, cw) in enumerate(zip(cells, COLW)):
            ly = y + 6
            col = YEL if k == 0 else WHITE
            for ln in lines:
                d.text((x + 7, ly), ln, font=fb if k == 0 else fc, fill=col + (aa,)); ly += 21
            x += cw
        y += rh
    if hl_col is not None:
        pulse = 0.6 + 0.4 * math.sin((t - E["table_m12"]) * 5) if t < E["table_m34"] + 1.5 else 1.0
        cx0 = x0 + sum(COLW[:hl_col]); cx1 = cx0 + COLW[hl_col]
        d.rounded_rectangle((cx0 - 2, y0 + 50, cx1 + 2, y + 2), 6, outline=YEL + (int(a * pulse),), width=4)
        lab = "Minggu 1–2: kuasai teknik" if t < E["table_m34"] else "Minggu 3–4: tambah set / jarak"
        f = font(F_XB, 18); lw = tw(lab, f) + 24
        rrect(d, (cx1 - lw, y + 8, cx1, y + 38), 8, YEL + (a,)); d.text((cx1 - lw + 12, y + 13), lab, font=f, fill=INK + (a,))

def safety(d, t):
    p, q = inout(t, E["safe"], E["safe_out"] + 0.3, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 380; x0 = W - pw - 36 + (1 - eo(p)) * (pw + 60); y0 = 150
    rrect(d, (x0, y0, x0 + pw, y0 + 46), 10, RED + (a,))
    d.text((x0 + 16, y0 + 9), "KESELAMATAN", font=font(F_XB, 24), fill=WHITE + (a,))
    items = [(E["safe_1"], "Rehat yang cukup", "setiap latihan"), (E["safe_2"], "Kotak 20–30 cm", "had ketinggian"),
             (E["safe_3"], "Letih? Berhenti", "jangan paksa")]
    y = y0 + 58
    for k, (ti, t1, t2) in enumerate(items):
        if ti is None or t < ti: continue
        pi = eob((t - ti) / 0.35); aa = int(a * clamp(pi))
        rrect(d, (x0, y, x0 + pw, y + 74), 12, PANEL + (int(230 * clamp(pi) * q),))
        check(d, x0 + 16, y + 22, 28, YEL + (aa,))
        d.text((x0 + 58, y + 10), t1, font=font(F_XB, 25), fill=WHITE + (aa,))
        d.text((x0 + 58, y + 44), t2, font=font(F_SB, 18), fill=(190, 220, 216, aa))
        if k == 1:  # box height ruler
            bx = x0 + pw - 70
            d.rectangle((bx, y + 30, bx + 44, y + 64), fill=(160, 110, 60, aa))
            d.line([(bx + 54, y + 14), (bx + 54, y + 64)], fill=YEL + (aa,), width=3)
        y += 84

def end_card(d, t):
    lt = t - CARD_T0
    if lt < 0: return
    p = eob(lt / 0.45)
    f1 = font(F_XB, 30); l1 = "SETERUSNYA"; w1 = tw(l1, f1) + 36
    y = 60 + (1 - p) * 40
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 48), 10, YEL + (255,))
    d.text(((W - tw(l1, f1)) / 2, y + 7), l1, font=f1, fill=INK + (255,))
    if lt > 0.15:
        sc = clamp(eob((lt - 0.15) / 0.4), 0, 1.2); f = font(F_XB, max(8, int(64 * sc)))
        l2 = "DEMONSTRASI DI PADANG →"
        d.text(((W - tw(l2, f)) / 2, y + 100 - 32 * sc), l2, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=(0, 0, 0, 255))

def intro(d, t):
    if "intro" not in E or E["intro"] is None: return
    p, q = inout(t, E["intro"], E["intro_out"], 0.5, 0.4)
    if q <= 0: return
    a = int(255 * q); f1, f2 = font(F_XB, 26), font(F_XB, 58)
    l1 = "PERBINCANGAN"; w1 = tw(l1, f1) + 32
    y = 230 + (1 - eo(p)) * 30
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 44), 10, YEL + (a,))
    d.text(((W - tw(l1, f1)) / 2, y + 7), l1, font=f1, fill=INK + (a,))
    sc = clamp(eob((t - E["intro"] - 0.15) / 0.45), 0, 1.2)
    if sc > 0.02:
        f = font(F_XB, max(8, int(58 * sc))); l2 = "REKA BENTUK 5 LATIHAN"
        d.text(((W - tw(l2, f)) / 2, y + 100 - 29 * sc), l2, font=f, fill=WHITE + (a,), stroke_width=6, stroke_fill=(0, 0, 0, a))

def overlays(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    intro(d, t)
    hook_gfx(d, t)
    lower_third(d, t, E["lt_zarith"], E["lt_zarith_out"], "Muhammad Zarith Ridzuan", "JURULATIH LAPANGAN 1")
    lower_third(d, t, E["lt_hatim"], E["lt_hatim_out"], "Ahmad Hatim", "JURULATIH LAPANGAN 2")
    five_strip(d, t); load_chart(d, t); week(d, t); safety(d, t)
    prinsip(d, t)
    table(d, t)
    end_card(d, t)
    if t < TAIL_T0: caption(d, t, 640 if E["table"] - 0.2 <= t <= E["table_out"] else 610)
    if not FINAL: d.text((W - 110, 696), "PREVIEW", font=font(F_B, 16), fill=(255, 255, 255, 140))
    return img

# ------------------------------------------------------------------ video
def framing(src_t):
    for a, b, xy, z in L.FRAMING:
        if a <= src_t < b: return xy, z
    return L.C_XY, 1.0

def read_frames(a, n, step=1.0):
    need = int(math.ceil(n * step)) + 1
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", SRC, "-frames:v", str(need),
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    frames, last = [], None
    want = [int(round(k * step)) for k in range(n)]
    idx = 0; wi = 0
    while wi < n:
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3: buf = last
        last = buf
        while wi < n and want[wi] == idx:
            yield np.frombuffer(buf, np.uint8).reshape(H, W, 3); wi += 1
        idx += 1
    p.stdout.close(); p.wait()

def crop(fr, cx, cy, z):
    if z <= 1.001: return Image.fromarray(fr)
    cw, ch = W / z, H / z
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    return Image.fromarray(fr).resize((W, H), Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

vid = os.path.join(OUT, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                        "-crf", "18" if FINAL else "26", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
FLASHES = ([HOOK_END] if HOOK_REGS else []) + [E["table"]]
fi = 0
def emit(img, t):
    global fi
    base = img.convert("RGBA"); base.alpha_composite(overlays(t)); out = base.convert("RGB")
    for ft in FLASHES:
        dt = t - ft
        if -0.02 <= dt < 0.16: out = Image.blend(out, Image.new("RGB", (W, H), WHITE), 0.75 * (1 - clamp(dt / 0.16)))
    if t > DUR - 0.4: out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (DUR - 0.4)) / 0.4))
    enc.stdin.write(out.tobytes()); fi += 1

last = None
for si, ((a, b, r, kind), (f0, n)) in enumerate(zip(SEGS, seg_f)):
    for k, fr in enumerate(read_frames(a, n, r)):
        st = a + k * r / FPS
        (fx, fy), z = framing(st)
        if HOOK_REGS and kind != "tail": z += 0.12 * (si % 2)
        last = crop(fr, fx, fy, z)
        emit(last, fi / FPS)
print(f"segments done ({len(SEGS)})", flush=True)
blur = last.filter(ImageFilter.GaussianBlur(14)); dark = Image.blend(blur, Image.new("RGB", (W, H), (8, 28, 30)), 0.6)
for k in range(END_N):
    t = fi / FPS; emit(Image.blend(last, dark, eo((t - END_T0) / 0.4)), t)
enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio
srcw = os.path.join(OUT, "src48.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-ac", "2", "-ar", str(SR), srcw], check=True)
w = wave.open(srcw); A = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
NS = int(DUR * SR); voice = np.zeros((NS + SR, 2), np.float32); amb = np.zeros((NS + SR, 2), np.float32)
fade = int(0.012 * SR)
for (a, b, r, kind), (f0, n) in zip(SEGS, seg_f):
    o = int(f0 / FPS * SR)
    if kind == "tail":  # sped-up ambience, quiet
        idx = (np.arange(int(n / FPS * SR)) * r).astype(int) + int(a * SR)
        idx = idx[idx < len(A)]; c = A[idx] * 0.5
        env = np.ones(len(c), np.float32); env[:fade] = np.linspace(0, 1, fade); env[-int(0.3 * SR):] = np.linspace(1, 0, int(0.3 * SR))
        amb[o:o + len(c)] += c * env[:, None] * 1.6; continue
    s0 = int(a * SR); Ln = int(n / FPS * SR); c = A[s0:s0 + Ln].copy()
    env = np.ones(len(c), np.float32); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
    voice[o:o + len(c)] += c * env[:, None]
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
def tick():
    t_ = tt(0.05); return (np.sin(2 * np.pi * 2200 * t_) * np.exp(-t_ * 90) * 0.4).astype(np.float32)
def paper():
    n = int(0.25 * SR); x = rng.standard_normal(n).astype(np.float32)
    y = np.diff(x, prepend=0) * np.exp(-np.arange(n) / SR * 14) * 0.35
    return y

sfx = np.zeros(NS, np.float32); cues = []
def cue(name, sig, at, g):
    if at is None: return
    o = int(at * SR)
    if o < 0: sig = sig[-o:]; o = 0
    m = min(len(sig), NS - o)
    if m > 0: sfx[o:o + m] += sig[:m] * g
    cues.append((round(at, 2), name))
cue("boom (hook title)", boom(), E["hook_title"], 0.7)
cue("whoosh (hook title)", whoosh(0.45), E["hook_title"] - 0.2, 0.35)
for k in ("eq_kon", "eq_kotak", "eq_tali", "eq_pasir"): cue(f"pop ({k})", pop(), E[k], 0.9)
if HOOK_REGS:
    cue("riser into body", riser(0.8), HOOK_END - 0.8, 0.5)
    cue("boom + flash (cut to body)", boom(), HOOK_END, 0.6)
cue("whoosh (intro title)", whoosh(0.5), E["intro"] - 0.1, 0.35)
cue("boom (intro title)", boom(), E["intro"] + 0.2, 0.5)
cue("whoosh (lower third Zarith)", whoosh(0.4), E["lt_zarith"] - 0.1, 0.3)
cue("whoosh (prinsip)", whoosh(0.4), E["prinsip"] - 0.1, 0.3)
for k in ("pr_laksana", "pr_sistematik", "pr_tahap", "pr_selamat"): cue(f"ding ({k})", ding(), E[k], 0.45)
for k in range(5): cue(f"pop (latihan {k + 1})", pop(), E["five"] + 0.18 * k, 0.7)
cue("whoosh (beban chart)", whoosh(0.5), E["load"] - 0.1, 0.35)
cue("riser (beban naik)", riser(1.2), E["load_naik"] - 1.2, 0.35)
cue("whoosh (lower third Hatim)", whoosh(0.4), E["lt_hatim"] - 0.1, 0.3)
cue("whoosh down (minggu)", whoosh(0.5, up=False), E["week"] - 0.1, 0.35)
cue("pop (latihan 1)", pop(), E["week_2x"], 0.8); cue("pop (latihan 2)", pop(), E["week_2x"] + 0.2, 0.8)
cue("tick (rehat)", tick(), E["week_rest"], 0.8)
cue("whoosh + flash (jadual)", whoosh(0.5), E["table"] - 0.15, 0.45)
for r in range(5): cue(f"paper tick (row {r + 1})", paper(), E["table"] + 0.25 + 0.22 * r, 0.6)
cue("ding (minggu 1-2)", ding(), E["table_m12"], 0.5); cue("ding (minggu 3-4)", ding(), E["table_m34"], 0.5)
cue("whoosh (keselamatan)", whoosh(0.5), E["safe"] - 0.1, 0.35)
for k in ("safe_1", "safe_2", "safe_3"): cue(f"pop ({k})", pop(), E[k], 0.8)
cue("whoosh (end card)", whoosh(0.5), CARD_T0 - 0.1, 0.4); cue("boom (end card)", boom(), CARD_T0 + 0.2, 0.6)

def wr(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    ww = wave.open(path, "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR)
    ww.writeframes((x * 32767).astype(np.int16).tobytes()); ww.close()
wr(os.path.join(OUT, "voice.wav"), voice); wr(os.path.join(OUT, "amb.wav"), amb); wr(os.path.join(OUT, "sfx.wav"), sfx)
name = "FINAL_ADEGAN3.mp4" if FINAL else "PREVIEW_ADEGAN3.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", os.path.join(OUT, "voice.wav"),
                "-i", os.path.join(OUT, "amb.wav"), "-i", os.path.join(OUT, "sfx.wav"), "-filter_complex",
                "[1]highpass=f=90,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                "loudnorm=I=-16:TP=-1.5:LRA=9[v];[v][2][3]amix=inputs=3:normalize=0:duration=longest,apad[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{DUR:.3f}",
                os.path.join(OUT, name)], check=True)
json.dump({"duration": DUR, "hook_end": HOOK_END, "tail_t0": TAIL_T0, "segments": SEGS,
           "events": {k: (round(v, 2) if v is not None else None) for k, v in E.items()}, "sfx": cues},
          open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, name), f"{DUR:.2f}s")
