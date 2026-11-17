#!/usr/bin/env python3
"""Wheel hubs + silicone molds (format of the user's tire_mold_and_hub_27x33), revised to be sturdy and easy to print.
Hub: smooth spool, flange each end, 45 deg chamfer under the top flange (no supports), 0.5 mm chamfer on the bottom
edge (no elephant foot), 4 mm deep 2.6 socket under it (sits on the mold pin) and a centre mark on top to drill
the shaft hole after casting (closed top, so no silicone gets into it). 6 notches only on
the 42 mm hubs (high torque). Printed 100% solid so it is strong and does not float in the silicone.
Mold: 2.4 base, 2.0 wall, 1.6 spill rim, 1.5 deg draft, inner lead-in chamfer (no knife edge), strong 2.1 centre pin
with a root fillet and pointed tip. Cavity is only 0.2 mm taller than the hub: fill to the brim = tyre flush with the
hub, the extra spills into the rim. Hubs and molds are separate prints, 1 part per file, each with its own G-code."""
import os, glob, re, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [(27, 33), (34, 27), (34, 12), (32, 12), (32, 8), (42, 20), (42, 30)]     # tyre OD, width = hub height
BASE, TUBE, RIM, DRAFT, HOLE, PIN = 2.4, 2.0, 1.6, np.radians(1.5), 2.6, 2.1


def cyl(z0, z1, d, d1=None): return Manifold.cylinder(z1 - z0, d / 2, (d1 if d1 else d) / 2).translate([0, 0, z0])


def hub(D, W):
    FD = D - 15.0; BD = FD - 2.97; FT = 3.0 if W >= 20 else (2.0 if W >= 12 else 1.5); CH = (FD - BD) / 2
    h = cyl(0, 0.5, FD - 1.0, FD) + cyl(0.5, FT, FD) + cyl(FT - 0.01, W - FT - CH + 0.01, BD) + cyl(W - FT - CH, W - FT + 0.01, BD, FD) + cyl(W - FT, W, FD)
    if D >= 42:                                  # keys kept only where needed: high-torque 25/37 mm gear motors
        n = Manifold.cube([FD / 2, 0.22 * FD, FT + CH + 1]).translate([BD / 2 + 0.1, -0.11 * FD, W - FT - CH])
        for a in range(0, 360, 60): h -= n.rotate([0, 0, a])
    h -= cyl(-1, min(4.0, W - 2.5), HOLE) + cyl(-0.01, 0.4, HOLE + 0.8, HOLE)          # pin socket from the bottom only (silicone can't get in)
    return h - cyl(W - 0.6, W + 0.01, 0.4, 1.6)                                     # drill centre mark on the top face


def mold(D, W):
    top = BASE + W + 0.2; ro = D / 2 + (W + 0.2) * np.tan(DRAFT); bd = D + 2 * TUBE + 2 * RIM + 6
    m = cyl(0, 0.6, bd - 1.2, bd) + cyl(0.6, BASE, bd) + (cyl(BASE - 0.01, BASE + 3, bd) - cyl(BASE - 0.1, BASE + 3.1, bd - 2 * RIM))
    m += cyl(BASE - 0.01, top, 2 * ro + 2 * TUBE)
    m -= cyl(BASE, top + 0.01, D, 2 * ro) + cyl(top - 0.8, top + 0.01, 2 * ro, 2 * ro + 1.6)                   # cavity + lead-in
    return m + cyl(BASE - 0.01, BASE + 0.6, PIN + 1.2, PIN) + cyl(BASE + 0.6, BASE + 2.6, PIN) + cyl(BASE + 2.6, BASE + 3.2, PIN, 1.0)


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


MOLD_ARGS = ['--layer-height', '0.24', '--fill-density', '15%', '--fill-pattern', 'gyroid', '--perimeters', '3', '--bottom-solid-layers', '4', '--top-solid-layers', '4']
HUB_ARGS = ['--layer-height', '0.32', '--fill-density', '100%', '--fill-pattern', 'rectilinear', '--perimeters', '3']
if __name__ == '__main__':
    for g in glob.glob(os.path.join(HERE, '*', '*.gcode')): os.remove(g)
    os.makedirs(os.path.join(HERE, 'hubs'), exist_ok=True); os.makedirs(os.path.join(HERE, 'molds'), exist_ok=True)
    for D, W in SIZES:
        tag = f'{D}x{W}'; H, M = hub(D, W), mold(D, W)
        print(tag, 'hub^mold', round((H.translate([0, 0, BASE]) ^ M).volume(), 2), 'parts', len(H.decompose()), len(M.decompose()),
              'flush', round(BASE + W + 0.2 - (BASE + W), 2), 'pin clearance', (HOLE - PIN) / 2)
        stl(H, f'hubs/hub_{tag}.stl'); stl(M, f'molds/mold_{tag}.stl')           # hub file = hub only, mold file = mold only
        for nm, ex in ((f'hubs/hub_{tag}', HUB_ARGS), (f'molds/mold_{tag}', MOLD_ARGS)):
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                            '--output', os.path.dirname(os.path.join(HERE, nm)), os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    for g in sorted(glob.glob(os.path.join(HERE, '*', '*.gcode'))):
        print(os.path.basename(g), re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-400000:]).group(1), 'g')
