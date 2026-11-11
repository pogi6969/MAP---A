#!/usr/bin/env python3
"""Predator Mini: your Predator revised into a 500 g mini sumo (N20 2000 rpm, 4WD).
Kept from Predator: the built-in 32 deg front wedge with the front IR window coming out through the
slope, and every sensor opening at its original size:
  front opponent window 35 x 15 (tilted up 5 deg), side windows 28.8 x 7.5 (L + R),
  rear window 28.8 x 7.5 with a 30 x 9 seat, floor line-sensor slots 31 x 9 (L + R),
  roof openings 13 x 13 (x2), 30 x 10 (x2), 5 x 10 (x2), dia 4.
Small N20s compensated: 4 motors (4WD), all weight on 4 wheels (34 x 10, castable with wheel-mold).
Two versions on one base: regular lid, or flag lid (SG90 + 2 decoy flags).
Axes: x forward, y left, z up, ground = 0. mm.   Run: python3 predator_mini.py"""
import os, glob, re, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))

S = 50.0                                   # half width (100)
A1, A2 = 0.0, -38.0                        # front / rear axle
AXLES = (A1, A2)
XR = A2 - 21.0                             # rear wall outer face
XW = A1 + 30.0                             # wedge top edge = body front
ZF0, FT = 0.6, 3.0                         # floor underside (wheels stick out 0.6), floor
ZF1 = ZF0 + FT
H, LT = 36.0, 2.5
ZL = H + LT
WH, WA = 26.0, 32.0                        # wedge top height, wedge angle (Predator)
TIP = XW + (WH - ZF0) / np.tan(np.radians(WA))
WD, WW, AZ = 34.0, 10.0, 17.0              # wheels
MW, MH, ML, MY0, OW = 12.0, 10.0, 24.0, 5.0, 3.0
MY1 = MY0 + ML + 0.5
WY0, WY1 = MY1 + OW + 0.5, MY1 + OW + 0.5 + WW + 2
# Predator sensor openings (sizes from your STL)
FW, FWZ0 = (35.0, 15.0, 5.0), 4.5
SW, SWX0, SWZ0 = (28.8, 7.5), XW - 11.2, ZF1 + 3.0
RW, RSEAT, RWZ0 = (28.8, 7.5), (30.0, 9.0, 0.8), 26.5
LS, LSX0, LSY0 = (31.0, 9.0), XW - 13.0, 22.0
ROOF = [(13, 13, XW - 14, 37.5), (30, 10, -15, 30), (5, 10, -20, 14)]       # (dx, dy, x, |y|) pairs L + R
ROOF_D4 = (5.0, 0.0)
POCKET = (XW - 3.5, XW + 18.0, 20.5, S - 2.1, ZF1, 13.0)                     # sensor pockets inside the wedge
POSTS = [(XR + 7.0, 20.0), (12.0, 27.0)]
# flag lid
KR = 2.6
YA, ZA = S - KR, ZL + 6.0
FL, FP = 55.0, 1.6
LSEG = [(XR, XR + 3.6), (-33.0, -25.0), (-4.0, 4.0), (13.0, 17.0)]
FSEG = [(XR + 4.0, -33.4), (-24.6, -4.4), (4.4, 12.6)]
FX0, FX1 = FSEG[0][0], LSEG[-1][1]          # flags stop before the side IR windows
XS = -45.0
ZH = ZL + 15.9 + 6.6 + 4.0
PIN_R = YA - 3.4                            # centred in the flag tooth groove
TV0 = ZH - 4.5 - ZA - 3.0


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


