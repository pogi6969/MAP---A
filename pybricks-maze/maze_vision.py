# ================================================================
#  SPIKE Prime VISION MAZE robot - the HuskyLens camera drives (Pybricks)        BLACK WALLS
#  HuskyLens: Color Recognition, Learn Multiple ON, learn in this order:
#     ID1 = BLACK wall   ID2 = OBSTACLE colour   ID3 = TURN LEFT card   ID4 = TURN RIGHT card   ID5 = GOAL card
#     (IDs 2-5 optional). Protocol Type = Serial 115200. Camera at the front, level, looking straight ahead.
#  Every frame (picture 320 x 240):
#    STRAIGHT     left + right wall blocks -> steer until both are the same size and the gap is in the middle
#    AVOID WALLS  wall block bigger on one side = too close -> steer away (one wall only: keep it at H_REF)
#    OBSTACLE     obstacle ahead -> steer round it if the gap beside it is wide enough, else stop + turn
#    WALL AHEAD   wall low in the picture (= close) -> stop + turn
#    WHERE        turn card first, then the RULE side, then the other side, else U-turn
#    WHEN         opening on the wanted side -> drive to its middle -> turn 90
#  Ultrasonic C (front), A (right), D (left) help: exact stop point + side openings.
#  USE_SONAR = False = camera only (then mount the camera above the wall tops, tilted down, CAM_HIGH = True).
#  Wiring: HuskyLens T -> port F pin 5, R -> pin 6, GND -> pin 3, + to a 5 V power bank (its GND to pin 3 too).
#  Tuning: LOOK_ONLY = True -> robot stands still and prints what the camera sees.
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, UltrasonicSensor
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port, Direction, Color, Icon
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

# ---------------- PORTS ----------------
LEFT_MOTOR, RIGHT_MOTOR = Port.B, Port.E
HUSKY_PORT, BAUD = Port.F, 115200       # BAUD = HuskyLens Protocol Type
FRONT_EYE, RIGHT_EYE, LEFT_EYE = Port.C, Port.A, Port.D
USE_SONAR = True                        # missing ultrasonic sensors are skipped automatically
LOOK_ONLY = False                       # True = stand still and print what the camera sees

# ---------------- CAMERA (pixels) ----------------
WALL_ID, OBST_ID, LEFT_ID, RIGHT_ID, GOAL_ID = 1, 2, 3, 4, 5
CAM_HIGH = False      # True = camera above the wall tops looking down: top edge of the walls = distance
H_REF = 180           # side wall block height (hL / hR) with the robot in the middle of a corridor
NEAR_Y = 190          # wall / obstacle ahead whose bottom edge is below this row = close -> stop
FULL_NEAR_Y = 236     # all walls seen as one block: close when that block reaches this row
TOP_NEAR_Y = 150      # (CAM_HIGH) wall top edge below this row = close
AVOID_Y = 140         # obstacle bottom edge below this row: steer round it, slow down
PATH_HALF = 60        # half the robot width in the picture
MIN_GAP = 110         # free width needed to drive past something
MIN_AREA = 300        # smaller blocks are noise (shadows)
EDGE = 8              # block this close to the picture side touches it
SIGN_W = 35           # card at least this wide counts
KP_CAM, K_H = 0.45, 0.5  # steering per px of error, weight of the left / right wall size difference
RULE = "R"            # no card: "R" = right-hand rule, "L" = left-hand rule
SIDE_H = H_REF * 6 // 10  # side block at least this tall = wall beside the robot

# ---------------- ROBOT (mm, deg) ----------------
WHEEL, AXLE = 56, 112   # bigger AXLE = turns more
SPEED, SLOW = 320, 110  # mm/s
TURN_SPEED = 300        # deg/s
MAX_STEER = 90          # deg/s
FRONT_STOP = 90         # ultrasonic stop distance
SLOW_DIST = 260         # ultrasonic: slow down from here
OPEN = 240              # side ultrasonic above this = opening
SIDE_MID = 80           # side ultrasonic distance in the middle
KP_SONAR = 1.2          # deg/s per mm off the middle (when the camera can't tell)
SONAR_TURN_AT = 95      # side ultrasonic sees an opening -> drive this far, then turn
CAM_TURN_AT = 230       # camera sees an opening -> drive this far, then turn (the camera looks ahead)
ENTER = 140             # after a turn: ignore openings for this distance

