"""Lid for Predator Mini 2WD that carries the Cytron MOTION 2350 Pro (95.2 x 57.2) on 4 bosses.
Assumed hole pattern 88 x 48 mm (LEGO pitch) - bosses are 9 mm wide so small offsets can be re-drilled."""
import os, sys, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predator_mini_2wd import *
BXC, HX, HY, BH = 4.5, 24.0, 44.0, 5.0
m = box(XR, XW, -S, S, H, ZL)
for px, py in POSTS:
    for s in (-1, 1):
        m -= cyl(px, s * py, H - 1, ZL + 1, 3.4)
        m -= Manifold.cylinder(1.6, 1.7, 3.3).translate([px, s * py, ZL - 1.59])
m -= box(BXC - 6, BXC + 6, -15, 15, H - 1, ZL + 1)                       # wires to the board
for sx in (-1, 1):
    for sy in (-1, 1):
        x, y = BXC + sx * HX, sy * HY
        m += box(max(x - 4.5, XR), min(x + 4.5, XW), y - 4.5, y + 4.5, ZL - 0.01, ZL + BH) - cyl(x, y, ZL - 2, ZL + BH + 1, 2.6)
board = box(BXC - 28.6, BXC + 28.6, -47.6, 47.6, ZL + BH, ZL + BH + 1.6)
print('parts', len(m.decompose()), 'lid^base', round((m ^ BASE).volume(), 2), 'board x', BXC - 28.6, BXC + 28.6, 'lid x', XR, XW)
stl(floor0(m), 'lid_motion2350.stl')
for g in glob.glob(os.path.join(HERE, 'lid_motion2350_PETG_*.gcode')): os.remove(g)
subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '20%', '--perimeters', '3',
                '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, 'lid_motion2350.stl')], check=True, capture_output=True)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); fig = plt.figure(figsize=(8, 6)); ax = fig.add_subplot(projection='3d'); TT, CC = [], []
for mm, col in ((BASE, (0.85, 0.35, 0.2)), (m, (0.25, 0.25, 0.3)), (board, (0.5, 0.2, 0.6)), (WHEELS, (0.1, 0.1, 0.1))):
    me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
ax.set_xlim(-60, 80); ax.set_ylim(-70, 70); ax.set_zlim(-40, 100); ax.set_box_aspect((1, 1, 1), zoom=1.4); ax.view_init(28, -55); ax.axis('off')
ax.set_title('Predator Mini 2WD + MOTION 2350 Pro lid (purple = board)')
plt.savefig(os.path.join(HERE, 'lid_motion2350.png'), dpi=100)
