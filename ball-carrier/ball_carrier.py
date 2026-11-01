#!/usr/bin/env python3
"""LineaViper-X16 (xsx.3mf) 30-ball dump bin - all 3D printed, chassis unchanged.

Engineering choices (numbers are printed when you run this, see DESIGN.md):
  * Low, tilted bin over the wheelbase: a plain tray tipped 8 deg nose-down; its floor is
    the ramp, so the payload sits as low and as far back as the chassis allows.
  * Open-face discharge: the whole front wall is a fold-down gate (full width x full
    height). No hole, so the balls cannot arch and jam.
  * Gravity powered, contact released: the balls push the gate forward; a spur on the gate
    rests on the trigger tongue. The tower pushes the blade back 12 mm, the tongue slides
    out from under the spur (release force = friction only, ~mu x spur load), the gate
    falls forward into the tower and the balls roll off the floor edge after it.
  * Closed shell (tray + lift-off lid, nothing exposed), 0.8 mm skin: the balls press on it
    with only ~20 Pa. 45 deg chamfered top edges and a rounded tail: lower drag, stiffer
    skin, and every surface prints without supports.
  * Floor = rails (2 mm wide, 18 mm pitch) the balls roll along, ties underneath.

Parts: tray, lid, gate, trigger, 2 hinge pins, 2 frames (pegs go into existing chassis holes).
All print without supports.

Set BALL_D / N_BALLS / TOWER_H / PLATE_Z for your setup and rerun:
    pip install manifold3d numpy matplotlib && python3 ball_carrier.py

Axes: X forward, Y left, Z up, origin on the floor under the motor axis. Units: mm.
Bin frame: u along the floor (0 = floor front edge, + forward), v = Y, w normal to the floor.
"""
import os
import re
import zipfile
import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, Mesh, set_circular_segments

set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- your setup ----
BALL_D, BALL_G, N_BALLS = 40, 2.7, 30   # ping-pong balls
TOWER_H, TOWER_D = 50, 160       # tower rim height above the floor, outside dia (preview only)
PLATE_Z = 22                     # chassis underside above the floor (N20 under the plate, 34 mm wheels)
ROBOT_G, ROBOT_Z = 110, 25       # chassis + motors + wheels + MCB + battery, its CG height (estimate)
# ---- bin ----
TILT = 8                         # floor slope, deg (nose down)
HW = 70                          # inside half width
WT, RAIL_H, TIE_T = 0.8, 2.6, 1.2               # shell skin (2 perimeters), floor rails (> 2.1 mm ball sag), ties
R_TAIL, CH_TOP, CH_REAR = 40, 18, 30            # rounded tail (plan), 45 deg chamfers: top edges, rear-top edge
REAR_X = -24                     # bin rear (outside) X
AHEAD, LIP, CLEAR = 16, 3, 6     # blade ahead of the arm tips, floor edge ahead of the blade, edge above rim
TRAVEL, PD = 12, 22              # trigger stroke to release, blade depth below the floor edge
HINGE = (3.3, 3.0)               # gate hinge axis (u, w)
FOOT_U = 11.0                    # spur foot (rests on the tongue tip)
FRONT_X = 104                    # front frame near this X (arm hole column)
MU = 0.3                         # PLA on PLA
SA, CA = np.sin(np.radians(TILT)), np.cos(np.radians(TILT))


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


def ext_cs_v(cs, v0, v1):        # (u, w) cross-section extruded along v
    return Manifold.extrude(cs, v1 - v0).rotate([90, 0, 0]).translate([0, v1, 0])


