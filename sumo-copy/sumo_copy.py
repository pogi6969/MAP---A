#!/usr/bin/env python3
"""Copy of the reference grey sumo chassis (5 photos): main box with thick front wall + tapered 40 deg blade, 2 screw
holes on the front top, rear wall stubs leaving a centre opening to a narrower tail; tail = floor + 2 pinch-ring N20
clamps (slit ring, 2 ears, 2 x M2 pinch screws each) + rear bar with 2 screw holes; side walls end in wheel arcs.
No sensor windows. Wheels 32 x 12 (N20_32x12 hub + mold) in the rear notches. x forward, y left, z up, ground 0."""
import os, glob, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
S, H, ZF0, ZF1 = 50.0, 28.0, 0.6, 3.0             # half width, wall top, floor bottom / top
XB, XF, WA, BT = 0.0, 41.0, 40.0, 40.0            # main box rear, front wall front, blade angle, blade tip half width
TIP = XF + (H - ZF0 - 0.8) / np.tan(np.radians(WA))
AX, AZ, WD, WW, RA = -13.0, 16.0, 32.0, 12.0, 17.5 # wheel / motor axis, wheel dia + width, wheel arc radius
TW, GW = 36.0, 24.0                                # tail half width, rear opening half width
RO, RI, RY0, RY1 = 18.5, 12.3, 11.0, 24.0          # clamp ring OD / ID (N20 can), ring y range
XBAR = AX - RO / 2 - 5                             # rear bar back face


def box(x0, x1, y0, y1, z0, z1): return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def cyl(x, y, z0, z1, d): return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])
def cyly(x, z, y0, y1, d): return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])
def cylx(x0, x1, y, z, d): return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])
def both(m): return m + m.mirror([0, 1, 0])


def chassis():
    m = box(XB, XF, -S, S, ZF0, ZF1) + both(box(XB, XF, S - 2, S, ZF0, H)) + box(XF - 6, XF, -S, S, ZF0, H)
    m += both(box(XB, XB + 2, GW, S - 1, ZF0, H))                                                     # rear wall stubs
    m += Manifold.hull(Manifold.compose([box(XF - 0.01, XF, -S, S, ZF0, H), box(TIP - 0.01, TIP, -BT, BT, ZF0, ZF0 + 0.8)]))  # blade
    m += box(XBAR, XB + 1, -TW, TW, ZF0, ZF1) + box(XBAR, AX - RO / 2 + 0.5, -TW, TW, ZF0, H)          # tail floor + rear bar
    c = cyly(AX, AZ, RY0, RY1, RO) + box(AX - 7, AX + 7, RY0, RY1, ZF0, AZ)                           # clamp ring on pedestal
    c += box(AX - 4, AX - 1, RY0 - 1, RY1 + 1, AZ + 4, H + 1) + box(AX + 1, AX + 4, RY0 - 1, RY1 + 1, AZ + 4, H + 1)  # ears
    m += both(c)
    m -= both(cyly(AX, AZ, TW + 0.5, S + 1, 2 * RA))                                                  # wheel arcs
    k = cyly(AX, AZ, RY0 - 2, RY1 + 2, RI) + box(AX - 1, AX + 1, RY0 - 2, RY1 + 2, AZ + 3, H + 2)      # bore + slit
    for y in (RY0 + 2.5, RY1 - 2.5): k += cylx(AX - 5, AX + 5, y, AZ + 10.8, 2.2)                    # M2 pinch screws
    m -= both(k + cyl(AX - RO / 2 - 2.5, TW - 4, H - 10, H + 1, 2.6) + cyl(XF - 3, S - 6, H - 10, H + 1, 2.6))  # top holes
    return m


CH = chassis()
WHEELS = both(cyly(AX, AZ, TW + 1, TW + 1 + WW, WD))
MOT = both(cyly(AX, AZ, 10, 25, 12) + box(AX - 6, AX + 6, 25, 34.5, AZ - 5, AZ + 5))
if __name__ == '__main__':
    b = CH.bounding_box()
    print('size', round(b[3] - b[0], 1), round(b[4] - b[1], 1), round(b[5], 1), 'parts', len(CH.decompose()),
          'wheels^ch', round((WHEELS ^ CH).volume(), 2), 'mot^ch', round((MOT ^ CH).volume(), 2))
    me = CH.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, 'sumo_copy.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '20%', '--fill-pattern', 'gyroid',
                    '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'sumo_copy.stl')], check=True, capture_output=True)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); fig = plt.figure(figsize=(13, 6))
    G = (0.7, 0.72, 0.75)
    for k, (items, view, title) in enumerate((([(CH, G)], (35, -130), 'Chassis (rear view)'),
                                              ([(CH, G), (WHEELS, (0.1, 0.1, 0.1)), (MOT, (0.95, 0.75, 0.2))], (35, -50), 'With N20s + 32 x 12 wheels'))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-45, 95); ax.set_ylim(-70, 70); ax.set_zlim(-55, 85); ax.set_box_aspect((1, 1, 1), zoom=1.4); ax.view_init(*view); ax.axis('off')
        ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
