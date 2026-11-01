#!/usr/bin/env python3
"""LineaViper-X16 (xsx.3mf) ball carrier - all 3D printed, your chassis unchanged.

A single-file ball gutter rides on the centre line, sloped 4 deg to the front. The front
ball sits on a trapdoor. A trigger blade hangs under the gutter and sticks out 9 mm ahead
of the arm tips. Drive into the tower: the blade is pushed back, after 3.7 mm its tongue
slides out from under the trapdoor, the trapdoor swings down and the balls roll out one
after another and drop into the tower. A V-detent keeps the blade armed while driving;
push it forward by hand to re-arm.

The gutter drops onto two flat-printed frames whose square pegs go into existing chassis
holes (front frame: one arm hole per arm; rear frame: the two 4 mm body holes).
Narrow (47 mm), light, on the centre line, rear end over the drive axle: little speed lost.

Set BALL_D / N_BALLS / TOWER_H / PLATE_Z for your setup and rerun:
    pip install manifold3d numpy matplotlib && python3 ball_carrier.py

Axes: X forward, Y left, Z up, origin on the floor under the motor axis. Units: mm.
"""
import os
import re
import zipfile
import numpy as np
from manifold3d import CrossSection, Manifold, Mesh, set_circular_segments

set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- your setup ----
BALL_D, N_BALLS = 40, 5          # ping-pong balls
TOWER_H, TOWER_D = 50, 70        # tower rim height above the floor, outside dia (preview)
PLATE_Z = 22                     # chassis underside above the floor (N20 under the plate, 34 mm wheels)
# ---- carrier ----
SLOPE = 4                        # deg, front down
WT, WEB_T, BAND_W, BAND_T = 1.2, 1.2, 14, 3.2   # wall, floor web, rolling band
WI = BALL_D + 4                  # inside width
HW = WI / 2 + WT                 # outside half width
WALL_H = BAND_T + BALL_D / 2 + 6
OPEN_L = BALL_D + 4              # trapdoor opening (u = 0 at its rear edge)
U_R = -(N_BALLS - 1) * (BALL_D + 0.5) - 2       # rear wall inner face
FLAP_Z = BAND_T - 0.1            # trapdoor underside, rests on the tongue
HINGE = (OPEN_L - 3.5, FLAP_Z + 3)               # trapdoor hinge axis (u, w)
CLEAR, AHEAD = 6, 9              # trapdoor above the tower rim, blade ahead of the arm tips
OV, TRAVEL, PD = 4, 8, 22        # tongue overlap, slot travel, blade depth under the gutter
U_HUMP = -30                     # detent
FRONT_X = 104                    # front frame near this X (arm hole column)
A = np.radians(SLOPE)


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def poly(pts):
    p = np.asarray(pts, float)
    if np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]) < 0:
        p = p[::-1]
    return CrossSection([p.tolist()])


def strut(p, q, w):
    p, q = np.asarray(p, float), np.asarray(q, float)
    n = np.array([-(q - p)[1], (q - p)[0]]) / np.linalg.norm(q - p) * w / 2
    return poly([p + n, q + n, q - n, p - n])


def ext_v(pts, v0, v1):          # (u, w) polygon extruded along v
    return Manifold.extrude(poly(pts), v1 - v0).rotate([90, 0, 0]).translate([0, v1, 0])


def ext_x(cs, x0, x1):           # (y, z) cross-section extruded along x
    return Manifold.extrude(cs, x1 - x0).rotate([90, 0, 90]).translate([x0, 0, 0])


def cyl_v(u, w, v0, v1, d):
    return Manifold.cylinder(v1 - v0, d / 2).rotate([90, 0, 0]).translate([u, v1, w])


# ---- your chassis ----
def chassis():
    t = zipfile.ZipFile(os.path.join(HERE, "xsx.3mf")).read("3D/Objects/object_2.model").decode()
    V = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', t), np.float32)
    T = np.array(re.findall(r'<triangle v1="(\d+)" v2="(\d+)" v3="(\d+)"', t), np.uint32)
    m = Manifold(Mesh(vert_properties=V, tri_verts=T))
    # motor axis to the origin, underside to PLATE_Z, 0.36 deg skew of the outline squared up
    return (m.translate([61.55, -1.005, 2]).rotate([0, 0, np.degrees(np.arctan2(0.69, 108.54))])
            .translate([0, 0, PLATE_Z]))


