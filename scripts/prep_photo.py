#!/usr/bin/env python3
"""
Prepare a photo or illustration for clean ASCII conversion:
  1. Remove background (rembg) to isolate the subject
  2. Bilateral-smooth away micro-textures while preserving sharp drawn edges
  3. Tone stretch over subject so skin lands bright and hair/lines stay dark
  4. Darken linework (difference-of-gaussians ridges) for crisp features
  5. Composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.
Usage:
    python scripts/prep_photo.py [input.jpg] [output.png] [--bust]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in sys.argv[1:] if not a.startswith("--")]
flags = [a for a in sys.argv[1:] if a.startswith("--")]

BUST_MODE = "--bust" in flags or "--avatar" in flags

INP = args[0] if len(args) > 0 else os.path.join(HERE, "..", "source-photo.jpg")
OUT = args[1] if len(args) > 1 else os.path.join(HERE, "..", "source-prepped.png")

LINE_WEIGHT = 0.65

# 1. Cut out subject
print(f"Isolating subject with AI background removal from {INP}...")
img = Image.open(INP).convert("RGBA")
cut = remove(img)
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

# 2. Smooth texture, keep edges
smooth = gray
for _ in range(3):
    smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

# 3. Tone stretch over subject only
mask_strong = alpha > 128
if np.any(mask_strong):
    lo, hi = np.percentile(smooth[mask_strong], [2, 92])
    tone = np.clip((smooth.astype(np.float32) - lo) / max(1.0, (hi - lo)), 0, 1)
else:
    tone = smooth.astype(np.float32) / 255.0

# 4. Difference of gaussians ridges
fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
lines = np.clip((coarse - fine) / 40.0, 0, 1)
out = np.clip(tone - LINE_WEIGHT * lines, 0, 1) * 255

# 5. Paste onto white
mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = out * mask + 255.0 * (1.0 - mask)

# Framing & Crop
ys, xs = np.where(alpha > 20)
if len(xs) == 0:
    ys, xs = np.where(alpha >= 0)

if BUST_MODE:
    # Focus on head, cowl and shoulders
    head_cx = (xs.min() + xs.max()) // 2
    head_cy = int(ys.min() + (ys.max() - ys.min()) * 0.38)
    side = int(min(out.shape[0], out.shape[1], (ys.max() - ys.min()) * 0.76))
    cx, cy = head_cx, head_cy
else:
    side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
    cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2

canvas = np.full((side, side), 255, np.uint8)
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
