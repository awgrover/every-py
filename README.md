# Non-blocking periodic and durations for python

Including patterns for periodic, and non-repeating (timer), actions.

While written especially for micropython and circuitpython, this library works in normal python 3. The examples are for the Adafruit CircuitPlayground Express variants, because that's what we've been working with.

## Summary

    from adafruit_circuitplayground import cp
    from every import Every

    every_half_second = Every(0.5) # every 0.5 seconds

    while(1):
        ... stuff that still runs ...

        # on/off periods = 0.5 seconds.
        if every_half_second(): # note the "()" for the test
            # this block runs "every half second"
            cp.red_led = not cp.red_led # blink

        ... stuff that still runs ...

## Background

`time.sleep()` stops your code, so you can only do 1 thing at a time. Here's the typical blink:

    import sleep from time

    while(1):
        ... stuff that is affected by sleep ...

        sleep(0.5) # program stops
        cp.red_led = not cp.red_led # blink

        ... stuff that is affected by sleep ...

The entire body of the `while` is affected by the `sleep()`. So, you can't blink at 2 different rates:

    import sleep from time

    while(1):

        # this loop doesn't work 
        # because it stops completely at each sleep()

        # blink builtin neopixel "0"
        sleep(0.5) # program stops
        if cp.pixels[0] == (0,0,0):
            cp.pixels[0] = (30,30,30) # on
        else:
            cp.pixels[0] = (0,0,0) # off

        # blink builtin neopixel "1"
        sleep(0.3) # program stops
        if cp.pixels[1] == (0,0,0):
            cp.pixels[1] = (30,30,30) # on
        else:
            cp.pixels[1] = (0,0,0) # off

Similarly, if you wanted to read a sensor, update a servo, read another sensor, update a LED, etc., then `sleep()` prevents you from doing those together (concurrently).

To do several things periodically, you want a non-blocking solution.

It's common to pair a periodic action with a duration (timer), like "every minute, make an obnoxious beep noise". The beep-noise has a duration. You'll want a non-blocking duration (timer) for that. Patterns of intervals and non-repeating patterns of intervals are also useful.

This is the classic pattern, that blocks your code:
    interval = 0.5 # some seconds
    last_time = time.monotonic()

    while(1):
        if time.monotonic() - last_time > interval:
            last_time = time.monotonic()
            ...do something...

