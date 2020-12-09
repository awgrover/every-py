import unittest
import sys, os
from every.every import Every
import time, math

class PeriodAndDurationTests(unittest.TestCase):
    def setUp(self):
        # we are going to be tricky, and make it here, so it's start is now
        # when we test it, other tests may have run, using up its time!
        self.start_tester = Every(0.05)

    def test0Sanity_monotonic(self):
        # make sure our assumptions hold

        now = time.monotonic()
        dumywork = 0
        for x in range(1,100):
            dumywork += 1
        finished = time.monotonic()
        assert now != finished, "Time actually passes according to monotonic()"
        assert finished - now < 0.005, "But, we can get a lot of work done in 0.05 (actual %s)" % (finished-now)

    def testSimpleTimer(self):
        # does a basic behavior work

        tenth = Every(0.05, 0)
        start=time.monotonic()

        assert not tenth(), "Does not fire instantly"
        assert math.isclose(time.monotonic()-start, 0, rel_tol=0.01, abs_tol=0.001),"First test doesn't block or take time, saw %s != %s " % (time.monotonic()-start)

        start=time.monotonic()
        tenth.start()
        finished = None
        while( not finished and time.monotonic() - start < 1):
            if tenth():
                finished = time.monotonic()
                break

        assert math.isclose(finished-start, 0.05, rel_tol=0.1, abs_tol=0.0), "Elapsed ~0.05, actually %s" % (finished-start)

    def testSimpleEvery(self):
        # does a basic behavior work at all?

        tenth = Every(0.1)
        start=time.monotonic()
        finished = None
        while( not finished and time.monotonic() - start < 1):
            if tenth():
                finished = time.monotonic()
                break

        assert math.isclose(finished-start, 0.0, rel_tol=0.1, abs_tol=0.001), "1st period is instantly, actually %s" % (finished-start)

        start=time.monotonic()
        finished = None
        while( not finished and time.monotonic() - start < 1):
            if tenth():
                finished = time.monotonic()
                break

        assert math.isclose(finished-start, 0.1, rel_tol=0.1, abs_tol=0.0), "Elapsed ~0.1, actually %s" % (finished-start)

    def testNonBlocking(self):
        # a major claim!

        fifdred = Every(0.05)

        start = time.monotonic()
        fifdred() # expire immediately 1st time

        # yes, already tested, but if you are debugging, you'll want to know
        assert math.isclose(time.monotonic()-start, 0.0, rel_tol=0.1, abs_tol=0.001), "1st period is instantly, actually %s" % (finished-start)

        # might as well test till expired
        ct = 0
        last = time.monotonic()
        while not fifdred() and time.monotonic()-start < 1:
            ct+=1
            now = time.monotonic()
            assert math.isclose(now-last, 0.0, rel_tol=0.1, abs_tol=0.001), "Doesn't block (loop # %s), actually %s" % (ct, now-last)
            last = time.monotonic()
        # I got 56,000 loops!
        assert ct > 1,"Ran a polling loop, i.e., didn't block for %s>1 times" % ct

    def testFirstInterval(self):
        # do we provide an interval == first interval in patterns?
        # (cf. timers require .start(), and .start() causes "use first interval")

        tester = Every(0.05, 0.1) # simple case

        # on instant start, we'll get true immediately
        assert tester(),"Instantly true"
        assert tester.i==0,"After the first hit, we are at .i==0, saw %s" % tester.i

        # the next interval should be the first one
        start = time.monotonic()
        hit = None
        while not hit and time.monotonic()-start < 1:
            if tester():
                hit = time.monotonic()

        assert hit,"Should have hit"
        assert tester.i==1,"After the second hit, we are at .i==1, saw %s" % tester.i
        assert math.isclose(hit-start, 0.05, rel_tol=0.1, abs_tol=0.0), "1st elapsed ~0.05, actually %s" % (hit-start)

        # and double check that the 2nd is the second
        hit = None
        while not hit and time.monotonic()-start < 1:
            if tester():
                hit = time.monotonic()
        assert tester.i==0,"After the third hit, we are at .i==0, saw %s" % tester.i
        # actually we measure 1st+2nd here:
        assert math.isclose(hit-start, 0.15, rel_tol=0.1, abs_tol=0.0), "1st elapsed ~0.15, actually %s" % (hit-start)

    def testRunning(self):
        start = time.monotonic()
        tester = Every(0.05, 0)
        assert tester.running == False,"Timers aren't running till .start()"

        tester.start()
        assert tester.running == True,"Timers are running after .start()"

        hit = None
        while not hit and time.monotonic()-start < 1:
            if tester():
                hit = time.monotonic()
        assert hit
        assert tester.running == False,"Timers aren't running after last interval"

    def testEveries(self):
        # because Every takes time, we are going to test a bunch of things in parallel
        # I had to tune math.isclose( ... rel_tol=x ) to match my systems performance. yuk
        
        everies = []

        # periodics
        # we cause these to NOT fire instantly ( .start() ), so no 1st 0 duration:
        everies.append( (Every(0.1), 0.1, 0.1, 0.1) ) # also checks that it repeats
        everies.append( (Every(0.1, 0.15), 0.1, 0.15, 0.1, 0.15, 0.1) ) # also checks that it repeats
        # don't get too long, it takes the total just to run the tests!
        everies.append( (Every(0.1, 0.15, 0.2, 0.1), 0.1, 0.15, 0.2, 0.1, 0.1) )

        # durations, put a fake -1, 
        # which makes us keep trying for a firing, 
        # but means it shouldn't actually fire,
        # and which we handle special below
        everies.append( ( Every(0.1, 0), 0.1, -1 ))
        everies.append( ( Every(0.2, 0.15, 0.1, 0), 0.2, 0.15, 0.1, -1 ))

        start = time.monotonic()
        results = []
        done = False

        # avoid previous tests delaying the start (start is at construction time)
        for an_every, *want in everies:
            # Also, this causes it to NOT fire instantly
            an_every.start()

        while not done and time.monotonic()-start < 1.0:
            # will always run 1.0 seconds, because we don't try to test if everybody is finished
            i = 0
            done = True
            elapsed = time.monotonic()
            for an_every, *want in everies:
                if len( results ) <= i:
                    results.append( [ start ] ) # an extra for deltas!
                if len(results[i]) < len(want) + 1: # extra, and the rest
                    done = False
                    if an_every():
                        # just store the time, we'll "delta" it later
                        results[ i ].append( elapsed )
                        #print("  hit", i,elapsed-start,elapsed)
                i += 1

        for res_i,raw_result in enumerate(results):

            last = raw_result[0]
            #print("last", last)
            result = []
            for elapsed in raw_result[1:]:
                result.append( elapsed - last )
                #print("  delta %s ela %s last %s" % (elapsed - last, elapsed, last) )
                last = elapsed
            # for -1 being the "no more" marker, for duration/timers, make result have it
            if everies[res_i][-1] == -1:
                result.append(-1)
            #print( "[%s] %s SHOULD= %s" % (res_i,everies[res_i][1],result) )
            #print( "  raw",raw_result)
            
            an_every, *want = everies[res_i]

            self.do_intervals_match( '[%s]' % res_i, want, result )

    def do_intervals_match(self, prefix_msg, actual, want ):
        #print( "  e[]", want)
        isclose = []
        is_ok = True

        for i,an_actual in enumerate(actual):
            if len(want) > i:
                isclose.append( math.isclose(an_actual, want[i], rel_tol=0.1, abs_tol=0.001) )
                is_ok = is_ok and isclose[-1]

        assert is_ok and len(actual) == len(want), "Expected %s to be ~ %s, but got %s (%s)" % (prefix_msg, want, actual, isclose)

    def testLastIsStart(self):
        tester = Every(0.05)

        # again, instantly starts
        now = time.monotonic() - 0.05 
        assert math.isclose(tester.last-now, 0, rel_tol=0.01, abs_tol=0.001),"After constructor, expected .last == now, saw %s != %s " % (tester.last,now)
        time.sleep(0.05) # make things different
        tester.start()
        # But, .start() won't fire till first duration
        now = time.monotonic()
        # (test vs 0, because we really want to test digits of significance)
        assert math.isclose(tester.last-now, 0, rel_tol=0.01, abs_tol=0.001),"After .start(), expected .last == now, saw %s != %s " % (tester.last,now)

    def testStart(self):
        test_start = time.monotonic()

        hit_at = None
        while( time.monotonic() - test_start < 1):
            if self.start_tester():
                hit_at = time.monotonic()
                break
        assert hit_at, "Expected to expire at least once!" # sanity

    def testSetInterval(self):
        test_start = time.monotonic()

        unchanged = Every(0.05)
        changed = Every(0.05)
        changed.interval = 0.1

        hit_at = {
            'unchanged' : [],
            'changed' : [],
            }

        # let the slowest happen twice
        while( time.monotonic() - test_start < 0.24):
            if unchanged():
                #print("<<hit unchagned", time.monotonic() - test_start )
                hit_at['unchanged'].append( time.monotonic() - test_start )
            if changed():
                #print("<<hit chagned", time.monotonic() - test_start )
                hit_at['changed'].append( time.monotonic() - test_start )

        self.do_intervals_match( 'unchanged', hit_at['unchanged'], [ 0.0, 0.05, 0.1, 0.15, 0.2 ] )
        print( "ci", changed.interval)
        self.do_intervals_match( 'changed', hit_at['changed'], [ 0.0, 0.1, 0.2] )
        

if __name__ == "__main__":
    unittest.main() # run all tests
