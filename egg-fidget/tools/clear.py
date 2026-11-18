import sys, numpy as np, struct
from manifold3d import Manifold, Mesh, CrossSection
d = open(sys.argv[1], 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
T = np.frombuffer(d[84:84 + 50 * n], dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')])['v'].reshape(-1, 3)
u, inv = np.unique(T.round(4), axis=0, return_inverse=True)
m = Manifold(Mesh(vert_properties=u.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32)))
parts = m.decompose(); b = np.array(m.bounding_box())
res = []
for z in np.linspace(b[2] + 2, b[5] - 2, 9):
    secs = [p.slice(z) for p in parts]
    gmin = 9
    for i, si in enumerate(secs):
        if si.area() < 1: continue
        others = CrossSection()
        for j, sj in enumerate(secs):
            if j != i: others += sj
        lo, hi = 0.0, 1.0
        if (si.offset(hi) ^ others).area() < 1e-4: continue
        for _ in range(12):
            mid = (lo + hi) / 2
            if (si.offset(mid) ^ others).area() > 1e-4: hi = mid
            else: lo = mid
        gmin = min(gmin, hi)
    res.append((round(z, 1), round(gmin, 3)))
print('min horizontal clearance (mm) per height:', res)
