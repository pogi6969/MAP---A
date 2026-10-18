"""Reusable pieces for the rationale videos: icons, the M-C-S reveal, the MCS chain,
panels, counters, proof marks and the closing lines."""

import math

from rationale_video import (BLUE, CREAM, CRIMSON, GOLD, GOLD_LT, GREEN, GREY, H, INK, RED, W, WHITE,
                             back_out, clamp, ease, font, prog)

# ---------------------------------------------------------------------------
# icons


def person(cv, x, y, s, color=WHITE, alpha=1.0, cane=False):
    cv.circle((x, y - 1.55 * s), 0.42 * s, color, alpha)
    cv.rect((x - 0.42 * s, y - 1.05 * s, x + 0.42 * s, y), color, alpha, int(0.3 * s))
    if cane:
        cv.line([(x + 0.7 * s, y - 0.8 * s), (x + 0.7 * s, y + 0.15 * s)], color, alpha, max(2, int(0.12 * s)))


def house(cv, x, y, s, alpha=1.0, color=CREAM, roof=CRIMSON):
    cv.rect((x - s, y - 1.2 * s, x + s, y), color, alpha, 4)
    cv.poly([(x - 1.25 * s, y - 1.15 * s), (x, y - 2.1 * s), (x + 1.25 * s, y - 1.15 * s)], roof, alpha)
    cv.rect((x - 0.25 * s, y - 0.65 * s, x + 0.25 * s, y), (90, 60, 40), alpha)


def school(cv, x, y, s, alpha=1.0, fill_frac=0.0, label=None):
    w, h = 3.2 * s, 1.6 * s
    cv.rect((x - w / 2, y - h, x + w / 2, y), CREAM, alpha, 6)
    cv.poly([(x - w / 2 - 0.2 * s, y - h), (x, y - h - 0.9 * s), (x + w / 2 + 0.2 * s, y - h)], CRIMSON, alpha)
    cv.line([(x, y - h - 0.9 * s), (x, y - h - 1.7 * s)], GREY, alpha, 3)
    cv.poly([(x, y - h - 1.7 * s), (x + 0.6 * s, y - h - 1.5 * s), (x, y - h - 1.3 * s)], BLUE, alpha)
    cols, rows = 6, 2
    k = 0
    for r in range(rows):
        for c in range(cols):
            wx = x - w / 2 + 0.25 * s + c * (w - 0.5 * s) / cols
            wy = y - h + 0.25 * s + r * 0.65 * s
            filled = k < fill_frac * cols * rows
            cv.rect((wx, wy, wx + 0.38 * s, wy + 0.42 * s), (240, 170, 60) if filled else (120, 160, 200), alpha, 3)
            k += 1
    if label:
        cv.ctext(x, y + 12, label, int(0.42 * s), WHITE, alpha, "SemiBold")


def volcano(cv, x, y, s, alpha=1.0, t=0.0, glow=0.0):
    cv.poly([(x - 3.2 * s, y), (x - 0.35 * s, y - 2.6 * s), (x + 0.35 * s, y - 2.6 * s), (x + 3.2 * s, y)],
            (70, 40, 45), alpha)
    cv.poly([(x - 0.35 * s, y - 2.6 * s), (x + 0.35 * s, y - 2.6 * s), (x + 0.9 * s, y - 1.9 * s),
             (x - 0.8 * s, y - 1.95 * s)], (110, 70, 70), alpha)
    if glow > 0:
        cv.circle((x, y - 2.6 * s), 0.5 * s, (255, 120, 40), alpha * glow * 0.5)
    for i in range(6):
        ph = (t * 0.25 + i / 6.0) % 1.0
        r = (0.25 + 0.6 * ph) * s
        cv.circle((x + math.sin(i * 2.1) * 0.4 * s + ph * 0.8 * s, y - 2.8 * s - ph * 2.2 * s), r, (200, 190, 190),
                  alpha * 0.35 * (1 - ph))


