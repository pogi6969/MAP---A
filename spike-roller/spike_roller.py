#!/usr/bin/env python3
"""Front roller (caster) for the LEGO SPIKE robot. Bracket with a 7 x 5 grid of Technic pin holes (8 mm pitch)
pins to the hub's front holes; a free roller on an M3 screw holds the front up.
Pick the hole row that matches the height of the hub hole you pin into (heights from the floor printed below).
Axes: x forward (away from the robot), y left, z up, floor = 0. mm."""
import os, glob, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
P, T, NY, NZ = 8.0, 7.8, 7, 5            # Technic pitch, beam thickness, holes across / up
RD, RW = 20.0, 29.0                      # roller dia, width
ZB = 16.0                                # plate bottom above the floor
AX, AZ = T + 13.0, ZB - 6.0              # roller axle position


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cylx(y, z, x0, x1, d, d1=None):
    return Manifold.cylinder(x1 - x0, d / 2, (d if d1 is None else d1) / 2).rotate([0, 90, 0]).translate([x0, y, z])


def cyly(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])


W = NY * P
rows = [ZB + P / 2 + i * P for i in range(NZ)]


def bracket():
    m = box(0, T, -W / 2, W / 2, ZB, ZB + NZ * P)                                   # Technic plate
    for z in rows:
        for j in range(NY):
            y = -W / 2 + P / 2 + j * P
            m -= cylx(y, z, -1, T + 1, 4.85)                                         # pin hole
            m -= cylx(y, z, -1, 0.8, 6.2) + cylx(y, z, T - 0.8, T + 1, 6.2)          # counterbores
    ya = RW / 2 + 0.6
    for s in (-1, 1):                                                                # fork arms
        arm = box(0, AX + 6, ya, ya + 4, AZ - 6, ZB + 10) - box(AX + 6.01, AX + 20, ya - 1, ya + 5, ZB - 0.01, ZB + 20)
        arm += cyly(AX, AZ, ya, ya + 4, 12)
        arm -= cyly(AX, AZ, ya - 1, ya + 5, 3.2)                                     # M3 axle hole
        m += arm if s > 0 else arm.mirror([0, 1, 0])
    m += box(0, AX - RD / 2 - 1.5, -ya - 4, ya + 4, ZB - 2, ZB)                      # bridge between the arms
    return m


def roller():
    c = Manifold.cylinder(RW, RD / 2)
    c -= Manifold.cylinder(1.01, RD / 2 + 1, RD / 2 - 1).translate([0, 0, RW - 1]) - Manifold.cylinder(1.01, RD / 2 - 1, RD / 2 - 1).translate([0, 0, RW - 1])
    c -= Manifold.cylinder(1.01, RD / 2 - 1, RD / 2 + 1).translate([0, 0, -0.01]) - Manifold.cylinder(1.01, RD / 2 - 1, RD / 2 - 1).translate([0, 0, -0.01])
    return c - Manifold.cylinder(RW + 2, 1.75).translate([0, 0, -1])                 # free on an M3 screw


B = bracket()
R = roller().rotate([-90, 0, 0]).translate([AX, -RW / 2, AZ])


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(Tr[:, 1] - Tr[:, 0], Tr[:, 2] - Tr[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, Tr
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())


def floor0(m):
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    b = R.bounding_box()
    print('roller bottom z', round(b[2], 2), '| bracket^roller', round((B ^ R).volume(), 3), '| row heights', rows)
    bp = floor0(B.rotate([0, -90, 0]))                                               # plate flat on the bed
    rp = floor0(roller())
    stl(bp + rp.translate([bp.bounding_box()[3] + 6, 0, 0]), 'spike_front_roller.stl')
    for g in glob.glob(os.path.join(HERE, '*.gcode')):
        os.remove(g)
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '30%', '--perimeters', '3',
                    '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'spike_front_roller.stl')], check=True, capture_output=True)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8])
    fig = plt.figure(figsize=(12, 6))
    for k, (el, az) in enumerate(((20, -50), (5, -90))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
        for m, col in ((B, (0.95, 0.8, 0.2)), (R, (0.3, 0.6, 0.9))):
            me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)]
            n = np.cross(Tr[:, 1] - Tr[:, 0], Tr[:, 2] - Tr[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(Tr); CC.append(np.clip(np.outer(0.35 + 0.65 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-15, 45); ax.set_ylim(-30, 30); ax.set_zlim(0, 60); ax.set_box_aspect((1, 1, 1)); ax.view_init(el, az); ax.axis('off')
        ax.plot([-15, 45], [0, 0], [0, 0], 'k-', lw=0.5)
    fig.suptitle('SPIKE front roller — pin the yellow plate to the hub front, roller rides on the floor', fontsize=12)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=100)
