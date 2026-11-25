# ================================================================
#  HuskyLens LINK TEST - Pybricks, SPIKE Prime (camera on port F)
#  Sends the HuskyLens "knock" at every baud rate and prints what comes back.
#  Last line tells you what to fix. Hub light: yellow = testing, green = OK, red = no answer.
#  Wiring: HuskyLens T -> pin 6 (hub RX), R -> pin 5 (hub TX). Power: LM2596 IN+ / IN- on cable pins 1 + 2,
#  LM2596 OUT set to 5.0 V -> HuskyLens + / -. POWER_PIN = the cable wire on IN+ (Pybricks v4 switches it on).
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port, Color
from pybricks.tools import wait

PORT = Port.F
POWER_PIN = 1                 # cable wire on the converter IN+: 1 = pin 1, 2 = pin 2, 0 = camera has its own power
KNOCK = bytes([0x55, 0xAA, 0x11, 0x00, 0x2C, 0x3C])       # header, length 0, command knock, checksum
OK = b"\x55\xaa\x11\x00\x2e"                              # HuskyLens "OK" answer

hub = PrimeHub()
hub.light.on(Color.YELLOW)
try:
    from pybricks import version
    print("firmware:", version)
except ImportError:
    print("firmware: old Pybricks - update it at code.pybricks.com")
print("step 1: opening port F, power on pin", POWER_PIN)
wait(300)
try:
    uart = UARTDevice(PORT, 9600, timeout=100, power_pin=POWER_PIN)
except TypeError:
    print("this Pybricks has no power_pin - update it to v4")
    uart = UARTDevice(PORT, 9600, timeout=100)
print("waiting 3 s - the HuskyLens screen should light up now")
wait(3000)
print("step 2: port F open - asking the HuskyLens")
found, anything, counts = None, False, {}
for rnd in range(4):
    for baud in (9600, 115200, 1000000):
        uart.set_baudrate(baud)
        uart.clear()
        uart.write(KNOCK)
        wait(150)
        n = uart.waiting()
        data = uart.read(n) if n else b""
        anything = anything or n > 0
        counts[baud] = counts.get(baud, 0) + n
        print("  baud", baud, "->", n, "bytes", " ".join("%02x" % b for b in data[:12]))
        if data.find(OK) >= 0:
            found = baud
            break
    if found:
        break
    wait(500)
if found:
    hub.light.on(Color.GREEN)
    print("OK: HuskyLens answers at", found, "baud - the maze programs find it by themselves")
elif counts.get(1000000) and not counts.get(9600) and not counts.get(115200):
    hub.light.on(Color.ORANGE)
    print("Only 00 noise: is the HuskyLens screen on? If not: POWER_PIN = the other wire (1 <-> 2), LM2596 OUT 5 V.")
    print("If the screen is on: HuskyLens General Settings > UART Baudrate = 115200, then run this test again.")
elif anything:
    hub.light.on(Color.ORANGE)
    print("Bytes arrive but no HuskyLens answer: HuskyLens General Settings > Protocol Type = Serial, restart it")
else:
    hub.light.on(Color.RED)
    print("Nothing arrives: 1) HuskyLens screen on? (POWER_PIN, LM2596 OUT 5 V)  2) T -> pin 6, R -> pin 5")
    print("3) Protocol Type = Serial  4) cable really on port F")
wait(2000)
