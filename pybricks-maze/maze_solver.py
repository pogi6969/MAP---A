# SPIKE Prime maze robot (Pybricks) - fast, no scanning
# drive forward until an obstacle -> stop, read left + right sensors (robot stays put)
# -> turn 90 deg to the side with more space -> forward again
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
WHEEL = 56
AXLE = 112                 # distance between the wheels: bigger number = turns more
FRONT_STOP = 100           # obstacle closer than this in front = stop
SIDE_MIN = 60              # side wall closer than this while driving = steer away
OPEN = 200                 # side with more space than this = open path
SPEED = 400                # straight speed mm/s
TURN_SPEED = 300           # turning speed deg/s

hub = PrimeHub()
left_motor = Motor(LEFT_MOTOR)
right_motor = Motor(RIGHT_MOTOR, Direction.COUNTERCLOCKWISE)
robot = DriveBase(left_motor, right_motor, WHEEL, AXLE)
robot.settings(straight_speed=SPEED, straight_acceleration=800, turn_rate=TURN_SPEED, turn_acceleration=1200)

front = UltrasonicSensor(FRONT_EYE)
right = UltrasonicSensor(RIGHT_EYE)
left = UltrasonicSensor(LEFT_EYE)

hub.light.on(Color.GREEN)
hub.display.icon(Icon.ARROW_UP)

while True:
    if front.distance() > FRONT_STOP:          # path ahead: go
        r = right.distance()
        l = left.distance()
        steer = 0
        if r < SIDE_MIN:
            steer = -40                        # too close to right wall
        elif l < SIDE_MIN:
            steer = 40                         # too close to left wall
        robot.drive(SPEED, steer)
        continue

    robot.stop()                               # obstacle: stay put and read the sides
    r = right.distance()
    l = left.distance()
    if r >= l and r > OPEN:
        hub.display.icon(Icon.ARROW_RIGHT)
        robot.turn(90)
    elif l > OPEN:
        hub.display.icon(Icon.ARROW_LEFT)
        robot.turn(-90)
    else:
        hub.display.icon(Icon.ARROW_DOWN)      # dead end
        robot.turn(180)
    hub.display.icon(Icon.ARROW_UP)
