"""Procedural long-jump (lompat jauh) animation drawn with PIL.

draw_longjump(d, t, box, alpha) draws one frame at local time t (seconds) into box=(x0,y0,w,h).
Timeline: run 0-RUN, flight RUN-LAND, sand + measurement after LAND.  DURATION = full action.
"""
import math
import numpy as np

RUN, LAND, DURATION = 1.3, 2.1, 3.2
TEAL = (16, 143, 132)
YEL = (255, 210, 63)
WHITE = (255, 255, 255)
SAND = (233, 200, 140)
TRACK = (196, 78, 52)

_rng = np.random.default_rng(3)
_PART = [(_rng.uniform(-0.9, 0.5), _rng.uniform(0.6, 1.6), _rng.uniform(0.5, 1.0)) for _ in range(26)]


def _smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def _lerp(a, b, p):
    return {k: a[k] + (b[k] - a[k]) * p for k in a}


# poses: lean (torso, + = forward), thighs/shins/arms as angles from straight-down (+ = forward)
TAKEOFF = dict(lean=0.15, th1=1.3, sh1=0.2, th2=-0.5, sh2=-0.7, ua1=2.4, fa1=2.6, ua2=-0.6, fa2=-0.2)
SAIL = dict(lean=0.0, th1=0.4, sh1=-0.5, th2=0.1, sh2=-0.7, ua1=2.9, fa1=3.0, ua2=2.7, fa2=2.9)
REACH = dict(lean=0.55, th1=1.55, sh1=1.45, th2=1.5, sh2=1.4, ua1=1.5, fa1=1.6, ua2=1.4, fa2=1.5)
LANDED = dict(lean=0.8, th1=1.2, sh1=0.25, th2=1.1, sh2=0.2, ua1=1.3, fa1=1.4, ua2=1.2, fa2=1.3)


def _run_pose(t):
    ph = 2 * math.pi * 1.7 * t
    pose = dict(lean=0.28)
    for i, off in ((1, 0.0), (2, math.pi)):
        f = ph + off
        th = 0.8 * math.sin(f)
        pose[f"th{i}"] = th
        pose[f"sh{i}"] = th - 1.2 * (0.5 - 0.5 * math.cos(f + 0.7))
        ua = -0.9 * math.sin(f)
        pose[f"ua{i}"] = ua
        pose[f"fa{i}"] = ua + 1.3
    return pose, abs(math.sin(ph))


def _pt(p, ang, L, up=False):
    if up:
        return (p[0] + L * math.sin(ang), p[1] - L * math.cos(ang))
    return (p[0] + L * math.sin(ang), p[1] + L * math.cos(ang))


def _figure(d, hip, pose, S, a):
    lw = max(3, int(S * 0.055))
    torso_w = max(4, int(S * 0.11))
    neck = _pt(hip, pose["lean"], S * 0.32, up=True)
    sh = _pt(hip, pose["lean"], S * 0.28, up=True)
    head = _pt(hip, pose["lean"], S * 0.42, up=True)
    limbs = []
    for i in (2, 1):  # far limbs first
        knee = _pt(hip, pose[f"th{i}"], S * 0.25)
        foot = _pt(knee, pose[f"sh{i}"], S * 0.25)
        elb = _pt(sh, pose[f"ua{i}"], S * 0.17)
        hand = _pt(elb, pose[f"fa{i}"], S * 0.16)
        col = (200, 200, 200, a) if i == 2 else WHITE + (a,)
        limbs.append(([hip, knee, foot], col))
        limbs.append(([sh, elb, hand], col))
    for pts, col in limbs[:2]:
        d.line(pts, fill=col, width=lw, joint="curve")
        for q in pts:
            d.ellipse((q[0] - lw / 2, q[1] - lw / 2, q[0] + lw / 2, q[1] + lw / 2), fill=col)
    d.line([hip, neck], fill=TEAL + (a,), width=torso_w)
    for q in (hip, neck):
        d.ellipse((q[0] - torso_w / 2, q[1] - torso_w / 2, q[0] + torso_w / 2, q[1] + torso_w / 2), fill=TEAL + (a,))
    for pts, col in limbs[2:]:
        d.line(pts, fill=col, width=lw, joint="curve")
        for q in pts:
            d.ellipse((q[0] - lw / 2, q[1] - lw / 2, q[0] + lw / 2, q[1] + lw / 2), fill=col)
    r = S * 0.075
    d.ellipse((head[0] - r, head[1] - r, head[0] + r, head[1] + r), fill=WHITE + (a,))


