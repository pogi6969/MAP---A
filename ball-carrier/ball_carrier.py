#!/usr/bin/env python3
"""LineaViper-X16 (xsx.3mf) ball box: 30 balls, dumped on contact, all 3D printed.

Like the cardboard prototype: an open box on top of the robot with a ramp inside that slopes
down to a hole at the front. A trapdoor closes the hole. A trigger blade under the box sticks
out 9 mm ahead of the arm tips. When the robot drives into the tower the blade is pushed
back; after 3.7 mm its tongue slides out from under the trapdoor, the trapdoor swings down and
the balls pour down the ramp, through the hole, into the tower. A V-detent keeps the blade
armed while driving; to re-arm, close the trapdoor and push the blade forward.

Your xsx chassis is unchanged: the box sits on two flat-printed frames whose square pegs go
into existing holes (front frame: one arm hole per arm; rear frame: the two 4 mm body holes).
Parts: box, ramp (drops in, wedged by the tapered walls), trapdoor, trigger, hinge pin,
2 frames. All print without supports. Walls are slotted to save weight.

Set BALL_D / N_BALLS / TOWER_H / PLATE_Z for your setup and rerun:
    pip install manifold3d numpy matplotlib && python3 ball_carrier.py

Axes: X forward, Y left, Z up, origin on the floor under the motor axis. Units: mm.
"""
import os
import re
import zipfile
import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, Mesh, set_circular_segments

set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- your setup ----
BALL_D, N_BALLS = 40, 30         # ping-pong balls
TOWER_H, TOWER_D = 50, 140       # tower rim height above the floor, outside dia (preview only)
PLATE_Z = 22                     # chassis underside above the floor (N20 under the plate, 34 mm wheels)
# ---- box: u = X - X_O (0 = rear edge of the hole), v = Y, w = Z - Z_O (0 = box underside) ----
HW_R, HW_O = 70, 45              # inside half-widths: box, hole
OUT_L, TAPER_L = 60, 50          # hole length, tapered walls behind it
U_R = -180                       # rear wall inside face
RAMP = 10                        # ramp slope, deg
WT, BAND_T, RAMP_T, FLAP_T = 1.0, 3.2, 1.6, 1.6
FLAP_Z = BAND_T - 0.1            # trapdoor underside, rests on the trigger tongue
HINGE = (OUT_L - 3.5, FLAP_Z + 3)                 # trapdoor hinge axis (u, w)
Z0R = BAND_T + RAMP_T            # ramp top at the hole edge (= trapdoor top)
CLEAR, AHEAD = 6, 9              # box above the tower rim, blade ahead of the arm tips
OV, TRAVEL, PD, U_HUMP = 4, 8, 22, -30            # tongue overlap, slot travel, blade depth, detent
FRONT_X = 104                    # front frame near this X (arm hole column)
TR = np.tan(np.radians(RAMP))


def hw(u):
    return HW_O if u >= 0 else HW_R if u <= -TAPER_L else HW_O + (HW_R - HW_O) * -u / TAPER_L


def floor_w(u):                  # what a ball rests on: ramp, or the trapdoor ribs
    return Z0R + -u * TR if u < 0 else FLAP_Z + FLAP_T + 3


def pile(h, n_max):
    """Drop balls one by one into the lowest free spot (rolls down the ramp, stacks on others).
    Returns ball centres (u, v, w), all of them below the rim."""
    r, c, d = BALL_D / 2, np.cos(np.radians(RAMP)), BALL_D + 0.3
    U, V = (a.ravel() for a in np.meshgrid(np.arange(U_R + r, OUT_L - r, 2.5), np.arange(-HW_R + r, HW_R - r, 2.5)))
    ok = np.array([abs(v) + r + 0.3 <= min(hw(u - r), hw(u), hw(u + r)) for u, v in zip(U, V)])
    U, V = U[ok], V[ok]
    W = np.array([max(floor_w(x) + (r if x >= 0 else r / c) for x in (u - r, u, u + r)) for u in U])
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