def base():
    m = box(XR, XW, -S, S, ZF0, ZF1)                                                # floor
    m += both(box(XR, XW, S - 2, S, ZF0, H))                                        # side armour (wheels inside)
    m += box(XR, XR + 2, -S, S, ZF0, H)                                             # rear wall
    m += box(XW - 3, XW, -S, S, ZF0, H)                                             # front bulkhead
    m += xz([(XW - 0.01, ZF0), (TIP, ZF0), (XW - 0.01, WH)], -S, S)                 # Predator wedge (solid, 32 deg)
    for ax in AXLES:                                                                # 4 x N20 holders
        h = box(ax - MW / 2 - 3, ax + MW / 2 + 3, MY0, MY1 + OW, ZF0, AZ + MH / 2 + 3)
        h -= box(ax - MW / 2 - 0.2, ax + MW / 2 + 0.2, MY0 - 1, MY1, AZ - MH / 2 - 0.2, AZ + MH / 2 + 0.2)
        h -= cyly(ax, AZ, MY1 - 1, MY1 + OW + 1, 4.4)
        for dx in (-4.5, 4.5):
            h -= cyly(ax + dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)
        m += both(h)
    for px, py in POSTS:
        m += both(cyl(px, py, ZF0, H, 7) - cyl(px, py, ZF1, H + 1, 2.6))
    for ax in AXLES:
        m -= both(box(ax - WD / 2 - 1, ax + WD / 2 + 1, WY0, WY1, -1, H + 1))      # wheel wells
    m -= both(box(*POCKET))                                                         # side + line sensor pockets
    # --- Predator sensor openings, original sizes ---
    w, hh, tilt = FW
    m -= box(0, TIP - XW + 12, -w / 2, w / 2, 0, hh).rotate([0, -tilt, 0]).translate([XW - 3.5, 0, FWZ0])   # front 35 x 15
    m -= both(box(SWX0, SWX0 + SW[0], S - 3, S + 1, SWZ0, SWZ0 + SW[1]))            # sides 28.8 x 7.5
    m -= box(XR - 1, XR + 3, -RW[0] / 2, RW[0] / 2, RWZ0, RWZ0 + RW[1])             # rear 28.8 x 7.5
    m -= box(XR + 2 - RSEAT[2], XR + 3, -RSEAT[0] / 2, RSEAT[0] / 2,
             RWZ0 + RW[1] / 2 - RSEAT[1] / 2, RWZ0 + RW[1] / 2 + RSEAT[1] / 2)      # rear seat 30 x 9
    m -= both(box(LSX0, LSX0 + LS[0], LSY0, LSY0 + LS[1], ZF0 - 1, ZF1 + 0.5))      # line slots 31 x 9
    m -= box(-36, -26, -8, 8, ZF0 - 1, ZF1 + 1)                                     # wiring hole
    return m


def lid(flag=False):
    m = box(XR, XW, -S, S, H, ZL)
    for px, py in POSTS:
        for s in (-1, 1):
            m -= cyl(px, s * py, H - 1, ZL + 1, 3.4)
            m -= Manifold.cylinder(1.6, 1.7, 3.3).translate([px, s * py, ZL - 1.59])
    for dx, dy, x, y in ROOF:                                                        # Predator roof openings
        m -= both(box(x - dx / 2, x + dx / 2, y - dy / 2, y + dy / 2, H - 1, ZL + 1))
    m -= cyl(ROOF_D4[0], ROOF_D4[1], H - 1, ZL + 1, 4.0)
    if not flag:
        return m
    k = Manifold()
    for x0, x1 in LSEG:
        k += box(x0, x1, YA - KR, YA + KR, ZL - 0.01, ZA) + cylx(YA, ZA, x0, x1, 2 * KR)
    m += both(k - cylx(YA, ZA, XR - 1, XW + 1, 1.85))
    bx0, bx1 = XS - 5.9, XS + 16.6
    cx = (bx0 + bx1) / 2
    cr = box(bx0 - 5.4, bx1 + 5.4, -7.5, 7.5, ZL - 0.01, ZL + 15.9) - box(bx0 - 0.2, bx1 + 0.2, -6.1, 6.1, ZL, ZL + 17)
    for hx in (cx - 13.8, cx + 13.8):
        cr -= cyl(hx, 0, ZL + 6, ZL + 17, 1.8)
    cr -= box(bx1 - 1, bx1 + 6, -2, 2, ZL, ZL + 4)
    return m + cr - cyl(cx, 0, H - 1, ZL + 1, 6)


def flag_local():
    m = box(FX0, FX1, 0, FL, -KR, -KR + FP)
    for x0, x1 in LSEG:
        m -= box(x0 - 0.4, x1 + 0.4, -1, 7.5, -KR - 1, KR + 1)
    for x0, x1 in FSEG:
        m += cylx(0, 0, x0, x1, 2 * KR)
    m += box(XS - 5, XS + 5, TV0, TV0 + 7, -KR + FP - 0.01, 6.9) - box(XS - 6, XS + 6, TV0 + 3, TV0 + 8, 1.7, 5.1)
    return m - cylx(0, 0, FX0 - 1, FX1 + 1, 2.15)


