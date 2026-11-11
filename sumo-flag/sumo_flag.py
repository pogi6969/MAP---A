#!/usr/bin/env python3
"""Mini sumo with decoy flags. Body 99 x 99 mm, 500 g class.
Two side flags stand up inside the 99 x 99 footprint at the start. An SG90 servo turns the latch bar,
the flags flip out and down to the sides, and the opponent's sensors see them instead of the body.
Sensor openings unchanged from sumo-bot: 3 x Ø8.5 opponent windows in the front (z 22, y -30/0/30),
2 x 8 x 8 mm line-sensor holes in the floor (x 18..26, |y| 36..44).
Axes: x forward, y left, z up, floor = 0. mm.  Run: python3 sumo_flag.py"""
import os, glob, re, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(48)
HERE = os.path.dirname(os.path.abspath(__file__))
S, XF = 49.5, 30.0                        # half footprint, base front face (blade in front)
ZB, FT, H, LT = 3.0, 3.0, 36.0, 2.5       # floor underside, floor, wall top, lid
ZL = H + LT                               # lid top
WD, WW, AX = 34.0, 10.0, -8.0             # wheel Ø, width, axle x (weight over the wheels)
AZ = WD / 2
MW, MH, ML, MY0, OW = 12.0, 10.0, 24.0, 5.0, 3.0   # N20 2000 rpm body, holder
MY1 = MY0 + ML + 0.5
WY0, WY1 = MY1 + OW + 0.5, MY1 + OW + 0.5 + WW + 2  # wheel well |y| (inside the side armour)
BLADE_A = 30.0
POSTS = [(-44.0, 40.0), (16.0, 17.0)]
XS = -40.0                                # SG90 shaft (x, y=0)
ZT = ZL + 6.0                             # servo tab seat
ZH = ZT + 10.6                            # horn / latch bar underside
KR = 2.6                                  # hinge knuckle radius
YA, ZA = S - KR, ZL + 6.0                 # hinge axis
FL, FP = 55.0, 1.6                        # flag length, plate thickness
FX0, FX1 = -45.6, 22.0
LSEG = [(-49.5, -46.0), (-29.6, -21.6), (-4.8, 3.2), (14.0, 22.0)]   # lid knuckles
FSEG = [(-45.6, -30.0), (-21.2, -5.2), (3.6, 13.6)]                  # flag knuckles
PIN_R = 43.5


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
    m = box(-S, XF, -S, S, ZB, ZB + FT)                                             # floor
    m += both(box(-S, XF, S - 2, S, ZB, H))                                         # side armour (wheels inside)
    m += box(-S, -S + 2, -S, S, ZB, H)                                              # rear wall
    m += box(XF - 3, XF, -S, S, ZB, H)                                              # front bulkhead
    h = box(AX - MW / 2 - 3, AX + MW / 2 + 3, MY0, MY1 + OW, ZB, AZ + MH / 2 + 3)
    h -= box(AX - MW / 2 - 0.2, AX + MW / 2 + 0.2, MY0 - 1, MY1, AZ - MH / 2 - 0.2, AZ + MH / 2 + 0.2)  # N20 tunnel
    h -= cyly(AX, AZ, MY1 - 1, MY1 + OW + 1, 4.4)                                   # gearbox boss / shaft
    for dx in (-4.5, 4.5):
        h -= cyly(AX + dx, AZ, MY1 - 1, MY1 + OW + 1, 1.8)                          # M1.6, 9 mm apart
    m += both(h)
    for px, py in POSTS:
        m += both(cyl(px, py, ZB, H, 7) - cyl(px, py, ZB + FT, H + 1, 2.6))         # lid posts, M3
    m += both(box(XF - 8, XF - 3, 26, 34, ZB, ZB + FT + 9))                         # blade screw bosses
    m -= both(box(AX - WD / 2 - 1, AX + WD / 2 + 1, WY0, WY1, -1, H + 1))          # wheel wells
    m -= both(cylx(30, ZB + FT + 5, XF - 9, XF + 1, 2.6))                           # blade screws
    for y in (-30, 0, 30):
        m -= cylx(y, 22, XF - 4, XF + 1, 8.5)                                       # opponent sensors (unchanged)
    m -= both(box(18, 26, 36, 44, ZB - 1, ZB + FT + 1))                             # line sensors (unchanged)
    m -= box(-40, -30, -12, 12, ZB - 1, ZB + FT + 1)                                # wiring hole
    return m