(this is based on a c++ version I've written for Arduino)

## Prerequisites

This was written for python-3, and the standard libraries. It is specifically targetted to Adafruit's [circuitpython](https://circuitpython.org/) (a derivative of micropython).

## Installation

I haven't dealt with the standard python systems like pip, or the community library for circuitpython, etc. yet.

For circuitpython devices:

* go to [https://github.com/awgrover/every-py](https://github.com/awgrover/every-py)
* Use the **Code** button, and chose **Download ZIP**
* unzip it to somewhere that you can remember
* copy the `every` folder to your `CIRCUITPYTHON`
* write code that uses it

## Usage

### 1. Import

Most conveniently, you typically want to import the "class":

    from every import Every

I found the name "Every" to read well, but if that collides with some other thing, or doesn't read well to you, you can do the "alias" thing:

    # of course, the examples below won't match anymore
    from every import Every as EveryPeriod # make up your own name

### 2. Construct global objects

The objects need to be global since they keep track of time. Of course, expert programmers can figure out other patterns as long as the object persists for dynamic/temporal scope as needed (e.g. maybe construct it dynamically, and push to a global list).

#### Every(seconds) # Repeating interval
This creates an object that will "fire" _at_ every interval, e.g. "every 0.5 seconds, 'fire'".

    from every import Every

    # globals
    blink_interval = Every(0.5)

You'll find that giving it a good **name** will make your code clearer. Think of a name that will read well for the `if ...` pattern below: "if it-is-time-to-do-x()...", "if every\_half_second()..."

Note that this example as a blink-interval is actually half the blink-interval (a full cycle is on,off).

#### Every(seconds1, seconds2, ...) # Repeating pattern of intervals
This creates an object that has a sequence of intervals, then it repeats the sequence.

    from every import Every

    # globals
    long_short_blink = Every(0.5, 0.1)
    fancy_blink_interval = Every(0.5, 0.1, 0.1, 0.1)

The first one, `long_short_blink` can be used to have a long on period (0.5 seconds), and a short off period (0.1 seconds).
And, `fancy_blink_interval` will fire at 0.5 seconds, then 0.1, then 0.1, then 0.1, and then start over.

#### Every(seconds, 0) # a duration/timer, non-repeating
This creates an object that will fire only **once**, after `seconds`. So, it is used as a timer. Note the **0**, that is the signal that this is a timer (one-shot). You have to call `.start()` to start this. It is resettable.

    from every import Every

    # globals
    sound_duration = Every(2, 0)

#### Every(seconds1, seconds2, ..., 0) # a one-shot sequence of intervals
This creates an object that will fire for each interval, but does not repeat: "do this sequence once". So, still like a timer, but with a pattern before it stops firing. It is resettable.

    from every import Every

    # globals
    beeping = Every(1, 0.5, 1, 0.5, 0)

Again, **name** the object so that it reads well with the `if ...` pattern you'll use below: "if in-some-duration():..."

### 3. Expired predicate: `yourobject()`

In other words, "is it time?", "has the interval happened?", "every N, do...".

This uses a function-call pattern to test if the interval has expired. For all the object variations from above.

    from every import Every

    # globals
    beeping = Every(1, 0.5, 1, 0.5, 0)

    while(1): # typical "loop" to keep doing

        if beeping():
            ...it's time, do something...

The result of `yourobject()` is false until the interval, then true exactly once to signal that the interval has passed, and then becomes false again. For objects with multiple intervals (a pattern), it will become true again for the next interval in the pattern. For repeating objects (where the constructor had _no_ final `0`), it will start the pattern overagain. For non-repeating (_with_ a final `0` in the pattern), it will stay false after the last interval (not counting the final 0), see `.start`.

**Non-repeating** objects will not return true till you `.start` them (see below).

Note that this will return true if the interval has been passed: so you are not gauranteed to get exact timing. Consider the case where you have an `Every(0.1)`: if some code took 0.05 seconds, then you would get true at 0.15.

This will return true only once for the interval, so if you were somehow delayed 1 second for an `Every(0.1)`, you'd still only get true once at 1 second (and then every 0.1 as usual).

Especially relevant for timer/one-shot objects, the interval starts from when you construct the object. See below for resetting the start time.

**Drift** The code makes a decent attempt to avoid drift. So, in the cases above, where it can't "fire" exactly on 0.1 intervals, it will still try to fire on the next multiple of the 0.1 interval.

A typical pattern would be:

    if yourobject():
        # the interval has expired
        do something, like change state, read sensor, update motor

In the body of the `if`:

* long operations will still stop the whole program (e.g. fetching a web-page)
* `sleep()` will still stop the whole program
* long'ish operations may make other Every objects late, or cause one to skip

#### 4. Pattern state (index) `yourbobject.i`

The object knows which step of the pattern it is on, and you can use that instead of another variable to decide on the action.

The first time `yourobject()` is true, `.i` will be 1.

    if yourobject():
        if yourobject.i == 1: # not 0 first time!
            print("first step of sequence")
        elif yourobject.i == 2:
            print("second step of sequence")
        ...

Before the first true, `.i` should be 0. And, after the last interval in a non-repeating pattern, it should be 0.

#### 5. The last time it fired `yourobject.last`

Currently, you can look at the last time for the previous interval. The value is a `time.monotonic()`.

#### 6. Update the interval/patterns `yourobject.interval = newvalue`

or `yourobject.interval = (somesecs1, somesecs2, ...)`

You can change the interval/pattern at any time, so you can dynamical change your timing (e.g. blink interval is proportional to the potentiometer).

You can update to a single period, a pattern of repeating intervals, a one-shot, or a sequence of non-repeating intervals, just like the Constructor.

    from every import Every

    # globals
    blink_interval = Every(0.5)

    ....
    if forsomereason:
        blink_interval.interval = 0.3 # suddenly change to shorter
    elif someotherreason
        blink_interval.interval = (1, 0.5) # a pattern!

#### 7. Start/restart `yourobject.start()`

Remember, a duration/non-repeating/timer object (has the trailing `0` in its pattern), starts out as non-running: it's false till you `.start` it and it's interval(s) expire.

Typically useful to re-use a duration/non-repeating/timer after it has finished all of it's intervals.

Also useful to synchronize the period/interval to a start time. `Every` objects for repeating periods have a start time that is set when they are constructed. Duration/non-repeating "start" when you call `.start()`. But, you could also synchronize a repeating pattern by setting the start (or updating it).

    from every import Every

    # globals
    led_duration = Every(1.0, 0)

    # Turn on the led when the button is pushed
    # Leave it on for 1 second

    if abuttonwaspushed:
        cp.red_led = True
        led_duration.start()

    if led_duration(): # won't start running till .start
        cp.red_led = False

#### Longer example

This example uses the built-in LED, and neo-pixels:

    from adafruit_circuitplayground import cp
    from every import Every

    # globals
    blink_interval = Every(0.5)
    long_short_blink = Every(0.5, 0.1)
    fancy_blink_interval = Every(0.5, 0.1, 0.1, 0.1)
    sound_duration = Every(2, 0)
    beeping = Every(1, 0.5, 1, 0.5, 0)

    def blink_neo(index):
        '''simple blink: switch state on every call'''
        if cp.pixels[index] == (0,0,0):
            cp.pixels[index] = (30,30,30) # on
        else:
            cp.pixels[index] = (0,0,0) # off
        

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
            if sound_duration.i % 2
                # not playing:
                cp.start_tone(262)
            else:
                # playing, so:
                cp.stop_tone()

        # `if beeping()...` would have a similar pattern

## References

This is not the only solution, of course. 

Advantages: 

* the simplist pattern I could think of for the basic periodic action, so easier for beginners
* still allows periodic, patterns, and non-repeating durations
* reads well if you name the Every instance well
* conscious of code/variable footprint relevant for circuit/micro-python RAM limits
* works without the `threading` module

Disadvantages:

* not efficient for a large number of `Every` objects (perhaps 10 is the breakpoint)
* not minimal for _only_ the basic periodic action (but see the lightweight version soon to be released)
* the `if someperiod():...` pattern is a less common pattern in the python world
* a bit awkward for getting the index of the pattern
* does not support lambdas (nor function references), because the `if ...` pattern seemed good enough, and kept the memory size down
* unlike c++, you pay for features/behavior that you don't use (thus the lightweight versions)
* to do "repeat N times", you have to provide N intervals in the constructor, or do your own counter+reset
* doesn't use the `threading` module, nor async mechanisms

**other libs**

* https://github.com/Angeleno-Tech/nonblocking\_timer or https://github.com/mikepschneider/CircuitPython\_nonblocking_timer
* https://github.com/WarriorOfWire/tasko (Circuitpython 6.0)
* http://docs.python.org/2.7/library/threading.html#module-threading
* http://bleaklow.com/2010/07/20/a\_very\_simple\_arduino\_task\_manager.html

## TODO

* a lightweight version that takes less code-space/variable-space memory.
* the `.mpy` compiled versions
