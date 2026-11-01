#!/usr/bin/env python3
"""MCB chassis - two iterations, all mechanical parts 3D printed.

Base for both: LineaViper-X16 main plate, long sensor arms removed (same outline,
windows, MCB holes and motor tabs; 0.36 deg skew squared up; front = mirrored back).
N20s snap into cradles (snap lip + face wall with shaft boss hole + rear stop; the
M1.6 face-screw holes are optional). The MCB sits on 4 posts, held by printed
press-fit pins.

  balancer/    2 x 60 mm wheels. Keel under the plate carries the battery as
               counterweight, so the centre of gravity is below the axle. Keel, plate
               and MCB all stay inside the wheel radius: only the wheels can touch
               the ground, at any tilt. The keel slides on from the side, clips the
               front/back plate edges and is locked by the 4 long MCB pins.
  skid-steer/  2 N20s on the centre axle, 2 x 44 mm wheels, 4 printed corner skids
               (press-fit, seated in countersinks), tips 0.5 mm off the ground.

STLs are exported in print orientation; nothing needs supports.

    pip install manifold3d numpy matplotlib && python3 mcb_chassis.py

Axes (assembly): X = axle, Y = forward, Z = up, plate bottom at Z = 0. Units: mm.
"""
import os
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(48)

# ---- original LineaViper-X16 plate ----
T = 4.0                                    # plate thickness
W, L = 39.73, 25.68                        # body half-width (X), half-length (Y)
CX, CY = 7.73, 6.24                        # corner chamfer
TAB_X, TAB_Y0, TAB_Y1 = 44.8, -12.18, 13.83
BOARD = [(34.5, -19.89), (34.5, 18.06)]    # MCB holes, mirrored in X (69.0 x 37.95)
TABHOLE = [(38.07, -8.55), (38.07, 8.55)]  # original bracket holes d2.69
WIN = (5.5, 20.0, -16.48, 22.52)           # windows: X in +-[5.5, 20], Y range
# ---- N20 snap mount ----
MOT_W, MOT_H, MOT_L = 12, 10, 24
XR = 21.7                                  # motor rear, clear of the windows
XF, XW = XR + MOT_L, XR + MOT_L + 2        # gearbox face, face wall outside
AXLE = T + MOT_H / 2
CW, CT, LIP = MOT_W / 2 + 0.15, 1.6, 0.55  # cradle half gap, wall, snap lip
SCREW_SP, SCREW_D, BOSS_D = 9, 1.8, 4.5    # N20 face
# ---- MCB ----
POST_D, PIN_HOLE, PIN_D = 6.5, 2.8, 3.0    # posts, pin hole, pin (press fit)
POST_TOP, BOARD_T = T + MOT_H + 1.5, 1.6   # MCB underside, thickness
# ---- balancer ----
WHEEL_A = (60, 8)                          # wheel dia, width
R_K = WHEEL_A[0] / 2 - 2                   # keel radius about the axle
KEEL_X, LIP_X = 38, 31                     # keel / edge-clip half-lengths
BATT = (26, 13.5)                          # battery bay width (Y), depth (Z); 72.8 long
# ---- skid steer ----
WHEEL_B = (44, 12)
SKIDS = [(26, -21), (26, 21)]              # corner skids, mirrored in X
SKID_D, SKID_HOLE, SKID_GAP = 7.9, 4.6, 0.5   # body, hole (peg 4.5), tip above ground


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cylx(x0, x1, y, z, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def ext_x(cs, x0, x1):
    """Extrude a (Y, Z) profile along X."""
    return Manifold.extrude(cs, x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])


def mx(m):
    return m + m.mirror([1, 0, 0])


def plate_cs():
    half = [(W - CX, -L), (W, -L + CY), (W, TAB_Y0), (TAB_X, TAB_Y0), (TAB_X, TAB_Y1),
            (W, TAB_Y1), (W, L - CY), (W - CX, L)]
    return CrossSection([half + [(-x, y) for x, y in reversed(half)]])


