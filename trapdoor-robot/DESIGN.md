# Trapdoor ball robot — dispenses on contact

![preview](preview.png)

Two prints. CR-6 SE, PETG, 0.2 mm, G-code ready.

| file | print as | PETG | time | G-code |
|---|---|---|---|---|
| `hopper_door.stl` | carrier: hopper + trapdoor, open top up, door on the bed (hinge prints in place), supports off | 136 g | 11h 47m 21s | `hopper_door_PETG_11h47m.gcode` |
| `chassis.stl` | chassis + bumper + 4 posts in one piece, upright on the skids, organic supports under the plate | 142 g | 15h 8m 16s | `chassis_PETG_15h8m.gcode` |

## How it works
1. Robot drives at the tower's 150 mm face. Arms + skids pass beside the tower (5 mm each side); hopper floor is 10 mm above the tower top.
2. Bumper nub hits the tower → PETG plate bends back → its tongue slides out from under the door's rear edge after 3.3 mm → trapdoor swings down, balls drop straight into the tower. 45° back slope feeds the last ones.
3. Chassis front edge is the hard stop, 8 mm after first contact.
4. Backing away: the tower wall pushes the hanging door forward; it flips out under the front wall (no jam).
5. Reset: push the door up — the 45° cam on the tongue clicks it shut.

## After printing / assembly
* Snap off the thin fin under the hopper's front wall (support for that wall). Work the door a few times.
* Remove the supports under the chassis plate.
* Set the carrier on the 4 posts: square tenons into the bracket holes (drop of CA glue).
* Your N20 brackets: 2 × M3 each (19.5 mm holes, axle at x = 0). MCB on the xsx hole pattern. Sensor bar on the front slots.
* Battery centre ~30 mm in front of the axle.

## Numbers
| | |
|---|---|
| capacity | 31 balls of 40 mm fit below the rim (hopper 130 mm tall, top at 240 mm) |
| trapdoor | 87 × 139 mm, hinge Ø6 knuckles, 45° cone pins, 0.4 mm gaps |
| release | nub travel 3.3 mm, push ≈ 1.1 N (spring 0.29 N/mm + friction), plate strain 0.40 % at 8 mm (PETG yield ≈ 3 %) |
| mass | ≈ 548 g loaded (assumed: N20 ×2, wheels, MCB 30 g, battery 95 g, sensor bar 20 g) |
| CG | x = 54 mm, z = 88 mm → 63 % of weight on the drive wheels |
| tipping | sideways 0.96 g, forward (braking) 1.04 g, backward 0.61 g |
