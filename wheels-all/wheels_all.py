#!/usr/bin/env python3
"""Every wheel hub + silicone mold (v2 design: set-screw collar hub, one-piece drafted mold with push-out holes),
N20 and other motors, exported 1 part per file (hub_* and mold_*), each with its own G-code (CR-6 SE PETG fast)."""
import os, sys, glob, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'wheel-mold-v2'))
import wheel_mold_v2 as w
w.HERE = HERE
SETS = {'N20_34x12': (34.0, 12.0, 3.0, 2.5, False), 'N20_32x12': (32.0, 12.0, 3.0, 2.5, False), 'N20_32x8': (32.0, 8.0, 3.0, 2.5, False),
        'JGA25-370_42x20': (42.0, 20.0, 4.0, 3.5, False), 'JGB37-520_42x30': (42.0, 30.0, 6.0, 5.5, False), 'TT-yellow_42x20': (42.0, 20.0, 5.4, 3.7, True)}
for g in glob.glob(os.path.join(HERE, '*.gcode')): os.remove(g)
for tag, (D, W, sd, flat, dd) in SETS.items():
    w.stl(w.floor0(w.hub(D, W, sd, flat, dd).rotate([180, 0, 0])), f'hub_{tag}.stl')
    w.stl(w.floor0(w.mold(D, W, sd, flat, dd)), f'mold_{tag}.stl')
    for nm, ex in ((f'hub_{tag}', ['--fill-density', '30%', '--perimeters', '4']), (f'mold_{tag}', ['--fill-density', '15%', '--perimeters', '2'])):
        subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), *ex, '--center', '122.5,117.5',
                        '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
print('\n'.join(sorted(os.path.basename(g) for g in glob.glob(os.path.join(HERE, '*.gcode')))))
