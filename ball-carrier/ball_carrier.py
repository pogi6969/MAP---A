#!/usr/bin/env python3
"""LineaViper-X16 (xsx.3mf) 30-ball dump box - ONE-PIECE print-in-place, no assembly.

Prints roof-down as a single job: box, gate, hinge, snap latch and the legs that peg into
your (unchanged) xsx chassis all come off the bed together.

  * Box: plain closed box, solid sides, tipped 8 deg nose-down; the floor is the ramp.
    The floor bridges onto a centre rail carried by thin posts (spans <= 70 mm).
  * Gate: the whole front, on a print-in-place hinge (cone pins, 0.4 mm gap) under the
    floor front. Two paddles hang from the hinge below the tower rim; gate + paddles are one
    rigid part, so pushing the paddles back swings the gate open (bell crank).
  * Latch: a flexible finger on each gate wing snaps over a bump on the box side. It holds
    the gate against the balls (also under braking) and lets go when the tower pushes the
    paddles; the balls then push the gate open and roll into the tower.
  * Reset: lift a side wing (they point up after a dump) - the gate swings shut and the
    fingers click over the bumps. Load the balls through the front with the gate open.

Physics and numbers: run the script, see DESIGN.md.

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
PUSH = 2 * 0.049 / 0.017         # N, robot push at stall: 2 x N20 1:50 (~0.5 kg.cm) on 34 mm wheels
# ---- box ----
TILT = 8                         # floor slope, deg (nose down)
HW = 70                          # inside half width
WT, FLOOR_T, ROOF_T = 0.8, 1.0, 0.8
RAIL_H, POST_D = 2.4, 5.0        # centre rail on the floor, posts carrying it (print support for the floor)
POSTS_U = [-10, -55, -100, -145]
REAR_X = -24                     # box rear (outside) X
AHEAD, CLEAR = 16, 20            # paddles ahead of the arm tips; floor edge above the tower rim
FRONT_X = 104                    # front legs near this X (arm hole column)
MU = 0.3                         # PLA on PLA
GAP = 0.4                        # print-in-place clearance
# ---- gate, hinge, latch (bin frame u, w) ----
A2 = (-9.0, -15.2)               # hinge axis under the floor front
KNUCKLE = (24.4, 32.0)           # gate knuckles / paddles, |v|
LUGS = [(18.0, 24.0), (32.4, 38.0)]   # fixed lugs either side of each knuckle, |v|
CONE_R = 2.2                     # 45 deg cone pins
PADDLE_W = -50                   # paddle bottom
FINGER = (-8.0, -4.0, 12.5, 28.5)     # snap finger in each wing: u0, u1, tip w, root w (length 16)
BUMP = (-6.0, 14.5, 1.0)         # bump on the box side under the finger hole: u, w, radius
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
X_E = TIP + AHEAD + 9.6                           # floor front edge (paddle face 9.6 mm behind it)
Z_E = TOWER_H + CLEAR
U_R = (REAR_X - X_E) / CA + WT                    # rear wall inside face
U0, HWO = U_R - WT, HW + WT
GW = HWO + GAP + 1.2                              # gate half width (covers the wings)


def world(m):
    return m.rotate([0, TILT, 0]).translate([X_E, 0, Z_E])


def to_bin(m):
    return m.translate([-X_E, 0, -Z_E]).rotate([0, -TILT, 0])


def floor_z(x):                                   # box underside at X
    return Z_E + (X_E - x) * SA / CA


def about(m, c, deg):                             # rotate about an axis along v through c=(u, w); + = gate opens
    return m.translate([-c[0], 0, -c[1]]).rotate([0, deg, 0]).translate([c[0], 0, c[1]])


def both(m):
    return m + m.mirror([0, 1, 0])


def cone_v(u, w, v0, d, r0, h):                   # cone along v from v0 (radius r0) in direction d (+1/-1)
    c = Manifold.cylinder(h, r0, 0.05).rotate([-90 * d, 0, 0])
    return c.translate([u, v0, w])


def pile(h, n_max):
    """Drop balls one at a time into the lowest free spot (gravity tilted TILT deg in the bin
    frame) inside the closed box, around the posts, stacking on the balls already there."""
    r, d = BALL_D / 2, BALL_D + 0.3
    U, V = (a.ravel() for a in np.meshgrid(np.arange(U_R + r + 0.3, -r - 0.6, 2.5), np.arange(-HW + r + 0.3, HW - r - 0.3, 2.5)))
    keep = np.ones(len(U), bool)
    for up in POSTS_U:
        keep &= (U - up) ** 2 + V ** 2 > (r + POST_D / 2 + 0.3) ** 2
    U, V = U[keep], V[keep]
    W = np.full(len(U), FLOOR_T + r) + np.where(np.abs(V) < 12, RAIL_H, 0)   # balls near the rail sit on it
    out = []
    while len(out) < n_max:
        i = np.argmin(-U * SA + W * CA)
        if W[i] + r > h - ROOF_T:
            break
        out.append((U[i], V[i], W[i]))
        d2 = (U - U[i]) ** 2 + (V - V[i]) ** 2
        near = d2 < d * d
        W[near] = np.maximum(W[near], W[i] + np.sqrt(d * d - d2[near]))
    return out


DW = next(h for h in range(40, 200, 5) if len(pile(h, N_BALLS)) >= N_BALLS)   # box height


def legs():
    """Legs (world frame) from the box underside to the chassis plate, pegs into existing holes."""
    arm = HOLES[3.2]
    top, bot = arm[arm[:, 1] > 0], arm[arm[:, 1] < 0]
    ft = top[np.argmin(abs(top[:, 0] - FRONT_X))]
    front = [ft, bot[np.argmin(abs(bot[:, 0] - ft[0]))]]
    zt, m = PLATE_Z + 4, Manifold()
    for (x, y), peg, dx in [(p, 2.9, -1) for p in front] + [(p, 3.7, 1) for p in HOLES[4.0]]:
        top_z = floor_z(x) + 3
        m += box(x - 3, x + 3, y - 3, y + 3, zt, top_z) + box(x - 4.5, x + 4.5, y - 4.5, y + 4.5, zt, zt + 2)
        m += cyl(x, y, zt - 3.8, zt + 0.1, peg)
        sy = -np.sign(y)
        for (bx, by) in ((dx * 26, 0), (0, sy * 26)):                 # braces, >= 45 deg so they print
            p, q = np.array([x, y, zt + 12]), np.array([x + bx, y + by, floor_z(x + bx) + 3])
            n = q - p
            L = np.linalg.norm(n)
            b = Manifold.cube([4, 4, L], center=True).translate([0, 0, L / 2])
            ax = np.degrees(np.arctan2(np.hypot(n[0], n[1]), n[2]))
            az = np.degrees(np.arctan2(n[1], n[0]))
            m += b.rotate([0, ax, 0]).rotate([0, 0, az]).translate(list(p))
    return m


# ---- the print (bin frame) ----
def box_body():
    m = box(U0, 0, -HWO, HWO, 0, DW) - box(U_R, 5, -HW, HW, FLOOR_T, DW - ROOF_T)
    m += box(U_R, 0, -1.5, 1.5, FLOOR_T - 0.1, FLOOR_T + RAIL_H)                            # centre rail
    for u in POSTS_U:
        m += cyl(u, 0, FLOOR_T, DW - ROOF_T + 0.1, POST_D)
    lug_cs = poly([(A2[0] - 4, 0.5), (A2[0] + 4, 0.5), (A2[0] + 4, A2[1]), (A2[0] - 4, A2[1])]) \
        + CrossSection.circle(4, 40).translate(list(A2))
    for lo, hi in LUGS:                                                                     # fixed hinge lugs
        lug = ext_cs_v(lug_cs, lo, hi)
        if hi <= KNUCKLE[0]:
            lug += cone_v(*A2, hi, +1, CONE_R, CONE_R)
        else:
            lug += cone_v(*A2, lo, -1, CONE_R, CONE_R)
        m += both(lug)
    bump = Manifold.sphere(BUMP[2], 24).translate([BUMP[0], HWO, BUMP[1]]) ^ box(-50, 50, HWO - 0.1, HWO + 5, -50, 200)
    m += both(bump)
    m += to_bin(legs()) ^ box(-1000, 1000, -500, 500, -500, FLOOR_T - 0.1)
    return m


def gate_body():
    h = GW
    m = box(0.4, 1.2, -h, h, -4.6, DW) + (box(1.2, 3.0, -h, h, -4.6, DW) - box(1, 4, -h + 3, h - 3, -1.6, DW - 3))
    teardrop = CrossSection.circle(4, 40).translate(list(A2)) + poly(
        [(A2[0] - 2.83, A2[1] + 2.83), (A2[0], A2[1] + 5.66), (A2[0] + 2.83, A2[1] + 2.83)])
    t1 = (A2[0], A2[1] + 5.66)
    arm = poly([t1, (3.0, t1[1] + 3.0 - t1[0]), (3.0, -4.6), (A2[0] + 4, A2[1])])           # 45 deg top edge
    f0 = -7.0                                                                              # paddle face, world vertical
    paddle = poly([(f0 - 4, A2[1] - 1), (f0, A2[1] - 1), (f0 + (A2[1] - 3.8 - PADDLE_W) * 0 + (-19 - PADDLE_W) * np.tan(np.radians(TILT)), PADDLE_W),
                   (f0 - 4 + (-19 - PADDLE_W) * np.tan(np.radians(TILT)), PADDLE_W)])
    k = ext_cs_v(teardrop + arm + paddle, *KNUCKLE)
    for lo, hi in LUGS:                                                                    # cone sockets
        if hi <= KNUCKLE[0]:
            k -= cone_v(*A2, KNUCKLE[0], +1, CONE_R + 0.85 - GAP, CONE_R + 0.85 - GAP)
        else:
            k -= cone_v(*A2, KNUCKLE[1], -1, CONE_R + 0.85 - GAP, CONE_R + 0.85 - GAP)
    m += both(k)
    v0, v1 = HWO + GAP, HWO + GAP + 1.2                                                    # wings + snap fingers
    wing = ext_v([(3.0, 47), (3.0, 6), (-30, 6), (-30, 14)], v0, v1)
    u0, u1, wt, wr = FINGER
    wing -= ext_v([(u0 - 0.8, wt - 0.8), (u1 + 0.8, wt - 0.8), (u1 + 0.8, wr), (u0 - 0.8, wr)], v0 - 1, v1 + 1)
    wing += ext_v([(u0, wt), (u1, wt), (u1, wr + 0.5), (u0, wr + 0.5)], v0, v1)
    wing -= cyl_v(BUMP[0], BUMP[1], v0 - 1, v1 + 1, 2 * BUMP[2] + 0.4)
    r = np.array([BUMP[0] - A2[0], BUMP[1] - A2[1]])                                      # bump path once the
    for a in np.radians(np.arange(7, 121, 2)):                                             # finger has let go
        q = np.array([r[0] * np.cos(a) - r[1] * np.sin(a), r[0] * np.sin(a) + r[1] * np.cos(a)]) + A2
        wing -= cyl_v(q[0], q[1], v0 - 1, v1 + 1, 2 * BUMP[2] + 0.6)
    m += both(wing)
    return m


BOX, GATE = box_body(), gate_body()
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


def physics(box_w, gate_w, balls_w):
    """Back-of-envelope checks, written to DESIGN.md."""
    g, M = 9.81, N_BALLS * BALL_G / 1000
    mb, mg = box_w.volume() * 1.24e-3, gate_w.volume() * 1.24e-3                      # thin walls print ~solid
    cb = np.mean([c for _, c in balls_w], axis=0)
    items = [(mb, centroid(box_w)), (mg, centroid(gate_w)), (N_BALLS * BALL_G, cb), (ROBOT_G, np.array([35.0, 0, ROBOT_Z]))]
    mt = sum(a for a, _ in items)
    cg = sum(a * c for a, c in items) / mt
    x_front = TIP - 5
    a_lat = 50 / cg[2]
    phi = np.radians(25)
    K = (1 - np.sin(phi)) / (1 + np.sin(phi))
    rho_b = 0.6 * BALL_G / (np.pi / 6 * BALL_D ** 3) * 1e6
    h = (max(w for u, v, w in BALLS if u > -BALL_D) + BALL_D / 2) / 1000
    hc = np.mean([w for u, v, w in BALLS]) / 1000
    a2 = -A2[1] / 1000                                                                     # hinge below the floor
    t_s = 0.5 * K * rho_b * g * h ** 2 * (2 * HW / 1000) * (h / 3 + a2)                    # Rankine push on the gate
    gc = centroid(GATE)
    t_gate = mg / 1000 * g * ((gc[2] - A2[1]) * SA + (gc[0] - A2[0]) * CA) / 1000          # gate weight (tilted frame)
    t_st = t_s + M * g * SA * (hc + a2) + t_gate
    t_d = t_st + M * 0.5 * g * (hc + a2)                                                   # + 0.5 g braking
    u0, u1, wt, wr = FINGER
    L, b, t = wr - wt, u1 - u0, 1.2
    k = 3 * 2.0e9 * (b / 1000 * (t / 1000) ** 3 / 12) / (L / 1000) ** 3                   # PLA E ~2 GPa (printed)
    eng = BUMP[2] - GAP
    f_th = k * eng / 1000 * np.tan(np.radians(45) + np.arctan(MU))
    r_det = np.hypot(BUMP[0] - A2[0], BUMP[1] - A2[1]) / 1000
    t_det = 2 * f_th * r_det
    arm = (A2[1] - (-(TOWER_H + 0.0 - Z_E) + PADDLE_W) / 2 * 0 - (PADDLE_W + (TOWER_H - Z_E)) / 2) / -1000 * -1
    w_c = ((TOWER_H - Z_E) + PADDLE_W) / 2                                                 # paddle contact, mid overlap
    arm = (A2[1] - w_c) / 1000
    f_rel = t_det / arm
    strain = 3 * t * eng / (2 * L ** 2)
    v_run, rho_air = 1.5, 1.2
    area = 2 * HWO / 1000 * DW / 1000
    drag = 0.5 * rho_air * v_run ** 2 * 1.05 * area
    lines = [
        "# Ball carrier - design notes (generated by ball_carrier.py)", "",
        "One-piece print-in-place: box, gate, hinge, snap latch and legs print together, roof down, no supports, "
        "no assembly. Moving parts are separated by a 0.4 mm gap.", "",
        f"Payload: {N_BALLS} x {BALL_D} mm balls = {N_BALLS * BALL_G:.0f} g. Print: {mb + mg:.0f} g at 100 % "
        f"(box + legs {mb:.0f} g, gate {mg:.0f} g). Robot estimate: {ROBOT_G} g. Total {mt:.0f} g.", "",
        "## Capacity",
        f"Balls dropped one by one into the lowest free spot (gravity tilted {TILT} deg), around the posts: "
        f"{len(pile(DW, 999))} fit inside the {DW} mm tall box, so {N_BALLS} have margin. Inside {-U_R:.0f} x {2 * HW} mm.", "",
        "## Stability and traction",
        f"CG of robot + full box: x = {cg[0]:.0f} mm (drive axle at 0), z = {cg[2]:.0f} mm; "
        f"{100 * (x_front - cg[0]) / x_front:.0f} % on the drive wheels.",
        f"Side tip-over at a_lat = {a_lat:.2f} g -> max {np.sqrt(a_lat * 9.81 * 0.15):.2f} m/s on a 150 mm "
        f"radius curve, {np.sqrt(a_lat * 9.81 * 0.3):.2f} m/s on 300 mm.", "",
        "## Gate, latch and release",
        f"Opening moment on the gate about the hinge ({-A2[1]:.0f} mm below the floor): ball bed (Rankine K = {K:.2f}, "
        f"{rho_b:.0f} kg/m3) {t_s * 1000:.0f} N.mm + down-slope weight + gate weight = {t_st * 1000:.0f} N.mm static, "
        f"{t_d * 1000:.0f} N.mm with 0.5 g braking.",
        f"Snap fingers: {L:.0f} x {b:.0f} x {t} mm, k = {k:.0f} N/m each, bump engages {eng:.1f} mm -> "
        f"{f_th:.2f} N each at {r_det * 1000:.0f} mm = {t_det * 1000:.0f} N.mm hold "
        f"({t_det / t_d:.1f}x the braking case). Finger strain {100 * strain:.2f} % (PLA ok < 2 %).",
        f"Release: paddles {-(PADDLE_W - A2[1]):.0f} mm below the hinge, tower contact ~{arm * 1000:.0f} mm below it -> "
        f"{f_rel:.1f} N push; robot at stall ~{PUSH:.1f} N ({PUSH / f_rel:.1f}x). The paddles stick out {AHEAD} mm "
        "ahead of the arm tips; the floor edge is 9.6 mm further, over the tower.",
        "Once the fingers let go, the balls and the gate's own weight swing it open; it stops ~110 deg open, "
        "a chute into the tower.", "",
        "## Reset and loading",
        "After a dump the side wings point up: lift one and the gate swings shut, the fingers click over the bumps. "
        "To load, open the gate, tip the robot back and pour the balls in, then close it.", "",
        "## Printing (one job, no supports)",
        "Roof down on the bed (smooth top). Walls vertical; the floor bridges <= 70 mm onto the centre rail, "
        "which bridges <= 52 mm between posts. Hinge: 45 deg cone pins and teardrop knuckles. Legs and pegs "
        "point up. Wings rise at 45 deg. Gaps 0.4 mm: if the gate is stuck after printing, flex it gently once.", "",
        f"Drag at {v_run} m/s: {drag:.3f} N ({100 * drag / PUSH:.1f} % of the drive force) - negligible.", "",
        "## Assumptions (change at the top of ball_carrier.py)",
        f"Balls {BALL_D} mm / {BALL_G} g; tower rim {TOWER_H} mm, opening wider than {2 * HW} mm; chassis underside "
        f"{PLATE_Z} mm above the floor; robot push {PUSH:.1f} N.",
    ]
    open(os.path.join(HERE, "DESIGN.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    bw, gw = world(BOX), world(GATE)
    bl = [world(Manifold.sphere(BALL_D / 2, 24).translate([u, v, w])) for u, v, w in BALLS]
    bm = sum(bl[1:], bl[0])
    print("components: box", len(BOX.decompose()), "gate", len(GATE.decompose()))
    det = both(box(-12, 0, HWO - 0.1, HWO + 3, 5, 25))                                # finger/bump zone
    stop = None
    for ang in (0, 3, 10, 30, 60, 90, 100, 110, 120, 130):
        o = (about(GATE, A2, ang) ^ BOX)
        o_ex = (o - det).volume()
        print(f"gate {ang:3d} deg: overlap {o.volume():.2f} (outside latch zone {o_ex:.2f})")
        if o_ex > 0.5 and stop is None:
            stop = ang
    print("balls/parts", round((bm ^ (bw + gw)).volume(), 2), "box/chassis", round((bw ^ CH).volume(), 2),
          "gate/chassis closed/open", round((gw ^ CH).volume(), 2), round((world(about(GATE, A2, 110)) ^ CH).volume(), 2))
    low = box(-500, 500, -300, 300, -1, TOWER_H)
    print("frontmost below the rim: box", round((bw ^ low).bounding_box()[3], 1), "gate", round((gw ^ low).bounding_box()[3], 1),
          "floor edge", round(X_E, 1))
    physics(bw, gw, [(BALL_G, centroid(b)) for b in bl])

    part = (BOX + GATE).rotate([180, 0, 0])
    part = part.translate([0, 0, -part.bounding_box()[2]])
    write_stl(part, os.path.join(HERE, "ball_box_one_piece.stl"))
    write_3mf(os.path.join(HERE, "ball_box_one_piece.3mf"), [("ball_box", part)], [(1, 128, 128)])
    b = part.bounding_box()
    print(f"  ball_box_one_piece: {b[3]-b[0]:.1f} x {b[4]-b[1]:.1f} x {b[5]-b[2]:.1f} mm, {part.volume()/1000:.1f} cm3")

    xb = TIP + AHEAD
    tr = TOWER_D / 2
    tower = (Manifold.cylinder(TOWER_H, tr) - Manifold.cylinder(TOWER_H, tr - 3).translate([0, 0, 2]))
    wheel = Manifold.cylinder(8, 17).rotate([90, 0, 0])
    wheels = wheel.translate([0, 54.3, PLATE_Z - 5]) + wheel.translate([0, -46.3, PLATE_Z - 5])
    BLUE, SHELL, ACCENT, GREY, BLACK = ((0.0, 0.47, 0.84), (0.25, 0.28, 0.33), (0.95, 0.35, 0.1),
                                       (0.45, 0.45, 0.5), (0.2, 0.2, 0.2))
    gopen = world(about(GATE, A2, 110))
    full = ((-35, xb + TOWER_D), (-95, 95), (0, Z_E + DW + 40))
    pb = part.bounding_box()
    render(os.path.join(HERE, "preview.png"), [
        ([(CH, BLUE, 1), (wheels, BLACK, 1), (bw, SHELL, 1), (gw, ACCENT, 1)], 22, -60, f"one-piece {N_BALLS}-ball box", full),
        ([(CH, BLUE, 1), (wheels, BLACK, 1), (bw, SHELL, 1), (gopen, ACCENT, 1), (tower.translate([xb - 3 + tr, 0, 0]), GREY, 0.35)],
         0, -90, "tower pushes the paddles: gate swings open", full),
        ([(BOX.rotate([180, 0, 0]).translate([0, 0, -pb[2]]), SHELL, 1), (GATE.rotate([180, 0, 0]).translate([0, 0, -pb[2]]), ACCENT, 1)],
         25, -125, "prints as one piece, roof down", ((pb[0] - 5, pb[3] + 5), (pb[1] - 5, pb[4] + 5), (0, pb[5] + 5)))])