def ext_cs_u(cs, u0, u1):        # (v, w) cross-section extruded along u
    return ext_x(cs, u0, u1)


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def diamonds(u0, u1, w0, w1, a=9.0, s=2.4):
    """Diamond-truss holes (half-diagonal a, strut s) whose full shape fits in [u0,u1]x[w0,w1]."""
    p, out = 2 * a + s * np.sqrt(2), CrossSection()
    hole = CrossSection.square([a * np.sqrt(2)] * 2, center=True).rotate(45)
    for k, (cu, cw) in enumerate([(0, 0), (p / 2, p / 2)]):
        for x in np.arange(u0 + a + cu, u1 - a + 1e-6, p):
            for y in np.arange(w0 + a + cw, w1 - a + 1e-6, p):
                out += hole.translate([x, y])
    return out


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
X_E = CH.bounding_box()[3] + AHEAD + LIP          # floor front edge
Z_E = TOWER_H + CLEAR
U_R = (REAR_X - X_E) / CA + WT                    # rear wall inside face


def world(m):
    return m.rotate([0, TILT, 0]).translate([X_E, 0, Z_E])


def floor_z(x):                                   # bin underside at X
    return Z_E + (X_E - x) * SA / CA


BACK_UV = CrossSection.square([1000, 1000]).translate([-1000, -500])      # u <= 0
U0 = U_R - WT                                     # rear outside
HWO = HW + WT


def prof_side(h, d=0.0):          # (u, w), inset by d
    cs = poly([(U0, 0), (0, 0), (0, h), (U0 + CH_REAR, h), (U0, h - CH_REAR)])
    return cs.offset(-d, JoinType.Miter) if d else cs


def prof_plan(d=0.0):             # (u, v), rounded tail
    r, rect = R_TAIL, CrossSection.square([-U0, 2 * HWO]).translate([U0, -HWO])
    cs = (rect - CrossSection.square([r, 2 * HWO]).translate([U0, -HWO])
          + CrossSection.square([r, 2 * HWO - 2 * r]).translate([U0, -HWO + r])
          + CrossSection.circle(r, 64).translate([U0 + r, HWO - r]) + CrossSection.circle(r, 64).translate([U0 + r, -HWO + r]))
    return cs.offset(-d, JoinType.Round) if d else cs


def prof_cross(h, d=0.0):         # (v, w), chamfered top edges
    c = CH_TOP
    cs = poly([(-HWO, 0), (HWO, 0), (HWO, h - c), (HWO - c, h), (-HWO + c, h), (-HWO, h - c)])
    return cs.offset(-d, JoinType.Miter) if d else cs


def solid(h, d=0.0, open_front=False, open_bottom=False):
    """Body as the intersection of the side, plan and cross-section prisms, inset by d."""
    S, P, C = prof_side(h, d), prof_plan(d), prof_cross(h, d)
    if open_front:
        S += CrossSection.square([d + 6, h - d + 5]).translate([-d - 0.5, -5])
        P += CrossSection.square([d + 6, 2 * HW]).translate([-d - 0.5, -HW])
    if open_bottom:
        S += CrossSection.square([-U0 + 10, d + 5.5]).translate([U0, -5])
        C += CrossSection.square([2 * HW, d + 5.5]).translate([-HW, -5])
    return (ext_cs_v(S, -HWO - 5, HWO + 5) ^ Manifold.extrude(P, h + 10).translate([0, 0, -5])
            ^ ext_cs_u(C, U0 - 5, 10))


def pile(h, n_max):
    """Drop balls one at a time into the lowest free spot (gravity tilted TILT deg in the bin
    frame) inside the closed shell, stacking on the balls already there."""
    from matplotlib.path import Path
    r, d = BALL_D / 2, BALL_D + 0.3
    polys = [cs.offset(-(WT + r + 0.3), JoinType.Round).to_polygons() for cs in (prof_side(h), prof_plan(), prof_cross(h))]
    if not all(polys):
        return []
    paths = [Path(np.asarray(p[0])) for p in polys]
    U, V = (a.ravel() for a in np.meshgrid(np.arange(U_R, 0, 2.5), np.arange(-HW, HW, 2.5)))
    keep = paths[1].contains_points(np.c_[U, V])
    U, V = U[keep], V[keep]
    W = np.full(len(U), 3.2 + r)                 # rails, band and frame bars top
    out = []
    while len(out) < n_max:
        i = np.argmin(-U * SA + W * CA)
        if not np.isfinite(W[i]):
            break
        if not (paths[0].contains_point((U[i], W[i])) and paths[2].contains_point((V[i], W[i]))):
            W[i] = np.inf
            continue
        out.append((U[i], V[i], W[i]))
        d2 = (U - U[i]) ** 2 + (V - V[i]) ** 2
        near = d2 < d * d
        W[near] = np.maximum(W[near], W[i] + np.sqrt(d * d - d2[near]))
    return out


