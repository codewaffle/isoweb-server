from gevent import Greenlet

from scheduler import Scheduler


class Island(Greenlet):
    def __init__(self):
        super(Island, self).__init__()
        self.scheduler = Scheduler()

    def _run(self):
        self.scheduler.start()
        self.scheduler.schedule(func=self.update)
        self.scheduler.join()

    def update(self, dt):
        # print 'updated in', dt
        return 1/20.
