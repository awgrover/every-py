import unittest
import sys, os
from every.lightweight_timer import Timer
import time, math

class LightweightTimerTests(unittest.TestCase):

    def test0Sanity_monotonic(self):
        # make sure our assumptions hold

        now = time.monotonic()
        dumywork = 0
        for x in range(1,100):
            dumywork += 1
        finished = time.monotonic()
        assert now != finished, "Time actually passes according to monotonic()"
        assert finished - now < 0.005, "But, we can get a lot of work done in 0.05 (actual %s)" % (finished-now)

    def testInitialState(self):
        tester = Timer(0.05)
        start=time.monotonic()

        assert not tester(), "Does not fire instantly"
        assert tester.running == False, "Not running initially"

    def testNotStart(self):
        want_interval = 0.05
        tester = Timer(want_interval)
        # NB: we don't .start

        start=time.monotonic()
        finished = None
        while( not finished and time.monotonic() - start < want_interval * 2):
            if tester():
                finished = time.monotonic()
                break

        assert not finished,"It never fired, saw interval %s" % ( (finished if finished else 0) -start)

    def testStart(self):
        want_interval = 0.05
        tester = Timer(want_interval)

        tester.start()
        start=time.monotonic()
        finished = None
        while( not finished and time.monotonic() - start < want_interval * 2):
            if tester():
                finished = time.monotonic()
                break

        assert finished,"It fired"
        assert math.isclose(finished-start, want_interval, rel_tol=0.1, abs_tol=0.001), "Did its duration %s, actually %s" % (want_interval, finished-start)

    def testNonBlocking(self):
        # a major claim!
        want_interval = 0.05
        tester = Timer(want_interval)

        start = time.monotonic()
        tester.start() 

        # might as well test till expired
        ct = 0
        last = time.monotonic()
        while not tester() and time.monotonic()-start < want_interval*2:
            ct+=1
            now = time.monotonic()
            assert math.isclose(now-last, 0.0, rel_tol=0.1, abs_tol=0.001), "Doesn't block (loop # %s), actually %s" % (ct, now-last)
            last = time.monotonic()
        # I got 56,000 loops!
        assert ct > 1,"Ran a polling loop, i.e., didn't block for %s>1 times" % ct

    def testRunning(self):
        want_interval = 0.05
        tester = Timer(want_interval)
        assert not tester.running,"Timer isn't running initially"

        tester.start()
        start=time.monotonic()

        assert tester.running,"Timer is running after .start()"

        finished = None
        while( not finished and time.monotonic() - start < want_interval * 2):
            if tester():
                finished = time.monotonic()
                break

        assert finished,"It fired"
        assert not tester.running, "Timer isn't running after it is done"

    def testSetInterval(self):
        test_start = time.monotonic()

        unchanged_interval = 0.05
        changed_interval = unchanged_interval * 2

        unchanged = Timer(unchanged_interval)
        unchanged.start()

        changed = Timer(unchanged_interval)
        changed.interval = changed_interval
        changed.start()

        hit_at = {
            'unchanged' : [],
            'changed' : [],
            }

        # let the slowest happen twice
        while( time.monotonic() - test_start < unchanged_interval * 2 + unchanged_interval/2.0 ):
            if unchanged():
                #print("<<hit unchagned", time.monotonic() - test_start )
                hit_at['unchanged'].append( time.monotonic() - test_start )
            if changed():
                #print("<<hit chagned", time.monotonic() - test_start )
                hit_at['changed'].append( time.monotonic() - test_start )

        self.do_intervals_match( 'unchanged', hit_at['unchanged'], [unchanged_interval] )
        print( "ci", changed.interval)
        self.do_intervals_match( 'changed', hit_at['changed'], [changed_interval] )

    def do_intervals_match(self, prefix_msg, actual, want ):
        #print( "  e[]", want)
        isclose = []
        is_ok = True

        for i,an_actual in enumerate(actual):
            if len(want) > i:
                isclose.append( math.isclose(an_actual, want[i], rel_tol=0.1, abs_tol=0.001) )
                is_ok = is_ok and isclose[-1]

        assert is_ok and len(actual) == len(want), "Expected %s to be ~ %s, but got %s (%s)" % (prefix_msg, want, actual, isclose)

if __name__ == "__main__":
    unittest.main() # run all tests
