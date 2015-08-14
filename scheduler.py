from math import ceil
from queue import PriorityQueue
from isoweb_time import clock
import logbook
from twisted.internet.defer import inlineCallbacks
from util import sleep


logger = logbook.Logger(__name__)

class Scheduler:
    def __init__(self, resolution=1/40.):
        self.resolution = resolution
        self.queue = PriorityQueue()

    @inlineCallbacks
    def start(self):
        queue = self.queue

        while True:
            now = clock()
            while queue.queue[0][0] < now:
                # time desired, time when originally scheduled (used to compute dt), function, args, kwargs.
                try:
                    t, s, f, a, k = self.queue.get()
                except Exception as E:
                    logger.exception("IGNORING EXCEPTION WHILE GETTING")
                    print(t,s,f,a,k)

                d = now - s

                if a is not None:
                    if k is not None:
                        res = f(*a, **k)
                    else:
                        res = f(*a)
                elif k is not None:
                    res = f(**k)
                else:
                    res = f()

                if res:
                    if res > 0:
                        try:
                            queue.put((now + res, now, f, a, k))
                        except Exception as E:
                            logger.exception("IGNORING EXCEPTION WHILE PUTTING #0")
                            print((now + res, now, f, a, k))

                    else:  # negative reschedule supports fixed clock rate.
                        try:
                            queue.put((t - res, now, f, a, k))
                        except Exception as E:
                            logger.exception("IGNORING EXCEPTION WHILE PUTTING #1")
                            print(t-res, now, f, a, k)

            yield sleep(0.01)

    def schedule(self, at=None, wait=None, func=None, args=None, kwargs=None):
        # print 'scheduled', at, func, args, kwargs
        now = when = clock()

        if at:
            when = at
        elif wait:
            when += wait

        # snap it to our resolution
        when = ceil(when / self.resolution) * self.resolution

        self.queue.put((when, now, func, args, kwargs))
