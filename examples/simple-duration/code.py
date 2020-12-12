'''Example of simple duration
    On touch (pads near blinking leds), play tone for 2 seconds
    Also, run heartbeat
'''

from adafruit_circuitplayground import cp
from every.every import Every

sound_duration = Every(2, 0)

blink = Every(0.5)
tone = 100

cp.pixels.brightness = 0.1 # too bright otherwise
blink_white = (30,30,30)


while(1):

    # heartbeat
    if blink():
        cp.pixels[1] = (0,0,0) if cp.pixels[1] == blink_white else blink_white
        cp.pixels[8] = (0,0,0) if cp.pixels[8] == blink_white else blink_white

    # Touch near the usb port triggers
    if cp.touch_A3 or cp.touch_A2 or cp.touch_A5 or cp.touch_A4:
        sound_duration.start()
        cp.start_tone(tone)
        cp.red_led = True

    if sound_duration():
        #tone off
        cp.stop_tone()
        cp.red_led = False
