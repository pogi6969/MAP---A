#!/usr/bin/env python3
"""Sensor cover, hollow version: 150 x 18 x 5 mm frame with one open window over the LED area (no separators
between LEDs). Window = the 2 x 16 LED field of the plan (117.5 x 12.5 mm, R2.5 corners), Ø3.0 screw hole at
each end 6.25 mm from the end. Prints flat, no supports."""
import os
import numpy as np
from manifold3d import CrossSection, JoinType, Manifold, set_circular_segments
set_circular_segments(64)
HERE = os.path.dirname(os.path.abspath(__file__))
L, W, T = 150.0, 18.0, 5.0
WIN_L, WIN_W, R = 15 * 7.5 + 5.0, 7.5 + 5.0, 2.5   # LED field: 16 x 2 LEDs, 7.5 pitch, Ø5
END, SCREW_D, CH = 6.25, 3.0, 0.5

def win(l, w, r, h, z):                    # rounded rectangle prism
    return Manifold.extrude(CrossSection.square([l - 2 * r, w - 2 * r], center=True).offset(r, JoinType.Round), h).translate([0, 0, z])


m = Manifold.cube([L, W, T]).translate([-L / 2, -W / 2, 0])
m -= win(WIN_L, WIN_W, R, T + 2, -1)
m -= Manifold.hull(win(WIN_L + 2 * CH, WIN_W + 2 * CH, R + CH, 0.01, -0.01) + win(WIN_L, WIN_W, R, 0.01, CH))  # bed-side chamfer
for x in (-L / 2 + END, L / 2 - END):
    m -= Manifold.cylinder(T + 2, SCREW_D / 2).translate([x, 0, -1])
    m -= Manifold.cylinder(CH + 0.01, SCREW_D / 2 + CH, SCREW_D / 2).translate([x, 0, -0.01])

me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
n = np.cross(Tr[:, 1] - Tr[:, 0], Tr[:, 2] - Tr[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
rec = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['n'], rec['v'] = n, Tr
open(os.path.join(HERE, 'sensor_cover_hollow.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + rec.tobytes())
print('vol', round(m.volume(), 1), 'genus', m.genus(), 'side wall', (W - WIN_W) / 2, 'end wall to screw', L / 2 - END - SCREW_D / 2 - WIN_L / 2)
