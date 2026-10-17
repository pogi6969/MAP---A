"""Typeset the video's equations with LaTeX (latex + dvipng) as transparent PNGs.

Output: src/eq/<id>.png and src/eq/index.json ({id: {w, h, depth, em}}), where
em is the pixel size of 1 em (10 pt) in the PNG, so render.js can draw every
equation at a chosen em size in pixels.  Run:  python3 make_eqs.py
"""
import json
import os
import re
import shutil
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "eq")
DPI = 1100
INK = "F5F1E8"     # warm white
GOLD = "E8B23A"

EQS = {
    # MATHEMATICS
    "graph": r"G=(N,E),\qquad \tau_e\ \text{(minutes)},\qquad u_e\ \text{(persons per minute)}",
    "sigma": r"\sigma=(\text{active hazard zones},\ \text{closed bridges})",
    "demand": r"D_a(\sigma)\ \text{evacuees},\qquad V_a(\sigma)\ \text{vulnerable}",
    "cap": r"c_s=\left\lfloor \frac{A_s}{3.5\ \text{m}^2} \right\rfloor",
    "room": r"q=\left\lfloor \frac{7\ \text{m}\times 9\ \text{m}}{3.5\ \text{m}^2} \right\rfloor=\gold{18}",
    "rooms": r"K_s=\left\lceil \frac{y_s}{18} \right\rceil,\qquad L=\sum_s K_s\,\ell_s",
    # COMPUTING
    "cost": r"\mathrm{cost}(a,s,\iota)=T_\sigma(a,s)+M_O\,\mathbf{1}[\iota=1]+M_Y\,\mathbf{1}[\iota=2]",
    "flow": r"\sum_{s,\iota} x_{a,s\iota}\le D_a,\qquad \sum_{a} x_{a,s\iota}\le c^{\iota}_s,\qquad x\in\mathbb{Z}_{\ge 0}",
    "tstar": r"T^{*}_{\sigma}=\min\{\,T\ge 0 : F_\sigma(T)=D'\,\}",
    "lb": r"T^{*}\ \ge\ \tau_{\min}-1+\left\lceil D/c\right\rceil",
    # OPTIMISATION
    "lex": r"\max F_V\ \succ\ \max F\ \succ\ \min Y\ \succ\ \min O\ \succ\ \min \Theta",
    "pen": r"M_O=D\,T_{\max}+1,\qquad M_Y=D\,(M_O+T_{\max})+1",
    "fS": r"f(S)=\Phi_\theta(E\cup S)-\Phi_\theta(E)",
    "greedy": r"f(S_g)\ \ge\ \left(1-\tfrac{1}{e}\right) f(S^{*})\ \approx\ \gold{0.632}\,f(S^{*})",
    "submod": r"f(A\cup\{j\})-f(A)\ \ge\ f(B\cup\{j\})-f(B),\quad A\subseteq B",
    # small labels
    "K14": r"K=\gold{14}\ \text{not}\ 40",
    "Kq": r"K=\sum_s \left\lceil y_s/18 \right\rceil",
    # split pieces (highlighted one by one)
    "G": r"G=(N,E)",
    "tauu": r"\tau_e,\ \ u_e",
    "DV": r"D_a(\sigma),\ \ V_a(\sigma)",
    "xint": r"x\in\mathbb{Z}_{\ge 0}",
    "lexFV": r"\max F_V",
    "lexF": r"\max F",
    "lexY": r"\min Y",
    "lexO": r"\min O",
    "lexT": r"\min \Theta",
    "succ": r"\succ",
}

GROUPS = [["lexFV", "lexF", "lexY", "lexO", "lexT", "succ"]]

TEMPLATE = r"""\documentclass[10pt]{article}
\usepackage[paperwidth=9in,paperheight=1.6in,margin=0.25in]{geometry}
\usepackage{amsmath,amssymb}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\usepackage[HTML]{xcolor}
\newcommand{\gold}[1]{{\color[HTML]{%s}#1}}
\begin{document}
\color[HTML]{%s}
$\displaystyle %s$%%
\end{document}
"""


def main():
    from PIL import Image
    os.makedirs(OUT, exist_ok=True)
    index = {}
    raw = {}
    work = tempfile.mkdtemp(prefix="eq_", dir=os.environ.get("TMPDIR", "/tmp"))
    try:
        for key, tex in EQS.items():
            src = os.path.join(work, key + ".tex")
            grouped = any(key in g for g in GROUPS)
            if grouped:   # red strut rule fixes a common baseline band; cut away below
                tex = r"\textcolor[HTML]{FF0000}{\rule[-0.5em]{2pt}{1.6em}}\hspace{8pt}" + tex
            with open(src, "w") as f:
                f.write(TEMPLATE % (GOLD, INK, tex))
            subprocess.run(["latex", "-interaction=nonstopmode", "-halt-on-error", key + ".tex"],
                           cwd=work, check=True, stdout=subprocess.DEVNULL)
            png = os.path.join(work, key + ".png")
            subprocess.run(["dvipng", "-D", str(DPI), "-bg", "Transparent", "--truecolor",
                            "-o", png, key + ".dvi"], cwd=work, check=True, capture_output=True)
            im = Image.open(png).convert("RGBA")
            if grouped:
                import numpy as np
                a = np.array(im)
                red = (a[..., 0] > 200) & (a[..., 1] < 60) & (a[..., 2] < 60) & (a[..., 3] > 200)
                ys, xs = np.nonzero(red)
                ry0, ry1, rx1 = ys.min(), ys.max() + 1, xs.max() + 1
                a[:, :rx1 + 2, 3] = 0                      # erase the strut
                im = Image.fromarray(a)
                x0, _, x1, _ = im.getchannel("A").getbbox()
                raw[key] = (im, (x0, int(ry0), x1, int(ry1)))
            else:
                raw[key] = (im, im.getchannel("A").getbbox())
    finally:
        shutil.rmtree(work, ignore_errors=True)
    band = {}
    pad = 8
    for key, (im, (x0, y0, x1, y1)) in raw.items():
        if key in band:
            y0, y1 = band[key]
        im = im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))
        im.save(os.path.join(OUT, key + ".png"), optimize=True)
        index[key] = {"w": im.width, "h": im.height, "em": round(10 * DPI / 72.27, 3)}
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump(index, f, indent=1)
    print("typeset", len(index), "equations")


if __name__ == "__main__":
    main()
