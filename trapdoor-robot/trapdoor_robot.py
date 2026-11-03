#!/usr/bin/env python3
"""Trapdoor ball robot: new chassis (xsx-style arms) + 30-ball hopper with a floor trapdoor that drops
the balls the moment the bumper touches the tower. All printed, no supports.

  * Tower 150 x 100 x 100, met on its 150 side. Arms + skids pass beside it; hopper floor 10 mm above it.
  * Hopper: open top, 45 deg back slope, flat trapdoor hinged at its front edge (print-in-place cone pins).
  * Bumper: flexible PETG plate on the chassis front; its tongue holds the door's rear edge. The tower
    bends it ~3.4 mm -> tongue slips out -> door drops, balls fall into the tower.
  * Backing away, the tower wall flips the hanging door forward, out under the front wall (no jam).
    Push the door up to re-latch (45 deg cam on the tongue, click).
Run: python3 trapdoor_robot.py -> STLs, CR-6 SE PETG G-code (prusa-slicer + cr6se_petg.ini), preview.png,
DESIGN.md. Axes: x forward, y left, z up, origin on the floor under the axle. mm.
"""
import os, re, glob, shutil, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))
BALL_D, BALL_G, N_BALLS = 40, 2.7, 30
WHEEL_D = 34
XC, ZF = 80.0, 110.0                    # tower near face, hopper underside (tower top = 100)
PT = 3.0                                # chassis plate
ZP = WHEEL_D / 2 + 5                    # plate underside (N20 under the plate)
AI, AO = 80.0, 88.0                     # arm inner / outer |y| (tower +-75 passes between)
XF = XC - 8                             # chassis front edge = hard stop 8 mm after first contact
SKID_X = XC + 65
WT, GAP = 0.8, 0.4                      # hopper skin, print-in-place gap
HW = 70.0                               # hopper inner half width (< tower inner 73.8)
DX0, DX1, HZ, KD = XC + 4.8, XC + 92.0, 3.0, 6.0   # door rear edge, hinge axis x / z, knuckle dia
BUMP_T, BUMP_W = 1.35, 60.0             # bumper plate thickness, width
TONGUE = DX0 + 4.6                      # tongue tip (4.6 mm under the door)
NUB = (84.0, 98.0)                      # contact nub z range
POST_L = ZF - (ZP + PT)


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def xz(pts, y0, y1):                    # (x, z) polygon extruded along y
    p = np.asarray(pts, float)
    if np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]) < 0:
        p = p[::-1]
    return Manifold.extrude(CrossSection([p.tolist()]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def cone_y(x, z, ya, yb, da, db):       # frustum on an axis || y: diameter da at ya -> db at yb
    if ya > yb:
        ya, yb, da, db = yb, ya, db, da
    return Manifold.cylinder(yb - ya, da / 2, db / 2).rotate([-90, 0, 0]).translate([x, ya, z])


def both(m):
    return m + m.mirror([0, 1, 0])


def pile(h, n_max=200):
    """Lowest-free-spot ball drop inside the hopper (door + 45 deg slope), balls below the rim."""
    r, d = BALL_D / 2, BALL_D + 0.3
    U, V = (a.ravel() for a in np.meshgrid(np.arange(XC + 3 - h + r, DX1 - r, 2.0), np.arange(-HW + r, HW - r + 0.1, 2.0)))
    flat, slope = 1.6 + 3 + r, lambda x: (XC + 3 - x) + WT * 1.5 + r * np.sqrt(2)
    W = np.maximum(flat, slope(U))
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


H = next(h for h in range(60, 200, 5) if len(pile(h, N_BALLS)) >= N_BALLS)
XR = XC + 3 - H                          # hopper rear (top of the slope)
POSTS = [(XC + 50, 84.0), (max(XR + 12, 25.0), 84.0)]


# ---------------- hopper (own frame: z = world z - ZF; prints as built) ----------------
def hopper(fin=True):
    m = both(xz([(XR, 0), (XC + 96.6, 0), (XC + 96.6, H), (XR, H)], HW, HW + WT))      # side walls
    m += box(XC + 95.4, XC + 96.6, -HW - 0.1, HW + 0.1, 6.4, H)                     # front wall (door flips out under it)
    m += xz([(XC + 3, 0), (XC + 3 + WT * 1.5, 0), (XR + WT * 1.5, H), (XR, H)], -HW - 0.1, HW + 0.1)  # 45 deg slope
    for px, py in POSTS:                                                            # post brackets
        m += both(box(px - 7, px + 7, HW, py + 6, 0, 3) - box(px - 2.2, px + 2.2, py - 2.2, py + 2.2, -1, 4))
    m += both(cone_y(DX1, HZ, 64, HW + 0.1, KD, KD) + cone_y(DX1, HZ, 62, 64.5, 0.4, 5.4))   # fixed knuckle + 45 deg pin
    if fin:                                                                         # break-off support, snap off after print
        m += box(XC + 95.4, XC + 96.6, -HW + 0.5, HW - 0.5, 0, 6.2)
    return m


def door():
    m = box(DX0, DX1, -HW + GAP, HW - GAP, 0, 1.6)
    m -= both(box(DX1 - 3.4, DX1 + 1, 64 - GAP, HW, -1, 3))                         # clear the fixed knuckles
    for y in (-45, -15, 15, 45):                                                    # stiffening ribs
        m += box(DX0 + 2, DX1 - 4, y - 0.6, y + 0.6, 1.5, 4.5)
    m += box(DX0, DX0 + 1.5, -60, 60, 1.5, 4.5)                                     # rear edge rib (latch edge)
    m += both(cone_y(DX1, HZ, 50, 64 - GAP, KD, KD))                               # knuckles
    return m - both(cone_y(DX1, HZ, 61.6, 63.8, 0.732, 5.132))                      # pin sockets, 0.4 gap


# ---------------- chassis (world frame) ----------------
def chassis():
    body = CrossSection.square([XF + 45, 2 * AO]).translate([-45, -AO])
    arm = CrossSection.square([SKID_X + 8 - XF, AO - AI]).translate([XF, AI])
    m = Manifold.extrude(body + arm + arm.mirror([0, 1]), PT).translate([0, 0, ZP])
    z0, z1 = ZP - 1, ZP + PT + 1
    cut = [both(box(-20, 20, AI - 1, AO + 1, z0, z1)),                              # wheel wells
           box(-12, 12, -25, 25, z0, z1),                                           # wiring window
           box(XF - 6.7, XF - 3.3, -BUMP_W / 2 - 0.2, BUMP_W / 2 + 0.2, z0, z1)]     # bumper rib slot
    cut += [both(cyl(sx, 73, z0, z1, 3.2)) for sx in (-9.75, 9.75)]                 # your N20 brackets (19.5)
    cut += [both(cyl(x, 34.5, z0, z1, 3.4)) for x in (-39.9, -1.9)]                 # MCB (xsx pattern)
    cut += [both(box(px - 2.2, px + 2.2, py - 2.2, py + 2.2, z0, z1)) for px, py in POSTS]
    cut += [both(box(XC - 30, XC - 24, 70 - 1.6, 70 + 1.6, z0, z1))]                # sensor bar slots
    for c in cut:
        m -= c
    skid = (cyl(0, 0, 3, ZP + 0.1, 10) + Manifold.sphere(5, 24).translate([0, 0, 5])) ^ box(-6, 6, -6, 6, 0, 99)
    return m + both(skid.translate([SKID_X, 84, 0]))


def bumper():
    t0, zb = XF - BUMP_T, ZP + PT
    prof = [[(t0, zb), (XF, zb), (XF, ZF - 0.4), (t0, ZF - 0.4)],                    # flexible plate
            [(XF - 10, zb), (XF, zb), (XF, zb + 2.5), (XF - 10, zb + 2.5)],          # base flange
            [(XF - 6.5, ZP + 0.5), (XF - 3.5, ZP + 0.5), (XF - 3.5, zb + 0.1), (XF - 6.5, zb + 0.1)],  # rib -> slot
            [(XF - 0.1, NUB[0]), (XC, NUB[0] + 4), (XC, NUB[1] - 2), (XF - 0.1, NUB[1])],          # contact nub
            [(t0, ZF - 6), (TONGUE - 5.6, ZF - 6), (TONGUE, ZF - 0.4), (t0, ZF - 0.4)]]            # tongue, 45 deg cam
    m = Manifold()
    for p in prof:
        m += xz(p, -BUMP_W / 2, BUMP_W / 2)
    return m


def post():
    return box(-4, 4, -4, 4, 0, POST_L) + box(-2, 2, -2, 2, -3, 0.1) + box(-2, 2, -2, 2, POST_L - 0.1, POST_L + 3)


HOP, HOP0, DOOR, CH, BUMP, POST = hopper(), hopper(False), door(), chassis(), bumper(), post()
POSTW = sum((POST.translate([px, s * py, ZP + PT]) for px, py in POSTS for s in (-1, 1)), Manifold())
TOWER = box(80, 180, -75, 75, 0, 100) - box(81.2, 178.8, -73.8, 73.8, 1.6, 101)


def door_at(a):                          # a < 0 opens (rear edge down); -180 = flipped out front
    return DOOR.translate([-DX1, 0, -HZ]).rotate([0, a, 0]).translate([DX1, 0, HZ])


def up(m):
    return m.translate([0, 0, ZF])


def tris(m):
    me = m.to_mesh()
    return np.asarray(me.vert_properties)[:, :3][np.asarray(me.tri_verts)]


def write_stl(m, name):
    T = tris(m).astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])
    rec['n'], rec['v'] = n, T
    with open(os.path.join(HERE, name), 'wb') as f:
        f.write(b'\0' * 80 + np.uint32(len(T)).tobytes() + rec.tobytes())