DW = next(h for h in range(40, 200, 5) if len(pile(h, N_BALLS)) >= N_BALLS)   # body height
W_SPLIT = DW - max(CH_TOP, CH_REAR) - 8          # tray / lid joint


# ---- printed parts (bin frame) ----
def body_parts(frame_us):
    shell = solid(DW) - solid(DW, WT, True, True)
    slab = box(U0 - 10, 20, -HWO - 10, HWO + 10, W_SPLIT, DW + 10)
    lid = shell ^ slab
    lip = (solid(DW, WT, True, True) - solid(DW, WT + 1.0, True, True)) ^ box(U0 - 10, -0.1, -HWO - 10, HWO + 10,
                                                                             W_SPLIT - 3, W_SPLIT + 5)
    tray = (shell - slab) + lip
    for s in (-1, 1):                                                                      # hinge ears
        tray += box(-1, HINGE[0] + 4, *sorted((s * HW, s * HWO)), 0, HINGE[1] + 4)
    fl = prof_plan() ^ BACK_UV
    grid = CrossSection()                                                                  # floor: rails + ties
    for v in np.arange(-63, 64, 18):
        grid += CrossSection.square([-U0, 2]).translate([U0, v - 1])
    grid += fl - fl.offset(-3, JoinType.Miter)                                             # rim
    grid += CrossSection.square([62, 14]).translate([-62, -7])                             # trigger band
    for u in frame_us:
        grid += CrossSection.square([6, 2 * HW]).translate([u - 2, -HW])                   # frame bars
    ties = CrossSection()
    for u in np.arange(-4, U0, -36):
        ties += CrossSection.square([3, 2 * HW]).translate([u - 3, -HW])
    band = CrossSection.square([62, 14]).translate([-62, -7])
    for u in frame_us:
        band += CrossSection.square([6, 2 * HW]).translate([u - 2, -HW])
    tray += Manifold.extrude(grid ^ fl, RAIL_H) + Manifold.extrude(ties ^ fl, TIE_T) + Manifold.extrude(band ^ fl, 3.2)
    tray -= box(-44 - TRAVEL, 1, -4.2, 4.2, 1.2, 4.5)                                     # tongue recess
    tray -= box(-21 - TRAVEL - 1, 1, -1.7, 1.7, -1, 4.5)                                  # blade slot
    tray -= cyl_v(*HINGE, -HWO - 1, HWO + 1, 3.3)                                         # hinge pins
    for u in frame_us:
        for v in (-40, 40):
            tray -= box(u - 1.45, u + 1.45, v - 1.45, v + 1.45, -1, 4.5)                   # frame pegs (8 deg tilt)
    return tray, lid


def gate_part():
    out = prof_cross(DW, WT + 0.4) ^ CrossSection.square([300, DW]).translate([-150, 1.9])
    out -= CrossSection.square([12, 10]).translate([-6, 0])                                # tongue passes under
    m = ext_cs_u(out, 0.3, 1.1)                                                            # 0.8 mm skin
    frame_cs = out - out.offset(-3, JoinType.Miter)
    m += ext_cs_u(frame_cs, 1.0, 3.0)                                                      # raised border + rib
    for s in (-1, 1):                                                                      # knuckles
        m += cyl_v(*HINGE, *sorted((s * (HW - 6), s * (HW - 0.4))), 6)
    spur = box(1.5, FOOT_U, -5, 5, 3.6, 6.2) + box(FOOT_U - 2, FOOT_U, -5, 5, 3.1, 6.2)
    spur += ext_v([(1.5, 6.1), (6, 6.1), (1.5, 14)], -5, 5)                               # gusset
    return m + spur - cyl_v(*HINGE, -HW, HW, 3.5)


