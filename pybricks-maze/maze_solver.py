# SPIKE Prime maze robot (Pybricks): drive straight until an obstacle is in front, then turn to the open side
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

# ---------------- SETTINGS (mm) ----------------
RULE = "right"             # which side to try first at an obstacle: "right" or "left"
USE_GYRO = False           # True only if the hub is mounted flat, screen up
WHEEL = 56
AXLE = 112
FRONT_STOP = 120           # obstacle closer than this in front = stop and turn
WALL = 170                 # side reading below this = wall on that side
SIDE_TARGET = 70           # keep this far from a side wall while driving
SPEED = 250
TURN_SPEED = 180
KP = 1.0
MAX_STEER = 40

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, turn_rate=TURN_SPEED)
if USE_GYRO:
    robot.use_gyro(True)

front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)
for eye in (front, right, left):
    eye.lights.on(100)


def dist(eye):
    r = sorted([eye.distance(), eye.distance(), eye.distance()])
    return r[1]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def steer_from_walls():
    l = dist(left)
    r = dist(right)
    if l < WALL and r < WALL:
        return (r - l) * KP / 2
    if r < WALL:
        return (r - SIDE_TARGET) * KP
    if l < WALL:
        return (SIDE_TARGET - l) * KP
    return 0


def turn(angle, icon):
    robot.stop()
    hub.display.icon(icon)
    robot.turn(angle)
    hub.display.icon(Icon.ARROW_UP)


# ---------------- MAIN ----------------
hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)
wait(1000)

while True:
    if dist(front) > FRONT_STOP:
        robot.drive(SPEED, clamp(steer_from_walls(), -MAX_STEER, MAX_STEER))    # straight
        wait(10)
        continue

    robot.stop()                                   # obstacle in front
    hub.light.on(Color.ORANGE)
    wait(100)
    right_open = dist(right) > WALL
    left_open = dist(left) > WALL
    if RULE == "right":
        if right_open:
            turn(90, Icon.ARROW_RIGHT)
        elif left_open:
            turn(-90, Icon.ARROW_LEFT)
        else:
            turn(180, Icon.ARROW_DOWN)
    else:
        if left_open:
            turn(-90, Icon.ARROW_LEFT)
        elif right_open:
            turn(90, Icon.ARROW_RIGHT)
        else:
            turn(180, Icon.ARROW_DOWN)
    hub.light.on(Color.GREEN)
