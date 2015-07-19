from mathx.aabb import AABB
from mathx.vector2 import Vector2

def try_len(n):
    try:
        return len(n)
    except:
        return n


cdef class Node:
    def __init__(self, box, d, p):
        self.box = box
        self.d = d
        self.p = p

        self.nodes = None
        self.items = set()

    def __repr__(self):
        return 'Node({}, {}, num_items={}, num_nodes={})'.format(
            self.box, self.d,
            try_len(self.items),
            try_len(self.nodes)
        )

    def index(self, Vector2 point):
        if point.y < self.box.center.y:
            if point.x < self.box.center.x:
                return 0
            else:
                return 1
        else:
            if point.x < self.box.center.x:
                return 2
            else:
                return 3

    def subdivide(self, n=1):
        qw = self.box.hwidth / 2
        nd = self.d + 1

        #
        # 2 -/+ | 3 +/+
        # -----
        # 0 -/- | 1 +/-
        #
        self.nodes = True

        self.nodes = [
            Node(AABB(Vector2(self.box.center.x - qw, self.box.center.y - qw), qw), nd, self),
            Node(AABB(Vector2(self.box.center.x + qw, self.box.center.y - qw), qw), nd, self),
            Node(AABB(Vector2(self.box.center.x - qw, self.box.center.y + qw), qw), nd, self),
            Node(AABB(Vector2(self.box.center.x + qw, self.box.center.y + qw), qw), nd, self),
        ]

        x = self.items
        self.items = None

        if n > 1:
            for node in self.nodes:
                node.subdivide(n - 1)

        if x:
            for item in x:
                self.insert(item)

    def expand(self):
        assert self.p is None

        self.box.hwidth *= 2

        if self.nodes:
            prev = self.nodes[:]

            self.subdivide(2)

            # reattach manually for maximum speed
            n0 = self.nodes[0].nodes[3] = prev[0]
            n1 = self.nodes[1].nodes[2] = prev[1]
            n2 = self.nodes[2].nodes[1] = prev[2]
            n3 = self.nodes[3].nodes[0] = prev[3]

            n0.p = self.nodes[0]
            n1.p = self.nodes[1]
            n2.p = self.nodes[2]
            n3.p = self.nodes[3]

    def insert(self, NodeItem item):
        if self.nodes:
            index = self.index(item.pos)
            self.nodes[index].insert(item)
            return

        self.items.add(item)
        item.node = self

        if len(self.items) >= 8 and self.box.hwidth > 1:
            self.subdivide()

    def remove(self, NodeItem item):
        item.node = None

        self.items.remove(item)

        if self.p and not self.items:
            self.p.check_collapse()

    def check_collapse(self):
        """
        Check if < threshold items are in subnodes.. if so, steal them and demolish the subnodes.
        :return:
        """
        items = set()

        assert bool(self.nodes)

        for n in self.nodes:
            if n.nodes:  # subnodes? don't collapse
                return

            if n.items:
                items |= n.items

        if len(items) < 5:
            self.nodes = None
            self.items = set()

            for i in items:
                self.insert(i)

            self.nodes = None

    def _q_aabb(self, AABB aabb, set output):
        # completely outside of this quad
        if not self.box.intersects(aabb):
            return

        if self.items:
            output |= set((i for i in self.items if aabb.contains(i.pos)))
            return

        if self.nodes:
            for n in self.nodes:
                n._q_aabb(aabb, output)
            return

cdef class NodeItem:
    def __init__(self):
        self.node = None
        self.pos = Vector2(0, 0)

    def update_quadtree(self):
        node = self.node

        while not node.box.contains(self.pos):
            if node.p is None:
                node.expand()
            else:
                node = node.p

        if node != self.node:
            self.node.remove(self)
            node.insert(self)


cdef class Quadtree:
    def __init__(self):
        self.root = Node(AABB(Vector2(0, 0), 65536), 0, None)

    def insert(self, NodeItem item):
        self.root.insert(item)

    def query_aabb(self, AABB aabb):
        result = set()
        self.root._q_aabb(aabb, result)
        return result
