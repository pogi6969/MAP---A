# ================================================================
#  HuskyLens LINK TEST - Pybricks, SPIKE Prime (camera on port F)
#  Sends the HuskyLens "knock" at every baud rate and prints what comes back.
#  Last line tells you what to fix.
# ================================================================
from pybricks.iodevices import UARTDevice
from pybricks.parameters import Port
from pybricks.tools import wait

PORT = Port.F
KNOCK = bytes([0x55, 0xAA, 0x11, 0x00, 0x2C, 0x3C])       # header, length 0, command knock, checksum
OK = b"\x55\xaa\x11\x00\x2e"                              # HuskyLens "OK" answer

uart = UARTDevice(PORT, 9600, timeout=100)
found, anything = None, False
for rnd in range(4):
    for baud in (9600, 115200, 1000000):
        uart.set_baudrate(baud)
        uart.clear()
        uart.write(KNOCK)
        wait(150)
        n = uart.waiting()
        data = uart.read(n) if n else b""
        anything = anything or n > 0
        print("baud", baud, "->", n, "bytes", " ".join("%02x" % b for b in data[:12]))
        if data.find(OK) >= 0:
            found = baud
            break
    if found:
        break
    wait(500)
if found:
    print("OK: HuskyLens answers at", found, "baud - the maze programs find it by themselves")
elif anything:
    print("Bytes arrive but no HuskyLens answer: HuskyLens General Settings > Protocol Type = Serial, restart it")
else:
    print("Nothing arrives: 1) swap the T and R wires  2) HuskyLens + on 5 V (screen must be on)")
    print("3) power bank GND joined to pin 3  4) wires really on port F")