def gate_open(deg):
    return gate_part().translate([-HINGE[0], 0, -HINGE[1]]).rotate([0, deg, 0]).translate([HINGE[0], 0, HINGE[1]])


def trigger_part(pushed=0.0):
    blade = ext_v([(-21, -PD), (-LIP, -PD), (-LIP, 1.7), (-21, 1.7)], -1.5, 1.5)
    return (box(-44, FOOT_U + 0.5, -4, 4, 1.2, 3.1) + blade).translate([-pushed, 0, 0])


def pin():
    return cyl(0, 0, 0, 1.2, 6) + cyl(0, 0, 1.1, 1.2 + WT + 5.4, 3.0)


def frame(feet, peg):
    """Flat-printed support: feet with square pegs into chassis holes, beam + 2 pegs under the bin."""
    xh = float(np.mean(feet[:, 0]))
    zt, zs, hb = PLATE_Z + 4, floor_z(xh + 2.9), HW + WT
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
TRAY, LID = body_parts([(x - X_E) / CA for x in (XF, XR)])
GATE, TRIGGER = gate_part(), trigger_part()
BALLS = pile(DW, N_BALLS)


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



def centroid(m):
    t = tris(m).astype(float)
    v = np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])) / 6
    return (v[:, None] * t.sum(1) / 4).sum(0) / v.sum()


