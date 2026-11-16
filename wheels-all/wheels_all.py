#!/usr/bin/env python3
"""Plain wheel hubs + silicone molds (spool format, no holes, no screws), 1 part per file with G-code.
Hub: body with a flange at each end; silicone tyre covers the whole hub (3 mm over the flanges).
Mold: low-cost thin cup (1.6 wall / floor, 1.5 deg draft), 0.6 mm centring recess for the bottom flange, 2 pry notches.
Sizes: 34x27 / 34x12 / 32x12 / 32x8 (N20), 42x20 (JGA25-370, TT yellow), 42x30 (JGB37-520)."""
import os, glob, re, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [(34, 27), (34, 12), (32, 12), (32, 8), (42, 20), (42, 30)]     # tyre OD, width = hub height
WALL, FLOOR, DRAFT, SIL = 1.6, 1.6, np.radians(1.5), 3.0


def cyl(z0, z1, d, d1=None): return Manifold.cylinder(z1 - z0, d / 2, (d1 if d1 else d) / 2).translate([0, 0, z0])
def geo(D, W): FD = D - 2 * SIL; return FD, FD - 3.4, (1.5 if W < 10 else 2.0)


def hub(D, W):
    FD, BD, FT = geo(D, W)
    return cyl(0, FT, FD) + cyl(FT - 0.01, W - FT + 0.01, BD) + cyl(W - FT, W, FD)


def mold(D, W):
    FD, BD, FT = geo(D, W); ro = D / 2 + (W + 0.5) * np.tan(DRAFT)
    m = cyl(0, FLOOR + W + 0.5, 2 * (ro + WALL)) - cyl(FLOOR, FLOOR + W + 0.51, D, 2 * ro) - cyl(FLOOR - 0.6, FLOOR + 0.01, FD + 0.3)
    for a in (0, 180): m -= Manifold.cube([8, 4 * WALL + 2, 6], center=True).translate([0, ro + WALL / 2, FLOOR + W + 0.5]).rotate([0, 0, a])
    return m


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


if __name__ == '__main__':
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    for D, W in SIZES:
        tag = f'{D}x{W}'; H, M = hub(D, W), mold(D, W)
        print(tag, 'hub^mold', round((H.translate([0, 0, FLOOR - 0.6]) ^ M).volume(), 2))
        stl(H, f'hub_{tag}.stl'); stl(M, f'mold_{tag}.stl')
        for nm, ex in ((f'hub_{tag}', ['--fill-density', '30%', '--perimeters', '4']),
                       (f'mold_{tag}', ['--fill-density', '10%', '--fill-pattern', 'lightning', '--perimeters', '2', '--bottom-solid-layers', '5', '--top-solid-layers', '3'])):
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                            '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    for g in sorted(glob.glob(os.path.join(HERE, '*.gcode'))):
        print(os.path.basename(g), re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-400000:]).group(1), 'g')
