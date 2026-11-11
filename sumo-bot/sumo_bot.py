#!/usr/bin/env python3
"""Mini sumo (10 x 10 cm, 500 g class) in the style of Predator: base + top lid + front blade.
2 x N20 gearmotor (2000 rpm) in built-in holders, Ø34 wheels, ballast bay behind the blade.
Footprint 99 x 99 mm. Axes: x forward, y left, z up, floor = 0. mm.
Run: python3 sumo_bot.py -> base.stl, lid.stl, blade.stl (print-ready), CR-6 SE PETG G-code, preview.png."""
import os, glob, re, shutil, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))
S = 49.5                                  # half footprint (99 mm)
XF = 30.0                                 # base front face (blade in front of it)
ZB, FT, H, LT = 3.0, 3.0, 30.0, 2.5       # floor underside, floor, wall top, lid
WD, WW, AX = 34.0, 10.0, -18.0            # wheel Ø, width, axle x
AZ = WD / 2                               # axle height
MW, MH, ML = 12.0, 10.0, 24.0             # N20 body (gearbox face 12 x 10), length incl. gearbox
MY0 = 4.0                                 # motor inner end |y|
MY1 = MY0 + ML + 0.5                      # gearbox face |y|
OW = 3.0                                  # holder outer wall (shaft side)
BLADE_A = 30.0                            # blade angle from the floor


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cyly(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])


