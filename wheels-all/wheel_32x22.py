#!/usr/bin/env python3
"""Copy of the MakerPH / Cytron "High Grade Silicone Wheel 32 x 22 mm" (sumo, 500 g class) as a printed hub + silicone mold.
Product: complete wheel 32 mm OD x 22 mm wide, aluminium rim 26 mm x 22 mm, silicone tyre 20 mm wide, 3 mm motor shaft.
Hub = the rim: two 26 mm flanges (1 mm thick, 20 mm tyre between them), 22 mm barrel, 45 deg chamfer under the top flange
(prints without supports), 0.5 mm chamfer at the bed, 2.6 mm socket underneath for the mold pin, centre mark on top:
drill 3 mm there after casting (same build as the other hubs, so no silicone gets into the hole).
Mold = same format as the other molds (2.4 base, 2.0 wall, spill rim, 1.5 deg draft, lead-in, centre pin), cavity 32 x 22.2."""
import os, re, glob, subprocess
import numpy as np
from manifold3d import Manifold
from wheels_all import BASE, TUBE, RIM, HOLE, cyl, mold, stl, HERE
from combine import write_3mf

D, W = 32, 22                     # tyre OD, wheel width
FD, BD, FT = 26.0, 22.0, 1.0      # rim flange diameter, barrel diameter, flange thickness
OUT = os.path.join(HERE, 'copy_32x22')
INI = os.path.join(HERE, 'cr6se_petg_fast.ini')
HUB_ARGS = ['--layer-height', '0.32', '--fill-density', '100%', '--fill-pattern', 'rectilinear', '--perimeters', '3']
MOLD_ARGS = ['--layer-height', '0.24', '--fill-density', '15%', '--fill-pattern', 'gyroid', '--perimeters', '3', '--bottom-solid-layers', '4', '--top-solid-layers', '4']


def hub_copy():
    ch = (FD - BD) / 2
    h = (cyl(0, 0.5, FD - 1.0, FD) + cyl(0.5, FT, FD) + cyl(FT - 0.01, W - FT - ch + 0.01, BD)
         + cyl(W - FT - ch, W - FT + 0.01, BD, FD) + cyl(W - FT, W, FD))
    h -= cyl(-1, 4.0, HOLE) + cyl(-0.01, 0.4, HOLE + 0.8, HOLE)          # mold-pin socket from below only
    return h - cyl(W - 0.6, W + 0.01, 0.4, 1.6)                          # centre mark on top: drill 3 mm here


def slice_gcode(src, args, base):
    gc = os.path.join(OUT, base + '.gcode')
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', INI, *args, '--output', gc, src], check=True, capture_output=True)
    t = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', open(gc).read()).group(1)
    name = os.path.join(OUT, f'{base}_PETG_' + ''.join(n + u for n, u in re.findall(r'(\d+)([dhm])', t)) + '.gcode')
    os.replace(gc, name)
    return os.path.basename(name)


def preview(H, M, path):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rot = lambda m: m.rotate([-90, 0, 0])                                  # section through the axis (x-z plane)
    secs = {'mold': rot(M).slice(0), 'hub': rot(H.translate([0, 0, BASE])).slice(0),
            'silicone': rot(cyl(BASE, BASE + W + 0.2, D) - H.translate([0, 0, BASE]) - cyl(BASE - 0.1, BASE + 4.1, HOLE + 1.0)).slice(0)}
    fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=150)
    for name, col in (('silicone', '#7fd3f0'), ('mold', '#5b6573'), ('hub', '#e8b04a')):
        for poly in secs[name].to_polygons():
            p = np.asarray(poly); ax.fill(p[:, 0], p[:, 1], color=col, lw=0.6, ec='#222222', label=name)
    hd, lb = ax.get_legend_handles_labels(); u = dict(zip(lb, hd))
    ax.legend([u['hub'], u['silicone'], u['mold']], ['hub (print)', 'silicone tyre (cast)', 'mold (print)'], loc='upper right', fontsize=8)
    z0 = BASE
    for x0, x1, y, txt in ((-D / 2, D / 2, z0 + W + 3.2, 'tyre OD 32'), (-FD / 2, FD / 2, z0 + W + 1.2, 'rim flange 26'),
                           (-BD / 2, BD / 2, z0 + W / 2, 'barrel 22')):
        ax.annotate('', (x0, y), (x1, y), arrowprops=dict(arrowstyle='<->', lw=0.8)); ax.text(0, y + 0.35, txt, ha='center', fontsize=8)
    ax.annotate('', (D / 2 + 4.5, z0), (D / 2 + 4.5, z0 + W), arrowprops=dict(arrowstyle='<->', lw=0.8))
    ax.text(D / 2 + 5.2, z0 + W / 2, 'width 22\n(tyre 20 between\nthe flanges)', fontsize=8, va='center')
    ax.set_aspect('equal'); ax.set_xlim(-26, 34); ax.set_ylim(-1, z0 + W + 6); ax.axis('off')
    ax.set_title('32 x 22 wheel copy: hub sits on the mold pin, silicone poured around it', fontsize=10)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


if __name__ == '__main__':
    for g in glob.glob(os.path.join(OUT, '*.gcode')): os.remove(g)
    H, M = hub_copy(), mold(D, W)
    print('hub inside mold overlap', round((H.translate([0, 0, BASE]) ^ M).volume(), 3), 'mm3 | parts', len(H.decompose()), len(M.decompose()),
          '| tyre radial thickness over barrel', (D - BD) / 2, 'over flange', (D - FD) / 2)
    stl(H, 'copy_32x22/hub_32x22.stl'); stl(M, 'copy_32x22/mold_32x22.stl')
    rm, rh = (D + 2 * TUBE + 2 * RIM + 6) / 2, FD / 2
    xm, xh = -(rh + 3), rm + 3
    both = Manifold.compose([M.translate([xm, 0, 0]), H.translate([xh, 0, 0])]); b = both.bounding_box()
    stl(both.translate([-(b[0] + b[3]) / 2, 0, 0]), 'copy_32x22/hub_and_mold_32x22.stl')
    sx = 117.5 - (b[0] + b[3]) / 2
    write_3mf(os.path.join(OUT, 'hub_and_mold_32x22.3mf'), [('mold', M, xm + sx, 117.5), ('hub', H, xh + sx, 117.5)])
    print(slice_gcode(os.path.join(OUT, 'hub_32x22.stl'), HUB_ARGS + ['--center', '117.5,117.5'], 'hub_32x22'))
    print(slice_gcode(os.path.join(OUT, 'mold_32x22.stl'), MOLD_ARGS + ['--center', '117.5,117.5'], 'mold_32x22'))
    print(slice_gcode(os.path.join(OUT, 'hub_and_mold_32x22.3mf'), ['--dont-arrange'], 'hub_and_mold_32x22'))
    preview(H, M, os.path.join(OUT, 'preview_32x22.png'))
    print(sorted(os.listdir(OUT)))
