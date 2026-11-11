#!/usr/bin/env python3
"""Sumo wheel like the MakerPH photo: printed cup hub + silicone tyre, and a one-piece open mold
(same idea as your mold_onepiece_62.4mm: cup = tyre OD, centre key locates the hub, spill tray,
2 push-out holes). Hub bore = N20 3 mm D-shaft; the N20 gearbox sits inside the cup.
Sizes: 42 x 30 and 30 x 23 (photo) + 34 x 10 (fits sumo-v2). Run: python3 wheel_mold.py"""
import os, glob, re, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(96)
HERE = os.path.dirname(os.path.abspath(__file__))
SIZES = [(42.0, 30.0), (30.0, 23.0), (34.0, 10.0)]          # tyre OD x width
WEB, LIP, NRIB = 3.0, 1.5, 16
FLOOR, WALL = 3.0, 3.0


def cyl(z0, z1, d, d1=None):
    return Manifold.cylinder(z1 - z0, d / 2, (d if d1 is None else d1) / 2).translate([0, 0, z0])


def dbore(z0, z1, d=3.1, flat=1.05):                          # N20 D-shaft hole (3 mm, 2.5 across the flat)
    return cyl(z0, z1, d) ^ Manifold.cube([d, flat + d / 2, z1 - z0 + 2]).translate([-d / 2, -d / 2, z0 - 1])


def dims(D, W):
    fl = round(0.81 * D, 1)                                    # hub flange OD (photo ratio)
    core = fl - 4.0                                            # rim under the tyre
    return dict(fl=fl, core=core, cup=core - 5.0, boss=9.0 if D >= 36 else 8.0, bh=min(8.0, W - 1.5))


def hub(D, W):
    p = dims(D, W); ch = (p['fl'] - p['core']) / 2
    m = cyl(0, W, p['core']) + cyl(0, LIP, p['fl'])                           # rim + outer-face flange
    m += cyl(W - LIP, W, p['fl']) + cyl(W - LIP - ch, W - LIP, p['core'], p['fl'])   # motor-side flange, 45 deg underside
    rib = Manifold.cube([1.5, 1.6, W - 2 * LIP - ch]).translate([p['core'] / 2 - 0.5, -0.8, LIP])
    for i in range(NRIB):                                                     # grip ribs (tyre can't spin)
        m += rib.rotate([0, 0, 360 * i / NRIB])
    m -= cyl(WEB, W + 1, p['cup'])                                            # cup (opens toward the motor)
    m += cyl(0, p['bh'], p['boss'])
    return m - dbore(-1, p['bh'] + 1)


def tyre(D, W):
    return cyl(0, W, D) - cyl(-1, W + 1, dims(D, W)['core']) - hub(D, W)


def mold(D, W):
    p = dims(D, W); R = D / 2; rt = R + WALL + 7
    m = cyl(0, FLOOR, 2 * (rt + 2))                                           # base disk
    m += cyl(0, FLOOR + W + 1, D + 2 * WALL) - cyl(FLOOR, FLOOR + W + 2, D)  # cup = tyre OD, 1 mm above the hub
    m -= cyl(FLOOR + W - 1.4, FLOOR + W + 1.01, 2 * rt) - cyl(FLOOR + W - 1.4, FLOOR + W + 1.01, D + 2 * WALL + 0.02, D + 1.2)  # outside top chamfer
    m += cyl(0, FLOOR + 5, 2 * (rt + 2)) - cyl(FLOOR, FLOOR + 6, 2 * rt)      # spill tray rim
    m += dbore(FLOOR - 0.01, FLOOR + p['bh'] - 1.5, 2.95, 0.95)               # D key into the hub bore
    e = p['core'] / 2 * 0.6
    for s in (-1, 1):
        m -= Manifold.cylinder(FLOOR + 2, 2.0).translate([0, s * e, -1])      # push-out holes (under the hub)
    return m


