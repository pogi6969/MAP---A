#!/usr/bin/env python3
"""Wheel hub + one-piece silicone mold v2, one set per motor. Same design as wheel-mold (cup hub, flanges, grip ribs,
one-piece open mold with centre key, spill tray, push-out holes) plus easy removal:
  * hub: collar outside the wheel with an M3 set screw + nut trap -> loosen 1 screw, wheel slides off the shaft
  * mold: 1.5 deg draft on the cup wall, 3 big push-out holes + 2 pry notches -> wheel pops out
Run: python3 wheel_mold_v2.py"""
import os, glob, re, subprocess
import numpy as np
from manifold3d import Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
# name: (tyre OD, width, shaft d, flat across (None = round), double-D?)
MOTORS = {'N20':        (34.0, 12.0, 3.0, 2.5, False),
          'JGA25-370':  (42.0, 20.0, 4.0, 3.5, False),
          'JGB37-520':  (42.0, 30.0, 6.0, 5.5, False),
          'TT-yellow':  (42.0, 20.0, 5.4, 3.7, True)}
WEB, LIP, NRIB, FLOOR, WALL, COL = 3.0, 1.5, 16, 3.0, 3.0, 7.0
DRAFT = np.radians(1.5)


def cyl(z0, z1, d, d1=None):
    return Manifold.cylinder(z1 - z0, d / 2, (d if d1 is None else d1) / 2).translate([0, 0, z0])


def bore(z0, z1, d, flat, dd, clr=0.1):
    d += clr
    m = cyl(z0, z1, d)
    if flat:
        f = flat + clr
        cut = Manifold.cube([d, d, z1 - z0 + 2]).translate([f - d / 2, -d / 2, z0 - 1])
        m -= cut
        if dd:
            m -= cut.mirror([1, 0, 0])
    return m


def dims(D, W, sd):
    fl = round(0.81 * D, 1); core = fl - 4.0
    boss = max(9.0, sd + 7.0)
    return dict(fl=fl, core=core, cup=core - 5.0, boss=boss, bh=min(8.0, W - 1.5), col=boss + 6.0)


def hub(D, W, sd, flat, dd):
    p = dims(D, W, sd); ch = (p['fl'] - p['core']) / 2
    m = cyl(0, W, p['core']) + cyl(0, LIP, p['fl']) + cyl(W - LIP, W, p['fl']) + cyl(W - LIP - ch, W - LIP, p['core'], p['fl'])
    rib = Manifold.cube([1.5, 1.6, W - 2 * LIP - ch]).translate([p['core'] / 2 - 0.5, -0.8, LIP])
    for i in range(NRIB):
        m += rib.rotate([0, 0, 360 * i / NRIB])
    m -= cyl(WEB, W + 1, p['cup'])
    m += cyl(-COL, p['bh'], p['boss']) + cyl(-COL, 0.01, p['col'])               # boss + outside collar
    m -= bore(-COL - 1, p['bh'] + 1, sd, flat, dd)
    zc = -COL / 2                                                                # M3 set screw + nut trap in the collar
    m -= Manifold.cylinder(p['col'], 1.6).rotate([0, 90, 0]).translate([0, 0, zc])
    m -= Manifold.cube([2.8, 5.8, COL + 2]).translate([sd / 2 + 1.2, -2.9, -COL - 1])   # nut slot, open at the bottom
    return m


def tyre(D, W, sd, flat, dd):
    return cyl(0, W, D) - cyl(-1, W + 1, dims(D, W, sd)['core']) - hub(D, W, sd, flat, dd)