hub = PrimeHub()
robot = DriveBase(Motor(LEFT_MOTOR), Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE), WHEEL, AXLE)
robot.settings(straight_speed=SPEED, straight_acceleration=1200, turn_rate=TURN_SPEED, turn_acceleration=1500)
OTHER = {"L": "R", "R": "L"}


def eye_at(port):
    if not USE_SONAR:
        return None
    try:
        return UltrasonicSensor(port)
    except OSError:
        print("no ultrasonic on", port)
        return None


front, left, right = eye_at(FRONT_EYE), eye_at(LEFT_EYE), eye_at(RIGHT_EYE)


def us(eye):
    """ultrasonic distance in mm, None if that sensor is not fitted"""
    if eye is None:
        return None
    v = eye.distance()
    return 2000 if v <= 0 else v


# ================= HuskyLens (UART protocol) =================
class HuskyLens:
    HEAD = b"\x55\xaa\x11"
    BAUDS = (115200, 9600, 1000000)                            # every HuskyLens "UART Baudrate" setting

    def __init__(self, port, baud):
        self.ok, self.baud = False, None
        try:
            self.uart = UARTDevice(port, baud, timeout=50)
        except Exception as e:
            print("HuskyLens port error:", e)
            return
        order = [baud] + [b for b in self.BAUDS if b != baud]
        for _ in range(6):                                     # camera needs about 3 s to start up
            for b in order:
                try:
                    self.uart.set_baudrate(b)
                except AttributeError:
                    self.uart = UARTDevice(port, b, timeout=50)
                if self.cmd(0x2C) == 0x2E:                     # knock -> OK
                    self.ok, self.baud = True, b
                    return
            wait(400)

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


# ================= VISION MATHS =================
def analyse(blocks):
    """camera blocks -> err (px, + = steer right / None), ahead (row of the closest thing in the path),
    blocked, obst, full, l_wall, r_wall, card, goal (+ L R hL hR for LOOK_ONLY)"""
    p0, p1 = 160 - PATH_HALF, 160 + PATH_HALF                  # robot's path in the picture
    L, R, hL, hR, sides = 0, 320, 0, 0, 0                      # inner edges + heights of the side walls
    full = obst = goal = False
    ahead, card, cuts = 0, None, []
    for i, x, y, w, h in blocks:
        x0, x1, y0, y1 = x - w // 2, x + w // 2, y - h // 2, y + h // 2
        path = x0 < p1 and x1 > p0
        if i == WALL_ID and w * h >= MIN_AREA:
            tl, tr = x0 <= EDGE, x1 >= 320 - EDGE
            if tl and tr:                                      # walls merged into one block over the picture
                full, hL, hR = True, max(hL, h), max(hR, h)
            elif tl:                                           # left wall (closer = taller block)
                hL = max(hL, h)
                if x1 < p1:
                    L, sides = max(L, x1), sides | 1
            elif tr:                                           # right wall
                hR = max(hR, h)
                if x0 > p0:
                    R, sides = min(R, x0), sides | 2
            if CAM_HIGH:
                row = y0 * NEAR_Y // TOP_NEAR_Y                # top edge of the walls = distance
            elif (tl and tr) or (tl and x1 >= p1) or (tr and x0 <= p0):
                row = NEAR_Y if y1 >= FULL_NEAR_Y else 0       # merged block over the path: close when it reaches the bottom
            elif tl or tr:
                row = 0                                        # side wall: steering handles it
            else:
                row = y1                                       # wall ahead: bottom edge = distance
            if path and row:
                ahead = max(ahead, row)
                if row >= NEAR_Y:
                    cuts.append((x0, x1))
        elif i == OBST_ID and w * h >= MIN_AREA:
            if path:
                ahead = max(ahead, y1)
                if y1 >= AVOID_Y:
                    cuts.append((x0, x1))
                    obst = True
        elif w >= SIGN_W:
            if i == LEFT_ID:
                card = "L"
            elif i == RIGHT_ID:
                card = "R"
            elif i == GOAL_ID:
                goal = True
    free = [(L, R)] if R > L else []                           # free gaps = corridor minus things ahead
    for c0, c1 in cuts:
        nxt = []
        for a, b in free:
            if c1 <= a or c0 >= b:
                nxt.append((a, b))
            else:
                if c0 > a:
                    nxt.append((a, c0))
                if c1 < b:
                    nxt.append((c1, b))
        free = nxt
    best = max(free, key=lambda g: (g[1] - g[0], -abs(g[0] + g[1] - 320))) if free else (160, 160)
    l_wall, r_wall = hL >= SIDE_H, hR >= SIDE_H
    if cuts:
        err = (best[0] + best[1]) / 2 - 160                    # round the obstacle / away from the wall
    elif sides == 3 and l_wall and r_wall and not full:
        err = (L + R) / 2 - 160 + K_H * (hL - hR)              # middle of the corridor, pointing straight
    elif l_wall and not full:
        err = K_H * (hL - H_REF)                               # one wall: keep the distance
    elif r_wall and not full:
        err = K_H * (H_REF - hR)
    else:
        err = None                                             # camera can't tell: ultrasonic / straight
    return {"err": err, "ahead": ahead, "blocked": ahead >= NEAR_Y and best[1] - best[0] < MIN_GAP,
            "obst": obst, "full": full, "l_wall": l_wall, "r_wall": r_wall, "card": card, "goal": goal,
            "L": L, "R": R, "hL": hL, "hR": hR}


