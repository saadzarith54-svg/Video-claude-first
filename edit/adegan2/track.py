"""Runner position in ADEGAN 2 jump clip (jump-clip seconds -> x,y in 1280x720)."""
import numpy as np

KEYS = [
    (0.00, 640, 360), (2.20, 1080, 340), (3.00, 1072, 330), (3.20, 1110, 320), (3.33, 1020, 340),
    (3.40, 980, 400), (3.53, 880, 410), (3.67, 840, 430), (3.73, 780, 430), (3.80, 740, 420),
    (3.87, 680, 380), (3.93, 560, 410), (4.00, 580, 400), (4.13, 500, 400), (4.20, 440, 450),
    (4.33, 400, 460), (4.40, 380, 470), (4.53, 300, 460), (5.90, 300, 460),
]
_T = np.array([k[0] for k in KEYS]); _X = np.array([k[1] for k in KEYS]); _Y = np.array([k[2] for k in KEYS])


def pos(t, smooth=0.12):
    # average over a small window to avoid jitter
    ts = np.linspace(t - smooth, t + smooth, 9)
    return float(np.interp(ts, _T, _X).mean()), float(np.interp(ts, _T, _Y).mean())
