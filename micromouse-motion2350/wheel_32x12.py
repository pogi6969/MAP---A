"""N20 hub + one-piece silicone mold for the micromouse wheel (32 x 8), same design as wheel-mold-v2."""
import os, sys, subprocess, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'wheel-mold-v2'))
import wheel_mold_v2 as w
HERE = os.path.dirname(os.path.abspath(__file__))
D, W, sd, flat, dd = 32.0, 12.0, 3.0, 2.5, False
M = w.floor0(w.mold(D, W, sd, flat, dd)); H = w.floor0(w.hub(D, W, sd, flat, dd).rotate([180, 0, 0]))
print('hub^mold', round((w.hub(D, W, sd, flat, dd).translate([0, 0, w.FLOOR + w.COL]) ^ w.mold(D, W, sd, flat, dd)).volume(), 2), w.dims(D, W, sd))
nm = 'N20_32x12_hub_and_mold'
w.HERE = HERE
w.stl(M + H.translate([M.bounding_box()[3] + 8, 0, 0]), nm + '.stl')
for g in glob.glob(os.path.join(HERE, nm + '*.gcode')):
    os.remove(g)
subprocess.run(['prusa-slicer', '--export-gcode', '--load', os.path.join(HERE, 'cr6se_petg_fast.ini'), '--fill-density', '15%', '--perimeters', '2',
                '--center', '122.5,117.5', '--output', HERE, os.path.join(HERE, nm + '.stl')], check=True, capture_output=True)