# ================= MOVES =================
def sonar_steer():
    l, r = us(left), us(right)
    if l is None or r is None:
        return 0
    if l < OPEN and r < OPEN:
        e = (r - l) / 2
    elif r < OPEN:
        e = r - SIDE_MID
    elif l < OPEN:
        e = SIDE_MID - l
    else:
        return 0
    return KP_SONAR * e


def side_open(v, sd):
    d = us(left if sd == "L" else right)
    if d is not None:
        return d > OPEN                                        # ultrasonic on that side
    mine, other = (v["l_wall"], v["r_wall"]) if sd == "L" else (v["r_wall"], v["l_wall"])
    return other and not mine                                  # camera: that wall gone, the other still seen


def turn(angle, icon):
    robot.stop()
    hub.display.icon(icon)
    robot.turn(angle)
    hub.display.icon(Icon.ARROW_UP)


def turn_side(sd):
    if sd == "R":
        turn(90, Icon.ARROW_RIGHT)
    else:
        turn(-90, Icon.ARROW_LEFT)


def go(mm, speed=SPEED):
    """straight for mm, stops early at a wall"""
    start = robot.distance()
    while robot.distance() - start < mm:
        f = us(front)
        if f is not None and f < FRONT_STOP:
            break
        robot.drive(speed, 0)
        wait(10)
    robot.stop()


def clear_ahead():
    wait(150)                                                  # let the picture settle
    b = cam.blocks() or cam.blocks()
    if b is None:
        return False
    v = analyse(b)
    f = us(front)
    return not v["blocked"] and v["ahead"] < NEAR_Y and (f is None or f > OPEN)


def choose_turn(want):
    order = [want, OTHER[want]] if want else [RULE, OTHER[RULE]]
    if us(left) is not None and us(right) is not None:         # ultrasonic: no looking needed
        for sd in order:
            if side_open(None, sd):
                turn_side(sd)
                return
        turn(180, Icon.ARROW_DOWN)
        return
    turn_side(order[0])                                        # camera only: turn and look
    if clear_ahead():
        return
    turn(180, Icon.ARROW_DOWN)                                 # now facing the other side
    if clear_ahead():
        return
    turn_side(order[1])                                        # dead end: back the way it came