WALL = [(CW, T - 0.1), (CW + CT, T - 0.1), (CW + CT, AXLE + 3.5), (CW + 0.45, AXLE + 3.5),
        (CW - LIP, AXLE + 2.4), (CW - LIP, AXLE + 2.0), (CW, AXLE + 1.45)]


def mount(ym):
    """N20 snap cradle on the +X side, motor axis along X at y = ym."""
    walls = CrossSection([WALL, [(-y, z) for y, z in reversed(WALL)]])
    m = (ext_x(walls, XR, XF - 1)
         + box(XR - 1.4, XR - 0.1, -CW - CT, CW + CT, T - 0.1, T + 2.5)   # rear stop
         + box(XF, XW, -9, 9, 0, AXLE + 8)                                 # face wall
         + box(XR - 1.4, XW, -9, 9, 0, T))                                 # base
    holes = (cylx(XF - 1, XW + 1, 0, AXLE, BOSS_D)
             + cylx(XF - 1, XW + 1, -SCREW_SP / 2, AXLE, SCREW_D)
             + cylx(XF - 1, XW + 1, SCREW_SP / 2, AXLE, SCREW_D))
    return m.translate([0, ym, 0]), holes.translate([0, ym, 0])


def chassis(motor_ys, skids=()):
    cs = plate_cs()
    prism = Manifold.extrude(cs, 40)
    body, cut = Manifold.extrude(cs, T), []
    for ym in motor_ys:
        m, h = mount(ym)
        body += mx(m)
        cut.append(mx(h))
    for x, y in BOARD:
        for s in (-1, 1):
            body += cyl(s * x, y, T - 0.1, POST_TOP, POST_D) ^ prism
            cut.append(cyl(s * x, y, -1, POST_TOP + 1, PIN_HOLE))
    for x, y in skids:
        for s in (-1, 1):
            body += cyl(s * x, y, T - 0.1, T + 4, 8) ^ prism
            cut.append(cyl(s * x, y, -1, T + 5, SKID_HOLE)
                       + Manifold.cylinder(1.71, 4.0, 2.29).translate([s * x, y, -0.01]))
    for x, y in TABHOLE:
        for s in (-1, 1):
            cut.append(cyl(s * x, y, -1, AXLE + 4, 2.69))
    x0, x1, y0, y1 = WIN
    cut += [box(x0, x1, y0, y1, -1, T + 1), box(-x1, -x0, y0, y1, -1, T + 1)]
    for c in cut:
        body -= c
    return body


def keel():
    circ = CrossSection.circle(R_K).translate([0, AXLE])
    below = CrossSection.square([2 * R_K, R_K]).translate([-R_K, -R_K])
    clip = [(L + 0.1, -2), (L + 1.7, -2), (L + 1.7, T + 1.4), (L - 1.0, T + 1.4),
            (L - 1.0, T + 0.15), (L + 0.1, T + 0.15)]
    clips = ext_x(CrossSection([clip, [(-y, z) for y, z in reversed(clip)]]) ^ circ, -KEEL_X, KEEL_X)
    ends = CrossSection([[(-LIP_X - 7.5, -2), (LIP_X + 7.5, -2), (LIP_X, T + 1.5), (-LIP_X, T + 1.5)]])
    clips ^= Manifold.extrude(ends, 80).rotate([90, 0, 0]).translate([0, 40, 0])   # 45 deg ends
    k = ext_x(circ ^ below, -KEEL_X, KEEL_X) + clips
    k -= box(-KEEL_X + 1.6, KEEL_X - 1.6, -BATT[0] / 2, BATT[0] / 2, -BATT[1], 1)
    for x, y in BOARD:
        for s in (-1, 1):
            k -= cyl(s * x, y, -6, 1, PIN_HOLE)
    return k


def skid(ground):
    tip, r = ground + SKID_GAP, SKID_D / 2
    return (cyl(0, 0, tip + r, 0, SKID_D) + Manifold.sphere(r).translate([0, 0, tip + r])
            + Manifold.cylinder(1.7, r, 2.25) + cyl(0, 0, 1.69, T + 3.7, 4.5))


