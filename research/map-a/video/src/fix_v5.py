"""MAP-A rationale video v5 with the study's four objectives added and the long holds trimmed
(final length 1:45). The original v5 picture and music are kept; an objectives segment in the
same style is inserted before "Twelve results, proven, then verified."

Run: python3 fix_v5.py v5.mp4 out.mp4
"""

import os
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "tools")))
import rationale_video as V  # noqa: E402

W, H, FPS = 1920, 1080, 30
INSERT_AT = 83.2                       # just before "Twelve results, proven, then verified."
INSERT_LEN = 12.4
KEEP = [(0.0, 16.5), (18.6, 37.7), (38.3, 83.2), None, (83.2, 88.0), (89.1, 89.8), (91.7, 93.2),
        (94.6, 96.8), (98.3, 101.1), (102.9, 103.0)]
MUSIC_FOR_INSERT = (70.8, 83.2)

CARDS = [((212, 165, 55), "Objective 1", "Timetable graph", "Routes by arrival, fare, and transfers within vehicle road limits"),
         ((205, 95, 40), "Objective 2", "Access and inequality", "Gini, Theil, and Palma across landmarks and towns"),
         ((165, 32, 48), "Objective 3", "Hospital mode", "Bed reports by e-mail; the nearest hospital with a free bed and the right care"),
         ((112, 22, 40), "Objective 4", "The MAP-A app", "Everything in one phone app, even offline")]
SUBS = [(0.25, 3.0, "Our first objective: route every trip by arrival, fare, and transfers."),
        (3.2, 6.0, "Second: measure who can reach what, and how unequal access is."),
        (6.2, 9.1, "Third: find the nearest hospital with a free bed and the right care."),
        (9.3, 12.1, "Fourth: put it all in one app that works even offline.")]


def frame_at(src, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.3f" % t, "-i", src, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)


def background(src):
    """Empty stage of the proof scene: per-pixel median over frames whose content moves around."""
    stack = np.stack([frame_at(src, t) for t in np.linspace(66.0, 85.5, 25)])
    med = np.median(stack, axis=0)
    # content is brighter than the stage, so the darkest value per pixel is the empty stage
    low = stack.min(axis=0)
    # the stage is a radial gradient: rebuild it from the darkest values at each radius
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot(xx - 870, yy - 540).astype(int) // 4
    stage = np.zeros((H, W, 3))
    m = xx < 1740
    for ch in range(3):
        prof = np.zeros(r.max() + 1)
        for k in range(r.max() + 1):
            v = low[..., ch][(r == k) & m & (yy < 860)]
            prof[k] = np.percentile(v, 30) if v.size else prof[k - 1]
        prof[:70] = prof[70]                      # dark cards sat at the centre; keep it flat there
        stage[..., ch] = prof[r]
    bg = np.where(m[..., None], stage, med).astype(np.uint8)
    return Image.fromarray(bg)


def subtitle(cv, text, a):
    lines = cv.wrap(text, 40, 1400, "Regular")
    lh = 52
    hh = lh * len(lines) + 30
    y1 = 1022
    y0 = y1 - hh
    wmax = max(V.font(40, "Regular").getlength(ln) for ln in lines)
    cv.rect((W / 2 - wmax / 2 - 26, y0, W / 2 + wmax / 2 + 26, y1), (6, 4, 5), 0.88 * a, 8)
    y = y0 + 13
    for ln in lines:
        cv.ctext(W / 2, y, ln, 40, V.WHITE, a, "Regular")
        y += lh


def render_insert(src, path):
    bg = background(src)
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                             "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    n = int(round(INSERT_LEN * FPS))
    for fi in range(n):
        t = fi / FPS
        cv = V.Canvas(bg)
        fade = min(V.prog(t, 0.0, 0.3), 1 - V.prog(t, INSERT_LEN - 0.3, 0.3))
        cv.ctext(W / 2 - 80, 170, "Four objectives", 64, V.WHITE, fade, "SerifBold")
        for i, (col, lab, head, body) in enumerate(CARDS):
            a = V.prog(t, SUBS[i][0] - 0.1, 0.45) * fade
            x0 = 120 + i * 395
            y0 = 300 + int(20 * (1 - V.ease(V.prog(t, SUBS[i][0] - 0.1, 0.45))))
            cv.rect((x0, y0, x0 + 365, y0 + 420), col, a, 6, outline=(255, 235, 200), width=2,
                    oalpha=0.9 * a if SUBS[i][0] <= t <= SUBS[i][1] + 0.2 else 0.25 * a)
            cv.text((x0 + 26, y0 + 24), lab, 24, (255, 240, 220), a, "Regular")
            cv.para((x0 + 26, y0 + 64), head, 38, 320, V.WHITE, a, "SerifBold", 1.15)
            cv.para((x0 + 26, y0 + 200), body, 26, 315, (255, 244, 230), a, "Regular", 1.3)
        for (s, e, txt) in SUBS:
            if s - 0.1 <= t <= e + 0.1:
                subtitle(cv, txt, min(V.prog(t, s - 0.1, 0.15), 1 - V.prog(t, e - 0.05, 0.15)))
        proc.stdin.write(cv.im.tobytes())
    proc.stdin.close()
    proc.wait()


def main():
    src, out = sys.argv[1:3]
    ins = out + ".insert.mp4"
    render_insert(src, ins)
    parts, labels = [], []
    k = 0
    for seg in KEEP:
        if seg is None:
            parts.append("[1:v]setpts=PTS-STARTPTS[v%d];"
                         "[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.25,afade=t=out:st=%.3f:d=0.25[a%d];"
                         % (k, MUSIC_FOR_INSERT[0], MUSIC_FOR_INSERT[1], INSERT_LEN - 0.25, k))
        else:
            s, e = seg
            d = e - s
            parts.append("[0:v]trim=%.3f:%.3f,setpts=PTS-STARTPTS[v%d];"
                         "[0:a]atrim=%.3f:%.3f,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=%.3f:d=0.03[a%d];"
                         % (s, e, k, s, e, max(0.0, d - 0.03), k))
        labels.append("[v%d][a%d]" % (k, k))
        k += 1
    fc = "".join(parts) + "".join(labels) + "concat=n=%d:v=1:a=1[v][a]" % k
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-i", ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-map_metadata", "-1", "-movflags", "+faststart", out],
                   check=True)
    os.remove(ins)
    print(out)


if __name__ == "__main__":
    main()
