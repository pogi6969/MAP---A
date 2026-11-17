import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheels_all import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
set_circular_segments(160)
L = np.array([0.45, -0.55, 0.7]) / np.linalg.norm([0.45, -0.55, 0.7]); L2 = np.array([-0.6, 0.3, 0.4]) / np.linalg.norm([-0.6, 0.3, 0.4])
fig = plt.figure(figsize=(16, 9), facecolor='white')
for k, (D, W) in enumerate(SIZES):
    H = hub(D, W); FD = D - 15.0; BD = FD - 2.97
    ax = fig.add_subplot(2, 4, k + 1, projection='3d')
    me = H.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
    sh = 0.25 + 0.55 * np.clip(n @ L, 0, 1) + 0.2 * np.clip(n @ L2, 0, 1)
    ax.add_collection3d(Poly3DCollection(T, facecolors=np.clip(np.outer(sh, (0.62, 0.65, 0.72)), 0, 1), edgecolors='none'))
    r = max(FD, W) * 0.62
    ax.set_xlim(-r, r); ax.set_ylim(-r, r); ax.set_zlim(W / 2 - r, W / 2 + r); ax.set_box_aspect((1, 1, 1), zoom=1.25)
    ax.view_init(28, -55); ax.axis('off')
    ax.set_title(f'hub_{D}x{W}', fontsize=14, weight='bold', pad=0)
    ax.text2D(0.5, 0.02, f'flange Ø{FD:.0f} · body Ø{BD:.1f} · height {W}\npin socket Ø2.6 bottom · drill mark top\n' + ('6 notches (high-torque)' if D >= 42 else 'smooth'),
              transform=ax.transAxes, ha='center', fontsize=9.5)
ax = fig.add_subplot(2, 4, 8); ax.axis('off')
ax.text(0.05, 0.6, 'HUBS (silicone wheel)\n\nPrint: flange down, no supports\nCR-6 SE · PETG · 100% solid · 0.32 mm\n\nN20: 27x33, 34x27, 34x12,\n       32x12, 32x8\nJGA25 / TT: 42x20\nJGB37: 42x30\n\nAfter casting: drill the shaft hole\nat the top centre mark',
        fontsize=12, va='center', family='DejaVu Sans')
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'hubs', 'preview_hubs_zoom.png'), dpi=130)
