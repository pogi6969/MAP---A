"""Sensor cover for the LED strip ("LED Strip Assembly and Gap Plan" blueprint).

The strip has 18 positions per row in 2 rows. The outer position pair at each
end is a screw slot, not LEDs, so the cover has 16 x 2 = 32 LED bores and
2 screw slots.

Run:   python sensor_cover.py      (needs CadQuery: pip install cadquery)
Makes: sensor_cover.step and sensor_cover.stl next to this file.
Units: mm. Origin: centre of the bottom face (the face that sits on the PCB).
X runs along the strip, Y across it, Z up.
"""
from pathlib import Path

import cadquery as cq

# Blueprint
PCB_LENGTH = 150.0        # ~150 mm
PCB_HEIGHT = 18.0         # ~18 mm
LED_DIA = 5.0             # T-1 3/4 (5 mm) through-hole LED
PITCH_X = 7.5             # LED pitch, centre to centre (2.5 mm gap)
PITCH_Y = 7.5             # row-to-row pitch (2.5 mm gap)
POSITIONS_PER_ROW = 18    # outer position at each end = screw slot
ROWS = 2

# Cover
THICKNESS = 2.0           # thin plate; the LEDs pass through it
LED_HOLE_DIA = 5.2        # LED 5.0 mm + clearance
FLANGE_DIA = 6.2          # LED base flange 5.8 mm + clearance
FLANGE_DEPTH = 1.2        # LED base flange 1.0 mm + clearance
SLOT_WIDTH = 5.0          # screw slot width
SLOT_LENGTH = PITCH_Y + SLOT_WIDTH   # 12.5 mm overall, 7.5 mm centre to centre
CORNER_RADIUS = 1.0
TOP_EDGE_CHAMFER = 0.5

xs = [(i - (POSITIONS_PER_ROW - 1) / 2) * PITCH_X for i in range(POSITIONS_PER_ROW)]
ys = [(j - (ROWS - 1) / 2) * PITCH_Y for j in range(ROWS)]
LED_POINTS = [(x, y) for x in xs[1:-1] for y in ys]
SLOT_POINTS = [(xs[0], 0.0), (xs[-1], 0.0)]


def cylinders(points, dia, z0, height):
    return (cq.Workplane("XY").workplane(offset=z0)
            .pushPoints(points).circle(dia / 2).extrude(height))


def build():
    body = (cq.Workplane("XY")
            .box(PCB_LENGTH, PCB_HEIGHT, THICKNESS, centered=(True, True, False))
            .edges("|Z").fillet(CORNER_RADIUS)
            .faces(">Z").edges().chamfer(TOP_EDGE_CHAMFER))

    led_bores = cylinders(LED_POINTS, LED_HOLE_DIA, -1, THICKNESS + 2)
    flange_pockets = cylinders(LED_POINTS, FLANGE_DIA, -1, FLANGE_DEPTH + 1)
    screw_slots = (cq.Workplane("XY").workplane(offset=-1)
                   .pushPoints(SLOT_POINTS)
                   .slot2D(SLOT_LENGTH, SLOT_WIDTH, angle=90)
                   .extrude(THICKNESS + 2))

    return body.cut(led_bores).cut(flange_pockets).cut(screw_slots)


if __name__ == "__main__":
    cover = build()
    out = Path(__file__).resolve().with_suffix("")
    cq.exporters.export(cover, str(out.with_suffix(".step")))
    cq.exporters.export(cover, str(out.with_suffix(".stl")))
    print(f"LED bores: {len(LED_POINTS)}, screw slots: {len(SLOT_POINTS)}")
    print(f"Volume: {cover.val().Volume():.1f} mm^3")
