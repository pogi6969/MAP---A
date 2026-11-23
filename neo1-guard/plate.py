import os, sys, struct, numpy as np
from manifold3d import Manifold, Mesh
HERE = os.path.dirname(os.path.abspath(__file__))
def load(n):
    d = open(os.path.join(HERE, n), 'rb').read(); c = struct.unpack('<I', d[80:84])[0]
    T = np.frombuffer(d[84:84 + 50 * c], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])['v'].reshape(-1, 3)
    u, inv = np.unique(T.round(4), axis=0, return_inverse=True)
    m = Manifold(Mesh(vert_properties=u.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32)))
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])
BL, BR, CAM, REAR, LEG = (load(f'neo1_{n}.stl') for n in ('bumper_left', 'bumper_right', 'camera_guard', 'rear_guard', 'landing_leg'))
gap = 6; w = lambda m: m.bounding_box()[3]; h = lambda m: m.bounding_box()[4]
x = 0; items = [BL.translate([0, 0, 0])]; x = w(BL) + gap
items.append(BR.translate([x, 0, 0])); x += w(BR) + gap
items.append(CAM.translate([x, 0, 0])); items.append(REAR.translate([x, h(CAM) + gap, 0]))
lx = x + max(w(CAM), w(REAR)) + gap
for i in range(4): items.append(LEG.translate([lx + (i % 2) * (w(LEG) + gap), (i // 2) * (h(LEG) + gap), 0]))
m = Manifold.compose(items); b = m.bounding_box(); print('plate', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'parts', len(m.decompose()))
me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
open(os.path.join(HERE, 'dji_neo_full_set.stl'), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())
