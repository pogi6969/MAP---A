#!/usr/bin/env python3
"""MR.D 16ch line follower chassis (new design). One printed part, no brackets:
- rear body with 2 built-in N20 tunnel mounts (gearbox plate, M1.6 x 2), wheels 32 x 12 outside
- 4 standoffs for a Cytron MOTION 2350 Pro (95.2 x 57.2, M3, assumed 88 x 48) sitting low behind nothing
- hexagon lightening pockets, centre wire slot
- triangulated delta truss (Warren) to the sensor head: stiff + light
- 16ch sensor head 156 wide with 2 rows of slots (board holes 50-140 mm apart), 2 M3 holes for a ball caster / skids,
  raised 'MR.D' logo on top.  Plate 3 mm, x forward, y left, z up."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, FillRule, Manifold, set_circular_segments
set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))
T = 3.0                                            # plate thickness
BX0, BX1, BW = -22.0, 66.0, 48.0                   # body x range, half width
AX, MY0, MY1, OW = -12.0, 20.0, 44.5, 3.0          # motor axis x, N20 y range, gearbox plate
HX0, HX1, HW = 160.0, 182.0, 78.0                  # sensor head x range, half width
BOARD = (6.0, 95.2, 57.2)                          # MOTION 2350 Pro rear x, size
SO = [(BOARD[0] + 4.6, 44.0), (BOARD[0] + 52.6, 44.0)]


def rrect(x0, x1, y0, y1, r): return CrossSection.square([x1 - x0 - 2 * r, y1 - y0 - 2 * r]).translate([x0 + r, y0 + r]).offset(r, join_type=__import__('manifold3d').JoinType.Round)
def circ(x, y, d): return CrossSection.circle(d / 2).translate([x, y])
def bar(p, q, w): return CrossSection.batch_hull([circ(*p, w), circ(*q, w)])
def hexa(x, y, r): return CrossSection.circle(r, 6).translate([x, y])
def both2(c): return c + c.mirror([0, 1])
def box(x0, x1, y0, y1, z0, z1): return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def cyly(x, z, y0, y1, d): return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])
def both(m): return m + m.mirror([0, 1, 0])


def plate():
    c = rrect(BX0, BX1, -BW, BW, 6) + rrect(HX0, HX1, -HW, HW, 5)
    L = [(BX1 - 4, 44.0), (HX0 + 4, 16.0)]                                         # side rail ends
    def lp(t): return (L[0][0] + t * (L[1][0] - L[0][0]), L[0][1] + t * (L[1][1] - L[0][1]))
    tr = bar(L[0], L[1], 7) + bar((BX1 - 4, 0), (HX0 + 4, 0), 7)                   # rails + spine
    zig = [lp(0), (BX1 + 17, 0), lp(0.36), (BX1 + 50, 0), lp(0.7), (BX1 + 80, 0), lp(1)]
    for a, b in zip(zig, zig[1:]): tr += bar(a, b, 5)                              # Warren diagonals
    c += both2(tr)
    for x, y in [(24, 22), (46, 22), (35, 0)]: c -= both2(hexa(x, y, 9))           # lightening pockets
    c -= rrect(-6, 2, -10, 10, 2)                                                  # wire slot
    for s in (1, -1):
        for x in (HX0 + 6, HX0 + 16): c -= CrossSection.batch_hull([circ(x, s * 25, 3.4), circ(x, s * 70, 3.4)])  # sensor slots
        c -= circ(HX0 + 11, s * 24, 3.2)                                           # caster / skid M3
    for x, y in SO: c -= both2(circ(x, y, 2.6))
    return Manifold.extrude(c, T)


def mounts():
    h = box(AX - 8.2, AX + 8.2, MY0, MY1, T, T + 12.9) - box(AX - 6.2, AX + 6.2, MY0 - 1, MY1, T - 0.01, T + 10.4)
    h += box(AX - 8.2, AX + 8.2, MY1, MY1 + OW, T, T + 12.9)
    h -= cyly(AX, T + 5.2, MY1 - 1, MY1 + OW + 1, 4.4)
    for dx in (-4.5, 4.5): h -= cyly(AX + dx, T + 5.2, MY1 - 1, MY1 + OW + 1, 1.8)
    m = both(h)
    for x, y in SO: m += both(Manifold.cylinder(6, 3.5).translate([x, y, T]) - Manifold.cylinder(7, 1.3).translate([x, y, T]))
    return m


def logo(text='MR.D', h=11.0):
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    tp = TextPath((0, 0), text, size=h, prop=FontProperties(family='DejaVu Sans', weight='bold'))
    cs = CrossSection([np.asarray(p) for p in tp.to_polygons() if len(p) > 2], FillRule.EvenOdd)
    b = cs.bounds(); cs = cs.translate([-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2]).rotate(-90)   # reads from behind
    return Manifold.extrude(cs.translate([HX0 + 11, 0]), 1.0).translate([0, 0, T])


CH = plate() + mounts() + logo()
WHEELS = both(cyly(AX, T + 5.2, MY1 + OW + 1.5, MY1 + OW + 13.5, 32))
MOT = both(box(AX - 6, AX + 6, MY0, MY1, T, T + 10))
BRD = box(BOARD[0], BOARD[0] + BOARD[2], -BOARD[1] / 2, BOARD[1] / 2, T + 6, T + 7.6)
if __name__ == '__main__':
    b = CH.bounding_box()
    print('size', np.round([b[3] - b[0], b[4] - b[1], b[5]], 1), 'parts', len(CH.decompose()), 'mot^ch', round((MOT ^ CH).volume(), 2),
          'wheel^ch', round((WHEELS ^ CH).volume(), 2), 'brd^ch', round((BRD ^ CH).volume(), 2), 'axis above ground (32 wheel)', 16, 'plate bottom', 16 - T - 5.2)
    me = CH.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
    open(os.path.join(HERE, 'MR.D_16ch_chassis.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '15%', '--perimeters', '2',
                    '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'MR.D_16ch_chassis.stl')], check=True, capture_output=True)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    Lt = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); fig = plt.figure(figsize=(15, 7))
    G = (0.75, 0.77, 0.8)
    for k, (items, view, title) in enumerate((([(CH, G)], (55, -120), 'MR.D 16ch chassis'),
                                              ([(CH, G), (WHEELS, (0.1, 0.1, 0.1)), (MOT, (0.95, 0.75, 0.2)), (BRD, (0.5, 0.2, 0.6))], (35, -55), 'With N20s, 32 x 12 wheels, MOTION 2350 Pro'))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tq = V[np.asarray(me.tri_verts)]
            n = np.cross(Tq[:, 1] - Tq[:, 0], Tq[:, 2] - Tq[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(Tq); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ Lt), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-30, 190); ax.set_ylim(-110, 110); ax.set_zlim(-90, 130); ax.set_box_aspect((1, 1, 1), zoom=1.5); ax.view_init(*view); ax.axis('off'); ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