def mold(D, W, sd, flat, dd):
    p = dims(D, W, sd); R = D / 2; rt = R + WALL + 7
    zf = FLOOR + COL                                                             # cavity floor (collar sits in a pocket)
    top = zf + W + 1
    m = cyl(0, zf, 2 * (rt + 2))
    m += cyl(0, top, D + 2 * WALL) - cyl(zf, top + 0.01, D, D + 2 * (W + 1) * np.tan(DRAFT))   # drafted cup
    m += cyl(0, zf + 5, 2 * (rt + 2)) - cyl(zf, zf + 6, 2 * rt)                  # spill tray
    m -= cyl(FLOOR, zf + 0.01, p['col'] + 0.6)                                   # collar pocket
    m += bore(FLOOR - 0.01, zf + p['bh'] - 1.5, sd - 0.15, (flat - 0.15) if flat else None, dd, 0)   # key into the bore
    e = (p['col'] / 2 + p['core'] / 2) / 2 + 0.5
    for a in (90, 210, 330):                                                     # push-out holes under the web
        m -= Manifold.cylinder(zf + 2, 2.6).translate([e * np.cos(np.radians(a)), e * np.sin(np.radians(a)), -1])
    for a in (0, 180):                                                           # pry notches in the cup rim
        m -= Manifold.cube([8, 6, 3]).translate([R - 1, -3, top - 2.5]).rotate([0, 0, a])
    return m


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m):
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


if __name__ == '__main__':
    rows, info = [], {}
    for g in glob.glob(os.path.join(HERE, '*.gcode')):
        os.remove(g)
    for name, (D, W, sd, flat, dd) in MOTORS.items():
        H, M, Ty = hub(D, W, sd, flat, dd), mold(D, W, sd, flat, dd), tyre(D, W, sd, flat, dd)
        Hm = H.translate([0, 0, FLOOR + COL])
        print(name, dims(D, W, sd), 'hub^mold', round((Hm ^ M).volume(), 2), 'parts', len(H.decompose()), len(M.decompose()))
        tag = f'{name}_{D:.0f}x{W:.0f}'
        stl(floor0(H.rotate([180, 0, 0])), f'hub_{tag}.stl')   # cup face on the bed, collar up; stl(M, f'mold_{tag}.stl')
        for nm, ex in ((f'hub_{tag}', ['--fill-density', '30%', '--perimeters', '4']), (f'mold_{tag}', ['--fill-density', '15%', '--perimeters', '2'])):
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                            '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
            g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
            info[nm] = (float(re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-300000:]).group(1)), re.search(r'_PETG_(.+)\.gcode', g).group(1))
        rows.append((name, D, W, sd, flat, dd, tag, H, Ty, M))
        print('  ', info[f'hub_{tag}'], info[f'mold_{tag}'])
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82])

    def render(ax, items, lim, title, zc):
        TT, CC = [], []
        for m, col in items:
            me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.35 + 0.65 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(zc - lim, zc + lim); ax.set_box_aspect((1, 1, 1), zoom=1.25)
        ax.view_init(30, -60); ax.axis('off'); ax.set_title(title, fontsize=10, weight='bold')

    cut = lambda m: m - Manifold.cube([200, 200, 200]).translate([0, -200, -50])
    fig = plt.figure(figsize=(15, 4.6 * len(rows)))
    for r, (name, D, W, sd, flat, dd, tag, H, Ty, M) in enumerate(rows):
        sh = f'Ø{sd:g} ' + ('double-D' if dd else 'D') + (f' {flat:g}' if flat else '')
        render(fig.add_subplot(len(rows), 3, 3 * r + 1, projection='3d'), [(H.rotate([180, 0, 0]), (0.82, 0.84, 0.88))], D * 0.62,
               f'{name}: hub, shaft {sh}, M3 set screw', 0)
        render(fig.add_subplot(len(rows), 3, 3 * r + 2, projection='3d'), [(H, (0.82, 0.84, 0.88)), (Ty, (0.36, 0.66, 0.82))], D * 0.62,
               f'{name}: wheel {D:.0f} × {W:.0f}', W / 2)
        render(fig.add_subplot(len(rows), 3, 3 * r + 3, projection='3d'), [(cut(M), (0.95, 0.55, 0.25)), (cut(H.translate([0, 0, FLOOR + COL])), (0.82, 0.84, 0.88)),
               (cut(Ty.translate([0, 0, FLOOR + COL])), (0.36, 0.66, 0.82))], D / 2 + 12, f'{name}: mold cut-away (draft, push-out holes)', W / 2 + 8)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=90)