def lid():
    m = box(-S, XF, -S, S, H, ZL)
    m -= box(XS - 6.2, XS + 6.2, -6.2, 16.8, H - 1, ZL + 1)                         # servo opening
    for y0, y1, hy in ((-11.6, -6.3, -8.45), (16.9, 22.0, 19.15)):                  # servo risers
        m += box(XS - 6, XS + 6, y0, y1, ZL - 0.01, ZT) - cyl(XS, hy, ZL - 3, ZT + 1, 1.8)
    for px, py in POSTS:
        for s in (-1, 1):
            m -= cyl(px, s * py, H - 1, ZL + 1, 3.4)
            m -= Manifold.cylinder(1.6, 1.7, 3.3).translate([px, s * py, ZL - 1.59])  # countersink
    m -= cyl(-38, -30, H - 1, ZL + 1, 6.5)                                          # power switch
    k = Manifold()
    for x0, x1 in LSEG:
        k += box(x0, x1, YA - KR, YA + KR, ZL - 0.01, ZA) + cylx(YA, ZA, x0, x1, 2 * KR)
    return m + both(k - cylx(YA, ZA, -S - 1, XF + 1, 1.85))                         # 1.75 mm filament pin, snug


def blade():
    t = np.tan(np.radians(BLADE_A))
    ztop = (S - XF) * t
    m = xz([(S, 0.0), (XF, ztop), (XF, ztop - 3 / np.cos(np.radians(BLADE_A)))], -S, S)
    m += box(XF, XF + 3, -S, S, ZB + 1, ZB + FT + 9)
    return m - both(cylx(30, ZB + FT + 5, XF - 1, XF + 4, 3.3))


def flag_local():                         # x = hinge, y = along the flag, z = plate normal (print: flat)
    m = box(FX0, FX1, 0, FL, -KR, -KR + FP)
    for x0, x1 in LSEG:
        m -= box(x0 - 0.4, x1 + 0.4, -1, 7.5, -KR - 1, KR + 1)                      # clear the lid knuckles
    for x0, x1 in FSEG:
        m += cylx(0, 0, x0, x1, 2 * KR)
    m += box(XS - 5, XS + 5, 3.1, 10.1, -KR + FP - 0.01, 6.9) - box(XS - 6, XS + 6, 6.1, 11, 1.7, 5.1)  # latch tooth
    return m - cylx(0, 0, FX0 - 1, FX1 + 1, 2.15)                                   # free on the pin


def bar(theta=0.0):                       # latch bar on the SG90 horn; theta = servo turn
    m = box(XS - 3, XS + 3, -PIN_R - 2, PIN_R + 2, ZH, ZH + 3) + box(XS - 5, XS + 5, -18, 18, ZH, ZH + 3)
    m -= box(XS - 3.6, XS + 3.6, -17.5, 17.5, ZH - 1, ZH + 1.6)                     # stock double horn sits in here
    m -= cyl(XS, 0, ZH - 1, ZH + 4, 2.4)
    m += both(cyl(XS, PIN_R, ZH - 4, ZH + 0.1, 3.0))                                # pins into the flag teeth
    return m.translate([-XS, 0, 0]).rotate([0, 0, theta]).translate([XS, 0, 0])


def servo():                              # SG90 dummy (checks + preview)
    return (box(XS - 5.9, XS + 5.9, -5.9, 16.6, ZT - 15.9, ZT + 6.6) + box(XS - 5.9, XS + 5.9, -10.85, 21.35, ZT, ZT + 2.5)
            + cyl(XS, 0, ZT + 6.6, ZH, 5))


BASE, LID, BLADE, FLAG, SERVO = base(), lid(), blade(), flag_local(), servo()
BODY = BASE + LID + BLADE


