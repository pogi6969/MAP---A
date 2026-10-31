#!/usr/bin/env python3
"""MCB chassis (3D) - LineaViper-X16 main plate, long sensor arms removed.

Same plate, windows and motor tabs as the original (0.36 deg skew squared up),
front closed as a mirror of the back so the axle sits at the plate centre.
On top: two N20 cradles with gearbox face walls (M1.6 face screws), zip-tie
holes on the original bracket holes, and 4 short MCB posts (M3 self-tap) on the
original board holes, just above the motors. Motors on top keep the plate
below the axle, so it stands and drives on the two wheels only.
Prints flat side down, no supports.

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
# ---- 3D parts ----
MOT_W, MOT_H, MOT_L = 12, 10, 24          # N20 body (gearbox + can)
WALL_T, CRADLE_T, CRADLE_X0 = 2, 1.6, 21  # face wall, cradle walls, cradle inner end
SCREW_SP, SCREW_D, BOSS_D = 9, 1.8, 4.5   # N20 face: 2x M1.6 @ 9 mm, shaft boss
POST_D, PILOT, POST_GAP = 6.5, 2.6, 1.5   # MCB posts, M3 self-tap, clearance over motors
WHEEL_D, WHEEL_W, WHEEL_GAP = 34, 8, 1.5  # preview only
BOARD_SIZE = (75, 44, 1.6)                # preview only

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
prism = Manifold.extrude(CrossSection([outline]), 30)

AXLE = T + MOT_H / 2                      # axle height above plate bottom
GROUND = AXLE - WHEEL_D / 2               # ground Z in plate coordinates
POST_TOP = T + MOT_H + POST_GAP           # MCB underside
XF = TAB_X - WALL_T                       # gearbox face


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cylx(x0, x1, y, z, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def mx(m):
    return m + m.mirror([1, 0, 0])


cw = MOT_W / 2 + 0.15
mount = (box(CRADLE_X0, XF, -cw - CRADLE_T, cw + CRADLE_T, T - 0.1, AXLE)
         - box(CRADLE_X0 - 1, XF + 0.1, -cw, cw, T, AXLE + 1)
         + box(XF, TAB_X, -SCREW_SP / 2 - 4.5, SCREW_SP / 2 + 4.5, T - 0.1, AXLE + 8)
         - cylx(XF - 1, TAB_X + 1, 0, AXLE, BOSS_D)
         - cylx(XF - 1, TAB_X + 1, -SCREW_SP / 2, AXLE, SCREW_D)
         - cylx(XF - 1, TAB_X + 1, SCREW_SP / 2, AXLE, SCREW_D))
body = Manifold.extrude(cs, T) + mx(mount)
for x, y in BOARD:
    for s in (-1, 1):
        body += cyl(s * x, y, T - 0.1, POST_TOP, POST_D) ^ prism
cut = [cyl(s * x, y, -1, POST_TOP + 1, PILOT) for x, y in BOARD for s in (-1, 1)]
cut += [cyl(s * x, y, -1, 30, MOTOR_D) for x, y in MOTOR for s in (-1, 1)]   # zip-tie holes
plate = body
for c in cut:
    plate -= c

motors = mx(box(XF - MOT_L, XF, -MOT_W / 2, MOT_W / 2, T, T + MOT_H))
wheels = mx(cylx(TAB_X + WHEEL_GAP, TAB_X + WHEEL_GAP + WHEEL_W, 0, AXLE, WHEEL_D))
bw, bl, bt = BOARD_SIZE
board = box(-bw / 2, bw / 2, (BOARD[0][1] + BOARD[1][1] - bl) / 2, (BOARD[0][1] + BOARD[1][1] + bl) / 2,
            POST_TOP, POST_TOP + bt)


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

    def mesh(parts):
        t, col = [], []
        for m, c, a in parts:
            tt = tris(m)
            shade = 0.35 + 0.65 * np.clip(normals(tt) @ light, 0, 1)
            t.append(tt)
            col.append(np.c_[np.array(c)[None] * shade[:, None], np.full(len(tt), a)])
        return np.concatenate(t), np.concatenate(col)

    blue, grey, black, green = (0.0, 0.47, 0.84), (0.78, 0.78, 0.78), (0.22, 0.22, 0.22), (0.1, 0.55, 0.25)
    part = mesh([(plate, blue, 1)])
    full = mesh([(plate, blue, 1), (motors, grey, 1), (wheels, black, 1), (board, green, 0.35)])
    xw = TAB_X + WHEEL_GAP + WHEEL_W
    fig = plt.figure(figsize=(15, 5))
    for i, ((t, col), el, az, title) in enumerate(((part, 32, -55, "chassis (print)"),
                                                   (full, 25, -55, "with N20s, wheels, MCB"),
                                                   (full, 0, 0, "side: only the wheels touch the ground"))):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(t, facecolors=col, linewidths=0))
        ax.plot([-xw, xw, xw, -xw, -xw], [-L, -L, L, L, -L], GROUND, "k-", lw=0.6)
        ax.set(xlim=(-xw, xw), ylim=(-L, L), zlim=(GROUND, AXLE + WHEEL_D / 2), title=title)
        ax.set_box_aspect((2 * xw, 2 * L, WHEEL_D))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.92, wspace=0)
    fig.savefig(path, dpi=100)


if __name__ == "__main__":
    write_stl(plate, "mcb_chassis.stl")
    render("preview.png")
    bb = plate.bounding_box()
    print(f"bbox {bb[3]-bb[0]:.2f} x {bb[4]-bb[1]:.2f} x {bb[5]-bb[2]:.2f} mm, genus {plate.genus()}, "
          f"vol {plate.volume()/1000:.1f} cm3 (~{plate.volume()*1.24e-3:.0f} g PLA solid), "
          f"ground clearance {-GROUND:.1f} mm, MCB at {POST_TOP - GROUND:.1f} mm, "
          f"motor/board overlap {(motors ^ board).volume():.0f}, tris {len(tris(plate))}")
