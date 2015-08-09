import asyncio
from math import ceil
from queue import PriorityQueue
from time import time, clock, sleep


class Scheduler:
    def __init__(self, resolution=1/40.):
        super(Scheduler, self).__init__()
        self.resolution = resolution
        self.queue = PriorityQueue()

    def start(self):
        queue = self.queue

        while True:
            now = clock()
            while queue.queue[0][0] < now:
                # time desired, time when originally scheduled (used to compute dt), function, args, kwargs.
                t, s, f, a, k = self.queue.get()
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
                        queue.put((now + res, now, f, a, k))
                    else:  # negative reschedule supports fixed clock rate.
                        queue.put((t - res, now, f, a, k))

            sleep(0.1)
            print('.')

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