# ================= MAIN =================
cam = HuskyLens(HUSKY_PORT, BAUD)
if not cam.ok:
    hub.light.on(Color.RED)
    print("HuskyLens not answering - check: Protocol Type = Serial, T -> pin 5 / R -> pin 6 (swap if silent),")
    print("5 V power with GND joined to pin 3. Run husky_test.py to see what comes back.")
    raise SystemExit
cam.color_mode()
hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)
wait(800)

pending = None            # card seen ("L" / "R"): used at the next opening or wall
seen = 0                  # frames in a row the wanted side looked open
ignore_to = 0             # openings ignored until this travelled distance (just turned)
ef = 0                    # smoothed camera error
lost, show = StopWatch(), StopWatch()

while True:
    blocks = cam.blocks()
    if blocks is None:                                         # camera hiccup: keep going briefly
        if lost.time() > 400:
            robot.stop()
        wait(5)
        continue
    lost.reset()
    v = analyse(blocks)
    f = us(front)

    if LOOK_ONLY:                                              # tuning: push the robot around by hand
        if show.time() > 300:
            show.reset()
            print(len(blocks), "blocks | left wall", v["L"], "h", v["hL"], "| right wall", v["R"], "h", v["hR"],
                  "| ahead", v["ahead"], "blocked", v["blocked"], "| err", v["err"], "| card", v["card"],
                  "goal", v["goal"], "| sonar F L R", f, us(left), us(right))
        wait(20)
        continue

    if v["goal"]:                                              # GOAL card
        robot.stop()
        hub.light.on(Color.BLUE)
        hub.display.icon(Icon.HAPPY)
        hub.speaker.beep(1000, 300)
        print("goal")
        break
    if v["card"]:
        pending = v["card"]
        hub.light.on(Color.MAGENTA)

    # ---- WALL / OBSTACLE AHEAD -> where to turn ----
    near_wall = f is not None and f < FRONT_STOP
    cam_block = v["blocked"] and (v["obst"] or f is None or f < SLOW_DIST)   # ultrasonic can overrule a camera wall
    if near_wall or cam_block:
        robot.stop()
        if not near_wall and not v["obst"] and f is not None:
            go(SLOW_DIST, SLOW)                                # camera saw the wall early: roll up to the stop point
        wait(80)
        b = cam.blocks()
        card = analyse(b)["card"] if b else None
        choose_turn(card or pending)                           # card on the wall in front wins
        pending, seen, ef = None, 0, 0
        ignore_to = robot.distance() + ENTER
        hub.light.on(Color.GREEN)
        continue

    # ---- WHEN TO TURN: opening on the wanted side ----
    side = pending or RULE
    if robot.distance() > ignore_to:
        seen = seen + 1 if side_open(v, side) else 0
        if seen >= 3:
            go(CAM_TURN_AT if us(left if side == "L" else right) is None else SONAR_TURN_AT)
            turn_side(side)
            pending, seen, ef = None, 0, 0
            ignore_to = robot.distance() + ENTER
            hub.light.on(Color.GREEN)
            continue

    # ---- STRAIGHT + AVOID WALLS ----
    if v["err"] is not None:
        ef = 0.6 * ef + 0.4 * v["err"]                         # smoothed = no wobble
        steer = KP_CAM * ef
    else:
        steer = sonar_steer()
    spd = SPEED
    if v["ahead"] > AVOID_Y:                                   # something ahead: slow down
        spd = max(SLOW, SPEED - (SPEED - SLOW) * (v["ahead"] - AVOID_Y) // (NEAR_Y - AVOID_Y))
    if f is not None and f < SLOW_DIST:
        spd = min(spd, max(SLOW, SPEED * (f - FRONT_STOP) // (SLOW_DIST - FRONT_STOP)))
    robot.drive(spd, max(-MAX_STEER, min(MAX_STEER, steer)))
    wait(5)

robot.stop()
wait(3000)