def wheel(d, w, hub=7):
    r, n = d / 2, int(d * 0.8)
    m = cyl(0, 0, 0, w, d) - cyl(0, 0, -1, w + 1, d - 6) + cyl(0, 0, 0, 2, d - 5) + cyl(0, 0, 0, hub, 8)
    ring, hd = (r + 1) / 2, 0.55 * (r - 7)
    for i in range(6):
        a = np.radians(60 * i)
        m -= cyl(ring * np.cos(a), ring * np.sin(a), -1, 3, hd)
    for i in range(n):                                       # tread
        m -= box(r - 1, r + 1, -0.8, 0.8, -1, w + 1).rotate([0, 0, 360 * i / n])
    bore = CrossSection.circle(1.55) ^ CrossSection.square([4, 2.6]).translate([-2, -1.55])  # N20 D-shaft
    return m - Manifold.extrude(bore, hub + 2).translate([0, 0, -1])


def pin(length):
    return (cyl(0, 0, 0, 1.2, 6.5) + cyl(0, 0, 1.1, 1.2 + length - 0.5, PIN_D)
            + Manifold.cylinder(0.5, PIN_D / 2, PIN_D / 2 - 0.4).translate([0, 0, 0.7 + length]))


def tris(m):
    mesh = m.to_mesh()
    return np.asarray(mesh.vert_properties)[:, :3][np.asarray(mesh.tri_verts)]


def normals(t):
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def centroid(m):
    t = tris(m).astype(float)
    v = np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])) / 6
    return (v[:, None] * t.sum(1) / 4).sum(0) / v.sum(), v.sum()


def write_stl(m, path):
    t = tris(m).astype("<f4")
    rec = np.zeros(len(t), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = normals(t), t
    with open(path, "wb") as f:
        f.write(os.path.basename(path).encode().ljust(80, b" "))
        f.write(np.uint32(len(t)).tobytes())
        rec.tofile(f)


def render(path, panels, ext, ground):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = np.array([0.3, -0.5, 0.8]) / np.linalg.norm([0.3, -0.5, 0.8])
    (x0, x1), (y0, y1), (z0, z1) = ext
    fig = plt.figure(figsize=(15, 5))
    for i, (parts, el, az, title) in enumerate(panels):
        t, col = [], []
        for m, c, a in parts:
            tt = tris(m)
            shade = 0.35 + 0.65 * np.clip(normals(tt) @ light, 0, 1)
            t.append(tt)
            col.append(np.c_[np.array(c)[None] * shade[:, None], np.full(len(tt), a)])
        ax = fig.add_subplot(1, len(panels), i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(np.concatenate(t), facecolors=np.concatenate(col), linewidths=0))
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], ground, "k-", lw=0.6)
        ax.set(xlim=(x0, x1), ylim=(y0, y1), zlim=(z0, z1), title=title)
        ax.set_box_aspect((x1 - x0, y1 - y0, z1 - z0))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.92, wspace=0)
    fig.savefig(path, dpi=100)
    plt.close(fig)


