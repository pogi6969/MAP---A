#!/usr/bin/env python3
"""Predator Mini 2WD: your Predator revised into a 10 x 10 cm, 500 g mini sumo with 2 x N20 2000 rpm.
Kept from Predator: built-in 32 deg wedge (front IR window comes out through the slope) and every sensor
opening at its original size: front 35 x 15 (tilt 5 deg), side 28.8 x 7.5 (L + R), rear 28.8 x 7.5 + 30 x 9
seat, floor line slots 31 x 9 (L + R), roof 13 x 13 (x2), 30 x 10 (x2), 5 x 10 (x2), dia 4.
Small N20s compensated: ~89 % of the 500 g on the two drive wheels (CG just ahead of the axle, wedge tip
skims), wider 34 x 12 silicone wheels, motors and lead low.
Flags: Matador-style module (like the JSumo Matador used in the All Japan tournament): SG90 drives two
meshing gears, both wings stand up inside the footprint at the start and swing open to both sides at once.
Bolts onto the lid with 2 x M3; the same lid works with or without it.
Axes: x forward, y left, z up, ground = 0. mm.   Run: python3 predator_mini_2wd.py"""
import os, glob, re, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))

S = 50.0
AX = 0.0                                   # the one axle
XR = AX - 21.0                             # rear wall outer face
XW = AX + 30.0                             # wedge top edge = body front
ZF0, FT = 0.6, 3.0                         # floor underside (wheels stick out 0.6), floor
ZF1 = ZF0 + FT
H, LT = 36.0, 2.5
ZL = H + LT
WH, WA = 26.0, 32.0
TIP = XW + (WH - ZF0) / np.tan(np.radians(WA))
WD, WW, AZ = 34.0, 12.0, 17.0
MW, MH, ML, MY0, OW = 12.0, 10.0, 24.0, 5.0, 3.0
MY1 = MY0 + ML + 0.5
WY0, WY1 = MY1 + OW + 0.5, MY1 + OW + 0.5 + WW + 2
FW, FWZ0 = (35.0, 15.0, 5.0), 4.5
SW, SWX0, SWZ0 = (28.8, 7.5), XW - 11.2, ZF1 + 3.0
RW, RSEAT, RWZ0 = (28.8, 7.5), (30.0, 9.0, 0.8), 26.5
LS, LSX0, LSY0 = (31.0, 9.0), XW - 13.0, 22.0
ROOF = [(13, 13, 20.0, 37.5), (30, 10, -4.0, 30.0), (5, 10, 15.0, 14.0)]       # (dx, dy, x, |y|), L + R
ROOF_D4 = (25.0, 0.0)
POCKET = (XW - 3.5, XW + 18.0, 20.5, S - 2.1, ZF1, 13.0)
POSTS = [(XR + 7.0, 20.0), (12.0, 27.0)]
MOUNT = [(-14.0, 14.0)]                    # Matador module bolts (L + R), M3
# ---- Matador module ----
GM, GZ, GBL = 1.5, 12, 0.2                 # gear module, teeth, backlash
GC = GM * GZ / 2 * 2 + 0.3                 # centre distance (+0.3 print clearance)
Y1, Y2 = -GC / 2, GC / 2                   # gear 1 (on the servo) / gear 2 (on an M3 pin)
ZS = 50.0                                  # arm pivot height (gears just clear the lid)
XT = AX + 3.0                              # SG90 top face (shaft points forward); flags at x ~ 9, clear of the side IR
XWF = XT - 6.8                             # wall front face = servo tab plane
GX0 = XT + 0.8                             # gear back face (gear presses onto the spline)
RA1, RA2 = 42.0, 92.0                      # flag sheet from / to (distance along the arm from the pivot)
HF, SP = 38.5, 1.2                         # flag sheet height (hangs down when open), thickness
OPEN = 90.0                                # arms horizontal, flags hang beside the robot


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl(x, y, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2).translate([x, y, z0])


def cyly(x, z, y0, y1, d):
    return Manifold.cylinder(y1 - y0, d / 2).rotate([-90, 0, 0]).translate([x, y0, z])


def cylx(y, z, x0, x1, d):
    return Manifold.cylinder(x1 - x0, d / 2).rotate([0, 90, 0]).translate([x0, y, z])


def both(m):
    return m + m.mirror([0, 1, 0])


def xz(pts, y0, y1):
    p = np.asarray(pts, float)
    if np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]) < 0:
        p = p[::-1]
    return Manifold.extrude(CrossSection([p.tolist()]), y1 - y0).rotate([90, 0, 0]).translate([0, y1, 0])


