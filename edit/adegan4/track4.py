"""Auto-track the moving person in a static-camera clip (median background subtraction).
usage: python3 track4.py CLIP OUT.json   -> list of [t, cx, cy, h] at 10 fps (1280x720 coords; h = bbox height)"""
import json, subprocess, sys
import numpy as np
clip, out = sys.argv[1], sys.argv[2]
W, H = 320, 180
p = subprocess.run(["ffmpeg", "-v", "error", "-i", clip, "-vf", f"fps=10,scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                   capture_output=True).stdout
fr = np.frombuffer(p, np.uint8).reshape(-1, H, W).astype(np.int16)
bg = np.median(fr[:: max(1, len(fr) // 60)], axis=0)
res = []
for i, f in enumerate(fr):
    m = np.abs(f - bg) > 28
    m[:int(H * 0.25)] = False  # ignore sky / trees swaying
    ys, xs = np.nonzero(m)
    if len(xs) < 25:
        res.append([i / 10, None, None, None]); continue
    # robust centre: take the biggest column cluster
    cx = np.median(xs); keep = np.abs(xs - cx) < 30
    xs, ys = xs[keep], ys[keep]
    if len(xs) < 10:
        res.append([i / 10, None, None, None]); continue
    res.append([i / 10, float(np.median(xs) * 4), float((ys.min() + ys.max()) / 2 * 4), float((ys.max() - ys.min()) * 4)])
json.dump(res, open(out, "w"))
ok = [r for r in res if r[1] is not None]
print(clip, len(res), "frames,", len(ok), "tracked")
