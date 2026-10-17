"""Math for the paper pipeline.

Display equations ($$ ... $$) are typeset by LaTeX (Times math) into PNG images,
the way equations appear in the sample papers. Inline math ($ ... $) becomes
ordinary formatted text: italic letters, Unicode symbols, and Pandoc sub- and
superscripts, so it renders the same in Word and in LibreOffice.
"""

import hashlib
import os
import re
import shutil
import subprocess
import tempfile

GREEK = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "epsilon": "ε", "varepsilon": "ε",
    "zeta": "ζ", "eta": "η", "theta": "θ", "vartheta": "ϑ", "iota": "ι", "kappa": "κ",
    "lambda": "λ", "mu": "μ", "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ", "sigma": "σ", "varsigma": "ς", "varrho": "ϱ", "varpi": "ϖ",
    "tau": "τ", "upsilon": "υ", "phi": "φ", "varphi": "φ", "chi": "χ", "psi": "ψ",
    "omega": "ω", "Gamma": "Γ", "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
}
SYMBOLS = {
    "le": "≤", "leq": "≤", "ge": "≥", "geq": "≥", "ne": "≠", "neq": "≠", "approx": "≈",
    "in": "∈", "notin": "∉", "subseteq": "⊆", "subset": "⊂", "supseteq": "⊇", "cup": "∪",
    "cap": "∩", "setminus": "∖", "times": "×", "cdot": "·", "infty": "∞", "sum": "∑",
    "prod": "∏", "to": "→", "rightarrow": "→", "Rightarrow": "⇒", "iff": "⇔",
    "leftarrow": "←", "mapsto": "↦", "emptyset": "∅", "varnothing": "∅", "ldots": "…",
    "dots": "…", "cdots": "⋯", "pm": "±", "mid": "|", "forall": "∀", "exists": "∃",
    "partial": "∂", "lfloor": "⌊", "rfloor": "⌋", "lceil": "⌈", "rceil": "⌉",
    "langle": "⟨", "rangle": "⟩", "prime": "′", "circ": "∘", "star": "⋆", "ast": "∗",
    "vee": "∨", "wedge": "∧", "neg": "¬", "lvert": "|", "rvert": "|", "|": "‖",
    "lbrace": "{", "rbrace": "}", "{": "{", "}": "}", "%": "%", "#": "#", "&": "&",
    "equiv": "≡", "sim": "∼", "propto": "∝", "ll": "≪", "gg": "≫", "preceq": "⪯",
    "succeq": "⪰", "prec": "≺", "succ": "≻", "lesssim": "≲", "Leftrightarrow": "⇔",
    "uparrow": "↑", "downarrow": "↓", "triangle": "△", "square": "□", "checkmark": "✓",
    "ell": "ℓ", "hbar": "ℏ", "aleph": "ℵ", "Re": "ℜ", "Im": "ℑ", "bullet": "•", "dagger": "†",
}
SPACED = {"le", "leq", "ge", "geq", "ne", "neq", "approx", "in", "notin", "subseteq", "subset",
          "supseteq", "cup", "cap", "setminus", "times", "to", "rightarrow", "Rightarrow", "iff",
          "leftarrow", "mapsto", "equiv", "propto", "preceq", "succeq", "prec", "succ", "sim",
          "Leftrightarrow", "pm", "ll", "gg", "lesssim"}
SPACES = {"quad": "  ", "qquad": "   ", ",": "", ";": " ", ":": " ",
          "!": "", " ": " ", "enspace": " ", "thinspace": ""}
UPRIGHT_FUNCS = {"max", "min", "log", "ln", "exp", "arg", "deg", "det", "sup", "inf", "lim",
                 "sin", "cos", "tan", "argmin", "argmax", "Pr", "diag", "rank", "tr", "sgn"}
ACCENTS = {"bar": "\u0304", "hat": "\u0302", "tilde": "\u0303", "dot": "\u0307",
           "overline": "\u0305", "widehat": "\u0302", "widetilde": "\u0303", "vec": "\u20d7"}


class Seg:
    __slots__ = ("text", "italic", "bold", "pos")

    def __init__(self, text, italic=False, bold=False, pos=0):
        self.text, self.italic, self.bold, self.pos = text, italic, bold, pos  # pos: 0, -1 sub, +1 sup


def _read_group(s, i):
    """s[i] is '{' -> return (content, index after matching '}')."""
    depth = 0
    j = i
    while j < len(s):
        if s[j] == "\\" and j + 1 < len(s):
            j += 2
            continue
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("unbalanced braces in: " + s)


