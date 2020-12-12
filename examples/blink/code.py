from adafruit_circuitplayground import cp
from every.every import Every

every_half_second = Every(0.5) # every 0.5 seconds

while(1):

    # on/off periods = 0.5 seconds.
    if every_half_second(): # note the "()" for the test
        # this block runs "every half second"
        cp.red_led = not cp.red_led # blink
