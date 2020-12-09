# `every
# ====================================================
# 
# Test whether an duration has expired (once).
# Minimal functionality, smaller memory footprint
# 
# has_been_a_minute = Every(60) # 60 seconds
# while (1):
#     if every_minute():
#         do something

# imports

import time

class Timer(object):
    # True after a duration, once

    def __init__(self, interval):
        # Make an instance.
        #   :interval in seconds
        # "interval" to be parallel with Every wording,
        # but actually a duration.

        # lightweight! no @property
        self.interval = interval
        self.last = 0
        self.running = False # we aren't usable till .start()

    def start(self):
        self.running = True
        self.last = time.monotonic()

    def __call__(self):
        if (self.running):
            now = time.monotonic()
            if ((now - self.last) >= self.interval):
                self.last = now # record of when we expired
                self.running = False
                return True
        return False