def draw_longjump(d, t, box, alpha=255, font=None, label="LEBIH JAUH!"):
    x0, y0, w, h = box
    a = int(alpha)
    gy = y0 + h * 0.70
    S = h * 0.38
    bx = x0 + w * 0.42           # take-off board
    px0, px1 = x0 + w * 0.47, x0 + w * 0.97
    # ground
    d.rectangle((x0 + w * 0.02, gy, bx, gy + h * 0.07), fill=TRACK + (a,))
    d.rectangle((bx - w * 0.012, gy, bx, gy + h * 0.07), fill=WHITE + (a,))
    d.rectangle((bx, gy, px0, gy + h * 0.07), fill=TRACK + (a,))
    d.rounded_rectangle((px0, gy - h * 0.01, px1, gy + h * 0.08), int(h * 0.03), fill=SAND + (a,))
    for k in range(6):  # runway lane marks
        lx = x0 + w * (0.05 + k * 0.06)
        d.line([(lx, gy + h * 0.035), (lx + w * 0.025, gy + h * 0.035)], fill=(240, 150, 120, a), width=2)

    land_x = x0 + w * 0.80
    hip_h = S * 0.5  # hip height above ground when standing
    trail = []
    if t < RUN:
        p = t / RUN
        hx = x0 + w * 0.06 + (bx - (x0 + w * 0.06)) * (p * (0.6 + 0.4 * p))  # accelerate
        pose, bob = _run_pose(t)
        hy = gy - hip_h - S * 0.04 * bob
        if p > 0.85:
            pose = _lerp(pose, TAKEOFF, _smooth((p - 0.85) / 0.15))
    elif t < LAND:
        p = (t - RUN) / (LAND - RUN)
        hx = bx + (land_x - bx) * p
        hy = gy - hip_h - h * 0.30 * 4 * p * (1 - p) + S * 0.15 * p * p
        pose = _lerp(TAKEOFF, SAIL, _smooth(p / 0.45)) if p < 0.45 else _lerp(SAIL, REACH, _smooth((p - 0.45) / 0.55))
        for k in range(1, 9):  # motion trail of the jump arc
            q = p * k / 9
            trail.append((bx + (land_x - bx) * q, gy - hip_h - h * 0.30 * 4 * q * (1 - q) + S * 0.15 * q * q))
    else:
        p = min(1.0, (t - LAND) / 0.25)
        hx = land_x + w * 0.02 * p
        hy = gy - hip_h + S * 0.15 + S * 0.12 * p
        pose = _lerp(REACH, LANDED, _smooth(p))
        for k in range(1, 12):
            q = k / 12
            trail.append((bx + (land_x - bx) * q, gy - hip_h - h * 0.30 * 4 * q * (1 - q) + S * 0.15 * q * q))

    # dotted arc trail
    ta = a if t < LAND else int(a * max(0.35, 1 - (t - LAND) / 1.2))
    for (tx, ty) in trail:
        r = max(2, S * 0.025)
        d.ellipse((tx - r, ty - r, tx + r, ty + r), fill=YEL + (ta,))

    _figure(d, (hx, hy), pose, S, a)

    if t >= LAND:  # sand burst
        st = t - LAND
        for (vx, vy, sz) in _PART:
            px = land_x + vx * w * 0.16 * min(st, 0.6) / 0.6
            py = gy - vy * h * 0.55 * st + h * 1.4 * st * st
            if py < gy + h * 0.02 and st < 0.8:
                r = sz * S * 0.05
                d.ellipse((px - r, py - r, px + r, py + r), fill=SAND + (int(a * (1 - st / 0.8)),))
        # landing mark
        d.ellipse((land_x - w * 0.012, gy - h * 0.005, land_x + w * 0.012, gy + h * 0.03), fill=(150, 110, 60, a))

    if t >= LAND + 0.3:  # measurement arrow board -> landing mark
        p = _smooth((t - LAND - 0.3) / 0.45)
        ay = gy + h * 0.12
        ex = bx + (land_x - bx) * p
        d.line([(bx, ay), (ex, ay)], fill=YEL + (a,), width=max(3, int(h * 0.012)))
        d.line([(bx, ay - h * 0.035), (bx, ay + h * 0.035)], fill=YEL + (a,), width=3)
        if p > 0.98:
            d.line([(land_x, ay - h * 0.035), (land_x, ay + h * 0.035)], fill=YEL + (a,), width=3)
        if font is not None and t >= LAND + 0.7 and label:
            q = min(1.0, (t - LAND - 0.7) / 0.2)
            tw = font.getlength(label)
            d.text(((bx + land_x) / 2 - tw / 2, ay + h * 0.03), label, font=font,
                   fill=YEL + (int(a * q),), stroke_width=3, stroke_fill=(0, 0, 0, int(a * q)))
