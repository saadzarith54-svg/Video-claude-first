"""Render ADEGAN 5 preview.
usage: python3 render5.py SRCDIR WORKDIR OUTDIR [--final]
  SRCDIR: <key>.bin   WORKDIR: <key>.json transcripts, <key>.wav (16k), tr_<key>.json tracks
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "adegan3"))
import edl5 as L
import edl3 as L3   # parameter table (same data as the script table)

SRCDIR, WORK, OUT = sys.argv[1:4]
FINAL = "--final" in sys.argv
W, H, FPS, SR = 1280, 720, 30, 48000
os.makedirs(OUT, exist_ok=True)
TEAL = (16, 143, 132); TEAL_D = (8, 70, 66); YEL = (255, 210, 63); WHITE = (255, 255, 255)
RED = (220, 60, 50); GREEN = (40, 170, 90); INK = (20, 20, 20); PANEL = (10, 30, 34)
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
def src(k): return os.path.join(SRCDIR, f"{k}.bin")
def check(d, x, y, s, col):
    d.line([(x, y + s * 0.5), (x + s * 0.38, y + s * 0.85), (x + s, y + s * 0.1)], fill=col, width=max(3, int(s * 0.18)), joint="curve")
def cross(d, x, y, s, col):
    w = max(3, int(s * 0.18)); d.line([(x, y), (x + s, y + s)], fill=col, width=w); d.line([(x + s, y), (x, y + s)], fill=col, width=w)
def wrap(txt, f, width):
    lines, cur = [], ""
    for wd in txt.split():
        test = (cur + " " + wd).strip()
        if tw(test, f) <= width or not cur: cur = test
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

# ------------------------------------------------------------------ media helpers
def read_raw(path, a, n, size=(W, H)):
    w, h = size
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{max(a, 0):.3f}", "-i", path, "-frames:v", str(n),
                          "-vf", f"fps=30,scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(w * h * 3)
        if len(buf) < w * h * 3: buf = last if last is not None else bytes(w * h * 3)
        last = buf
        yield np.frombuffer(buf, np.uint8).reshape(h, w, 3)
    p.stdout.close(); p.wait()

def mi_file(k, a, b):
    p = os.path.join(OUT, f"mi_{k}_{a:.2f}_{b:.2f}.mp4")
    if not os.path.exists(p):
        s0 = max(0, a - 0.2)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s0:.3f}", "-t", f"{b - a + 0.5:.3f}", "-i", src(k), "-an",
                        "-vf", "fps=30,minterpolate=fps=120:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1",
                        "-c:v", "libx264", "-crf", "16", "-preset", "fast", p + ".tmp.mp4"], check=True)
        os.rename(p + ".tmp.mp4", p)
    return p, max(0, a - 0.2)

def shot_frames(k, a, b, rate):
    n = int(round((b - a) / rate * FPS))
    if rate >= 0.999:
        for j, fr in enumerate(read_raw(src(k), a, n)): yield a + j / FPS, fr
        return
    path, s0 = mi_file(k, a, b)
    need = int(math.ceil((b - s0) * 120)) + 2
    want = [int(round((a + j * rate / FPS - s0) * 120)) for j in range(n)]
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

def crop(fr, cx, cy, z, size=(W, H)):
    img = fr if isinstance(fr, Image.Image) else Image.fromarray(fr)
    ow, oh = size; ar = ow / oh
    ch = H / z; cw = ch * ar
    if cw > W: cw = W; ch = cw / ar
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    return img.resize(size, Image.BICUBIC, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))

_trk = {}
def track_pos(k, t, sigma=0.5):
    key = (k, sigma)
    if key not in _trk:
        r = json.load(open(os.path.join(WORK, f"tr_{k}.json")))
        tt = np.array([x[0] for x in r])
        ok = np.array([x[1] is not None and x[3] is not None and 110 < x[3] < 470 for x in r])
        if ok.sum() < 3: _trk[key] = None
        else:
            xs = np.interp(tt, tt[ok], np.array([x[1] if o else 0 for x, o in zip(r, ok)])[ok])
            ys = np.interp(tt, tt[ok], np.array([x[2] if o else 0 for x, o in zip(r, ok)])[ok])
            kk = np.exp(-0.5 * (np.arange(-30, 31) / (sigma * 10)) ** 2); kk /= kk.sum()
            sm = lambda v: np.convolve(np.pad(v, 30, mode="edge"), kk, mode="valid")
            _trk[key] = (tt, sm(xs), sm(ys))
    tr = _trk[key]
    if tr is None: return 640, 360
    return float(np.interp(t, tr[0], tr[1])), float(np.interp(t, tr[0], tr[2]))

def demo_view(k, t, extra, size=(W, H), fr=None):
    if "fixed" in extra: x, y, z = extra["fixed"]
    elif L.FRAME.get(k) is not None: x, y, z = L.FRAME[k]
    else:
        x, y = track_pos(k, t); y -= 15; z = extra.get("zoom", L.TRACK_ZOOM.get(k, 1.6))
    return crop(fr, x, y, z, size)

# ------------------------------------------------------------------ transcripts & talk regions
WORDS = {}
def words(k):
    if k not in WORDS:
        ws = []
        for s in json.load(open(os.path.join(WORK, f"{k}.json"))):
            for w in s["words"]: ws.append((w["w"].strip(), w["s"], w["e"]))
        WORDS[k] = ws
    return WORDS[k]
def kw(k, key, after):
    if not isinstance(key, str): return float(key)
    for w, s, e in words(k):
        if s >= after - 0.3 and w.strip(",.?!").lower().startswith(key.strip(",.?!").lower()): return max(s, after - 0.3)
    print("WARN keyword not found", k, key, after); return float(after)

def gaps16(k):
    wf = wave.open(os.path.join(WORK, f"{k}.wav")); a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 800; db = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(a) - hop, hop)])
    thr = np.percentile(db, 20) + 5; low = db < thr; g, i = [], 0
    while i < len(low):
        if low[i]:
            j = i
            while j < len(low) and low[j]: j += 1
            if (j - i) * 0.05 >= L.PAUSE_MIN: g.append((i * 0.05, j * 0.05))
            i = j
        else: i += 1
    return g
def talk_regions(k, a0, b0, cuts):
    regs, cur, pad = [], a0, L.PAUSE_KEEP / 2
    for g0, g1 in gaps16(k):
        if g1 <= a0 or g0 >= b0: continue
        a, b = max(cur, a0), min(g0 + pad, b0)
        if b - a > 0.15: regs.append((a, b))
        cur = max(g1 - pad, a0)
    if b0 - cur > 0.15: regs.append((cur, b0))
    for c0, c1 in cuts:
        nr = []
        for a, b in regs:
            if c1 <= a or c0 >= b: nr.append((a, b)); continue
            if c0 - a > 0.15: nr.append((a, c0))
            if b - c1 > 0.15: nr.append((c1, b))
        regs = nr
    return regs

# ------------------------------------------------------------------ build timeline
SEGS = []   # dicts with f0, n
f = 0
def add(seg, n):
    global f
    seg["f0"], seg["n"] = f, n; SEGS.append(seg); f += n
HOOK_N = int(round(max((L.HOOK_LEFT[2] - L.HOOK_LEFT[1]) / L.HOOK_LEFT[3], (L.HOOK_RIGHT[2] - L.HOOK_RIGHT[1]) / L.HOOK_RIGHT[3]) * FPS))
for it in L.SEQ:
    kind = it[0]
    if kind == "hook":
        add({"kind": "hook"}, HOOK_N + int(L.HOOK_TITLE_HOLD * FPS))
    elif kind == "card":
        add({"kind": "card", "num": it[1], "name": it[2], "jenis": it[3]}, int(L.CARD_DUR * FPS))
    elif kind == "talk":
        _, k, a, b, who, cuts = it
        regs = talk_regions(k, a, b, cuts)
        start = f
        for ri, (ra, rb) in enumerate(regs):
            add({"kind": "talk", "clip": k, "a": ra, "b": rb, "who": who, "ri": ri, "talk_start": start}, int(round((rb - ra) * FPS)))
    elif kind == "demo":
        _, k, a, b, rate, label, ps, extra = it
        add({"kind": "demo", "clip": k, "a": a, "b": b, "rate": rate, "label": label, "pass": ps, "extra": extra},
            int(round((b - a) / rate * FPS)))
    elif kind == "recap": add({"kind": "recap"}, int(L.RECAP_DUR * FPS))
    elif kind == "end": add({"kind": "end"}, int(L.END_DUR * FPS))
TOTAL = f; DUR = TOTAL / FPS
SEG_AT = np.zeros(TOTAL, np.int32)
for i, s in enumerate(SEGS): SEG_AT[s["f0"]:s["f0"] + s["n"]] = i
def s2o(k, t):
    """talk clip local time -> output seconds"""
    best = None
    for s in SEGS:
        if s["kind"] == "talk" and s["clip"] == k:
            if s["a"] <= t <= s["b"]: return s["f0"] / FPS + (t - s["a"])
            if t < s["a"] and best is None: best = s["f0"] / FPS
    if best is None:
        last = [s for s in SEGS if s["kind"] == "talk" and s["clip"] == k][-1]; best = (last["f0"] + last["n"]) / FPS
    return best
def talk_span(k):
    ss = [s for s in SEGS if s["kind"] == "talk" and s["clip"] == k]
    return ss[0]["f0"] / FPS, (ss[-1]["f0"] + ss[-1]["n"]) / FPS

# panels resolved to output time
PAN = []
for k, plist in L.PANELS.items():
    for (t0, t1, title, rows, pipspec) in plist:
        rr = [(s2o(k, kw(k, key, after if after else key)), txt) for key, after, txt in rows]
        PAN.append({"clip": k, "t0": s2o(k, t0), "t1": s2o(k, t1), "title": title, "rows": rr, "pip": pipspec})

# captions
cap = []
for it in L.SEQ:
    if it[0] != "talk": continue
    k = it[1]; ws = []
    for txt, s0, e0 in words(k):
        if any(d0 <= s0 <= d1 for d0, d1 in L.DROP.get(k, [])): continue
        bare = txt.strip(",.?!")
        if bare in L.CORRECTIONS: txt = txt.replace(bare, L.CORRECTIONS[bare]) if L.CORRECTIONS[bare] else ""
        if not txt or txt.lower().startswith("terima"): continue
        for s in SEGS:
            if s["kind"] == "talk" and s["clip"] == k:
                ov = min(e0, s["b"]) - max(s0, s["a"])
                if ov > 0.06 and s0 < s["b"] - 0.1:
                    a2, b2 = max(s0, s["a"]), min(e0, s["b"])
                    if b2 - a2 > 0.9: a2 = b2 - 0.6
                    ws.append((txt, s["f0"] / FPS + a2 - s["a"], s["f0"] / FPS + b2 - s["a"])); break
    chunks, cur = [], []
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
            f = font(F_XB, 40); sp = f.getlength(" ")
            total = sum(f.getlength(x[0]) for x in c) + sp * (len(c) - 1)
            x = (W - total) / 2; y = 622 + (1 - eob((t - st) / 0.18)) * 14
            for wt, s, e in c:
                d.text((x, y), wt, font=f, fill=(YEL if s <= t < e + 0.05 else WHITE) + (255,), stroke_width=4, stroke_fill=(0, 0, 0, 255))
                x += f.getlength(wt) + sp
            return

# ------------------------------------------------------------------ graphics
def lower_third(d, t, t_in, t_out, name, tagt):
    p, q = inout(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q); fN, fT = font(F_XB, 34), font(F_B, 18)
    wN = tw(name, fN) + 48; x0 = -wN + (wN + 40) * eo(p); y0 = 470; wT = tw(tagt, fT) + 28
    rrect(d, (x0, y0, x0 + wT, y0 + 30), 8, YEL + (a,)); d.text((x0 + 14, y0 + 5), tagt, font=fT, fill=INK + (a,))
    rrect(d, (x0, y0 + 36, x0 + wN, y0 + 92), 10, TEAL + (int(235 * q),))
    d.rectangle((x0, y0 + 36, x0 + 8, y0 + 92), fill=YEL + (a,)); d.text((x0 + 26, y0 + 44), name, font=fN, fill=WHITE + (a,))

def info_panel(d, t, pan):
    p, q = inout(t, pan["t0"], pan["t1"], 0.4, 0.3)
    if q <= 0: return
    a = int(255 * q); pw = 430; x0 = 28 - (1 - eo(p)) * (pw + 60); y0 = 96
    ft, fr = font(F_XB, 22), font(F_B, 21)
    rrect(d, (x0, y0, x0 + tw(pan["title"], ft) + 30, y0 + 40), 10, YEL + (a,)); d.text((x0 + 15, y0 + 8), pan["title"], font=ft, fill=INK + (a,))
    y = y0 + 50
    shown = [r for r in pan["rows"] if t >= r[0]]
    for i, (ti, txt) in enumerate(shown):
        pi = clamp(eob((t - ti) / 0.35)); aa = int(a * pi)
        lines = wrap(txt, fr, pw - 64); h = 22 + 27 * len(lines)
        last = i == len(shown) - 1
        rrect(d, (x0, y, x0 + pw, y + h), 12, ((TEAL if last else PANEL) + (int(230 * q * pi),)))
        check(d, x0 + 14, y + h / 2 - 11, 22, YEL + (aa,))
        ly = y + 11
        for ln in lines: d.text((x0 + 48, ly), ln, font=fr, fill=WHITE + (aa,)); ly += 27
        y += h + 8

def card(d, t, seg):
    t0 = seg["f0"] / FPS; t1 = t0 + seg["n"] / FPS; lt = t - t0
    q = 1 - clamp((t - (t1 - 0.3)) / 0.3); a = int(255 * q)
    f1, f2, f3 = font(F_XB, 30), font(F_XB, 70), font(F_XB, 30)
    l1 = f"LATIHAN {seg['num']}/5"; w1 = tw(l1, f1) + 36; y = 220
    p = eob(lt / 0.4)
    rrect(d, ((W - w1) / 2, y + (1 - p) * 30, (W + w1) / 2, y + 48 + (1 - p) * 30), 10, YEL + (a,))
    d.text(((W - tw(l1, f1)) / 2, y + 7 + (1 - p) * 30), l1, font=f1, fill=INK + (a,))
    sc = clamp(eob((lt - 0.12) / 0.45), 0, 1.15)
    name = seg["name"]; fsz = 70 if tw(name, f2) < W - 120 else 52
    if sc > 0.02:
        f = font(F_XB, max(8, int(fsz * sc)))
        d.text(((W - tw(name, f)) / 2, y + 110 - fsz / 2 * sc), name, font=f, fill=WHITE + (a,), stroke_width=7, stroke_fill=(0, 0, 0, a))
    if lt > 0.5:
        aa = int(a * clamp((lt - 0.5) / 0.3)); txt = "Jenis: " + seg["jenis"]
        d.text(((W - tw(txt, f3)) / 2, y + 175), txt, font=f3, fill=YEL + (aa,), stroke_width=4, stroke_fill=(0, 0, 0, aa))
    # 5-dot progress
    for i in range(5):
        cx = W / 2 - 80 + i * 40
        d.ellipse((cx - 9, 470 - 9, cx + 9, 470 + 9), fill=((YEL if i < seg["num"] else (90, 110, 110)) + (a,)))

def demo_gfx(d, t, seg):
    t0 = seg["f0"] / FPS; t1 = t0 + seg["n"] / FPS
    p, q = inout(t, t0 + 0.1, t1, 0.35, 0.2)
    if q <= 0: return
    a = int(255 * q); f1, f2 = font(F_XB, 18), font(F_XB, 30)
    slow = seg["rate"] < 0.999
    small = f"CONTOH PERGERAKAN · ULANGAN {seg['pass']}/2" + (" · SLOW-MO" if slow else "")
    x = 30 - (1 - eo(p)) * 700; y = 30
    rrect(d, (x, y, x + tw(small, f1) + 26, y + 30), 8, YEL + (a,)); d.text((x + 13, y + 6), small, font=f1, fill=INK + (a,))
    col = {"BETUL": GREEN, "SALAH": RED}.get(seg["extra"].get("stamp"), (RED if seg["pass"] == 1 else TEAL))
    rrect(d, (x, y + 36, x + tw(seg["label"], f2) + 36, y + 86), 10, col + (int(235 * q),))
    d.text((x + 18, y + 43), seg["label"], font=f2, fill=WHITE + (a,))
    if slow:
        d.ellipse((W - 168, 34, W - 152, 50), fill=RED + (255,)); d.text((W - 144, 30), "SLOW-MO", font=font(F_XB, 20), fill=WHITE + (255,))
    # cue chips bottom
    cues = L.DEMO_CUES.get(seg["clip"], [])
    fc = font(F_XB, 21); xx = 30; yy = 640
    for i, c in enumerate(cues):
        ti = t0 + 0.6 + 0.5 * i
        if t < ti: break
        pi = clamp(eob((t - ti) / 0.3)); w = tw(c, fc) + 34
        rrect(d, (xx, yy, xx + w * clamp(pi, 0.3, 1), yy + 44), 22, (PANEL + (int(220 * q),)))
        if pi > 0.9: d.text((xx + 17, yy + 9), c, font=fc, fill=WHITE + (a,))
        xx += w + 10
    st = seg["extra"].get("stamp")
    if st:
        pi = eob((t - t0 - 0.4) / 0.4)
        if pi > 0:
            sz = int(110 * clamp(pi, 0.2, 1.1)); cx, cy = W - 150, 210
            colr = GREEN if st == "BETUL" else RED
            d.ellipse((cx - sz / 2 - 20, cy - sz / 2 - 20, cx + sz / 2 + 20, cy + sz / 2 + 20), fill=colr + (int(230 * q),))
            (check if st == "BETUL" else cross)(d, cx - sz * 0.35, cy - sz * 0.35, sz * 0.7, WHITE + (a,))
            f = font(F_XB, 30); d.text((cx - tw(st, f) / 2, cy + sz / 2 + 26), st, font=f, fill=colr + (a,), stroke_width=4, stroke_fill=(0, 0, 0, a))
    if seg["extra"].get("line"):
        pi = eo((t - t0 - 1.0) / 0.8)
        if pi > 0:   # straight body line guide for plank (approx head -> heel in the tight crop)
            x0_, y0_, x1_, y1_ = 300, 452, 300 + (980 - 300) * pi, 452 + (470 - 452) * pi
            d.line([(x0_, y0_), (x1_, y1_)], fill=YEL + (a,), width=6)
            if pi > 0.95:
                f = font(F_XB, 24); txt = "LURUS: KEPALA → TUMIT"
                d.text((640 - tw(txt, f) / 2, 390), txt, font=f, fill=YEL + (a,), stroke_width=4, stroke_fill=(0, 0, 0, a))

def zone_bar(d, t, t_in, t_out):
    p, q = inout(t, t_in, t_out, 0.4, 0.3)
    if q <= 0: return
    a = int(255 * q); x0, y0, w = 480, 520, 740
    rrect(d, (x0, y0, x0 + w, y0 + 70), 14, PANEL + (int(220 * q),))
    wz = (w - 30) * eo(p)
    d.rectangle((x0 + 15, y0 + 15, x0 + 15 + wz * 0.55, y0 + 55), fill=RED + (a,))
    d.rectangle((x0 + 15 + wz * 0.55, y0 + 15, x0 + 15 + wz, y0 + 55), fill=YEL + (a,))
    if p > 0.9:
        f = font(F_XB, 20); d.text((x0 + 30, y0 + 24), "ZON TOLAK · condong", font=f, fill=WHITE + (a,))
        d.text((x0 + 15 + (w - 30) * 0.55 + 15, y0 + 24), "ZON TEGAK", font=f, fill=INK + (a,))

def recap(d, t, t0):
    q = 1 - clamp((t - (t0 + L.RECAP_DUR - 0.35)) / 0.35); a = int(255 * q)
    rrect(d, (30, 24, 470, 70), 10, YEL + (a,)); d.text((46, 32), "PARAMETER 5 LATIHAN", font=font(F_XB, 26), fill=INK + (a,))
    cols = [172, 140, 152, 172, 182, 134, 272]; x0 = (W - sum(cols)) / 2; y = 84
    fh, fc, fb = font(F_XB, 17), font(F_M, 17), font(F_XB, 17)
    d.rectangle((x0, y, x0 + sum(cols), y + 50), fill=TEAL + (a,)); x = x0
    for hd, cw in zip(L3.TABLE_HEAD, cols):
        ly = y + 6
        for ln in wrap(hd, fh, cw - 14)[:2]: d.text((x + 7, ly), ln, font=fh, fill=WHITE + (a,)); ly += 20
        x += cw
    y += 50
    for r, row in enumerate(L3.TABLE):
        pr = clamp((t - (t0 + 0.4 + 0.3 * r)) / 0.3)
        if pr <= 0: break
        aa = int(a * pr)
        cells = [wrap(c, fb if k == 0 else fc, cw - 14) for k, (c, cw) in enumerate(zip(row, cols))]
        rh = max(len(c) for c in cells) * 21 + 14
        d.rectangle((x0, y, x0 + sum(cols), y + rh), fill=((24, 52, 56) if r % 2 == 0 else (16, 40, 44)) + (int(240 * pr * q),))
        x = x0
        for k, (lines, cw) in enumerate(zip(cells, cols)):
            ly = y + 7
            for ln in lines: d.text((x + 7, ly), ln, font=fb if k == 0 else fc, fill=(YEL if k == 0 else WHITE) + (aa,)); ly += 21
            x += cw
        y += rh

def end_card(d, t, t0):
    lt = t - t0; p = eob(lt / 0.45); f1 = font(F_XB, 30); l1 = "SETERUSNYA"; w1 = tw(l1, f1) + 36; y = 250 + (1 - p) * 40
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 48), 10, YEL + (255,)); d.text(((W - tw(l1, f1)) / 2, y + 7), l1, font=f1, fill=INK + (255,))
    if lt > 0.15:
        sc = clamp(eob((lt - 0.15) / 0.4), 0, 1.2); f = font(F_XB, max(8, int(70 * sc))); l2 = "PENYEJUKAN →"
        d.text(((W - tw(l2, f)) / 2, y + 100 - 35 * sc), l2, font=f, fill=WHITE + (255,), stroke_width=6, stroke_fill=(0, 0, 0, 255))

def hook_gfx(d, t):
    hold0 = HOOK_N / FPS
    if t < hold0 + 0.2:
        q = 1 - clamp((t - (hold0 - 0.25)) / 0.25); a = int(255 * q)
        f = font(F_XB, 30); txt = "BOLEH BEZAKAN?"; w = tw(txt, f) + 40
        rrect(d, ((W - w) / 2, 26, (W + w) / 2, 76), 12, YEL + (a,)); d.text(((W - tw(txt, f)) / 2, 34), txt, font=f, fill=INK + (a,))
        for side, (lab, colr, fn) in enumerate((("BETUL", GREEN, check), ("SALAH", RED, cross))):
            pi = eob((t - 0.8 - 0.4 * side) / 0.4)
            if pi <= 0: continue
            cx = 320 + side * 640; cy = 560; sz = 64 * clamp(pi, 0.3, 1.1)
            d.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), fill=colr + (int(230 * q),))
            fn(d, cx - sz * 0.4, cy - sz * 0.4, sz * 0.8, WHITE + (a,))
            ff = font(F_XB, 32); d.text((cx - tw(lab, ff) / 2, cy + 70), lab, font=ff, fill=WHITE + (a,), stroke_width=4, stroke_fill=(0, 0, 0, a))
        d.rectangle((W / 2 - 3, 0, W / 2 + 3, H), fill=WHITE + (a,))
    else:
        lt = t - hold0
        f1 = font(F_XB, 28); l1 = "BOUNDING · PECUTAN · LITAR · LOMPAT KOTAK"; w1 = tw(l1, f1) + 36
        p = eob(lt / 0.4)
        rrect(d, ((W - w1) / 2, 230, (W + w1) / 2, 276), 10, YEL + (255,)); d.text(((W - tw(l1, f1)) / 2, 237), l1, font=f1, fill=INK + (255,))
        sc = clamp(eob((lt - 0.1) / 0.45), 0, 1.15); f = font(F_XB, max(8, int(84 * sc)))
        t2 = "5 LATIHAN UTAMA"; d.text(((W - tw(t2, f)) / 2, 350 - 42 * sc), t2, font=f, fill=WHITE + (255,), stroke_width=8, stroke_fill=(0, 0, 0, 255))

# ------------------------------------------------------------------ PiP preload
PW, PH = 400, 225
_pipcache = {}
def pip_frames(spec):
    if spec not in _pipcache:
        k, a, b = spec; n = int(round((b - a) * FPS)); frs = []
        for j, fr in enumerate(read_raw(src(k), a, n)):
            ex = {"zoom": 1.6} if L.FRAME.get(k) is None else {}
            frs.append(demo_view(k, a + j / FPS, ex, (PW, PH), fr))
        _pipcache[spec] = frs
    return _pipcache[spec]
def draw_pip(base, t):
    for pan in PAN:
        if pan["pip"] and pan["t0"] <= t < pan["t1"]:
            frs = pip_frames(pan["pip"])
            p = eo((t - pan["t0"]) / 0.4) * (1 - clamp((t - (pan["t1"] - 0.25)) / 0.25))
            img = frs[int((t - pan["t0"]) * FPS) % len(frs)]
            x, y = W - PW - 30 + (1 - p) * (PW + 60), 110
            sh = Image.new("RGBA", (PW + 16, PH + 54), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((0, 0, PW + 16, PH + 54), 16, fill=PANEL + (235,))
            base.alpha_composite(sh, (int(x - 8), int(y - 8)))
            m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW, PH), 12, fill=255)
            base.paste(img, (int(x), int(y)), m)
            dd = ImageDraw.Draw(base); dd.ellipse((x + 6, y + PH + 13, x + 18, y + PH + 25), fill=RED + (255,))
            dd.text((x + 26, y + PH + 7), "CONTOH PERGERAKAN", font=font(F_XB, 20), fill=WHITE + (255,))
            return

def overlays(t, seg):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    k = seg["kind"]
    if k == "hook": hook_gfx(d, t)
    elif k == "card": card(d, t, seg)
    elif k == "demo": demo_gfx(d, t, seg)
    elif k == "talk":
        ts, te = talk_span(seg["clip"])
        if seg["clip"] in ("5.0a", "5.4a", "5.5d"):
            nm, tg = L.PEOPLE[seg["who"]]; lower_third(d, t, ts + 0.3, ts + 4.5, nm, tg)
        for pan in PAN:
            if pan["clip"] == seg["clip"]: info_panel(d, t, pan)
        if seg["clip"] == "5.0a": zone_bar(d, t, s2o("5.0a", 108.3), s2o("5.0a", 122.9))
        caption(d, t)
    elif k == "recap": recap(d, t, seg["f0"] / FPS)
    elif k == "end": end_card(d, t, seg["f0"] / FPS)
    if not FINAL: d.text((W - 100, 698), "PREVIEW", font=font(F_B, 16), fill=(255, 255, 255, 140))
    return img

# ------------------------------------------------------------------ video
vid = os.path.join(OUT, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18" if FINAL else "26", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
FLASH = [s["f0"] / FPS for s in SEGS if s["kind"] in ("card",) or (s["kind"] == "demo" and s["pass"] == 1)] + [HOOK_N / FPS]
fi = 0
def emit(img, seg):
    global fi
    t = fi / FPS; base = img.convert("RGBA")
    if seg["kind"] == "talk": draw_pip(base, t)
    base.alpha_composite(overlays(t, seg)); out = base.convert("RGB")
    for ft in FLASH:
        dt = t - ft
        if -0.02 <= dt < 0.13: out = Image.blend(out, Image.new("RGB", (W, H), WHITE), 0.65 * (1 - clamp(dt / 0.13)))
    if t > DUR - 0.5: out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (DUR - 0.5)) / 0.5))
    enc.stdin.write(out.tobytes()); fi += 1

def bg_from(k, t):
    fr = next(read_raw(src(k), t, 1)); im = Image.fromarray(fr).filter(ImageFilter.GaussianBlur(16))
    return Image.blend(im, Image.new("RGB", (W, H), (6, 22, 26)), 0.6)

last = None
for si, seg in enumerate(SEGS):
    k = seg["kind"]
    if k == "hook":
        lk, la, lb, lr = L.HOOK_LEFT; rk, ra, rb, rr = L.HOOK_RIGHT
        lf = list(shot_frames(lk, la, lb, lr)); rf = list(shot_frames(rk, ra, rb, rr))
        for j in range(HOOK_N):
            lt, lfr = lf[min(j, len(lf) - 1)]; rt, rfr = rf[min(j, len(rf) - 1)]
            canvas = Image.new("RGB", (W, H))
            canvas.paste(demo_view(lk, lt, {}, (W // 2, H), lfr), (0, 0)); canvas.paste(demo_view(rk, rt, {}, (W // 2, H), rfr), (W // 2, 0))
            last = canvas; emit(canvas, seg)
        dark = Image.blend(last.filter(ImageFilter.GaussianBlur(14)), Image.new("RGB", (W, H), (6, 22, 26)), 0.55)
        for j in range(seg["n"] - HOOK_N): emit(Image.blend(last, dark, eo(j / 8)), seg)
    elif k == "card":
        nxt = next(s for s in SEGS[si + 1:] if s["kind"] in ("talk", "demo"))
        bg = bg_from(nxt["clip"], nxt["a"] + 0.5)
        for j in range(seg["n"]): emit(bg, seg)
    elif k == "talk":
        z0 = 1.0 if seg["ri"] % 2 == 0 else 1.12
        for j, fr in enumerate(read_raw(src(seg["clip"]), seg["a"], seg["n"])):
            img = crop(fr, 640, 330, z0 + 0.015 * j / max(seg["n"] - 1, 1)); last = img; emit(img, seg)
    elif k == "demo":
        for ct, fr in shot_frames(seg["clip"], seg["a"], seg["b"], seg["rate"]):
            img = demo_view(seg["clip"], ct, seg["extra"], (W, H), fr); last = img; emit(img, seg)
    elif k in ("recap", "end"):
        if k == "recap": bgr = Image.blend(last.filter(ImageFilter.GaussianBlur(16)), Image.new("RGB", (W, H), (6, 22, 26)), 0.62)
        for j in range(seg["n"]): emit(bgr, seg)
    print("done", si, k, seg.get("clip", ""), flush=True)
enc.stdin.close(); enc.wait()

# ------------------------------------------------------------------ audio
NS = int(DUR * SR); voice = np.zeros((NS + SR, 2), np.float32)
_a48 = {}
def a48(k):
    if k not in _a48:
        p = os.path.join(OUT, f"a48_{k}.wav")
        if not os.path.exists(p): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src(k), "-ac", "2", "-ar", str(SR), p], check=True)
        w = wave.open(p); _a48[k] = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    return _a48[k]
fade = int(0.015 * SR); mg = np.full(NS + SR, 0.30, np.float32)
for seg in SEGS:
    o = int(seg["f0"] / FPS * SR); Ln = int(seg["n"] / FPS * SR)
    if seg["kind"] == "talk":
        mg[o:o + Ln] = 0.07
        A = a48(seg["clip"]); s0 = int(seg["a"] * SR); c = A[s0:s0 + Ln].copy()
        env = np.ones(len(c), np.float32); env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
        voice[o:o + len(c)] += c * env[:, None]
    # demo clips: natural sound removed (user: buang background sound yang mengganggu)
kk = int(0.35 * SR); mg = np.convolve(mg, np.ones(kk) / kk, mode="same")[:NS]; mg[-int(0.6 * SR):] *= np.linspace(1, 0, int(0.6 * SR))
voice = voice[:NS]

rng = np.random.default_rng(11)
def tt(dd): return np.arange(int(dd * SR)) / SR
def onepole(x, fc):
    al = 1 - math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += al * (x[i] - acc); y[i] = acc
    return y
# original music loop, 104 BPM, Dm - Bb - F - C
BPM = 104; BEAT = 60 / BPM; BAR = 4 * BEAT; NL = int(4 * BAR * SR); loop = np.zeros(NL, np.float32); T = np.arange(NL) / SR
CH = [(73.42, [293.66, 349.23, 440.0]), (116.54, [233.08, 293.66, 349.23]), (87.31, [349.23, 440.0, 523.25]), (65.41, [261.63, 329.63, 392.0])]
for bi, (root, triad) in enumerate(CH):
    s, e = int(bi * BAR * SR), int((bi + 1) * BAR * SR); tb = T[s:e] - bi * BAR
    pad = sum(np.sin(2 * np.pi * fq * tb) + 0.4 * np.sin(2 * np.pi * fq * 2.004 * tb) for fq in triad) / 3
    loop[s:e] += pad * np.minimum(1, tb / 0.25) * np.minimum(1, (BAR - tb) / 0.3) * 0.13
    for q8 in range(8):
        bs = s + int(q8 * BEAT / 2 * SR); bl = int(BEAT / 2 * SR * 0.9); tq = np.arange(bl) / SR
        loop[bs:bs + bl] += np.tanh(2.0 * np.sin(2 * np.pi * root * 2 * tq)) * np.exp(-tq * 5) * 0.15
    for q16 in range(16):
        fq = triad[[0, 2, 1, 2, 0, 2, 1, 2, 0, 1, 2, 1, 0, 2, 1, 2][q16]] * 2; ps = s + int(q16 * BEAT / 4 * SR); pl = int(0.18 * SR); tq = np.arange(pl) / SR
        loop[ps:ps + pl] += np.sin(2 * np.pi * fq * tq) * np.exp(-tq * 18) * 0.045
for bt in range(16):
    ks = int(bt * BEAT * SR); kl = int(0.35 * SR); tq = np.arange(kl) / SR; fk = 48 + 95 * np.exp(-tq * 30)
    loop[ks:ks + kl] += np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tq * 9) * 0.5
    if bt % 2 == 1:
        cl = int(0.18 * SR); nz = rng.standard_normal(cl).astype(np.float32)
        loop[ks:ks + cl] += (nz - onepole(nz, 1500)) * np.exp(-np.arange(cl) / SR * 22) * 0.22
for h8 in range(32):
    hs = int(h8 * BEAT / 2 * SR); hl = int(0.05 * SR); nz = rng.standard_normal(hl).astype(np.float32)
    loop[hs:hs + hl] += np.diff(nz, prepend=0) * np.exp(-np.arange(hl) / SR * 80) * (0.08 if h8 % 2 else 0.05)
loop /= np.max(np.abs(loop)) + 1e-6
music = np.tile(loop, NS // NL + 2)[:NS] * 0.55 * mg

def whoosh(dd=0.5, up=True):
    x = rng.standard_normal(int(dd * SR)).astype(np.float32); out = np.zeros_like(x); y = 0.0
    for i in range(len(x)):
        p = i / len(x); fc = 300 + 5000 * (p if up else 1 - p); al = 1 - math.exp(-2 * math.pi * fc / SR); y += al * (x[i] - y); out[i] = y
    return out * np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2 * 0.9
WH, WHD = whoosh(0.45), whoosh(0.55, False)
def pop():
    t_ = tt(0.09); fq = 900 * np.exp(-t_ * 25) + 350; return (np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t_ * 45) * 0.6).astype(np.float32)
def boom():
    t_ = tt(0.8); fq = 90 * np.exp(-t_ * 4) + 40
    s = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t_ * 5); s[:300] += rng.standard_normal(300) * np.linspace(0.5, 0, 300); return (s * 0.9).astype(np.float32)
def ding():
    t_ = tt(0.9); return ((np.sin(2 * np.pi * 1320 * t_) + 0.4 * np.sin(2 * np.pi * 2640 * t_)) * np.exp(-t_ * 5) * 0.25).astype(np.float32)
def buzz():
    t_ = tt(0.45); return (np.sign(np.sin(2 * np.pi * 140 * t_)) * np.exp(-t_ * 4) * 0.18).astype(np.float32)
def riser(dd=1.0):
    t_ = tt(dd); fq = 200 + 1200 * (t_ / dd) ** 2
    return ((np.sin(2 * np.pi * np.cumsum(fq) / SR) * 0.15 + rng.standard_normal(len(t_)) * 0.08) * (t_ / dd) ** 2).astype(np.float32)
def swoop(dd=0.8):
    t_ = tt(dd); fq = 600 * np.exp(-t_ * 3.5) + 60; s = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t_ * 2.5) * 0.35
    m = min(len(s), len(WHD)); s[:m] += WHD[:m] * 0.4; return s.astype(np.float32)
POP, BOOM, DING, BUZZ = pop(), boom(), ding(), buzz()
sfx = np.zeros(NS, np.float32); cues = []
def cue(name, sig, at, g):
    o = int(at * SR)
    if o < 0: sig = sig[-o:]; o = 0
    m = min(len(sig), NS - o)
    if m > 0: sfx[o:o + m] += sig[:m] * g
    cues.append((round(at, 2), name))
cue("swoop (hook slow-mo)", swoop(), 0.0, 0.5); cue("ding (BETUL)", DING, 0.8, 0.6); cue("buzz (SALAH)", BUZZ, 1.2, 0.7)
cue("riser (hook title)", riser(0.9), HOOK_N / FPS - 0.9, 0.5); cue("boom (hook title)", BOOM, HOOK_N / FPS, 0.8)
for seg in SEGS:
    t0 = seg["f0"] / FPS
    if seg["kind"] == "card": cue(f"whoosh+boom (card {seg['num']})", WH, t0 - 0.1, 0.4); cue(f"boom (card {seg['num']})", BOOM, t0 + 0.15, 0.6)
    if seg["kind"] == "demo":
        if seg["rate"] < 0.999: cue(f"slow-mo swoop ({seg['clip']})", swoop(), t0, 0.5)
        else: cue(f"whoosh ({seg['clip']})", WH, t0 - 0.1, 0.35)
        st = seg["extra"].get("stamp")
        if st: cue(f"{'ding' if st == 'BETUL' else 'buzz'} ({seg['clip']})", DING if st == "BETUL" else BUZZ, t0 + 0.45, 0.6)
for pan in PAN:
    cue(f"whoosh (panel {pan['title']})", WH, pan["t0"] - 0.1, 0.25)
    for ti, txt in pan["rows"]: cue(f"pop ({txt[:24]})", POP, ti, 0.55)
st0, _ = talk_span("5.0a"); cue("whoosh (zone bar)", WH, s2o("5.0a", 108.3) - 0.1, 0.3)
for seg in SEGS:
    if seg["kind"] == "recap":
        cue("whoosh (recap)", WHD, seg["f0"] / FPS - 0.1, 0.4)
        for r in range(5): cue(f"pop (recap {r + 1})", POP, seg["f0"] / FPS + 0.4 + 0.3 * r, 0.55)
    if seg["kind"] == "end": cue("whoosh (end)", WH, seg["f0"] / FPS - 0.1, 0.4); cue("boom (end)", BOOM, seg["f0"] / FPS + 0.2, 0.6)

def wr(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    ww = wave.open(path, "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((x * 32767).astype(np.int16).tobytes()); ww.close()
wr(os.path.join(OUT, "voice.wav"), voice); wr(os.path.join(OUT, "sfx.wav"), sfx); wr(os.path.join(OUT, "music.wav"), music)
name = "FINAL_ADEGAN5.mp4" if FINAL else "PREVIEW_ADEGAN5.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", os.path.join(OUT, "voice.wav"), "-i", os.path.join(OUT, "sfx.wav"),
                "-i", os.path.join(OUT, "music.wav"), "-filter_complex",
                # stronger clean-up of outdoor speech: wind rumble, broadband noise, gate between words
                "[1]highpass=f=110,lowpass=f=9000,afftdn=nf=-24:nt=w,agate=threshold=0.006:ratio=2:range=0.3:attack=5:release=200,"
                "acompressor=threshold=-20dB:ratio=3:attack=5:release=120,loudnorm=I=-16:TP=-1.5:LRA=9[v];"
                "[v][2][3]amix=inputs=3:normalize=0:duration=longest,alimiter=limit=0.95,apad[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", f"{DUR:.3f}",
                os.path.join(OUT, name)], check=True)
json.dump({"duration": DUR, "segments": [{k: v for k, v in s.items() if k in ("kind", "clip", "a", "b", "label", "pass", "num", "name")} |
           {"t0": round(s["f0"] / FPS, 2), "t1": round((s["f0"] + s["n"]) / FPS, 2)} for s in SEGS],
           "panels": [{"clip": p["clip"], "title": p["title"], "t0": round(p["t0"], 2), "t1": round(p["t1"], 2)} for p in PAN]},
          open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
print("wrote", os.path.join(OUT, name), f"{DUR:.2f}s")
