# `every
# ====================================================
# 
# Test whether an interval has gone by. 
# Minimal functionality, smaller memory footprint
# 
# every_half_second = Every(0.5) # every 1/2 second
# while (1):
#     if every_half_second():
#         do something

# imports

import time

class Every(object):
    # True on every interval

    def __init__(self, interval):
        # Make an instance.
        #   :interval in seconds

        self.interval = interval
        self.last = time.monotonic() - interval # start immediatly

    def __call__(self):
        now = time.monotonic()
        diff = now - self.last
        if (diff >= self.interval):
            drift = diff % self.interval
            self.last = now
            self.last -= drift
            return True
        else:
            return False
