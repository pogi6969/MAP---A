# ================================================================
#  SPIKE Prime MICROMOUSE - Pybricks  (3 ultrasonic sensors, 2 motors)
#  1. SEARCH  : maps the maze cell by cell, flood fill picks the shortest way to the goal
#  2. RETURN  : maps more on the way back to the start
#  3. SPEED RUN: shortest known path, straights joined, braking curve v = sqrt(2*a*d)
#  Math used:
#   - sensor geometry  -> expected readings when centred (SIDE_CENTER, FRONT_CENTER)
#   - wall threshold   -> half way into the next cell
#   - lateral error e  -> from left/right readings,  heading error th = atan2(dd, ds) from the wall slope
#   - steering         -> turn_rate = KP*e + KH*th  (PD on position + heading)
#   - speed            -> trapezoid: accelerate, cruise, brake so v^2 = 2*a*d to the stop point
#   - median filter + "2000 = nothing in range" handling + stall (stuck) detection
#  Set CALIBRATE = True first: it prints the 3 sensor values so you can check the numbers.
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
import umath

# ---------------- PORTS ----------------
LEFT_MOTOR = Port.B
RIGHT_MOTOR = Port.E
FRONT_EYE = Port.C
RIGHT_EYE = Port.A
LEFT_EYE = Port.D            # change to Port.F if your left sensor is there

CALIBRATE = False            # True = only print sensor values (robot does not move)

# ---------------- MAZE ----------------
MAZE_W, MAZE_H = 6, 6        # cells across, cells forward
START = (0, 0)               # bottom-left corner, robot facing north (up)
GOALS = [(2, 2), (2, 3), (3, 2), (3, 3)]
CELL = 250                   # cell pitch, mm (centre to centre) - measure your maze
WALL_T = 12                  # wall thickness, mm

# ---------------- ROBOT GEOMETRY (mm, measure yours) ----------------
WHEEL = 56                   # wheel diameter
AXLE = 112                   # wheel to wheel (centre of tyres)
SIDE_OFS = 40                # robot centre line -> face of a side sensor
FRONT_OFS = 40               # robot centre (wheel axle) -> face of the front sensor
USE_GYRO = False             # True only if the hub is mounted flat, screen up

# ---------------- DERIVED (math, do not change) ----------------
FREE = (CELL - WALL_T) / 2               # free space from cell centre to a wall face
SIDE_CENTER = FREE - SIDE_OFS            # side reading when centred between walls
FRONT_CENTER = FREE - FRONT_OFS          # front reading when centred with a wall ahead
SIDE_WALL = SIDE_CENTER + CELL / 2       # side reading below this = wall in this cell
FRONT_WALL = FRONT_CENTER + CELL / 2     # front reading below this = wall at the end of this cell
SENSOR_MIN = 30                          # ultrasonic blind zone; below this = very close

# ---------------- MOTION ----------------
SEARCH_SPEED = 350           # mm/s
RUN_SPEED = 700              # mm/s (speed run)
V_MIN = 120                  # mm/s minimum while braking
ACCEL = 1800                 # mm/s^2 (used for the braking curve too)
TURN_SPEED = 400             # deg/s
TURN_ACCEL = 2500            # deg/s^2
KP = 2.0                     # deg/s of turn per mm of lateral error
KH = 3.0                     # deg/s of turn per degree of heading error
MAX_STEER = 90               # deg/s

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SEARCH_SPEED, straight_acceleration=ACCEL, turn_rate=TURN_SPEED, turn_acceleration=TURN_ACCEL)
if USE_GYRO:
    robot.use_gyro(True)
front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)


