"""Writes the LIGTA-S logo variants as SVG (rendered to PNG by render_icons.cjs).

The mark: a gold shelter roof at the foot of a crimson volcano cone, with a teal
check mark for "ligtas" (safe) and "verified". Original artwork for this project.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def mark(scale=1.0, plume=True):
    """Foreground artwork in a 512 x 512 box, scaled about the centre."""
    s = scale
    t = (1 - s) * 256
    g = []
    g.append('<g transform="translate(%.2f %.2f) scale(%.4f)">' % (t, t, s))
    # volcano cone with concave flanks (a Mayon-like perfect cone), crimson with a lit flank
    g.append('<path d="M30 404 C150 372 214 262 234 118 L278 118 C298 262 362 372 482 404 Z" fill="#B81E28"/>')
    g.append('<path d="M258 118 L278 118 C298 262 362 372 482 404 L372 404 C318 332 270 236 258 118 Z" fill="#D9454A"/>')
    if plume:
        g.append('<g fill="#FFF5DE"><circle cx="270" cy="88" r="20"/><circle cx="304" cy="64" r="25"/>'
                 '<circle cx="344" cy="58" r="18"/></g>')
    # shelter: gold walls under a cream roof line
    g.append('<path d="M172 330 L256 264 L340 330 L340 440 L172 440 Z" fill="#F6D06B"/>')
    g.append('<path d="M134 344 L256 248 L378 344" fill="none" stroke="#FFF5DE" stroke-width="28" '
             'stroke-linecap="round" stroke-linejoin="round"/>')
    # teal check mark: safe and verified
    g.append('<path d="M206 380 L242 414 L306 342" fill="none" stroke="#0E7C74" stroke-width="30" '
             'stroke-linecap="round" stroke-linejoin="round"/>')
    g.append('</g>')
    return "".join(g)


BG = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
      '<stop offset="0" stop-color="#4A0A12"/><stop offset="1" stop-color="#1F0407"/></linearGradient></defs>')


def svg(variant):
    if variant == "rounded":      # favicon, website mark: rounded square, transparent corners
        body = '<rect x="8" y="8" width="496" height="496" rx="112" fill="url(#bg)"/>' + mark(1.0)
    elif variant == "square":     # icon-192/512 and apple-touch-icon: full bleed
        body = '<rect width="512" height="512" fill="url(#bg)"/>' + mark(0.94)
    elif variant == "maskable":   # content inside the 80% safe circle
        body = '<rect width="512" height="512" fill="url(#bg)"/>' + mark(0.72)
    elif variant == "small":      # 16-32 px: no plume, slightly larger artwork
        body = '<rect x="0" y="0" width="512" height="512" rx="104" fill="url(#bg)"/>' + mark(1.12, plume=False)
    else:
        raise ValueError(variant)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">'
            + BG + body + '</svg>')


for v in ("rounded", "square", "maskable", "small"):
    with open(os.path.join(HERE, "logo-%s.svg" % v), "w") as f:
        f.write(svg(v))
print("ok")