def holes(ch):
    out = {}
    for p in ch.slice(PLATE_Z + 2).to_polygons():
        p = np.asarray(p)
        c = p.mean(0)
        r = np.linalg.norm(p - c, axis=1)
        if len(p) > 8 and r.std() < 0.05 * r.mean():
            out.setdefault(round(2 * r.mean(), 1), []).append(c)
    return {k: np.array(v) for k, v in out.items()}


CH = chassis()
HOLES = holes(CH)
X_O = CH.bounding_box()[3] + AHEAD + 4            # trapdoor rear edge
Z_O = TOWER_H + CLEAR                             # gutter underside there


def floor_z(x):
    return Z_O - (x - X_O) * np.tan(A)


def world(m):
    return m.rotate([0, SLOPE, 0]).translate([X_O, 0, Z_O])


# ---- printed parts (carrier, trapdoor, trigger in the gutter frame u, v, w) ----
def carrier(peg_us):
    m = box(U_R - WT, OPEN_L + WT, -HW, HW, 0, WALL_H) - box(U_R, OPEN_L, -WI / 2, WI / 2, WEB_T, WALL_H + 1)
    m -= box(0, OPEN_L, -WI / 2, WI / 2, -1, WEB_T + 1)                         # trapdoor opening
    for u0 in np.arange(U_R + 6, -34, 34):                                      # lightening
        for s in (-1, 1):
            m -= box(u0, u0 + 26, *sorted((s * (BAND_W / 2 + 2), s * (WI / 2 - 2))), -1, WEB_T + 1)
            m -= box(u0, u0 + 26, *sorted((s * (WI / 2 - 0.5), s * (HW + 0.5))), 9, WALL_H - 6)
    m += box(U_R, 0, -BAND_W / 2, BAND_W / 2, 0, BAND_T)                         # rolling band
    m -= box(-44 - TRAVEL, 1, -4.2, 4.2, WEB_T, BAND_T + 1)                     # tongue recess
    m -= box(-22 - TRAVEL - 1, 1, -1.7, 1.7, -1, BAND_T + 1)                    # blade slot
    hump = [(U_HUMP - 1, WEB_T - 0.01), (U_HUMP + 1, WEB_T - 0.01), (U_HUMP, WEB_T + 0.6)]
    m += ext_v(hump, 1.7, 4.2) + ext_v(hump, -4.2, -1.7)
    m -= cyl_v(*HINGE, -HW - 1, HW + 1, 3.3)                                    # hinge pin
    for u in peg_us:
        m -= box(u - 1.25, u + 1.25, -1.25, 1.25, -1, BAND_T + 1)               # frame pegs
    return m


def trapdoor():
    m = box(0.3, HINGE[0], -WI / 2 + 0.4, WI / 2 - 0.4, FLAP_Z, FLAP_Z + 1.6)
    m += cyl_v(*HINGE, -WI / 2 + 0.4, WI / 2 - 0.4, 6)
    return m - cyl_v(*HINGE, -WI / 2, WI / 2, 3.5)


def trigger():
    t = np.tan(A)                 # front edge vertical in the world
    blade = ext_v([(-22, -PD), (-4 + PD * t, -PD), (-4, 0), (-4, WEB_T + 0.5), (-22, WEB_T + 0.5)], -1.5, 1.5)
    m = box(-44, OV, -4, 4, WEB_T, FLAP_Z) + blade
    return m - ext_v([(U_HUMP - 1.3, WEB_T - 0.01), (U_HUMP + 1.3, WEB_T - 0.01), (U_HUMP, WEB_T + 0.7)], -5, 5)


def pin():
    cs = CrossSection.circle(1.6) ^ CrossSection.square([4, 2.9]).translate([-2, -1.3])   # flat side down
    return ext_x(cs, 0, 2 * HW + 1).translate([0, 0, 1.3])