def bar(theta=0.0):
    m = box(XS - 3, XS + 3, -PIN_R - 2, PIN_R + 2, ZH, ZH + 3) + box(XS - 5, XS + 5, -18, 18, ZH, ZH + 3)
    m -= box(XS - 3.6, XS + 3.6, -17.5, 17.5, ZH - 1, ZH + 1.6)
    m -= cyl(XS, 0, ZH - 1, ZH + 4, 2.4)
    m += both(cyl(XS, PIN_R, ZH - 4, ZH + 0.1, 3.0))
    return m.translate([-XS, 0, 0]).rotate([0, 0, theta]).translate([XS, 0, 0])


def servo():
    return (box(XS - 5.9, XS + 16.6, -5.9, 5.9, ZL, ZL + 22.5) + box(XS - 10.75, XS + 21.45, -5.9, 5.9, ZL + 15.9, ZL + 18.4)
            + cyl(XS, 0, ZL + 22.5, ZH, 5))


BASE, LID, LIDF, FLAG, SERVO = base(), lid(), lid(True), flag_local(), servo()
WHEELS = sum((both(cyly(ax, AZ, WY0 + 0.5, WY0 + 0.5 + WW, WD)) for ax in AXLES), Manifold())
MOTORS = sum((both(box(ax - MW / 2, ax + MW / 2, MY0, MY1, AZ - MH / 2, AZ + MH / 2)) for ax in AXLES), Manifold())


