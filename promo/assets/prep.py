"""Cut out brand/event assets (background removal) -> assets/*.png"""
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
import colorsys, sys
src = 'assets/src/'
def border_flood(mask):
    lab, n = ndimage.label(mask)
    edge = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    return np.isin(lab, list(edge))
def save(rgb, alpha, name, feather=1.2):
    a = Image.fromarray((alpha * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(feather))
    im = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); im.putalpha(a)
    bb = im.getbbox(); im = im.crop(bb); im.save('assets/' + name); print(name, im.size)

# 1) PERAH LAB logo: white background connected to border
im = np.asarray(Image.open(src + 'logo_perahlab.png').convert('RGB')).astype(float)
white = (im.min(2) > 232) & (im.max(2) - im.min(2) < 22)
bg = border_flood(white); bg = ndimage.binary_dilation(bg, iterations=1) & white | bg
save(im, 1 - bg, 'perahlab_logo.png', 1.0)

# 2) Poster: hand + cup (+ splashes), blue sky removed
im = np.asarray(Image.open(src + 'poster_orange_blast.png').convert('RGB')).astype(float)
crop = im[560:1398, 0:1000].copy()
r, g, b = crop[..., 0], crop[..., 1], crop[..., 2]
blue = (b > r + 55) & (b > g + 5) & (b > 150)
bg = border_flood(blue) | blue & (r < 70)
alpha = 1 - bg.astype(float)
alpha[140:260, 120:345] = np.where((r[140:260, 120:345] > 180) & (g[140:260, 120:345] < 120), 0, alpha[140:260, 120:345])  # drop tagline text
alpha[140:260, 120:345] = 0
# keep only big connected component(s): hand+cup, splashes, orange slice
lab, n = ndimage.label(alpha > .5); sizes = ndimage.sum(alpha > .5, lab, range(1, n + 1))
keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 600])
save(crop, keep.astype(float), 'cup_hand.png', 1.0)

# 3) HTK 26 logo: light-blue background
im = np.asarray(Image.open(src + 'logo_htk26.jpg').convert('RGB')).astype(float)
im = im[0:262, 120:440]
hsv = np.array([[colorsys.rgb_to_hsv(*(p / 255)) for p in row] for row in im])
bgm = (hsv[..., 1] < .30) & (hsv[..., 2] > .62) & (hsv[..., 0] > .45) & (hsv[..., 0] < .7) | ((hsv[..., 1] < .12) & (hsv[..., 2] > .7))
bg = border_flood(bgm)
save(im, 1 - bg, 'logo_htk26.png', 1.0)

# 4) IPG Perlis 10s logo: grey textured background
im = np.asarray(Image.open(src + 'logo_ipg10s.jpg').convert('RGB')).astype(float)
sat = im.max(2) - im.min(2); val = im.max(2)
bgm = (sat < 28) & (val > 150)
bg = border_flood(bgm)
save(im, 1 - bg, 'logo_ipg10s.png', 1.0)
