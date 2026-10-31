#!/usr/bin/env python3
"""MCB chassis - main plate of LineaViper-X16, long sensor arms removed.

Same plate, holes, windows and motor tabs as the original (0.36 deg skew of
the original outline squared up). Front closed as a mirror of the back, so the
motor axle sits at the plate centre and the robot stands on its two wheels.
Mount the N20s on top (brackets on the original tab holes): the plate hangs
below the axle and keeps the centre of gravity low. Prints flat, no supports.

    pip install manifold3d numpy matplotlib && python3 mcb_chassis.py

Axes: X = axle, Y = forward, Z = up, origin = axle centre. Units: mm.
"""
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(48)

# ---- original LineaViper-X16 dimensions ----
T = 4.0                                   # plate thickness
W, L = 39.73, 25.68                       # body half-width (X), half-length (Y, back edge; front mirrored)
CX, CY = 7.73, 6.24                       # corner chamfer
TAB_X, TAB_Y0, TAB_Y1 = 44.8, -12.18, 13.83   # motor tabs (gearbox face at TAB_X)
BOARD = [(34.5, -19.89), (34.5, 18.06)]   # MCB holes d3.49, mirrored in X (69.0 x 37.95)
BOARD_D = 3.49
MOTOR = [(38.07, -8.55), (38.07, 8.55)]   # N20 bracket holes d2.69, mirrored in X (17.1 pitch)
MOTOR_D = 2.69
WIN = (5.5, 20.0, -16.48, 22.52)          # two windows: X in +-[5.5, 20], Y range
# ---- preview parts ----
MOT_W, MOT_H, MOT_L = 12, 10, 24          # N20
WHEEL_D, WHEEL_W, WHEEL_GAP = 34, 8, 1.5

half = [(W - CX, -L), (W, -L + CY), (W, TAB_Y0), (TAB_X, TAB_Y0), (TAB_X, TAB_Y1),
        (W, TAB_Y1), (W, L - CY), (W - CX, L)]
outline = half + [(-x, y) for x, y in reversed(half)]
cs = CrossSection([outline])
for x0, x1, y0, y1 in [(WIN[0], WIN[1], WIN[2], WIN[3]), (-WIN[1], -WIN[0], WIN[2], WIN[3])]:
    cs -= CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])
for pts, d in ((BOARD, BOARD_D), (MOTOR, MOTOR_D)):
    for x, y in pts:
        for s in (-1, 1):
            cs -= CrossSection.circle(d / 2).translate([s * x, y])
plate = Manifold.extrude(cs, T)

AXLE = T + MOT_H / 2                      # axle height above plate bottom (motors on top)
GROUND = AXLE - WHEEL_D / 2               # ground Z in plate coordinates


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def mx(m):
    return m + m.mirror([1, 0, 0])


motors = mx(box(TAB_X - MOT_L, TAB_X, -MOT_W / 2, MOT_W / 2, T, T + MOT_H))
wheels = mx(Manifold.cylinder(WHEEL_W, WHEEL_D / 2).rotate([0, 90, 0])
            .translate([TAB_X + WHEEL_GAP, 0, AXLE]))


def tris(m):
    mesh = m.to_mesh()
    return np.asarray(mesh.vert_properties)[:, :3][np.asarray(mesh.tri_verts)]


def normals(t):
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def write_stl(m, path):
    t = tris(m).astype("<f4")
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = normals(t), t
    with open(path, "wb") as f:
        f.write(b"mcb chassis".ljust(80, b" "))
        f.write(np.uint32(len(t)).tobytes())
        rec.tofile(f)


def render(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = np.array([0.3, -0.5, 0.8]) / np.linalg.norm([0.3, -0.5, 0.8])
    t, col = [], []
    for m, c in ((plate, (0.0, 0.47, 0.84)), (motors, (0.78, 0.78, 0.78)), (wheels, (0.22, 0.22, 0.22))):
        tt = tris(m)
        shade = 0.35 + 0.65 * np.clip(normals(tt) @ light, 0, 1)
        t.append(tt)
        col.append(np.array(c)[None] * shade[:, None])
    t, col = np.concatenate(t), np.concatenate(col)
    xw = TAB_X + WHEEL_GAP + WHEEL_W
    fig = plt.figure(figsize=(14, 5))
    for i, (el, az, title) in enumerate(((28, -55, "iso"), (90, -90, "top"),
                                         (0, 0, "side: only the wheels touch the ground"))):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(t, facecolors=col, linewidths=0))
        ax.plot([-xw, xw, xw, -xw, -xw], [-L, -L, L, L, -L], GROUND, "k-", lw=0.6)
        ax.set(xlim=(-xw, xw), ylim=(-L, L), zlim=(GROUND, AXLE + WHEEL_D / 2), title=title)
        ax.set_box_aspect((2 * xw, 2 * L, WHEEL_D))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, dpi=100)


if __name__ == "__main__":
    write_stl(plate, "mcb_chassis.stl")
    render("preview.png")
    bb = plate.bounding_box()
    print(f"bbox {bb[3]-bb[0]:.2f} x {bb[4]-bb[1]:.2f} x {bb[5]-bb[2]:.2f} mm, genus {plate.genus()}, "
          f"vol {plate.volume()/1000:.1f} cm3, ground clearance {-GROUND:.1f} mm, tris {len(tris(plate))}")
