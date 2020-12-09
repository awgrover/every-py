import unittest
import sys, os
from every.lightweight_every import Every
import time, math

class LightweightEveryTests(unittest.TestCase):

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
        tester = Every(0.05)
        start=time.monotonic()

        assert tester(), "Does fire instantly"

    def testRepeats(self):
        want_interval = 0.05
        tester = Every(want_interval)

        start=time.monotonic()
        finished = []
        # so, three times, immediate, and 2 durations
        while( time.monotonic() - start < want_interval * 2):
            if tester():
                finished.append(time.monotonic() - start)

        self.do_intervals_match( 'unchanged', finished, [0, want_interval, 2*want_interval] )

    def testSetLast(self):
        # there is no .start(), but you can use .last=
        want_interval = 0.05
        tester = Every(want_interval)
        
        # make it go off at 0.025
        tester.last = time.monotonic() - want_interval/2

        start=time.monotonic()
        finished = None
        while( not finished and time.monotonic() - start < want_interval * 2):
            if tester():
                finished = time.monotonic()
                break

        assert finished,"It fired"
        assert math.isclose(finished-start, want_interval/2, rel_tol=0.1, abs_tol=0.001), "Did its duration %s, actually %s" % (want_interval/2, finished-start)

    def testNonBlocking(self):
        # a major claim!
        want_interval = 0.05
        tester = Every(want_interval)

        start = time.monotonic()
        tester() # get rid of immediate firing
        now = time.monotonic()
        assert math.isclose(now-start, 0.0, rel_tol=0.1, abs_tol=0.001), "Doesn't block at first (immedate), actually %s" % (ct, now-start)


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

    def testSetInterval(self):
        test_start = time.monotonic()

        unchanged_interval = 0.05
        changed_interval = unchanged_interval * 2

        unchanged = Every(unchanged_interval)

        changed = Every(unchanged_interval)
        changed.interval = changed_interval
        changed.last = time.monotonic() # it was tweaked for immediate for unchanged_interval
        # That prevents the immediate firing!

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

        # we are recording elapsed from start (not interval), thus the 2*
        self.do_intervals_match( 'unchanged', hit_at['unchanged'], [0, unchanged_interval, 2*unchanged_interval] )
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