def flags(phi):
    f = FLAG.rotate([phi, 0, 0]).translate([0, YA, ZA])
    return f + f.mirror([0, 1, 0])


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
    for nm, m in (('regular', BASE + LID), ('flag (start)', BASE + LIDF + flags(90) + bar() + SERVO)):
        b = m.bounding_box(); print(nm, 'size', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'x', round(b[5], 1))
    print('overlaps', v(BASE ^ LID), v(BASE ^ LIDF), v(SERVO ^ LIDF), v(flags(90) ^ (BASE + LIDF)), v(bar() ^ (flags(90) + LIDF + SERVO)),
          '| wheels/motors', v(WHEELS ^ BASE), v(MOTORS ^ BASE), '| wheel bottom z', round(WHEELS.bounding_box()[2], 2))
    print('bar release', [v(bar(t) ^ flags(90)) for t in (10, 20, 30)])
    body = BASE + LIDF
    stop = None
    for phi in range(90, -61, -5):
        if v(flags(phi) ^ body) > 0.01:
            stop = phi + 5; break
    for phi in np.arange(stop, stop - 5.01, -0.5):
        if v(flags(phi) ^ body) > 0.01:
            break
        stop = phi
    d = flags(stop).bounding_box()
    print('flags rest at', stop, 'width', round(d[4] - d[1], 1), 'tip z', round(d[2], 1), 'flag x', FX0, FX1, '< side window', SWX0)
    print('parts', [len(p.decompose()) for p in (BASE, LID, LIDF, FLAG, bar())])

    stl(BASE, 'base.stl'); stl(floor0(LID), 'lid_regular.stl'); stl(floor0(LIDF), 'lid_flag.stl')
    fr, fl, br = floor0(FLAG), floor0(FLAG.mirror([0, 1, 0])), floor0(bar().rotate([180, 0, 0]).rotate([0, 0, 90]))
    dy = fr.bounding_box()[4] + 6
    stl(fr + fl.translate([0, dy, 0]) + br.translate([0, 2 * dy, 0]), 'flags_bar.stl')
    info = {}
    for nm in ('base', 'lid_regular', 'lid_flag', 'flags_bar'):
        old = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))
        if not (os.environ.get('NOSLICE') and old):
            for g in old:
                os.remove(g)
            subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg.ini'), '--fill-density', '40%',
                            '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')],
                           check=True, capture_output=True)
        g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
        info[nm] = (float(re.search(r'filament used \[g\] = ([\d.]+)', open(g).read()[-300000:]).group(1)), re.search(r'_PETG_(.+)\.gcode', g).group(1))
        print(os.path.basename(g), info[nm][0], 'g')

    # ---- weight + balance ----
    xm = (A1 + A2) / 2
    xr0, xr1 = XR + 2, A2 - 9.5
    rear_cap = ((xr1 - xr0) * 2 * (WY0 - 0.5) * 19 - 2 * np.pi * 3.5 ** 2 * 19) / 1000 * 11.3
    xrb = (xr0 + xr1) / 2
    comps = {'4 × N20 2000 rpm': (40, (xm, 0, AZ)), '4 × wheel Ø34': (32, (xm, 0, AZ)), '2S LiPo 450 mAh': (30, (xm, 0, 30)),
             'controller + 2 drivers': (25, (xm, 0, 31)), '6 IR sensors': (35, (XW, 0, 10)), 'screws, wires, switch': (15, (xm, 0, 20))}
    vf, vr = FLAG.volume(), bar().volume()
    gfb = info['flags_bar'][0] / (2 * vf + vr)
    budget = {}
    for variant in ('regular', 'flag'):
        items = [(info['base'][0], centroid(BASE))]
        c = dict(comps)
        if variant == 'regular':
            items.append((info['lid_regular'][0], centroid(LID)))
        else:
            items += [(info['lid_flag'][0], centroid(LIDF)), (gfb * 2 * vf, centroid(flags(90))), (gfb * vr, centroid(bar()))]
            c['SG90 servo'] = (9, (XS + 5, 0, ZL + 12))
        printed = sum(m for m, _ in items)
        ballast = 500 - printed - sum(m for m, _ in c.values())
        others = items + list(c.values())
        sx = sum(m * p[0] for m, p in others) + ballast * xm
        mr = float(np.clip((sx - 500 * xm) / (xm - xrb), 0, min(ballast, rear_cap)))
        allm = others + [(ballast - mr, (xm, 0, ZF1 + 6)), (mr, (xrb, 0, ZF1 + 6))]
        M = sum(m for m, _ in allm); cg = sum(m * np.asarray(p, float) for m, p in allm) / M
        front = (cg[0] - A2) / (A1 - A2)
        budget[variant] = dict(printed=printed, comps=c, ballast=ballast, rear=mr, mid=ballast - mr, cg=cg, front=front)
        print(variant, f'printed {printed:.0f} g ballast {ballast:.0f} g (mid {ballast - mr:.0f} + rear {mr:.0f}) cg {cg.round(1)} front {100 * front:.0f} %')

    # ---------------- drawings ----------------
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle, Polygon as Poly, Patch
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    LGT = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    SENS, LINE, MOT, ROOFC = '#0b6fb8', '#c00000', '#8a6d00', '#6a1b9a'

    def render(ax, items, title, el=24, az=-55, lim=95):
        TT, CC = [], []
        for mm, col in items:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            TT.append(T); CC.append(np.clip(np.outer(0.4 + 0.6 * np.abs(n @ LGT), col), 0, 1))
        ax.add_collection3d(Poly3DCollection(np.concatenate(TT), facecolors=np.concatenate(CC), edgecolors='none'))
        ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-0.3 * lim, 1.2 * lim); ax.set_box_aspect((1, 1, 0.75), zoom=1.45)
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

    def sheet(variant):
        fl = variant == 'flag'
        bud = budget[variant]
        lidm = LIDF if fl else LID
        fig = plt.figure(figsize=(16, 17.5))
        fig.text(0.5, 0.982, ('PREDATOR MINI — FLAG' if fl else 'PREDATOR MINI') + '   |   4WD · 4 × N20 2000 rpm · 500 g · Predator sensor openings (original sizes)',
                 fontsize=15, weight='bold', ha='center')
        gs = fig.add_gridspec(3, 2, height_ratios=[1.3, 0.85, 0.8], width_ratios=[1.3, 1], hspace=0.1, wspace=0.04,
                              left=0.015, right=0.99, top=0.965, bottom=0.015)
        ymax = (d[4] + 18) if fl else (S + 42)
        X0, X1 = XR - 50, TIP + 48
        # ---------- TOP VIEW ----------
        ax = fig.add_subplot(gs[0, 0])
        ax.set_title('TOP VIEW — lid shown as outline' + (' (flags: solid = up, dashed = deployed)' if fl else ''), fontsize=11, weight='bold', loc='left')
        if fl:
            draw(ax, flags(stop), 'top', fc='#fff4bf', ec='#c9a400', ls='--', z=0)
        draw(ax, BASE, 'top', z=1)
        for q in proj(BASE.slice(ZF1 + 2).extrude(1), 'top'):
            ax.add_patch(Poly(q, closed=True, fc='#f3f4f6', ec='#666', lw=0.6, zorder=2))
        rect(ax, A2 + 9.5, -(WY0 - 0.5), A1 - A2 - 19, 2 * (WY0 - 0.5), 'none', '#555', lw=0.8, z=3, hatch='///')
        rect(ax, xr0, -(WY0 - 0.5), xr1 - xr0, 2 * (WY0 - 0.5), 'none', '#555', lw=0.8, z=3, hatch='\\\\\\')
        for ax_ in AXLES:
            for s in (1, -1):
                rect(ax, ax_ - WD / 2, (WY0 + 0.5) if s > 0 else -(WY0 + 0.5 + WW), WD, WW, '#3a3a3a', 'k', z=4)
                rect(ax, ax_ - MW / 2, MY0 if s > 0 else -MY1, MW, ML, '#f2c94c', MOT, z=4)
        for s in (1, -1):
            rect(ax, LSX0, LSY0 if s > 0 else -LSY0 - LS[1], LS[0], LS[1], '#ffc2c2', LINE, ls='--', z=5)
            rect(ax, SWX0, (S - 2.5) if s > 0 else -S - 0.5, SW[0], 3, '#7cc4ff', SENS, lw=1.4, z=6)
        rect(ax, XW - 3.5, -FW[0] / 2, TIP - XW - 6, FW[0], '#7cc4ff', SENS, lw=1.2, z=5, ls='--')
        rect(ax, XR - 0.5, -RW[0] / 2, 3, RW[0], '#7cc4ff', SENS, lw=1.4, z=6)
        for dx, dy, x, y in ROOF:
            for s in (1, -1):
                rect(ax, x - dx / 2, s * y - dy / 2, dx, dy, 'none', ROOFC, ls=':', lw=1.2, z=6)
        ax.add_patch(Circle(ROOF_D4, 2, fc='none', ec=ROOFC, ls=':', lw=1.2, zorder=6))
        draw(ax, lidm, 'top', fill=False, ec='#333', lw=0.8, ls='-.', z=6)
        if fl:
            draw(ax, flags(90), 'top', fc='#ffd84a', ec='#8a7300', z=7)
            draw(ax, SERVO, 'top', fc='#7aa7e6', ec='#1f4e99', z=7); draw(ax, bar(), 'top', fc='#eeeeee', ec='#444', z=8)
        yl = S + 26
        label(ax, (XW + 16, 6), f'FRONT IR window {FW[0]:.0f} × {FW[1]:.0f}\nthrough the wedge, tilt {FW[2]:.0f}°', (TIP + 18, 40), SENS)
        label(ax, (SWX0 + SW[0] / 2, S - 1), f'SIDE IR window\n{SW[0]} × {SW[1]}  (L + R)', (SWX0 + 26, yl), SENS)
        label(ax, (XR + 1, 10), f'REAR IR window\n{RW[0]} × {RW[1]}\n+ {RSEAT[0]:.0f} × {RSEAT[1]:.0f} seat', (XR - 26, 36), SENS)
        label(ax, (LSX0 + LS[0] / 2, -LSY0 - LS[1] / 2), f'LINE sensor slot\n{LS[0]:.0f} × {LS[1]:.0f}  (L + R)', (LSX0 + 30, -yl), LINE)
        label(ax, (A1, MY0 + ML / 2), 'N20 holder ×4\n12.4 × 10.4 × 24.5', (A1 - 6, yl), MOT)
        label(ax, (A2, -(WY0 + WW / 2)), f'wheel Ø{WD:.0f} × {WW:.0f}  ×4', (A2 - 10, -yl), '#222')
        label(ax, (xm, -22), f'ballast\n{bud["mid"]:.0f} g', (XR - 26, -10), '#444')
        label(ax, (xrb, -26), f'ballast\n{bud["rear"]:.0f} g', (XR - 26, -36), '#444')
        label(ax, (ROOF[1][2], -ROOF[1][3]), 'Predator roof\nopenings\n13×13, 30×10,\n5×10, Ø4', (XR - 26, -68), ROOFC)
        label(ax, (TIP - 8, -30), f'built-in wedge {WA:.0f}°\ntip {ZF0} mm off floor', (TIP + 18, -40), '#444')
        if fl:
            label(ax, (XS + 8, 3), 'SG90 servo\n+ latch bar', (XR - 26, 64), '#1f4e99')
            label(ax, (-20, d[4] - 4), f'flag deployed → {d[4] - d[1]:.0f} mm wide', (-20, d[4] + 9), '#8a7300')
        dim(ax, (XR, -ymax + 7), (TIP, -ymax + 7), f'{TIP - XR:.1f}')
        dim(ax, (XR - 44, -S), (XR - 44, S), f'{2 * S:.0f}')
        dim(ax, (A2, WY0 + WW + 9), (A1, WY0 + WW + 9), f'{A1 - A2:.0f}')
        ax.text(TIP + 36, 0, 'FRONT ▶', fontsize=10, weight='bold', va='center', ha='center', rotation=90)
        ax.set_xlim(X0, X1); ax.set_ylim(-ymax, ymax); ax.set_aspect('equal'); ax.axis('off')
        # ---------- 3D ----------
        if fl:
            sub = gs[0, 1].subgridspec(2, 1, hspace=0.0)
            render(fig.add_subplot(sub[0], projection='3d'), [(BASE, (0.85, 0.35, 0.2)), (LIDF, (0.25, 0.25, 0.3)), (WHEELS, (0.1, 0.1, 0.1)),
                   (SERVO, (0.2, 0.4, 0.9)), (bar(), (0.9, 0.9, 0.9)), (flags(90), (0.95, 0.85, 0.1))], 'At the start (inside 100 mm)')
            render(fig.add_subplot(sub[1], projection='3d'), [(BASE, (0.85, 0.35, 0.2)), (LIDF, (0.25, 0.25, 0.3)), (WHEELS, (0.1, 0.1, 0.1)),
                   (SERVO, (0.2, 0.4, 0.9)), (bar(30), (0.9, 0.9, 0.9)), (flags(stop), (0.95, 0.85, 0.1))], 'After the start (flags down)')
        else:
            render(fig.add_subplot(gs[0, 1], projection='3d'), [(BASE, (0.85, 0.35, 0.2)), (LID, (0.25, 0.25, 0.3)), (WHEELS, (0.1, 0.1, 0.1))],
                   '3D view', lim=80)
        # ---------- SIDE VIEW ----------
        ax = fig.add_subplot(gs[1, 0]); ax.set_title('SIDE VIEW — left', fontsize=11, weight='bold', loc='left')
        zt = (ZA + FL) if fl else ZL
        if fl:
            draw(ax, flags(90), 'side', fc='#ffd84a', ec='#8a7300', z=0)
        draw(ax, BASE + lidm, 'side', z=1)
        for ax_ in AXLES:
            ax.add_patch(Circle((ax_, AZ), WD / 2, fc='#3a3a3a', ec='k', lw=0.8, zorder=2, alpha=0.35))
        rect(ax, SWX0, SWZ0, SW[0], SW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        ax.add_patch(Poly(np.array([[XW - 3.5, FWZ0], [TIP - 4, FWZ0 + (TIP - XW) * np.tan(np.radians(FW[2]))],
                                    [TIP - 4, FWZ0 + FW[1] + (TIP - XW) * np.tan(np.radians(FW[2]))], [XW - 3.5, FWZ0 + FW[1]]]),
                          closed=True, fc='#7cc4ff', ec=SENS, ls='--', lw=1, zorder=5, alpha=0.6))
        rect(ax, XR, RWZ0, 2, RW[1], '#7cc4ff', SENS, ls='--', z=6)
        if fl:
            draw(ax, SERVO, 'side', fc='#7aa7e6', ec='#1f4e99', z=5); draw(ax, bar(), 'side', fc='#eeeeee', ec='#444', z=6)
        ax.plot([X0 + 20, X1 - 20], [0, 0], color='#666', lw=1.4)
        dim(ax, (XR - 14, 0), (XR - 14, zt), f'{zt:.1f}')
        if fl:
            dim(ax, (XR - 32, 0), (XR - 32, ZL), f'{ZL:.1f}')
        label(ax, (SWX0 + SW[0] / 2, SWZ0 + SW[1]), f'SIDE IR {SW[0]} × {SW[1]}', (SWX0 + 10, ZL + 14), SENS)
        label(ax, (XW + 22, FWZ0 + 9), f'FRONT IR {FW[0]:.0f} × {FW[1]:.0f}', (TIP + 14, 34), SENS)
        label(ax, (TIP - 1, 1), f'wedge {WA:.0f}°, tip {ZF0} mm', (TIP + 16, 12), '#444')
        ax.text(xm, -10, f'4WD · axles x = {A2:.0f} / {A1:.0f} · wheels Ø{WD:.0f} stick out {ZF0} mm below the floor', fontsize=9, ha='center')
        ax.set_xlim(X0, X1); ax.set_ylim(-18, zt + 14); ax.set_aspect('equal'); ax.axis('off')
        # ---------- FRONT VIEW ----------
        ax = fig.add_subplot(gs[1, 1]); ax.set_title('FRONT VIEW', fontsize=11, weight='bold', loc='left')
        if fl:
            draw(ax, flags(stop), 'front', fc='#fff4bf', ec='#c9a400', ls='--', z=0); draw(ax, flags(90), 'front', fc='#ffd84a', ec='#8a7300', z=4)
            draw(ax, SERVO + bar(), 'front', fc='#7aa7e6', ec='#1f4e99', z=4)
        draw(ax, BASE + lidm, 'front', z=1)
        draw(ax, xz([(XW, ZF0), (TIP, ZF0), (XW, WH)], -S, S), 'front', fc='#c7ccd4', z=2)
        rect(ax, -FW[0] / 2, FWZ0 + 1.5, FW[0], FW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        ax.text(0, FWZ0 + 1.5 + FW[1] / 2, f'IR {FW[0]:.0f} × {FW[1]:.0f}', fontsize=9, ha='center', va='center', color='#063e66', zorder=8)
        ax.plot([-100, 100], [0, 0], color='#666', lw=1.4)
        if fl:
            dim(ax, (d[1], -10), (d[4], -10), f'flags down: {d[4] - d[1]:.0f}')
        dim(ax, (-S, -22 if fl else -10), (S, -22 if fl else -10), f'{2 * S:.0f}')
        ax.set_xlim(-100, 100); ax.set_ylim(-30, zt + 10); ax.set_aspect('equal'); ax.axis('off')
        # ---------- REAR VIEW ----------
        ax = fig.add_subplot(gs[2, 1]); ax.set_title('REAR VIEW', fontsize=11, weight='bold', loc='left')
        if fl:
            draw(ax, flags(90), 'rear', fc='#ffd84a', ec='#8a7300', z=4); draw(ax, SERVO + bar(), 'rear', fc='#7aa7e6', ec='#1f4e99', z=4)
        draw(ax, BASE + lidm, 'rear', z=1)
        rect(ax, -RW[0] / 2, RWZ0, RW[0], RW[1], '#7cc4ff', SENS, lw=1.4, z=6)
        rect(ax, -RSEAT[0] / 2, RWZ0 + RW[1] / 2 - RSEAT[1] / 2, RSEAT[0], RSEAT[1], 'none', SENS, ls=':', z=7)
        ax.text(0, RWZ0 - 6, f'IR {RW[0]} × {RW[1]}  (seat {RSEAT[0]:.0f} × {RSEAT[1]:.0f})', fontsize=9, ha='center', color='#063e66')
        ax.plot([-65, 65], [0, 0], color='#666', lw=1.4)
        ax.set_xlim(-100, 100); ax.set_ylim(-8, zt + 8); ax.set_aspect('equal'); ax.axis('off')
        # ---------- INFO ----------
        ax = fig.add_subplot(gs[2, 0]); ax.axis('off')
        prints = [('base.stl', info['base'])]
        prints += [('lid_flag.stl', info['lid_flag']), ('flags_bar.stl', info['flags_bar'])] if fl else [('lid_regular.stl', info['lid_regular'])]
        L1 = ['SENSOR OPENINGS (Predator, original size)',
              f'  front opponent   {FW[0]:.0f} × {FW[1]:.0f}, tilt {FW[2]:.0f}°',
              f'  side ×2          {SW[0]} × {SW[1]}',
              f'  rear             {RW[0]} × {RW[1]} + {RSEAT[0]:.0f}×{RSEAT[1]:.0f} seat',
              f'  line slots ×2    {LS[0]:.0f} × {LS[1]:.0f} (floor)',
              '  roof             13×13 ×2, 30×10 ×2,', '                   5×10 ×2, Ø4', '',
              'PRINT  CR-6 SE · PETG · 3 walls · 40 %'] + [f'  {n:<15s}{g:4.0f} g  {t}' for n, (g, t) in prints]
        L2 = ['WEIGHT → 500 g', f'  printed parts          {bud["printed"]:4.0f} g'] + \
             [f'  {k[:22]:<22s} {m:4.0f} g' for k, (m, _) in bud['comps'].items()] + \
             [f'  BALLAST (lead)         {bud["ballast"]:4.0f} g', f'    between axles {bud["mid"]:.0f} g, behind rear {bud["rear"]:.0f} g',
              f'  wheel load  front {100 * bud["front"]:.0f} % / rear {100 * (1 - bud["front"]):.0f} %', '',
              'Small N20s → 4WD, all weight on 4 wheels']
        if fl:
            L2 += [f'Flags: SG90 turns 30° → flags drop {abs(stop):.0f}°,', f'  {d[4] - d[1]:.0f} mm wide, clear of the side IR']
        ax.text(0.0, 0.98, '\n'.join(L1), family='DejaVu Sans Mono', fontsize=9.6, va='top', transform=ax.transAxes)
        ax.text(0.5, 0.98, '\n'.join(L2), family='DejaVu Sans Mono', fontsize=9.6, va='top', transform=ax.transAxes)
        leg = [Patch(fc='#7cc4ff', ec=SENS, label='IR opening (Predator size)'), Patch(fc='#ffc2c2', ec=LINE, ls='--', label='line sensor slot'),
               Patch(fc='none', ec=ROOFC, ls=':', label='Predator roof opening'), Patch(fc='#f2c94c', ec=MOT, label='N20 motor / holder'),
               Patch(fc='#3a3a3a', label='wheel'), Patch(fc='white', ec='#555', hatch='///', label='ballast')]
        if fl:
            leg += [Patch(fc='#ffd84a', ec='#8a7300', label='flag'), Patch(fc='#7aa7e6', ec='#1f4e99', label='SG90 servo')]
        ax.legend(handles=leg, loc='lower left', ncol=4, fontsize=8.5, frameon=False, bbox_to_anchor=(0, -0.02))
        fig.savefig(os.path.join(HERE, f'diagram_{variant}.png'), dpi=120)
        plt.close(fig)

    sheet('regular'); sheet('flag')
    rb, fb = budget['regular'], budget['flag']
    open(os.path.join(HERE, 'DESIGN.md'), 'w').write(f"""# Predator Mini — your Predator as a 500 g N20 mini sumo

![regular](diagram_regular.png)
![flag](diagram_flag.png)

* **Kept from Predator:** built-in {WA:.0f}° front wedge with the front IR window coming out through the slope, and all sensor openings
  at their original size: front {FW[0]:.0f} × {FW[1]:.0f} (tilt {FW[2]:.0f}°), side {SW[0]} × {SW[1]} (L + R), rear {RW[0]} × {RW[1]} + {RSEAT[0]:.0f} × {RSEAT[1]:.0f} seat,
  floor line slots {LS[0]:.0f} × {LS[1]:.0f} (L + R), roof 13 × 13 (×2), 30 × 10 (×2), 5 × 10 (×2), Ø4.
* **Small N20s compensated:** 4 × N20 2000 rpm (4WD; holders 12.4 × 10.4 × 24.5 mm, Ø4.4 boss, 2 × M1.6 at 9 mm),
  wheels Ø{WD:.0f} × {WW:.0f} (cast them with `wheel-mold`, 34 × 10) stick out {ZF0} mm below the floor, so all weight is on the wheels and the wedge tip skims at {ZF0} mm.
* Size {TIP - XR:.1f} × {2 * S:.0f} mm, {ZL:.1f} mm tall (flag version {ZA + FL:.1f} mm at the start). Base prints flat on the bed, no supports.
* Side and line sensors sit in pockets inside the wedge, reached from the inside.

| file | g | time |
|---|---|---|
""" + '\n'.join(f'| `{n}.stl` | {g:.0f} | {t} |' for n, (g, t) in info.items()) + f"""

| | regular | flag |
|---|---|---|
| printed | {rb['printed']:.0f} g | {fb['printed']:.0f} g |
| lead ballast: between axles / behind rear motors | {rb['mid']:.0f} / {rb['rear']:.0f} g | {fb['mid']:.0f} / {fb['rear']:.0f} g |
| front / rear wheel load | {100 * rb['front']:.0f} / {100 * (1 - rb['front']):.0f} % | {100 * fb['front']:.0f} / {100 * (1 - fb['front']):.0f} % |

Flag version: SG90 turns the latch bar 30° at the start → flags drop to {abs(stop):.0f}° below horizontal, {d[4] - d[1]:.0f} mm wide;
they end before the side IR windows so they don't block them. Hinge pin: 1.75 mm filament.
""")