def cylx(y, z, x0, x1, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def both(m):
    return m + m.mirror([0, 1, 0])


def xz(pts, y0, y1):
    p = np.asarray(pts, float)
    if np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]) < 0:
        p = p[::-1]
    return Manifold.extrude(CrossSection([p.tolist()]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


WELL = box(AX - WD / 2 - 1, AX + WD / 2 + 1, MY1 + OW + 0.5, S + 1, -1, H + LT + 1)   # wheel well (one side)
POSTS = [(-44.0, 43.0), (24.0, 43.0)]


def base():
    m = box(-S, XF, -S, S, ZB, ZB + FT)                                             # floor
    m += both(box(-S, XF, S - 2, S, ZB, H))                                         # side walls
    m += box(-S, -S + 2, -S, S, ZB, H)                                              # rear wall
    m += box(XF - 3, XF, -S, S, ZB, H)                                              # front bulkhead
    hz0 = AZ - MH / 2 - 0.2
    holder = box(AX - MW / 2 - 3, AX + MW / 2 + 3, MY0, MY1 + OW, ZB, AZ + MH / 2 + 3)
    holder -= box(AX - MW / 2 - 0.2, AX + MW / 2 + 0.2, MY0 - 1, MY1, hz0, AZ + MH / 2 + 0.2)  # motor tunnel
    holder -= cyly(AX, AZ, MY1 - 1, MY1 + OW + 1, 4.4)                              # gearbox boss / shaft
    for dx in (-4.5, 4.5):
        holder -= cyly(AX + dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)                     # M1.6 screws, 9 mm
    m += both(holder)
    m += box(0, 2, -S, S, ZB, ZB + FT + 10)                                         # ballast bay back wall
    for px, py in POSTS:                                                            # lid posts, M3 self-tap
        m += both(cyl(px, py, ZB, H, 7) - cyl(px, py, ZB + FT, H + 1, 2.6))
    m += both(box(XF - 8, XF - 3, 26, 34, ZB, ZB + FT + 9))                         # blade screw bosses
    m -= both(WELL)
    m -= both(cylx(30, ZB + FT + 5, XF - 9, XF + 1, 2.6))                           # blade screws M3
    for y in (-30, 0, 30):                                                          # opponent sensor windows
        m -= cylx(y, 22, XF - 4, XF + 1, 8.5)
    m -= both(box(18, 26, 36, 44, ZB - 1, ZB + FT + 1))                             # line sensor holes
    m -= box(-40, -30, -12, 12, ZB - 1, ZB + FT + 1)                                # wiring hole
    return m


def lid():
    m = box(-S, XF, -S, S, H, H + LT) - both(WELL)
    for px, py in POSTS:
        m -= both(cyl(px, py, H - 1, H + LT + 1, 3.4))
    return m - cyl(-38, 0, H - 1, H + LT + 1, 6.5)                                  # power switch


def blade():
    t = np.tan(np.radians(BLADE_A))
    ztop = (S - XF) * t
    m = xz([(S, 0.0), (XF, ztop), (XF, ztop - 3 / np.cos(np.radians(BLADE_A)))], -S, S)  # sharp wedge, 3 mm
    m += box(XF, XF + 3, -S, S, ZB + 1, ZB + FT + 9)                               # mounting flange
    return m - both(cylx(30, ZB + FT + 5, XF - 1, XF + 4, 3.3))


BASE, LID, BLADE = base(), lid(), blade()


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m):
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    asm = BASE + LID + BLADE
    b = asm.bounding_box()
    print('footprint', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'height', round(b[5], 1))
    print('overlaps', round((BASE ^ LID).volume(), 2), round((BASE ^ BLADE).volume(), 2), 'parts', [len(p.decompose()) for p in (BASE, LID, BLADE)])
    stl(BASE, 'base.stl'); stl(floor0(LID), 'lid.stl'); stl(floor0(BLADE.rotate([0, -90, 0])), 'blade.stl')
    info = {}
    for g in glob.glob(os.path.join(HERE, '*.gcode')):
        os.remove(g)
    for nm in ('base', 'lid', 'blade'):
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg.ini'), '--fill-density', '40%',
                        '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
        g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
        info[nm] = float(re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-300000:]).group(1))
        print(os.path.basename(g), info[nm], 'g')
    parts = sum(info.values())
    other = {'2 x N20 motor': 20, '2 x wheel Ø34': 16, '2S LiPo ~450 mAh': 30, 'controller + driver': 20,
             '3 opponent + 2 line sensors': 20, 'screws, wires, switch': 15}
    ballast = 500 - parts - sum(other.values())
    print(f'printed {parts:.0f} g, parts {sum(other.values())} g -> ballast {ballast:.0f} g')
    # preview
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    wheels = both(cyly(AX, AZ, MY1 + OW + 1.5, MY1 + OW + 1.5 + WW, WD))
    motors = both(box(AX - MW / 2, AX + MW / 2, MY0, MY1, AZ - MH / 2, AZ + MH / 2) + cyly(AX, AZ, MY1, MY1 + 10, 3))
    fig = plt.figure(figsize=(13, 6.5))
    for k, (items, title) in enumerate((([(BASE, (0.85, 0.35, 0.2), 1), (BLADE, (0.6, 0.6, 0.65), 1), (LID, (0.2, 0.2, 0.25), 0.35),
                                          (wheels, (0.1, 0.1, 0.1), 1), (motors, (0.9, 0.8, 0.2), 1)], 'Assembled (lid see-through)'),
                                        ([(BASE, (0.85, 0.35, 0.2), 1), (motors, (0.9, 0.8, 0.2), 1)], 'Base with N20 holders'))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d')
        for mm, col, al in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            fc = np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1)
            ax.add_collection3d(Poly3DCollection(T, facecolors=np.c_[fc, np.full(len(T), al)], edgecolors='none'))
        ax.set_xlim(-55, 55); ax.set_ylim(-55, 55); ax.set_zlim(-20, 90); ax.set_box_aspect((1, 1, 1)); ax.view_init(28, -130 if k else -50)
        ax.axis('off'); ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=110)
    rows = '\n'.join(f'| {k} | {v} g |' for k, v in other.items())
    open(os.path.join(HERE, 'DESIGN.md'), 'w').write(f"""# Mini sumo — 99 × 99 mm, 500 g

![preview](preview.png)

Revised from Predator (base + top + front): same layout, shrunk to the 10 × 10 cm class.

| print (CR-6 SE, PETG, 3 walls, 40 % infill, no supports) | g |
|---|---|
| `base.stl` — floor down | {info['base']:.0f} |
| `lid.stl` — flat | {info['lid']:.0f} |
| `blade.stl` — flange down | {info['blade']:.0f} |

* **N20 holders** (in the base): tunnel {MW + 0.4:.1f} × {MH + 0.4:.1f} mm, {ML + 0.5:.1f} mm long (N20 2000 rpm with gearbox), Ø4.4 boss hole,
  2 × M1.6 screw holes 9 mm apart on the gearbox face. Slide the motors in from the middle.
* **Wheels** Ø{WD:.0f} × {WW:.0f} mm on the 3 mm D-shaft, axle {abs(AX):.0f} mm behind centre, inside the 99 mm width.
* **Blade**: 30° sharp wedge, full width, 2 × M3 into the base front.
* **Lid**: 4 × M3 into the posts, Ø6.5 power switch hole. 3 opponent-sensor windows Ø8.5 in the front, 2 line-sensor holes in the floor.

## Weight to 500 g
| item | estimate |
|---|---|
| printed parts | {parts:.0f} g |
{rows}
| **ballast to add** | **≈ {ballast:.0f} g** — lead in the bay behind the blade (26 × 92 × 14 mm ≈ 33 cm³ holds ≈ 370 g lead; steel only ≈ 260 g, put the rest under the lid) |

N20 at 2000 rpm with Ø{WD:.0f} wheels: ≈ {2000 * np.pi * WD / 60000:.1f} m/s top speed.
""")