def export(folder, parts):
    os.makedirs(folder, exist_ok=True)
    for name, m in parts.items():
        write_stl(m, os.path.join(folder, name + ".stl"))
        bb = m.bounding_box()
        print(f"  {name}.stl: {bb[3]-bb[0]:.1f} x {bb[4]-bb[1]:.1f} x {bb[5]-bb[2]:.1f} mm, "
              f"{m.volume()/1000:.1f} cm3, genus {m.genus()}")


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    BLUE, GREY, BLACK, GREEN, AMBER, ORANGE, WHITE = (
        (0.0, 0.47, 0.84), (0.78, 0.78, 0.78), (0.22, 0.22, 0.22), (0.1, 0.55, 0.25),
        (0.95, 0.65, 0.1), (1.0, 0.45, 0.2), (0.95, 0.95, 0.95))
    yc = (BOARD[0][1] + BOARD[1][1]) / 2
    board = box(-37.5, 37.5, yc - 22, yc + 22, POST_TOP, POST_TOP + BOARD_T)
    pin_top = POST_TOP + BOARD_T

    # ---- balancer ----
    ch, k, wh = chassis([0]), keel(), wheel(*WHEEL_A)
    wheels = mx(wh.rotate([0, 90, 0]).translate([XW + 1, 0, AXLE]))
    motors = mx(box(XR, XF, -MOT_W / 2, MOT_W / 2, T, T + MOT_H))
    print("balancer/")
    export(os.path.join(here, "balancer"), {
        "chassis": ch, "keel": k.rotate([0, -90, 0]).translate([0, 0, KEEL_X]),
        f"wheel_{WHEEL_A[0]}_x2": wh, "pin_long_x4": pin(pin_top + 5.5)})
    tot = mom = 0.0
    for m, f in ((ch, 0.5), (k, 1.0), (wheels, 0.6)):        # printed parts, effective fill
        c, v = centroid(m)
        tot, mom = tot + v * 1.24e-3 * f, mom + v * 1.24e-3 * f * c[2]
    for g, z in ((25, -BATT[1] / 2), (15, pin_top - BOARD_T / 2), (20, AXLE)):   # battery, MCB, motors
        tot, mom = tot + g, mom + g * z
    print(f"  CG {mom / tot - AXLE:+.1f} mm vs axle (25 g battery in keel, 15 g MCB, keel 100% infill), "
          f"~{tot:.0f} g; keel bottom {AXLE - R_K - (AXLE - WHEEL_A[0] / 2):.1f} mm above ground at any tilt")
    full = [(ch, BLUE, 1), (k, AMBER, 1), (motors, GREY, 1), (wheels, BLACK, 1), (board, GREEN, 0.35)]
    ga, xa, ra = AXLE - WHEEL_A[0] / 2, XW + 2 + WHEEL_A[1], WHEEL_A[0] / 2 + 1
    render(os.path.join(here, "balancer", "preview.png"),
           [([(ch, BLUE, 1), (k, AMBER, 1)], -18, -55, "chassis + keel (from below)"),
            (full, 22, -55, "balancer: N20s, 60 mm wheels, MCB"),
            (full, 0, 0, "side: keel inside wheel radius, only wheels touch")],
           ((-xa, xa), (-ra, ra), (ga, AXLE + ra)), ga)

    # ---- skid steer: 2 N20s + 4 corner skids ----
    gb = AXLE - WHEEL_B[0] / 2
    ch, wh, sk = chassis([0], SKIDS), wheel(*WHEEL_B), skid(gb)
    wheels = mx(wh.rotate([0, 90, 0]).translate([XW + 1, 0, AXLE]))
    skids = mx(sk.translate([*SKIDS[0], 0]) + sk.translate([*SKIDS[1], 0]))
    sp = sk.rotate([180, 0, 0])
    print("skid-steer/")
    export(os.path.join(here, "skid-steer"), {
        "chassis": ch, f"wheel_{WHEEL_B[0]}_x2": wh, "skid_x4": sp.translate([0, 0, -sp.bounding_box()[2]]),
        "pin_short_x4": pin(pin_top - 1)})
    print(f"  overlap skids/chassis {(skids ^ ch).volume():.2f}, wheels/chassis {(wheels ^ ch).volume():.2f}")
    full = [(ch, BLUE, 1), (motors, GREY, 1), (wheels, ORANGE, 1), (skids, WHITE, 1), (board, GREEN, 0.35)]
    xb, rb = XW + 2 + WHEEL_B[1], WHEEL_B[0] / 2 + 1
    render(os.path.join(here, "skid-steer", "preview.png"),
           [([(ch, BLUE, 1), (skids, WHITE, 1)], -18, -55, "chassis + 4 skids (from below)"),
            (full, 22, -55, "2 N20s, 44 mm wheels, 4 skids, MCB"),
            (full, 0, 0, f"side: skids {SKID_GAP} mm off the ground")],
           ((-xb, xb), (-L - 2, L + 2), (gb, AXLE + rb)), gb)
