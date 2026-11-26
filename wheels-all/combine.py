#!/usr/bin/env python3
"""Hub + mold of each size on ONE plate (format of the user's tire_mold_and_hub_27x33_combined.stl):
combined/hub_and_mold_<size>.stl  - both parts side by side, hub NOT inside the mold
combined/hub_and_mold_<size>.3mf  - same plate with per-part settings (hub 100% solid 0.32 mm, mold 15% gyroid 0.24 mm)
combined/hub_and_mold_<size>_PETG_<time>.gcode - sliced from the 3mf for the CR-6 SE"""
import os, re, glob, zipfile, subprocess
import numpy as np
from manifold3d import Manifold
from wheels_all import SIZES, TUBE, RIM, hub, mold, stl, HERE

GAP = 6.0                                        # mm between mold and hub
CX, CY = 117.5, 117.5                            # bed centre (CR-6 SE 235 x 235)
SET = {'mold': {'layer_height': '0.24', 'fill_density': '15%', 'fill_pattern': 'gyroid', 'perimeters': '3',
                'bottom_solid_layers': '4', 'top_solid_layers': '4'},
       'hub': {'layer_height': '0.32', 'fill_density': '100%', 'fill_pattern': 'rectilinear', 'perimeters': '3'}}


def mesh_xml(m, oid):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = np.asarray(me.tri_verts)
    v = ''.join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>\n' for a, b, c in V)
    t = ''.join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>\n' for a, b, c in T)
    return f'<object id="{oid}" type="model"><mesh><vertices>\n{v}</vertices><triangles>\n{t}</triangles></mesh></object>\n', len(T)


def write_3mf(path, parts):                     # parts: [(name, manifold centred at 0,0 with z from 0, x, y)]
    objs, items, cfg = '', '', ''
    for i, (name, m, x, y) in enumerate(parts, 1):
        xml, nt = mesh_xml(m, i); objs += xml
        items += f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {x:.3f} {y:.3f} 0"/>\n'
        cfg += f'<object id="{i}" instances_count="1">\n<metadata type="object" key="name" value="{name}"/>\n'
        cfg += ''.join(f'<metadata type="object" key="{k}" value="{v}"/>\n' for k, v in SET[name].items())
        cfg += f'<volume firstid="0" lastid="{nt - 1}">\n<metadata type="volume" key="name" value="{name}"/>\n</volume>\n</object>\n'
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n<resources>\n' + objs + '</resources>\n<build>\n' + items + '</build>\n</model>\n')
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', model)
        z.writestr('Metadata/Slic3r_PE_model.config', '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + cfg + '</config>\n')


if __name__ == '__main__':
    out = os.path.join(HERE, 'combined')
    for g in glob.glob(os.path.join(out, '*.gcode')): os.remove(g)
    for D, W in SIZES:
        tag = f'{D}x{W}'; H, M = hub(D, W), mold(D, W)
        rm = (D + 2 * TUBE + 2 * RIM + 6) / 2; rh = (D - 15.0) / 2
        xm, xh = -(rh + GAP / 2), rm + GAP / 2         # mold left, hub right, pair centred on the bed
        both = Manifold.compose([M.translate([xm, 0, 0]), H.translate([xh, 0, 0])])
        b = both.bounding_box()
        assert len(both.decompose()) == 2 and abs(b[2]) < 1e-6, tag
        stl(both.translate([-(b[0] + b[3]) / 2, 0, 0]), f'combined/hub_and_mold_{tag}.stl')
        sx = CX - (b[0] + b[3]) / 2
        write_3mf(os.path.join(out, f'hub_and_mold_{tag}.3mf'), [('mold', M, xm + sx, CY), ('hub', H, xh + sx, CY)])
        gc = os.path.join(out, f'hub_and_mold_{tag}.gcode')
        r = subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--dont-arrange',
                            '--output', gc, os.path.join(out, f'hub_and_mold_{tag}.3mf')], capture_output=True, text=True)
        if r.returncode:
            print(tag, 'SLICE ERROR', r.stderr[-600:])
        else:                                    # name it like the other G-codes: <name>_PETG_<time>.gcode
            t = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', open(gc).read()).group(1)
            hm = re.findall(r'(\d+)([dhm])', t); txt = ''.join(n + u for n, u in hm) or '1m'
            os.replace(gc, os.path.join(out, f'hub_and_mold_{tag}_PETG_{txt}.gcode'))
        print(tag, 'size', np.round(np.array(b[3:5]) - b[0:2], 1))
    print(sorted(os.path.basename(g) for g in glob.glob(os.path.join(out, '*.gcode'))))
