#!/usr/bin/env python3
"""Sensor cover revised to the LED strip plan: 150 x 18 x 5 mm, 2 rows x 16 LEDs (5 mm T-1 3/4),
7.5 mm pitch both ways (2.5 mm edge-to-edge, 15 gaps), Ø3.0 screw hole at each end, 6.25 mm from the end
(fits the trapdoor chassis sensor slots, 137.5 mm apart). Prints flat, no supports."""
import os
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
L, W, T = 150.0, 18.0, 5.0
PITCH, ROW, N, LED_D = 7.5, 7.5, 16, 5.0
END, SCREW_D, CH = 6.25, 3.0, 0.5            # screw hole centre from end, Ø, bottom chamfer

def hole(x, y, d):                           # through hole, 45 deg chamfer at the bed side
    return (Manifold.cylinder(T + 2, d / 2).translate([x, y, -1])
            + Manifold.cylinder(CH + 0.01, d / 2 + CH, d / 2).translate([x, y, -0.01]))

m = Manifold.cube([L, W, T]).translate([-L / 2, -W / 2, 0])
for i in range(N):
    for y in (-ROW / 2, ROW / 2):
        m -= hole((i - (N - 1) / 2) * PITCH, y, LED_D)
for x in (-L / 2 + END, L / 2 - END):
    m -= hole(x, 0, SCREW_D)

me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
n = np.cross(Tr[:, 1] - Tr[:, 0], Tr[:, 2] - Tr[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
rec = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'], rec['v'] = n, Tr
open(os.path.join(HERE, 'sensor_cover.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + rec.tobytes())
print('vol', round(m.volume(), 1), 'genus', m.genus(), 'end LED edge to end', L / 2 - ((N - 1) / 2 * PITCH + LED_D / 2),
      'screw edge to LED edge', (L / 2 - END - SCREW_D / 2) - ((N - 1) / 2 * PITCH + LED_D / 2))
