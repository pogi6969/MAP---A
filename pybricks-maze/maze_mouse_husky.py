# ================================================================
#  SPIKE Prime MICROMOUSE + HuskyLens camera - Pybricks        (black walls, HuskyLens on port F)
#  BRAIN (micromouse):
#   1. SEARCH   : maps the maze cell by cell, flood fill picks the shortest way to the goal
#   2. RETURN   : maps more on the way back to the start
#   3. SPEED RUN: shortest known path, straights joined, braking curve v = sqrt(2*a*d)
#   MEMORY: map saved in the hub - next run is a SMOOTH run (no stops, corners driven as arcs)
#  EYES: 3 ultrasonic sensors (exact wall distances) + HuskyLens camera (Color Recognition):
#   STRAIGHT / AVOID WALLS : black side walls in the picture -> extra steering on top of the ultrasonic centring
#   OBSTACLE AHEAD         : obstacle colour in the next cell -> put on the map as a wall, flood fill goes round it
#                            (obstacle suddenly close while driving -> stop, back to the cell centre, re-plan)
#   WALL AHEAD             : black wall filling the bottom of the picture = wall at the end of this cell
#   WHERE / WHEN TO TURN   : at every cell centre from the flood fill; a LEFT / RIGHT card on the wall ahead
#                            overrides it (search only); the GOAL card makes that cell the goal
#  No camera / camera not answering -> it runs as the plain ultrasonic micromouse.
#  HuskyLens: Color Recognition, Learn Multiple ON, learn: ID1 = BLACK wall, ID2 = obstacle,
#             ID3 = LEFT card, ID4 = RIGHT card, ID5 = GOAL card (2-5 optional).
#             General Settings: Protocol Type = Serial, UART Baudrate = 115200.
#  Wiring: HuskyLens T -> port F pin 6, R -> pin 5, GND -> pin 3, + to a 5 V power bank (its GND to pin 3 too).
#  Set CALIBRATE = True first: robot stands still and prints the 3 ultrasonic values + what the camera sees.
#  Hold the LEFT button while starting to forget the saved map. Turn the hub off with its button.
#  Math: sensor geometry -> expected readings, wall threshold half way into the next cell,
#  steering turn_rate = KP*e + KH*th (+ KC*camera error), braking v^2 = 2*a*d, median filter, stall detection.
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port, Direction, Color, Icon, Button, Stop
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch
import umath

# ---------------- PORTS ----------------
LEFT_MOTOR = Port.B
RIGHT_MOTOR = Port.E
FRONT_EYE = Port.C
RIGHT_EYE = Port.A
LEFT_EYE = Port.D
HUSKY_PORT = Port.F          # HuskyLens camera (UART)
BAUD = 115200                # = HuskyLens UART Baudrate
HUSKY_POWER = 1              # LEGO cable wire feeding the 5 V converter IN+: 1 = pin 1, 2 = pin 2, 0 = own power
USE_CAMERA = True            # False = run without the HuskyLens (unplug it from port F)

CALIBRATE = False            # True = only print sensor + camera values (robot does not move)

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
SMOOTH_SPEED = 600           # mm/s on remembered runs
ARC_SPEED = 300              # mm/s through the arc turns
V_MIN = 120                  # mm/s minimum while braking
ACCEL = 1800                 # mm/s^2 (used for the braking curve too)
TURN_SPEED = 400             # deg/s
TURN_ACCEL = 2500            # deg/s^2
KP = 2.0                     # deg/s of turn per mm of lateral error
KH = 3.0                     # deg/s of turn per degree of heading error
MAX_STEER = 90               # deg/s

