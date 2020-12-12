''' The longer example from the docs '''

from adafruit_circuitplayground import cp
from every.every import Every

# globals
blink_interval = Every(0.5)
long_short_blink = Every(0.5, 0.1)
fancy_blink_interval = Every(0.5, 0.1, 0.1, 0.1)
# the first interval is a delay at start, then on/off/on/off
sound_duration = Every(0.1, 2, 2, 0.3, 0)

def blink_neo(index):
    '''simple blink: switch state on every call'''
    if cp.pixels[index] == (0,0,0):
        cp.pixels[index] = (30,30,30) # on
    else:
        cp.pixels[index] = (0,0,0) # off
    
sound_duration.start()

while(1): # typical "loop" for "keep doing stuff" in circuit/micro python
    
    # Repeating

    if blink_interval():
        cp.red_led = not cp.red_led # blink

    if long_short_blink(): # on is longer than off
        blink_neo(0)
                
    if fancy_blink_interval(): # a pattern of 4 intervals, then repeat
        blink_neo(1)
                
    # Timer/One-shots
    # in this example, these happen only once per run

    if sound_duration():
        # the even/odd trick:
        if sound_duration.i % 2:
            # not playing:
            cp.start_tone(262)
        else:
            # playing, so:
            cp.stop_tone()
