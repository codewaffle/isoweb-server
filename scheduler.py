from time import time
from gevent import Greenlet, sleep
from gevent.queue import PriorityQueue


class Scheduler(Greenlet):
    def __init__(self, resolution=1/40.):
        super(Scheduler, self).__init__()
        self.resolution = resolution
        self.queue = PriorityQueue()

    def _run(self):
        queue = self.queue
        resolution = self.resolution

        while True:
            now = time()
            while queue.peek()[0] < now:
                # time desired, time when originally scheduled (used to compute dt), function, args, kwargs.
                t, s, f, a, k = self.queue.get()
                d = now - s

                if a is not None:
                    if k is not None:
                        res = f(d, *a, **k)
                    else:
                        res = f(d, *a)
                elif k is not None:
                    res = f(d, **k)
                else:
                    res = f(d)

                if res:
                    if res > 0:
                        queue.put((now + res, now, f, a, k))
                    else:  # negative reschedule supports fixed clock rate.
                        queue.put((t - res, now, f, a, k))

            sleep(resolution)

    def schedule(self, at=None, wait=None, func=None, args=None, kwargs=None):
        # print 'scheduled', at, func, args, kwargs
        now = when = time()

        if at:
            when = at
        elif wait:
            when += wait

        self.queue.put((when, now, func, args, kwargs))
