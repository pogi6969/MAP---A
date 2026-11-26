#!/usr/bin/env python3
"""Copy of the MakerPH / Cytron "High Grade Silicone Wheel 32 x 22 mm" (sumo, 500 g class) as a printed hub + silicone mold,
with the same N20 motor connection as the other N20 hubs.
Product: complete wheel 32 mm OD x 22 mm wide, aluminium rim 26 mm x 22 mm, silicone tyre 20 mm wide, 3 mm motor shaft.
Hub = the rim: two 26 mm flanges (1 mm thick, 20 mm tyre between them), 22 mm barrel, 45 deg chamfer under the top flange.
Motor connection (as the N20 hubs): 3 mm D-shaft bore (3.1 / 2.6 across the flat) 10 mm deep from the motor side with an
entry cone, M3 set screw (2.6 pilot, 4.8 counterbore) square onto the flat, 8 mm in from the motor face. Top stays closed.
Mold = same format as the other molds, but the centre pin is a D key that fills the bore (no silicone in it, and it turns
the hub so the set-screw hole faces the side pin). Side pin (printed with the mold) goes through the mold wall into the
set-screw hole and keeps it open through the tyre: pull it out before demolding."""
import os, re, glob, subprocess
import numpy as np
from manifold3d import Manifold
from wheels_all import BASE, TUBE, RIM, DRAFT, cyl, stl, HERE
from combine import write_3mf

D, W = 32, 22                     # tyre OD, wheel width
FD, BD, FT = 26.0, 22.0, 1.0      # rim flange diameter, barrel diameter, flange thickness
BORE, FLAT, DEPTH = 3.1, 1.05, 10.0   # N20 D bore: diameter, centre-to-flat (2.6 across the flat), depth
ZS = 8.0                          # set screw height from the motor face
OUT = os.path.join(HERE, 'copy_32x22')
INI = os.path.join(HERE, 'cr6se_petg_fast.ini')
HUB_ARGS = ['--layer-height', '0.32', '--fill-density', '100%', '--fill-pattern', 'rectilinear', '--perimeters', '3']
MOLD_ARGS = ['--layer-height', '0.24', '--fill-density', '15%', '--fill-pattern', 'gyroid', '--perimeters', '3', '--bottom-solid-layers', '4', '--top-solid-layers', '4']


def dbore(z0, z1, d, flat):                       # single D: round side -d/2, flat at +flat (on +y)
    return cyl(z0, z1, d) ^ Manifold.cube([d + 1, d / 2 + flat, z1 - z0 + 2]).translate([-(d + 1) / 2, -d / 2, z0 - 1])


def radial_y(z, r0, r1, d):                        # hole along +y from radius r0 to r1 at height z
    return Manifold.cylinder(r1 - r0, d / 2).rotate([-90, 0, 0]).translate([0, r0, z])


def hub_copy():
    ch = (FD - BD) / 2
    h = (cyl(0, 0.5, FD - 1.0, FD) + cyl(0.5, FT, FD) + cyl(FT - 0.01, W - FT - ch + 0.01, BD)
         + cyl(W - FT - ch, W - FT + 0.01, BD, FD) + cyl(W - FT, W, FD))
    h -= dbore(-1, DEPTH, BORE, FLAT) + cyl(-0.01, 1.0, 5.0, BORE)                    # N20 D bore + entry cone (motor side)
    h -= radial_y(ZS, 0, BD / 2 + 1, 2.6) + radial_y(ZS, BD / 2 - 2.5, BD / 2 + 1, 4.8)  # M3 set screw onto the flat
    return h


def mold_n20():
    top = BASE + W + 0.2; ro = D / 2 + (W + 0.2) * np.tan(DRAFT); bd = D + 2 * TUBE + 2 * RIM + 6
    m = cyl(0, 0.6, bd - 1.2, bd) + cyl(0.6, BASE, bd) + (cyl(BASE - 0.01, BASE + 3, bd) - cyl(BASE - 0.1, BASE + 3.1, bd - 2 * RIM))
    m += cyl(BASE - 0.01, top, 2 * ro + 2 * TUBE)
    m -= cyl(BASE, top + 0.01, D, 2 * ro) + cyl(top - 0.8, top + 0.01, 2 * ro, 2 * ro + 1.6)                   # cavity + lead-in
    m += cyl(BASE - 0.01, BASE + 0.6, 4.4, BORE - 0.15)                                                        # key root
    m += dbore(BASE + 0.3, BASE + DEPTH - 1.5, BORE - 0.15, FLAT - 0.075) + (cyl(BASE + DEPTH - 1.5, BASE + DEPTH - 0.9, BORE - 0.15, 1.2) ^
                                                                            dbore(BASE + DEPTH - 1.6, BASE + DEPTH, BORE - 0.15, FLAT - 0.075))  # D key, chamfered tip
    wall_out = D / 2 + (ZS + 0.2) * np.tan(DRAFT) + TUBE
    return m - radial_y(BASE + ZS, D / 2 - 2, wall_out + 1, 4.9)                                             # side pin hole


def side_pin():                                    # along +y, flat-sided so it prints lying down
    r0 = BD / 2 - 2.4; r1 = D / 2 + (ZS + 0.2) * np.tan(DRAFT) + TUBE + 1.0
    body = radial_y(0, r0, r1, 4.6) + radial_y(0, r1, r1 + 2, 8.0)
    return body ^ Manifold.cube([10, r1 + 4, 4.2], center=True).translate([0, (r1 + 4) / 2, 0])