# ---------------- body ----------------
def base():
    m = box(XR, XW, -S, S, ZF0, ZF1)
    m += both(box(XR, XW, S - 2, S, ZF0, H))
    m += box(XR, XR + 2, -S, S, ZF0, H)
    m += box(XW - 3, XW, -S, S, ZF0, H)
    m += xz([(XW - 0.01, ZF0), (TIP, ZF0), (XW - 0.01, WH)], -S, S)                 # Predator wedge
    h = box(AX - MW / 2 - 3, AX + MW / 2 + 3, MY0, MY1 + OW, ZF0, AZ + MH / 2 + 3)  # 2 x N20 holders
    h -= box(AX - MW / 2 - 0.2, AX + MW / 2 + 0.2, MY0 - 1, MY1, AZ - MH / 2 - 0.2, AZ + MH / 2 + 0.2)
    h -= cyly(AX, AZ, MY1 - 1, MY1 + OW + 1, 4.4)
    for dx in (-4.5, 4.5):
        h -= cyly(AX + dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)
    m += both(h)
    for px, py in POSTS:
        m += both(cyl(px, py, ZF0, H, 7) - cyl(px, py, ZF1, H + 1, 2.6))
    m -= both(box(AX - WD / 2 - 1, AX + WD / 2 + 1, WY0, WY1, -1, H + 1))          # wheel wells
    m -= both(box(*POCKET))
    w, hh, tilt = FW
    m -= box(0, TIP - XW + 12, -w / 2, w / 2, 0, hh).rotate([0, -tilt, 0]).translate([XW - 3.5, 0, FWZ0])
    m -= both(box(SWX0, SWX0 + SW[0], S - 3, S + 1, SWZ0, SWZ0 + SW[1]))
    m -= box(XR - 1, XR + 3, -RW[0] / 2, RW[0] / 2, RWZ0, RWZ0 + RW[1])
    m -= box(XR + 2 - RSEAT[2], XR + 3, -RSEAT[0] / 2, RSEAT[0] / 2,
             RWZ0 + RW[1] / 2 - RSEAT[1] / 2, RWZ0 + RW[1] / 2 + RSEAT[1] / 2)
    m -= both(box(LSX0, LSX0 + LS[0], LSY0, LSY0 + LS[1], ZF0 - 1, ZF1 + 0.5))
    m -= box(-15, -11, -6, 6, ZF0 - 1, ZF1 + 1)                                      # wiring hole
    return m


def lid():
    m = box(XR, XW, -S, S, H, ZL)
    for px, py in POSTS:
        for s in (-1, 1):
            m -= cyl(px, s * py, H - 1, ZL + 1, 3.4)
            m -= Manifold.cylinder(1.6, 1.7, 3.3).translate([px, s * py, ZL - 1.59])
    for dx, dy, x, y in ROOF:
        m -= both(box(x - dx / 2, x + dx / 2, y - dy / 2, y + dy / 2, H - 1, ZL + 1))
    m -= cyl(ROOF_D4[0], ROOF_D4[1], H - 1, ZL + 1, 4.0)
    for mx, my in MOUNT:
        m -= both(cyl(mx, my, H - 1, ZL + 1, 3.4))                                   # Matador bolts
    return m


# ---------------- Matador flag module ----------------
def gear_cs(m=GM, z=GZ, pa=20.0, bl=GBL, phase=0.0):
    a = np.radians(pa); r = m * z / 2; rb = r * np.cos(a); ra = r + m; rf = r - 1.25 * m
    t = np.linspace(0, np.sqrt((ra / rb) ** 2 - 1), 10)
    rho, phi = rb * np.sqrt(1 + t ** 2), t - np.arctan(t)
    half = (np.pi * m / 2 - bl) / (2 * r) + (np.tan(a) - a)
    pts = []
    for k in range(z):
        c = phase + 2 * np.pi * k / z
        pts.append((rf * np.cos(c - half), rf * np.sin(c - half)))
        pts += list(zip(rho * np.cos(c - half + phi), rho * np.sin(c - half + phi)))
        pts += list(zip((rho * np.cos(c + half - phi))[::-1], (rho * np.sin(c + half - phi))[::-1]))
        pts.append((rf * np.cos(c + half), rf * np.sin(c + half)))
    return CrossSection([pts])


def gear_hub(servo_side, phase):              # local: axis z, wing slot toward -x (-> world up)
    g = Manifold.extrude(gear_cs(phase=phase), 5.0) + cyl(0, 0, 4.99, 14, 17.6)
    g -= box(-9.8, -3.6, -0.9, 0.9, 5.5, 15)                                          # wing slot
    g -= cyly(-6.7, 9.8, -10, 10, 2.0)                                                # cross pin (M2 / filament)
    if servo_side:
        g -= cyl(0, 0, -1, 4.0, 4.7) + cyl(0, 0, -1, 15, 2.2) + cyl(0, 0, 5.5, 15, 4.8)   # SG90 spline + screw
    else:
        g -= cyl(0, 0, -1, 15, 3.3) + cyl(0, 0, 5.5, 15, 6.2)                          # M3 pin + head
    return g


def arm_local():                          # arm bar along local -x, flag sheet on the outboard side (local -y)
    a = box(-RA2, -9.6, -2.0, 2.0, 5.0, 10.0)                                         # arm bar 4 x 5
    a += box(-9.65, -3.8, -0.8, 0.8, 5.6, 14.0)                                       # root tab -> hub slot
    a += box(-RA2, -RA1, -2.0 - HF, -1.0, 5.0, 5.0 + SP)                              # flag sheet (faces front / back)
    return a - cyly(-6.7, 9.8, -10, 10, 2.0)


def place(local, y):
    return local.rotate([0, 90, 0]).translate([GX0, y, ZS])          # local z -> world +x, local -x -> world +z


