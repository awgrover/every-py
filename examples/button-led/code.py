'''From Docs,
    Press button, led stays on for 1 second
'''
from adafruit_circuitplayground import cp
from every.every import Every

# globals
led_duration = Every(1.0, 0)

# Turn on the led when the button is pushed
# Leave it on for 1 second

while (True):

    if cp.button_a: # button pushed
        cp.red_led = True
        led_duration.start()

    if led_duration(): # won't start running till .start
        cp.red_led = False

