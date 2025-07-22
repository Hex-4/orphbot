
import board
import digitalio
import time, math, random
import board, busio
import displayio
import time
import board
import pwmio
from adafruit_motor import servo
from analogio import AnalogIn


a = digitalio.DigitalInOut(board.GP1)
a.direction = digitalio.Direction.OUTPUT

b = digitalio.DigitalInOut(board.GP0)
b.direction = digitalio.Direction.OUTPUT

x_pin = AnalogIn(board.GP27_A1)
y_pin = AnalogIn(board.GP26_A0)

while True:
    if x_pin.value / 65535 > 0.95:
        a.value = True
        b.value = True
    elif y_pin.value / 65535 < 0.05:
        print("B")
        a.value = False
        b.value = True
    elif y_pin.value / 65535 > 0.95:
        print('A')
        a.value = True
        b.value = False
    else:
        a.value = False
        b.value = False
    print(y_pin.value / 65535)
