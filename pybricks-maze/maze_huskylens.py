# ================================================================
#  SPIKE Prime MAZE robot + HuskyLens camera  (Pybricks)
#  - drives fast between walls with 3 ultrasonic sensors (centred, no scanning)
#  - at every wall in front it asks the HuskyLens what it sees:
#      a learned SIGN (AprilTag or colour) tells it what to do (left / right / turn around / stop at goal)
#      no sign -> right-hand rule from the side sensors (right, else left, else turn around)
#  - a sign seen early while driving is remembered for the next wall
#  HuskyLens: set "Protocol Type" to Serial 9600 (or 115200 and change BAUD), choose the
#  Tag Recognition (or Color Recognition) algorithm and LEARN the signs: ID1, ID2, ID3, ID4.
#  Wiring (UART): HuskyLens T -> hub port pin 6 (hub RX), R -> pin 5 (hub TX), GND -> pin 3,
#  power the HuskyLens from 5 V (power bank / regulator) with GND shared - the hub port's 3.3 V is too weak.
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

# ---------------- PORTS ----------------
LEFT_MOTOR = Port.B
RIGHT_MOTOR = Port.E
FRONT_EYE = Port.C
RIGHT_EYE = Port.A
LEFT_EYE = Port.D
HUSKY_PORT = Port.F
BAUD = 9600                  # must match HuskyLens Settings > Protocol Type

# ---------------- SIGNS (learned IDs on the HuskyLens) ----------------
ALGORITHM = "TAG"            # "TAG" = AprilTags (most reliable), "COLOR" = coloured cards
SIGNS = {1: "L", 2: "R", 3: "U", 4: "STOP"}   # ID -> left, right, U-turn, goal
SIGN_NEAR_W = 40             # sign wider than this many pixels (of 320) = close enough to trust

# ---------------- ROBOT (mm, deg) ----------------
WHEEL = 56
AXLE = 112                   # bigger = turns more
SPEED = 380                  # mm/s
TURN_SPEED = 300             # deg/s
FRONT_STOP = 90              # stop this far from a front wall
SIDE_CENTER = 80             # side distance when centred
WALL = 180                   # side reading below this = wall
OPEN = 240                   # side reading above this = open
KP = 1.4                     # steering per mm off-centre
CAM_EVERY = 150              # ms between camera checks while driving

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, straight_acceleration=1200, turn_rate=TURN_SPEED, turn_acceleration=1500)
front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)


# ================= HuskyLens (UART protocol) =================
class HuskyLens:
    ALGOS = {"FACE": 0, "TRACK": 1, "OBJECT": 2, "LINE": 3, "COLOR": 4, "TAG": 5, "CLASSIFY": 6}
    HEAD = b"\x55\xaa\x11"

    def __init__(self, port, baud):
        self.uart = UARTDevice(port, baud, timeout=50)
        self.ok = self.knock()

    def _send(self, cmd, data=b""):
        f = self.HEAD + bytes([len(data), cmd]) + data
        self.uart.clear()
        self.uart.write(f + bytes([sum(f) & 0xFF]))       # last byte = checksum

    def _read(self, n, ms=60):
        buf = b""
        t = StopWatch()
        while len(buf) < n and t.time() < ms:
            w = self.uart.waiting()
            if w:
                buf += self.uart.read(min(w, n - len(buf)))
            else:
                wait(1)
        return buf

    def _frame(self):
        """next reply frame -> (command, data) or None"""
        t = StopWatch()
        h = b""
        while t.time() < 120:
            b = self._read(1, 20)
            if not b:
                continue
            h = (h + b)[-3:]
            if h != self.HEAD:
                continue
            lc = self._read(2)
            if len(lc) < 2:
                return None
            n, cmd = lc[0], lc[1]
            rest = self._read(n + 1)
            if len(rest) < n + 1 or (sum(self.HEAD) + n + cmd + sum(rest[:-1])) & 0xFF != rest[-1]:
                return None
            return cmd, rest[:-1]
        return None

    def knock(self):
        self._send(0x2C)
        r = self._frame()
        return bool(r) and r[0] == 0x2E

    def algorithm(self, name):
        a = self.ALGOS[name]
        self._send(0x2D, bytes([a & 0xFF, a >> 8]))
        r = self._frame()
        return bool(r) and r[0] == 0x2E

    def objects(self):
        """list of (id, x, y, w, h) for blocks; arrows come as (id, x0, y0, x1, y1). Screen is 320 x 240."""
        self._send(0x20)
        r = self._frame()
        if not r or r[0] != 0x29 or len(r[1]) < 2:
            return []
        count = r[1][0] | (r[1][1] << 8)
        out = []
        for _ in range(count):
            f = self._frame()
            if not f or len(f[1]) < 10:
                break
            v = [f[1][i] | (f[1][i + 1] << 8) for i in range(0, 10, 2)]
            out.append((v[4], v[0], v[1], v[2], v[3]))
        return out


