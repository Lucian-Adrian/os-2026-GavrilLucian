#!/usr/bin/env python3
"""Render a captured terminal transcript (text file) as a terminal-style PNG.
Usage: term2png.py evidence/x.txt assets/x.png
Lines starting with '$ ' are drawn as commands (green prompt)."""
import sys
from PIL import Image, ImageDraw, ImageFont
src, dst = sys.argv[1], sys.argv[2]
lines = open(src, encoding="utf-8").read().rstrip("\n").expandtabs(8).split("\n")
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 26)
cw = font.getbbox("M")[2]; lh = 34; pad = 24
w = pad * 2 + cw * max(40, max(len(l) for l in lines)); h = pad * 2 + lh * len(lines)
img = Image.new("RGB", (w, h), (30, 33, 41)); d = ImageDraw.Draw(img)
for i, l in enumerate(lines):
    y = pad + i * lh
    if l.startswith("$ "):
        d.text((pad, y), "$", font=font, fill=(110, 200, 120))
        d.text((pad + 2 * cw, y), l[2:], font=font, fill=(240, 240, 240))
    elif l.startswith("#") or l.startswith("=="):
        d.text((pad, y), l, font=font, fill=(150, 160, 180))
    else:
        d.text((pad, y), l, font=font, fill=(215, 220, 225))
img.save(dst)
