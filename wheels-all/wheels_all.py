#!/usr/bin/env python3
"""All wheel hubs + silicone molds in the spool format (wheel-copy-n20): hub = body with a flange at each end, D bore
with entry cone on face A, 2.2 through hole, radial M3 set-screw hole (2.6 pilot + 4.8 counterbore). Silicone tyre
covers the whole hub (3 mm over the flanges). Mold = low-cost thin cup (1.6 wall / floor, 1.5 deg draft) with centre
pin, 3 push-out holes under the flange, 2 pry notches and a side pin (printed with it) that keeps the screw hole open.
1 part per file, each with its own CR-6 SE PETG G-code."""
import os, glob, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
# tag: (tyre OD, width = hub height, shaft d, flat across, double-D, bore depth)
SETS = {'N20_34x27': (34, 27, 3.0, 2.5, False, 10), 'N20_34x12': (34, 12, 3.0, 2.5, False, 10), 'N20_32x12': (32, 12, 3.0, 2.5, False, 10),
        'N20_32x8': (32, 8, 3.0, 2.5, False, 10), 'JGA25-370_42x20': (42, 20, 4.0, 3.5, False, 12), 'JGB37-520_42x30': (42, 30, 6.0, 5.5, False, 15),
        'TT-yellow_42x20': (42, 20, 5.4, 3.7, True, 9)}
WALL, FLOOR, DRAFT, SIL = 1.6, 1.6, np.radians(1.5), 3.0


def cyl(z0, z1, d, d1=None): return Manifold.cylinder(z1 - z0, d / 2, (d1 if d1 else d) / 2).translate([0, 0, z0])
def radial(z, r0, r1, d): return Manifold.cylinder(r1 - r0, d / 2).rotate([0, 90, 0]).translate([r0, 0, z])


def geo(D, W, bd):
    FD = D - 2 * SIL; BD = FD - 3.4; FT = 1.5 if W < 10 else 2.0
    da = min(8.0, W / 2); bd = min(bd, W - 2); return FD, BD, FT, W - da, bd


def hub(D, W, sd, flat, dd, bd):
    FD, BD, FT, ZS, bd = geo(D, W, bd)
    h = cyl(0, FT, FD) + cyl(FT - 0.01, W - FT + 0.01, BD) + cyl(W - FT, W, FD)
    b = cyl(W - bd, W + 1, sd + 0.05)
    if dd: b = b ^ Manifold.cube([sd + 1, flat + 0.05, 2 * W], center=True)                                      # double D
    else: b = b ^ Manifold.cube([sd + 1, sd + 1, 2 * W], center=True).translate([0, flat + 0.05 - (sd + 0.05) / 2 - (sd + 1) / 2, 0])  # D flat
    h -= b + cyl(W - 1.5, W + 0.01, sd + 0.05, sd + 3.5) + cyl(-1, W, 2.2)
    h -= radial(ZS, 0, BD / 2 + 1, 2.6) + radial(ZS, BD / 2 - 2.5, BD / 2 + 1, 4.8)
    return h


def mold(D, W, sd, flat, dd, bd):
    FD, BD, FT, ZS, bd = geo(D, W, bd)
    ro = D / 2 + (W + 0.5) * np.tan(DRAFT); zp = FLOOR + ZS
    m = cyl(0, FLOOR + W + 0.5, 2 * (ro + WALL)) - cyl(FLOOR, FLOOR + W + 0.51, D, 2 * ro)
    m += radial(zp, ro, ro + WALL + 2, 9.0) + cyl(FLOOR - 0.01, FLOOR + min(4, W / 3), 2.0)                     # pin boss, centre pin
    for a in (60, 180, 300): m -= Manifold.cylinder(FLOOR + 2, 2).translate([(FD / 2 - 3) * np.cos(np.radians(a)), (FD / 2 - 3) * np.sin(np.radians(a)), -1])
    for a in (90, 270): m -= Manifold.cube([8, 4 * WALL + 2, 6], center=True).translate([0, 0, FLOOR + W + 0.5]).translate([0, ro + WALL / 2, 0]).rotate([0, 0, a - 90])
    m -= radial(zp, D / 2 - 2, ro + WALL + 3, 4.9)
    return m, zp, ro


def pin(D, W, sd, flat, dd, bd):
    FD, BD, FT, ZS, bd = geo(D, W, bd); _, zp, ro = mold(D, W, sd, flat, dd, bd)
    r0 = BD / 2 - 2.4; L = ro + WALL + 2 - r0
    return (Manifold.cylinder(L, 2.3).rotate([0, 90, 0]) + Manifold.cylinder(2, 4).rotate([0, 90, 0]).translate([L, 0, 0])) ^ \
        Manifold.cube([L + 4, 9, 4.2], center=True).translate([L / 2 + 1, 0, 0]), r0, zp


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m): b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    for tag, p in SETS.items():
        H = hub(*p); M, zp, ro = mold(*p); P, r0, _ = pin(*p)
        sd, flat = p[2], p[3]; Ht = H.translate([0, 0, FLOOR])
        shaft = cyl(p[1] - geo(p[0], p[1], p[5])[4] + FLOOR, p[1] + FLOOR + 5, sd) ^ (Manifold.cube([sd, flat, 99], center=True) if p[4] else
                                                                                        Manifold.cube([sd, sd, 99], center=True).translate([0, flat - sd, 0]))
        print(tag, 'hub^mold', round((Ht ^ M).volume(), 2), 'pin^mold+hub', round((P.translate([r0, 0, zp]) ^ (M + Ht)).volume(), 2),
              'shaft^hub', round((shaft ^ Ht).volume(), 2), 'parts', len(H.decompose()), len(M.decompose()))
        stl(floor0(H), f'hub_{tag}.stl'); Mf = floor0(M); stl(Mf + floor0(P).translate([Mf.bounding_box()[3] + 5, 0, 0]), f'mold_{tag}.stl')
        for nm, ex in ((f'hub_{tag}', ['--fill-density', '30%', '--perimeters', '4']),
                       (f'mold_{tag}', ['--fill-density', '10%', '--fill-pattern', 'lightning', '--perimeters', '2', '--bottom-solid-layers', '5', '--top-solid-layers', '3'])):
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                            '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    for g in sorted(glob.glob(os.path.join(HERE, '*.gcode'))):
        t = open(g).read()[-400000:]; import re
        print(os.path.basename(g), re.search(r'filament used \[g\] = ([\d.]+)', t).group(1), 'g')
