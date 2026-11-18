# SPIKE Prime MICROMOUSE (Pybricks)
# Maps the maze cell by cell with 3 ultrasonic sensors, uses flood fill to find the shortest way to the goal,
# drives back to the start, then does a fast SPEED RUN on the shortest known path (long straights in one go).
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

# ---------------- MAZE ----------------
MAZE_W = 6                 # cells across
MAZE_H = 6                 # cells forward
START = (0, 0)             # start cell = bottom-left corner, robot facing "up" (north)
GOALS = [(2, 2), (2, 3), (3, 2), (3, 3)]   # goal cells (centre of a 6 x 6 maze)
CELL = 180                 # size of one cell in mm (centre to centre)

# ---------------- ROBOT (mm) ----------------
WHEEL = 56
AXLE = 112                 # distance between the wheels: bigger number = turns more
USE_GYRO = False           # True = more accurate turns, ONLY if the hub is mounted flat, screen up
WALL = 120                 # sensor reading below this = wall next to / in front of this cell
FRONT_CENTER = 55          # front sensor reading when the robot is centred in a cell with a wall ahead
SIDE_CENTER = 55           # side sensor reading when the robot is centred between walls
KP = 1.5                   # steering strength (wall centring)
MAX_STEER = 60
EXPLORE_SPEED = 300        # mm/s while mapping
RUN_SPEED = 600            # mm/s on the speed run
TURN_SPEED = 360           # deg/s

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=EXPLORE_SPEED, straight_acceleration=1500,
               turn_rate=TURN_SPEED, turn_acceleration=2000)
if USE_GYRO:
    robot.use_gyro(True)
front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)

DX = [0, 1, 0, -1]         # 0 = north, 1 = east, 2 = south, 3 = west
DY = [1, 0, -1, 0]
walls = [[0] * MAZE_H for _ in range(MAZE_W)]      # bit d set = wall on side d of the cell
seen = [[False] * MAZE_H for _ in range(MAZE_W)]   # cells the robot has measured


def inside(x, y):
    return 0 <= x < MAZE_W and 0 <= y < MAZE_H


def add_wall(x, y, d):
    walls[x][y] |= 1 << d
    nx, ny = x + DX[d], y + DY[d]
    if inside(nx, ny):
        walls[nx][ny] |= 1 << ((d + 2) % 4)


for i in range(MAZE_W):                            # outer walls
    add_wall(i, 0, 2)
    add_wall(i, MAZE_H - 1, 0)
for j in range(MAZE_H):
    add_wall(0, j, 3)
    add_wall(MAZE_W - 1, j, 1)


def flood(targets, known_only=False):
    """Distance (in cells) from every cell to the nearest target. Unknown walls count as open."""
    dist = [[999] * MAZE_H for _ in range(MAZE_W)]
    queue = []
    for (x, y) in targets:
        dist[x][y] = 0
        queue.append((x, y))
    i = 0
    while i < len(queue):
        x, y = queue[i]
        i += 1
        for d in range(4):
            if walls[x][y] & (1 << d):
                continue
            nx, ny = x + DX[d], y + DY[d]
            if not inside(nx, ny) or (known_only and not seen[nx][ny]):
                continue
            if dist[nx][ny] > dist[x][y] + 1:
                dist[nx][ny] = dist[x][y] + 1
                queue.append((nx, ny))
    return dist


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def sense(x, y, h):
    """Read the 3 sensors in the middle of a cell and store the walls."""
    if left.distance() < WALL:
        add_wall(x, y, (h + 3) % 4)
    if front.distance() < WALL:
        add_wall(x, y, h)
    if right.distance() < WALL:
        add_wall(x, y, (h + 1) % 4)
    seen[x][y] = True


def turn_to(h, d):
    diff = (d - h) % 4
    if diff == 1:
        robot.turn(90)
    elif diff == 2:
        robot.turn(180)
    elif diff == 3:
        robot.turn(-90)
    return d


def drive_cells(n, speed):
    """Drive n cells straight, centred between the walls, then fix the position on a front wall."""
    target = n * CELL
    robot.reset()
    while robot.distance() < target:
        f = front.distance()
        if f < FRONT_CENTER:
            break
        l = left.distance()
        r = right.distance()
        if l < WALL and r < WALL:
            steer = (r - l) * KP / 2
        elif r < WALL:
            steer = (r - SIDE_CENTER) * KP
        elif l < WALL:
            steer = (SIDE_CENTER - l) * KP
        else:
            steer = 0
        left_to_go = target - robot.distance()
        v = speed if left_to_go > 120 else max(150, speed * left_to_go / 120)   # slow down at the end
        robot.drive(v, clamp(steer, -MAX_STEER, MAX_STEER))
    robot.stop()
    f = front.distance()
    if f < WALL:                                   # wall ahead: correct the distance error
        robot.straight(f - FRONT_CENTER)


def best_dir(x, y, h, dist):
    best, best_d = None, 999
    for k in (0, 1, 3, 2):                         # prefer straight, then right, left, back
        d = (h + k) % 4
        if walls[x][y] & (1 << d):
            continue
        nx, ny = x + DX[d], y + DY[d]
        if inside(nx, ny) and dist[nx][ny] < best_d:
            best, best_d = d, dist[nx][ny]
    return best


def explore(x, y, h, targets, icon):
    """Map while driving to the targets (flood fill after every cell)."""
    hub.display.icon(icon)
    while (x, y) not in targets:
        sense(x, y, h)
        dist = flood(targets)
        d = best_dir(x, y, h, dist)
        if d is None:                              # no way out (maze settings wrong)
            hub.light.on(Color.RED)
            return x, y, h
        h = turn_to(h, d)
        drive_cells(1, EXPLORE_SPEED)
        x, y = x + DX[h], y + DY[h]
    sense(x, y, h)
    return x, y, h


def speed_run(x, y, h):
    """Follow the shortest known path; join straight cells into one fast move."""
    hub.display.icon(Icon.FULL)
    dist = flood(GOALS, known_only=True)
    if dist[x][y] >= 999:
        dist = flood(GOALS)
    while (x, y) not in GOALS:
        d = best_dir(x, y, h, dist)
        if d is None:
            break
        h = turn_to(h, d)
        n = 0
        cx, cy = x, y
        while True:                                # count cells in this straight line
            nx, ny = cx + DX[h], cy + DY[h]
            if walls[cx][cy] & (1 << h) or not inside(nx, ny) or dist[nx][ny] != dist[cx][cy] - 1:
                break
            cx, cy = nx, ny
            n += 1
            if (cx, cy) in GOALS:
                break
        drive_cells(n, RUN_SPEED)
        x, y = cx, cy
    return x, y, h


# ---------------- MAIN ----------------
hub.light.on(Color.GREEN)
wait(1000)
x, y, h = START[0], START[1], 0
x, y, h = explore(x, y, h, GOALS, Icon.ARROW_UP)          # 1. search to the goal
hub.light.on(Color.YELLOW)
x, y, h = explore(x, y, h, [START], Icon.ARROW_DOWN)       # 2. search back to the start
h = turn_to(h, 0)
hub.light.on(Color.MAGENTA)
wait(1000)
x, y, h = speed_run(x, y, h)                               # 3. fast run on the shortest path
hub.light.on(Color.BLUE)
hub.display.icon(Icon.HAPPY)
wait(5000)