def mesh_phase():
    a = place(Manifold.extrude(gear_cs(), 5.0), Y1)
    for ph in (0.0, np.pi / GZ):
        b = place(Manifold.extrude(gear_cs(phase=ph), 5.0), Y2)
        if (a ^ b).volume() < 0.01:
            return ph
    return np.pi / GZ


PH2 = mesh_phase()
HUB1, HUB2 = place(gear_hub(True, 0.0), Y1), place(gear_hub(False, PH2), Y2)
WING1, WING2 = place(arm_local(), Y1), place(arm_local().mirror([0, 1, 0]), Y2)


def turn(m, y, deg):
    return m.translate([0, -y, -ZS]).rotate([deg, 0, 0]).translate([0, y, ZS])


def wings(theta=0.0):                     # theta = servo turn; wing 1 -> -y, wing 2 -> +y
    return turn(HUB1 + WING1, Y1, theta) + turn(HUB2 + WING2, Y2, -theta)


def frame():                             # SG90 lies on its side, body toward -y, shaft forward at (Y1, ZS)
    zb = ZL + 3
    m = box(-20, GX0 - 0.3, -34, 18, ZL, zb)                                          # base plate on the lid
    m += box(XWF - 2.5, XWF, -32, 15, zb - 0.01, ZS + 9)                              # servo wall
    m -= box(XWF - 3, XWF + 1, Y1 - 16.8, Y1 + 6.1, ZS - 6.1, ZS + 6.1)               # SG90 body opening
    for hy in (Y1 - 19.15, Y1 + 8.45):
        m -= cylx(hy, ZS, XWF - 3, XWF + 1, 1.8)                                      # tab screws
    m += box(XWF - 0.01, GX0 - 0.3, Y2 - 3.5, Y2 + 3.5, ZL, ZS + 3.5)                 # gear-2 pin pillar
    m -= cylx(Y2, ZS, XWF - 3, GX0, 2.6)                                              # M3 pin
    for y0, y1 in ((-32, -30), (13, 15)):
        m += xz([(XWF - 2.49, zb - 0.01), (-19.5, zb - 0.01), (XWF - 2.49, ZS + 8)], y0, y1)   # gussets
    for mx, my in MOUNT:
        m -= both(cyl(mx, my, ZL - 1, zb + 1, 3.4))
    return m


def servo_dummy():                       # SG90 body + tabs (tab plane = wall front face)
    return (box(XT - 22.7, XT, Y1 - 16.6, Y1 + 5.9, ZS - 5.9, ZS + 5.9)
            + box(XWF, XWF + 2.5, Y1 - 21.45, Y1 + 10.75, ZS - 5.9, ZS + 5.9))


BASE, LID, FRAME, SERVO = base(), lid(), frame(), servo_dummy()
WHEELS = both(cyly(AX, AZ, WY0 + 0.5, WY0 + 0.5 + WW, WD))
MOTORS = both(box(AX - MW / 2, AX + MW / 2, MY0, MY1, AZ - MH / 2, AZ + MH / 2))


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)].astype('<f4')
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    r = np.zeros(len(T), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['n'], r['v'] = n, T
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(T)).tobytes() + r.tobytes())


def floor0(m):
    b = m.bounding_box(); return m.translate([-b[0], -b[1], -b[2]])


def centroid(m):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3].astype(float); T = V[np.asarray(me.tri_verts)]
    vol = np.einsum('ij,ij->i', T[:, 0], np.cross(T[:, 1], T[:, 2])) / 6
    return (vol[:, None] * T.sum(1) / 4).sum(0) / vol.sum()


