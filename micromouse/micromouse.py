#!/usr/bin/env python3
"""Micromouse like the Banary Source one: round-front printed chassis, 2 x Pololu N20 with encoder,
4 IR emitter + photodiode pairs (940 nm, 5 mm) in black blocks, wheels at the back, skids front/back.
One print = chassis with motor holders and sensor blocks + 2 push-in skids.
Axes: x forward, y left, z up, floor = 0, axle at x = 0. mm."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
R = 45.0                                  # front circle radius (width 90)
XC = 12.0                                 # circle centre (front tip at XC + R)
XB = -22.0                                # flat back
ZP, PT = 5.0, 2.5                         # plate underside, thickness
WD, WW = 32.0, 8.0                        # wheel
AZ = WD / 2
MW, MH, ML = 12.0, 10.0, 33.0             # N20 + encoder (Pololu extended shaft): body length
MY0 = 2.0                                 # motor rear (encoder) end |y|
MY1 = MY0 + ML + 0.5                      # gearbox face |y|
OW = 2.5
SENS = [(XC + R - 6, 13.0, 0.0), (XC + R - 6, -13.0, 0.0),               # front pair, looking forward
        (XC + 22, 34.0, 60.0), (XC + 22, -34.0, -60.0)]                   # diagonal pair, looking out 60 deg


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cyly(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])


def both(m):
    return m + m.mirror([0, 1, 0])


def sensor_block():                       # local: looks along +x, sits on the plate (z = 0)
    b = box(-11, 0, -7.5, 7.5, 0, 13)
    for y in (-3.6, 3.6):                 # emitter + photodiode, 5 mm
        b -= Manifold.cylinder(13, 2.6).rotate([0, 90, 0]).translate([-12, y, 7.5])
    return b - box(-11.5, -7.5, -6.5, 6.5, -1, 14)          # rear pocket for the leads (divider stays in front)


def chassis():
    outline = CrossSection.circle(R).translate([XC, 0]) + CrossSection.square([XC - XB, 2 * R]).translate([XB, -R])
    outline -= both_cs(CrossSection.square([WD + 3, WW + 3]).translate([-(WD + 3) / 2, MY1 + OW + 0.5]))
    m = Manifold.extrude(outline, PT).translate([0, 0, ZP])
    h = box(-MW / 2 - 2.5, MW / 2 + 2.5, MY0 + 6, MY1 + OW, ZP, AZ + MH / 2 + 2.5)       # N20 holder (encoder end open)
    h -= box(-MW / 2 - 0.2, MW / 2 + 0.2, MY0 - 1, MY1, AZ - MH / 2 - 0.2, AZ + MH / 2 + 0.2)
    h -= box(-MW / 2 - 3, MW / 2 + 3, MY0 + 9, MY0 + 21, AZ + MH / 2 - 0.5, AZ + MH / 2 + 3)  # zip-tie / clamp window
    h -= cyly(0, AZ, MY1 - 1, MY1 + OW + 1, 4.4)
    for dx in (-4.5, 4.5):
        h -= cyly(dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)
    m += both(h)
    for x, y, a in SENS:
        m += sensor_block().rotate([0, 0, a]).translate([x, y, ZP + PT - 0.01])
    for x, y in ((24, 20), (24, -20), (-14, 20), (-14, -20)):          # M3 standoffs for the PCB (38 x 40)
        m -= cyl(x, y, ZP - 1, ZP + PT + 1, 3.2)
    for x in (8.0, -6.0):                                              # battery strap slots
        m -= both(box(x - 1.5, x + 1.5, 16, 20, ZP - 1, ZP + PT + 1))
    m -= box(-4, 4, -6, 6, ZP - 1, ZP + PT + 1)                        # wire pass-through
    for x in (XC + R - 9, XB + 5):
        m -= cyl(x, 0, ZP - 1, ZP + PT + 1, 4.2)                       # skid holes
    return m


def both_cs(c):
    return c + c.mirror([0, 1])


def skid():                               # push-in skid: dome touches 0.4 mm above the floor
    h = ZP - 0.4
    s = Manifold.sphere(4.0, 32).translate([0, 0, 4.0]) ^ box(-5, 5, -5, 5, 0, h)
    s += cyl(0, 0, 3.9, h, 8.0) + cyl(0, 0, h - 0.01, h + PT, 4.0)
    return s.translate([0, 0, 0.4])


CH, SK = chassis(), skid()
WHEELS = both(cyly(0, AZ, MY1 + OW + 1.0, MY1 + OW + 1.0 + WW, WD))
MOTORS = both(box(-MW / 2, MW / 2, MY0, MY1, AZ - MH / 2, AZ + MH / 2))


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m):
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    asm = CH + WHEELS
    b = asm.bounding_box()
    print('size', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'x', round(b[5], 1), '| wheels^ch', round((WHEELS ^ CH).volume(), 2),
          'motors^ch', round((MOTORS ^ CH).volume(), 2), 'parts', len(CH.decompose()))
    c0 = floor0(CH)
    sk = floor0(SK.rotate([180, 0, 0]))
    plate = c0 + sk.translate([c0.bounding_box()[3] + 5, 0, 0]) + sk.translate([c0.bounding_box()[3] + 5, 12, 0])
    stl(plate, 'micromouse_chassis.stl')
    for g in glob.glob(os.path.join(HERE, '*.gcode')):
        os.remove(g)
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '25%', '--perimeters', '3',
                    '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'micromouse_chassis.stl')], check=True, capture_output=True)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8])
    fig = plt.figure(figsize=(13, 6))
    for k, (el, az) in enumerate(((35, -130), (60, -60))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
        items = [(CH, (0.15, 0.35, 0.85)), (WHEELS, (0.85, 0.15, 0.2)), (MOTORS, (0.75, 0.75, 0.75)),
                 (SK.translate([XC + R - 9, 0, 0]) + SK.translate([XB + 5, 0, 0]), (0.2, 0.2, 0.2))]
        for m, col in items:
            me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.35 + 0.65 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-45, 65); ax.set_ylim(-55, 55); ax.set_zlim(-20, 50); ax.set_box_aspect((110, 110, 70)); ax.view_init(el, az); ax.axis('off')
    fig.suptitle(f'Micromouse — {b[3] - b[0]:.0f} × {b[4] - b[1]:.0f} mm, 2 × N20 + encoder, 4 IR pairs (940 nm)', fontsize=13)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
