# Based on:
# qteye.py - a stand-alone GC9A01 round LCD "eye" on a QTPy
# 23 Oct 2022 - @todbot / Tod Kurt
# Part of https://github.com/todbot/CircuitPython_GC9A01_demos
# also see: https://twitter.com/todbot/status/1584309133263532033
#      and: https://twitter.com/todbot/status/1584309133263532033
# 
# To install needed libraries: "circup install adafruit_imageload gc9a01"
#
import time, math, random
import board, busio
import displayio
import adafruit_imageload
import gc9a01
import time
import board
import pwmio
from adafruit_motor import servo
from analogio import AnalogIn

# create a PWMOut object on Pin A2.
pwm = pwmio.PWMOut(board.GP0, duty_cycle=2 ** 15, frequency=50)
pwm2 = pwmio.PWMOut(board.GP1, duty_cycle=2 ** 15, frequency=50)

x_pin = AnalogIn(board.GP27_A1)
y_pin = AnalogIn(board.GP26_A0)

# Create a servo object, my_servo.
my_servo = servo.Servo(pwm)
my_servo_2 = servo.Servo(pwm2)

def get_voltage(pin):
    return ((pin.value * 180) / 65536)

displayio.release_displays()

dw, dh = 240,240  # display dimensions

print("HELLO")

# load our eye and iris bitmaps
eyeball_bitmap = displayio.Bitmap(240,240,2)
bw = displayio.Palette(2)
bw[0] = 0x000000  # black
bw[1] = 0xFFFFFF  # white
print("eyeball loaded")
iris_bitmap, iris_pal = adafruit_imageload.load("imgs/eye0_iris0.bmp")



eyeball_bitmap.fill(1)

for i in range(iris_bitmap.width):
    print(i)
    if i <= 120:
        iris_bitmap[i, iris_bitmap.height-1] = 1
    iris_bitmap.dirty()


print("images loaded")

# compute or declare some useful info about the eyes
iris_w, iris_h = iris_bitmap.width, iris_bitmap.height-1  # iris is normally 110x110
iris_cx, iris_cy = dw//2 - iris_w//2, dh//2 - iris_h//2
r = 50  # allowable deviation from center for iris


tft0_clk  = board.GP10
tft0_mosi = board.GP11

tft_L0_rst = board.GP12
tft_L0_dc  = board.GP13
tft_L0_cs  = board.GP14

spi0 = busio.SPI(clock=tft0_clk, MOSI=tft0_mosi)

# class to help us track eye info (not needed for this use exactly, but I find it interesting)
class Eye:
    def __init__(self, spi, dc, cs, rst, rot=0, eye_speed=0.25, twitch=2):
        display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=rst)
        display = gc9a01.GC9A01(display_bus, width=dw, height=dh, rotation=rot)
        main = displayio.Group()
        display.root_group = main
        self.display = display
        self.eyeball = displayio.TileGrid(eyeball_bitmap, pixel_shader=bw)
        self.iris = displayio.TileGrid(iris_bitmap, pixel_shader=iris_pal, x=iris_cx,y=iris_cy)
        main.append(self.eyeball)
        main.append(self.iris)
        self.x, self.y = iris_cx, iris_cy
        self.tx, self.ty = self.x, self.y
        self.next_time = time.monotonic()
        self.eye_speed = eye_speed
        self.twitch = twitch
        print("eye initialized")

    def update(self):
        self.x = self.x * (1-self.eye_speed) + self.tx * self.eye_speed # "easing"
        self.y = self.y * (1-self.eye_speed) + self.ty * self.eye_speed
        self.iris.x = int( self.x )
        self.iris.y = int( self.y )
        if time.monotonic() > self.next_time:
            t = random.uniform(0.25,self.twitch)
            self.next_time = time.monotonic() + t
            self.tx = iris_cx + random.uniform(-r,r)
            self.ty = iris_cy + random.uniform(-r,r)
        self.display.refresh()

# a list of all the eyes, in this case, only one
the_eyes = [
    Eye( spi0, tft_L0_dc, tft_L0_cs,  tft_L0_rst, rot=0),
]

while True:
    for eye in the_eyes:
        eye.update()
    my_servo_2.angle = get_voltage(x_pin)
    my_servo.angle = get_voltage(y_pin)