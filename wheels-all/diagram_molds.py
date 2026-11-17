import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheels_all import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Patch


def section(m):   # cut through the axis (xz plane): rotate so y -> z and slice at 0
    return [np.c_[np.asarray(q)[:, 0], -np.asarray(q)[:, 1]][::-1] for q in m.rotate([90, 0, 0]).slice(0).to_polygons()]   # vertical = z


def fill(ax, polys, col, **kw):
    for q in sorted(polys, key=lambda q: -abs(np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1]))):
        a = np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])
        ax.add_patch(Polygon(np.c_[q[:, 0], -q[:, 1]] if False else q, closed=True, fc=col if a > 0 else 'white', ec='k', lw=0.6, **kw))


def dim(ax, a, b, t, off=(0, 0), fs=8):
    ax.annotate('', a, b, arrowprops=dict(arrowstyle='<|-|>', lw=0.7, mutation_scale=7, shrinkA=0, shrinkB=0))
    ax.text((a[0] + b[0]) / 2 + off[0], (a[1] + b[1]) / 2 + off[1], t, fontsize=fs, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=0.3))


fig = plt.figure(figsize=(18, 10), facecolor='white')
fig.suptitle('SILICONE WHEEL MOLDS — cross-section (cut through the centre)', fontsize=16, weight='bold')
for k, (D, W) in enumerate(SIZES):
    ax = fig.add_subplot(2, 4, k + 1); M = mold(D, W); H = hub(D, W).translate([0, 0, BASE])
    top = BASE + W + 0.2; ro = D / 2 + (W + 0.2) * np.tan(DRAFT); bo = (D + 2 * TUBE + 2 * RIM + 6) / 2
    tyre = cyl(BASE, BASE + W, D) - cyl(BASE - 1, BASE + W + 1, D - 15.0)
    fill(ax, section(tyre), '#f4b183'); fill(ax, section(H), '#3a3a3a'); fill(ax, section(M), '#b8bec8')
    dim(ax, (-D / 2, top + 3), (D / 2, top + 3), f'cavity Ø{D} (tyre)')
    dim(ax, (bo + 3, 0), (bo + 3, top), f'{top:.1f}', off=(2.2, 0))
    dim(ax, (-bo, -3), (bo, -3), f'base Ø{2 * bo:.0f}')
    dim(ax, (-bo - 3, BASE), (-bo - 3, BASE + W), f'hub {W}', off=(-3, 0))
    ax.annotate(f'wall {TUBE}', (ro + TUBE / 2, top - 4), (ro + 8, top - 1), fontsize=7.5, arrowprops=dict(arrowstyle='-', lw=0.5))
    ax.annotate(f'base {BASE}', (bo - 2, BASE / 2), (bo + 1, -7.5), fontsize=7.5, arrowprops=dict(arrowstyle='-', lw=0.5))
    ax.annotate('pin Ø2.1', (0, BASE + 3), (-D / 2 + 1, BASE + W * 0.55 + 2), fontsize=7.5, color='#1f4e9a', arrowprops=dict(arrowstyle='-', lw=0.5, color='#1f4e9a'))
    ax.annotate('spill rim', (bo - RIM / 2, BASE + 2.5), (bo + 1.5, BASE + 4.5), fontsize=7.5, arrowprops=dict(arrowstyle='-', lw=0.5))
    r = max(bo, top) + 12
    ax.set_xlim(-bo - 12, bo + 14); ax.set_ylim(-11, top + 8); ax.set_aspect('equal'); ax.axis('off')
    t = open(sorted(__import__('glob').glob(os.path.join(HERE, 'molds', f'mold_{D}x{W}_PETG_*.gcode')))[0]).name
    ax.set_title(f'mold_{D}x{W}   ({t.split("_PETG_")[1][:-6]} print)', fontsize=12, weight='bold')
ax = fig.add_subplot(2, 4, 8); ax.axis('off')
ax.legend(handles=[Patch(fc='#b8bec8', ec='k', label='mold (print this)'), Patch(fc='#3a3a3a', ec='k', label='hub (separate print)'),
                   Patch(fc='#f4b183', ec='k', label='silicone tyre')], loc='upper left', fontsize=11, frameon=False)
ax.text(0.0, 0.62, 'HOW TO CAST\n1  Thin mold release inside the tube\n2  Push the hub onto the centre pin\n    (hole on the pin, it sits flat)\n'
        '3  Mix silicone, pour slowly beside the hub\n    to the brim (tyre ends flush with the hub)\n4  Let it cure fully\n5  Pull the hub + tyre straight up\n    (1.5° taper, lead-in chamfer)\n6  Drill the shaft hole at the top centre mark\n\n'
        f'Mold: base {BASE} · wall {TUBE} · rim {RIM} · draft 1.5°\nPrint: open side up, no supports, 0.24 mm, 3 walls', transform=ax.transAxes, fontsize=10.5, va='top', family='DejaVu Sans')
plt.tight_layout(rect=(0, 0, 1, 0.95)); plt.savefig(os.path.join(HERE, 'molds', 'diagram_molds.png'), dpi=120)
