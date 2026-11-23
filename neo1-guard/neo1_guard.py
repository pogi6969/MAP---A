#!/usr/bin/env python3
"""DJI Neo (1st gen) anti-collision guard set (own design, made to fit the original Neo):
  bumper_left / bumper_right : figure-8 bumpers around the two prop guards on each side, front J-hook over the
                               guard's front tab, waist locator between the guards, rounded rear end
  camera_guard               : sleeve around the front gimbal camera (open front, top window, bottom slots)
  rear_guard                 : C-clamp bumper over the rear end (top hole kept open)
  landing_leg                : tapered leg with a spoke slot (print 4)
Sizes from DJI's Neo spec (130 x 157 x 48.5 mm, 2016S props 50.8 mm), layout scaled from the Neo 2 set.
MEASURE your drone and change the numbers below, then run: python3 neo1_guard.py
x = right, y = forward, z = up (mm)."""
import os, glob, subprocess
import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments
set_circular_segments(128)
HERE = os.path.dirname(os.path.abspath(__file__))

# ---- DRONE (measure these) ----
RG = 31.0          # prop guard ring outer radius (outer diameter 62)
CX, CY = 47.5, 33.5  # guard centre offsets: left/right, front/rear  (width 2*(CX+RG) = 157, length 2*(CY+RG) = 129)
BODY_W_CAM = 31.0  # body width at the camera
BODY_H_CAM = 32.0  # body height at the camera
BODY_W_REAR = 30.0 # body width at the rear end
BODY_H_REAR = 30.0 # body height at the rear end
SPOKE = 2.0        # guard spoke / rim thickness the legs clip onto
# ---- PARTS ----
CLR = 0.35         # gap to the guard ring
T = 3.0            # bumper band thickness
HB = 10.0          # bumper band height
HOOK_LEN = 12.0    # hook reaches this far past the front of the ring
HOOK_OPEN = 12.5   # inside width of the hook (front tab of the guard goes in here)
WALL = 2.1         # camera / rear guard wall


def circ(x, y, r): return CrossSection.circle(r).translate([x, y])
def rect(x0, x1, y0, y1): return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])
def box(x0, x1, y0, y1, z0, z1): return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def arc(cx, cy, r0, r1, a0, a1, n=96):
    """annular sector, math angles in degrees"""
    a = np.radians(np.linspace(a0, a1, n))
    pts = [(cx + r1 * np.cos(t), cy + r1 * np.sin(t)) for t in a] + [(cx + r0 * np.cos(t), cy + r0 * np.sin(t)) for t in a[::-1]]
    return CrossSection([pts])


def bumper_left():
    ri, ro, rm = RG + CLR, RG + CLR + T, RG + CLR + T / 2
    cf, cr = (-CX, CY), (-CX, -CY)
    c = arc(*cf, ri, ro, 101, 270) + arc(*cr, ri, ro, 90, 308)                 # front + rear guard arcs
    c += CrossSection([[(-CX - 12, -4.5), (-CX - 12, 4.5), (-CX - 1.5, 0.7), (-CX - 1.5, -0.7)]])   # waist locator
    px, py = cf[0] + rm * np.cos(np.radians(101)), cf[1] + rm * np.sin(np.radians(101))
    ytop = CY + RG + HOOK_LEN
    c += rect(px - T / 2, px + T / 2, py - 2, ytop)                              # hook: forward leg
    c += rect(px - T / 2, px + T / 2 + HOOK_OPEN + T, ytop - T, ytop)            #        top bar
    c += rect(px + T / 2 + HOOK_OPEN, px + T / 2 + HOOK_OPEN + T, ytop - 9, ytop)  #      back leg
    a = np.radians(308)
    c += circ(cr[0] + rm * np.cos(a), cr[1] + rm * np.sin(a), T * 0.75)          # rounded rear end
    c -= circ(*cf, ri) + circ(*cr, ri)                                           # keep clear of both rings
    return Manifold.extrude(c, HB)