H = next(h for h in range(60, 200, 5) if len(pile(h, N_BALLS)) >= N_BALLS)   # wall height for N_BALLS


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


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
X_O = CH.bounding_box()[3] + AHEAD + 4            # rear edge of the hole
Z_O = TOWER_H + CLEAR                             # box underside
INNER = poly([(U_R, -HW_R), (-TAPER_L, -HW_R), (0, -HW_O), (OUT_L, -HW_O), (OUT_L, HW_O), (0, HW_O),
              (-TAPER_L, HW_R), (U_R, HW_R)])
BACK = CrossSection.square([1000, 1000]).translate([-1000, -500])   # u <= 0


def world(m):
    return m.translate([X_O, 0, Z_O])


# ---- printed parts (box frame u, v, w) ----
def box_part(frame_us):
    ring = INNER.offset(WT, JoinType.Miter) - INNER
    m = Manifold.extrude(ring, H)
    pts = np.asarray(INNER.to_polygons()[0])
    posts = CrossSection()
    for a, b in zip(pts, np.roll(pts, -1, axis=0)):                            # posts every <= 45 mm
        for t in np.linspace(0, 1, int(np.ceil(np.linalg.norm(b - a) / 45)) + 1):
            posts += CrossSection.square([5, 5]).translate(a + t * (b - a) - 2.5)
    posts += CrossSection.square([16, 2 * HW_O + 10]).translate([HINGE[0] - 8, -HW_O - 5])   # hinge stays solid
    slots = Manifold.extrude(ring - posts, 12)
    for w0 in np.arange(4, H - 14, 15):                                         # rails: 12 mm slots, 3 mm bars
        m -= slots.translate([0, 0, w0])
    region = INNER ^ BACK                                                       # floor frame
    thin = region - region.offset(-5, JoinType.Miter)
    for v in (-56, -28, 28, 56):
        thin += CrossSection.square([-U_R, 6]).translate([U_R, v - 3])
    thick = CrossSection.square([60, 14]).translate([-60, -7]) + CrossSection.square([6, 200]).translate([-6, -100])
    for u in frame_us:                                                          # trigger band, hole edge, frame bars
        thick += CrossSection.square([8, 2 * HW_R]).translate([u - 3, -HW_R])
    m += Manifold.extrude(thin ^ region, 2) + Manifold.extrude(thick ^ region, BAND_T)
    for u in (-20, -55, -95, -135, -170):                                       # ramp posts
        for v in (-56, -28, 28, 56):
            if abs(v) + 4 < min(hw(u - 3), hw(u + 3)):
                m += cyl(u, v, 1.9, BAND_T + -(u + 3) * TR - 0.2, 6)
    m -= box(-44 - TRAVEL, 1, -4.2, 4.2, 1.2, BAND_T + 1)                       # tongue recess
    m -= box(-22 - TRAVEL - 1, 1, -1.7, 1.7, -1, BAND_T + 1)                    # blade slot
    hump = [(U_HUMP - 1, 1.19), (U_HUMP + 1, 1.19), (U_HUMP, 1.8)]
    m += ext_v(hump, 1.7, 4.2) + ext_v(hump, -4.2, -1.7)
    m -= cyl_v(*HINGE, -HW_O - WT - 1, HW_O + WT + 1, 3.3)                      # hinge pin
    for u in frame_us:
        for v in (-40, 40):
            m -= box(u - 1.25, u + 1.25, v - 1.25, v + 1.25, -1, BAND_T + 1)    # frame pegs
    return m


def ramp_flat():
    out = INNER.offset(-0.5, JoinType.Miter) ^ BACK.translate([-0.5, 0])
    out -= CrossSection.square([12, 12]).translate([-12, -6])                   # clear of the tongue
    holes = CrossSection()                                                      # slats every 14 mm, ties every 30
    for k in range(-5, 5):
        for u0 in np.arange(-4, U_R, -30):
            holes += CrossSection.square([27, 11]).translate([u0 - 27, 14 * k + 1.5])
    out -= holes ^ out.offset(-4, JoinType.Miter)
    return Manifold.extrude(out.scale([1 / np.cos(np.radians(RAMP)), 1]), RAMP_T)


