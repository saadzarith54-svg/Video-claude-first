"""Render a PREVIEW of the edit.  usage: python3 render.py SRC.mp4 TRANSCRIPT.json OUTDIR [--final]

Preview: 1280x720, CRF 26, "PREVIEW" tag.  Final (not run yet): same pipeline, CRF 18, no tag.
"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from edl import SEGMENTS, FOCUS_X, FOCUS_Y, CORRECTIONS, EVENTS

SRC, TRANSCRIPT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
FINAL = "--final" in sys.argv
W, H, FPS, SR = 1280, 720, 30, 48000
os.makedirs(OUT, exist_ok=True)

TEAL = (16, 143, 132)
TEAL_D = (8, 70, 66)
YEL = (255, 210, 63)
WHITE = (255, 255, 255)
F_XB = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_B = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
F_SB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

# ---------------------------------------------------------------- timeline
seg_frames, t = [], 0
for (lab, a, b, *_r) in SEGMENTS:
    n = int(round((b - a) * FPS))
    seg_frames.append((t, n))
    t += n
TOTAL = t
DUR = TOTAL / FPS

def src2out(ts):
    """Map a source time to output seconds (first segment containing it)."""
    for (lab, a, b, *_r), (f0, n) in zip(SEGMENTS, seg_frames):
        if a <= ts <= b:
            return f0 / FPS + (ts - a)
    return None

def seg_start_out(i):
    return seg_frames[i][0] / FPS

def seg_end_out(i):
    return (seg_frames[i][0] + seg_frames[i][1]) / FPS

def seg_index_of(label_prefix):
    return [i for i, s in enumerate(SEGMENTS) if s[0].startswith(label_prefix)]

E = {k: src2out(v) for k, v in EVENTS.items()}

# ---------------------------------------------------------------- captions
words = []
for s in json.load(open(TRANSCRIPT)):
    for w in s["words"]:
        txt = w["w"].strip()
        bare = txt.strip(",.?!")
        if bare in CORRECTIONS:
            txt = txt.replace(bare, CORRECTIONS[bare])
        if txt:
            words.append((txt, w["s"], w["e"]))

chunks = []  # (out_start, out_end, [(word, ws, we)], seg_idx)
for i, (lab, a, b, *_r) in enumerate(SEGMENTS):
    o0 = seg_start_out(i)
    ws = []
    for (txt, s, e) in words:
        if min(e, b) - max(s, a) > 0.08:
            s2, e2 = max(s, a), min(e, b)
            # whisper stretches the first word across leading silence: keep its tail only
            if e2 - s2 > 0.7:
                s2 = e2 - 0.55
            ws.append((txt, o0 + s2 - a, o0 + e2 - a))
    cur = []
    for w in ws:
        cur.append(w)
        if len(cur) >= 4 or w[0][-1] in ",.?!":
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    # tag segment index
    for c in chunks:
        if len(c) and not isinstance(c[-1], int):
            pass
cap = []
for ci, c in enumerate(chunks):
    st = c[0][1]
    en = c[-1][2] + 0.25
    if ci + 1 < len(chunks):
        en = min(en, chunks[ci + 1][0][1]) if chunks[ci + 1][0][1] > st else en
    cap.append((st, en, c))
HOOK_END = seg_end_out(0)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out_cubic(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_out_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def ease_in_cubic(x): x = clamp(x); return x ** 3

def anim_in_out(t, t_in, t_out, d_in=0.35, d_out=0.25):
    """progress 0..1 for enter, and fade factor for exit."""
    if t_in is None or t < t_in or t > t_out:
        return 0.0, 0.0
    p = (t - t_in) / d_in
    q = 1 - clamp((t - (t_out - d_out)) / d_out)
    return p, q

# ---------------------------------------------------------------- drawing helpers
def rrect(d, box, r, fill):
    d.rounded_rectangle(box, r, fill=fill)

def text_w(txt, f):
    return f.getlength(txt)

def draw_caption(d, t):
    hook = t < HOOK_END
    for (st, en, ws) in cap:
        if st <= t < en:
            f = font(F_XB, 62 if hook else 44)
            items = [(w[0].upper() if hook else w[0], w[1], w[2]) for w in ws]
            sp = f.getlength(" ")
            total = sum(f.getlength(x[0]) for x in items) + sp * (len(items) - 1)
            x = (W - total) / 2
            y = 520 if hook else 610
            pop = ease_out_back((t - st) / 0.18)
            y += (1 - pop) * 14
            for (wt, s, e) in items:
                active = s <= t < e + 0.05
                col = YEL if active else WHITE
                d.text((x, y), wt, font=f, fill=col + (255,), stroke_width=5 if hook else 4,
                       stroke_fill=(0, 0, 0, 255))
                x += f.getlength(wt) + sp
            return

def lower_third(d, t, t_in, t_out, name, tag="PEMBENTANG"):
    p, q = anim_in_out(t, t_in, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q)
    fN, fT = font(F_XB, 38), font(F_B, 20)
    wN = text_w(name, fN) + 48
    x0 = -wN + (wN + 40) * ease_out_cubic(p)
    y0 = 430
    rrect(d, (x0, y0, x0 + 150, y0 + 34), 8, YEL + (a,))
    d.text((x0 + 14, y0 + 5), tag, font=fT, fill=(20, 20, 20, a))
    rrect(d, (x0, y0 + 40, x0 + wN, y0 + 102), 10, TEAL + (int(235 * q),))
    d.rectangle((x0, y0 + 40, x0 + 8, y0 + 102), fill=YEL + (a,))
    d.text((x0 + 26, y0 + 49), name, font=fN, fill=WHITE + (a,))

def title_card(d, t, t_in, t_out):
    p, q = anim_in_out(t, t_in, t_out, 0.5, 0.3)
    if q <= 0: return
    a = int(255 * q)
    y = -140 + 180 * ease_out_back(p)
    f1, f2 = font(F_XB, 30), font(F_XB, 52)
    l1, l2 = "TUGASAN 3", "Latihan Sistematik: Lompat Jauh"
    w2 = text_w(l2, f2) + 64
    x0 = (W - w2) / 2
    rrect(d, (x0, y + 44, x0 + w2, y + 124), 14, TEAL + (int(240 * q),))
    w1 = text_w(l1, f1) + 36
    rrect(d, ((W - w1) / 2, y, (W + w1) / 2, y + 50), 10, YEL + (a,))
    d.text(((W - text_w(l1, f1)) / 2, y + 8), l1, font=f1, fill=(20, 20, 20, a))
    d.text((x0 + 32, y + 54), l2, font=f2, fill=WHITE + (a,))

def list_panel(d, t, side, header, t_header, t_out, items, active_by_time=True):
    """items: [(t_in, num, title, sub)]"""
    p, q = anim_in_out(t, t_header, t_out, 0.45, 0.3)
    if q <= 0: return
    a = int(255 * q)
    pw = 430
    x0 = W - pw - 36 if side == "right" else 36
    slide = (1 - ease_out_cubic(p)) * (pw + 60) * (1 if side == "right" else -1)
    x0 += slide
    y0 = 70
    fH, fN, fT, fS = font(F_XB, 30), font(F_XB, 34), font(F_B, 27), font(F_SB, 21)
    rrect(d, (x0, y0, x0 + pw, y0 + 58), 12, YEL + (a,))
    d.text((x0 + 22, y0 + 11), header, font=fH, fill=(20, 20, 20, a))
    y = y0 + 74
    shown = [it for it in items if it[0] is not None and t >= it[0]]
    for k, (ti, num, title, sub) in enumerate(items):
        if ti is None or t < ti: continue
        pi = ease_out_back((t - ti) / 0.35)
        is_active = (k == len(shown) - 1)
        h = 96 if sub else 70
        sc = 0.85 + 0.15 * pi
        bx0, bx1 = x0 + (1 - sc) * pw / 2, x0 + pw - (1 - sc) * pw / 2
        fill = TEAL if is_active else TEAL_D
        rrect(d, (bx0, y, bx1, y + h), 12, fill + (int(235 * q * clamp(pi)),))
        aa = int(a * clamp(pi))
        d.ellipse((bx0 + 14, y + h / 2 - 24, bx0 + 62, y + h / 2 + 24), fill=YEL + (aa,))
        d.text((bx0 + 38 - text_w(num, fN) / 2, y + h / 2 - 22), num, font=fN, fill=(20, 20, 20, aa))
        d.text((bx0 + 78, y + (12 if sub else 19)), title, font=fT, fill=WHITE + (aa,))
        if sub:
            d.text((bx0 + 78, y + 52), sub, font=fS, fill=(210, 240, 236, aa))
        y += h + 12

def badge(d, t, t_in, t_out, txt, x, y):
    p, q = anim_in_out(t, t_in, t_out, 0.3, 0.3)
    if q <= 0: return
    a = int(255 * q * clamp(p * 2))
    f = font(F_XB, 22)
    sc = ease_out_back(p)
    w = (text_w(txt, f) + 28) * sc
    rrect(d, (x, y, x + w, y + 38), 19, (220, 60, 50, a))
    if sc > 0.9:
        d.text((x + 14, y + 7), txt, font=f, fill=WHITE + (a,))

def outro(d, t, t_in, t_out):
    p, q = anim_in_out(t, t_in, t_out + 1, 0.4, 0.2)
    if p <= 0: return
    sc = ease_out_back(p)
    f = font(F_XB, int(96 * max(sc, 0.05)))
    txt = "JOM MULAKAN!"
    w = text_w(txt, f)
    d.text(((W - w) / 2, 250 - 48 * sc), txt, font=f, fill=YEL + (255,), stroke_width=6,
           stroke_fill=(0, 0, 0, 255))

def hook_tag(d, t, t_in, t_out):
    p, q = anim_in_out(t, t_in, t_out, 0.35, 0.2)
    if q <= 0: return
    a = int(255 * q)
    f = font(F_XB, 26)
    txt = "LOMPAT JAUH  •  TUGASAN 3"
    w = text_w(txt, f) + 36
    x = 40 - (1 - ease_out_cubic(p)) * (w + 60)
    rrect(d, (x, 40, x + w, 88), 10, (220, 60, 50, a))
    d.text((x + 18, 49), txt, font=f, fill=WHITE + (a,))

# ---------------------------------------------------------------- overlay schedule
OBJ_I = seg_index_of("Objektif")
ROLE_I = seg_index_of("Peranan")
OBJ_END = seg_end_out(OBJ_I[-1])
ROLE_END = seg_end_out(ROLE_I[-1])

def overlays(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hook_tag(d, t, E["hook_tag"], HOOK_END)
    lower_third(d, t, E["lt_amsyar"], seg_end_out(2), "Muhammad Amsyar Rasif")
    lower_third(d, t, E["lt_zarif"], seg_end_out(3), "Muhammad Zarif Rizwan")
    lower_third(d, t, E["lt_hatim"], seg_end_out(4), "Ahmad Hatim")
    title_card(d, t, E["title_card"], seg_end_out(5))
    list_panel(d, t, "right", "3 OBJEKTIF", E["obj_header"], OBJ_END, [
        (E["obj_1"], "1", "Kenal pasti keperluan", "fizikal acara lompat jauh"),
        (E["obj_2"], "2", "Reka latihan sistematik", "untuk memperbaiki teknik"),
        (E["obj_3"], "3", "Sesuai tahap pelajar", "& selamat dilaksanakan"),
    ])
    list_panel(d, t, "left", "PEMBAHAGIAN PERANAN", E["roles_header"], ROLE_END, [
        (E["role_amsyar"], "A", "Amsyar", "Penganalisis"),
        (E["role_zarif"], "Z", "Zarif", "Jurulatih Lapangan 1"),
        (E["role_hatim"], "H", "Hatim", "Jurulatih Lapangan 2"),
    ])
    badge(d, t, E["role_safety"], ROLE_END, "+ PEGAWAI KESELAMATAN", 36 + 78, 70 + 74 + 3 * 108 + 4)
    outro(d, t, E["outro"], DUR)
    draw_caption(d, t)
    if not FINAL:
        f = font(F_B, 18)
        d.text((W - 110, 14), "PREVIEW", font=f, fill=(255, 255, 255, 140))
    return img

# ---------------------------------------------------------------- video
def frames_for(a, n):
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", SRC, "-frames:v", str(n),
           "-vf", f"fps={FPS},scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    last = None
    for _ in range(n):
        buf = p.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            buf = last
        last = buf
        yield np.frombuffer(buf, np.uint8).reshape(H, W, 3)
    p.stdout.close(); p.wait()

def zoom(fr, focus, z):
    if z <= 1.001:
        return Image.fromarray(fr)
    cw, ch = W / z, H / z
    cx = clamp(FOCUS_X[focus], cw / 2, W - cw / 2)
    cy = clamp(FOCUS_Y, ch / 2, H - ch / 2)
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return Image.fromarray(fr).resize((W, H), Image.BICUBIC, box=box)

vid_path = os.path.join(OUT, "video.mp4")
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                        "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18" if FINAL else "26",
                        "-pix_fmt", "yuv420p", vid_path], stdin=subprocess.PIPE)
flash_t = seg_start_out(1)
fi = 0
for i, ((lab, a, b, focus, z0, z1), (f0, n)) in enumerate(zip(SEGMENTS, seg_frames)):
    for k, fr in enumerate(frames_for(a, n)):
        t = fi / FPS
        z = z0 + (z1 - z0) * (k / max(n - 1, 1))
        base = zoom(fr, focus, z).convert("RGBA")
        base.alpha_composite(overlays(t))
        out = base.convert("RGB")
        # white flash after hook + quick flash at outro
        for ft in (flash_t, E["outro"]):
            dt = t - ft
            if -0.03 <= dt < 0.2:
                out = Image.blend(out, Image.new("RGB", (W, H), WHITE), 0.85 * (1 - clamp(dt / 0.2)))
        # fade out last 0.4s
        if t > DUR - 0.4:
            out = Image.blend(out, Image.new("RGB", (W, H), (0, 0, 0)), clamp((t - (DUR - 0.4)) / 0.4))
        enc.stdin.write(out.tobytes())
        fi += 1
    print(f"seg {i+1}/{len(SEGMENTS)} {lab} done", flush=True)
enc.stdin.close(); enc.wait()

# ---------------------------------------------------------------- audio
src_wav = os.path.join(OUT, "src.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-ac", "2", "-ar", str(SR), src_wav], check=True)
wf = wave.open(src_wav)
A = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
voice = np.zeros((int(DUR * SR) + SR, 2), np.float32)
fade = int(0.012 * SR)
for (lab, a, b, *_r), (f0, n) in zip(SEGMENTS, seg_frames):
    s0 = int(a * SR); L = int(n / FPS * SR)
    chunk = A[s0:s0 + L].copy()
    env = np.ones(len(chunk), np.float32)
    env[:fade] = np.linspace(0, 1, fade); env[-fade:] = np.linspace(1, 0, fade)
    chunk *= env[:, None]
    o = int(f0 / FPS * SR)
    voice[o:o + len(chunk)] += chunk
voice = voice[:int(DUR * SR)]

rng = np.random.default_rng(7)
def tt(d): return np.arange(int(d * SR)) / SR
def whoosh(d=0.55, up=True):
    x = rng.standard_normal(int(d * SR)).astype(np.float32)
    # moving one-pole lowpass for a sweep
    out = np.zeros_like(x); y = 0.0
    for i in range(len(x)):
        p = i / len(x)
        fc = 300 + 5000 * (p if up else 1 - p)
        al = 1 - math.exp(-2 * math.pi * fc / SR)
        y += al * (x[i] - y); out[i] = y
    env = np.sin(np.pi * np.linspace(0, 1, len(out))) ** 2
    return out * env * 0.9
def pop():
    t_ = tt(0.09); f = 900 * np.exp(-t_ * 25) + 350
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 45) * 0.6).astype(np.float32)
def boom():
    t_ = tt(0.8); f = 90 * np.exp(-t_ * 4) + 40
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t_ * 5)
    s[:300] += rng.standard_normal(300) * np.linspace(0.5, 0, 300)
    return (s * 0.9).astype(np.float32)
def ding():
    t_ = tt(0.9)
    s = (np.sin(2 * np.pi * 1320 * t_) + 0.4 * np.sin(2 * np.pi * 2640 * t_)) * np.exp(-t_ * 5)
    return (s * 0.25).astype(np.float32)
def riser(d=1.0):
    t_ = tt(d); f = 200 + 1200 * (t_ / d) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + rng.standard_normal(len(t_)) * 0.08
    return (s * (t_ / d) ** 2).astype(np.float32)

sfx = np.zeros(len(voice), np.float32)
def place(sig, at, gain=1.0):
    if at is None: return
    o = int(at * SR)
    if o < 0: sig = sig[-o:]; o = 0
    m = min(len(sig), len(sfx) - o)
    if m > 0: sfx[o:o + m] += sig[:m] * gain

cues = []
def cue(name, sig, at, gain):
    place(sig, at, gain); cues.append((round(at, 2) if at is not None else None, name))
cue("boom (hook open)", boom(), 0.0, 0.7)
cue("whoosh (hook tag)", whoosh(0.4), E["hook_tag"] - 0.15, 0.35)
cue("riser into transition", riser(0.9), flash_t - 0.9, 0.6)
cue("boom + flash (cut to salam)", boom(), flash_t, 0.6)
for k in ("lt_amsyar", "lt_zarif", "lt_hatim"):
    cue(f"whoosh ({k})", whoosh(0.4), E[k] - 0.1, 0.3)
cue("whoosh down (title card)", whoosh(0.6, up=False), E["title_card"] - 0.15, 0.4)
cue("ding (title card)", ding(), E["title_card"] + 0.35, 0.8)
cue("whoosh (objektif panel)", whoosh(0.5), E["obj_header"] - 0.1, 0.35)
for k in ("obj_1", "obj_2", "obj_3"):
    cue(f"pop ({k})", pop(), E[k], 0.8)
cue("whoosh (peranan panel)", whoosh(0.5), E["roles_header"] - 0.1, 0.35)
for k in ("role_amsyar", "role_zarif", "role_hatim"):
    cue(f"pop ({k})", pop(), E[k], 0.8)
cue("ding (pegawai keselamatan)", ding(), E["role_safety"], 0.8)
cue("riser (outro)", riser(0.6), E["outro"] - 0.6, 0.6)
cue("boom (JOM MULAKAN)", boom(), E["outro"], 0.8)

def wr(path, x):
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32767).astype(np.int16).tobytes()); w.close()
wr(os.path.join(OUT, "voice.wav"), voice)
wr(os.path.join(OUT, "sfx.wav"), sfx)

name = "FINAL.mp4" if FINAL else "PREVIEW.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid_path,
                "-i", os.path.join(OUT, "voice.wav"), "-i", os.path.join(OUT, "sfx.wav"),
                "-filter_complex",
                "[1]highpass=f=90,afftdn=nf=-30,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,"
                "loudnorm=I=-16:TP=-1.5:LRA=9[v];[2]volume=0.9[s];[v][s]amix=inputs=2:normalize=0:duration=first[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                "-shortest", os.path.join(OUT, name)], check=True)
json.dump({"duration": DUR, "segments": [[s[0], s[1], s[2], seg_start_out(i), seg_end_out(i)]
           for i, s in enumerate(SEGMENTS)], "sfx": cues,
           "events_out": {k: (round(v, 2) if v is not None else None) for k, v in E.items()}},
          open(os.path.join(OUT, "timeline.json"), "w"), indent=1, ensure_ascii=False)
print("wrote", os.path.join(OUT, name), f"{DUR:.2f}s")
