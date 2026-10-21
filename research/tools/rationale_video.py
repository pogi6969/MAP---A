"""Rationale-video engine: draws every frame with Pillow, writes the music bed with NumPy,
and encodes with ffmpeg. The same timeline drives the burned-in subtitles and the
narration script, so the times in the script match the video exactly.

A project supplies a Spec: the scenes (narration cues, each with an on-screen note),
a draw function per scene, and the title-card text. See make_video.py in each
project's video/src folder.
"""

import json
import math
import os
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1920, 1080, 30
CRIMSON = (122, 16, 32)
DEEP = (30, 6, 12)
GOLD = (224, 169, 42)
GOLD_LT = (246, 210, 120)
WHITE = (255, 255, 255)
CREAM = (250, 244, 232)
INK = (24, 20, 22)
GREY = (170, 160, 160)
BLUE = (80, 150, 230)
GREEN = (70, 190, 120)
RED = (230, 70, 70)

INTER = "/usr/share/fonts/opentype/inter/Inter-%s.otf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
_fonts = {}


def font(size, weight="Regular"):
    key = (size, weight)
    if key not in _fonts:
        if weight == "SerifBold":
            path = SERIF_B
        elif weight == "Serif":
            path = SERIF_R
        else:
            path = INTER % weight
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def prog(t, start, dur):
    return ease((t - start) / dur) if dur > 0 else float(t >= start)


def back_out(x):
    x = clamp(x)
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def rgba(c, a):
    return (c[0], c[1], c[2], int(round(255 * clamp(a))))


# ---------------------------------------------------------------------------
# drawing helpers (all blend with alpha on an RGB canvas)

class Canvas:
    def __init__(self, base):
        self.im = base.copy()
        self.d = ImageDraw.Draw(self.im, "RGBA")

    def text(self, xy, s, size, color=WHITE, alpha=1.0, weight="Regular", anchor="la", spacing=6):
        if alpha <= 0.01:
            return
        self.d.text(xy, s, font=font(size, weight), fill=rgba(color, alpha), anchor=anchor, spacing=spacing)

    def ctext(self, cx, y, s, size, color=WHITE, alpha=1.0, weight="Regular"):
        self.text((cx, y), s, size, color, alpha, weight, anchor="ma")

    def rect(self, box, color, alpha=1.0, radius=0, outline=None, width=2, oalpha=None):
        if alpha <= 0.01 and outline is None:
            return
        fill = rgba(color, alpha) if alpha > 0.01 else None
        ol = rgba(outline, alpha if oalpha is None else oalpha) if outline else None
        if radius:
            self.d.rounded_rectangle(box, radius=radius, fill=fill, outline=ol, width=width)
        else:
            self.d.rectangle(box, fill=fill, outline=ol, width=width)

    def line(self, pts, color, alpha=1.0, width=3):
        if alpha > 0.01:
            self.d.line(pts, fill=rgba(color, alpha), width=width, joint="curve")

    def circle(self, c, r, color, alpha=1.0, outline=None, width=2):
        if alpha > 0.01:
            x, y = c
            self.d.ellipse((x - r, y - r, x + r, y + r), fill=rgba(color, alpha) if color else None,
                           outline=rgba(outline, alpha) if outline else None, width=width)

    def poly(self, pts, color, alpha=1.0, outline=None, width=2):
        if alpha > 0.01:
            self.d.polygon(pts, fill=rgba(color, alpha) if color else None,
                           outline=rgba(outline, alpha) if outline else None, width=width)

    def paste(self, img, xy, alpha=1.0, anchor="la"):
        if alpha <= 0.01:
            return
        x, y = xy
        w, h = img.size
        if anchor == "mm":
            x, y = x - w // 2, y - h // 2
        elif anchor == "ma":
            x = x - w // 2
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        mask = img.getchannel("A")
        if alpha < 0.999:
            mask = mask.point(lambda v: int(v * alpha))
        self.im.paste(img.convert("RGB"), (int(x), int(y)), mask)

    def wrap(self, s, size, maxw, weight="Regular"):
        f = font(size, weight)
        words, lines, cur = s.split(), [], ""
        for wd in words:
            test = (cur + " " + wd).strip()
            if f.getlength(test) <= maxw or not cur:
                cur = test
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, xy, s, size, maxw, color=WHITE, alpha=1.0, weight="Regular", lh=1.3, align="left"):
        x, y = xy
        for ln in self.wrap(s, size, maxw, weight):
            if align == "center":
                self.text((x, y), ln, size, color, alpha, weight, anchor="ma")
            else:
                self.text((x, y), ln, size, color, alpha, weight)
            y += int(size * lh)
        return y

    def card(self, box, alpha=1.0, color=CREAM, radius=22, shadow=True):
        if alpha <= 0.01:
            return
        if shadow:
            x0, y0, x1, y1 = box
            self.rect((x0 + 6, y0 + 10, x1 + 6, y1 + 10), (0, 0, 0), 0.25 * alpha, radius)
        self.rect(box, color, 0.96 * alpha, radius)

    def check(self, c, r, alpha=1.0, color=GREEN):
        x, y = c
        self.circle((x, y), r, color, alpha)
        self.line([(x - r * 0.45, y + r * 0.02), (x - r * 0.1, y + r * 0.38), (x + r * 0.5, y - r * 0.35)],
                  WHITE, alpha, max(3, int(r * 0.22)))