def flags(phi):                           # phi = 90 stowed (up), < 0 deployed (down to the sides)
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
    start = BODY + flags(90) + bar() + SERVO
    b = start.bounding_box()
    print('start size', round(b[3] - b[0], 1), 'x', round(b[4] - b[1], 1), 'x', round(b[5], 1))
    print('overlaps base/lid/blade', v(BASE ^ LID), v(BASE ^ BLADE), '| servo', v(SERVO ^ (BASE + LID)),
          '| flags up', v(flags(90) ^ BODY), '| bar', v(bar() ^ (flags(90) + LID + SERVO)))
    stop = None
    for phi in range(90, -61, -5):
        if v(flags(phi) ^ BODY) > 0.01:
            stop = phi + 5; break
    for phi in np.arange(stop, stop - 5.01, -0.5):
        if v(flags(phi) ^ BODY) > 0.01:
            break
        stop = phi
    d = flags(stop).bounding_box()
    print('flags rest at', stop, 'deg  width', round(d[4] - d[1], 1), 'tip z', round(d[2], 1))
    print('parts', [len(p.decompose()) for p in (BASE, LID, BLADE, FLAG, bar())])

    stl(BASE, 'base.stl'); stl(floor0(LID), 'lid.stl'); stl(floor0(BLADE.rotate([0, -90, 0])), 'blade.stl')
    fr, fl, br = floor0(FLAG), floor0(FLAG.mirror([0, 1, 0])), floor0(bar().rotate([180, 0, 0]).rotate([0, 0, 90]))
    dy = fr.bounding_box()[4] + 6
    stl(fr + fl.translate([0, dy, 0]) + br.translate([0, 2 * dy, 0]), 'flags_bar.stl')

    info = {}
    for g in glob.glob(os.path.join(HERE, '*.gcode')):
        os.remove(g)
    for nm in ('base', 'lid', 'blade', 'flags_bar'):
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg.ini'), '--fill-density', '40%',
                        '--perimeters', '3', '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
        g = glob.glob(os.path.join(HERE, nm + '_PETG_*.gcode'))[0]
        tail = open(g).read()[-300000:]
        info[nm] = (float(re.search(r'filament used \[g\] = ([\d.]+)', tail).group(1)), re.search(r'_PETG_(.+)\.gcode', g).group(1))
        print(os.path.basename(g), info[nm][0], 'g')

    # ---- weight + balance ----
    vb, vl, vbl, vf, vr = BASE.volume(), LID.volume(), BLADE.volume(), FLAG.volume(), bar().volume()
    gfb = info['flags_bar'][0] / (2 * vf + vr)
    items = [(info['base'][0], centroid(BASE)), (info['lid'][0], centroid(LID)), (info['blade'][0], centroid(BLADE)),
             (gfb * 2 * vf, centroid(flags(90))), (gfb * vr, centroid(bar()))]
    parts = {'2 x N20 2000 rpm': (20, (AX, 0, AZ)), '2 x wheel Ø34': (16, (AX, 0, AZ)), 'SG90 servo': (9, (XS, 5, ZT - 4)),
             '2S LiPo ~450 mAh': (30, (-37, 0, 11)), 'controller + driver': (20, (-37, 0, 22)),
             '3 opponent + 2 line sensors': (20, (22, 0, 18)), 'screws, wires, switch': (15, (-10, 0, 20))}
    printed = sum(m for m, _ in items)
    ballast = 500 - printed - sum(m for m, _ in parts.values())
    bay = (BASE.volume() * 0 + (9 * 2 * (WY0 - 0.5) + 17 * 2 * (S - 2)) * 11 - 2 * 8 * 8 * 11) / 1000   # cm3, bay x 1..27, 11 mm deep
    allm = items + list(parts.values()) + [(ballast, (15.0, 0, ZB + FT + 5.5))]
    M = sum(m for m, _ in allm)
    cg = sum(m * np.asarray(c, float) for m, c in allm) / M
    blade_share = (cg[0] - AX) / (S - AX)
    print(f'printed {printed:.0f} g, ballast {ballast:.0f} g, bay {bay:.1f} cm3, cg {cg.round(1)}, on wheels {100 * (1 - blade_share):.0f} %')

    # ---- preview ----
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    L = np.array([0.4, -0.5, 0.75]) / np.linalg.norm([0.4, -0.5, 0.75])
    wheels = both(cyly(AX, AZ, WY0 + 0.5, WY0 + 0.5 + WW, WD))
    motors = both(box(AX - MW / 2, AX + MW / 2, MY0, MY1, AZ - MH / 2, AZ + MH / 2))
    common = [(BASE, (0.85, 0.35, 0.2), 1), (BLADE, (0.6, 0.6, 0.65), 1), (LID, (0.25, 0.25, 0.3), 1),
              (SERVO, (0.2, 0.4, 0.9), 1), (wheels, (0.1, 0.1, 0.1), 1)]
    fig = plt.figure(figsize=(14, 7))
    for k, (extra, title) in enumerate((([(flags(90), (0.95, 0.85, 0.1), 1), (bar(), (0.9, 0.9, 0.9), 1)], 'At the start: flags up, inside 99 x 99 mm'),
                                        ([(flags(stop), (0.95, 0.85, 0.1), 1), (bar(30), (0.9, 0.9, 0.9), 1)], f'After the start: flags down, {d[4] - d[1]:.0f} mm wide'))):
        ax = fig.add_subplot(1, 2, k + 1, projection='3d')
        for mm, col, al in common + extra:
            me = mm.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; T = V[np.asarray(me.tri_verts)]
            n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
            ax.add_collection3d(Poly3DCollection(T, facecolors=np.clip(np.outer(0.4 + 0.6 * np.abs(n @ L), col), 0, 1), edgecolors='none'))
        ax.set_xlim(-110, 110); ax.set_ylim(-110, 110); ax.set_zlim(-60, 160); ax.set_box_aspect((1, 1, 1)); ax.view_init(24, -55)
        ax.axis('off'); ax.set_title(title)
    plt.tight_layout(); plt.savefig(os.path.join(HERE, 'preview.png'), dpi=110)

    rows = '\n'.join(f'| {k} | {m} g |' for k, (m, _) in parts.items())
    open(os.path.join(HERE, 'DESIGN.md'), 'w').write(f"""# Flag mini sumo — 99 × 99 mm body, 500 g

![preview](preview.png)

| print (CR-6 SE, PETG, 3 walls, 40 % infill, no supports) | g | time |
|---|---|---|
| `base.stl` — floor down | {info['base'][0]:.0f} | {info['base'][1]} |
| `lid.stl` — flat, hinge knuckles up | {info['lid'][0]:.0f} | {info['lid'][1]} |
| `blade.stl` — flange down | {info['blade'][0]:.0f} | {info['blade'][1]} |
| `flags_bar.stl` — 2 flags flat + latch bar | {info['flags_bar'][0]:.0f} | {info['flags_bar'][1]} |

## Flags
* At the start both flags stand up on the lid edges, inside the 99 × 99 mm footprint (robot {b[5]:.0f} mm tall).
* SG90 servo at the rear turns the latch bar ~30° → its pins leave the flag teeth → the flags fall outward,
  rest at {abs(stop):.0f}° below horizontal on the lid edge: {d[4] - d[1]:.0f} mm wide, tips {d[2]:.0f} mm off the floor,
  covering the height the opponent's sensors look at.
* Hinges: 1.75 mm filament as the pin (push it in from the back corner; snug in the lid, free in the flags).
* Re-arm: lift the flags, servo back to 0°. Release in code right when the start delay ends.
* Servo horn: the stock SG90 double horn sits in the groove under the bar; horn screw + a drop of glue.

## Body
* Sensor openings exactly as before: 3 × Ø8.5 front windows (z 22, y −30/0/30), 2 × 8 × 8 mm floor holes.
* N20 holders unchanged (12.4 × 10.4 × 24.5 mm tunnel, Ø4.4 boss, 2 × M1.6 at 9 mm), axle moved to x = {AX:.0f}
  so the weight sits on the wheels; wheels Ø{WD:.0f} × {WW:.0f} now fully inside the side armour.
* Blade: 30° sharp wedge, 2 × M3. Lid: 4 × M3 countersunk, Ø6.5 switch hole.

## Weight to 500 g
| item | g |
|---|---|
| printed parts | {printed:.0f} |
{rows}
| **ballast to add** | **≈ {ballast:.0f}** |

Ballast goes flat on the floor in front of the motors (bay ≈ {bay:.0f} cm³ at 11 mm high → ≈ {bay * 11.3:.0f} g of lead;
steel ≈ {bay * 7.85:.0f} g, rest on top of the motor holders). Glue it down.
Balance: CG {cg[0] - AX:.0f} mm ahead of the axle, {cg[2]:.0f} mm high → ≈ {100 * (1 - blade_share):.0f} % of the weight on the wheels.
""")
