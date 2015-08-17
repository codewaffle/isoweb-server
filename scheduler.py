from math import ceil
from queue import PriorityQueue
from isoweb_time import clock
import logbook
from twisted.internet.defer import inlineCallbacks
from util import sleep


logger = logbook.Logger(__name__)

class Scheduler:
    def __init__(self, resolution=1/100.):
        self.resolution = resolution
        self.queue = PriorityQueue()
        self._next_task_id = 0

    def next_task_id(self):
        self._next_task_id += 1
        return self._next_task_id

    @inlineCallbacks
    def start(self):
        queue = self.queue

        while True:
            now = clock()

            while queue.queue[0][0] < now:
                # time desired, time when originally scheduled (used to compute dt), function, args, kwargs.
                t, i, s, f, a, k = self.queue.get()

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
                        queue.put((now + res, i, now, f, a, k))
                    else:  # negative reschedule supports fixed clock rate.
                        queue.put((t - res, i, now, f, a, k))

            yield sleep(self.resolution/4.)

    def schedule(self, at=None, wait=None, func=None, args=None, kwargs=None):
        # print 'scheduled', at, func, args, kwargs
        now = when = clock()

        if at:
            when = at
        elif wait:
            when += wait

        # snap it to our resolution
        when = ceil(when / self.resolution) * self.resolution

        self.queue.put((when, self.next_task_id(), now, func, args, kwargs))
