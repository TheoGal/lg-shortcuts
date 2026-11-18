#!/usr/bin/env python3
"""Draw the four tile icons: white symbols on coloured squares.

  python3 scripts/make-icons.py

Writes icon.png (80 px) and largeIcon.png (130 px) into each app folder, and the
README picture to docs/tiles.png. Needs Pillow (pip install pillow).

Icons are full squares, coloured to the edges: LG Home and launchers such as
Hearth give every tile their own rounded shape, and corners rounded in the icon
itself show up as notches or a second, mismatched curve. Only the README
picture is rounded here, since GitHub shows it as it is.
"""
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 4  # draw large, then shrink for smooth edges

DARK = (36, 29, 25)
YELLOW = (255, 196, 0)
WHITE = (255, 255, 255)
BLUE = (64, 168, 232)
PINK = (236, 72, 140)
GREY = (118, 124, 134)
DARK_GREY = (72, 76, 84)


def canvas(size, background):
    W = size * SCALE
    im = Image.new('RGBA', (W, W), background + (255,))
    d = ImageDraw.Draw(im)
    return im, d, W


def rounded(im):
    """The README icon only: rounded corners, as a launcher would show it."""
    W = im.size[0]
    mask = Image.new('L', (W, W), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, W - 1, W - 1], radius=W // 5, fill=255)
    out = Image.new('RGBA', (W, W), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def stroke(W):
    return max(2, round(W * 0.055))


def outline(d, points, colour, width):
    """Closed outline with rounded joins."""
    d.line(points + points[:2], fill=colour, width=width, joint='curve')
    r = width / 2
    for x, y in points:
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def smooth(mask, r):
    """Round every corner of a 1-bit shape (blur, then threshold)."""
    return mask.filter(ImageFilter.GaussianBlur(r)).point(lambda v: 255 if v >= 128 else 0)


def odd(n):
    n = max(3, int(round(n)))
    return n if n % 2 else n + 1


def outline_of(mask, width):
    """A stroke centred on the edge of a shape."""
    grow = mask.filter(ImageFilter.MaxFilter(odd(width)))
    shrink = mask.filter(ImageFilter.MinFilter(odd(width)))
    return ImageChops.subtract(grow, shrink)


def paint(im, mask, colour):
    im.paste(Image.new('RGBA', im.size, colour + (255,)), (0, 0), mask)


def lg_gear_mask(W):
    """LG's settings gear: 6 short, wide, rounded teeth."""
    m = Image.new('L', (W, W), 0)
    d = ImageDraw.Draw(m)
    c = W / 2
    body, tip, tooth_w = W * 0.2, W * 0.285, W * 0.17
    d.ellipse([c - body, c - body, c + body, c + body], fill=255)
    for i in range(6):
        a = math.radians(i * 60 - 90)
        ux, uy = math.cos(a), math.sin(a)
        px, py = -uy, ux
        hw = tooth_w / 2
        d.polygon([(c + ux * r + px * t, c + uy * r + py * t) for r, t in
                   ((body * 0.7, -hw), (tip, -hw * 0.9), (tip, hw * 0.9), (body * 0.7, hw))], fill=255)
    return smooth(m, W * 0.018)


def lg_bell_mask(W):
    """LG's notifications bell: round dome, straight sides flaring to a rim."""
    m = Image.new('L', (W, W), 0)
    d = ImageDraw.Draw(m)
    c = W / 2
    r, top, side_bottom, rim = W * 0.165, W * 0.24, W * 0.6, W * 0.69
    d.ellipse([c - r, top, c + r, top + 2 * r], fill=255)
    d.rectangle([c - r, top + r, c + r, side_bottom], fill=255)
    d.polygon([(c - r, side_bottom - W * 0.02), (c + r, side_bottom - W * 0.02),
               (c + r + W * 0.08, rim), (c - r - W * 0.08, rim)], fill=255)
    return smooth(m, W * 0.012), rim


def live_tv(d, W, colour, background):
    w = stroke(W)
    c = W / 2
    # antenna
    d.line([(c - W * 0.12, W * 0.17), (c, W * 0.3), (c + W * 0.12, W * 0.17)], fill=colour, width=w, joint='curve')
    # screen
    d.rounded_rectangle([W * 0.16, W * 0.3, W * 0.84, W * 0.72], radius=W * 0.06, outline=colour, width=w)
    # stand
    d.line([(W * 0.36, W * 0.8), (W * 0.64, W * 0.8)], fill=colour, width=w)
    r = w / 2
    for x in (W * 0.36, W * 0.64):
        d.ellipse([x - r, W * 0.8 - r, x + r, W * 0.8 + r], fill=colour)
    # LIVE
    for name in ('DejaVuSans-Bold.ttf', 'Arial Bold.ttf', 'arialbd.ttf'):
        try:
            font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/' + name if name.startswith('DejaVu') else name,
                                      round(W * 0.15))
            break
        except OSError:
            font = None
    if font is None:
        font = ImageFont.load_default()
    box = d.textbbox((0, 0), 'LIVE', font=font)
    tw, th = box[2] - box[0], box[3] - box[1]
    d.text((c - tw / 2 - box[0], W * 0.51 - th / 2 - box[1]), 'LIVE', fill=colour, font=font)


def lg_settings(size):
    """Solid gear with the centre cut out."""
    im, d, W = canvas(size, GREY)
    hole = Image.new('L', (W, W), 0)
    h = W * 0.085
    ImageDraw.Draw(hole).ellipse([W / 2 - h, W / 2 - h, W / 2 + h, W / 2 + h], fill=255)
    paint(im, ImageChops.subtract(lg_gear_mask(W), hole), WHITE)
    return im


def lg_quick_settings(size):
    """Outlined gear with a ring in the middle."""
    im, d, W = canvas(size, DARK_GREY)
    w = stroke(W)
    paint(im, outline_of(lg_gear_mask(W), w), WHITE)
    h = W * 0.095
    d.ellipse([W / 2 - h, W / 2 - h, W / 2 + h, W / 2 + h], outline=WHITE + (255,), width=w)
    return im


def lg_notifications(size):
    im, d, W = canvas(size, BLUE)
    w = stroke(W)
    bell, rim = lg_bell_mask(W)
    paint(im, outline_of(bell, w), WHITE)
    r, cy = W * 0.065, rim + w * 0.45  # clapper
    d.arc([W / 2 - r, cy - r, W / 2 + r, cy + r], 0, 180, fill=WHITE + (255,), width=w)
    return im


def lg_live_tv(size):
    im, d, W = canvas(size, PINK)
    live_tv(d, W, WHITE, PINK)
    return im


def save(draw, folder):
    for size, name in ((80, 'icon.png'), (130, 'largeIcon.png')):
        im = draw(size)
        im.resize((size, size), Image.LANCZOS).save(ROOT / folder / name, optimize=True)


def main():
    tiles = [(lg_settings, 'lgsettings'), (lg_quick_settings, 'lgquicksettings'),
             (lg_notifications, 'lgnotifications'), (lg_live_tv, 'lglivetv')]
    for draw, folder in tiles:
        save(draw, 'apps/' + folder)
    # README picture: the four tiles in a row, rounded as a launcher shows them.
    size, gap = 128, 24
    row = Image.new('RGBA', (4 * size + 3 * gap, size), (0, 0, 0, 0))
    for i, (draw, _) in enumerate(tiles):
        row.paste(rounded(draw(size)).resize((size, size), Image.LANCZOS), (i * (size + gap), 0))
    row.save(ROOT / 'docs/tiles.png', optimize=True)
    print('icons written')


if __name__ == '__main__':
    main()
