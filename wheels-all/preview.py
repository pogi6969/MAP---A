import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheels_all import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
L = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82])
for kind, fn, col in (('hubs', hub, (0.25, 0.25, 0.27)), ('molds', mold, (0.75, 0.77, 0.8))):
    fig = plt.figure(figsize=(21, 4.5))
    for k, (D, W) in enumerate(SIZES):
        ax = fig.add_subplot(1, 7, k + 1, projection='3d'); mm = fn(D, W)
        me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        ax.add_collection3d(Poly3DCollection(T, facecolors=np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1), edgecolors='none'))
        ax.set_xlim(-28, 28); ax.set_ylim(-28, 28); ax.set_zlim(-10, 46); ax.set_box_aspect((1, 1, 1), zoom=1.2); ax.view_init(30, -60); ax.axis('off')
        ax.set_title(f'{kind[:-1]}_{D}x{W}', fontsize=10)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, kind, f'preview_{kind}.png'), dpi=80); plt.close(fig)
