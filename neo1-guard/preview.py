import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from neo1_guard import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
set_circular_segments(64)
Z0 = 12.0                                         # guard rings height band z 12..22
rings = Manifold()
for sx in (-1, 1):
    for sy in (-1, 1):
        rings += Manifold.cylinder(10, RG).translate([sx * CX, sy * CY, Z0]) - Manifold.cylinder(12, RG - 1.6).translate([sx * CX, sy * CY, Z0 - 1])
body = box(-BODY_W_REAR / 2, BODY_W_REAR / 2, -65, 42, 4, 4 + BODY_H_REAR) + box(-BODY_W_CAM / 2, BODY_W_CAM / 2, 42, 62, 2, 2 + BODY_H_CAM)
BL = bumper_left().translate([0, 0, Z0]); BR = BL.mirror([1, 0, 0])
cam = camera_guard().translate([0, 42, 2 - WALL - 0.3])
rear = rear_guard(); b = rear.bounding_box(); rear = rear.translate([-(b[0] + b[3]) / 2, -65 - 5 - b[1] + 0.3 - 0.3, 4 - WALL - 0.3])
legs = Manifold()
for sx in (-1, 1):
    for sy in (-1, 1):
        legs += landing_leg().translate([0, 0, -4]).rotate([90, 0, 0]).translate([sx * (CX + RG - 6), sy * CY, Z0 - 20])
items = [(rings, (0.62, 0.64, 0.68)), (body, (0.5, 0.52, 0.56)), (BL, (0.95, 0.42, 0.12)), (BR, (0.95, 0.42, 0.12)), (cam, (0.95, 0.42, 0.12)), (rear, (0.95, 0.42, 0.12)), (legs, (0.95, 0.42, 0.12))]
L = np.array([0.4, -0.5, 0.8]) / np.linalg.norm([0.4, -0.5, 0.8]); fig = plt.figure(figsize=(14, 7))
for k, (view, title) in enumerate((((90, -90), 'Top view (front = up)'), ((28, -55), '3D view'))):
    ax = fig.add_subplot(1, 2, k + 1, projection='3d'); TT, CC = [], []
    for mm, col in items:
        me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tq = V[np.asarray(me.tri_verts)]
        n = np.cross(Tq[:, 1] - Tq[:, 0], Tq[:, 2] - Tq[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        TT.append(Tq); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1))
    ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
    ax.set_xlim(-95, 95); ax.set_ylim(-95, 95); ax.set_zlim(-80, 110); ax.set_box_aspect((1, 1, 1), zoom=1.35); ax.view_init(*view); ax.axis('off'); ax.set_title(title)
plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview_fit.png'), dpi=90)
print('bumper^rings', round((BL ^ rings).volume(), 2), 'cam^body', round((cam ^ body).volume(), 2), 'rear^body', round((rear ^ body).volume(), 2))
