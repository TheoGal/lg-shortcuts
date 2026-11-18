#!/usr/bin/env python3
"""Draw the tile icons: white symbols on coloured squares.

  python3 scripts/make-icons.py

Writes icon.png (80 px) and largeIcon.png (130 px) into each app folder, and the
README picture to docs/tiles.png. Needs Pillow and NumPy (pip install pillow numpy).

Icons are full squares, coloured to the edges: LG Home and launchers such as
Hearth give every tile their own rounded shape, and corners rounded in the icon
itself show up as notches or a second, mismatched curve. Only the README
picture is rounded here, since GitHub shows it as it is.
"""
import math

import numpy as np
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 4  # draw large, then shrink for smooth edges

DARK = (36, 29, 25)
YELLOW = (255, 196, 0)
WHITE = (255, 255, 255)
BLUE = (64, 168, 232)
PINK = (242, 106, 164)
DARK_PINK = (216, 51, 122)
NAVY = (4, 79, 160)
TEAL = (0, 163, 163)
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


STROKE = 0.045  # line weight as a share of the tile, as LG's own tiles (measured on a C3)
_stroke = STROKE  # the weight while drawing, before the symbol is scaled to size


def stroke(W):
    return max(2, round(W * _stroke))


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


# ---- Outline icons drawn on a 24-unit grid (the same symbols as Hearth's LG Home buttons) ----

GRID_SCALE = 0.84  # shrink the 24-unit symbols a little to sit like the other tiles


def grid(W):
    """Map 24-unit coordinates to the canvas, scaled about the centre."""
    k = GRID_SCALE * W / 24
    return lambda x, y: (W / 2 + (x - 12) * k, W / 2 + (y - 12) * k), k


def cap_line(d, points, colour, width):
    """Open polyline with rounded joins and ends."""
    d.line(points, fill=colour, width=width, joint='curve')
    r = width / 2
    for x, y in (points[0], points[-1]):
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)


def ring(d, centre, radius, colour, width):
    """Circle stroke centred on the radius (Pillow strokes inwards)."""
    x, y = centre
    R = radius + width / 2
    d.ellipse([x - R, y - R, x + R, y + R], outline=colour, width=width)


def box(d, p0, p1, radius, colour, width):
    """Rectangle stroke centred on its edge."""
    h = width / 2
    d.rounded_rectangle([p0[0] - h, p0[1] - h, p1[0] + h, p1[1] + h], radius=radius + h, outline=colour, width=width)


def bezier(p0, p1, p2, p3, n=24):
    return [tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t ** 2 * c + t ** 3 * e
                  for a, b, c, e in zip(p0, p1, p2, p3)) for t in (i / n for i in range(n + 1))]


def lg_account(size):
    """Person: head and shoulders."""
    im, d, W = canvas(size, NAVY)
    g, k = grid(W)
    w = stroke(W)
    ring(d, g(12, 8.5), 3.6 * k, WHITE, w)
    body = bezier(g(5, 19.5), g(6.2, 15.9), g(9, 14.2), g(12, 14.2)) + \
        bezier(g(12, 14.2), g(15, 14.2), g(17.8, 15.9), g(19, 19.5))[1:]
    cap_line(d, body, WHITE, w)
    return im


def lg_search(size):
    """Magnifier."""
    im, d, W = canvas(size, TEAL)
    g, k = grid(W)
    w = stroke(W)
    ring(d, g(10.5, 10.5), 6 * k, WHITE, w)
    cap_line(d, [g(15, 15), g(20, 20)], WHITE, w)
    return im


def lg_tv_guide(size):
    """Programme guide: a screen with a picture and listing lines."""
    im, d, W = canvas(size, DARK_PINK)
    g, k = grid(W)
    w = stroke(W)
    box(d, g(3.5, 5), g(20.5, 19), 1.2 * k, WHITE, w)
    box(d, g(6, 7.6), g(11, 11), 0, WHITE, w)
    for a, b in ((g(6, 13.6), g(18, 13.6)), (g(6, 16.2), g(18, 16.2)), (g(13.5, 8.4), g(18, 8.4))):
        cap_line(d, [a, b], WHITE, w)
    return im


# ---- Size every symbol like LG's own tiles ----

# Largest side of the symbol as a share of the tile, measured on LG's Live TV tile (C3):
# wide symbols 55%. Squarish ones a little smaller, so they don't look heavier.
WIDE, SQUARE = 0.55, 0.50


def symbol_mask(im):
    """The white symbol as an 8-bit mask, read off the solid background."""
    a = np.asarray(im.convert('RGB')).astype(float)
    bg = a[0, 0]
    ch = int(np.argmax(255 - bg))  # the channel with most room between background and white
    alpha = np.clip((a[..., ch] - bg[ch]) / max(1.0, 255 - bg[ch]), 0, 1)
    return Image.fromarray((alpha * 255).astype('uint8'), 'L'), tuple(int(v) for v in bg)


def fitted(draw, target):
    """Draw the tile, then scale its symbol so the largest side is `target` of the tile,
    with the stroke drawn heavier first so it ends up at STROKE after scaling."""
    global _stroke

    def render(size, weight):
        global _stroke
        _stroke = weight
        try:
            im = draw(size)
        finally:
            _stroke = STROKE
        mask, bg = symbol_mask(im)
        box = mask.point(lambda v: 255 if v > 32 else 0).getbbox()
        return im, mask, bg, box

    def wrapped(size):
        im, mask, bg, box = render(size, STROKE)
        W = im.size[0]
        f = target * W / max(box[2] - box[0], box[3] - box[1])
        im, mask, bg, box = render(size, STROKE / f)  # redraw with the compensated weight
        f = target * W / max(box[2] - box[0], box[3] - box[1])
        sym = mask.crop(box)
        sym = sym.resize((max(1, round(sym.size[0] * f)), max(1, round(sym.size[1] * f))), Image.LANCZOS)
        out = Image.new('RGBA', (W, W), bg + (255,))
        out.paste(Image.new('RGBA', sym.size, WHITE + (255,)), (round((W - sym.size[0]) / 2), round((W - sym.size[1]) / 2)), sym)
        return out
    return wrapped


def save(draw, folder):
    for size, name in ((80, 'icon.png'), (130, 'largeIcon.png')):
        im = draw(size)
        im.resize((size, size), Image.LANCZOS).save(ROOT / folder / name, optimize=True)


def main():
    tiles = [(fitted(lg_settings, SQUARE), 'lgsettings'), (fitted(lg_quick_settings, SQUARE), 'lgquicksettings'),
             (fitted(lg_notifications, SQUARE), 'lgnotifications'), (fitted(lg_live_tv, WIDE), 'lglivetv'),
             (fitted(lg_account, SQUARE), 'lgaccount'), (fitted(lg_search, SQUARE), 'lgsearch'),
             (fitted(lg_tv_guide, WIDE), 'lgtvguide')]
    for draw, folder in tiles:
        save(draw, 'apps/' + folder)
    # README picture: all tiles in a row, rounded as a launcher shows them.
    size, gap = 128, 24
    row = Image.new('RGBA', (len(tiles) * size + (len(tiles) - 1) * gap, size), (0, 0, 0, 0))
    for i, (draw, _) in enumerate(tiles):
        row.paste(rounded(draw(size)).resize((size, size), Image.LANCZOS), (i * (size + gap), 0))
    row.save(ROOT / 'docs/tiles.png', optimize=True)
    print('icons written')


if __name__ == '__main__':
    main()