def physics(parts_w, balls_w):
    """Back-of-envelope checks, written to DESIGN.md."""
    g, M = 9.81, N_BALLS * BALL_G / 1000                                   # SI
    masses = [(m.volume() * 1.24e-3, centroid(m)) for m in parts_w]       # thin walls print ~solid
    mp = sum(a for a, _ in masses)
    cb = np.mean([c for _, c in balls_w], axis=0)
    items = masses + [(N_BALLS * BALL_G, cb), (ROBOT_G, np.array([35.0, 0, ROBOT_Z]))]
    mt = sum(a for a, _ in items)
    cg = sum(a * c for a, c in items) / mt
    x_front = CH.bounding_box()[3] - 5                                   # sensor-bar skid
    a_lat = 50 / cg[2]                                                    # wheels at +-50 mm
    # gate load: Rankine lateral pressure of the ball bed + down-slope weight + 0.5 g braking
    phi = np.radians(25)                                                  # ball-ball repose angle
    K = (1 - np.sin(phi)) / (1 + np.sin(phi))
    rho_b = 0.6 * BALL_G / (np.pi / 6 * BALL_D ** 3) * 1e6                # kg/m3, random packing 0.6
    h = (max(w for u, v, w in BALLS if u > -BALL_D) + BALL_D / 2) / 1000
    hc = (np.mean([w for u, v, w in BALLS]) - HINGE[1]) / 1000
    t_s = 0.5 * K * rho_b * g * h ** 2 * (2 * HW / 1000) * (h / 3 - HINGE[1] / 1000)
    t_d = t_s + M * g * SA * hc + M * 0.5 * g * hc
    arm = (FOOT_U - 1 - HINGE[0]) / 1000
    n_s, n_d = t_s / arm, t_d / arm
    sig = 6 * n_d * (FOOT_U / 1000) / (0.008 * 0.0019 ** 2) / 1e6
    push = 2 * 0.049 / 0.017                                              # 2 x N20 1:50 stall ~0.5 kg.cm, 34 mm wheel
    v_run, rho_air = 1.5, 1.2
    area = 2 * HWO / 1000 * DW / 1000
    drag = [0.5 * rho_air * v_run ** 2 * cd * area for cd in (1.05, 0.6)]
    lines = [
        "# Ball carrier - design notes (generated by ball_carrier.py)", "",
        f"Payload: {N_BALLS} x {BALL_D} mm balls = {N_BALLS * BALL_G:.0f} g. Printed parts: {mp:.0f} g "
        f"(at 100 %, thin walls print solid). Robot estimate: {ROBOT_G} g. Total {mt:.0f} g.", "",
        "## Capacity",
        f"Balls dropped one by one into the lowest free spot (gravity tilted {TILT} deg): {len(pile(DW, 999))} fit "
        f"inside the closed {DW} mm tall shell, so {N_BALLS} have margin. Inside: {-U_R:.0f} x {2 * HW} mm.", "",
        "## Stability and traction",
        f"CG of robot + full bin: x = {cg[0]:.0f} mm (drive axle at 0), z = {cg[2]:.0f} mm.",
        f"Load on the drive wheels: {100 * (x_front - cg[0]) / x_front:.0f} % (front skid at x = {x_front:.0f}).",
        f"Side tip-over at a_lat = {a_lat:.2f} g -> max {np.sqrt(a_lat * 9.81 * 0.15):.2f} m/s on a 150 mm "
        f"radius curve, {np.sqrt(a_lat * 9.81 * 0.3):.2f} m/s on 300 mm.", "",
        "## Discharge",
        f"Open face: the whole front ({2 * HW} x {DW} mm = {2 * HW / BALL_D:.1f} D wide, open to the top) "
        "falls away, so no arch can form (arching needs a roofed outlet narrower than ~4-5 D).",
        f"Floor {TILT} deg on 2 mm rails: rolling resistance of a ball is < 1 deg, so every ball rolls out; "
        "the pile above collapses as the front empties (repose ~25 deg).", "",
        "## Gate and trigger",
        f"Ball bed on the gate (Rankine K = {K:.2f}, bulk density {rho_b:.0f} kg/m3, fill {h * 1000:.0f} mm): "
        f"{t_s * 1000:.0f} N.mm static; with down-slope weight and 0.5 g braking {t_d * 1000:.0f} N.mm.",
        f"Spur foot on the tongue ({arm * 1000:.1f} mm from the hinge): {n_s:.2f} N static, {n_d:.2f} N design.",
        f"Release force = mu x load = {MU * n_s:.2f}-{MU * n_d:.2f} N; robot push at stall ~{push:.1f} N "
        f"-> {push / (MU * n_d):.0f}x margin. Stroke {TRAVEL} mm; blade sticks out {AHEAD} mm ahead of the arm tips.",
        f"Trigger stays put while driving: friction {MU * n_s:.2f} N vs its inertia at 1 g "
        f"{TRIGGER.volume() * 1.24e-3 * 9.81e-3:.3f} N.",
        f"Tongue bending at design load: {sig:.1f} MPa (PLA ~50 MPa).", "",
        "## Shell and aerodynamics",
        f"Closed shell, {WT} mm skin (2 perimeters). Ball pressure on it is only ~K.rho.g.h = "
        f"{K * rho_b * g * h:.0f} Pa, so a thin skin is enough; the chamfers and the rounded tail stiffen it.",
        f"Drag at {v_run} m/s, frontal area {area * 1e4:.0f} cm2: sharp box (Cd ~1.05) {drag[0]:.3f} N, "
        f"chamfered/rounded edges (Cd ~0.6) {drag[1]:.3f} N, i.e. {100 * drag[1] / push:.1f} % of the drive force. "
        "Shape helps a little; mass and CG height matter far more for speed.", "",
        "## Printing (no supports)",
        "Tray: floor down. Lid: upside down (roof on the bed), 45 deg chamfers. Gate: inner face down. "
        "Frames flat, trigger tongue down, pins standing. Lid drops over a 5 mm lip inside the tray.", "",
        "## Assumptions (change at the top of ball_carrier.py)",
        f"Balls {BALL_D} mm / {BALL_G} g; tower rim {TOWER_H} mm with an opening wider than {2 * HW} mm; "
        f"chassis underside {PLATE_Z} mm above the floor.",
    ]
    open(os.path.join(HERE, "DESIGN.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    yw, lw, gw, tw = world(TRAY), world(LID), world(GATE), world(TRIGGER)
    bw, frames = yw + lw, FRAME_F + FRAME_R
    bl = [world(Manifold.sphere(BALL_D / 2, 24).translate([u, v, w])) for u, v, w in BALLS]
    bm = sum(bl[1:], bl[0])
    gopen = world(gate_open(110))
    pairs = {"tray/lid": yw ^ lw, "body/gate": bw ^ gw, "body/trigger": bw ^ tw, "gate/trigger": gw ^ tw,
             "body/frames": bw ^ frames, "balls/parts": bm ^ (bw + gw), "frames/chassis": CH ^ frames,
             "open gate/body": gopen ^ bw, "open gate/pushed trigger": gopen ^ world(trigger_part(TRAVEL))}
    print("overlaps", {k: round(v.volume(), 2) for k, v in pairs.items()})
    physics([yw, lw, gw, tw, frames], [(BALL_G, centroid(b)) for b in bl])

    parts = {"tray": TRAY, "lid": LID.rotate([180, 0, 0]), "gate": GATE.rotate([0, -90, 0]),
             "trigger": TRIGGER.rotate([180, 0, 0]), "hinge_pin_x2": pin(),
             "frame_front": FRAME_F.rotate([0, -90, 0]).rotate([0, 0, 90]),
             "frame_rear": FRAME_R.rotate([0, -90, 0]).rotate([0, 0, 90])}
    for name, m in parts.items():
        m = m.translate([0, 0, -m.bounding_box()[2]])
        parts[name] = m
        write_stl(m, os.path.join(HERE, name + ".stl"))
        b = m.bounding_box()
        print(f"  {name}.stl: {b[3]-b[0]:.1f} x {b[4]-b[1]:.1f} x {b[5]-b[2]:.1f} mm, {m.volume()/1000:.1f} cm3")
    write_3mf(os.path.join(HERE, "plate1_tray.3mf"), [("tray", parts["tray"])], [(1, 128, 128)])
    write_3mf(os.path.join(HERE, "plate2_lid.3mf"), [("lid", parts["lid"])], [(1, 128, 128)])
    names = ["gate", "trigger", "hinge_pin_x2", "frame_front", "frame_rear"]
    write_3mf(os.path.join(HERE, "plate3_parts.3mf"), [(n, parts[n]) for n in names],
              [(1, 70, 75), (2, 200, 40), (3, 200, 100), (3, 220, 100), (4, 128, 175), (5, 128, 227)])

    xb = X_E - LIP
    tr = TOWER_D / 2
    tower = (Manifold.cylinder(TOWER_H, tr) - Manifold.cylinder(TOWER_H, tr - 3).translate([0, 0, 2]))
    wheel = Manifold.cylinder(8, 17).rotate([90, 0, 0])
    wheels = wheel.translate([0, 54.3, PLATE_Z - 5]) + wheel.translate([0, -46.3, PLATE_Z - 5])
    BLUE, SHELL, ACCENT, GREY, WHITE, BLACK, PURPLE = ((0.0, 0.47, 0.84), (0.25, 0.28, 0.33), (0.95, 0.35, 0.1),
                                                       (0.45, 0.45, 0.5), (0.97, 0.97, 0.97), (0.2, 0.2, 0.2),
                                                       (0.55, 0.15, 0.6))
    base = [(CH, BLUE, 1), (frames, GREY, 1), (wheels, BLACK, 1), (tw, PURPLE, 1)]
    full = ((-35, xb + TOWER_D), (-90, 90), (0, Z_E + DW + 40))
    render(os.path.join(HERE, "preview.png"), [
        (base + [(yw, SHELL, 1), (lw, SHELL, 1), (gw, ACCENT, 1)], 22, -60, f"closed {N_BALLS}-ball bin", full),
        (base + [(yw, SHELL, 1), (bm, WHITE, 1), (gw, ACCENT, 1)], 22, -60, f"lid off: {N_BALLS} balls inside", full),
        ([(CH, BLUE, 1), (frames, GREY, 1), (wheels, BLACK, 1), (yw, SHELL, 1), (lw, SHELL, 1), (gopen, ACCENT, 1),
          (world(trigger_part(TRAVEL)), PURPLE, 1), (tower.translate([xb - TRAVEL + tr, 0, 0]), GREY, 0.35)],
         0, -90, f"tower contact, pushed {TRAVEL} mm: gate drops", full)])