def mosquito(cv, x, y, s, alpha=1.0, t=0.0, color=(30, 30, 30)):
    flap = math.sin(t * 40) * 0.3
    cv.poly([(x, y), (x - 1.2 * s, y - (0.9 + flap) * s), (x - 0.2 * s, y - 0.2 * s)], (220, 230, 245), alpha * 0.7)
    cv.poly([(x, y), (x + 1.2 * s, y - (0.9 + flap) * s), (x + 0.2 * s, y - 0.2 * s)], (220, 230, 245), alpha * 0.7)
    cv.d.ellipse((x - 0.25 * s, y - 0.2 * s, x + 0.25 * s, y + 1.1 * s), fill=(color[0], color[1], color[2], int(255 * alpha)))
    cv.circle((x, y - 0.35 * s), 0.22 * s, color, alpha)
    cv.line([(x, y - 0.5 * s), (x, y - 1.0 * s)], color, alpha, 2)
    for k in (-1, 1):
        for j in range(3):
            cv.line([(x, y + 0.2 * s + j * 0.25 * s), (x + k * 0.9 * s, y + 0.5 * s + j * 0.35 * s)], color, alpha, 2)
    for j in range(3):
        cv.circle((x, y + 0.35 * s + j * 0.28 * s), 0.08 * s, WHITE, alpha)


def badge(cv, x, y, text, size, color, alpha=1.0, fg=WHITE, pad=18, anchor="m"):
    f = font(size, "Bold")
    w = f.getlength(text) + 2 * pad
    h = size + 2 * pad * 0.7
    x0 = x - w / 2 if anchor == "m" else x
    cv.rect((x0, y - h / 2, x0 + w, y + h / 2), color, alpha, int(h / 2))
    cv.text((x0 + w / 2, y - size * 0.62), text, size, fg, alpha, "Bold", anchor="ma")
    return w


def stamp(cv, x, y, text, alpha, size=54, color=RED, angle=-12):
    """A rotated rubber-stamp word drawn on its own layer."""
    from PIL import Image, ImageDraw
    f = font(size, "Black")
    tw = int(f.getlength(text)) + 60
    th = size + 50
    lay = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((4, 4, tw - 4, th - 4), radius=12, outline=color + (255,), width=6)
    d.text((tw / 2, th / 2), text, font=f, fill=color + (255,), anchor="mm")
    lay = lay.rotate(angle, expand=True, resample=Image.BICUBIC)
    sc = 1 + 0.6 * (1 - clamp(alpha * 1.5))
    if sc != 1:
        lay = lay.resize((int(lay.size[0] * sc), int(lay.size[1] * sc)), Image.BICUBIC)
    cv.paste(lay, (x, y), clamp(alpha * 1.5), anchor="mm")


def chip(cv, x, y, title, sub, alpha, color=GOLD, w=560):
    cv.card((x, y, x + w, y + 110), alpha, (25, 10, 14))
    cv.rect((x, y, x + 12, y + 110), color, alpha, 0)
    cv.text((x + 34, y + 16), title, 34, color, alpha, "Bold")
    cv.text((x + 34, y + 62), sub, 28, WHITE, alpha, "Regular")


# ---------------------------------------------------------------------------
# MCS pieces

WORDS = ["Mathematical", "Computational", "Sciences"]


def mcs_reveal(cv, lt, y=330, alpha=1.0):
    """M, C and S drop in side by side, then slide into a column and unfold into the three words."""
    letters = "MCS"
    xs = [W / 2 - 300, W / 2, W / 2 + 300]
    unfold = prog(lt, 1.3, 0.8)
    for i, ch in enumerate(letters):
        st = 0.1 + 0.25 * i
        p = back_out((lt - st) / 0.45)
        if lt < st:
            continue
        a = clamp((lt - st) / 0.15) * alpha
        size = int(230 - 90 * unfold)
        f = font(size, "Black")
        fw = f.getlength(ch)
        x_drop = xs[i] - fw / 2
        y_drop = y - (1 - p) * 260
        x_col = W / 2 - 520
        y_col = 170 + i * 175
        x = x_drop + (x_col - x_drop) * unfold
        yy = y_drop + (y_col - y_drop) * unfold
        cv.text((x, yy), ch, size, GOLD, a, "Black")
        if unfold > 0:
            rest = WORDS[i][1:]
            fw2 = font(size, "Black").getlength(ch)
            cv.text((x + fw2 + 6, yy + size * 0.80), rest, int(size * 0.62), WHITE, a * unfold, "Bold", anchor="ls")


