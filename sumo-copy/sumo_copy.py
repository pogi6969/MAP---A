#!/usr/bin/env python3
"""Exact copy of the reference grey sumo chassis (5 photos), measured off the photos: main box 51 long with 6.5 mm front
wall + 45 deg blade tapering to 77 wide, 2 screw holes on the front top, 2 angled tabs inside, rear wall stubs with a
48 wide opening to the tail; tail 61 wide = floor with a wire slot + 2 slit-ring N20 clamps sitting on the floor
(OD 18.5, bore 12.3 = motor hole, 2 ears, 2 x M2 pinch screws) + rear bar with 2 screw holes; side walls end in wheel
arcs. No sensor windows. Wheels up to 32 x 12 in the rear notches. x forward, y left, z up."""
import os, glob, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
S, H, ZF0, ZF1 = 50.0, 23.0, 0.0, 2.2              # half width, wall top, floor bottom / top
XB, XF, BT = 0.0, 51.0, 38.5                       # side wall rear end, front wall front, blade tip half width
TIP = XF + 22.0
RO, RI, RY0, RY1 = 18.5, 12.3, 10.5, 28.0          # clamp ring OD / ID (N20 can), ring y range
AX, AZ = XB - 2.4 - RO / 2, ZF1 + RO / 2 - 0.3     # motor / wheel axis
WD, WW, RA = 32.0, 12.0, 17.5                      # wheel dia, width, wheel arc radius
TW, GW = 30.5, 24.0                                # tail half width, rear opening half width
XBAR = AX - 13.5                                   # rear bar back face


def box(x0, x1, y0, y1, z0, z1): return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])
def cyl(x, y, z0, z1, d): return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])
def cyly(x, z, y0, y1, d): return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])
def cylx(x0, x1, y, z, d): return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])
def both(m): return m + m.mirror([0, 1, 0])


def chassis():
    m = box(XB + 2, XF, -S, S, ZF0, ZF1) + both(box(XB, XF, S - 2, S, ZF0, H)) + box(XF - 6.5, XF, -S, S, ZF0, H)
    m += both(box(XB + 2, XB + 7.5, GW, S - 1, ZF0, H))                                               # rear wall stubs
    m += Manifold.hull(Manifold.compose([box(XF - 0.01, XF, -S, S, ZF0, H), box(TIP - 0.01, TIP, -BT, BT, ZF0, ZF0 + 0.8)]))  # blade
    m += both(box(0, 9, -1, 1, ZF0, ZF1 + 10).rotate([0, 0, -45]).translate([XF - 22, S - 2.5, 0]))   # angled tabs
    m += box(XBAR, XB + 3, -TW, TW, ZF0, ZF1) + box(XBAR, AX - 7, -TW, TW, ZF0, H)                    # tail floor + rear bar
    c = cyly(AX, AZ, RY0, RY1, RO)                                                                    # clamp ring on the floor
    c += box(AX - 1.8, AX + 2, RY0, RY1, AZ + 3, H) + box(AX - 6.5, AX - 3.2, RY0, RY1, AZ + 3, H)     # ears
    m += both(c)
    m -= both(cyly(AX, AZ, TW + 0.5, S + 1, 2 * RA))                                                  # wheel arcs
    k = cyly(AX, AZ, RY0 - 2, RY1 + 2, RI) + box(AX - 3.2, AX - 1.8, RY0 - 2, RY1 + 2, AZ + 3, H + 1)  # motor hole + slit
    for y in (RY0 + 3, RY1 - 3): k += cylx(AX - 8, AX + 4, y, (AZ + RO / 2 + H) / 2 + 0.2, 2.2)       # M2 pinch screws
    m -= both(k + cyl(AX - 10.2, TW - 4, H - 10, H + 1, 2.6) + cyl(XF - 3.25, S - 6, H - 10, H + 1, 2.6))  # top holes
    m -= box(AX - 6.5, AX + 2, -7, 7, -1, ZF1 + 1)                                                    # wire slot
    return m


CH = chassis()
WHEELS = both(cyly(AX, AZ, 38, 38 + WW, WD))
MOT = both(cyly(AX, AZ, 13, 28, 12) + box(AX - 6, AX + 6, 28, 37.5, AZ - 5, AZ + 5))
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