def ramp():
    return ramp_flat().rotate([0, RAMP, 0]).translate([0, 0, BAND_T])


def trapdoor():
    h = HW_O - 0.4
    m = box(0.3, HINGE[0], -h, h, FLAP_Z, FLAP_Z + FLAP_T) + cyl_v(*HINGE, -h, h, 6)
    for u0 in (7, 25):
        for v0 in (-40, -18, 4, 26):
            m -= box(u0, u0 + 14, v0, v0 + 14, 0, 10)
    for v in (-22, 22):
        m += box(4, HINGE[0] - 3, v - 0.8, v + 0.8, FLAP_Z + FLAP_T - 0.1, FLAP_Z + FLAP_T + 3)
    return m - cyl_v(*HINGE, -HW_O, HW_O, 3.5)


def trigger():
    blade = ext_v([(-22, -PD), (-4, -PD), (-4, 1.7), (-22, 1.7)], -1.5, 1.5)
    m = box(-44, OV, -4, 4, 1.2, FLAP_Z) + blade
    return m - ext_v([(U_HUMP - 1.3, 1.19), (U_HUMP + 1.3, 1.19), (U_HUMP, 1.9)], -5, 5)


def pin():
    cs = CrossSection.circle(1.6) ^ CrossSection.square([4, 2.9]).translate([-2, -1.3])   # flat side down
    return ext_x(cs, 0, 2 * (HW_O + WT) + 1).translate([0, 0, 1.3])


def frame(feet, peg):
    """Flat-printed support: feet with square pegs into chassis holes, beam + 2 pegs under the box."""
    xh = float(np.mean(feet[:, 0]))
    zt, zs, hb = PLATE_Z + 4, Z_O, HW_R + WT
    cs = poly([(-hb, zs - 4), (hb, zs - 4), (hb, zs), (-hb, zs)])
    for _, y in feet:
        s = np.sign(y)
        cs += poly([(y - 5, zt), (y + 5, zt), (y + 5, zt + 4), (y - 5, zt + 4)])
        cs += strut((y, zt + 3), (s * (hb - 6), zs - 3.5), 5) + strut((y, zt + 3), (s * 15, zs - 3.5), 5)
    m = ext_x(cs, xh - 1.1, xh + 2.9)
    for v in (-40, 40):
        m += box(xh - 1.1, xh + 1.1, v - 1.15, v + 1.15, zs - 0.1, zs + 2.9)
    for _, y in feet:
        m += box(xh - 1.1, xh + 1.1, y - peg / 2, y + peg / 2, zt - 3.8, zt + 0.1)
    return m, xh


arm = HOLES[3.2]
top, bot = arm[arm[:, 1] > 0], arm[arm[:, 1] < 0]
ft = top[np.argmin(abs(top[:, 0] - FRONT_X))]
FRAME_F, XF = frame(np.array([ft, bot[np.argmin(abs(bot[:, 0] - ft[0]))]]), 2.2)
FRAME_R, XR = frame(HOLES[4.0], 2.8)
BOX = box_part([XF - X_O, XR - X_O])