def slice_gcode(src, args, base):
    gc = os.path.join(OUT, base + '.gcode')
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', INI, *args, '--output', gc, src], check=True, capture_output=True)
    t = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', open(gc).read()).group(1)
    name = os.path.join(OUT, f'{base}_PETG_' + ''.join(n + u for n, u in re.findall(r'(\d+)([dhm])', t)) + '.gcode')
    os.replace(gc, name)
    return os.path.basename(name)


def preview(H, M0, Pp, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rot = lambda m: m.rotate([0, 0, -90]).rotate([-90, 0, 0])            # cut through the set-screw axis (screw side on the right)
    Hb = H.translate([0, 0, BASE])
    sil = cyl(BASE, BASE + W + 0.2, D) - Hb - cyl(BASE - 0.1, BASE + DEPTH + 0.1, 5.2) - Pp
    secs = {'silicone': rot(sil).slice(0), 'mold': rot(M0).slice(0), 'hub': rot(Hb).slice(0), 'pin': rot(Pp).slice(0)}
    fig, ax = plt.subplots(figsize=(8.2, 5.4), dpi=150)
    cols = {'silicone': '#7fd3f0', 'mold': '#5b6573', 'hub': '#e8b04a', 'pin': '#3b6fd8'}
    for name in ('silicone', 'mold', 'hub', 'pin'):
        for poly in secs[name].to_polygons():
            q = np.asarray(poly); ax.fill(q[:, 0], q[:, 1], color=cols[name], lw=0.6, ec='#222222', label=name)
    hd, lb = ax.get_legend_handles_labels(); u = dict(zip(lb, hd))
    ax.legend([u['hub'], u['silicone'], u['mold'], u['pin']], ['hub (print)', 'silicone tyre (cast)', 'mold with D key (print)',
              'side pin (print) - pull out before demolding'], loc='upper left', bbox_to_anchor=(0.0, 1.0), fontsize=7.5)
    z0 = BASE
    for x0, x1, y, txt in ((-D / 2, D / 2, z0 + W + 3.2, 'tyre OD 32'), (-FD / 2, FD / 2, z0 + W + 1.2, 'rim flange 26'),
                           (-BD / 2, BD / 2, z0 + 17, 'barrel 22')):
        ax.annotate('', (x0, y), (x1, y), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(0, y + 0.35, txt, ha='center', fontsize=8)
    ax.annotate('N20 3 mm D bore\n10 deep (motor side)', (0, z0 + 6), (-23, z0 + 9), fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.7))
    ax.annotate('M3 set screw\nonto the flat', (BD / 2 - 1, z0 + ZS + 2.4), (6, z0 + 13.5), fontsize=7.5, arrowprops=dict(arrowstyle='->', lw=0.7))
    ax.annotate('', (26, z0), (26, z0 + W), arrowprops=dict(arrowstyle='<->', lw=0.8))
    ax.text(26.7, z0 + W / 2, 'width 22\n(tyre 20 between\nthe flanges)', fontsize=8, va='center')
    ax.set_aspect('equal'); ax.set_xlim(-27, 38); ax.set_ylim(-1, z0 + W + 6); ax.axis('off')
    ax.set_title('32 x 22 wheel with N20 connection: hub on the D key, side pin in the set-screw hole, silicone around', fontsize=9.5)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == '__main__':
    for g in glob.glob(os.path.join(OUT, '*.gcode')): os.remove(g)
    H, M0, P = hub_copy(), mold_n20(), side_pin()
    Pp = P.translate([0, 0, BASE + ZS])                                    # pin in place (for the checks)
    print('key in bore overlap', round((H.translate([0, 0, BASE]) ^ M0).volume(), 3), '| pin in hub hole overlap',
          round((Pp ^ H.translate([0, 0, BASE])).volume(), 3), '| pin in mold wall overlap', round((Pp ^ M0).volume(), 3))
    b0 = M0.bounding_box(); pb = P.rotate([90, 0, 0]); pbb = pb.bounding_box()
    M = Manifold.compose([M0, pb.translate([b0[3] + 4 - pbb[0], -(pbb[1] + pbb[4]) / 2, -pbb[2]])])   # pin printed lying next to the mold
    print('parts: hub', len(H.decompose()), 'mold+pin', len(M.decompose()), '| tyre over barrel', (D - BD) / 2, 'over flange', (D - FD) / 2)
    stl(H, 'copy_32x22/hub_32x22.stl'); stl(M, 'copy_32x22/mold_32x22.stl')
    xm, xh = 0.0, -((D + 2 * TUBE + 2 * RIM + 6) / 2 + 3 + FD / 2)          # hub left of the mold, pin right of it
    both = Manifold.compose([M.translate([xm, 0, 0]), H.translate([xh, 0, 0])]); b = both.bounding_box()
    stl(both.translate([-(b[0] + b[3]) / 2, 0, 0]), 'copy_32x22/hub_and_mold_32x22.stl')
    sx = 117.5 - (b[0] + b[3]) / 2
    write_3mf(os.path.join(OUT, 'hub_and_mold_32x22.3mf'), [('mold', M, xm + sx, 117.5), ('hub', H, xh + sx, 117.5)])
    print(slice_gcode(os.path.join(OUT, 'hub_32x22.stl'), HUB_ARGS + ['--center', '117.5,117.5'], 'hub_32x22'))
    print(slice_gcode(os.path.join(OUT, 'mold_32x22.stl'), MOLD_ARGS + ['--center', '117.5,117.5'], 'mold_32x22'))
    print(slice_gcode(os.path.join(OUT, 'hub_and_mold_32x22.3mf'), ['--dont-arrange'], 'hub_and_mold_32x22'))
    preview(H, M0, Pp, os.path.join(OUT, 'preview_32x22.png'))
    print(sorted(os.listdir(OUT)))