# ---------------- SENSORS ----------------
def read(eye, n=3):
    """Median of n readings (mm). 2000 = no echo = open. Below the blind zone = touching."""
    v = sorted([eye.distance() for _ in range(n)])[n // 2]
    if v <= 0:
        return 2000
    return max(v, SENSOR_MIN)


if CALIBRATE:
    print("expected  side centred:", SIDE_CENTER, " front centred:", FRONT_CENTER,
          " side wall below:", SIDE_WALL, " front wall below:", FRONT_WALL)
    while True:
        l, f, r = read(left), read(front), read(right)
        print("L", l, " F", f, " R", r)
        hub.display.number(min(99, f // 10))          # front distance in cm on the hub
        wait(200)


# ---------------- MAP ----------------
DX = [0, 1, 0, -1]           # 0 north, 1 east, 2 south, 3 west
DY = [1, 0, -1, 0]
walls = [[0] * MAZE_H for _ in range(MAZE_W)]
seen = [[False] * MAZE_H for _ in range(MAZE_W)]


def inside(x, y):
    return 0 <= x < MAZE_W and 0 <= y < MAZE_H


def add_wall(x, y, d):
    walls[x][y] |= 1 << d
    nx, ny = x + DX[d], y + DY[d]
    if inside(nx, ny):
        walls[nx][ny] |= 1 << ((d + 2) % 4)


for i in range(MAZE_W):
    add_wall(i, 0, 2)
    add_wall(i, MAZE_H - 1, 0)
for j in range(MAZE_H):
    add_wall(0, j, 3)
    add_wall(MAZE_W - 1, j, 1)


def flood(targets, known_only=False):
    """Breadth-first flood fill: distance in cells to the nearest target (unknown walls = open)."""
    dist = [[999] * MAZE_H for _ in range(MAZE_W)]
    q = []
    for (x, y) in targets:
        dist[x][y] = 0
        q.append((x, y))
    i = 0
    while i < len(q):
        x, y = q[i]
        i += 1
        for d in range(4):
            if walls[x][y] & (1 << d):
                continue
            nx, ny = x + DX[d], y + DY[d]
            if not inside(nx, ny) or (known_only and not seen[nx][ny]):
                continue
            if dist[nx][ny] > dist[x][y] + 1:
                dist[nx][ny] = dist[x][y] + 1
                q.append((nx, ny))
    return dist


def sense(x, y, h):
    """At a cell centre: read the 3 sensors (5 samples each) and store the walls."""
    if read(left, 5) < SIDE_WALL:
        add_wall(x, y, (h + 3) % 4)
    if read(front, 5) < FRONT_WALL:
        add_wall(x, y, h)
    if read(right, 5) < SIDE_WALL:
        add_wall(x, y, (h + 1) % 4)
    seen[x][y] = True


def print_map():
    for y in range(MAZE_H - 1, -1, -1):
        top = ""
        mid = ""
        for x in range(MAZE_W):
            top += "+--" if walls[x][y] & 1 else "+  "
            mid += ("|" if walls[x][y] & 8 else " ") + ("G " if (x, y) in GOALS else ("S " if (x, y) == START else "  "))
        print(top + "+")
        print(mid + "|")
    print("+--" * MAZE_W + "+")


# ---------------- MOTION ----------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def turn_to(h, d):
    diff = (d - h) % 4
    if diff:
        robot.stop()
        robot.turn((90, 180, -90)[diff - 1])
    return d


def drive_cells(n, vmax):
    """Drive n cells: PD wall centring, braking curve, front-wall correction, stall detection.
    Returns False if the robot got stuck (an unseen obstacle)."""
    target = n * CELL
    robot.reset()
    prev_s, prev_side, prev_which = 0, None, None
    th = 0.0
    stuck = StopWatch()
    while True:
        s = robot.distance()
        f, l, r = read(front, 1), read(left, 1), read(right, 1)
        to_go = target - s
        if f < FRONT_WALL + CELL:                      # wall ahead within reach: stop on it exactly
            to_go = min(to_go, f - FRONT_CENTER)
        if to_go <= 2:
            break
        # lateral error e (mm, + = robot is left of centre) and heading from the wall slope
        if l < SIDE_WALL and r < SIDE_WALL:
            e, which, side = (r - l) / 2, "R", r
        elif r < SIDE_WALL:
            e, which, side = r - SIDE_CENTER, "R", r
        elif l < SIDE_WALL:
            e, which, side = SIDE_CENTER - l, "L", l
        else:
            e, which, side = 0, None, None
        if which and which == prev_which and s - prev_s >= 25:
            dd = side - prev_side
            th = umath.atan2(dd if which == "R" else -dd, s - prev_s) * 180 / umath.pi
            prev_s, prev_side = s, side
        elif which != prev_which:
            prev_s, prev_side, prev_which, th = s, side, which, 0.0
        steer = clamp(KP * e + KH * th, -MAX_STEER, MAX_STEER) if which else 0
        # trapezoid speed: accelerate (DriveBase limits), cruise vmax, brake with v = sqrt(2*a*d)
        v = clamp(umath.sqrt(2 * ACCEL * max(to_go, 0)) * 0.8, V_MIN, vmax)
        robot.drive(v, steer)
        # stall: commanded to move but wheels not turning
        if abs(robot.state()[1]) > 40:
            stuck.reset()
        elif stuck.time() > 500:
            robot.stop()
            robot.straight(-min(s % CELL, 60) - 10)   # back off the obstacle
            return False
        wait(5)
    robot.stop()
    f = read(front, 3)
    if f < FRONT_WALL:                                 # final front-wall correction
        robot.straight(f - FRONT_CENTER)
    return True


def best_dir(x, y, h, dist):
    best, best_d = None, 999
    for k in (0, 1, 3, 2):                             # straight, right, left, back
        d = (h + k) % 4
        if walls[x][y] & (1 << d):
            continue
        nx, ny = x + DX[d], y + DY[d]
        if inside(nx, ny) and dist[nx][ny] < best_d:
            best, best_d = d, dist[nx][ny]
    return best


def explore(x, y, h, targets, icon):
    hub.display.icon(icon)
    while (x, y) not in targets:
        sense(x, y, h)
        d = best_dir(x, y, h, flood(targets))
        if d is None:
            hub.light.on(Color.RED)
            print("no path - check MAZE_W / MAZE_H / GOALS / thresholds")
            return x, y, h
        h = turn_to(h, d)
        if drive_cells(1, SEARCH_SPEED):
            x, y = x + DX[h], y + DY[h]
        else:
            add_wall(x, y, h)                          # stuck = there is a wall the sensor missed
    sense(x, y, h)
    return x, y, h


def speed_run(x, y, h):
    hub.display.icon(Icon.FULL)
    dist = flood(GOALS, known_only=True)
    if dist[x][y] >= 999:
        dist = flood(GOALS)
    while (x, y) not in GOALS:
        d = best_dir(x, y, h, dist)
        if d is None:
            break
        h = turn_to(h, d)
        n, cx, cy = 0, x, y
        while True:
            nx, ny = cx + DX[h], cy + DY[h]
            if walls[cx][cy] & (1 << h) or not inside(nx, ny) or dist[nx][ny] != dist[cx][cy] - 1:
                break
            cx, cy, n = nx, ny, n + 1
            if (cx, cy) in GOALS:
                break
        if not drive_cells(n, RUN_SPEED):
            add_wall(x, y, h)
            dist = flood(GOALS)
            continue
        x, y = cx, cy
    return x, y, h


# ---------------- MAIN ----------------
print("side centred", SIDE_CENTER, "| front centred", FRONT_CENTER, "| side wall <", SIDE_WALL, "| front wall <", FRONT_WALL)
if SIDE_CENTER < 40 or FRONT_CENTER < 40:
    print("WARNING: robot too wide for this CELL - sensors would be closer than 4 cm (ultrasonic blind zone)")
hub.light.on(Color.GREEN)
wait(1000)
x, y, h = START[0], START[1], 0
x, y, h = explore(x, y, h, GOALS, Icon.ARROW_UP)          # 1. search
hub.light.on(Color.YELLOW)
x, y, h = explore(x, y, h, [START], Icon.ARROW_DOWN)       # 2. back to start
h = turn_to(h, 0)
print_map()
hub.light.on(Color.MAGENTA)
wait(1500)
x, y, h = speed_run(x, y, h)                               # 3. speed run
hub.light.on(Color.BLUE)
hub.display.icon(Icon.HAPPY)
print("done at", x, y)
wait(5000)
