from collections import defaultdict
from time import time
from component import BaseComponent


class NetworkViewer(BaseComponent):
    data = {
        'socket': None,
        'visibility_radius': 300
    }


class NetworkData(BaseComponent):
    """
    everything that has a transform will have a NetworkVars..
    NetworkView will only see NetworkVars :/
    need to move quadtree shittles here maybe.. maybe not. maybe two quadtrees!

    (i'm actually thinking a few quadtrees, one per priority level.. as the higher priorities would be much more
    sparsely populated the performance hit should be low)
    """
    data = {

    }
