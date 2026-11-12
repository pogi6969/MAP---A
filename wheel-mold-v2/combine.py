import os, glob, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wheel_mold_v2 import *
for g in glob.glob(os.path.join(HERE, '*.gcode')):
    os.remove(g)
for f in glob.glob(os.path.join(HERE, 'hub_*.stl')) + glob.glob(os.path.join(HERE, 'mold_*.stl')):
    os.remove(f)
for name, (D, W, sd, flat, dd) in MOTORS.items():
    M = floor0(mold(D, W, sd, flat, dd)); H = floor0(hub(D, W, sd, flat, dd).rotate([180, 0, 0]))
    nm = f'{name}_{D:.0f}x{W:.0f}_hub_and_mold'
    stl(M + H.translate([M.bounding_box()[3] + 8, 0, 0]), nm + '.stl')
    subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '20%', '--perimeters', '3',
                    '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
print('\n'.join(sorted(os.path.basename(g) for g in glob.glob(os.path.join(HERE, '*.gcode')))))
