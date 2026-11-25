# ================================================================
#  HuskyLens LINK TEST - Pybricks, SPIKE Prime (camera on port F)
#  Sends the HuskyLens "knock" at every baud rate and prints what comes back.
#  Last line tells you what to fix. Hub light: yellow = testing, green = OK, red = no answer.
#  Wiring: HuskyLens T -> pin 6 (hub RX), R -> pin 5 (hub TX), - -> pin 3,
#          + -> 5 V power bank + ONLY (power bank - to pin 3). Nothing on pin 4 or pins 1-2.
# ================================================================
from pybricks.hubs import PrimeHub
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port, Color
from pybricks.tools import wait

PORT = Port.F
KNOCK = bytes([0x55, 0xAA, 0x11, 0x00, 0x2C, 0x3C])       # header, length 0, command knock, checksum
OK = b"\x55\xaa\x11\x00\x2e"                              # HuskyLens "OK" answer

hub = PrimeHub()
hub.light.on(Color.YELLOW)
try:
    from pybricks import version
    print("firmware:", version)
except ImportError:
    print("firmware: old Pybricks - update it at code.pybricks.com")
print("step 1: opening port F")
wait(300)
uart = UARTDevice(PORT, 9600, timeout=100)
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
    print("The HuskyLens is set to 1000000 baud - too fast for the hub port (its answer arrives as 00 00 ...).")
    print("On the HuskyLens: General Settings > UART Baudrate = 115200, save, restart it, run this test again.")
elif anything:
    hub.light.on(Color.ORANGE)
    print("Bytes arrive but no HuskyLens answer: HuskyLens General Settings > Protocol Type = Serial, restart it")
else:
    hub.light.on(Color.RED)
    print("Nothing arrives: 1) T -> pin 6, R -> pin 5  2) HuskyLens + on the 5 V power bank (screen on)")
    print("3) power bank - joined to pin 3  4) wires really on port F")
wait(2000)
