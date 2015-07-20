from collections import defaultdict
from random import random
from time import time
from component import BaseComponent
from entity import ObFlags


class NetworkViewer(BaseComponent):
    data = {
        'socket': None,
        'visibility_radius': 300
    }

    @classmethod
    def gather(cls, entity, data):
        entity.Position.find_nearby(data.visibility_radius, flags=ObFlags.REPLICATE)


class NetworkManager(BaseComponent):
    """
    Lives on any entity that has a network representation.. responsible for stuff.
    """
    @classmethod
    def initialize(cls, entity, data):
        entity.ob.flags |= ObFlags.REPLICATE
        entity.cache.network_last = time()
        entity.scheduler.schedule(func=entity.NetworkManager.update)

    @classmethod
    def update(cls, entity, data, dt):
        print 'replicate, wait 5s, waited: ', dt
        return -5.5 + random()


