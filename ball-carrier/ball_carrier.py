#!/usr/bin/env python3
"""LineaViper-X16 (xsx.3mf) 30-ball dump box - all 3D printed, chassis unchanged.

A plain closed box (tray + lift-off lid, solid walls, no holes in the sides) tipped 8 deg
nose-down over the wheelbase; its floor is the ramp. The whole front is a gate on a square
hinge shaft that runs across the front, outside the box.

Dump: a ratchet disc on the shaft is held by a gravity pawl under the box front. The tower
pushes the pawl paddle back ~5 mm, the tooth drops out of the notch (release force = friction
only), the balls push the gate open and roll off the floor edge into the tower.
Reset: push either side lever down. The gate closes and the counterweighted pawl drops into
the notch by itself - click, armed. The levers also show the state (up = dumped).

Physics and numbers: run the script, see DESIGN.md.
Parts: tray, lid, gate, ratchet disc, 2 levers, shaft, latch block, pawl, pawl pin, 2 frames.
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
WT, RAIL_H, TIE_T = 0.8, 2.6, 1.2               # skin (2 perimeters), floor rails (> 2.1 mm ball sag), ties
REAR_X = -24                     # bin rear (outside) X
AHEAD, CLEAR = 16, 15            # pawl paddle ahead of the arm tips, floor edge above the tower rim
FRONT_X = 104                    # front frame near this X (arm hole column)
MU = 0.3                         # PLA on PLA
# ---- hinge, ratchet, reset lever (bin frame u, w) ----
A = (4.0, 4.0)                   # hinge shaft axis, ahead of the box front (no holes in the side walls)
SQ = 3.0                         # square shaft
R_CUT = 4.6                      # floor edge relief so the gate can swing
GATE_W0 = 1.8                    # gate bottom edge
RD, ND = 7.5, 2.2                # ratchet disc radius, notch depth
P = (-7.0, -3.0)                 # pawl pivot: ~level with the notch face -> load passes (just) below it
LUGS = [(30, 36), (54, 60)]      # tray bearing lugs |v|
KNUCKLES = [(40, 50)]            # gate knuckles |v| (keyed to the shaft)
CHEEK = (2.3, 4.3)               # latch block cheeks |v|
DISC_V, PAWL_V = 2.0, 1.8        # ratchet disc / pawl half thickness
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


def ext_cs_v(cs, v0, v1):        # (u, w) cross-section extruded along v
    return Manifold.extrude(cs, v1 - v0).rotate([90, 0, 0]).translate([0, v1, 0])


def ext_cs_u(cs, u0, u1):        # (v, w) cross-section extruded along u
    return ext_x(cs, u0, u1)


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


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
TIP = CH.bounding_box()[3]
X_E = TIP + AHEAD + 7.0                           # floor front edge (paddle face sits 7 mm behind it)
Z_E = TOWER_H + CLEAR
U_R = (REAR_X - X_E) / CA + WT                    # rear wall inside face
U0, HWO = U_R - WT, HW + WT
LEVER_V = (HWO + 0.6, HWO + 3.6)


def world(m):
    return m.rotate([0, TILT, 0]).translate([X_E, 0, Z_E])


def floor_z(x):                                   # bin underside at X
    return Z_E + (X_E - x) * SA / CA


def about(m, c, deg):                             # rotate about an axis along v through c=(u, w); + = front down
    return m.translate([-c[0], 0, -c[1]]).rotate([0, deg, 0]).translate([c[0], 0, c[1]])


def diamond(c, v0, v1, s=SQ + 0.1):               # keyed square hole, 45 deg so it prints without support
    return ext_cs_v(CrossSection.square([s, s], center=True).rotate(45).translate(list(c)), v0, v1)


def cyl_a(v0, v1, d, c=A):
    return cyl_v(c[0], c[1], v0, v1, d)


def both(f):                                      # build at +v and mirror to -v
    m = f(1)
    return m + m.mirror([0, 1, 0])


def pile(h, n_max):
    """Drop balls one at a time into the lowest free spot (gravity tilted TILT deg in the bin
    frame) inside the closed box, stacking on the balls already there."""
    r, d = BALL_D / 2, BALL_D + 0.3
    U, V = (a.ravel() for a in np.meshgrid(np.arange(U_R + r + 0.3, -r - 0.6, 2.5), np.arange(-HW + r + 0.3, HW - r - 0.3, 2.5)))
    W = np.full(len(U), 3.2 + r)
    out = []
    while len(out) < n_max:
        i = np.argmin(-U * SA + W * CA)
        if W[i] + r > h - WT:
            break
        out.append((U[i], V[i], W[i]))
        d2 = (U - U[i]) ** 2 + (V - V[i]) ** 2
        near = d2 < d * d
        W[near] = np.maximum(W[near], W[i] + np.sqrt(d * d - d2[near]))
    return out


DW = next(h for h in range(40, 200, 5) if len(pile(h, N_BALLS)) >= N_BALLS)   # box height
W_SPLIT = DW - 25                                 # tray / lid joint


# ---- printed parts (bin frame) ----
def body_parts(frame_us):
    outer = box(U0, 0, -HWO, HWO, 0, DW)
    shell = outer - box(U_R, 5, -HW, HW, -5, DW - WT)
    slab = box(U0 - 10, 20, -HWO - 10, HWO + 10, W_SPLIT, DW + 10)
    lid = shell ^ slab
    tray = shell - slab
    for s in (-1, 1):                                                                      # lid locating tabs, in the
        for u0, u1 in ((U_R, U_R + 8), (-9, -0.5)):                                        # corners balls never reach
            tray += box(u0, u1, *sorted((s * (HW - 1), s * HW)), W_SPLIT - 3, W_SPLIT + 5)
        tray += box(U_R, U_R + 1, *sorted((s * (HW - 8), s * HW)), W_SPLIT - 3, W_SPLIT + 5)
    fl = CrossSection.square([-U0, 2 * HWO]).translate([U0, -HWO])
    grid = CrossSection()                                                                  # floor: rails + ties
    for v in np.arange(-63, 64, 18):
        grid += CrossSection.square([-U0, 2]).translate([U0, v - 1])
    grid += fl - fl.offset(-3, JoinType.Miter)                                             # rim
    ties = CrossSection()
    for u in np.arange(-4, U0, -36):
        ties += CrossSection.square([3, 2 * HW]).translate([u - 3, -HW])
    pads = CrossSection.square([16, 12]).translate([-20, -6])                              # latch block seat
    for u in frame_us:
        pads += CrossSection.square([6, 2 * HW]).translate([u - 2, -HW])                   # frame bars
    tray += Manifold.extrude(grid ^ fl, RAIL_H) + Manifold.extrude(ties ^ fl, TIE_T) + Manifold.extrude(pads ^ fl, 3.2)
    tray -= cyl_a(-HW, HW, 2 * R_CUT)                                                      # gate swing relief (walls intact)
    tray -= box(-4.2, 1, -4.8, 4.8, -1, 6)                                                 # ratchet disc / block
    for lo, hi in LUGS:                                                                    # shaft bearings
        lug = ((cyl_a(lo, hi, 8.6) + box(-2, A[0], lo, hi, 0, A[1])) - cyl_a(lo - 1, hi + 1, 4.7)) ^ box(-5, 10, lo, hi, 0, 20)
        tray += lug + lug.mirror([0, 1, 0])
    for u in frame_us:
        for v in (-40, 40):
            tray -= box(u - 1.45, u + 1.45, v - 1.45, v + 1.45, -1, 4.5)                   # frame pegs (8 deg tilt)
    return tray, lid


def gate_part():
    m = box(0.3, 1.1, -HWO, HWO, GATE_W0, DW)                                              # 0.8 mm skin
    m += box(1.1, 3.0, -HWO, HWO, GATE_W0, DW) - box(0, 4, -HWO + 3, HWO - 3, GATE_W0 + 3, DW - 3)   # border
    for lo, hi in LUGS:
        m -= both(lambda s: box(0, 4, *sorted((s * (lo - 0.5), s * (hi + 0.5))), 0, A[1] + 4.8))
    m -= box(0, 4, -4.8, 4.8, 0, A[1] + RD + 0.3)                                          # ratchet disc + block
    m -= both(lambda s: box(0, 9, *sorted((s * (HW - 0.5), s * (HWO + 1))), 0, A[1] + 4.8))  # clear the side walls
    for lo, hi in KNUCKLES:                                                                # keyed knuckles
        m += both(lambda s: cyl_a(*sorted((s * lo, s * hi)), 7.6) + box(0.3, A[0], *sorted((s * lo, s * hi)), A[1], A[1] + 3.5))
    return m - diamond(A, -HWO, HWO)


def disc_part():
    d = cyl_a(-DISC_V, DISC_V, 2 * RD)
    notch = ext_v([(A[0] + 1.2, A[1] - RD - 1), (A[0] + 1.2, A[1] - RD + ND), (A[0] - 0.8, A[1] - RD + ND),
                   (A[0] - 2.8, A[1] - RD - 1)], -DISC_V - 1, DISC_V + 1)
    return d - notch - diamond(A, -DISC_V - 1, DISC_V + 1)


def lever_part():
    hub = cyl_a(*LEVER_V, 11)
    arm = ext_v([(A[0], A[1] - 3), (A[0], A[1] + 3), (-70, A[1] + 3), (-70, A[1] - 3)], *LEVER_V)
    tab = cyl_v(-74, A[1] + 4, *LEVER_V, 14)
    return hub + arm + tab - diamond(A, LEVER_V[0] - 1, LEVER_V[1] + 1)


def block_part():
    cheek = (ext_v([(A[0] - 1, A[1] + 3.5), (A[0] + 2, A[1] - 2), (P[0] + 2.5, P[1] - 3.5), (P[0] - 3.5, P[1] - 3.5),
                    (-16, -3.0), (-16, 0), (A[0] - 4.5, 0)], *CHEEK) + cyl_a(*CHEEK, 9) + cyl_v(*P, *CHEEK, 5.6))
    return cheek - cyl_a(-5, 5, 4.7) - cyl_v(*P, -5, 5, 3.2)                              # one cheek; tail seats on the floor


def pawl_part():
    """Gravity pawl: tooth in the ratchet notch, paddle hits the tower, counterweight tail behind."""
    t0 = A[1] - RD + ND - 0.2                                                              # tooth top
    pts = [(P[0], P[1] + 2.6), (A[0] - 1.0, -4.8), (A[0] - 0.6, -4.8), (A[0] - 0.6, t0), (A[0] + 0.8, t0),
           (A[0] + 0.8, -7.5), (P[0] + 3.5, -7.5), (-4.9, -15.5), (-3.0, -29), (-6.5, -29),
           (P[0] - 1.5, -10), (-30, -10.5), (-30, -3.6), (P[0] - 3, -3.6)]
    m = ext_v(pts, -PAWL_V, PAWL_V) + cyl_v(*P, -PAWL_V, PAWL_V, 5.6) - cyl_v(*P, -5, 5, 3.2)
    return m - ext_v([(-5.0, -14), (-4.2, -26), (-5.6, -26), (-6.2, -14)], -5, 5)          # lighten the paddle


def shaft_part():
    return box(-(HWO + 4), HWO + 4, -SQ / 2, SQ / 2, 0, SQ)                                # lies flat


def pawl_pin():
    return cyl(0, 0, 0, 2 * CHEEK[1] + 0.4, 3.0)


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
GATE, DISC, LEVER, BLOCK, PAWL = gate_part(), disc_part(), both(lambda s: lever_part()), both(lambda s: block_part()), pawl_part()
SHAFT_W = ext_cs_v(CrossSection.square([SQ, SQ], center=True).rotate(45).translate(list(A)), -HWO - 4, HWO + 4)
BALLS = pile(DW, N_BALLS)


def mech(gate_deg=0.0, pawl_deg=0.0):
    """Moving parts in the bin frame: gate + disc + levers + shaft turn about A, pawl about P."""
    g = sum((about(m, A, gate_deg) for m in (DISC, LEVER, SHAFT_W)), about(GATE, A, gate_deg))
    return g, about(PAWL, P, pawl_deg)


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




def centroid(m):
    t = tris(m).astype(float)
    v = np.einsum("ij,ij->i", t[:, 0], np.cross(t[:, 1], t[:, 2])) / 6
    return (v[:, None] * t.sum(1) / 4).sum(0) / v.sum()


def tooth_drop_deg():
    """Pawl rotation that drops the tooth top below the disc periphery (+0.3 mm)."""
    r = np.array([A[0] + 0.8 - P[0], A[1] - RD + ND - 0.2 - P[1]])
    target = A[1] - RD - 0.3 - P[1]
    return next(d for d in np.arange(0, 60, 0.1)
                if -r[0] * np.sin(np.radians(d)) + r[1] * np.cos(np.radians(d)) < target)


def physics(parts_w, balls_w):
    """Back-of-envelope checks, written to DESIGN.md."""
    g, M = 9.81, N_BALLS * BALL_G / 1000                                   # SI
    masses = [(m.volume() * 1.24e-3, centroid(m)) for m in parts_w]       # thin walls print ~solid
    mp = sum(a for a, _ in masses)
    cb = np.mean([c for _, c in balls_w], axis=0)
    items = masses + [(N_BALLS * BALL_G, cb), (ROBOT_G, np.array([35.0, 0, ROBOT_Z]))]
    mt = sum(a for a, _ in items)
    cg = sum(a * c for a, c in items) / mt
    x_front = TIP - 5                                                     # sensor-bar skid
    a_lat = 50 / cg[2]                                                    # wheels at +-50 mm
    phi = np.radians(25)                                                  # ball-ball repose angle
    K = (1 - np.sin(phi)) / (1 + np.sin(phi))
    rho_b = 0.6 * BALL_G / (np.pi / 6 * BALL_D ** 3) * 1e6                # kg/m3, random packing 0.6
    h = (max(w for u, v, w in BALLS if u > -BALL_D) + BALL_D / 2) / 1000
    hc = (np.mean([w for u, v, w in BALLS]) - A[1]) / 1000
    t_s = 0.5 * K * rho_b * g * h ** 2 * (2 * HW / 1000) * (h / 3 - A[1] / 1000)
    t_d = t_s + M * g * SA * hc + M * 0.5 * g * hc
    rf = (RD - ND / 2) / 1000                                             # notch face radius
    f_s, f_d = t_s / rf, t_d / rf
    e = (A[1] - RD + ND / 2 - P[1]) / 1000                                # self-locking arm
    lt = (A[0] - P[0]) / 1000                                             # pivot -> tooth
    lp = (P[1] + 22) / -1000 * -1 if False else 0.020                     # pivot -> paddle contact
    rel = [(f * e + MU * f * lt) / lp for f in (f_s, f_d)]
    push = 2 * 0.049 / 0.017                                              # 2 x N20 1:50 stall ~0.5 kg.cm, 34 mm wheel
    pc = centroid(PAWL)
    rg = (pc[0] - P[0], pc[2] - P[1])
    drop = tooth_drop_deg()
    stroke = np.hypot(3.0 - P[0], -22 - P[1]) * np.radians(drop + 2)
    v_run, rho_air = 1.5, 1.2
    area = 2 * HWO / 1000 * DW / 1000
    drag = [0.5 * rho_air * v_run ** 2 * cd * area for cd in (1.05, 0.8)]
    lines = [
        "# Ball carrier - design notes (generated by ball_carrier.py)", "",
        f"Payload: {N_BALLS} x {BALL_D} mm balls = {N_BALLS * BALL_G:.0f} g. Printed parts: {mp:.0f} g "
        f"(at 100 %, thin walls print solid). Robot estimate: {ROBOT_G} g. Total {mt:.0f} g.", "",
        "## Capacity",
        f"Balls dropped one by one into the lowest free spot (gravity tilted {TILT} deg): {len(pile(DW, 999))} fit "
        f"inside the closed {DW} mm tall box, so {N_BALLS} have margin. Inside: {-U_R:.0f} x {2 * HW} mm.", "",
        "## Stability and traction",
        f"CG of robot + full box: x = {cg[0]:.0f} mm (drive axle at 0), z = {cg[2]:.0f} mm.",
        f"Load on the drive wheels: {100 * (x_front - cg[0]) / x_front:.0f} % (front skid at x = {x_front:.0f}).",
        f"Side tip-over at a_lat = {a_lat:.2f} g -> max {np.sqrt(a_lat * 9.81 * 0.15):.2f} m/s on a 150 mm "
        f"radius curve, {np.sqrt(a_lat * 9.81 * 0.3):.2f} m/s on 300 mm.", "",
        "## Discharge",
        f"The whole front ({2 * HW} x {DW} mm = {2 * HW / BALL_D:.1f} D wide) swings away, so no arch can form "
        "(arching needs a roofed outlet narrower than ~4-5 D).",
        f"Floor {TILT} deg on 2 mm rails: a ball's rolling resistance is < 1 deg, so every ball rolls out.", "",
        "## Latch: ratchet disc + gravity pawl",
        f"Ball bed on the gate (Rankine K = {K:.2f}, bulk density {rho_b:.0f} kg/m3, fill {h * 1000:.0f} mm): "
        f"{t_s * 1000:.0f} N.mm static; with down-slope weight and 0.5 g braking {t_d * 1000:.0f} N.mm.",
        f"Force on the notch face (r = {rf * 1000:.1f} mm): {f_s:.2f} N static, {f_d:.2f} N design. Its line passes "
        f"{e * 1000:.1f} mm above the pawl pivot, so the load presses the tooth deeper (self-locking).",
        f"Release force at the paddle (tooth friction mu = {MU} + locking moment, paddle arm {lp * 1000:.0f} mm): "
        f"{rel[0]:.2f}-{rel[1]:.2f} N; robot push at stall ~{push:.1f} N -> {push / rel[1]:.0f}x margin.",
        f"Release stroke: the pawl turns {drop:.0f} deg = ~{stroke:.0f} mm at the paddle; it sticks out {AHEAD} mm "
        "ahead of the arm tips.",
        f"Pawl CG is {-rg[0]:.1f} mm behind and {-rg[1]:.1f} mm below the pivot: gravity holds the tooth up and "
        f"re-arms it; a forward jerk would need {abs(rg[0] / rg[1]) if rg[1] else 99:.1f} g to lift it (unloaded).", "",
        "## Reset",
        "Push either side lever down (or lift the gate): the shaft turns the gate shut, the notch comes round "
        "under the tooth and the counterweighted pawl drops in - click, armed. Lever up = dumped.", "",
        "## Shell and aerodynamics",
        f"Plain closed box, {WT} mm skin, solid sides (the hinge shaft runs across the front, outside the box). "
        f"Ball pressure on the walls is only ~K.rho.g.h = {K * rho_b * g * h:.0f} Pa.",
        f"Drag at {v_run} m/s, frontal area {area * 1e4:.0f} cm2: {drag[0]:.3f} N (box, Cd ~1.05) - "
        f"{100 * drag[0] / push:.1f} % of the drive force. Mass and CG height matter far more for speed.", "",
        "## Printing (no supports)",
        "Tray floor down, lid roof down, gate inner face down, disc / levers / pawl / latch cheeks flat, "
        "shaft and pins lying / standing, frames flat. Lid drops onto 4 corner tabs inside the tray.", "",
        "## Assumptions (change at the top of ball_carrier.py)",
        f"Balls {BALL_D} mm / {BALL_G} g; tower rim {TOWER_H} mm with an opening wider than {2 * HW} mm; "
        f"chassis underside {PLATE_Z} mm above the floor.",
    ]
    open(os.path.join(HERE, "DESIGN.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    yw, lw = world(TRAY), world(LID)
    body, frames, blk = yw + lw, FRAME_F + FRAME_R, world(BLOCK)
    bl = [world(Manifold.sphere(BALL_D / 2, 24).translate([u, v, w])) for u, v, w in BALLS]
    bm = sum(bl[1:], bl[0])
    drop = tooth_drop_deg()
    checks = {}
    for name, (gd, pd) in {"armed": (0, 0), "released": (0, drop + 2), "dumped": (110, 0), "closing": (25, 0)}.items():
        g, pw = (world(m) for m in mech(gd, pd))
        if name in ("dumped", "closing"):                          # tooth rides on the disc rim
            pw = world(about(PAWL, P, drop))
        checks[name] = {"body/gate": (body ^ g).volume(), "block/gate": (blk ^ g).volume(),
                        "pawl/gate": (pw ^ g).volume(), "pawl/body": (pw ^ body).volume(),
                        "pawl/block": (pw ^ blk).volume()}
    checks["armed"].update({"block/body": (blk ^ body).volume(), "balls/parts": (bm ^ (body + world(GATE))).volume(),
                            "frames/body": (frames ^ body).volume(), "frames/chassis": (CH ^ frames).volume(),
                            "lever/frames": (world(LEVER) ^ frames).volume()})
    for k, v in checks.items():
        print(k, {a: round(b, 2) for a, b in v.items()})
    g0, p0 = (world(m) for m in mech(0, 0))
    below = [(n, m.bounding_box()[3]) for n, m in (("pawl", p0), ("gate+disc+levers", g0), ("box", body), ("block", blk))
             if (m ^ box(-500, 500, -200, 200, -1, TOWER_H)).volume() > 0]
    print("frontmost parts below the rim:", [(n, round((m ^ box(-500, 500, -200, 200, -1, TOWER_H)).bounding_box()[3], 1))
                                              for n, m in (("pawl", p0), ("gate+disc+levers", g0), ("box", body), ("block", blk))
                                              if (m ^ box(-500, 500, -200, 200, -1, TOWER_H)).volume() > 0],
          "floor edge x", round(X_E, 1))
    physics([yw, lw, world(GATE), world(DISC), world(LEVER), world(SHAFT_W), blk, p0, frames], [(BALL_G, centroid(b)) for b in bl])

    flat = lambda m: m.rotate([90, 0, 0])                          # v -> z
    parts = {"tray": TRAY, "lid": LID.rotate([180, 0, 0]), "gate": GATE.rotate([0, -90, 0]), "ratchet_disc": flat(DISC),
             "lever_x2": flat(lever_part()), "shaft": shaft_part(), "latch_cheek_x2": flat(block_part()), "pawl": flat(PAWL),
             "pawl_pin": pawl_pin(), "frame_front": FRAME_F.rotate([0, -90, 0]).rotate([0, 0, 90]),
             "frame_rear": FRAME_R.rotate([0, -90, 0]).rotate([0, 0, 90])}
    for name, m in parts.items():
        m = m.translate([0, 0, -m.bounding_box()[2]])
        parts[name] = m
        write_stl(m, os.path.join(HERE, name + ".stl"))
        b = m.bounding_box()
        print(f"  {name}.stl: {b[3]-b[0]:.1f} x {b[4]-b[1]:.1f} x {b[5]-b[2]:.1f} mm, {m.volume()/1000:.1f} cm3")
    write_3mf(os.path.join(HERE, "plate1_tray.3mf"), [("tray", parts["tray"])], [(1, 128, 128)])
    write_3mf(os.path.join(HERE, "plate2_lid.3mf"), [("lid", parts["lid"])], [(1, 128, 128)])
    names = ["gate", "frame_front", "frame_rear", "shaft", "lever_x2", "ratchet_disc", "latch_cheek_x2", "pawl", "pawl_pin"]
    write_3mf(os.path.join(HERE, "plate3_parts.3mf"), [(n, parts[n]) for n in names],
              [(1, 70, 75), (2, 128, 175), (3, 128, 227), (4, 128, 248), (5, 190, 30), (5, 190, 55), (6, 160, 85),
               (7, 190, 85), (7, 220, 85), (8, 220, 115), (9, 160, 115)])

    xb = TIP + AHEAD
    tr = TOWER_D / 2
    tower = (Manifold.cylinder(TOWER_H, tr) - Manifold.cylinder(TOWER_H, tr - 3).translate([0, 0, 2]))
    wheel = Manifold.cylinder(8, 17).rotate([90, 0, 0])
    wheels = wheel.translate([0, 54.3, PLATE_Z - 5]) + wheel.translate([0, -46.3, PLATE_Z - 5])
    BLUE, SHELL, ACCENT, GREY, WHITE, BLACK, PURPLE = ((0.0, 0.47, 0.84), (0.25, 0.28, 0.33), (0.95, 0.35, 0.1),
                                                       (0.45, 0.45, 0.5), (0.97, 0.97, 0.97), (0.2, 0.2, 0.2),
                                                       (0.55, 0.15, 0.6))
    base = [(CH, BLUE, 1), (frames, GREY, 1), (wheels, BLACK, 1), (blk, GREY, 1)]
    gd, pd = (world(m) for m in mech(110, 0))
    pd = world(about(PAWL, P, drop))
    full = ((-35, xb + TOWER_D), (-95, 95), (0, Z_E + DW + 50))
    render(os.path.join(HERE, "preview.png"), [
        (base + [(yw, SHELL, 1), (lw, SHELL, 1), (g0, ACCENT, 1), (p0, PURPLE, 1)], 22, -60, f"closed {N_BALLS}-ball box", full),
        (base + [(yw, SHELL, 1), (lw, SHELL, 1), (g0, ACCENT, 1), (p0, PURPLE, 1), (tower.translate([xb + tr, 0, 0]), GREY, 0.35)],
         0, -90, "armed, pawl touches the tower", full),
        (base + [(yw, SHELL, 1), (lw, SHELL, 1), (gd, ACCENT, 1), (pd, PURPLE, 1), (tower.translate([xb - 5 + tr, 0, 0]), GREY, 0.35)],
         0, -90, "dumped: gate open, lever up (push down to reset)", full)])
