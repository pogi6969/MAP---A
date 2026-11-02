#!/usr/bin/env python3
"""Ball tower: 10 x 15 cm footprint, 10 cm tall, open top, one piece, prints without supports.

The robot's dump bin empties into it. The long (150 mm) side faces the robot. Stiff 1.2 mm
walls with rounded corners, 1.6 mm floor
with 4 countersunk screw holes: screw or tape it down - the robot pushes ~3 N against it and
the empty tower weighs only ~70 g, so friction alone (~0.2 N) would let it slide.

    pip install manifold3d numpy matplotlib && python3 tower.py
Units: mm.
"""
import os
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
X, Y, H = 100, 150, 100          # footprint, height
WALL, FLOOR, R = 1.2, 1.6, 8     # wall (3 lines), floor, corner radius
BALL_D = 40


def rrect(x, y, r):
    from manifold3d import JoinType
    return CrossSection.square([x - 2 * r, y - 2 * r], center=True).offset(r, JoinType.Round, circular_segments=48)


tower = Manifold.extrude(rrect(X, Y, R), H) - Manifold.extrude(rrect(X - 2 * WALL, Y - 2 * WALL, R - WALL), H).translate([0, 0, FLOOR])
for sx in (-1, 1):                                               # countersunk floor screw holes
    for sy in (-1, 1):
        cx, cy = sx * (X / 2 - 14), sy * (Y / 2 - 14)
        tower -= Manifold.cylinder(FLOOR + 2, 1.75).translate([cx, cy, -1])
        tower -= Manifold.cylinder(1.8, 1.75, 3.6).translate([cx, cy, FLOOR - 1.8 + 0.01])


def pile(n_max=200, h=H):
    """Drop balls one at a time into the lowest free spot; count those fully below the rim."""
    r, d = BALL_D / 2, BALL_D + 0.3
    U, V = (a.ravel() for a in np.meshgrid(np.arange(-X / 2 + WALL + r, X / 2 - WALL - r + 0.01, 1.0),
                                          np.arange(-Y / 2 + WALL + r, Y / 2 - WALL - r + 0.01, 1.0)))
    W = np.full(len(U), FLOOR + r)
    out = []
    while len(out) < n_max:
        i = np.argmin(W)
        if W[i] + r > h:
            break
        out.append((U[i], V[i], W[i]))
        d2 = (U - U[i]) ** 2 + (V - V[i]) ** 2
        near = d2 < d * d
        W[near] = np.maximum(W[near], W[i] + np.sqrt(d * d - d2[near]))
    return out


if __name__ == "__main__":
    from manifold3d import Mesh
    balls = pile()
    m = tower.to_mesh()
    t = np.asarray(m.vert_properties)[:, :3][np.asarray(m.tri_verts)].astype("<f4")
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]); rec["n"], rec["v"] = n, t
    with open(os.path.join(HERE, "ball_tower.stl"), "wb") as f:
        f.write(b"ball tower 100x150x100".ljust(80, b" ")); f.write(np.uint32(len(t)).tobytes()); rec.tofile(f)
    b = tower.bounding_box()
    print(f"tower {b[3]-b[0]:.1f} x {b[4]-b[1]:.1f} x {b[5]-b[2]:.1f} mm, {tower.volume()/1000:.1f} cm3 "
          f"(~{tower.volume()*1.27e-3:.0f} g PETG solid), genus {tower.genus()}; "
          f"holds {len(balls)} x {BALL_D} mm balls below the rim (one-by-one drop simulation); "
          f"30 would need {next(h for h in range(100, 400, 5) if len(pile(30, h)) >= 30)} mm height")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.3, -0.5, 0.8]); L /= np.linalg.norm(L)
    sp = sum((Manifold.sphere(BALL_D / 2, 20).translate(list(p)) for p in balls[1:]), Manifold.sphere(BALL_D / 2, 20).translate(list(balls[0])))
    fig = plt.figure(figsize=(12, 6))
    for k, (parts, title) in enumerate((([(tower, (0.95, 0.35, 0.1), 1)], "ball tower 10 x 15 x 10 cm"),
                                        ([(tower, (0.95, 0.35, 0.1), 0.25), (sp, (0.97, 0.97, 0.97), 1)], f"{len(balls)} balls fit"))):
        ax = fig.add_subplot(1, 2, k + 1, projection="3d")
        for mm, c, a in parts:
            tt = np.asarray(mm.to_mesh().vert_properties)[:, :3][np.asarray(mm.to_mesh().tri_verts)]
            nn = np.cross(tt[:, 1] - tt[:, 0], tt[:, 2] - tt[:, 0]); nn /= np.linalg.norm(nn, axis=1, keepdims=True) + 1e-12
            col = np.c_[np.array(c)[None] * (0.35 + 0.65 * np.clip(nn @ L, 0, 1))[:, None], np.full(len(tt), a)]
            ax.add_collection3d(Poly3DCollection(tt, facecolors=col, linewidths=0))
        ax.set(xlim=(-80, 80), ylim=(-80, 80), zlim=(0, 110), title=title); ax.set_box_aspect((160, 160, 110))
        ax.view_init(25, -60); ax.set_axis_off()
    fig.tight_layout(); fig.savefig(os.path.join(HERE, "preview.png"), dpi=90)