def centroid(m):
    T = tris(m).astype(float)
    vol = np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])) / 6
    return (vol[:, None] * T.sum(1) / 4).sum(0) / vol.sum()


def floor0(m):
    b = m.bounding_box()
    return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    v = lambda m: round(m.volume(), 2)
    balls = pile(H)
    print('H', H, 'balls fit', len(balls), 'posts', POSTS)
    print('door x hopper at 0..-180 deg', [v(HOP0 ^ door_at(a)) for a in (0, -30, -60, -90, -120, -150, -180)])
    print('bumper x hop/door/chassis', v(BUMP ^ up(HOP)), v(BUMP ^ up(DOOR)), v(BUMP ^ CH),
          '| posts x chassis/hop', v(POSTW ^ CH), v(POSTW ^ up(HOP)))
    print('tower x robot', v(TOWER ^ (CH + BUMP + up(HOP) + up(DOOR) + POSTW)))
    print('components', [len(m.decompose()) for m in (HOP, DOOR, CH, BUMP, POST)])

    # ---- print-ready STLs ----
    write_stl(HOP + DOOR, 'hopper_door.stl')                                        # as built, door on the bed
    write_stl(floor0(CH.rotate([180, 0, 0])), 'chassis.stl')                        # upside down, skids up
    B, P = floor0(BUMP.rotate([90, 0, 0])), floor0(POST.rotate([0, 90, 0]))         # bumper on its side, posts lying
    bx = B.bounding_box()[3] + 8
    write_stl(B + sum((P.translate([bx, 12 * i, 0]) for i in range(4)), Manifold()), 'bumper_posts.stl')

    # ---- G-code ----
    info, ps = {}, shutil.which('prusa-slicer')
    if ps:
        for g in glob.glob(os.path.join(HERE, '*.gcode')):
            os.remove(g)
        for name in ('hopper_door', 'chassis', 'bumper_posts'):
            subprocess.run([ps, '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg.ini'), '--center', '122.5,117.5',
                            '--output', HERE, os.path.join(HERE, name + '.stl')], check=True, capture_output=True)
            g = glob.glob(os.path.join(HERE, name + '_PETG_*.gcode'))[0]
            with open(g, 'rb') as f:
                f.seek(max(0, os.path.getsize(g) - 300000))
                tail = f.read().decode(errors='ignore')
            info[name] = (float(re.search(r'filament used \[g\] = ([\d.]+)', tail).group(1)),
                          re.search(r'estimated printing time \(normal mode\) = (.+)', tail).group(1).strip(), os.path.basename(g))
            print(name, info[name])
    gr = lambda k, vol: info[k][0] if k in info else vol * 1.27e-3

    # ---- mass, CG, loads ----
    vh, vd, vb, vp = HOP0.volume(), DOOR.volume(), BUMP.volume(), POST.volume()
    g_hd, g_bp = gr('hopper_door', vh + vd), gr('bumper_posts', vb + 4 * vp)
    bc = np.mean(balls[:N_BALLS], axis=0) + [0, 0, ZF]
    BAT_X = 30.0
    items = [(g_hd * vh / (vh + vd), centroid(up(HOP0))), (g_hd * vd / (vh + vd), centroid(up(DOOR))),
             (gr('chassis', CH.volume()), centroid(CH)), (g_bp * vb / (vb + 4 * vp), centroid(BUMP)),
             (g_bp * 4 * vp / (vb + 4 * vp), centroid(POSTW)),
             (24, (0, 0, 17)), (20, (0, 0, 17)), (30, (-21, 0, 35)), (95, (BAT_X, 0, 40)), (20, (XC - 27, 0, 12)),
             (N_BALLS * BALL_G, bc)]
    M = sum(m for m, _ in items)
    cg = sum(m * np.asarray(c, float) for m, c in items) / M
    wheel = (SKID_X - cg[0]) / SKID_X
    E, t = 2000.0, BUMP_T                                     # PETG
    I = BUMP_W * t ** 3 / 12
    a = np.mean(NUB) - (ZP + PT + 2.5)
    f = 1 + 1.5 * ((ZF - 3.2) - np.mean(NUB)) / a             # tongue / nub deflection ratio
    d_rel = 4.6 / f
    k = 3 * E * I / a ** 3
    on_door = [b for b in balls[:N_BALLS] if b[0] > DX0]
    Mh = (g_hd * vd / (vh + vd)) * (DX1 - centroid(DOOR)[0]) + sum(BALL_G * (DX1 - b[0]) for b in on_door)
    Nt = Mh / (DX1 - DX0 - 2.3) * 9.81e-3
    F = k * d_rel + 0.4 * Nt
    strain = 3 * t * 8.0 / (2 * a * a)

    # ---- preview ----
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])

    def draw(ax, parts, title):
        for m, col, al in parts:
            T = tris(m)
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
            n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            fc = np.clip(np.outer(0.45 + 0.55 * np.abs(n @ L), col), 0, 1)
            ax.add_collection3d(Poly3DCollection(T, facecolors=np.c_[fc, np.full(len(T), al)], edgecolors='none'))
        ax.set_xlim(-60, 200), ax.set_ylim(-130, 130), ax.set_zlim(0, 260), ax.set_box_aspect((1, 1, 1))
        ax.view_init(20, -60), ax.axis('off'), ax.set_title(title)

    ballm = sum((Manifold.sphere(19.8, 14).translate([x, y, z + ZF]) for x, y, z in balls[:N_BALLS]), Manifold())
    base = [(CH, (0.25, 0.25, 0.28), 1), (POSTW, (0.3, 0.3, 0.35), 1), (BUMP, (0.95, 0.55, 0.1), 1),
            (TOWER, (0.6, 0.75, 0.9), 0.35)]
    fig = plt.figure(figsize=(13, 6.5))
    draw(fig.add_subplot(121, projection='3d'), base + [(up(HOP0), (0.2, 0.55, 0.85), 0.55), (up(DOOR), (0.9, 0.2, 0.2), 1),
                                                        (ballm, (1, 1, 0.9), 1)], f'Loaded, at the tower ({N_BALLS} balls)')
    draw(fig.add_subplot(122, projection='3d'), base + [(up(HOP0), (0.2, 0.55, 0.85), 0.55), (up(door_at(-90)), (0.9, 0.2, 0.2), 1)],
         'Bumper pressed -> trapdoor open')
    plt.tight_layout()
    plt.savefig(os.path.join(HERE, 'preview.png'), dpi=110)

    # ---- DESIGN.md ----
    row = lambda k, how: f"| `{k}.stl` | {how} | {info[k][0]:.0f} g | {info[k][1]} | `{info[k][2]}` |" if k in info else f"| `{k}.stl` | {how} | | | |"
    open(os.path.join(HERE, 'DESIGN.md'), 'w').write(f"""# Trapdoor ball robot — dispenses on contact

![preview](preview.png)

CR-6 SE, PETG, 0.2 mm, **supports off** (G-code ready, profile `cr6se_petg.ini`).

| file | print as | PETG | time | G-code |
|---|---|---|---|---|
{row('hopper_door', 'as is: open top up, door on the bed (hinge prints in place)')}
{row('chassis', 'as is: upside down, skids up')}
{row('bumper_posts', 'as is: bumper on its side + 4 posts lying')}

## How it works
1. Robot drives at the tower's 150 mm face. Arms + skids pass beside the tower (5 mm each side); hopper floor is 10 mm above the tower top.
2. Bumper nub hits the tower → PETG plate bends back → its tongue slides out from under the door's rear edge after {d_rel:.1f} mm → trapdoor swings down, balls drop straight into the tower. 45° back slope feeds the last ones.
3. Chassis front edge is the hard stop, 8 mm after first contact.
4. Backing away: the tower wall pushes the hanging door forward; it flips out under the front wall (no jam).
5. Reset: push the door up — the 45° cam on the tongue clicks it shut.

## After printing / assembly
* Snap off the thin fin under the hopper's front wall (support for that wall). Work the door a few times.
* 4 posts: square tenons into the chassis and hopper bracket holes (drop of CA glue).
* Bumper: rib into the chassis front slot (glue).
* Your N20 brackets: 2 × M3 each (19.5 mm holes, axle at x = 0). MCB on the xsx hole pattern. Sensor bar on the front slots.
* Battery centre ~{BAT_X:.0f} mm in front of the axle.

## Numbers
| | |
|---|---|
| capacity | {len(balls)} balls of 40 mm fit below the rim (hopper {H} mm tall, top at {ZF + H:.0f} mm) |
| trapdoor | {DX1 - DX0:.0f} × {2 * (HW - GAP):.0f} mm, hinge Ø{KD:.0f} knuckles, 45° cone pins, 0.4 mm gaps |
| release | nub travel {d_rel:.1f} mm, push ≈ {F:.1f} N (spring {k:.2f} N/mm + friction), plate strain {100 * strain:.2f} % at 8 mm (PETG yield ≈ 3 %) |
| mass | ≈ {M:.0f} g loaded (assumed: N20 ×2, wheels, MCB 30 g, battery 95 g, sensor bar 20 g) |
| CG | x = {cg[0]:.0f} mm, z = {cg[2]:.0f} mm → {100 * wheel:.0f} % of weight on the drive wheels |
| tipping | sideways {84 / cg[2]:.2f} g, forward (braking) {(SKID_X - cg[0]) / cg[2]:.2f} g, backward {cg[0] / cg[2]:.2f} g |
""")
    print(f'M {M:.0f} g  cg {cg.round(1)}  wheel {wheel:.2f}  release {d_rel:.2f} mm {F:.2f} N  strain {strain:.4f}')
