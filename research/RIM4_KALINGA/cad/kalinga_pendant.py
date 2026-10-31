"""KALINGA pendant shell: makes front_shell.stl, back_shell.stl, and pill_carousel.stl (sizes in mm).

Run:  pip install manifold3d trimesh   then   python kalinga_pendant.py
Axes: x = width, y = height (top is +y), z = depth (the face is +z). Change the numbers below to adjust the fit.
"""
import math, os
import numpy as np
import trimesh
from manifold3d import Manifold

OUT = os.path.dirname(os.path.abspath(__file__))
SEG = 96
WALL = 2.0
DEPTH = 0.65          # outer depth scale: 60 mm wide egg -> 39 mm deep
SPLIT_Z = -2.0        # front and back shells meet here
CAROUSEL = (0.0, -18.0)  # servo shaft position (x, y)
SLOT_R, POCKET_R = 11.0, 4.8


def egg(r_top, r_bot, zscale):
    top = Manifold.sphere(r_top, SEG).translate((0, 18, 0))
    bot = Manifold.sphere(r_bot, SEG).translate((0, -8, 0))
    return (top + bot).hull().scale((1, 1, zscale))


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def cyl_z(x, y, r, z0, z1):
    return Manifold.cylinder(z1 - z0, r, r, SEG).translate((x, y, z0))


def cyl_x(y, z, r, x0, x1):
    return Manifold.cylinder(x1 - x0, r, r, SEG).rotate((0, 90, 0)).translate((x0, y, z))


def cyl_y(x, z, r, y0, y1):
    return Manifold.cylinder(y1 - y0, r, r, SEG).rotate((-90, 0, 0)).translate((x, y0, z))


outer = egg(24, 30, DEPTH)
inner_scale = (30 * DEPTH - WALL) / (30 - WALL)
inner = egg(24 - WALL, 30 - WALL, inner_scale)
shell = outer - inner

# Openings in the face and sides
cx, cy = CAROUSEL
cuts = [
    box(-12, 12, -2, 6, 0, 40),                    # 0.91-in OLED window (24 x 8)
    box(-6.5, 6.5, 10, 23, 0, 40),                 # MAX30102 finger pad window (13 x 13)
    cyl_z(cx + SLOT_R, cy, 5.5, 0, 40),            # pill window over slot position 0
    cyl_y(0, 3, 4.9, 30, 50),                      # MLX90614 window at the top, pointing up
    cyl_x(8, 3, 3.3, -40, 40),                     # OK (left) and SOS (right) button holes
    box(-16, -6, -50, -30, SPLIT_Z - 4.2, SPLIT_Z - 0.2),  # USB-C charging port (bottom, back shell)
    box(4, 13, -50, -30, SPLIT_Z - 4.2, SPLIT_Z - 0.2),    # slide switch (bottom, back shell)
]
for x in (-9, 9):                                  # shallow eye recesses for black paint
    z_face = DEPTH * math.sqrt(24**2 - x**2 - (30 - 18)**2)
    cuts.append(cyl_z(x, 30, 3.2, z_face - 0.8, 40))
for c in cuts:
    shell = shell - c

# Lanyard loop on top, toward the back
loop = cyl_x(43, -6, 4.5, -5, 5) - cyl_x(43, -6, 2.0, -6, 6)
shell = shell + loop

front = shell ^ box(-40, 40, -50, 60, SPLIT_Z, 40)
back = shell ^ box(-40, 40, -50, 60, -40, SPLIT_Z)

# Locating lip on the back shell (slides 3 mm into the front shell)
lip_outer = egg(24 - WALL - 0.2, 30 - WALL - 0.2, inner_scale)
lip_inner = egg(24 - WALL - 1.4, 30 - WALL - 1.4, inner_scale)
lip = (lip_outer - lip_inner) ^ box(-40, 40, -50, 60, SPLIT_Z, SPLIT_Z + 3)
lip = lip - box(-16, -6, -50, -30, -10, 10) - box(4, 13, -50, -30, -10, 10)
back = back + lip

# SG90 servo cradle in the back shell: shaft at CAROUSEL, body runs toward +x
sx0, sx1, sy0, sy1 = cx - 5.9, cx + 16.9, cy - 6.1, cy + 6.1
back_inner_z = -(30 * DEPTH - WALL)
cradle = box(sx0 - 1.6, sx1 + 1.6, sy0 - 1.6, sy1 + 1.6, back_inner_z - 1, back_inner_z + 7) - \
    box(sx0, sx1, sy0, sy1, back_inner_z - 2, back_inner_z + 8)
back = back + (cradle ^ outer)

# Pill carousel: 4 pockets at 45, 90, 135, 180 degrees; solid at 0 degrees = closed
disk = Manifold.cylinder(7, 18, 18, SEG)
for k in range(1, 5):
    a = math.radians(-45 * k)
    disk = disk - cyl_z(SLOT_R * math.cos(a), SLOT_R * math.sin(a), POCKET_R, 1.2, 8)
disk = disk - cyl_z(0, 0, 1.2, -1, 8)                       # horn screw
disk = disk - box(-10.5, 10.5, -3.2, 3.2, -1, 1.8)          # single-arm horn recess


def save(m, name):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts))
    t.export(os.path.join(OUT, name))
    return t


if __name__ == "__main__":
    for m, n in ((front, "front_shell.stl"), (back, "back_shell.stl"), (disk, "pill_carousel.stl")):
        t = save(m, n)
        print(f"{n}: {t.bounds[1] - t.bounds[0]} mm, volume {t.volume / 1000:.1f} cm³, watertight {t.is_watertight}")
