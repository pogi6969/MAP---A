# Predator Mini 2WD + Matador flags

![regular](diagram_regular.png)
![flag](diagram_flag.png)
![matador](matador.png)

* **Size 91.6 × 100 mm** (fits 10 × 10 cm), 38.5 mm tall. 2 × N20 2000 rpm.
* **Kept from Predator:** built-in 32° wedge with the front IR window through the slope, every sensor opening at its original size.
* **Small N20s compensated:** CG just ahead of the axle → 89 % of the 500 g on the drive wheels; wedge tip skims at 0.6 mm;
  wider Ø34 × 12 silicone wheels (make them with `wheel-mold`, set the size to 34 × 12); lead low in the body.
* **Flags (Matador style):** SG90 lying behind a wall, two 12-tooth gears (module 1.5) make the wings turn in opposite directions.
  Wings 85 × 50 mm stand up inside the footprint at the start (151 mm tall), open 120° to 166 mm wide.
  Bolt the module to the lid with 2 × M3; same lid for both robots.

| file | g | time |
|---|---|---|
| `base.stl` | 104 | 8h25m |
| `lid.stl` | 11 | 1h0m |
| `matador_flags.stl` | 32 | 2h57m |

| | regular | with flags |
|---|---|---|
| printed | 114 g | 146 g |
| lead: front / on motors / behind motors | 95 / 66 / 83 g | 83 / 25 / 95 g |
| on the drive wheels | 89 % | 89 % |

**Matador assembly:** press gear 1 onto the SG90 spline + horn screw; gear 2 on an M3 × 16 into the pillar; servo into the wall
(2 tab screws); slide each wing into its gear slot and pin it (M2 screw or 2 mm filament). Set the servo so both wings point up,
then in code: at the start signal turn the servo 120°. Check your event's flag rules (some allow max 2–4 flags, upright and
inside the robot's outline at the start).
