# SPIKE Prime maze robot (Pybricks)
# 1) drive forward until an obstacle is in front
# 2) stop and SCAN: turn from left to right, measuring the distance at each angle
# 3) turn to the direction with the most free space (the path)
# 4) drive forward again, repeat
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# ---------------- PORTS ----------------
LEFT_MOTOR = Port.B
RIGHT_MOTOR = Port.E
FRONT_EYE = Port.C
RIGHT_EYE = Port.A
LEFT_EYE = Port.D          # change to Port.F if your left sensor is there

# ---------------- SETTINGS (mm, deg) ----------------
WHEEL = 56
AXLE = 112                 # distance between the wheels: bigger number = turns more
FRONT_STOP = 120           # obstacle closer than this in front = stop and scan
SIDE_MIN = 60              # a side wall closer than this = steer away while driving
OPEN = 250                 # a direction with more free space than this counts as a path
SCAN_FROM = -90            # scan from 90 deg left ...
SCAN_TO = 90               # ... to 90 deg right
SCAN_STEP = 15             # one reading every 15 deg
BACK_UP = 30               # back up a little before scanning
SPEED = 250
TURN_SPEED = 150

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, turn_rate=TURN_SPEED)

front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)
for eye in (front, right, left):
    eye.lights.on(100)


def dist(eye):
    r = sorted([eye.distance(), eye.distance(), eye.distance()])
    return r[1]


def scan():
    """Turn left to right, read the front sensor at each step, return (best angle, its distance)."""
    hub.light.on(Color.ORANGE)
    hub.display.icon(Icon.CIRCLE)
    robot.turn(SCAN_FROM)
    angle = SCAN_FROM
    best_angle, best_dist = angle, dist(front)
    while angle < SCAN_TO:
        robot.turn(SCAN_STEP)
        angle += SCAN_STEP
        wait(50)
        d = dist(front)
        if d > best_dist:
            best_angle, best_dist = angle, d
    robot.turn(best_angle - angle)          # face the best direction
    return best_angle, best_dist


# ---------------- MAIN ----------------
hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)
wait(1000)

while True:
    if dist(front) > FRONT_STOP:            # path ahead: drive forward
        steer = 0
        if dist(right) < SIDE_MIN:
            steer = -30                     # too close to the right wall: steer left
        elif dist(left) < SIDE_MIN:
            steer = 30                      # too close to the left wall: steer right
        robot.drive(SPEED, steer)
        wait(10)
        continue

    robot.stop()                            # obstacle: back up a little, then scan
    robot.straight(-BACK_UP)
    best_angle, best_dist = scan()
    if best_dist < OPEN:                    # nothing open from left to right: turn around
        robot.turn(180)
    hub.light.on(Color.GREEN)
    hub.display.icon(Icon.ARROW_UP)