def cover(img, w, h):
    sw, sh = img.size
    s = max(w / sw, h / sh)
    img = img.resize((int(sw * s + 0.5), int(sh * s + 0.5)), Image.LANCZOS)
    x = (img.size[0] - w) // 2
    y = (img.size[1] - h) // 2
    return img.crop((x, y, x + w, y + h))


def make_background(seed=0):
    """Deep crimson-to-black gradient with a soft vignette and a faint grid."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(0.55 * (1 - yy / H) + 0.25 * (1 - xx / W), 0, 1)
    top = np.array(CRIMSON, np.float32) * 0.62
    bot = np.array(DEEP, np.float32)
    img = bot[None, None, :] * (1 - g[..., None]) + top[None, None, :] * g[..., None]
    r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
    img *= (1 - 0.45 * np.clip(r - 0.35, 0, 1))[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(im, "RGBA")
    for x in range(0, W, 96):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 7), width=1)
    for y in range(0, H, 96):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 7), width=1)
    return im


# ---------------------------------------------------------------------------
# LaTeX equations rendered white on transparent for dark slides

def latex_png(tex, path, dpi=300, color="1 1 1"):
    if os.path.exists(path):
        return Image.open(path)
    tmp = path + "_tmp"
    os.makedirs(tmp, exist_ok=True)
    doc = (r"\documentclass[12pt]{article}\usepackage{amsmath,amssymb,mathptmx,bm}\pagestyle{empty}"
           r"\begin{document}$\displaystyle %s$\end{document}" % tex)
    with open(os.path.join(tmp, "e.tex"), "w") as f:
        f.write(doc)
    subprocess.run(["latex", "-interaction=nonstopmode", "e.tex"], cwd=tmp, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["dvipng", "-D", str(dpi), "-T", "tight", "-bg", "Transparent", "-fg", "rgb " + color,
                    "-o", os.path.abspath(path), "e.dvi"], cwd=tmp, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=True)
    for fn in os.listdir(tmp):
        os.remove(os.path.join(tmp, fn))
    os.rmdir(tmp)
    return Image.open(path)


def scaled(img, height=None, width=None):
    w, h = img.size
    if height:
        s = height / h
    else:
        s = width / w
    return img.resize((max(1, int(w * s)), max(1, int(h * s))), Image.LANCZOS)


# ---------------------------------------------------------------------------
# timeline

def layout(scenes, wps=2.35, gap=0.55, lead=0.3, tail=0.8):
    """Give every cue a start and finish from its word count; scenes follow one another.
    A cue may carry 'hold' (seconds of silence after it) and 'pause' (silence before it)."""
    t = 0.0
    out = []
    for sc in scenes:
        s0 = t
        t += lead
        cues = []
        for c in sc["cues"]:
            t += c.get("pause", 0.0)
            words = len(c["text"].replace("[pause]", "").split())
            dur = max(1.2, words / wps)
            cues.append(dict(c, start=round(t, 2), end=round(t + dur, 2), words=words))
            t += dur + gap + c.get("hold", 0.0)
        t += tail + sc.get("extra", 0.0)
        out.append(dict(sc, start=round(s0, 2), end=round(t, 2), cues=cues))
    return out, t


def fmt_t(t):
    m = int(t // 60)
    s = t - 60 * m
    return "%d:%04.1f" % (m, s)


# ---------------------------------------------------------------------------
# subtitles

def draw_subtitle(cv, t, scenes):
    for sc in scenes:
        if sc["start"] <= t < sc["end"]:
            live = [c for c in sc["cues"] if c["start"] - 0.1 <= t <= c["end"] + 0.35]
            # when lines follow closely, show only the newest one
            for c in live[-1:]:
                a = min(prog(t, c["start"] - 0.1, 0.18), 1 - prog(t, c["end"] + 0.15, 0.2))
                txt = c["text"].replace("[pause] ", "").replace("[pause]", "")
                lines = cv.wrap(txt, 44, 1500, "SemiBold")
                hh = 44 * 1.28 * len(lines) + 34
                y0 = H - 70 - hh
                wmax = max(font(44, "SemiBold").getlength(ln) for ln in lines)
                cv.rect((W / 2 - wmax / 2 - 34, y0, W / 2 + wmax / 2 + 34, H - 70), (8, 4, 6), 0.72 * a, 18)
                y = y0 + 17
                for ln in lines:
                    cv.ctext(W / 2, y, ln, 44, WHITE, a, "SemiBold")
                    y += int(44 * 1.28)
            return


# ---------------------------------------------------------------------------
# title card

class TitleCard:
    def __init__(self, brand, title_lines, assets, duration=10.0):
        self.brand = brand
        self.lines = title_lines
        self.dur = duration
        bld = Image.open(assets["building"]).convert("RGB")
        bg = cover(bld, W, H)
        ov = Image.new("RGB", (W, H), (110, 12, 24))
        self.bg = Image.blend(bg, ov, 0.72)
        d = ImageDraw.Draw(self.bg, "RGBA")
        # white corner grid motif
        for (x0, y0, sx, sy) in ((W - 360, 40, 1, 1), (40, H - 300, 1, 1)):
            for i in range(5):
                d.line([(x0 + i * 64, y0), (x0 + i * 64, y0 + 256)], fill=(255, 255, 255, 60), width=2)
                d.line([(x0, y0 + i * 64), (x0 + 256, y0 + i * 64)], fill=(255, 255, 255, 60), width=2)
        seal = Image.open(assets["seal"]).convert("RGBA")
        self.seal = scaled(seal, height=170)

    def draw(self, t):
        """t from 0 to self.dur."""
        cv = Canvas(self.bg)
        cv.paste(self.seal, (60, 50), prog(t, 0.0, 0.8))
        letters = list(self.brand.replace("-", " - "))
        f = font(190, "SerifBold")
        widths = [f.getlength(ch) for ch in letters]
        total = sum(widths)
        x = W / 2 - total / 2
        y_final = 150
        hits = []
        for i, ch in enumerate(letters):
            st = 0.35 + 0.12 * i
            hits.append(st + 0.28)
            p = back_out((t - st) / 0.4)
            if t >= st:
                y = y_final - (1 - p) * 220
                cv.text((x, y), ch, 190, GOLD, clamp((t - st) / 0.2), "SerifBold")
            x += widths[i]
        # gold shine sweep across the brand
        shine = clamp((t - 2.0) / 0.9)
        if 0 < shine < 1:
            sx = W / 2 - total / 2 + shine * (total + 200) - 100
            cv.poly([(sx - 30, y_final + 10), (sx + 10, y_final + 10), (sx - 40, y_final + 200), (sx - 80, y_final + 200)],
                    (255, 245, 210), 0.35)
        y = 405
        for i, ln in enumerate(self.lines):
            cv.ctext(W / 2, y, ln, 46, WHITE, prog(t, 1.6 + 0.12 * i, 0.5), "SerifBold")
            y += 60
        # two thin lines drawing outward
        pl = prog(t, 2.6, 0.8)
        ly = y + 26
        cv.line([(W / 2 - 40 - 520 * pl, ly), (W / 2 - 40, ly)], WHITE, 0.9 * pl, 2)
        cv.line([(W / 2 + 40, ly), (W / 2 + 40 + 520 * pl, ly)], WHITE, 0.9 * pl, 2)
        cv.ctext(W / 2, ly + 34, "De Asis, Dave Justin Ll.", 62, GOLD, prog(t, 3.0, 0.6), "SerifBold")
        cv.ctext(W / 2, ly + 118, "LEAD RESEARCHER  ·  FOUNDER OF THE %s RESEARCH & APPLICATION" % self.brand,
                 25, GOLD_LT, prog(t, 3.4, 0.6), "SemiBold")
        cv.ctext(W / 2, ly + 172, "Brimbuela, Peter John A.     ·     Shin, Yeaseong", 38, WHITE,
                 prog(t, 3.9, 0.6), "Serif")
        fade = prog(t, self.dur - 1.0, 1.0)
        if fade > 0:
            cv.rect((0, 0, W, H), (0, 0, 0), fade)
        return cv.im, hits


# ---------------------------------------------------------------------------
# audio

SR = 48000


def _env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def music(total, mcs_start, boom_t, title_t, seed=7):
    rng = np.random.default_rng(seed)
    n = int(total * SR)
    out = np.zeros((n, 2))
    tt = np.arange(n) / SR
    # A minor progression: Am F C G (one chord per 4 s)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    seg = 4.0
    for k in range(int(total / seg) + 1):
        t0 = k * seg
        i0, i1 = int(t0 * SR), min(n, int((t0 + seg + 0.6) * SR))
        if i0 >= n:
            break
        loc = tt[i0:i1] - t0
        env = np.minimum(1, loc / 1.2) * np.exp(-np.maximum(0, loc - seg) * 3)
        sig = np.zeros(i1 - i0)
        for m in chords[k % 4]:
            f = hz(m)
            sig += np.sin(2 * np.pi * f * loc) * 0.5 + 0.18 * np.sin(2 * np.pi * 2 * f * loc + 0.3)
            sig += 0.25 * np.sin(2 * np.pi * (f * 1.003) * loc)
        sig += 0.6 * np.sin(2 * np.pi * hz(chords[k % 4][0] - 12) * loc)
        out[i0:i1, 0] += sig * env * 0.06
        out[i0:i1, 1] += sig * env * 0.06
    # arpeggio from the MCS scene to the boom
    step = 0.25
    t = mcs_start
    j = 0
    while t < boom_t - 0.3:
        k = int(t / seg) % 4
        notes = chords[k] + [chords[k][0] + 12]
        f = hz(notes[j % 4] + 12)
        i0 = int(t * SR)
        L = int(0.5 * SR)
        loc = np.arange(L) / SR
        build = 0.5 + 0.5 * clamp((t - mcs_start) / max(1, boom_t - mcs_start))
        pl = np.sin(2 * np.pi * f * loc) * np.exp(-loc * 7) * 0.05 * build
        pan = 0.5 + 0.35 * math.sin(j)
        i1 = min(n, i0 + L)
        out[i0:i1, 0] += pl[: i1 - i0] * (1 - pan)
        out[i0:i1, 1] += pl[: i1 - i0] * pan
        t += step
        j += 1
    # duck the bed under the conclusion and the title card, fade out at the end
    g = np.ones(n)
    g *= 1 - 0.35 * np.clip((tt - boom_t) / 0.5, 0, 1) * (tt < title_t)
    g *= np.clip((total - tt) / 2.0, 0, 1)
    out *= g[:, None]
    return out


def whoosh(out, t, dur=0.7, gain=0.10, seed=1):
    rng = np.random.default_rng(seed + int(t * 10))
    i0 = int(t * SR)
    L = int(dur * SR)
    if i0 >= len(out):
        return
    noise = rng.standard_normal(L)
    # crude band-pass by differencing a moving average
    k = 40
    sm = np.convolve(noise, np.ones(k) / k, mode="same")
    sig = noise - sm
    sig = np.convolve(sig, np.ones(6) / 6, mode="same")
    loc = np.arange(L) / L
    env = np.sin(np.pi * loc) ** 2
    s = sig * env * gain
    i1 = min(len(out), i0 + L)
    out[i0:i1, 0] += s[: i1 - i0] * (0.6 + 0.4 * loc[: i1 - i0])
    out[i0:i1, 1] += s[: i1 - i0] * (1.0 - 0.4 * loc[: i1 - i0])


def boom(out, t, gain=0.55):
    i0 = int(t * SR)
    L = int(3.0 * SR)
    loc = np.arange(L) / SR
    f = 52 * np.exp(-loc * 0.6) + 30
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-loc * 1.6) * gain
    rng = np.random.default_rng(3)
    s += rng.standard_normal(L) * np.exp(-loc * 18) * 0.12
    i1 = min(len(out), i0 + L)
    out[i0:i1, 0] += s[: i1 - i0]
    out[i0:i1, 1] += s[: i1 - i0]


def hit(out, t, gain=0.22):
    i0 = int(t * SR)
    L = int(0.6 * SR)
    loc = np.arange(L) / SR
    s = (np.sin(2 * np.pi * 110 * loc) * 0.7 + np.sin(2 * np.pi * 220 * loc) * 0.3) * np.exp(-loc * 9) * gain
    rng = np.random.default_rng(int(t * 100))
    s += rng.standard_normal(L) * np.exp(-loc * 60) * 0.08
    i1 = min(len(out), i0 + L)
    out[i0:i1, 0] += s[: i1 - i0]
    out[i0:i1, 1] += s[: i1 - i0]


def title_hits(brand):
    """Times (from the start of the title card) at which the brand letters land; matches TitleCard.draw."""
    return [0.35 + 0.12 * i + 0.28 for i in range(len(brand.replace("-", " - ")))]


def soundtrack(total, mcs_start, boom_t, title_t, scene_starts, brand):
    """Music bed and effects for the whole video (stereo, SR)."""
    aud = music(total, mcs_start, boom_t, title_t)
    for t in scene_starts[1:]:
        whoosh(aud, t - 0.35)
    whoosh(aud, title_t - 0.35, gain=0.12)
    boom(aud, boom_t)
    for h in title_hits(brand):
        hit(aud, title_t + h)
    return aud


def write_wav(path, data):
    data = np.clip(data, -1, 1)
    pcm = (data * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------------------
# render

def render(spec, out_dir, name, preview_every=None, only=None):
    """spec: object with .scenes (laid out), .total, .draw(cv, t, scene, local_t), .title (TitleCard),
    .mcs_start, .boom_t, .base (background image)."""
    os.makedirs(out_dir, exist_ok=True)
    total = spec.total
    title_t = spec.title_start
    nframes = int(round(total * FPS))
    tmp_video = os.path.join(out_dir, "_video_tmp.mp4")
    wav = os.path.join(out_dir, "_audio_tmp.wav")
    final = os.path.join(out_dir, name)
    proc = None
    if only is None:
        proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                                 "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                                 "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                                 tmp_video], stdin=subprocess.PIPE)
    title_hits = []
    frames = range(nframes) if only is None else only
    for fi in frames:
        t = fi / FPS
        if t >= title_t:
            img, hits = spec.title.draw(t - title_t)
            title_hits = hits
        else:
            cv = Canvas(spec.base)
            for sc in spec.scenes:
                if sc["start"] <= t < sc["end"]:
                    spec.draw(cv, t, sc, t - sc["start"])
                    # fades at scene edges
                    fin = 1 - prog(t, sc["start"], 0.35)
                    fout = prog(t, sc["end"] - 0.35, 0.35)
                    a = max(fin, fout)
                    if a > 0.01:
                        cv.rect((0, 0, W, H), (0, 0, 0), a)
                    break
            draw_subtitle(cv, t, spec.scenes)
            img = cv.im
        if proc:
            proc.stdin.write(img.tobytes())
        if only is not None:
            img.save(os.path.join(out_dir, "frame_%05d.png" % fi))
    if proc is None:
        return None
    proc.stdin.close()
    proc.wait()
    # audio
    aud = soundtrack(total, spec.mcs_start, spec.boom_t, title_t, [sc["start"] for sc in spec.scenes], spec.title.brand)
    write_wav(wav, aud)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_video, "-i", wav, "-c:v", "copy",
                    "-af", "loudnorm=I=-20:TP=-2:LRA=11", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-map_metadata", "-1", "-metadata", "title=", "-shortest", "-movflags", "+faststart", final],
                   check=True)
    os.remove(tmp_video)
    os.remove(wav)
    return final


def save_timeline(spec, path):
    data = {"total": round(spec.total, 2), "title_start": round(spec.title_start, 2), "boom": round(spec.boom_t, 2),
            "scenes": [{k: v for k, v in sc.items() if k != "draw"} for sc in spec.scenes]}
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    return data