def frame(feet, peg):
    """Flat-printed support: feet with square pegs into chassis holes, saddle + peg under the gutter."""
    xh = float(np.mean(feet[:, 0]))
    zt, zs = PLATE_Z + 4, floor_z(xh + 2.9)
    yc = HW + 2.2
    cs = poly([(-yc, zs - 3), (yc, zs - 3), (yc, zs + 8), (HW + 0.2, zs + 8), (HW + 0.2, zs),
               (-HW - 0.2, zs), (-HW - 0.2, zs + 8), (-yc, zs + 8)])
    for _, y in feet:
        cs += poly([(y - 5, zt), (y + 5, zt), (y + 5, zt + 4), (y - 5, zt + 4)])
        cs += strut((y, zt + 2), (np.sign(y) * (HW + 1.2), zs - 1.5), 5)
    m = ext_x(cs, xh - 1.1, xh + 2.9) + box(xh - 1.1, xh + 1.1, -1.15, 1.15, zs - 0.1, zs + 2.9)
    for _, y in feet:
        m += box(xh - 1.1, xh + 1.1, y - peg / 2, y + peg / 2, zt - 3.8, zt + 0.1)
    return m, xh


arm = HOLES[3.2]
top, bot = arm[arm[:, 1] > 0], arm[arm[:, 1] < 0]
ft = top[np.argmin(abs(top[:, 0] - FRONT_X))]
FRAME_F, XF = frame(np.array([ft, bot[np.argmin(abs(bot[:, 0] - ft[0]))]]), 2.2)
FRAME_R, XR = frame(HOLES[4.0], 2.8)
PEG_U = [(x - X_O) / np.cos(A) for x in (XF, XR)]
CARRIER, TRAPDOOR, TRIGGER = carrier(PEG_U), trapdoor(), trigger()

b1 = (OPEN_L - BALL_D / 2, FLAP_Z + 1.6 + BALL_D / 2)
u2 = b1[0] - np.sqrt(BALL_D ** 2 - (b1[1] - BAND_T - BALL_D / 2) ** 2)
BALLS = [b1] + [(u2 - k * BALL_D, BAND_T + BALL_D / 2) for k in range(N_BALLS - 1)]


# ---- output ----
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
        f.write(os.path.basename(path).encode().ljust(80, b" "))
        f.write(np.uint32(len(t)).tobytes())
        rec.tofile(f)


def write_3mf(path, objs, items):
    """objs: [(name, manifold)], items: [(object index from 1, x, y)] on the build plate."""
    res = []
    for i, (name, m) in enumerate(objs, 1):
        b = m.bounding_box()
        mesh = m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]]).to_mesh()
        vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in np.asarray(mesh.vert_properties)[:, :3])
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in np.asarray(mesh.tri_verts))
        res.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>{vs}</vertices>'
                   f'<triangles>{ts}</triangles></mesh></object>')
    build = "".join(f'<item objectid="{o}" transform="1 0 0 0 1 0 0 0 1 {x} {y} 0"/>' for o, x, y in items)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.'
                   'openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/'
                   'vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/'
                   'vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.'
                   'openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" '
                   'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", '<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" '
                   'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>'
                   + "".join(res) + f"</resources><build>{build}</build></model>")


