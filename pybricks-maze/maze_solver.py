# SPIKE Prime fast maze robot (Pybricks) - right-hand wall follower, no scanning turns
# - drives fast, keeps the right wall at a fixed distance
# - takes every opening on the RIGHT as soon as the right sensor sees it
# - at a wall in front: right if open, else left, else turn around
# - anti-trap: if the wheels get stuck or it keeps turning without moving, it backs up and turns around
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

# ---------------- PORTS ----------------
LEFT_MOTOR = Port.B
RIGHT_MOTOR = Port.E
FRONT_EYE = Port.C
RIGHT_EYE = Port.A
LEFT_EYE = Port.D          # change to Port.F if your left sensor is there

# ---------------- SETTINGS (mm) ----------------
WHEEL = 56
AXLE = 112                 # distance between the wheels: bigger number = turns more
SPEED = 450                # top speed mm/s
TURN_SPEED = 360           # deg/s
FRONT_STOP = 110           # wall in front closer than this = stop and choose
SLOW_ZONE = 250            # start slowing down when the front wall is closer than this
WALL = 180                 # side reading below this = there is a wall on that side
OPEN = 260                 # side reading above this (2 reads in a row) = opening
RIGHT_TARGET = 80          # distance to keep from the right wall
KP = 1.2                   # steering strength
MAX_STEER = 70
PASS = 70                  # after an opening appears on the right, drive this far before turning
ENTER = 120                # after turning into an opening, drive this far in before looking again

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, straight_acceleration=1500, turn_rate=TURN_SPEED, turn_acceleration=2000)
front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)


def read(eye):
    """Median of 3 readings. 2000 means nothing in range (open)."""
    a, b, c = eye.distance(), eye.distance(), eye.distance()
    return sorted([a, b, c])[1]


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def turn(angle, icon):
    robot.stop()
    hub.display.icon(icon)
    robot.turn(angle)
    hub.display.icon(Icon.ARROW_UP)


def unstuck():
    hub.light.on(Color.RED)
    robot.stop()
    robot.straight(-80)
    turn(180, Icon.ARROW_DOWN)
    hub.light.on(Color.GREEN)


def at_front_wall():
    """Stopped at a wall: check RIGHT first, then left, else turn around."""
    robot.stop()
    r, l = read(right), read(left)
    if r > OPEN:
        turn(90, Icon.ARROW_RIGHT)
    elif l > OPEN:
        turn(-90, Icon.ARROW_LEFT)
    elif r > l and r > WALL:
        turn(90, Icon.ARROW_RIGHT)          # right is a bit more open
    elif l > WALL:
        turn(-90, Icon.ARROW_LEFT)
    else:
        turn(180, Icon.ARROW_DOWN)          # dead end


# ---------------- MAIN ----------------
hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)
wait(500)
had_right_wall = False
open_count = 0
turns_in_a_row = 0
stuck = StopWatch()

while True:
    f = front.distance()
    r = right.distance()
    l = left.distance()

    # 1) wall in front -> choose a side
    if f < FRONT_STOP:
        at_front_wall()
        turns_in_a_row += 1
        if turns_in_a_row >= 4:              # spinning in place = trapped
            unstuck()
            turns_in_a_row = 0
        had_right_wall, open_count = False, 0
        stuck.reset()
        continue

    # 2) opening on the right -> take it (right-hand rule)
    if r < WALL:
        had_right_wall = True
        open_count = 0
    elif r > OPEN and had_right_wall:
        open_count += 1
        if open_count >= 2:
            robot.straight(PASS)
            turn(90, Icon.ARROW_RIGHT)
            robot.straight(ENTER)
            had_right_wall, open_count, turns_in_a_row = False, 0, 0
            stuck.reset()
            continue

    # 3) drive: follow the right wall, avoid the left wall, slow down near a front wall
    if r < WALL:
        steer = (r - RIGHT_TARGET) * KP
    elif l < WALL:
        steer = (RIGHT_TARGET - l) * KP
    else:
        steer = 0
    v = SPEED if f > SLOW_ZONE else max(150, SPEED * (f - FRONT_STOP) / (SLOW_ZONE - FRONT_STOP))
    robot.drive(v, clamp(steer, -MAX_STEER, MAX_STEER))

    # 4) anti-stuck: wheels not turning while driving
    if abs(robot.state()[1]) > 40:
        stuck.reset()
        if robot.distance() > 50:
            turns_in_a_row = 0
    elif stuck.time() > 600:
        unstuck()
        stuck.reset()
    wait(5)
