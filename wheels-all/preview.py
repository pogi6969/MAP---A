import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheels_all import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
L = np.array([0.35, -0.45, 0.82]) / np.linalg.norm([0.35, -0.45, 0.82]); fig = plt.figure(figsize=(21, 7))
for k, (tag, p) in enumerate(SETS.items()):
    H = hub(*p); M, zp, ro = mold(*p); cut = Manifold.cube([80, 80, 80]).translate([0, -80, -10])
    ax = fig.add_subplot(1, 7, k + 1, projection='3d'); TT, CC = [], []
    for mm, col in ((M - cut, (0.75, 0.77, 0.8)), (H.translate([0, -2 * ro - 12, 0]), (0.25, 0.25, 0.27))):
        me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
    ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
    ax.set_xlim(-30, 30); ax.set_ylim(-75, -15 + 30); ax.set_zlim(-20, 40); ax.set_box_aspect((1, 1, 1), zoom=1.2); ax.view_init(25, -60); ax.axis('off'); ax.set_title(tag + '\nhub | mold (cut)', fontsize=10)
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=80)