def _read_arg(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return "", i
    if s[i] == "{":
        return _read_group(s, i)
    if s[i] == "\\":
        m = re.match(r"\\([A-Za-z]+|.)", s[i:])
        return m.group(0), i + len(m.group(0))
    return s[i], i + 1


def _parse(s, pos=0, italic_default=True, bold=False):
    segs = []
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\\":
            m = re.match(r"\\([A-Za-z]+|.)", s[i:])
            name = m.group(1)
            i += len(m.group(0))
            if name in GREEK:
                segs.append(Seg(GREEK[name], italic=italic_default and name[0].islower(), bold=bold, pos=pos))
            elif name in SYMBOLS:
                sym = SYMBOLS[name]
                if pos == 0 and name in SPACED:
                    sym = " %s " % sym
                segs.append(Seg(sym, bold=bold, pos=pos))
            elif name in SPACES:
                segs.append(Seg(SPACES[name], pos=pos))
            elif name in UPRIGHT_FUNCS:
                txt = {"argmin": "arg min", "argmax": "arg max"}.get(name, name)
                segs.append(Seg(txt, bold=bold, pos=pos))
            elif name in ("text", "mathrm", "operatorname", "textrm", "mathsf", "textup"):
                arg, i = _read_arg(s, i)
                if name == "text":
                    segs.append(Seg(arg.replace("\\ ", " "), bold=bold, pos=pos))
                else:
                    segs.extend(_parse(arg, pos, italic_default=False, bold=bold))
            elif name in ("textit", "mathit"):
                arg, i = _read_arg(s, i)
                segs.extend(_parse(arg, pos, italic_default=True, bold=bold))
            elif name in ("mathbf", "textbf", "boldsymbol", "bm"):
                arg, i = _read_arg(s, i)
                segs.extend(_parse(arg, pos, italic_default=(name in ("boldsymbol", "bm")), bold=True))
            elif name in ("mathcal", "mathscr"):
                arg, i = _read_arg(s, i)
                segs.extend(_parse(arg, pos, italic_default=True, bold=bold))
            elif name == "mathbb":
                arg, i = _read_arg(s, i)
                dbl = {"R": "ℝ", "N": "ℕ", "Z": "ℤ", "Q": "ℚ", "E": "𝔼", "P": "ℙ"}
                segs.append(Seg("".join(dbl.get(c, c) for c in arg), pos=pos))
            elif name in ACCENTS:
                arg, i = _read_arg(s, i)
                inner = _parse(arg, pos, italic_default, bold)
                if inner:
                    inner[-1].text += ACCENTS[name]
                segs.extend(inner)
            elif name in ("left", "right", "big", "Big", "bigl", "bigr", "Bigl", "Bigr",
                          "displaystyle", "textstyle", "limits", "nolimits"):
                pass
            elif name == "frac" or name == "tfrac" or name == "dfrac":
                a, i = _read_arg(s, i)
                b, i = _read_arg(s, i)
                segs.extend(_wrap_paren(_parse(a, pos, italic_default, bold), a, pos))
                segs.append(Seg("/", pos=pos))
                segs.extend(_wrap_paren(_parse(b, pos, italic_default, bold), b, pos))
            elif name == "sqrt":
                a, i = _read_arg(s, i)
                segs.append(Seg("√", pos=pos))
                segs.extend(_wrap_paren(_parse(a, pos, italic_default, bold), a, pos))
            elif name == "top":
                segs.append(Seg("T", pos=pos))
            else:
                raise ValueError("inline math: unknown command \\%s in %r" % (name, s))
        elif ch in "_^":
            arg, i = _read_arg(s, i + 1)
            newpos = -1 if ch == "_" else 1
            if arg in ("\\top",):
                segs.append(Seg("T", pos=newpos))
            elif arg in ("*", "\\ast", "\\star"):
                segs.append(Seg("*", pos=newpos))
            else:
                segs.extend(_parse(arg, newpos, italic_default, bold))
        elif ch == "{" :
            arg, i = _read_group(s, i)
            segs.extend(_parse(arg, pos, italic_default, bold))
        elif ch == "'":
            segs.append(Seg("′", pos=pos))
            i += 1
        elif ch.isalpha():
            segs.append(Seg(ch, italic=italic_default, bold=bold, pos=pos))
            i += 1
        elif ch == "-":
            segs.append(Seg("−", pos=pos))
            i += 1
        elif ch == " ":
            i += 1
        else:
            out = {"<": "<", ">": ">", "=": "=", "+": "+"}.get(ch, ch)
            if ch in "=<>+" and pos == 0:
                out = " %s " % out
            segs.append(Seg(out, bold=bold, pos=pos))
            i += 1
    return segs


def _wrap_paren(segs, src, pos):
    simple = len(src.strip()) <= 1 or re.fullmatch(r"[A-Za-z0-9]+|\\[A-Za-z]+", src.strip())
    if simple:
        return segs
    return [Seg("(", pos=pos)] + segs + [Seg(")", pos=pos)]


def _escape(t, in_script):
    out = []
    for c in t:
        if c in "\\*_[]`<>|~^#$":
            out.append("\\" + c)
        elif c == " " and in_script:
            out.append("\\ ")
        else:
            out.append(c)
    return "".join(out)


def _serialize(segs):
    # merge runs with identical formatting
    runs = []
    for sg in segs:
        if not sg.text:
            continue
        key = (sg.italic, sg.bold, sg.pos)
        if runs and runs[-1][0] == key:
            runs[-1][1].append(sg.text)
        else:
            runs.append((key, [sg.text]))
    out = []
    for (italic, bold, pos), parts in runs:
        txt = "".join(parts)
        if pos == 0:
            txt = re.sub(r" {2,}", " ", txt)
        core = _escape(txt, pos != 0)
        if pos != 0 and txt.strip() == "":
            continue
        if bold and italic:
            core = "***%s***" % core
        elif bold:
            core = "**%s**" % core
        elif italic:
            core = "*%s*" % core
        if pos == -1:
            core = "~%s~" % core
        elif pos == 1:
            core = "^%s^" % core
        out.append(core)
    s = "".join(out)
    return s.strip()


def inline_to_md(tex):
    return _serialize(_parse(tex))


# ---------------------------------------------------------------------------
# Display equations
# ---------------------------------------------------------------------------

PREAMBLE = r"""\documentclass[12pt]{article}
\usepackage{amsmath,amssymb}
\usepackage{mathptmx}
\usepackage{bm}
\pagestyle{empty}
\begin{document}
\thispagestyle{empty}
"""


def render_display(tex, eq_dir, dpi=300):
    os.makedirs(eq_dir, exist_ok=True)
    key = hashlib.sha1(tex.encode("utf-8")).hexdigest()[:16]
    png = os.path.join(eq_dir, "eq_%s.png" % key)
    if not os.path.exists(png):
        tmp = tempfile.mkdtemp()
        body = PREAMBLE + "\\[\n" + tex + "\n\\]\n\\end{document}\n"
        with open(os.path.join(tmp, "e.tex"), "w") as f:
            f.write(body)
        r = subprocess.run(["latex", "-interaction=nonstopmode", "e.tex"], cwd=tmp,
                           capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(os.path.join(tmp, "e.dvi")):
            raise RuntimeError("LaTeX failed for:\n%s\n%s" % (tex, r.stdout[-2000:]))
        subprocess.run(["dvipng", "-T", "tight", "-D", str(dpi), "-bg", "White", "-o",
                        os.path.join(tmp, "e.png"), "e.dvi"], cwd=tmp, check=True,
                       capture_output=True)
        shutil.copy(os.path.join(tmp, "e.png"), png)
        shutil.rmtree(tmp)
    from PIL import Image
    with Image.open(png) as im:
        wpx, hpx = im.size
    return png, wpx / dpi, hpx / dpi


def preprocess(md, eq_dir, max_width_in=5.7):
    """Replace $$..$$ with rendered images and $..$ with formatted text."""
    lines = md.split("\n")
    out = []
    in_code = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            out.append(line)
            i += 1
            continue
        if in_code:
            out.append(line)
            i += 1
            continue
        if line.strip().startswith("$$"):
            buf = [line.strip()[2:]]
            if not (line.strip().endswith("$$") and len(line.strip()) > 4):
                i += 1
                while i < len(lines) and not lines[i].strip().endswith("$$"):
                    buf.append(lines[i])
                    i += 1
                buf.append(lines[i].strip()[:-2])
            else:
                buf = [line.strip()[2:-2]]
            tex = "\n".join(buf).strip()
            png, wi, hi = render_display(tex, eq_dir)
            scale = min(1.0, max_width_in / wi)
            out.append('::: {custom-style="Equation Para"}')
            out.append("![](%s){width=%.3fin}" % (os.path.abspath(png), wi * scale))
            out.append(":::")
            i += 1
            continue
        out.append(_inline_line(line))
        i += 1
    return "\n".join(out)


def _inline_line(line):
    res = []
    j = 0
    while j < len(line):
        if line[j] == "$" and (j == 0 or line[j - 1] != "\\"):
            k = line.find("$", j + 1)
            if k < 0:
                res.append(line[j:])
                break
            res.append(inline_to_md(line[j + 1:k]))
            j = k + 1
        else:
            res.append(line[j])
            j += 1
    return "".join(res)
