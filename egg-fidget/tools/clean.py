import sys, numpy as np, struct
from manifold3d import Manifold, Mesh
d = open(sys.argv[1], 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
T = np.frombuffer(d[84:84 + 50 * n], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])['v'].reshape(-1, 3)
u, inv = np.unique(T.round(4), axis=0, return_inverse=True)
m = Manifold(Mesh(vert_properties=u.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32)))
res = Manifold.compose([p for p in m.decompose() if p.volume() > 1]); bb = np.array(res.bounding_box())
print('parts', len(res.decompose()), 'size', np.round(bb[3:] - bb[:3], 1))
me = res.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
rec = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['v'] = Tr
open(sys.argv[2], 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + rec.tobytes())
