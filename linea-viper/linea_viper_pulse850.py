#!/usr/bin/env python3
"""LineaViper-X16 chassis for the PULSE 850 motor (flouw robotics, 850 rpm 1.6 kgcm) + a printed motor clamp.
Motor (from its drawing): shaft 3 mm D (2.5 flat) x 10, gearbox 12 x 13 x 11 long, can 15.5 round with flats 12 apart x 26.7.
Motor lies on its flat (12 high, 15.5 wide), shaft at the same place as the old N20 (x 25.9), gearbox front at y 32.5.
Chassis: the 4 small N20 bracket holes (2.7) are replaced by 4 bigger M3 holes (3.3), 28 mm apart, under the new clamp.
Clamp: saddle shaped to the can (flat top, round sides), 11 long, sits just behind the gearbox, 0.2 mm press on the can,
2 ears with M3 holes + nut traps. Print 2."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold
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


if __name__ == '__main__':
    yl = 2 * lv.YC - YH
    lv.HOLES = [h for h in lv.HOLES if abs(h[2] - 2.7) > 0.01] + [(MX - S / 2, YH, 3.3), (MX + S / 2, YH, 3.3), (MX - S / 2, yl, 3.3), (MX + S / 2, yl, 3.3)]
    A, s0 = lv.VERSIONS['X16']
    ch, cb = lv.chassis(A), lv.crossbar(A, s0)
    C = clamp()
    Cm = C.translate([MX, Y0, lv.T])                                 # clamp in place on top of the plate
    M = motor().translate([0, 0, lv.T])
    print('motor/clamp overlap', round((Cm ^ M).volume(), 2), 'mm3 (press fit on the can)', '| clamp parts', len(C.decompose()),
          '| clamp/chassis overlap', round((Cm ^ ch).volume(), 3), '| motor rear end y', YF + GB_L + CAN_L, '| left motor rear y', 2 * lv.YC - (YF + GB_L + CAN_L))
    b = C.bounding_box(); w = b[3] - b[0]
    clamps = Manifold.compose([C.translate([0, 0, 0]), C.translate([0, CL + 6, 0])])
    plate = ch + cb.rotate([0, 0, 90]).translate([lv.XE + 12, lv.YC, 0]) + clamps.translate([lv.XE + 34, lv.YC - CL - 3, 0])
    def stl(m, name):
        me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
        r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
        open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())
    for g in glob.glob(os.path.join(HERE, '*PULSE850*.gcode')): os.remove(g)
    stl(plate, 'LineaViper-X16_PULSE850.stl'); stl(ch, 'LineaViper-X16_PULSE850_chassis_only.stl'); stl(clamps, 'PULSE850_motor_clamp_x2.stl')
    print('plate bbox', np.round(plate.bounding_box(), 1))
    for nm, ex in (('LineaViper-X16_PULSE850', ['--fill-density', '15%', '--perimeters', '2']), ('PULSE850_motor_clamp_x2', ['--fill-density', '40%', '--perimeters', '3'])):
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '117.5,117.5',
                        '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    print(sorted(os.path.basename(g) for g in glob.glob(os.path.join(HERE, '*PULSE850*'))))
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