def camera_guard():
    """sleeve: x across, z up, y = length; printed standing on its front face"""
    wi, hi, L = BODY_W_CAM + 0.6, BODY_H_CAM + 0.6, 26.0
    s = box(-wi / 2 - WALL, wi / 2 + WALL, 0, L, 0, hi + 2 * WALL) - box(-wi / 2, wi / 2, -1, L + 1, WALL, WALL + hi)
    s -= box(-wi / 2 + 4, wi / 2 - 4, 6, L - 4, hi + WALL - 1, hi + 2 * WALL + 1)                # top window
    for i in range(5):                                                                         # bottom slots (sensors stay open)
        x = -wi / 2 + 6 + i * (wi - 12) / 4
        s -= box(x - 1.3, x + 1.3, 7, L - 5, -1, WALL + 1)
    return s


def rear_guard():
    """C-clamp profile (y back..front, z up) extruded across the width"""
    hi, L_top, L_bot, B = BODY_H_REAR + 0.6, 28.4, 22.0, 5.0     # B = rear bumper block thickness
    W = BODY_W_REAR + 1.0
    c = rect(0, B, 0, hi + 2 * WALL) + rect(B, B + L_top, hi + WALL, hi + 2 * WALL) + rect(B, B + L_bot, 0, WALL)
    m = Manifold.extrude(c, W).transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])   # -> x across, y = depth, z up
    m -= Manifold.cylinder(WALL + 2, 6.0).translate([W / 2, B + L_top - 7.6, hi + WALL - 1])  # top hole kept open
    for i in range(4):
        x = 6 + i * (W - 12) / 3
        m -= box(x - 1.3, x + 1.3, B + 4, B + L_bot - 3, -1, WALL + 1)                           # bottom slots
    return m


def landing_leg():
    """profile (x across, z up) extruded 8 mm; printed lying on its side"""
    s = SPOKE / 2
    p = [(-3, 0), (3, 0), (7.5, 17), (7.5, 23), (5, 23), (5, 20), (s, 20), (s, 14), (-s, 14), (-s, 20), (-5, 20), (-5, 23), (-7.5, 23), (-7.5, 17)]
    return Manifold.extrude(CrossSection([p]), 8.0)


def floor0(m):
    b = m.bounding_box(); return m.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def stl(m, name):
    me = m.to_mesh(); V = np.asarray(me.vert_properties)[:, :3]; Tr = V[np.asarray(me.tri_verts)].astype('<f4')
    r = np.zeros(len(Tr), dtype=[('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]); r['v'] = Tr
    open(os.path.join(HERE, name), 'wb').write(b'\0' * 80 + np.uint32(len(Tr)).tobytes() + r.tobytes())


if __name__ == '__main__':
    BL = bumper_left(); BR = BL.mirror([1, 0, 0])
    CAM = camera_guard().rotate([-90, 0, 0])                    # stand on the front face
    REAR = rear_guard().rotate([0, 90, 0])                      # C profile flat on the bed
    LEG = landing_leg()
    parts = {'neo1_bumper_left': BL, 'neo1_bumper_right': BR, 'neo1_camera_guard': CAM, 'neo1_rear_guard': REAR, 'neo1_landing_leg': LEG}
    for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
    for nm, m in parts.items():
        m = floor0(m); b = m.bounding_box()
        print(nm, 'size', np.round(np.array(b[3:]) - b[:3], 1), 'parts', len(m.decompose()), 'vol', round(m.volume() / 1000, 1), 'cm3')
        stl(m, nm + '.stl')
    legs4 = Manifold.compose([floor0(LEG).translate([dx, 0, 0]) for dx in (-27, -9, 9, 27)])
    stl(legs4, 'neo1_landing_legs_x4.stl')
    for nm in list(parts) + ['neo1_landing_legs_x4']:
        if nm == 'neo1_landing_leg':
            continue
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '20%', '--perimeters', '3',
                        '--center', '117.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
    print(sorted(os.path.basename(g) for g in glob.glob(os.path.join(HERE, '*.gcode'))))
