#!/usr/bin/env python3
"""Sumo chassis like the grey printed one (box, wedge front with 2 sensor windows, motors at the back), sized so the
Cytron MOTION 2350 Pro (95.2 x 57.2) drops in on top: it sits on front + rear ledges inside the walls, 4 x M3.
Assumed board holes 88 x 48 mm. 2 x N20, wheels 34 x 12 inside the walls. x forward, y left, z up, floor 0."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))
S, XR, XW = 50.0, -17.4, 45.2
ZF0, ZF1, H, ZBD = 0.6, 3.6, 40.0, 36.0          # floor, wall top, board underside
WH, WA = 26.0, 32.0
TIP = XW + (WH - ZF0) / np.tan(np.radians(WA))
AX, AZ, WD, WW = 6.0, 17.0, 34.0, 12.0
MW, MH, MY0, MY1, OW = 12.0, 10.0, 5.0, 29.5, 3.0
WY0, WY1 = 33.0, 47.0
BX0, BX1 = XR + 2.2, XW - 3.2                    # board x range (57.2)
HOLES = [(BX0 + 4.6, 44.0), (BX1 - 4.6, 44.0)]


def box(x0, x1, y0, y1, z0, z1): return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def cyl(x, y, z0, z1, d): return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])
def cyly(x, z, y0, y1, d): return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])
def both(m): return m + m.mirror([0, 1, 0])
def xz(pts, y0, y1):
    p = np.asarray(pts, float)
    if np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]) < 0: p = p[::-1]
    return Manifold.extrude(CrossSection([p.tolist()]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def chassis():
    m = box(XR, XW, -S, S, ZF0, ZF1) + both(box(XR, XW, S - 2, S, ZF0, H)) + box(XR, XR + 2, -S, S, ZF0, H) + box(XW - 3, XW, -S, S, ZF0, H)
    m += xz([(XW - 0.01, ZF0), (TIP, ZF0), (XW - 0.01, WH)], -S, S)                                  # wedge
    m += xz([(XR + 1.9, ZBD - 9), (XR + 1.9, ZBD), (XR + 11, ZBD)], -S + 1, S - 1)                   # rear board ledge (45 deg)
    m += xz([(XW - 2.9, ZBD - 9), (XW - 2.9, ZBD), (XW - 12, ZBD)], -S + 1, S - 1)                   # front board ledge
    h = box(AX - 9, AX + 9, MY0, MY1 + OW, ZF0, AZ + 8) - box(AX - 6.2, AX + 6.2, MY0 - 1, MY1, AZ - 5.2, AZ + 5.2)
    h -= cyly(AX, AZ, MY1 - 1, MY1 + OW + 1, 4.4)
    for dx in (-4.5, 4.5): h -= cyly(AX + dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)
    m += both(h)
    m -= both(box(AX - 18, AX + 18, WY0, WY1, -1, AZ) + cyly(AX, AZ, WY0, WY1, 37))                  # wheel wells
    for x, y in HOLES: m -= both(cyl(x, y, ZBD - 8, ZBD + 1, 2.6))                                   # board screws M3
    for y in (-25, 25): m -= box(XW - 4, TIP + 1, y - 11, y + 11, 6, 18)                             # 2 sensor windows through the wedge
    m -= box(XR - 1, XR + 3, -8, 8, ZBD + 0.5, H + 1)                                                # USB / wire notch at the back
    return m


CH = chassis()
BOARD = box(BX0, BX1, -47.6, 47.6, ZBD, ZBD + 1.6)
WHEELS = both(cyly(AX, AZ, WY0 + 1, WY0 + 1 + WW, WD))
if __name__ == '__main__':
    b = CH.bounding_box()
    print('size', round(b[3] - b[0], 1), round(b[4] - b[1], 1), round(b[5], 1), 'parts', len(CH.decompose()),
          'board^ch', round((BOARD ^ CH).volume(), 2), 'wheels^ch', round((WHEELS ^ CH).volume(), 2))
    me = CH.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, 'sumo_2350_chassis.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '20%', '--fill-pattern', 'gyroid',
                    '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'sumo_2350_chassis.stl')], check=True, capture_output=True)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); fig = plt.figure(figsize=(13, 6))
    for k, items in enumerate(([(CH, (0.7, 0.72, 0.75))], [(CH, (0.7, 0.72, 0.75)), (BOARD, (0.5, 0.2, 0.6)), (WHEELS, (0.1, 0.1, 0.1))])):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-35, 105); ax.set_ylim(-70, 70); ax.set_zlim(-50, 90); ax.set_box_aspect((1, 1, 1), zoom=1.4); ax.view_init(35, -50); ax.axis('off')
        ax.set_title(('Chassis', 'With MOTION 2350 Pro (purple) and wheels')[k])
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