# ---------------- CAMERA (picture 320 x 240) ----------------
WALL_ID, OBST_ID, LEFT_ID, RIGHT_ID, GOAL_ID = 1, 2, 3, 4, 5
USE_CARDS = True             # LEFT / RIGHT / GOAL cards change the route
H_REF = 180                  # side wall block height when centred (CALIBRATE shows "wall h")
OBST_NEAR_Y = 185            # at a cell centre: obstacle bottom edge below this row = obstacle in the next cell
OBST_STOP_Y = 236            # while driving: obstacle reaching this row = right in front -> stop
WALL_NEAR_Y = 236            # black wall across the path reaching this row = wall at the end of this cell
WALL_MIN_H = 30              # black blocks flatter than this are floor lines, not walls
SIGN_W = 40                  # card at least this wide = on the wall in front of this cell
KC = 0.25                    # deg/s per px of camera error, added to the ultrasonic steering
KP_CAM = 0.45                # deg/s per px when only the camera sees walls
K_H = 0.5                    # weight of the left / right wall size difference
PATH_HALF = 60               # half the robot width in the picture
MIN_AREA = 300               # smaller blocks are noise (shadows)
EDGE = 8                     # block this close to the picture side touches it
CAM_MS = 30                  # read the camera every 30 ms while driving
SIDE_H = H_REF * 6 // 10     # side block this tall = wall beside the robot

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


# ---------------- HUSKYLENS (UART protocol) ----------------
class HuskyLens:
    HEAD = b"\x55\xaa\x11"
    BAUDS = (115200, 9600, 1000000)                            # every HuskyLens "UART Baudrate" setting

    def __init__(self, port, baud, power_pin=0):
        self.ok, self.baud = False, None
        try:
            self.uart = self._open(port, baud, power_pin)
        except Exception as e:
            print("HuskyLens port error:", e)
            return
        if power_pin:
            print("power on pin", power_pin, "- HuskyLens screen should light up")
            wait(2500)                                         # camera boots after the power comes on
        order = [baud] + [b for b in self.BAUDS if b != baud]
        for _ in range(6):                                     # camera needs about 3 s to start up
            for b in order:
                try:
                    self.uart.set_baudrate(b)
                except AttributeError:
                    self.uart = self._open(port, b, power_pin)
                if self.cmd(0x2C) == 0x2E:                     # knock -> OK
                    self.ok, self.baud = True, b
                    return
            wait(400)

    def _open(self, port, b, power_pin):
        try:
            return UARTDevice(port, b, timeout=50, power_pin=power_pin)    # Pybricks v4: power on pin 1 / 2
        except TypeError:
            if power_pin:
                print("this Pybricks has no power_pin - update it to v4 so the hub can power the camera")
            return UARTDevice(port, b, timeout=50)

    def _send(self, cmd, data=b""):
        f = self.HEAD + bytes([len(data), cmd]) + data
        self.uart.clear()
        self.uart.write(f + bytes([sum(f) & 0xFF]))

    def _read(self, n, ms=40):
        buf, t = b"", StopWatch()
        while len(buf) < n and t.time() < ms:
            w = self.uart.waiting()
            if w:
                buf += self.uart.read(min(w, n - len(buf)))
            else:
                wait(1)
        return buf

    def _frame(self):
        t, h = StopWatch(), b""
        while t.time() < 80:
            b = self._read(1, 10)
            if not b:
                continue
            h = (h + b)[-3:]
            if h != self.HEAD:
                continue
            lc = self._read(2)
            if len(lc) < 2:
                return None
            n, c = lc[0], lc[1]
            rest = self._read(n + 1)
            if len(rest) < n + 1 or (sum(self.HEAD) + n + c + sum(rest[:-1])) & 0xFF != rest[-1]:
                return None
            return c, rest[:-1]
        return None

    def cmd(self, c, data=b""):
        self._send(c, data)
        r = self._frame()
        return r[0] if r else None

    def color_mode(self):
        return self.cmd(0x2D, bytes([4, 0])) == 0x2E              # 4 = Color Recognition

    def blocks(self):
        """[(id, x, y, w, h)] centre x / y and size in pixels, None = no answer"""
        self._send(0x21)
        r = self._frame()
        if not r or r[0] != 0x29 or len(r[1]) < 2:
            return None
        out = []
        for _ in range(r[1][0] | (r[1][1] << 8)):
            f = self._frame()
            if not f or len(f[1]) < 10:
                break
            v = [f[1][i] | (f[1][i + 1] << 8) for i in range(0, 10, 2)]
            out.append((v[4], v[0], v[1], v[2], v[3]))
        return out