if __name__ == '__main__':
    v = lambda m: round(m.volume(), 2)
    MOD0 = FRAME + wings(0) + SERVO
    for nm, m in (('regular', BASE + LID), ('flag (start)', BASE + LID + MOD0)):
        b = m.bounding_box(); print(nm, 'size', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'x', round(b[5], 1))
    print('body overlaps', v(BASE ^ LID), '| wheels/motors', v(WHEELS ^ BASE), v(MOTORS ^ BASE), '| wheel z', round(WHEELS.bounding_box()[2], 2))
    print('module: frame^lid', v(FRAME ^ LID), 'servo^frame', v(SERVO ^ FRAME), 'gear mesh', v(HUB1 ^ HUB2),
          'wing^wing', v(WING1 ^ WING2), 'hub^frame', v((HUB1 + HUB2) ^ FRAME), 'hub^servo', v((HUB1 + HUB2) ^ SERVO))
    body = BASE + LID + FRAME + SERVO
    sweep = {t: (v(wings(t) ^ body), v(turn(HUB1, Y1, t) ^ turn(HUB2, Y2, -t))) for t in range(0, int(OPEN) + 1, 15)}
    print('opening sweep (deg: wings^body, gear mesh)', sweep)
    o = wings(OPEN).bounding_box()
    print('open: width', round(o[4] - o[1], 1), 'lowest z', round(o[2], 1), '| parts', [len(p.decompose()) for p in (BASE, LID, FRAME, HUB1, HUB2, WING1)])

    stl(BASE, 'base.stl'); stl(floor0(LID), 'lid.stl')
    g1 = floor0(gear_hub(True, 0.0)); g2 = floor0(gear_hub(False, PH2))
    w1 = floor0(arm_local()); w2 = floor0(arm_local().mirror([0, 1, 0]))                     # arms + sheets print flat
    fr = floor0(FRAME)
    fb = fr.bounding_box()
    plate = fr + g1.translate([fb[3] + 6, 0, 0]) + g2.translate([fb[3] + 6, 24, 0])
    pb = plate.bounding_box()
    plate += w1.translate([0, pb[4] + 6, 0]) + w2.translate([0, pb[4] + 6 + w1.bounding_box()[4] + 4, 0])
    stl(plate, 'matador_flags.stl')
    info = {}
    for nm in ('base', 'lid', 'matador_flags'):
        old = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))
        if not (os.environ.get('NOSLICE') and old):
            for g in old:
                os.remove(g)
            ini, dens = (('cr6se_petg_fast.ini', ['--fill-density', '20%', '--fill-pattern', 'gyroid']) if nm in ('base', 'lid', 'matador_flags')   # fast: 0.32 mm
                         else ('cr6se_petg.ini', ['--fill-density', '40%']))
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, ini), *dens,
                            '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')],
                           check=True, capture_output=True)
        g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
        info[nm] = (float(re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-300000:]).group(1)), re.search(r'_PETG_(.+)\.gcode', g).group(1))
        print(os.path.basename(g), info[nm][0], 'g')

    # ---- weight + balance: CG ~8 mm ahead of the axle -> ~89 % on the drive wheels ----
    XCG = AX + 8.0
    front_pk = (AX + 9.5, XW - 3.5, 17.5, WY0 - 0.5, ZF1, 20.0)          # lead beside the centre sensor (L + R)
    rear_pk = (XR + 2, AX - 9.5, -(WY0 - 0.5), WY0 - 0.5, ZF1, 25.0)      # lead behind the motors
    vol = lambda p: (p[1] - p[0]) * (p[3] - p[2]) * (p[5] - p[4]) / 1000
    cap_f, cap_r = 2 * vol(front_pk) * 11.3, (vol(rear_pk) - 2 * np.pi * 3.5 ** 2 * 21.4 / 1000) * 11.3
    top_pk = (AX - MW / 2 - 3, AX + MW / 2 + 3, MY0, MY1 + OW, AZ + MH / 2 + 3, H - 0.5)   # on top of the motor holders (L + R)
    cap_m = 2 * vol(top_pk) * 11.3
    xf, xr_ = (front_pk[0] + front_pk[1]) / 2, (rear_pk[0] + rear_pk[1]) / 2
    comps = {'2 × N20 2000 rpm': (20, (AX, 0, AZ)), '2 × wheel Ø34 × 12': (22, (AX, 0, AZ)), '2S LiPo 450 mAh': (30, (XW - 15, 0, 26)),
             'controller + driver': (20, (AX - 12, 0, 30)), '6 IR sensors': (35, (XW, 0, 10)), 'screws, wires, switch': (15, (AX, 0, 20))}
    gm = info['matador_flags'][0]
    budget = {}
    for variant in ('regular', 'flag'):
        items = [(info['base'][0], centroid(BASE)), (info['lid'][0], centroid(LID))]
        c = dict(comps)
        if variant == 'flag':
            items.append((gm, centroid(FRAME + wings(0))))
            c['SG90 servo'] = (9, tuple(centroid(SERVO)))
        printed = sum(m for m, _ in items)
        ballast = 500 - printed - sum(m for m, _ in c.values())
        others = items + list(c.values())
        sx = sum(m * p[0] for m, p in others)
        mm = min(cap_m, max(0.0, ballast - cap_r - cap_f / 2))                 # over the axle: best for grip
        b2, T = ballast - mm, 500 * XCG - sx - mm * AX
        mf = float(np.clip((T - b2 * xr_) / (xf - xr_), max(0, b2 - cap_r), min(b2, cap_f)))
        mr = b2 - mf
        allm = others + [(mf, (xf, 0, 12)), (mm, (AX, 0, 30)), (mr, (xr_, 0, 14))]
        M = sum(m for m, _ in allm); cg = sum(m * np.asarray(p, float) for m, p in allm) / M
        wheel = 1 - (cg[0] - AX) / (TIP - AX)
        budget[variant] = dict(printed=printed, comps=c, ballast=ballast, front=mf, top=mm, rear=mr, cg=cg, wheel=wheel)
        print(variant, f'printed {printed:.0f} g ballast {ballast:.0f} g (front {mf:.0f} + on motors {mm:.0f} + rear {mr:.0f}, caps {cap_f:.0f}/{cap_m:.0f}/{cap_r:.0f}) cg {cg.round(1)} on wheels {100 * wheel:.0f} %')

    # ---------------- drawings ----------------
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon as Poly, Patch
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    LGT = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    SENS, LINE, MOT, ROOFC, WINGC = '#0b6fb8', '#c00000', '#8a6d00', '#6a1b9a', '#f2f2f2'

    def render(ax, items, title, el=22, az=-55, lim=95, zt=1.2):
        TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ LGT), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-0.3 * lim, zt * lim); ax.set_box_aspect((1, 1, (zt + 0.3) / 2), zoom=1.35)
        ax.view_init(el, az); ax.axis('off'); ax.set_title(title, fontsize=11, weight='bold')

    def proj(m, view):
        if view == 'top':
            mm, f = m, lambda q: q
        elif view == 'side':
            mm, f = m.rotate([90, 0, 0]), lambda q: np.c_[q[:, 0], -q[:, 1]]
        elif view == 'front':
            mm, f = m.rotate([0, -90, 0]), lambda q: np.c_[q[:, 1], -q[:, 0]]
        else:
            mm, f = m.rotate([0, -90, 0]), lambda q: np.c_[-q[:, 1], -q[:, 0]]
        return [f(np.asarray(q)) for q in mm.project().to_polygons()]

    def draw(ax, m, view, fc='#d9dde3', ec='k', lw=1.0, ls='-', fill=True, z=1):
        for q in proj(m, view):
            ax.add_patch(Poly(q, closed=True, fc=fc if fill else 'none', ec=ec, lw=lw, ls=ls, zorder=z))

    def dim(ax, a, b, txt, fs=9):
        a, b = np.asarray(a, float), np.asarray(b, float)
        ax.annotate('', a, b, arrowprops=dict(arrowstyle='<|-|>', lw=0.9, color='#222', mutation_scale=8))
        ax.text(*((a + b) / 2), txt, fontsize=fs, ha='center', va='center', bbox=dict(fc='white', ec='none', pad=0.8), zorder=9)

    def label(ax, xy, txt, xytext, col):
        ax.annotate(txt, xy, xytext, fontsize=8.5, color=col, ha='center', va='center', zorder=10,
                    arrowprops=dict(arrowstyle='-|>', lw=0.7, color=col, mutation_scale=7),
                    bbox=dict(fc='white', ec=col, lw=0.7, boxstyle='round,pad=0.3'))

    def rect(ax, x, y, w, h, fc, ec, ls='-', lw=1.1, z=5, hatch=None):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, ls=ls, lw=lw, zorder=z, hatch=hatch))

    BODYC, LIDC = (0.85, 0.35, 0.2), (0.25, 0.25, 0.3)

    def sheet(variant):
        fl = variant == 'flag'
        bud = budget[variant]
        fig = plt.figure(figsize=(16, 17.5))
        fig.text(0.5, 0.982, ('PREDATOR MINI 2WD + MATADOR FLAGS' if fl else 'PREDATOR MINI 2WD') +
                 '   |   2 × N20 2000 rpm · 500 g · Predator sensor openings (original sizes)', fontsize=15, weight='bold', ha='center')
        gs = fig.add_gridspec(3, 2, height_ratios=[1.25, 0.95 if fl else 0.8, 0.8], width_ratios=[1.3, 1], hspace=0.1, wspace=0.04,
                              left=0.015, right=0.99, top=0.965, bottom=0.015)
        ymax = S + 46
        X0, X1 = XR - 52, TIP + 50
        # ---------- TOP ----------
        ax = fig.add_subplot(gs[0, 0])
        ax.set_title('TOP VIEW — lid shown as outline' + (', flags closed' if fl else ''), fontsize=11, weight='bold', loc='left')
        draw(ax, BASE, 'top', z=1)
        for q in proj(BASE.slice(ZF1 + 2).extrude(1), 'top'):
            ax.add_patch(Poly(q, closed=True, fc='#f3f4f6', ec='#666', lw=0.6, zorder=2))
        for s in (1, -1):
            rect(ax, front_pk[0], s * front_pk[2] if s > 0 else -front_pk[3], front_pk[1] - front_pk[0], front_pk[3] - front_pk[2], 'none', '#555', lw=0.8, z=3, hatch='///')
            rect(ax, AX - WD / 2, (WY0 + 0.5) if s > 0 else -(WY0 + 0.5 + WW), WD, WW, '#3a3a3a', 'k', z=4)
            rect(ax, AX - MW / 2, MY0 if s > 0 else -MY1, MW, ML, '#f2c94c', MOT, z=4)
            rect(ax, LSX0, LSY0 if s > 0 else -LSY0 - LS[1], LS[0], LS[1], '#ffc2c2', LINE, ls='--', z=5)
            rect(ax, SWX0, (S - 2.5) if s > 0 else -S - 0.5, SW[0], 3, '#7cc4ff', SENS, lw=1.4, z=6)
        rect(ax, rear_pk[0], rear_pk[2], rear_pk[1] - rear_pk[0], rear_pk[3] - rear_pk[2], 'none', '#555', lw=0.8, z=3, hatch='\\\\\\')
        rect(ax, XW - 3.5, -FW[0] / 2, TIP - XW - 6, FW[0], '#7cc4ff', SENS, lw=1.2, z=5, ls='--')
        rect(ax, XR - 0.5, -RW[0] / 2, 3, RW[0], '#7cc4ff', SENS, lw=1.4, z=6)
        for dx, dy, x, y in ROOF:
            for s in (1, -1):
                rect(ax, x - dx / 2, s * y - dy / 2, dx, dy, 'none', ROOFC, ls=':', lw=1.2, z=6)
        ax.add_patch(Circle(ROOF_D4, 2, fc='none', ec=ROOFC, ls=':', lw=1.2, zorder=6))
        draw(ax, LID, 'top', fill=False, ec='#333', lw=0.8, ls='-.', z=6)
        if fl:
            draw(ax, FRAME + SERVO, 'top', fc='#7aa7e6', ec='#1f4e99', z=7); draw(ax, wings(0), 'top', fc=WINGC, ec='#444', z=8)
        yl = S + 26
        label(ax, (XW + 16, 6), f'FRONT IR window {FW[0]:.0f} × {FW[1]:.0f}\nthrough the wedge, tilt {FW[2]:.0f}°', (TIP + 18, 42), SENS)
        label(ax, (SWX0 + SW[0] / 2, S - 1), f'SIDE IR window {SW[0]} × {SW[1]}  (L + R)', (SWX0 + 20, yl), SENS)
        label(ax, (XR + 1, 10), f'REAR IR\n{RW[0]} × {RW[1]}\n+ {RSEAT[0]:.0f} × {RSEAT[1]:.0f} seat', (XR - 28, 36), SENS)
        label(ax, (LSX0 + LS[0] / 2, -LSY0 - LS[1] / 2), f'LINE sensor slot {LS[0]:.0f} × {LS[1]:.0f}  (L + R)', (LSX0 + 22, -yl), LINE)
        label(ax, (AX, MY0 + ML / 2), 'N20 holder ×2\n12.4 × 10.4 × 24.5', (AX - 14, yl + 8), MOT)
        label(ax, (AX, -(WY0 + WW / 2)), f'wheel Ø{WD:.0f} × {WW:.0f}  ×2', (AX - 16, -yl - 8), '#222')
        label(ax, (xf, -25), f'lead\n{bud["front"]:.0f} g', (XR - 28, -10), '#444')
        label(ax, (xr_, -12), f'lead\n{bud["rear"]:.0f} g', (XR - 28, -38), '#444')
        if bud['top'] > 0.5:
            label(ax, (AX + 6, 18), f'lead on motors\n{bud["top"]:.0f} g', (TIP + 18, 74), '#444')
        label(ax, (ROOF[1][2], -ROOF[1][3]), 'Predator roof\nopenings', (XR - 28, -66), ROOFC)
        label(ax, (TIP - 8, -30), f'built-in wedge {WA:.0f}°\ntip {ZF0} mm', (TIP + 18, -42), '#444')
        if fl:
            label(ax, (XT - 10, Y1), 'Matador module\nSG90 + 2 gears', (XR - 28, 66), '#1f4e99')
        dim(ax, (XR, -ymax + 7), (TIP, -ymax + 7), f'{TIP - XR:.1f}')
        dim(ax, (XR - 46, -S), (XR - 46, S), f'{2 * S:.0f}')
        ax.text(TIP + 38, 0, 'FRONT ▶', fontsize=10, weight='bold', va='center', ha='center', rotation=90)
        ax.set_xlim(X0, X1); ax.set_ylim(-ymax, ymax); ax.set_aspect('equal'); ax.axis('off')
        # ---------- 3D ----------
        if fl:
            sub = gs[0, 1].subgridspec(2, 1, hspace=0.0)
            render(fig.add_subplot(sub[0], projection='3d'), [(BASE, BODYC), (LID, LIDC), (WHEELS, (0.1, 0.1, 0.1)), (FRAME, (0.2, 0.4, 0.9)),
                   (SERVO, (0.15, 0.15, 0.6)), (wings(0), (0.95, 0.95, 0.95))], 'At the start: wings up (inside 100 mm)', zt=1.7)
            render(fig.add_subplot(sub[1], projection='3d'), [(BASE, BODYC), (LID, LIDC), (WHEELS, (0.1, 0.1, 0.1)), (FRAME, (0.2, 0.4, 0.9)),
                   (SERVO, (0.15, 0.15, 0.6)), (wings(OPEN), (0.95, 0.95, 0.95))], f'After the start: wings open {OPEN:.0f}°', zt=1.0)
        else:
            render(fig.add_subplot(gs[0, 1], projection='3d'), [(BASE, BODYC), (LID, LIDC), (WHEELS, (0.1, 0.1, 0.1))], '3D view', lim=70)
        # ---------- SIDE ----------
        ax = fig.add_subplot(gs[1, 0]); ax.set_title('SIDE VIEW — left', fontsize=11, weight='bold', loc='left')
        ztop = (ZS + RA2) if fl else ZL
        draw(ax, BASE + LID, 'side', z=1)
        ax.add_patch(Circle((AX, AZ), WD / 2, fc='#3a3a3a', ec='k', lw=0.8, zorder=2, alpha=0.35))
        rect(ax, SWX0, SWZ0, SW[0], SW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        ax.add_patch(Poly(np.array([[XW - 3.5, FWZ0], [TIP - 4, FWZ0 + (TIP - XW) * np.tan(np.radians(FW[2]))],
                                    [TIP - 4, FWZ0 + FW[1] + (TIP - XW) * np.tan(np.radians(FW[2]))], [XW - 3.5, FWZ0 + FW[1]]]),
                          closed=True, fc='#7cc4ff', ec=SENS, ls='--', lw=1, zorder=5, alpha=0.6))
        rect(ax, XR, RWZ0, 2, RW[1], '#7cc4ff', SENS, ls='--', z=6)
        if fl:
            draw(ax, FRAME + SERVO, 'side', fc='#7aa7e6', ec='#1f4e99', z=4); draw(ax, wings(0), 'side', fc=WINGC, ec='#444', z=5)
            label(ax, (GX0 + 8, ZS + 70), f'flag sheets {RA2 - RA1:.0f} × {HF} on {RA2:.0f} mm arms\n(upright at the start)', (TIP + 6, ZS + 60), '#444')
            dim(ax, (XR - 30, 0), (XR - 30, ZL), f'{ZL:.1f}')
        ax.plot([X0 + 20, X1 - 20], [0, 0], color='#666', lw=1.4)
        dim(ax, (XR - 14, 0), (XR - 14, ztop), f'{ztop:.1f}')
        label(ax, (SWX0 + SW[0] / 2, SWZ0 + SW[1]), f'SIDE IR {SW[0]} × {SW[1]}', (SWX0 - 2, ZL + 12), SENS)
        label(ax, (XW + 22, FWZ0 + 9), f'FRONT IR {FW[0]:.0f} × {FW[1]:.0f}', (TIP + 14, 34), SENS)
        label(ax, (TIP - 1, 1), f'wedge {WA:.0f}°, tip {ZF0} mm', (TIP + 18, 12), '#444')
        ax.text(AX + 18, -10, f'2WD · axle x = {AX:.0f} · wheels Ø{WD:.0f} stick out {ZF0} mm · {100 * bud["wheel"]:.0f} % of weight on the wheels',
                fontsize=9, ha='center')
        ax.set_xlim(X0, X1); ax.set_ylim(-18, ztop + 14); ax.set_aspect('equal'); ax.axis('off')
        # ---------- FRONT ----------
        ax = fig.add_subplot(gs[1, 1]); ax.set_title('FRONT VIEW' + (' — wings closed (solid) and open (dashed)' if fl else ''), fontsize=11, weight='bold', loc='left')
        if fl:
            draw(ax, wings(OPEN), 'front', fc='none', ec='#555', ls='--', fill=False, z=3)
            draw(ax, FRAME + SERVO, 'front', fc='#7aa7e6', ec='#1f4e99', z=4); draw(ax, wings(0), 'front', fc=WINGC, ec='#444', z=5)
            dim(ax, (o[1], -10), (o[4], -10), f'wings open: {o[4] - o[1]:.0f}')
        draw(ax, BASE + LID, 'front', z=1)
        draw(ax, xz([(XW, ZF0), (TIP, ZF0), (XW, WH)], -S, S), 'front', fc='#c7ccd4', z=2)
        rect(ax, -FW[0] / 2, FWZ0 + 1.5, FW[0], FW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        ax.text(0, FWZ0 + 1.5 + FW[1] / 2, f'IR {FW[0]:.0f} × {FW[1]:.0f}', fontsize=9, ha='center', va='center', color='#063e66', zorder=8)
        ax.plot([-100, 100], [0, 0], color='#666', lw=1.4)
        dim(ax, (-S, -22 if fl else -10), (S, -22 if fl else -10), f'{2 * S:.0f}')
        ax.set_xlim(-100, 100); ax.set_ylim(-30, ztop + 10); ax.set_aspect('equal'); ax.axis('off')
        # ---------- REAR ----------
        ax = fig.add_subplot(gs[2, 1]); ax.set_title('REAR VIEW', fontsize=11, weight='bold', loc='left')
        if fl:
            draw(ax, FRAME + SERVO, 'rear', fc='#7aa7e6', ec='#1f4e99', z=4); draw(ax, wings(0), 'rear', fc=WINGC, ec='#444', z=3)
        draw(ax, BASE + LID, 'rear', z=1)
        rect(ax, -RW[0] / 2, RWZ0, RW[0], RW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        rect(ax, -RSEAT[0] / 2, RWZ0 + RW[1] / 2 - RSEAT[1] / 2, RSEAT[0], RSEAT[1], 'none', SENS, ls=':', z=7)
        ax.text(0, RWZ0 - 6, f'IR {RW[0]} × {RW[1]}  (seat {RSEAT[0]:.0f} × {RSEAT[1]:.0f})', fontsize=9, ha='center', color='#063e66')
        ax.plot([-65, 65], [0, 0], color='#666', lw=1.4)
        ax.set_xlim(-100, 100); ax.set_ylim(-8, ztop + 8); ax.set_aspect('equal'); ax.axis('off')
        # ---------- INFO ----------
        ax = fig.add_subplot(gs[2, 0]); ax.axis('off')
        prints = [('base.stl', info['base']), ('lid.stl', info['lid'])] + ([('matador_flags.stl', info['matador_flags'])] if fl else [])
        L1 = ['SENSOR OPENINGS (Predator, original size)',
              f'  front opponent   {FW[0]:.0f} × {FW[1]:.0f}, tilt {FW[2]:.0f}°', f'  side ×2          {SW[0]} × {SW[1]}',
              f'  rear             {RW[0]} × {RW[1]} + {RSEAT[0]:.0f}×{RSEAT[1]:.0f} seat', f'  line slots ×2    {LS[0]:.0f} × {LS[1]:.0f} (floor)',
              '  roof             13×13 ×2, 30×10 ×2,', '                   5×10 ×2, Ø4', '',
              'PRINT  CR-6 SE · PETG · fast 0.32 mm, 20 %'] + [f'  {n:<18s}{g:4.0f} g  {t}' for n, (g, t) in prints]
        L2 = ['WEIGHT → 500 g', f'  printed parts          {bud["printed"]:4.0f} g'] + \
             [f'  {k[:22]:<22s} {m:4.0f} g' for k, (m, _) in bud['comps'].items()] + \
             [f'  LEAD (glue in)         {bud["ballast"]:4.0f} g', f'    front {bud["front"]:.0f} · on motors {bud["top"]:.0f} · rear {bud["rear"]:.0f} g',
              f'  {100 * bud["wheel"]:.0f} % on the drive wheels', '',
              '2 small N20s → weight on the wheels,', '  wider 34 × 12 silicone tyres']
        if fl:
            L2 += ['', f'Matador: SG90 turns {OPEN:.0f}° → both wings', f'  open together, {o[4] - o[1]:.0f} mm wide']
        ax.text(0.0, 0.98, '\n'.join(L1), family='DejaVu Sans Mono', fontsize=9.4, va='top', transform=ax.transAxes)
        ax.text(0.52, 0.98, '\n'.join(L2), family='DejaVu Sans Mono', fontsize=9.4, va='top', transform=ax.transAxes)
        leg = [Patch(fc='#7cc4ff', ec=SENS, label='IR opening (Predator size)'), Patch(fc='#ffc2c2', ec=LINE, ls='--', label='line sensor slot'),
               Patch(fc='none', ec=ROOFC, ls=':', label='Predator roof opening'), Patch(fc='#f2c94c', ec=MOT, label='N20 motor / holder'),
               Patch(fc='#3a3a3a', label='wheel'), Patch(fc='white', ec='#555', hatch='///', label='lead')]
        if fl:
            leg += [Patch(fc=WINGC, ec='#444', label='flag wing'), Patch(fc='#7aa7e6', ec='#1f4e99', label='Matador frame + SG90')]
        ax.legend(handles=leg, loc='lower left', ncol=4, fontsize=8.5, frameon=False, bbox_to_anchor=(0, -0.02))
        fig.savefig(os.path.join(HERE, f'diagram_{variant}.png'), dpi=120)
        plt.close(fig)

    sheet('regular'); sheet('flag')

    # Matador close-up
    fig = plt.figure(figsize=(15, 5.6))
    for k, (th, ttl) in enumerate(((0, 'closed (start)'), (60, 'opening'), (OPEN, f'open {OPEN:.0f}°'))):
        render(fig.add_subplot(1, 3, k + 1, projection='3d'), [(LID, LIDC), (FRAME, (0.2, 0.4, 0.9)), (SERVO, (0.15, 0.15, 0.6)),
               (wings(th), (0.95, 0.95, 0.95))], f'Matador module — {ttl}', el=12, az=-20, lim=75, zt=1.9)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'matador.png'), dpi=100); plt.close(fig)

    rb, fb_ = budget['regular'], budget['flag']
    open(os.path.join(HERE, 'DESIGN.md'), 'w').write(f"""# Predator Mini 2WD + Matador flags

![regular](diagram_regular.png)
![flag](diagram_flag.png)
![matador](matador.png)

* **Size {TIP - XR:.1f} × {2 * S:.0f} mm** (fits 10 × 10 cm), {ZL:.1f} mm tall. 2 × N20 2000 rpm.
* **Kept from Predator:** built-in {WA:.0f}° wedge with the front IR window through the slope, every sensor opening at its original size.
* **Small N20s compensated:** CG just ahead of the axle → {100 * rb['wheel']:.0f} % of the 500 g on the drive wheels; wedge tip skims at {ZF0} mm;
  wider Ø{WD:.0f} × {WW:.0f} silicone wheels (make them with `wheel-mold`, set the size to 34 × 12); lead low in the body.
* **Flags (Matador style):** SG90 lying behind a wall, two 12-tooth gears (module 1.5) make the wings turn in opposite directions.
  Flag sheets {RA2 - RA1:.0f} × {HF} mm on {RA2:.0f} mm arms: upright inside the footprint at the start ({ZS + RA2:.0f} mm tall); the servo turns
  {OPEN:.0f}°, the arms go out flat to the sides and the sheets hang beside the robot ({o[4] - o[1]:.0f} mm wide, bottom {o[2]:.0f} mm off the floor).
  Bolt the module to the lid with 2 × M3; same lid for both robots.

| file | g | time |
|---|---|---|
""" + '\n'.join(f'| `{n}.stl` | {g:.0f} | {t} |' for n, (g, t) in info.items()) + f"""

| | regular | with flags |
|---|---|---|
| printed | {rb['printed']:.0f} g | {fb_['printed']:.0f} g |
| lead: front / on motors / behind motors | {rb['front']:.0f} / {rb['top']:.0f} / {rb['rear']:.0f} g | {fb_['front']:.0f} / {fb_['top']:.0f} / {fb_['rear']:.0f} g |
| on the drive wheels | {100 * rb['wheel']:.0f} % | {100 * fb_['wheel']:.0f} % |

**Matador assembly:** press gear 1 onto the SG90 spline + horn screw; gear 2 on an M3 × 16 into the pillar; servo into the wall
(2 tab screws); slide each wing into its gear slot and pin it (M2 screw or 2 mm filament). Set the servo so both wings point up,
then in code: at the start signal turn the servo {OPEN:.0f}°. Check your event's flag rules (some allow max 2–4 flags, upright and
inside the robot's outline at the start).
""")