def chain(cv, labels, lit, y=70, alpha=1.0):
    """A row of rounded labels joined by arrows; 'lit' (float) says how many are lit."""
    f = font(30, "Bold")
    widths = [f.getlength(s) + 52 for s in labels]
    gap = 46
    total = sum(widths) + gap * (len(labels) - 1)
    x = W / 2 - total / 2
    for i, s in enumerate(labels):
        on = clamp(lit - i)
        col = tuple(int(GOLD[k] * on + 70 * (1 - on)) for k in range(3))
        cv.rect((x, y, x + widths[i], y + 56), col, alpha * (0.35 + 0.65 * on), 28)
        cv.text((x + widths[i] / 2, y + 12), s, 30, (30, 12, 16) if on > 0.5 else WHITE, alpha, "Bold", anchor="ma")
        if i < len(labels) - 1:
            ax = x + widths[i] + 8
            on2 = clamp(lit - i - 1)
            cv.line([(ax, y + 28), (ax + gap - 16, y + 28)], GOLD if on2 > 0.5 else GREY, alpha, 4)
            cv.poly([(ax + gap - 16, y + 20), (ax + gap - 6, y + 28), (ax + gap - 16, y + 36)],
                    GOLD if on2 > 0.5 else GREY, alpha)
        x += widths[i] + gap


def panel(cv, box, title, alpha=1.0, color=GOLD):
    x0, y0, x1, y1 = box
    cv.rect((x0 + 6, y0 + 10, x1 + 6, y1 + 10), (0, 0, 0), 0.3 * alpha, 24)
    cv.rect(box, (22, 8, 12), 0.88 * alpha, 24, outline=color, width=3, oalpha=0.85 * alpha)
    cv.text((x0 + 30, y0 + 22), title, 34, color, alpha, "Black")


def proof_marks(cv, n, x, y, t, t0, step=0.22, size=46, label=None):
    """n proof squares (QED marks) that turn into green check marks one by one."""
    for i in range(n):
        st = t0 + i * step
        a = prog(t, st, 0.25)
        cx = x + i * (size + 22)
        if a <= 0:
            continue
        flip = prog(t, st + 0.5, 0.25)
        if flip < 1:
            cv.rect((cx - size / 2, y - size / 2, cx + size / 2, y + size / 2), WHITE, a * (1 - flip), 4)
        if flip > 0:
            cv.check((cx, y), size / 2 + 2, flip)
    if label:
        cv.text((x - size / 2, y + size / 2 + 20), label, 30, WHITE, prog(t, t0, 0.4), "SemiBold")


def counter(v, p, decimals=0):
    x = v * ease(p)
    if decimals:
        return ("{:,.%df}" % decimals).format(x)
    return "{:,}".format(int(round(x)))


def closing(cv, t, cue_a, cue_b, cue_c, line_a, line_b, line_c1, line_c2, end_t):
    """The three closing beats over a darkened screen: two statements, then the paired lines."""
    a1 = prog(t, cue_a - 0.2, 0.5) * (1 - prog(t, cue_b - 0.6, 0.4))
    cv.para((W / 2, 360), line_a, 70, 1500, WHITE, a1, "Bold", 1.2, "center")
    a2 = prog(t, cue_b - 0.2, 0.5) * (1 - prog(t, cue_c - 0.6, 0.4))
    cv.para((W / 2, 300), line_b, 62, 1500, GOLD, a2, "Bold", 1.25, "center")
    a3 = prog(t, cue_c - 0.1, 0.5)
    a4 = prog(t, cue_c + 2.6, 0.5)
    cv.para((W / 2, 300), line_c1, 64, 1600, WHITE, a3, "Bold", 1.2, "center")
    cv.para((W / 2, 470), line_c2, 64, 1600, GOLD, a4, "Bold", 1.2, "center")
