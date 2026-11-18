# SPIKE Prime maze solver (Pybricks) - wall follower with 3 ultrasonic sensors
# Paste into code.pybricks.com, connect the hub, press Run. Center button stops the robot.
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
LEFT_EYE = Port.D          # left sensor: change to Port.F if that is where you plugged it

# ---------------- SETTINGS (mm) ----------------
RULE = "right"             # "right" = follow the right wall, "left" = follow the left wall
WHEEL = 56                 # SPIKE wheel diameter
AXLE = 112                 # distance between the two wheels (measure yours)
CELL = 250                 # length of one maze square
WALL = 170                 # side/front reading below this = there is a wall
SIDE_TARGET = 70           # wanted distance to a side wall while driving
FRONT_STOP = 70            # stop this far from a wall in front
SPEED = 250                # mm/s straight
TURN_SPEED = 180           # deg/s turning
KP = 1.2                   # steering strength for keeping straight
MAX_STEER = 60             # deg/s

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)                                 # forward fixed: directions swapped
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, turn_rate=TURN_SPEED)
try:
    robot.use_gyro(True)   # uses the hub gyro for exact 90 deg turns (Pybricks 3.3+)
except AttributeError:
    pass

front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)
for eye in (front, right, left):
    eye.lights.on(100)


def dist(eye):
    """Median of 3 readings in mm (2000 = nothing seen)."""
    r = sorted(eye.distance() for _ in range(3))
    return r[1]


def walls():
    return dist(left) < WALL, dist(front) < WALL, dist(right) < WALL


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def forward_cell():
    """Drive one square, staying centred between the walls; stop early at a wall in front."""
    robot.reset()
    while robot.distance() < CELL:
        if dist(front) < FRONT_STOP:
            break
        l, r = dist(left), dist(right)
        if l < WALL and r < WALL:
            steer = (r - l) * KP / 2          # both walls: stay in the middle
        elif r < WALL:
            steer = (r - SIDE_TARGET) * KP    # only right wall
        elif l < WALL:
            steer = (SIDE_TARGET - l) * KP    # only left wall
        else:
            steer = 0
        robot.drive(SPEED, clamp(steer, -MAX_STEER, MAX_STEER))
        wait(10)
    robot.stop()
    square_to_front()


def square_to_front():
    """If a wall is in front, move to the same distance from it every time."""
    d = dist(front)
    if d < WALL:
        robot.straight(d - FRONT_STOP)


def turn(angle, icon):
    hub.display.icon(icon)
    robot.turn(angle)


# ---------------- MAIN ----------------
hub.light.on(Color.GREEN)
hub.display.icon(Icon.HAPPY)
wait(1000)
first, second = (90, -90) if RULE == "right" else (-90, 90)

while True:
    wall_l, wall_f, wall_r = walls()
    open_first = not wall_r if RULE == "right" else not wall_l
    open_second = not wall_l if RULE == "right" else not wall_r
    if open_first:                        # 1. turn to the followed side if it is open
        turn(first, Icon.ARROW_RIGHT if first > 0 else Icon.ARROW_LEFT)
        forward_cell()
    elif not wall_f:                      # 2. else go straight
        hub.display.icon(Icon.ARROW_UP)
        forward_cell()
    elif open_second:                     # 3. else turn to the other side
        turn(second, Icon.ARROW_LEFT if second < 0 else Icon.ARROW_RIGHT)
        forward_cell()
    else:                                 # 4. dead end: turn around
        hub.light.on(Color.ORANGE)
        turn(180, Icon.ARROW_DOWN)
        hub.light.on(Color.GREEN)
