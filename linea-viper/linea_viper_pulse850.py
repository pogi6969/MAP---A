#!/usr/bin/env python3
"""LineaViper-X16 chassis for the PULSE 850 motor (flouw robotics, 850 rpm 1.6 kgcm) + a printed motor clamp.
Motor (from its drawing): shaft 3 mm D (2.5 flat) x 10, gearbox 12 x 13 x 11 long, can 15.5 round with flats 12 apart x 26.7.
Motor lies on its flat (12 high, 15.5 wide), shaft at the same place as the old N20 (x 25.9), gearbox front at y 32.5.
Chassis: the 4 small N20 bracket holes (2.7) are replaced by 4 bigger M3 holes (3.3), 28 mm apart, under the new clamp.
Clamp: saddle shaped to the can (flat top, round sides), 11 long, sits just behind the gearbox, 0.2 mm press on the can,
2 ears with M3 holes + nut traps. Print 2.
Rear wing (F1 style, part of the chassis): raised high on 3 slim swan-neck struts with diamond lightening holes,
airfoil wing (flat bottom, rounded nose, thin trailing edge) with small swept endplates, "MR.D DRACOBOTS" raised
on top in 2 lines (reads from behind). Edges under 30 deg + 22 mm bridges: prints on the chassis without supports."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, FillRule
import linea_viper_multi as lv

HERE = lv.HERE
MX, YF = 25.89, 32.5                      # motor axis x, gearbox front face y (right motor)
GB_L, CAN_L, CAN_D, CAN_H, GB_W = 11.0, 26.7, 15.5, 12.0, 13.0
S, CL, Y0 = 28.0, 11.0, YF + GB_L + 0.5   # clamp hole spacing, clamp length, clamp start (just behind the gearbox)
YH = Y0 + CL / 2                          # clamp hole row (right motor); left motor mirrored about lv.YC
WALL, EAR_T, IN_W, IN_H = 2.4, 4.0, CAN_D + 0.3, CAN_H - 0.2


def clamp():                               # built with the motor axis along y, ears on z = 0
    zc = IN_H / 2
    band = lambda z0, z1, w: CrossSection.square([w, z1 - z0]).translate([-w / 2, z0])
    disc = lambda d: CrossSection.circle(d / 2, 96).translate([0, zc])
    outer = (disc(IN_W + 2 * WALL) ^ band(0, IN_H + WALL, 40)) + band(0, EAR_T, S + 8)
    for s in (1, -1):                      # gussets between ears and saddle
        outer += CrossSection.hull_points([(s * (IN_W / 2 + WALL - 0.5), 0), (s * (S / 2 - 2.6), EAR_T - 0.01),
                                           (s * (S / 2 - 2.6), 0), (s * (IN_W / 2 + WALL - 0.3), zc + 2)])
    prof = outer - (disc(IN_W) ^ band(-1, IN_H, 40))
    m = Manifold.extrude(prof, CL).rotate([90, 0, 0]).translate([0, CL, 0])   # profile up (+z), length along +y
    for s in (1, -1):
        m -= Manifold.cylinder(EAR_T + 2, 1.7, 1.7, 32).translate([s * S / 2, CL / 2, -1])
        m -= Manifold.cylinder(2.5 + 0.01, 3.3, 3.3, 6).translate([s * S / 2, CL / 2, EAR_T - 2.5])   # M3 nut trap (5.7 af)
    return m


def motor():                               # simple motor model for checks / preview (right motor, shaft towards -y)
    can = (Manifold.cylinder(CAN_L, CAN_D / 2, CAN_D / 2, 64) ^ Manifold.cube([CAN_D, CAN_H, CAN_L * 3], True)).rotate([90, 0, 0])
    can = can.translate([MX, YF + GB_L + CAN_L, CAN_H / 2])
    gb = Manifold.cube([GB_W, GB_L, 12.0]).translate([MX - GB_W / 2, YF, 0])
    sh = Manifold.cylinder(10.8, 1.5, 1.5, 24).rotate([90, 0, 0]).translate([MX, YF, CAN_H / 2])
    return can + gb + sh


ZB, XT, XL, TMAX = 40.0, -18.0, -2.0, 0.17      # wing underside height, trailing / leading edge x, thickness ratio
STRUT_Y, STRUT_T = (-25.0, 0.0, 25.0), 2.4     # 3 slim swan-neck struts (from the centre line), thickness
WING_HALF = 25.0 + STRUT_T / 2                 # wing half span


def xz(poly, y0, y1):                          # side profile (x, z) extruded across y0..y1
    return Manifold.extrude(CrossSection([poly]) if isinstance(poly, list) else poly, y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


def wing_profile(lift=0.0):                    # flat bottom (prints as a bridge), airfoil top, thin trailing edge
    c = XL - XT; pts = []
    for s in np.linspace(0, 1, 41):
        th = 2 * 5 * TMAX * c * (0.2969 * np.sqrt(s) - 0.1260 * s - 0.3516 * s ** 2 + 0.2843 * s ** 3 - 0.1015 * s ** 4)
        pts.append((XL - s * c, ZB + max(1.0 if s > 0.05 else 0.0, th) + lift))
    return [(XL, ZB)] + pts[1:] + [(XT, ZB)]


def spoiler():
    T, YC = lv.T, lv.YC
    tilt_front, tilt_rear = (XL - 6.8) / (ZB - T), (XT - 0.8) / (ZB - T)
    strut = CrossSection([[(0.8, T), (6.8, T), (XL, ZB + 0.6), (XT, ZB + 0.6)]])                          # narrow foot, fans out to the wing
    zc = T + 0.48 * (ZB - T); xf, xr = 6.8 + tilt_front * (zc - T), 0.8 + tilt_rear * (zc - T)
    hole = CrossSection([[((xf + xr) / 2, T + 8), (xf - 2.2, zc), ((xf + xr) / 2, ZB - 6), (xr + 2.6, zc)]])  # diamond lightening hole
    strut -= hole
    m = Manifold.compose([xz(strut, YC + y - STRUT_T / 2, YC + y + STRUT_T / 2) for y in STRUT_Y])
    m += xz(wing_profile(), YC - WING_HALF, YC + WING_HALF)
    fin = [(XT - 0.5, ZB + 0.5), (XL - 0.8, ZB + 0.5), (XL - 5.0, ZB + 7.0), (XT - 0.5, ZB + 7.0)]           # small swept endplates
    m += xz(fin, YC + WING_HALF - 1.6, YC + WING_HALF) + xz(fin, YC - WING_HALF, YC - WING_HALF + 1.6)
    from matplotlib.textpath import TextPath
    from matplotlib.font_manager import FontProperties
    fp = FontProperties(family='DejaVu Sans', weight='bold')
    def line(txt, cap):                        # text line, reading from behind the car (up = +x)
        tp = TextPath((0, 0), txt, size=10, prop=fp)
        cs = CrossSection([np.asarray(q) for q in tp.to_polygons() if len(q) > 2], FillRule.EvenOdd)
        b = cs.bounds(); k = min(cap / (b[3] - b[1]), (2 * WING_HALF - 6) / (b[2] - b[0]))
        return cs.translate([-(b[0] + b[2]) / 2, -(b[1] + b[3]) / 2]).scale([k, k]).rotate(-90)
    txt = line('MR.D', 4.6).translate([XL - 4.6, YC]) + line('DRACOBOTS', 4.0).translate([XL - 11.2, YC])
    raised = Manifold.extrude(txt, 10).translate([0, 0, ZB]) ^ xz(wing_profile(0.6), YC - WING_HALF, YC + WING_HALF)
    return m + raised


if __name__ == '__main__':
    yl = 2 * lv.YC - YH
    lv.HOLES = [h for h in lv.HOLES if abs(h[2] - 2.7) > 0.01] + [(MX - S / 2, YH, 3.3), (MX + S / 2, YH, 3.3), (MX - S / 2, yl, 3.3), (MX + S / 2, yl, 3.3)]
    A, s0 = lv.VERSIONS['X16']
    ch, cb = lv.chassis(A), lv.crossbar(A, s0)
    sp = spoiler(); ch = ch + sp
    C = clamp()
    Cm = C.translate([MX, Y0, lv.T])                                 # clamp in place on top of the plate
    M = motor().translate([0, 0, lv.T])
    print('motor/clamp overlap', round((Cm ^ M).volume(), 2), 'mm3 (press fit on the can)', '| clamp parts', len(C.decompose()),
          '| clamp/chassis overlap', round((Cm ^ ch).volume(), 3), '| wing vs motors', round(((M + M.mirror([0, 1, 0]).translate([0, 2 * lv.YC, 0])) ^ sp).volume(), 3),
          '| chassis parts', len(ch.decompose()), '| wing top z', round(sp.bounding_box()[5], 1), '| wing volume', round(sp.volume() / 1000, 2), 'cm3', '| rear x', round(ch.bounding_box()[0], 1), '| motor rear end y', YF + GB_L + CAN_L, '| left motor rear y', 2 * lv.YC - (YF + GB_L + CAN_L))
    def stl(m, name):
        me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
        r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
        open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())
    def floor0(m): bb = m.bounding_box(); return m.translate([-(bb[0] + bb[3]) / 2, -(bb[1] + bb[4]) / 2, -bb[2]])
    for g in glob.glob(os.path.join(HERE, '*PULSE850*.gcode')): os.remove(g)
    for f in ('LineaViper-X16_PULSE850.stl', 'LineaViper-X16_PULSE850_chassis_only.stl'):
        if os.path.exists(os.path.join(HERE, f)): os.remove(os.path.join(HERE, f))
    cbr = cb.rotate([0, 0, 90])                                          # crossbar lying along y
    clamps = Manifold.compose([C, C.translate([0, CL + 6, 0])])         # 2 pcs in one file
    items = {'LineaViper-X16_PULSE850_chassis': ch, 'LineaViper-X16_PULSE850_crossbar': cbr, 'PULSE850_motor_clamp_x2': clamps}
    for nm, m in items.items(): stl(floor0(m), nm + '.stl')
    # all items on one CR-6 SE bed (235 x 235): separate objects, laid out so they fit together
    cbb, clb = floor0(cbr), floor0(C)
    bc = ch.bounding_box(); ox, oy = 4 - bc[0], 117.5 - (bc[1] + bc[4]) / 2
    place = [('chassis', ch.translate([ox, oy, 0])),
             ('crossbar', cbb.translate([ox + bc[3] + 14, 117.5, 0])),
             ('clamp', clb.translate([ox + 130, 117.5 - 10, 0])),                # between the sensor arms
             ('clamp', clb.translate([ox + 130, 117.5 + 10, 0]))]
    allm = Manifold.compose([m for _, m in place]); ab = allm.bounding_box()
    assert ab[0] >= 0 and ab[1] >= 0 and ab[3] <= 235 and ab[4] <= 235, ab
    assert sum(1 for i in range(len(place)) for j in range(i) if (place[i][1] ^ place[j][1]).volume() > 0) == 0
    stl(allm, 'LineaViper-X16_PULSE850_all_items.stl')
    SET = {'chassis': {'fill_density': '15%', 'perimeters': '2'}, 'crossbar': {'fill_density': '15%', 'perimeters': '2'},
           'clamp': {'fill_density': '40%', 'perimeters': '3'}}
    import zipfile
    objs = items3 = cfg = ''
    for i, (name, m) in enumerate(place, 1):
        bb = m.bounding_box(); cx, cy = (bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2
        me = m.translate([-cx, -cy, 0]).to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = np.asarray(me.tri_verts)
        objs += f'<object id="{i}" type="model"><mesh><vertices>\n' + ''.join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>\n' for x, y, z in V)
        objs += '</vertices><triangles>\n' + ''.join(f'<triangle v1="{u}" v2="{v}" v3="{w}"/>\n' for u, v, w in T) + '</triangles></mesh></object>\n'
        items3 += f'<item objectid="{i}" transform="1 0 0 0 1 0 0 0 1 {cx:.3f} {cy:.3f} 0"/>\n'
        cfg += f'<object id="{i}" instances_count="1">\n<metadata type="object" key="name" value="{name}{i}"/>\n'
        cfg += ''.join(f'<metadata type="object" key="{k}" value="{v}"/>\n' for k, v in SET[name].items())
        cfg += f'<volume firstid="0" lastid="{len(T) - 1}">\n<metadata type="volume" key="name" value="{name}"/>\n</volume>\n</object>\n'
    with zipfile.ZipFile(os.path.join(HERE, 'LineaViper-X16_PULSE850_all_items.3mf'), 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
        z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr('3D/3dmodel.model', '<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n<resources>\n' + objs + '</resources>\n<build>\n' + items3 + '</build>\n</model>\n')
        z.writestr('Metadata/Slic3r_PE_model.config', '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + cfg + '</config>\n')
    import re
    def slice_one(src, args, base):
        gc = os.path.join(HERE, base + '.gcode')
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *args, '--output', gc, src], check=True, capture_output=True)
        t = re.search(r'estimated printing time \(normal mode\) = ([^\n]+)', open(gc).read()).group(1)
        os.replace(gc, os.path.join(HERE, base + '_PETG_' + ''.join(n + u for n, u in re.findall(r'(\d+)([dhm])', t)) + '.gcode'))
    for nm, ex in (('LineaViper-X16_PULSE850_chassis', ['--fill-density', '15%', '--perimeters', '2']), ('LineaViper-X16_PULSE850_crossbar', ['--fill-density', '15%', '--perimeters', '2']),
                   ('PULSE850_motor_clamp_x2', ['--fill-density', '40%', '--perimeters', '3'])):
        slice_one(os.path.join(HERE, nm + '.stl'), ex + ['--center', '117.5,117.5'], nm)
    slice_one(os.path.join(HERE, 'LineaViper-X16_PULSE850_all_items.3mf'), ['--dont-arrange'], 'LineaViper-X16_PULSE850_all_items')
    print('all items bbox', np.round(ab, 1))
    print(sorted(f for f in os.listdir(HERE) if 'PULSE850' in f))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6.2), gridspec_kw={'width_ratios': [1.25, 1]})
    for poly in ch.project().to_polygons(): q = np.asarray(poly); a1.fill(q[:, 0], q[:, 1], color='#d9dee5', ec='#333', lw=0.6)
    for mm, col in ((M.translate([0, 0, 0]), '#9aa3ad'), (M.mirror([0, 1, 0]).translate([0, 2 * lv.YC, 0]), '#9aa3ad'), (Cm, '#e8b04a'), (Cm.mirror([0, 1, 0]).translate([0, 2 * lv.YC, 0]), '#e8b04a')):
        for poly in mm.project().to_polygons(): q = np.asarray(poly); a1.fill(q[:, 0], q[:, 1], color=col, ec='#222', lw=0.5, alpha=0.9)
    for x, y, d in lv.HOLES[-4:]: a1.add_patch(plt.Circle((x, y), d / 2, color='#c0392b'))
    a1.set_aspect('equal'); a1.set_xlim(-5, 80); a1.set_ylim(20, 131); a1.set_title('Chassis front: PULSE 850 motors (grey), clamps (orange), new M3 holes (red)', fontsize=9)
    a1.set_xlabel('x mm (forward)'); a1.set_ylabel('y mm')
    sec = Cm.rotate([90, 0, 0]).translate([0, 0, 0])
    cut = lambda m: m.rotate([-90, 0, 0]).slice(-(Y0 + CL / 2))
    for mm, col in ((M, '#9aa3ad'), (Cm, '#e8b04a'), (ch, '#d9dee5')):
        for poly in cut(mm).to_polygons(): q = np.asarray(poly); a2.fill(q[:, 0], q[:, 1], color=col, ec='#222', lw=0.6)
    a2.annotate('', (MX - S / 2, lv.T + EAR_T + 3), (MX + S / 2, lv.T + EAR_T + 3), arrowprops=dict(arrowstyle='<->', lw=0.8))
    a2.text(MX, lv.T + EAR_T + 3.5, 'M3 holes 28 mm apart', ha='center', fontsize=8)
    a2.text(MX, lv.T + CAN_H + WALL + 2.0, 'clamp shaped to the motor can (15.5 x 12)', ha='center', fontsize=8)
    a2.set_aspect('equal'); a2.set_xlim(MX - 22, MX + 22); a2.set_ylim(-2, 26); a2.set_title('Cut through the clamp: motor can held flat on the plate', fontsize=9)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview_PULSE850.png'), dpi=110)