def read(eye, n=3):
    v = sorted([eye.distance() for _ in range(n)])[n // 2]   # median filter
    return 2000 if v <= 0 else v                              # 2000 = nothing in range


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def see_sign(cam, near_only=True):
    """biggest learned sign in view -> action letter or None"""
    if not cam or not cam.ok:
        return None
    best, best_w = None, 0
    for sid, x, y, w, h in cam.objects():
        if sid in SIGNS and w > best_w and (w >= SIGN_NEAR_W or not near_only):
            best, best_w = SIGNS[sid], w
    return best


def turn(angle, icon):
    robot.stop()
    hub.display.icon(icon)
    robot.turn(angle)
    hub.display.icon(Icon.ARROW_UP)


def drive_to_wall(cam):
    """drive centred until a wall is in front; returns a sign seen on the way (or None)"""
    pending = None
    t = StopWatch()
    while True:
        f = read(front, 1)
        if f < FRONT_STOP:
            break
        l, r = read(left, 1), read(right, 1)
        if l < WALL and r < WALL:
            e = (r - l) / 2
        elif r < WALL:
            e = r - SIDE_CENTER
        elif l < WALL:
            e = SIDE_CENTER - l
        else:
            e = 0
        v = SPEED if f > 300 else max(120, SPEED * (f - FRONT_STOP) / (300 - FRONT_STOP))   # slow down near the wall
        robot.drive(v, clamp(KP * e, -80, 80))
        if cam and cam.ok and t.time() > CAM_EVERY:      # look ahead for signs without stopping
            t.reset()
            s = see_sign(cam)
            if s:
                pending = s
                hub.light.on(Color.MAGENTA)
        wait(5)
    robot.stop()
    return pending


# ================= MAIN =================
cam = HuskyLens(HUSKY_PORT, BAUD)
if cam.ok:
    cam.algorithm(ALGORITHM)
    print("HuskyLens OK -", ALGORITHM)
else:
    print("HuskyLens not answering - check wiring, 5 V power, Protocol Type = Serial", BAUD, "- using sensors only")
hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)
wait(800)

while True:
    pending = drive_to_wall(cam)
    sign = see_sign(cam) or pending                       # sign on the wall in front wins
    l_open = read(left) > OPEN
    r_open = read(right) > OPEN
    hub.light.on(Color.GREEN)
    if sign == "STOP":
        hub.display.icon(Icon.HAPPY)
        hub.light.on(Color.BLUE)
        print("goal sign - finished")
        break
    if sign == "L" and l_open:
        turn(-90, Icon.ARROW_LEFT)
    elif sign == "R" and r_open:
        turn(90, Icon.ARROW_RIGHT)
    elif sign == "U":
        turn(180, Icon.ARROW_DOWN)
    elif r_open:                                          # no usable sign: right-hand rule
        turn(90, Icon.ARROW_RIGHT)
    elif l_open:
        turn(-90, Icon.ARROW_LEFT)
    else:
        turn(180, Icon.ARROW_DOWN)

robot.stop()
wait(3000)
