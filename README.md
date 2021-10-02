# Non-blocking periodic and durations for python

Including patterns for periodic, and non-repeating (timer), actions.

[https://github.com/awgrover/every-py](https://github.com/awgrover/every-py)

While written especially for micropython and circuitpython, this library works in normal python 3. The examples are for the Adafruit CircuitPlayground Express variants, because that's what we've been working with.

## Summary

    from adafruit_circuitplayground import cp
    from every.every import Every

    every_half_second = Every(0.5) # every 0.5 seconds

    while(1):
        ... stuff that still runs ...

        # on/off periods = 0.5 seconds.
        if every_half_second(): # note the "()" for the test
            # this block runs "every half second"
            cp.red_led = not cp.red_led # blink

        ... stuff that still runs ...

## Background

`time.sleep()` stops your code, so you can only do 1 thing at a time. Here's the familiar blocking-style blink:

    import sleep from time

    while(1):
        ... stuff that is affected by sleep ...

        sleep(0.5) # program stops
        cp.red_led = not cp.red_led # blink

        ... stuff that is affected by sleep ...

The entire body of the `while` is affected by the `sleep()`. So, you can't blink at 2 different rates:

    import sleep from time

    while(1):

        # this loop doesn't do what you hope 
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

It's common to pair a periodic action with a duration (timer), like "every minute, make an obnoxious beep noise". The beep-noise has a duration. You'll want a non-blocking duration (timer) for that, too. Patterns of intervals and non-repeating patterns of intervals are also useful.

This is the classic solution, that doesn't block your code:

    interval = 0.5 # some seconds
    last_time = time.monotonic()

    while(1):
        if time.monotonic() - last_time > interval:
            last_time = time.monotonic()
            ...do something...

I've turned that into a pattern via a class, with more flexibility.

(this is based on a c++ version I've written for Arduino)

## Prerequisites

This was written for python 3, and the standard libraries. It is specifically targetted to Adafruit's [circuitpython](https://circuitpython.org/) (a derivative of micropython). It does not have any extra prerequisites.

## Installation

I haven't dealt with the standard python systems like pip, or the community library for circuitpython, etc. yet.

For circuit/micro-python devices:

* go to [Latest release](https://github.com/awgrover/every-py/releases/latest)
* download the `every-mpy-*.zip` (or the "Source code" zip for regular .py files)
* unzip it to somewhere that you can remember
* copy the `every` folder to your `CIRCUITPYTHON/lib`
* write code that uses it

For the smaller-memory-footprint version:

* the instructions are the same except use the `every-mpy-lightweight-*.zip`

For regular python:

* go to [Latest release](https://github.com/awgrover/every-py/releases/latest)
* download the "Source code" zip file
* unzip it to somewhere that you can remember
* before the import, do this
`import sys; sys.path.append('somewhere that you can remember')`
* or otherwise put the unzipped directory in the python search path

## Usage

(see also, "Lightweight Usage" below)

### 1. Import

Most conveniently, you typically want to import the "class":

    from every.every import Every

I found the name "Every" to read well, but if that collides with some other thing, or doesn't read well to you, you can do the "alias" thing:

    # of course, the examples below won't match anymore
    from every.every import Every as EveryPeriod # make up your own name

### 2. Construct global objects

The objects need to be global since they keep track of time. Of course, expert programmers can figure out other patterns as long as the object persists for dynamic/temporal scope as needed (e.g. maybe construct it dynamically, and push to a global list).

#### Every(seconds) # Repeating interval
This creates an object that will "fire" _at_ every interval, e.g. "every 0.5 seconds, 'do something'".

    from every.every import Every

    # globals
    blink_interval = Every(0.5)

You'll find that giving it a good **name** will make your code clearer. Think of a name that will read well for the `if ...` pattern below: "if it-is-time-to-do-x()...", "if every\_half_second()..."

Note that this example as a blink-interval is actually half the blink-interval (a full cycle is on,off).

#### Every(seconds1, seconds2, ...) # Repeating pattern of intervals
This creates an object that has a sequence of intervals, then it repeats the sequence.

    from every.every import Every

    # globals
    long_short_blink = Every(0.5, 0.1)
    fancy_blink_interval = Every(0.5, 0.1, 0.1, 0.1)

The first one, `long_short_blink` can be used to have a long on period (0.5 seconds), and a short off period (0.1 seconds).
And, `fancy_blink_interval` will fire at 0.5 seconds, then 0.1, then 0.1, then 0.1, and then start over.

#### Every(seconds, 0) # a duration/timer, non-repeating
This creates an object that will fire only **once**, after `seconds`. So, it is used as a timer. Note the **0**, that is the signal that this is a timer (one-shot). You have to call `.start()` to start this. It is resettable.

    from every.every import Every

    # globals
    sound_duration = Every(2, 0)

#### Every(seconds1, seconds2, ..., 0) # a one-shot sequence of intervals
This creates an object that will fire for each interval, but does not repeat: "do this sequence once". So, still like a timer, but with a pattern before it stops firing. It is resettable.

    from every.every import Every

    # globals
    beeping = Every(1, 0.5, 1, 0.5, 0)

Again, **name** the object so that it reads well with the `if ...` pattern you'll use below: "if in-some-duration():..."

### 3. `yourobject()` # Expired predicate: 

In other words, "is it time?", "has the interval happened?", "every N, do...".

This uses a function-call pattern to test if the interval has expired. For all the object variations from above.

    from every.every import Every

    # globals
    beeping = Every(1, 0.5, 1, 0.5, 0)

    while(1): # typical "loop" to keep doing

        if beeping():
            ...it's time, do something...

For repeating/periodic objects:

* The first test of `yourobject()` will be True. I.e. instantly.
* It will then be false till the first interval has passed
* Then it will be True again, and so on through the pattern
* At the end of the pattern, it will repeat

For a non-repeating/duration object:

* `yourobject()` will be False
* When you call `yourobject.start()`, the first duration begins
* `yourobject()` will be False till the duration has passed
* Then it will be True again, and so on through the pattern
* After the last duration in the pattern, `yourobject()` will be False until you restart the whole sequence with `.start()`

Note that this will return True if the interval has been passed and you missed : so you are not guaranteed to get exact timing. Consider the case where you have an `Every(0.1)`: if some code took 0.2 seconds, then you would get true at 0.2.

This will return true only once for each interval, so an `if...` will fire _at_ each interval, which is the point.

A typical pattern would be:

    if yourobject():
        # the interval has expired
        do something, like change state, read sensor, update motor

In the body of the `if`:

* long operations will still stop the whole program (e.g. fetching a web-page)
* `sleep()` will still stop the whole program
* long'ish operations may make other Every objects late

**Drift** The code makes a decent attempt to avoid drift. So, in the cases above, where it can't "fire" exactly on 0.1 intervals, it will still try to fire on the next multiple of the 0.1 interval.

#### 4. `yourbobject.i` # Pattern state (index) 

The object knows which step of the pattern it is on, and you can use that instead of another variable to decide on the action.

* Before you test `yourobject()`, `.i` will be the maximum index, i.e. length of the pattern - 1. E.g. for a simple `Every(0.1)`, `.i` would be 1. For a pattern like `Every(1,2,3)`, `.i` will be 2.
* After the first time `yourobject()` is true (which is immediately), `.i` will be 0. 
* So, `.i` is the index of the next interval

For a non-repeating/duration object:

* After the last time `yourobject()` is true, `.i` should be 0

    if yourobject():
        if yourobject.i == 0: # 0 first time, but 0 duration for periodics
            print("start sequence")
            # e.g. turn led for 1st interval
        elif yourobject.i == 1:
            print("after 1st duration of sequence")
            # e.g. turn led off for 2nd interval
        ...

#### 5. `yourobject.last` # The last time it fired 

Currently, you can look at the last time for the previous interval. The value is a `time.monotonic()`.

Warning: this value is tweaked to adjust for drift, so isn't quite truthful! It's probably not a good idea to use this value.

#### 6. `yourobject.interval = newvalue` # Update the interval/patterns 

or `yourobject.interval = (somesecs1, somesecs2, ...)`

or `x = yourobject.interval`

You can change the interval/pattern at any time, so you can dynamical change your timing (e.g. blink interval is proportional to the potentiometer). Note: setting the interval acts a lot like the constructor: a periodic object will fire immediately (call .start() if you want the first interval), and a non-repeating/duration object with stop running (call `.start()` to start it).

You can read the current interval. You will _always_ get a tuple back:

    every_sec = Every(1)
    print(every_sec.interval) # prints a tuple: (1,)

You can update to a single period, a pattern of repeating intervals, a one-shot, or a sequence of non-repeating intervals, just like the Constructor.

    from every.every import Every

    # globals
    blink_interval = Every(0.5)

    ....
    if forsomereason:
        blink_interval.interval = 0.3 # suddenly change to shorter
    elif someotherreason
        blink_interval.interval = (1, 0.5) # a pattern!

#### 7. `yourobject.start()` # Start/restart 

Remember, a duration/non-repeating/timer object (has the trailing `0` in its pattern), starts out as non-running: it's false till you `.start`.

Typically useful to start a duration/non-repeating based on an event, or re-use a duration/non-repeating/timer after it has finished all of it's intervals.

Also useful to synchronize the period/interval to a start time. `Every` objects for repeating periods have a start time that is set when they are constructed. Duration/non-repeating "start" when you call `.start()`. But, you could also synchronize a repeating pattern by setting the start (or updating it).

    from adafruit_circuitplayground import cp
    from every.every import Every

    # globals
    led_duration = Every(1.0, 0)

    while(1):
        # Turn on the led when the button is pushed
        # Leave it on for 1 second

        if cp.button_a: # button pushed
            cp.red_led = True
            led_duration.start()

        if led_duration(): # won't start running till .start
            cp.red_led = False

### 8. `yourobject.running` # is it running?

Currently exposed, setting this is not supported.

Only relevant for duration/non-repeating/timer objects, you can test if `.start` has been called _and_ the last interval hasn't expired.

    if not sound_duration.running:
        # it's not running, we could restart it, or play another sound, etc


#### Longer example

This example uses the built-in LED, and neo-pixels:

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

## Lightweight Usage

It is not difficult to consume all available memory on a circuitplayground express, or other circuit/micro-python device. Supposedly, around 200 lines of python will do it on the circuitplayground express!

Using the .mpy files can help, as this avoids byte-code compilation on the device. See Installation above.

But, I've provided simplified versions of `Every`, for repeating periods; and a separate `Timer` class for one-shot durations. They don't support patterns, and are separate classes. They are significantly smaller ("significant" if you are at the point where you are worrying about it), and somewhat faster. Again, use the .mpy files, specifically see the `Releases` (as noted in "Installation" above) that have only the lightweight versions.

* If you only import one class from `every.lightweight`, it uses much less memory.
* If you import both `Every` and `Timer`, it doesn't save as much memory (especially byte-code), though each object you make is smaller than the full-function `Every`, and is somewhat faster. You should consider just using the full-function `Every`.
* I don't think special versions that can do patterns would end up being smaller enough to make it worthwhile. If you want patterns of intervals, just use the full-function `Every`

### Lightweight `Every`

The lightweight `Every` works much as above, except no patterns, and it _only_ does repeating periodic (see `Timer` below):

    from every.lightweight import Every

    # globals
    every_second = Every(1.0)

    while(1):
        if every_second():
            ....

* The constructor `Every(...)` takes exactly 1 argument: the number of seconds.
* You can't specify a pattern of intervals.
* It always repeats (see `Timer`, next)
* You can assign to `yourobject.interval` to update it, but only a single value. You will surprised unless you also set `yourobject.last = time.monotonic()`.
* You can read from `yourobject.interval`, but it is always a single value (not tuple).
* There is no `yourobject.start()` to synchronize, but you can read and set `yourobject.last`. Setting `.last = time.monotonic()` lets you "synchronize".
* There is no `yourobject.i` (there are no patterns)

### Lightweight `Timer`

The separate lightweight `Timer` works much as the regular `Every` for non-repeating/timer, except no patterns.

    from every.lightweight import Timer

    # globals
    has_been_one_second = Timer(1.0)

    while(1):
        if somethinginterestinghappens:
            ... start something ...
            has_been_one_second.start()

        if has_been_one_second():
            ....

* All the notes for lightweight `Every` apply
* It does have `yourobject.running`

## References

This is not the only solution, of course. 

Advantages: 

* the simplist pattern I could think of for the basic periodic action, so, easier for beginners
* still allows periodic, patterns, and non-repeating durations
* reads well if you name the Every instance well
* conscious of code/variable footprint relevant for circuit/micro-python RAM limits
* works without the `threading` module
* lightweight options available

Disadvantages:

* not efficient for a large number of `Every` objects (perhaps 10 is the breakpoint)
* not minimal for _only_ the basic periodic action (but see the lightweight versions)
* the `if someperiod():...` pattern is a less common pattern in the python world
* a bit awkward for getting the index of the pattern
* does not support lambdas (nor function references), because the `if ...` pattern seemed good enough, and kept the memory size down
* unlike c++, you pay for features/behavior that you don't use (thus the lightweight versions)
* to do "repeat N times", you have to provide N intervals in the constructor, or do your own counter+reset
* doesn't use the `threading` module, nor the (new) `async` mechanism

**other libs**

* https://github.com/Angeleno-Tech/nonblocking\_timer or https://github.com/mikepschneider/CircuitPython\_nonblocking_timer
* https://github.com/WarriorOfWire/tasko (Circuitpython 6.0)
* http://docs.python.org/2.7/library/threading.html#module-threading
* http://bleaklow.com/2010/07/20/a\_very\_simple\_arduino\_task\_manager.html

## Contributing

When reporting a bug, describe enough so that I can reproduce it (include code if possible). Obviously, if it involves some specific hardware, it may be hard to debug.

Please report bugs, issues, suggestions, improvements via the **Issues** in [https://github.com/awgrover/every-py](https://github.com/awgrover/every-py).

If you use this, I'd be interested in feedback about how well it works for you.

If you want to make a change, you could try to ask first in an "issue" (I may not respond quickly), or just make a pull-request which might lead to a discussion.

## Development/Building

No building is required for the .py files. But, the .mpy files have to be "compiled" by `cross-mpy`. And, the release artefacts (mpy zip files) have to be built.

### Building Prerequisites

* git
* get, install as mpy-cross, and add to PATH: `mpy-cross` command from [https://pypi.org/project/mpy-cross](https://pypi.org/project/mpy-cross)
* gnu-make

### Building

* update `every/version.py`, incrementing the `__version__` as appropriate
* commit changed files
* create a git tag if the `__version__` has changed
* run

    make

* It will check that the git-tag and version.py match, and will make the .zip files
* push and create a "Release" in gihub based on the tag, attach the new .zip files that were made

## TODO

* cleanup docstrings to be python'ish
* "publish" to pip-like and adafruit community
