"""Box-and-arrow diagrams for the conceptual frameworks (matplotlib)."""

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

PALETTE = {
    "blue": ("#EAF1FB", "#2E4F7E"),
    "orange": ("#FDEEDC", "#B4622A"),
    "green": ("#E7F4EA", "#2F7A45"),
    "red": ("#FBE7E7", "#9E2A2B"),
    "gray": ("#F2F2F2", "#555555"),
}


def draw(path, boxes, arrows, size=(10.0, 6.6), wrap=26, fontsize=8.6):
    """boxes: dict id -> (title, body, x, y, w, h, color); coordinates in figure units.
    arrows: list of (from_id, to_id) or (from_id, to_id, label)."""
    fig, ax = plt.subplots(figsize=size)
    ax.set_xlim(0, size[0])
    ax.set_ylim(0, size[1])
    ax.axis("off")
    plt.rcParams.update({"font.family": "serif", "font.serif": ["Liberation Serif", "Times New Roman"]})
    for bid, (title, body, x, y, w, h, color) in boxes.items():
        fill, edge = PALETTE[color]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=fill, ec=edge, lw=1.1))
        lines = []
        if title:
            lines.append(r"$\bf{%s}$" % title.replace(" ", r"\ "))
        if body:
            lines.extend(textwrap.wrap(body, wrap))
        ax.text(x + w / 2, y + h / 2, "\n".join(lines), ha="center", va="center",
                fontsize=fontsize, color="#1E1E1E", linespacing=1.25)
    for arr in arrows:
        a, b = arr[0], arr[1]
        label = arr[2] if len(arr) > 2 else None
        xa, ya, wa, ha = boxes[a][2:6]
        xb, yb, wb, hb = boxes[b][2:6]
        ca = (xa + wa / 2, ya + ha / 2)
        cb = (xb + wb / 2, yb + hb / 2)
        if abs(ca[1] - cb[1]) < 0.3:            # same row
            if cb[0] > ca[0]:
                p, q = (xa + wa, ca[1]), (xb, cb[1])
            else:
                p, q = (xa, ca[1]), (xb + wb, cb[1])
        elif cb[1] < ca[1]:                       # lower row
            p, q = (ca[0], ya), (cb[0], yb + hb)
        else:
            p, q = (ca[0], ya + ha), (cb[0], yb)
        ax.annotate("", xy=q, xytext=p,
                    arrowprops=dict(arrowstyle="-|>", color="#4A4A4A", lw=1.0,
                                    shrinkA=2, shrinkB=2))
        if label:
            ax.text((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + 0.08, label, ha="center",
                    fontsize=fontsize - 1, color="#4A4A4A", style="italic")
    fig.tight_layout(pad=0.2)
    fig.savefig(path, dpi=220)
    plt.close(fig)