def render(path, panels):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    light = np.array([0.3, -0.5, 0.8]) / np.linalg.norm([0.3, -0.5, 0.8])
    fig = plt.figure(figsize=(16, 6))
    for i, (parts, el, az, title, ((x0, x1), (y0, y1), (z0, z1))) in enumerate(panels):
        t, col = [], []
        for m, c, a in parts:
            tt = tris(m)
            shade = 0.35 + 0.65 * np.clip(normals(tt) @ light, 0, 1)
            t.append(tt)
            col.append(np.c_[np.array(c)[None] * shade[:, None], np.full(len(tt), a)])
        ax = fig.add_subplot(1, len(panels), i + 1, projection="3d")
        ax.add_collection3d(Poly3DCollection(np.concatenate(t), facecolors=np.concatenate(col), linewidths=0))
        ax.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], 0, "k-", lw=0.6)
        ax.set(xlim=(x0, x1), ylim=(y0, y1), zlim=(z0, z1), title=title)
        ax.set_box_aspect((x1 - x0, y1 - y0, z1 - z0))
        ax.view_init(el, az)
        ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=0.93, wspace=0)
    fig.savefig(path, dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    cw, tw, fw = world(CARRIER), world(TRAPDOOR), world(TRIGGER)
    balls = sum((world(Manifold.sphere(BALL_D / 2, 32).translate([u, 0, w])) for u, w in BALLS[1:]),
                world(Manifold.sphere(BALL_D / 2, 32).translate([BALLS[0][0], 0, BALLS[0][1]])))
    pairs = {"carrier/frames": cw ^ (FRAME_F + FRAME_R), "carrier/trigger": cw ^ fw, "carrier/trapdoor": cw ^ tw,
             "trapdoor/trigger": tw ^ fw, "balls/parts": balls ^ (cw + tw + fw), "frames/chassis": CH ^ (FRAME_F + FRAME_R)}
    print("overlaps", {k: round(v.volume(), 2) for k, v in pairs.items()})
    xb = X_O - 4 * np.cos(A)
    print(f"blade face x={xb:.1f} ({xb - CH.bounding_box()[3]:.1f} ahead of the arm tips), z={world(TRIGGER).bounding_box()[2]:.1f}"
          f"..{Z_O:.1f}; trapdoor x={X_O:.1f}..{X_O + OPEN_L:.1f} at z={Z_O:.1f}..{floor_z(X_O + OPEN_L):.1f}; "
          f"carrier x={cw.bounding_box()[0]:.1f}..{cw.bounding_box()[3]:.1f}, top z={cw.bounding_box()[5]:.1f}; "
          f"frames at x={XR:.1f}, {XF:.1f}")
    parts = {"carrier": CARRIER, "trapdoor": TRAPDOOR, "trigger": TRIGGER.rotate([180, 0, 0]), "hinge_pin": pin(),
             "frame_front": FRAME_F.rotate([0, -90, 0]), "frame_rear": FRAME_R.rotate([0, -90, 0])}
    tot = 0
    for name, m in parts.items():
        write_stl(m, os.path.join(HERE, name + ".stl"))
        bb, tot = m.bounding_box(), tot + m.volume()
        print(f"  {name}.stl: {bb[3]-bb[0]:.1f} x {bb[4]-bb[1]:.1f} x {bb[5]-bb[2]:.1f} mm, {m.volume()/1000:.1f} cm3")
    print(f"  total {tot/1000:.1f} cm3 = {tot*1.24e-3:.0f} g PLA at 100% infill")
    write_3mf(os.path.join(HERE, "ball_carrier.3mf"), list(parts.items()),
              [(1, 128, 32), (2, 160, 120), (3, 215, 120), (4, 160, 180), (5, 40, 160), (6, 100, 120)])

    tr = TOWER_D / 2
    tower = (Manifold.cylinder(TOWER_H, tr) - Manifold.cylinder(TOWER_H + 1, tr - 3).translate([0, 0, 2])).translate([xb + tr, 0, 0])
    wheel = Manifold.cylinder(8, 17).rotate([90, 0, 0])
    wheels = wheel.translate([0, 54.3, PLATE_Z - 5]) + wheel.translate([0, -46.3, PLATE_Z - 5])
    BLUE, AMBER, RED, GREY, WHITE, BLACK = ((0.0, 0.47, 0.84), (0.95, 0.65, 0.1), (0.85, 0.2, 0.2),
                                            (0.45, 0.45, 0.5), (0.97, 0.97, 0.97), (0.2, 0.2, 0.2))
    robot = [(CH, BLUE, 1), (FRAME_F + FRAME_R, GREY, 1), (cw, AMBER, 1), (tw + fw, RED, 1), (balls, WHITE, 1),
             (wheels, BLACK, 1)]
    full = ((-30, xb + TOWER_D + 5), (-80, 80), (0, 100))
    render(os.path.join(HERE, "preview.png"), [
        (robot, 25, -60, "xsx + ball carrier", full),
        (robot + [(tower, GREY, 0.35)], 0, -90, f"side: blade touches the tower ({TOWER_H} mm rim)", full),
        ([(cw, AMBER, 1), (tw, RED, 1), (fw, (0.6, 0.1, 0.6), 1), (FRAME_F, GREY, 1)], -25, -50,
         "trapdoor + trigger (from below)", ((X_O - 70, X_O + 50), (-35, 35), (Z_O - 30, Z_O + 20)))])