class NoCamera:
    ok = False


print("starting - camera", "on port F" if USE_CAMERA else "off")
cam = HuskyLens(HUSKY_PORT, BAUD, HUSKY_POWER) if USE_CAMERA else NoCamera()
if not USE_CAMERA:
    pass
elif cam.ok:
    cam.color_mode()
    print("HuskyLens OK on port F at", cam.baud, "baud")
else:
    print("HuskyLens not answering - running on ultrasonic only. Check: 1) HuskyLens General Settings >")
    print("Protocol Type = Serial  2) T -> pin 6, R -> pin 5  3) screen on? HUSKY_POWER = the cable wire on the")
    print("converter IN+ (1 or 2), converter OUT = 5 V  4) HuskyLens UART Baudrate = 115200")


# ---------------- SENSORS ----------------
def read(eye, n=3):
    """Median of n readings (mm). 2000 = no echo = open. Below the blind zone = touching."""
    v = sorted([eye.distance() for _ in range(n)])[n // 2]
    if v <= 0:
        return 2000
    return max(v, SENSOR_MIN)


def analyse(blocks):
    """camera blocks -> err (px, + = steer right, None = can't tell), wall (black wall right ahead),
    obst (bottom row of an obstacle in the path, 0 = none), card ("L" / "R" / None), goal, hL, hR"""
    p0, p1 = 160 - PATH_HALF, 160 + PATH_HALF                  # robot's path in the picture
    L, R, hL, hR, sides = 0, 320, 0, 0, 0                      # inner edges + heights of the side walls
    full, wall_row, obst, card, goal = False, 0, 0, None, False
    for i, x, y, w, h in blocks:
        x0, x1, y1 = x - w // 2, x + w // 2, y + h // 2
        path = x0 < p1 and x1 > p0
        if i == WALL_ID and w * h >= MIN_AREA and h >= WALL_MIN_H:
            tl, tr = x0 <= EDGE, x1 >= 320 - EDGE
            if tl and tr:                                      # walls merged into one block
                full, hL, hR = True, max(hL, h), max(hR, h)
            elif tl:                                           # left wall (closer = taller)
                hL = max(hL, h)
                if x1 < p1:
                    L, sides = max(L, x1), sides | 1
            elif tr:                                           # right wall
                hR = max(hR, h)
                if x0 > p0:
                    R, sides = min(R, x0), sides | 2
            if path and ((tl and tr) or (tl and x1 >= p1) or (tr and x0 <= p0) or not (tl or tr)):
                wall_row = max(wall_row, y1)                   # wall across the path: lower = closer
        elif i == OBST_ID and w * h >= MIN_AREA:
            if path:
                obst = max(obst, y1)
        elif w >= SIGN_W:
            if i == LEFT_ID:
                card = "L"
            elif i == RIGHT_ID:
                card = "R"
            elif i == GOAL_ID:
                goal = True
    l_wall, r_wall = hL >= SIDE_H, hR >= SIDE_H
    if sides == 3 and l_wall and r_wall and not full:
        err = (L + R) / 2 - 160 + K_H * (hL - hR)              # middle of the corridor, pointing straight
    elif l_wall and not full:
        err = K_H * (hL - H_REF)                               # one wall: keep the distance
    elif r_wall and not full:
        err = K_H * (H_REF - hR)
    else:
        err = None
    return {"err": err, "wall": wall_row >= WALL_NEAR_Y, "obst": obst, "card": card, "goal": goal, "hL": hL, "hR": hR}


cam_clock = StopWatch()
cam_last = None


def cam_view(fresh=False):
    """latest camera analysis (None = no camera); while driving the camera is read every CAM_MS"""
    global cam_last
    if not cam.ok:
        return None
    if fresh or cam_clock.time() >= CAM_MS:
        cam_clock.reset()
        b = cam.blocks()
        if b is None and fresh:
            b = cam.blocks()
        cam_last = analyse(b) if b is not None else None
    return cam_last


if CALIBRATE:
    print("expected  side centred:", SIDE_CENTER, " front centred:", FRONT_CENTER,
          " side wall below:", SIDE_WALL, " front wall below:", FRONT_WALL)
    while True:
        l, f, r = read(left), read(front), read(right)
        v = cam_view(True)
        if v:
            print("L", l, " F", f, " R", r, "| camera: wall h L", v["hL"], "R", v["hR"], " err", v["err"],
                  " wall ahead", v["wall"], " obstacle row", v["obst"], " card", v["card"], " goal", v["goal"])
        else:
            print("L", l, " F", f, " R", r, "| camera: no answer")
        hub.display.number(min(99, f // 10))          # front distance in cm on the hub
        wait(300)


# ---------------- MAP ----------------
DX = [0, 1, 0, -1]           # 0 north, 1 east, 2 south, 3 west
DY = [1, 0, -1, 0]
walls = [[0] * MAZE_H for _ in range(MAZE_W)]
seen = [[False] * MAZE_H for _ in range(MAZE_W)]
goal_card = None             # goal cell found with the GOAL card
GOALS_SET = list(GOALS)      # goals as set in the code
used_cards = set()           # (x, y, heading) where a card was already followed


def inside(x, y):
    return 0 <= x < MAZE_W and 0 <= y < MAZE_H


def add_wall(x, y, d):
    walls[x][y] |= 1 << d
    nx, ny = x + DX[d], y + DY[d]
    if inside(nx, ny):
        walls[nx][ny] |= 1 << ((d + 2) % 4)


def remove_wall(x, y, d):
    """Clear a wall that was misread (outer walls always stay)."""
    nx, ny = x + DX[d], y + DY[d]
    if not inside(nx, ny):
        return
    walls[x][y] &= ~(1 << d)
    walls[nx][ny] &= ~(1 << ((d + 2) % 4))


def reset_inner_walls():
    """Forget every inside wall (keeps the outer walls) - used when the map has no way out."""
    for i in range(MAZE_W):
        for j in range(MAZE_H):
            walls[i][j] = 0
            seen[i][j] = False
    for i in range(MAZE_W):
        add_wall(i, 0, 2)
        add_wall(i, MAZE_H - 1, 0)
    for j in range(MAZE_H):
        add_wall(0, j, 3)
        add_wall(MAZE_W - 1, j, 1)


reset_inner_walls()


# ---------------- MEMORY (map saved in the hub) ----------------
MAGIC = b"MH"


def save_map():
    gx, gy = goal_card if goal_card else (255, 255)
    data = bytes([MAGIC[0], MAGIC[1], MAZE_W, MAZE_H, CELL // 10, gx, gy])
    data += bytes([(walls[x][y] & 15) | (16 if seen[x][y] else 0) for x in range(MAZE_W) for y in range(MAZE_H)])
    try:
        hub.system.storage(0, write=data)
    except Exception:
        print("this firmware has no storage - update Pybricks to save the map")


def load_map():
    global goal_card
    try:
        data = hub.system.storage(0, read=7 + MAZE_W * MAZE_H)
    except Exception:
        return False
    if data[0] != MAGIC[0] or data[1] != MAGIC[1] or data[2] != MAZE_W or data[3] != MAZE_H or data[4] != CELL // 10:
        return False
    if data[5] < MAZE_W and data[6] < MAZE_H:
        goal_card = (data[5], data[6])
        GOALS[:] = [goal_card]
    k = 7
    for x in range(MAZE_W):
        for y in range(MAZE_H):
            walls[x][y] |= data[k] & 15
            seen[x][y] = bool(data[k] & 16)
            k += 1
    return True


def forget_map():
    try:
        hub.system.storage(0, write=bytes(7))
    except Exception:
        pass


def inner_walls():
    """number of walls inside the maze (outer walls not counted)"""
    return sum(1 for x in range(MAZE_W) for y in range(MAZE_H) for d in range(4)
               if walls[x][y] & (1 << d) and inside(x + DX[d], y + DY[d])) // 2


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


HYST = 40                    # mm: reading must be this far past the threshold to REMOVE a wall


def sense(x, y, h):
    """At a cell centre: 3 ultrasonic readings (5 samples each) + one camera picture. Adds walls it sees,
    removes misread ones; an obstacle in the next cell becomes a wall. Returns (card ahead, obstacle seen)."""
    global goal_card
    v = cam_view(True)
    obst = v is not None and v["obst"] >= OBST_NEAR_Y
    for eye, d, th in ((left, (h + 3) % 4, SIDE_WALL), (front, h, FRONT_WALL), (right, (h + 1) % 4, SIDE_WALL)):
        r = read(eye, 5)
        cam_wall = d == h and (obst or (v is not None and v["wall"]))
        if r < th or cam_wall:
            add_wall(x, y, d)
        elif r > th + HYST:
            remove_wall(x, y, d)
    seen[x][y] = True
    if v is None or not USE_CARDS:
        return None, obst
    if v["goal"] and goal_card is None:
        goal_card = (x, y)
        GOALS[:] = [goal_card]
        print("GOAL card - goal is", x, y)
    return v["card"], obst


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


def back_to_cell(s):
    """Blocked after s mm: back up to the centre of the last cell reached. Returns cells driven."""
    robot.stop()
    k = int(s // CELL)
    robot.straight(-(s - k * CELL))
    return k


def cam_steer(cv, ef):
    """smoothed camera error (px) or None"""
    if cv is None or cv["err"] is None:
        return None
    return 0.6 * ef + 0.4 * cv["err"]


def drive_cells(n, vmax):
    """Drive n cells: PD wall centring (ultrasonic + camera), braking curve, front-wall correction,
    obstacle / stall stop. Returns the cells driven (n = all; fewer = blocked, robot back on a cell centre)."""
    target = n * CELL
    robot.reset()
    prev_s, prev_side, prev_which = 0, None, None
    th, ef = 0.0, 0.0
    stuck = StopWatch()
    while True:
        s = robot.distance()
        f, l, r = read(front, 1), read(left, 1), read(right, 1)
        to_go = target - s
        if f < FRONT_WALL + CELL:                      # wall ahead within reach: stop on it exactly
            to_go = min(to_go, f - FRONT_CENTER)
        if to_go <= 2:
            break
        cv = cam_view()
        if cv is not None and cv["obst"] >= OBST_STOP_Y:   # obstacle right in front
            return back_to_cell(s)
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
        c = cam_steer(cv, ef)
        if c is not None:
            ef = c
        if which:                                      # ultrasonic centring + camera help
            steer = KP * e + KH * th + (KC * c if c is not None else 0)
        elif c is not None:                            # no side wall in sonar range: camera alone
            steer = KP_CAM * c
        else:
            steer = 0
        # trapezoid speed: accelerate (DriveBase limits), cruise vmax, brake with v = sqrt(2*a*d)
        v = clamp(umath.sqrt(2 * ACCEL * max(to_go, 0)) * 0.8, V_MIN, vmax)
        robot.drive(v, clamp(steer, -MAX_STEER, MAX_STEER))
        # stall: commanded to move but wheels not turning
        if abs(robot.state()[1]) > 40:
            stuck.reset()
        elif stuck.time() > 500:
            return back_to_cell(s)
        wait(5)
    robot.stop()
    f = read(front, 3)
    if f < FRONT_WALL:                                 # final front-wall correction
        robot.straight(f - FRONT_CENTER)
    return min(n, int((robot.distance() + CELL / 2) // CELL))


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


def any_open_dir(x, y, h):
    """Right-hand rule fallback: right, straight, left, back - first side without a wall."""
    for k in (1, 0, 3, 2):
        d = (h + k) % 4
        if not walls[x][y] & (1 << d) and inside(x + DX[d], y + DY[d]):
            return d
    return (h + 2) % 4


def explore(x, y, h, targets, icon, color):
    """Map while driving to the targets. Never gives up: if the map says there is no way out
    (a misread wall), it forgets the inside walls, re-reads the sensors and keeps going."""
    hub.display.icon(icon)
    steps = 0
    while True:
        card, obst = sense(x, y, h)
        hub.light.on(Color.RED if obst else color)     # red = obstacle put on the map
        if (x, y) in targets:
            break
        dist = flood(targets)
        d = best_dir(x, y, h, dist) if dist[x][y] < 999 else None
        if d is None:
            print("no way out on the map - forgetting inside walls and re-mapping")
            hub.light.on(Color.ORANGE)
            reset_inner_walls()
            sense(x, y, h)
            dist = flood(targets)
            d = best_dir(x, y, h, dist) if dist[x][y] < 999 else None
            if d is None:
                d = any_open_dir(x, y, h)              # still blocked: follow the right wall
            hub.light.on(color)
        if card and targets is GOALS and (x, y, h) not in used_cards:   # LEFT / RIGHT card: follow it once
            cd = (h + (1 if card == "R" else 3)) % 4
            if not walls[x][y] & (1 << cd) and inside(x + DX[cd], y + DY[cd]):
                used_cards.add((x, y, h))
                d = cd
                print("card", card, "at", x, y)
        h = turn_to(h, d)
        if drive_cells(1, SEARCH_SPEED):
            x, y = x + DX[h], y + DY[h]
        else:
            add_wall(x, y, h)                          # blocked = a wall / obstacle the sensors missed
        steps += 1
        if steps > MAZE_W * MAZE_H * 6:                # wandering too long = map is wrong
            print("too many steps - re-mapping")
            reset_inner_walls()
            steps = 0
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
        k = drive_cells(n, RUN_SPEED)
        x, y = x + DX[h] * k, y + DY[h] * k
        if k < n:                                      # obstacle / missed wall: map it, re-plan
            add_wall(x, y, h)
            dist = flood(GOALS)
    return x, y, h


def path_dirs(x, y, dist):
    """List of headings, one per cell, from (x, y) down the flood-fill distances to the goal."""
    dirs = []
    h = None
    while (x, y) not in GOALS:
        d = best_dir(x, y, h if h is not None else 0, dist)
        if d is None or dist[x + DX[d]][y + DY[d]] >= dist[x][y]:
            return None
        dirs.append(d)
        x, y, h = x + DX[d], y + DY[d], d
    return dirs


def drive_mm(dist_mm, vmax, stop_end):
    """Drive a distance with wall centring (ultrasonic + camera); keeps rolling at the end if stop_end is False.
    Returns None when done, or the distance driven if an obstacle stopped it."""
    robot.reset()
    ef = 0.0
    while True:
        s = robot.distance()
        to_go = dist_mm - s
        if to_go <= 2:
            break
        f, l, r = read(front, 1), read(left, 1), read(right, 1)
        if f < FRONT_CENTER + 5:
            break
        cv = cam_view()
        if cv is not None and cv["obst"] >= OBST_STOP_Y:
            robot.stop()
            return s
        if l < SIDE_WALL and r < SIDE_WALL:
            e, which = (r - l) / 2, True
        elif r < SIDE_WALL:
            e, which = r - SIDE_CENTER, True
        elif l < SIDE_WALL:
            e, which = SIDE_CENTER - l, True
        else:
            e, which = 0, False
        c = cam_steer(cv, ef)
        if c is not None:
            ef = c
        if which:
            steer = KP * e + (KC * c if c is not None else 0)
        elif c is not None:
            steer = KP_CAM * c
        else:
            steer = 0
        end_v = V_MIN if stop_end else ARC_SPEED
        v = clamp(umath.sqrt(end_v * end_v + 2 * ACCEL * max(to_go, 0)) * 0.9, end_v, vmax)   # v^2 = v_end^2 + 2*a*d
        robot.drive(v, clamp(steer, -MAX_STEER, MAX_STEER))
        wait(5)
    if stop_end:
        robot.stop()
    return None


def smooth_run(x, y, h):
    """Remembered map: shortest path without stopping, corners as arcs of radius CELL/2.
    Returns (x, y, h, done); done = False -> an obstacle stopped it, robot is on cell (x, y) facing h."""
    dist = flood(GOALS, known_only=True)
    dirs = path_dirs(x, y, dist)
    if not dirs:
        return None
    hub.display.icon(Icon.FULL)
    runs = []                                            # [heading, cells]
    for d in dirs:
        if runs and runs[-1][0] == d:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    h = turn_to(h, runs[0][0])
    robot.settings(straight_speed=ARC_SPEED)              # arcs use this speed (set while stopped)
    for i, (d, n) in enumerate(runs):
        length = n * CELL
        if i > 0:
            length -= CELL / 2                           # came out of an arc half way into the cell
        last = i == len(runs) - 1
        if not last:
            length -= CELL / 2                           # start the next arc half a cell early
        if length > 0:
            s = drive_mm(length, SMOOTH_SPEED, last)
            if s is not None:                            # obstacle: back to a cell centre, map it
                off = s + (CELL / 2 if i > 0 else 0)
                k = int(off // CELL)
                robot.straight(-(off - k * CELL))
                x, y = x + DX[d] * k, y + DY[d] * k
                add_wall(x, y, d)
                robot.settings(straight_speed=SEARCH_SPEED)
                return x, y, d, False
        if not last:
            diff = (runs[i + 1][0] - d) % 4
            angle = 90 if diff == 1 else -90
            robot.curve(CELL / 2, angle, Stop.NONE)      # arc turn without stopping
        x, y = x + DX[d] * n, y + DY[d] * n
    robot.stop()
    robot.settings(straight_speed=SEARCH_SPEED)
    f = read(front, 3)
    if f < FRONT_WALL:
        robot.straight(f - FRONT_CENTER)
    return x, y, runs[-1][0], True


# ---------------- MAIN ----------------
print("side centred", SIDE_CENTER, "| front centred", FRONT_CENTER, "| side wall <", SIDE_WALL, "| front wall <", FRONT_WALL)
if SIDE_CENTER < 40 or FRONT_CENTER < 40:
    print("WARNING: robot too wide for this CELL - sensors would be closer than 4 cm (ultrasonic blind zone)")


def main():
    global goal_card
    if Button.LEFT in hub.buttons.pressed():
        forget_map()
        print("map forgotten")
    remembered = load_map()
    if remembered and inner_walls() == 0:              # saved from a run where no wall was seen (test on a table)
        print("saved map has no walls - forgetting it and searching")
        reset_inner_walls()
        goal_card = None
        GOALS[:] = GOALS_SET
        remembered = False
    hub.light.on(Color.GREEN)
    wait(1000)
    x, y, h = START[0], START[1], 0
    if remembered and path_dirs(x, y, flood(GOALS, known_only=True)):
        print("map remembered - smooth run")
        print_map()
        hub.light.on(Color.CYAN)
        res = smooth_run(x, y, h)
        if res and res[3]:
            hub.light.on(Color.BLUE)
            hub.display.icon(Icon.HAPPY)
            print("done at", res[0], res[1])
            wait(5000)
            return
        if res:
            x, y, h = res[0], res[1], res[2]
            print("obstacle on the remembered path - searching again from", x, y)
    x, y, h = explore(x, y, h, GOALS, Icon.ARROW_UP, Color.GREEN)          # 1. search
    save_map()
    x, y, h = explore(x, y, h, [START], Icon.ARROW_DOWN, Color.YELLOW)     # 2. back to start
    h = turn_to(h, 0)
    save_map()
    print_map()
    hub.light.on(Color.MAGENTA)
    wait(1500)
    x, y, h = speed_run(x, y, h)                                           # 3. speed run
    save_map()
    hub.light.on(Color.BLUE)
    hub.display.icon(Icon.HAPPY)
    print("done at", x, y, "- map saved, next run will be smooth")
    wait(5000)


main()