def stl(m, path):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, T
    open(os.path.join(HERE, path), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


if __name__ == '__main__':
    v = lambda m: round(m.volume(), 2)
    rows, info = [], {}
    for D, W in SIZES:
        tag = f'{D:.0f}x{W:.0f}'
        H, Ty, M = hub(D, W), tyre(D, W), mold(D, W)
        Hm = H.translate([0, 0, FLOOR])
        print(tag, dims(D, W), '| hub in mold overlap', v(Hm ^ M), '| tyre', round(Ty.volume() / 1000, 2), 'cm3',
              '| parts', len(H.decompose()), len(M.decompose()), len(Ty.decompose()))
        stl(H, f'hub_{tag}.stl'); stl(M, f'mold_{tag}.stl')
        for nm, extra in ((f'hub_{tag}', ['--fill-density', '25%', '--perimeters', '3']), (f'mold_{tag}', ['--fill-density', '15%', '--perimeters', '2'])):
            old = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))
            if not (os.environ.get('NOSLICE') and old):                       # NOSLICE=1: reuse existing G-code
                for g in old:
                    os.remove(g)
                subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *extra, '--center', '122.5,117.5',
                                '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
            g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
            info[nm] = (float(re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-300000:]).group(1)), re.search(r'_PETG_(.+)\.gcode', g).group(1))
            print('  ', os.path.basename(g), info[nm][0], 'g')
        rows.append((D, W, tag, H, Ty, M))

    # ---------------- picture ----------------
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82])
    HUBC, TYC, MOC = (0.82, 0.84, 0.88), (0.36, 0.66, 0.82), (0.95, 0.55, 0.25)

    def render(ax, items, lim, title, el=32, az=-60, zc=0):
        TT, CC = [], []                                                       # one collection -> correct depth order
        for m, col in items:
            me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.35 + 0.65 * np.abs(n @ L), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(zc - lim, zc + lim); ax.set_box_aspect((1, 1, 1), zoom=1.25)
        ax.view_init(el, az); ax.axis('off'); ax.set_title(title, fontsize=10, weight='bold')

    def section(ax, items, D, W):
        for m, col, hatch in items:
            for q in m.rotate([90, 0, 0]).slice(0.0).to_polygons():
                q = np.asarray(q); ax.fill(q[:, 0], -q[:, 1], fc=col, ec='k', lw=0.6, hatch=hatch)
        p = dims(D, W); z0 = FLOOR
        def dim(a, b, t, vert=False):
            ax.annotate('', a, b, arrowprops=dict(arrowstyle='<|-|>', lw=0.7, mutation_scale=7))
            ax.text((a[0] + b[0]) / 2 + (1.5 if vert else 0), (a[1] + b[1]) / 2 + (0 if vert else 1.2), t, fontsize=7.5,
                    ha='left' if vert else 'center', va='center' if vert else 'bottom', bbox=dict(fc='white', ec='none', pad=0.3))
        top = z0 + W
        dim((-D / 2, top + 6), (D / 2, top + 6), f'tyre Ø{D:.0f}')
        dim((-p['fl'] / 2, top + 2.2), (p['fl'] / 2, top + 2.2), f'flange Ø{p["fl"]:.1f}')
        dim((-p['cup'] / 2, top - 1.0), (p['cup'] / 2, top - 1.0), f'cup Ø{p["cup"]:.1f}')
        dim((D / 2 + WALL + 2.5, z0), (D / 2 + WALL + 2.5, top), f'{W:.0f}', vert=True)
        ax.annotate('N20 D-bore\n3 mm / 2.5 flat', (0.8, z0 + p['bh'] * 0.6), (D / 2 + WALL + 9, z0 + W * 0.35), fontsize=7, ha='center',
                    arrowprops=dict(arrowstyle='-|>', lw=0.6, mutation_scale=6), bbox=dict(fc='white', ec='none', pad=0.3))
        ax.set_aspect('equal'); ax.axis('off'); ax.set_title(f'Section — hub + silicone in the mold', fontsize=10, weight='bold')
        ax.set_xlim(-(D / 2 + WALL + 10), D / 2 + WALL + 16); ax.set_ylim(-2, top + 11)

    fig = plt.figure(figsize=(18, 5.2 * len(rows)))
    fig.suptitle('Silicone sumo wheel — printed cup hub + one-piece open mold (N20 D-shaft)', fontsize=15, weight='bold', y=0.995)
    cut = lambda m: m - Manifold.cube([200, 200, 200]).translate([0, -200, -50])
    for r, (D, W, tag, H, Ty, M) in enumerate(rows):
        lim = D / 2 + 12
        render(fig.add_subplot(len(rows), 4, 4 * r + 1, projection='3d'), [(H, HUBC)], D * 0.62, f'{tag}: hub (cup faces the motor)', el=50, zc=W / 2)
        render(fig.add_subplot(len(rows), 4, 4 * r + 2, projection='3d'), [(H, HUBC), (Ty, TYC)], D * 0.62, f'{tag}: finished wheel', el=35, zc=W / 2)
        render(fig.add_subplot(len(rows), 4, 4 * r + 3, projection='3d'), [(cut(M), MOC), (cut(H.translate([0, 0, FLOOR])), HUBC),
               (cut(Ty.translate([0, 0, FLOOR])), TYC)], lim, f'{tag}: mold cut-away', el=28, zc=W / 2)
        section(fig.add_subplot(len(rows), 4, 4 * r + 4), [(M, '#f4b183', '///'), (H.translate([0, 0, FLOOR]), '#d9dde3', None),
                (Ty.translate([0, 0, FLOOR]), '#7cc0e0', None)], D, W)
    plt.tight_layout(rect=(0, 0, 1, 0.985)); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=95)

    tab = '\n'.join(f"| {D:.0f} × {W:.0f} | `hub_{t}` {info[f'hub_{t}'][0]:.0f} g, {info[f'hub_{t}'][1]} | `mold_{t}` {info[f'mold_{t}'][0]:.0f} g, {info[f'mold_{t}'][1]} | "
                    f"{tyre(D, W).volume() / 1000:.1f} cm³ |" for D, W, t, *_ in rows)
    open(os.path.join(HERE, 'README.md'), 'w').write(f"""# Silicone sumo wheel — hub + one-piece mold

![preview](preview.png)

Like the MakerPH photo: printed cup hub (flange ring flush with the tyre face, deep cup), silicone tyre cast on it.
One-piece open mold like your `mold_onepiece_62.4mm`: cup = tyre OD, centre D-key holds the hub, spill tray, 2 push-out holes.

| wheel Ø × width | hub (fast PETG, 0.32 mm) | mold (fast PETG, 0.32 mm) | silicone per wheel |
|---|---|---|---|
{tab}

**Hub:** N20 3 mm D-shaft bore (press fit + drop of CA), the gearbox sits inside the cup. 16 ribs + 2 flanges lock the tyre.

**Casting**
1. Thin mold release on the mold cup and floor (not on the hub).
2. Push the hub onto the centre key, cup facing up. Put a coin or nut in the cup (needed: the hub is not solid and would float).
3. Mix silicone (Shore 20–30 A, platinum or tin cure), degas if you can, pour slowly into the ring gap
   up to the hub's top face. Spill goes into the tray.
4. Cure, then push the wheel out through the 2 holes under the hub. Trim the top edge if needed.
""")
