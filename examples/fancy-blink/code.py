from adafruit_circuitplayground import cp
from every.every import Every

long_short_blink = Every(0.5, 0.1)
fancy_blink_interval = Every(0.5, 0.4, 0.2, 0.1)

colors = (0xFF0000, 0x00FF00, 0x0000FF, 0x606060)

cp.pixels.brightness = 0.2 # too bright otherwise

while(1):

    # on/off periods
    # On for 0.5, off for 0.1
    if long_short_blink(): # note the "()" for the test
        # this block runs "every half second"
        cp.red_led = not cp.red_led # blink

    # Using .i to determine what color 
    # and where
    # to show for each interval
    if fancy_blink_interval():
        cp.pixels.fill(0x0) # just clear them

        # change colors on one pixel
        cp.pixels[0] = colors[ fancy_blink_interval.i ]

        # show each progressive color on different pixel
        cp.pixels[ fancy_blink_interval.i + 1 ] = colors[ fancy_blink_interval.i ]

