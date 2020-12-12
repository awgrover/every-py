'''Example of updating duration
    On touch (pads near blinking leds), changes blink rate
'''

from adafruit_circuitplayground import cp
from every.every import Every

rate_a = 0.5
rate_b = 0.1
blink = Every(rate_a)

cp.pixels.brightness = 0.1 # too bright otherwise
blink_white = (30,30,30)


while(1):

    # heartbeat
    if blink():
        cp.pixels[1] = (30,30,30) if cp.pixels[1] == (0,0,0) else (0,0,0)
        cp.pixels[8] = (30,30,30) if cp.pixels[8] == (0,0,0) else (0,0,0)

    # This acts funny WHILE you are touching (blinks real fast)
    # Real code should detect touch as the _transition_ from not-touch to touch

    # Touch near the blinking leds changes rate
    if cp.touch_A3 or cp.touch_A2:
        blink.interval = rate_a

    if cp.touch_A5 or cp.touch_A4:
        blink.interval = rate_b
