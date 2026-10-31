#!/usr/bin/env python3
"""Micromouse chassis - 2x N20 gear motors, two wheels only (no caster).

Axle sits at the plate centre (turns in place). The plate hangs below the
axle so the centre of gravity stays under it and the mouse rests on its two
wheels alone. Front/back M3 bosses take optional screw-head tip-stops.
Prints flat side down, no supports.

    pip install manifold3d numpy matplotlib && python3 chassis.py

Axes: X = axle, Y = forward, Z = up. Units: mm.
"""
import numpy as np
from manifold3d import Manifold, set_circular_segments

set_circular_segments(40)

# ---- parameters ----
WHEEL_D, WHEEL_W, WHEEL_GAP = 34, 8, 1.5   # wheel dia, width, gap to bracket
MOT_W, MOT_H, MOT_L = 12, 10, 24           # N20 body (gearbox + can)
SCREW_SP, SCREW_D, BOSS_D = 9, 1.8, 4.5    # N20 face: 2x M1.6 @ 9 mm, shaft boss
CENTER_GAP = 8                             # between motor rear ends (~26 for encoder N20s)
L, CLEAR, T, R = 76, 4, 2.5, 6             # plate length, ground clearance, thickness, corner R
WALL_T, CRADLE_T = 2, 1.6                  # motor bracket wall, cradle side walls
POST_TOP, POST_D, PILOT = 26, 6, 2.6       # board standoffs: top Z, dia, M3 self-tap pilot
BOARD_HOLE = (36, 33)                      # board hole (x, y), mirrored to 4 corners
EXTRA_HOLES = [(18, 34), (35, 25)]         # spare M3 holes, mirrored to 4 corners
WIN_W, WIN_L, WIN_Y = 36, 14, 20           # two wiring / strap windows
SKID_Y = 33                                # tip-stop screw bosses (front / back)

AX = WHEEL_D / 2                           # axle height
Z0, Z1 = CLEAR, CLEAR + T                  # plate bottom / top
MZ = AX - MOT_H / 2                        # motor bottom
XR = CENTER_GAP / 2                        # motor rear end
XF = XR + MOT_L                            # gearbox face
XW = XF + WALL_T                           # bracket outer face
W = 2 * (XW + WHEEL_GAP + WHEEL_W + 1.5)   # plate width = overall width


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cz(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cx(x0, x1, y, z, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def quad(pts):
    return sorted({(sx * x, sy * y) for x, y in pts for sx in (-1, 1) for sy in (-1, 1)})


def mirror_x(m):
    return m + m.mirror([1, 0, 0])


# plate
body = Manifold.batch_hull([cz(x, y, Z0, Z1, 2 * R) for x, y in quad([(W / 2 - R, L / 2 - R)])])

# motor cradle (U channel + zip-tie tunnel) and bracket wall, right side mirrored
cw = MOT_W / 2 + 0.15
cradle = (box(XR, XF, -cw - CRADLE_T, cw + CRADLE_T, Z0 + 1, AX)
          - box(XR - 1, XF, -cw, cw, MZ, AX + 1)
          - box(XR + 6, XR + 9.5, -20, 20, MZ - 3.6, MZ - 1.8))
body += mirror_x(cradle + box(XF, XW, -9, 9, Z0 + 1, AX + 8))

# board standoffs + tip-stop bosses
for x, y in quad([BOARD_HOLE]):
    body += cz(x, y, Z0 + 1, POST_TOP, POST_D)
for s in (-1, 1):
    body += cz(0, s * SKID_Y, Z0 + 1, Z1 + 5, 7)

# cuts
cuts = [mirror_x(box(XW, W, -AX - 2, AX + 2, Z0 - 1, Z1 + 1))]  # wheel notches
cuts += [box(-WIN_W / 2, WIN_W / 2, s * WIN_Y - WIN_L / 2, s * WIN_Y + WIN_L / 2, Z0 - 1, Z1 + 1)
         for s in (-1, 1)]
cuts += [cz(x, y, Z0 - 1, POST_TOP + 1, PILOT) for x, y in quad([BOARD_HOLE])]
cuts += [cz(x, y, Z0 - 1, Z1 + 1, 3.2) for x, y in quad(EXTRA_HOLES)]
cuts += [cz(0, s * SKID_Y, Z0 - 1, Z1 + 6, PILOT) for s in (-1, 1)]
cuts += [mirror_x(cx(XF - 1, XW + 1, 0, AX, BOSS_D)
                  + cx(XF - 1, XW + 1, -SCREW_SP / 2, AX, SCREW_D)
                  + cx(XF - 1, XW + 1, SCREW_SP / 2, AX, SCREW_D))]
chassis = body
for c in cuts:
    chassis -= c

# reference parts (preview only)
motors = mirror_x(box(XR, XF, -MOT_W / 2, MOT_W / 2, MZ, MZ + MOT_H))
wheels = mirror_x(cx(XW + WHEEL_GAP, XW + WHEEL_GAP + WHEEL_W, 0, AX, WHEEL_D))


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
        f.write(b"micromouse chassis".ljust(80, b" "))
        f.write(np.uint32(len(t)).tobytes())
        rec.tofile(f)


def render(path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = np.array([0.3, -0.5, 0.8]) / np.linalg.norm([0.3, -0.5, 0.8])
    t, col = [], []
    for m, c in ((chassis, (0.0, 0.47, 0.84)), (motors, (0.78, 0.78, 0.78)), (wheels, (0.22, 0.22, 0.22))):
        tt = tris(m)
        shade = 0.35 + 0.65 * np.clip(normals(tt) @ light, 0, 1)
        t.append(tt)
        col.append(np.array(c)[None] * shade[:, None])
    t, col = np.concatenate(t), np.concatenate(col)
    fig = plt.figure(figsize=(12, 5))
    for i, (el, az, title) in enumerate(((28, -55, "iso"), (0, 0, "side: wheels only touch ground"))):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(t, facecolors=col, linewidths=0))
        ax.plot([-W / 2, W / 2, W / 2, -W / 2, -W / 2], [-L / 2, -L / 2, L / 2, L / 2, -L / 2], 0, "k-", lw=0.6)
        ax.set(xlim=(-W / 2, W / 2), ylim=(-L / 2, L / 2), zlim=(0, POST_TOP + 2), title=title)
        ax.set_box_aspect((W, L, POST_TOP + 2))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    out = chassis.translate([0, 0, -Z0])
    write_stl(out, "micromouse_chassis.stl")
    render("preview.png")
    bb = out.bounding_box()
    vol = out.volume() if hasattr(out, "volume") else out.get_volume()
    print(f"bbox {bb[3]-bb[0]:.1f} x {bb[4]-bb[1]:.1f} x {bb[5]-bb[2]:.1f} mm, "
          f"genus {out.genus()}, vol {vol/1000:.1f} cm3 (~{vol*1.24e-3:.0f} g PLA solid), "
          f"tris {len(tris(out))}")
