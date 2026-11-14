"""Labeled diagram of the micromouse (run plain: NOSENS=1)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from micromouse_v2 import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Poly, Patch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
plain = bool(os.environ.get('NOSENS'))
SK2 = SK.translate([XC + R - 12, 0, 0]) + SK.translate([XB + 5, 0, 0])
BOARD = box(BX0, BX0 + 95.2, -28.6, 28.6, ZR + 3, ZR + 4.6)
BEAMS = Manifold()
for x, y, a in SENS:
    BEAMS += Manifold.cylinder(45, 2.5, 2.5 + 45 * 0.27).rotate([0, 90, 0]).rotate([0, 0, a]).translate([x, y, ZP + PT + 7.5])
parts = [(CH, '#2f5fd0', 'chassis'), (RAIL, '#7aa2ff', 'board tray (8 mm grid holes)'), (BOARD, '#2e8b57', 'MOTION 2350 Pro 95.2 × 57.2'),
         (MOTORS, '#bdbdbd', '2 × N20 + encoder'), (WHEELS, '#d0283a', 'wheels Ø32 × 12 (silicone)'), (SK2, '#333333', 'skids')]


def proj(m, view):
    if view == 'top':
        mm, f = m, lambda q: q
    elif view == 'side':
        mm, f = m.rotate([90, 0, 0]), lambda q: np.c_[q[:, 0], -q[:, 1]]
    else:
        mm, f = m.rotate([0, -90, 0]), lambda q: np.c_[q[:, 1], -q[:, 0]]
    return [f(np.asarray(q)) for q in mm.project().to_polygons()]


def draw(ax, view, alpha_board=0.35):
    if not plain:
        for q in proj(BEAMS, view):
            ax.add_patch(Poly(q, closed=True, fc='#ffe08a', ec='#c9a400', lw=0.5, alpha=0.5, zorder=0))
    order = parts if view != 'top' else [parts[0], parts[3], parts[4], parts[5], parts[1], parts[2]]
    for m, c, _ in order:
        a = alpha_board if (view == 'top' and m in (RAIL, BOARD)) else 1
        for q in proj(m, view):
            ax.add_patch(Poly(q, closed=True, fc=c, ec='k', lw=0.4, alpha=a))
    ax.set_aspect('equal'); ax.axis('off')


def dim(ax, a, b, t):
    ax.annotate('', a, b, arrowprops=dict(arrowstyle='<|-|>', lw=0.8, mutation_scale=7))
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, t, fontsize=9, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=0.5))


fig = plt.figure(figsize=(16, 11))
title = 'MICROMOUSE — PLAIN CHASSIS' if plain else 'MICROMOUSE — 5 IR SENSORS'
fig.suptitle(f'{title}  |  Cytron MOTION 2350 Pro · 2 × N20 + encoder · Ø32 × 12 silicone wheels', fontsize=15, weight='bold')
gs = fig.add_gridspec(2, 3, height_ratios=[1.25, 1], hspace=0.12, wspace=0.05, left=0.02, right=0.98, top=0.93, bottom=0.03)
ax = fig.add_subplot(gs[0, 0:2]); ax.set_title('TOP VIEW (board + tray see-through' + ('' if plain else ', yellow = IR beams') + ')', loc='left', weight='bold')
draw(ax, 'top')
dim(ax, (XB, -60), (XC + R, -60), f'{XC + R - XB:.0f}'); dim(ax, (-75, -51), (-75, 51), '102')
if not plain:
    for x, y, a in SENS:
        ax.annotate(f'IR {a:+.0f}°', (x, y), (x + 22 * np.cos(np.radians(a)) + 8, y + 22 * np.sin(np.radians(a))), fontsize=8,
                    arrowprops=dict(arrowstyle='-', lw=0.5), bbox=dict(fc='white', ec='#c9a400', lw=0.5))
ax.text(XC + R + 6, 0, 'FRONT ▶', rotation=90, va='center', weight='bold')
ax.set_xlim(-85, 105); ax.set_ylim(-68, 68)
ax3 = fig.add_subplot(gs[0, 2], projection='3d')
L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); TT, CC = [], []
for m, c, _ in parts:
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    rgb = np.array(matplotlib.colors.to_rgb(c)); TT.append(T); CC.append(np.clip(np.outer(0.35 + 0.65 * np.abs(n @ L), rgb), 0, 1))
ax3.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
ax3.set_xlim(-50, 60); ax3.set_ylim(-55, 55); ax3.set_zlim(-15, 60); ax3.set_box_aspect((110, 110, 75), zoom=1.3); ax3.view_init(30, -130); ax3.axis('off')
ax3.set_title('3D', weight='bold')
ax = fig.add_subplot(gs[1, 0]); ax.set_title('SIDE VIEW', loc='left', weight='bold'); draw(ax, 'side')
ax.plot([-55, 70], [0, 0], color='#555'); dim(ax, (-50, 0), (-50, ZR + 4.6), f'{ZR + 4.6:.0f}')
ax.annotate('board on tray, M3 / Technic pins', (BX0 + 20, ZR + 4), (BX0 + 30, ZR + 18), fontsize=8, arrowprops=dict(arrowstyle='-', lw=0.5))
ax.set_xlim(-60, 75); ax.set_ylim(-8, 55)
ax = fig.add_subplot(gs[1, 1]); ax.set_title('FRONT VIEW', loc='left', weight='bold'); draw(ax, 'front')
ax.plot([-60, 60], [0, 0], color='#555'); ax.set_xlim(-60, 60); ax.set_ylim(-8, 55)
ax = fig.add_subplot(gs[1, 2]); ax.axis('off')
txt = ['PRINT  (CR-6 SE, PETG, 0.32 mm, no supports)', f'  {NAME}.stl  = chassis + tray + 2 skids', '',
       'MOUNTING', '  board: 4 × M3 + nut or 4 Technic pins', '         through the 8 mm grid holes (Ø4.9)', '  tray: 4 × M3 into the pillars',
       '  N20: 2 × M1.6 per gearbox + zip tie', '  skids: push in from below', '', 'WHEELS', '  N20_32x12_hub_and_mold (set screw M3)']
if not plain:
    txt += ['', 'SENSORS', '  5 × (IR LED 5 mm + photodiode 5 mm)', '  0°, ±45°, ±90° — tray and chassis clear', f'  of every beam, {ZR - (ZP + PT + 13):.1f} mm gap above blocks']
ax.text(0, 1, '\n'.join(txt), family='DejaVu Sans Mono', fontsize=10, va='top', transform=ax.transAxes)
ax.legend(handles=[Patch(fc=c, ec='k', label=l) for _, c, l in parts] + ([] if plain else [Patch(fc='#ffe08a', ec='#c9a400', label='IR beam')]),
          loc='lower left', fontsize=9, frameon=False)
fig.savefig(os.path.join(HERE, f'diagram_{"plain" if plain else "sensors"}.png'), dpi=110)
