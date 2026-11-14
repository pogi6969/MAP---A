import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sumo_2350 import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly, Patch
MOT = both(box(AX - 6, AX + 6, MY0, MY1, AZ - 5, AZ + 5))
parts = [(CH, '#b0b4ba', 'chassis'), (MOT, '#f2c94c', '2 × N20'), (WHEELS, '#333333', 'wheels Ø34 × 12'), (BOARD, '#7b2d8e', 'MOTION 2350 Pro 95.2 × 57.2')]
def proj(m, v):
    mm, f = {'top': (m, lambda q: q), 'side': (m.rotate([90, 0, 0]), lambda q: np.c_[q[:, 0], -q[:, 1]]),
             'front': (m.rotate([0, -90, 0]), lambda q: np.c_[q[:, 1], -q[:, 0]])}[v]
    return [f(np.asarray(q)) for q in mm.project().to_polygons()]
def draw(ax, v, see=False):
    for m, c, _ in parts:
        for q in proj(m, v):
            ax.add_patch(Poly(q, closed=True, fc=c, ec='k', lw=0.5, alpha=0.35 if (see and m is BOARD) else 1))
    ax.set_aspect('equal'); ax.axis('off')
def dim(ax, a, b, t):
    ax.annotate('', a, b, arrowprops=dict(arrowstyle='<|-|>', lw=0.8, mutation_scale=7))
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, t, fontsize=9, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=0.5))
fig = plt.figure(figsize=(15, 9.5)); fig.suptitle('SUMO 2350 — chassis for Cytron MOTION 2350 Pro + 2 × N20', fontsize=15, weight='bold')
gs = fig.add_gridspec(2, 2, left=0.02, right=0.98, top=0.92, bottom=0.03, hspace=0.1, wspace=0.05)
ax = fig.add_subplot(gs[0, 0]); ax.set_title('TOP VIEW (board see-through)', loc='left', weight='bold'); draw(ax, 'top', True)
for x, y in HOLES:
    for s in (1, -1): ax.plot(x, s * y, 'o', mfc='white', mec='r', ms=6)
ax.annotate('4 × M3 board screws\n(88 × 48 mm)', (HOLES[1][0], 44), (TIP + 5, 55), fontsize=8, color='r', arrowprops=dict(arrowstyle='-', color='r', lw=0.6))
dim(ax, (XR, -62), (TIP, -62), f'{TIP - XR:.1f}'); dim(ax, (XR - 10, -50), (XR - 10, 50), '100')
ax.text(TIP + 3, -5, 'FRONT ▶', rotation=90, weight='bold'); ax.set_xlim(XR - 18, TIP + 35); ax.set_ylim(-70, 70)
ax = fig.add_subplot(gs[0, 1]); ax.set_title('SIDE VIEW', loc='left', weight='bold'); draw(ax, 'side')
ax.plot([XR - 5, TIP + 5], [0, 0], color='#555'); dim(ax, (XR - 8, 0), (XR - 8, H), f'{H:.0f}')
ax.annotate(f'board on ledges at {ZBD:.0f} mm', (10, ZBD + 1), (20, ZBD + 12), fontsize=8, arrowprops=dict(arrowstyle='-', lw=0.6))
ax.annotate(f'wedge {WA:.0f}°', (TIP - 10, 6), (TIP, 20), fontsize=8, arrowprops=dict(arrowstyle='-', lw=0.6))
ax.set_xlim(XR - 15, TIP + 15); ax.set_ylim(-5, 55)
ax = fig.add_subplot(gs[1, 0]); ax.set_title('FRONT VIEW', loc='left', weight='bold'); draw(ax, 'front')
ax.plot([-55, 55], [0, 0], color='#555'); ax.set_xlim(-60, 60); ax.set_ylim(-5, 50)
ax = fig.add_subplot(gs[1, 1]); ax.axis('off')
ax.text(0, 0.95, '\n'.join(['PRINT  CR-6 SE · PETG · 0.32 mm · no supports · 3h16m', '  sumo_2350_chassis.stl (floor down)', '',
        'ASSEMBLY', '  N20: slide into holders, 2 × M1.6 on the gearbox', '  wheels: N20 34 × 12 hub + mold (wheel-mold-v2)',
        '  board: drop in, 4 × M3 into the ledges', '  USB / wires: notch in the back wall']), family='DejaVu Sans Mono', fontsize=11, va='top', transform=ax.transAxes)
ax.legend(handles=[Patch(fc=c, ec='k', label=l) for _, c, l in parts] + [Patch(fc='white', ec='r', label='board screw hole')], loc='lower left', fontsize=10, frameon=False)
fig.savefig(os.path.join(HERE, 'diagram.png'), dpi=110)
