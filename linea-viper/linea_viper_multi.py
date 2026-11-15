#!/usr/bin/env python3
"""LineaViper chassis (from LineaViper-X16.stl: same 4 mm plate body, N20 bracket holes, windows, caster holes) revised
for 4 sensor bar sizes: X4, X8, X16 and X24 channels. Each = chassis with 2 arms carrying rows of M3 holes
(slide the sensor forward/back) + a sensor crossbar that bolts across the arms (2 holes per arm) and has 2 long slots,
so the sensor board screws on at any hole spacing in its range (X4 12-76, X8 30-110, X16 50-127, X24 80-196 mm). x forward, y left."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(40)
HERE = os.path.dirname(os.path.abspath(__file__))
YC, T, XE, AW, PITCH = 75.4, 4.0, 175.0, 10.0, 6.5
BODY = [(0, 43.8), (6.2, 36.05), (13.2, 36.0), (13.15, 30.57), (39.72, 30.57), (39.68, 36.16), (47.08, 36.16), (72, 47.4), (72, 103.6),
        (47.8, 115.47), (39.69, 115.47), (39.72, 120.16), (13.72, 120.16), (13.69, 115.46), (6.69, 115.51), (0.41, 107.82)]
WINDOWS = [(9.4, 48.5, 55.4, 69.9), (9.4, 48.5, 80.9, 95.4)]
HOLES = [(17.34, 37.3, 2.7), (34.44, 37.3, 2.7), (17.34, 113.43, 2.7), (34.44, 113.43, 2.7), (5.99, 40.86, 3.5), (43.94, 40.86, 3.5),
         (5.99, 109.86, 3.5), (43.94, 109.86, 3.5), (54.44, 61.76, 4.0), (54.44, 89.16, 4.0)]
VERSIONS = {'X4': (45.0, 6.0), 'X8': (62.0, 15.0), 'X16': (70.5, 25.0), 'X24': (105.0, 40.0)}  # arm offset, slot inner end


def rect(x0, x1, y0, y1): return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])
def circ(x, y, d): return CrossSection.circle(d / 2).translate([x, y])


def chassis(A):
    XS = 88.0 + max(0.0, A - 62) * 0.5
    c = CrossSection([BODY])
    for s in (1, -1):
        ya = YC + s * A
        e = [(47.8, 115.47), (72, 103.6)] if s > 0 else [(47.08, 36.16), (72, 47.4)]
        c += CrossSection.hull_points(e + [(55, YC + s * 25), (XS + 0.01, ya - AW / 2), (XS + 0.01, ya + AW / 2)])
        c += rect(XS, XE, ya - AW / 2, ya + AW / 2)
        for x in XE - 5 - PITCH * np.arange(0, int((XE - XS - 10) / PITCH)): c -= circ(x, ya, 3.2)
    for x0, x1, y0, y1 in WINDOWS: c -= rect(x0, x1, y0, y1)
    for x, y, d in HOLES: c -= circ(x, y, d)
    return Manifold.extrude(c, T)


def crossbar(A, s0):                              # built along x (length 2A + 12), depth 16 along y, centred at origin
    c = rect(-A - 6, A + 6, -8, 8)
    for s in (1, -1):
        for dy in (-PITCH / 2, PITCH / 2): c -= circ(s * A, dy, 3.4)
        c -= CrossSection.batch_hull([circ(s * s0, 0, 3.4), circ(s * (A - 7), 0, 3.4)])
    return Manifold.extrude(c, T)


if __name__ == '__main__':
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon
    fig, axs = plt.subplots(2, 2, figsize=(15, 15)); axs = axs.ravel()
    for ax, (name, (A, s0)) in zip(axs, VERSIONS.items()):
        ch = chassis(A); cb = crossbar(A, s0)
        plate = ch + cb.rotate([0, 0, 90]).translate([XE + 12, YC, 0])
        print(name, 'parts', len(plate.decompose()), 'bbox', np.round(plate.bounding_box(), 1))
        me = plate.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
        r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
        stl = os.path.join(HERE, f'LineaViper-{name}.stl')
        open(stl, 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '15%',
                        '--perimeters', '2', '--center', '122.5,117.5', '--output', HERE, stl], check=True, capture_output=True)
        X0 = XE - 5 - PITCH * 3.5; cbp = cb.rotate([0, 0, 90]).translate([X0, YC, T])   # crossbar bolted on, for the picture
        for mm, col in ((ch, '#b0b4ba'), (cbp, '#f2994a')):
            for q in sorted(mm.project().to_polygons(), key=lambda q: -abs(CrossSection([q]).area())):
                q = np.asarray(q); a = np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])
                ax.add_patch(Polygon(q, fc=col if a > 0 else 'white', ec='k', lw=0.5, zorder=2 if mm is cbp else 1))
        ax.set_xlim(-5, 185); ax.set_ylim(YC - 120, YC + 120); ax.set_aspect('equal'); ax.grid(lw=0.3)
        ax.set_title(f'LineaViper-{name}: arms {2 * A:.0f} mm apart, sensor slots fit holes {2 * s0:.0f}-{2 * (A - 7):.0f} mm apart', fontsize=11)
        ax.text(150, YC - A - 14, 'crossbar (orange): 2 x M3 per arm,\nslide along the arm holes', ha='center', fontsize=9)
    print(glob.glob(os.path.join(HERE, '*.gcode')))
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=90)
