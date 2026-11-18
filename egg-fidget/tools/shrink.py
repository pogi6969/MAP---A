import sys, numpy as np, struct, time
from manifold3d import Manifold, Mesh, JoinType, OpType
src, out, s, gap0, gap1 = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
d = open(src, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
T = np.frombuffer(d[84:84 + 50 * n], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])['v'].reshape(-1, 3)
u, inv = np.unique(T.round(4), axis=0, return_inverse=True)
m = Manifold(Mesh(vert_properties=u.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32)))
b = np.array(m.bounding_box()); c = (b[:3] + b[3:]) / 2
m = m.translate(list(-np.array([c[0], c[1], b[2]]))).scale([s, s, s])
H = m.bounding_box()[5]; LH = float(sys.argv[6]) if len(sys.argv) > 6 else 0.2; ins = (gap1 - gap0 * s) / 2          # inset per side to get the new gap
print('height', round(H, 2), 'inset per side', round(ins, 3)); t = time.time()
parts = []
for p in m.decompose():
    slabs = []
    for z in np.arange(0, H - 1e-6, LH):
        cs = p.slice(min(z + LH / 2, H - 0.01)).offset(-ins, JoinType.Round, 2.0, 16).simplify(0.02)
        if cs.area() > 0.01: slabs.append(Manifold.extrude(cs, LH + 0.002).translate([0, 0, z]))
    parts.append(Manifold.batch_boolean(slabs, OpType.Add))
res = Manifold.compose(parts); bb = np.array(res.bounding_box())
print('parts', len(res.decompose()), 'size', np.round(bb[3:] - bb[:3], 1), 'secs', round(time.time() - t))
me = res.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
rec = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); rec['v'] = Tr
open(out, 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + rec.tobytes())