def balls():
    return [world(Manifold.sphere(BALL_D / 2, 24).translate([u, v, w])) for u, v, w in pile(H, N_BALLS)]


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
    bw, rw, tw, fw = world(BOX), world(ramp()), world(trapdoor()), world(trigger())
    bl, n_sites = balls(), len(pile(H, 999))
    bm = sum(bl[1:], bl[0])
    frames = FRAME_F + FRAME_R
    pairs = {"box/ramp": bw ^ rw, "box/trapdoor": bw ^ tw, "box/trigger": bw ^ fw, "box/frames": bw ^ frames,
             "ramp/trigger": rw ^ fw, "trapdoor/trigger": tw ^ fw, "balls/parts": bm ^ (bw + rw + tw),
             "frames/chassis": CH ^ frames}
    print("overlaps", {k: round(v.volume(), 2) for k, v in pairs.items()})
    xb = X_O - 4
    bb = bw.bounding_box()
    print(f"walls {H} mm: {len(bl)} balls in, {n_sites} fit below the rim; "
          f"box x={bb[0]:.0f}..{bb[3]:.0f}, y=+-{bb[4]:.0f}, z={bb[2]:.0f}..{bb[5]:.0f}; "
          f"hole {2 * HW_O} x {OUT_L} at x={X_O:.0f}; blade face x={xb:.1f} "
          f"({xb - CH.bounding_box()[3]:.1f} ahead of the arm tips), z={fw.bounding_box()[2]:.0f}..{Z_O:.0f}")
    parts = {"box": BOX, "ramp": ramp_flat(), "trapdoor": trapdoor(), "trigger": trigger().rotate([180, 0, 0]),
             "hinge_pin": pin(), "frame_front": FRAME_F.rotate([0, -90, 0]).rotate([0, 0, 90]),
             "frame_rear": FRAME_R.rotate([0, -90, 0]).rotate([0, 0, 90])}
    tot = 0
    for name, m in parts.items():
        write_stl(m, os.path.join(HERE, name + ".stl"))
        b, tot = m.bounding_box(), tot + m.volume()
        print(f"  {name}.stl: {b[3]-b[0]:.1f} x {b[4]-b[1]:.1f} x {b[5]-b[2]:.1f} mm, {m.volume()/1000:.1f} cm3")
    print(f"  total {tot/1000:.1f} cm3 = {tot*1.24e-3:.0f} g PLA at 100% infill; balls {N_BALLS * 2.7:.0f} g")
    write_3mf(os.path.join(HERE, "plate1_box.3mf"), [("box", parts["box"])], [(1, 128, 128)])
    names = ["ramp", "trapdoor", "trigger", "hinge_pin", "frame_front", "frame_rear"]
    write_3mf(os.path.join(HERE, "plate2_parts.3mf"), [(n, parts[n]) for n in names],
              [(1, 97, 72), (2, 225, 50), (3, 225, 120), (4, 205, 240), (5, 100, 170), (6, 100, 215)])

    tr = TOWER_D / 2
    tower = (Manifold.cylinder(TOWER_H, tr) - Manifold.cylinder(TOWER_H, tr - 3).translate([0, 0, 2])).translate([xb + tr, 0, 0])
    wheel = Manifold.cylinder(8, 17).rotate([90, 0, 0])
    wheels = wheel.translate([0, 54.3, PLATE_Z - 5]) + wheel.translate([0, -46.3, PLATE_Z - 5])
    BLUE, AMBER, RED, GREY, WHITE, BLACK, TAN = ((0.0, 0.47, 0.84), (0.95, 0.65, 0.1), (0.85, 0.2, 0.2),
                                                 (0.45, 0.45, 0.5), (0.97, 0.97, 0.97), (0.2, 0.2, 0.2),
                                                 (0.8, 0.55, 0.2))
    robot = [(CH, BLUE, 1), (frames, GREY, 1), (wheels, BLACK, 1), (rw, TAN, 1), (tw + fw, RED, 1),
             (bm, WHITE, 1), (bw, AMBER, 0.45)]
    full = ((-30, xb + TOWER_D + 5), (-90, 90), (0, Z_O + H + 10))
    render(os.path.join(HERE, "preview.png"), [
        (robot, 22, -60, f"xsx + {N_BALLS}-ball box", full),
        (robot + [(tower, GREY, 0.3)], 0, -90, f"side: blade touches the tower ({TOWER_H} mm rim)", full),
        ([(bw, AMBER, 1), (rw, TAN, 1), (tw, RED, 1), (fw, (0.6, 0.1, 0.6), 1)], -30, -55,
         "hole, trapdoor + trigger (from below)", ((X_O - 90, X_O + 70), (-75, 75), (Z_O - 25, Z_O + 40)))])
