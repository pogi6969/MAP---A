#!/usr/bin/env python3
"""Wheel hubs + silicone molds in the format of tire_mold_and_hub_27x33 (user file), made simpler / faster.
Hub: spool with a flange at each end, top flange with 45 deg chamfer underneath and 6 notches (silicone flows under it
and locks), 2.4 centre hole that sits on the mold pin. Silicone covers the whole hub.
Mold: thin base + low spill-tray rim + plain tube (cavity = tyre OD, 1 deg draft, chamfered top) + centre pin.
Pull the hub and the tyre straight up out of the tube. 1 part per file with G-code."""
import os, glob, re, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [(27, 33), (34, 27), (34, 12), (32, 12), (32, 8), (42, 20), (42, 30)]     # tyre OD, width = hub height
BASE, TUBE, RIM, DRAFT = 1.6, 1.2, 1.2, np.radians(1.0)


def cyl(z0, z1, d, d1=None): return Manifold.cylinder(z1 - z0, d / 2, (d1 if d1 else d) / 2).translate([0, 0, z0])


def hub(D, W):
    FD = D - 15.0; BD = FD - 2.97; FT = 3.0 if W >= 20 else (2.0 if W >= 12 else 1.5); CH = (FD - BD) / 2
    h = cyl(0, FT, FD) + cyl(FT - 0.01, W - FT - CH + 0.01, BD) + cyl(W - FT - CH, W - FT + 0.01, BD, FD) + cyl(W - FT, W, FD)
    n = Manifold.cube([FD / 2, 0.22 * FD, FT + CH + 1]).translate([BD / 2 + 0.1, -0.11 * FD, W - FT - CH])
    for a in range(0, 360, 60): h -= n.rotate([0, 0, a])
    return h - cyl(-1, W + 1, 2.4)


def mold(D, W):
    top = BASE + W + 1; ro = D / 2 + (W + 1) * np.tan(DRAFT)
    m = cyl(0, BASE, D + 9) + (cyl(BASE - 0.01, BASE + 2.5, D + 9) - cyl(BASE - 0.1, BASE + 2.6, D + 9 - 2 * RIM))
    m += cyl(BASE - 0.01, top - 1.5, 2 * ro + 2 * TUBE) + cyl(top - 1.5, top, 2 * ro + 2 * TUBE, 2 * ro + 0.6)
    m -= cyl(BASE, top + 0.01, D, 2 * ro)
    return m + cyl(BASE - 0.01, BASE + 3.6, 1.9) + cyl(BASE + 3.6, BASE + 4.0, 1.9, 1.4)


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


MOLD_ARGS = ['--fill-density', '10%', '--fill-pattern', 'lightning', '--perimeters', '2', '--bottom-solid-layers', '4', '--top-solid-layers', '3']
if __name__ == '__main__':
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    for D, W in SIZES:
        tag = f'{D}x{W}'; H, M = hub(D, W), mold(D, W)
        print(tag, 'hub^mold', round((H.translate([0, 0, BASE]) ^ M).volume(), 2), 'parts', len(H.decompose()), len(M.decompose()))
        stl(H, f'hub_{tag}.stl'); stl(M, f'mold_{tag}.stl')
        for nm, ex in ((f'hub_{tag}', ['--fill-density', '30%', '--perimeters', '4']), (f'mold_{tag}', MOLD_ARGS)):
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                            '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    for g in sorted(glob.glob(os.path.join(HERE, '*.gcode'))):
        print(os.path.basename(g), re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-400000:]).group(1), 'g')
