#!/usr/bin/env python3
"""Copy of the black printed spool hub (4 photos) for an N20 motor + its silicone mold.
Hub: 27 tall, 28 flanges (2 thick) both ends, 24.6 body; face A: 3 mm D bore (2.5 flat) 10 deep with entry cone;
face B: 2.2 through hole; radial M3 set-screw hole (2.6 pilot, 4.8 counterbore) 8 mm below face A.
Mold: one-piece open cup, 34 tyre, 1.5 deg draft, centre pin in face B hole, 3 push-out holes under the flange,
2 pry notches, side pin (printed with it) keeps the set-screw hole open: pull it out before demolding."""
import os, glob, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
HH, FD, FT, BD = 27.0, 28.0, 2.0, 24.6            # hub height, flange dia / thick, body dia
TD, FLOOR, WALL, DRAFT = 34.0, 3.0, 3.0, np.radians(1.5)
ZS = HH - 8.0                                      # set-screw hole height (from face B)


def cyl(z0, z1, d, d1=None): return Manifold.cylinder(z1 - z0, d / 2, (d1 if d1 else d) / 2).translate([0, 0, z0])
def radial(z, r0, r1, d): return Manifold.cylinder(r1 - r0, d / 2).rotate([0, 90, 0]).translate([r0, 0, z])


def hub():
    h = cyl(0, FT, FD) + cyl(FT - 0.01, HH - FT + 0.01, BD) + cyl(HH - FT, HH, FD)
    d = cyl(HH - 10, HH + 1, 3.05) ^ Manifold.cube([3.05, 2.55, 12], center=True).translate([0, 0, HH - 4])   # N20 D bore
    h -= d + cyl(HH - 1.5, HH + 0.01, 3.05, 6.5) + cyl(-1, HH, 2.2)                                         # entry cone, through hole
    h -= radial(ZS, 0, BD / 2 + 1, 2.6) + radial(ZS, BD / 2 - 2.5, BD / 2 + 1, 4.8)                           # set screw M3
    return h


def mold():
    ro = TD / 2 + (HH + 0.5) * np.tan(DRAFT)
    m = cyl(0, FLOOR + HH + 0.5, 2 * (ro + WALL)) - cyl(FLOOR, FLOOR + HH + 0.51, TD, 2 * ro)
    m += cyl(FLOOR - 0.01, FLOOR + 4, 2.0)                                                                  # centre pin
    for a in (0, 120, 240): m -= Manifold.cylinder(FLOOR + 2, 2).translate([11 * np.cos(np.radians(a + 60)), 11 * np.sin(np.radians(a + 60)), -1])  # push-out
    for a in (90, 270): m -= Manifold.cube([8, 4 * WALL, 4], center=True).rotate([0, 0, a]).translate([0, 0, FLOOR + HH + 0.5]).translate(
        [ (ro + WALL / 2) * np.cos(np.radians(a)), (ro + WALL / 2) * np.sin(np.radians(a)), 0])                # pry notches
    m -= radial(FLOOR + ZS, TD / 2 - 2, ro + WALL + 1, 4.9)                                                 # side pin hole
    return m


def pin():                                         # lies flat: head disc + shaft along x
    L = (TD / 2 + (FLOOR + ZS) * np.tan(DRAFT) + WALL + 1) - (BD / 2 - 2.4)
    return (Manifold.cylinder(L, 2.3).rotate([0, 90, 0]) + Manifold.cylinder(2, 4).rotate([0, 90, 0]).translate([L, 0, 0])) ^ Manifold.cube([L + 4, 9, 4.2], center=True).translate([L / 2 + 1, 0, 0])


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m): b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    H, M = hub(), mold()
    P = floor0(pin()); Mf = floor0(M)
    print('hub^mold', round((H.translate([0, 0, FLOOR]) ^ M).volume(), 2), 'pin fits', round((pin().translate([BD / 2 - 2.4, 0, FLOOR + ZS]) ^ (M + H.translate([0, 0, FLOOR]))).volume(), 2))
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    stl(H, 'hub_N20_copy_28x27.stl'); stl(Mf + P.translate([Mf.bounding_box()[3] + 6, 0, 0]), 'mold_N20_copy_34x27.stl')
    for nm, ex in (('hub_N20_copy_28x27', ['--fill-density', '30%', '--perimeters', '4']), ('mold_N20_copy_34x27', ['--fill-density', '15%', '--perimeters', '2'])):
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                        '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    print(sorted(os.path.basename(g) for g in glob.glob(os.path.join(HERE, '*.gcode'))))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82]); fig = plt.figure(figsize=(15, 5))
    tyre = (cyl(0, HH, TD) - cyl(-1, HH + 1, BD)) - (cyl(-1, FT, FD) + cyl(HH - FT, HH + 1, FD) - cyl(FT, HH - FT, FD))
    cut = Manifold.cube([60, 60, 60]).translate([0, -60, -10])
    for k, (items, title) in enumerate((([(H, (0.25, 0.25, 0.27))], 'Hub (copy)'), ([(H - cut, (0.25, 0.25, 0.27)), (tyre - cut, (0.85, 0.3, 0.2))], 'Hub + silicone tyre 34 (cut)'),
                                        ([(M - cut, (0.75, 0.77, 0.8)), (H.translate([0, 0, FLOOR]) - cut, (0.25, 0.25, 0.27)), (pin().translate([BD / 2 - 2.4, 0, FLOOR + ZS]), (0.2, 0.5, 0.9))], 'Mold + hub + pin (cut)'))):
        ax = fig.add_subplot(1, 3, k + 1, projection='3d'); TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-25, 25); ax.set_ylim(-25, 25); ax.set_zlim(-10, 40); ax.set_box_aspect((1, 1, 1), zoom=1.2); ax.view_init(25, -60); ax.axis('off'); ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
