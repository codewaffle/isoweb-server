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

        self.node0 = None
        self.node1 = None
        self.node2 = None
        self.node3 = None

        self.items = set()

    def __repr__(self):
        return 'Node({}, {}, num_items={}, nodes={})'.format(
            self.box, self.d,
            try_len(self.items),
            self.node0 is not None
        )

    cdef int index(self, Vector2 point):
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

    cdef Node subnode(self, Vector2 point):
        if point.y < self.box.center.y:
            if point.x < self.box.center.x:
                return self.node0
            else:
                return self.node1
        else:
            if point.x < self.box.center.x:
                return self.node2
            else:
                return self.node3


    cdef subdivide(self, int n=1):
        qw = self.box.hwidth / 2
        nd = self.d + 1

        #
        # 2 -/+ | 3 +/+
        # -----
        # 0 -/- | 1 +/-
        #

        self.node0 = Node(AABB(Vector2(self.box.center.x - qw, self.box.center.y - qw), qw), nd, self)
        self.node1 = Node(AABB(Vector2(self.box.center.x + qw, self.box.center.y - qw), qw), nd, self)
        self.node2 = Node(AABB(Vector2(self.box.center.x - qw, self.box.center.y + qw), qw), nd, self)
        self.node3 = Node(AABB(Vector2(self.box.center.x + qw, self.box.center.y + qw), qw), nd, self)

        x = self.items
        self.items = None

        if n > 1:
            self.node0.subdivide(n-1)
            self.node1.subdivide(n-1)
            self.node2.subdivide(n-1)
            self.node3.subdivide(n-1)

        if x:
            for item in x:
                self.insert(item)

    def expand(self):
        assert self.p is None

        self.box.hwidth *= 2

        if self.node0:
            prev = self.node0, self.node1, self.node2, self.node3

            self.subdivide(2)

            # reattach manually for maximum speed
            n0 = self.node0.node3 = prev[0]
            n1 = self.node1.node2 = prev[1]
            n2 = self.node2.node1 = prev[2]
            n3 = self.node3.node0 = prev[3]

            n0.p = self.node0
            n1.p = self.node1
            n2.p = self.node2
            n3.p = self.node3

    def get_node(self, index):
        if index == 0:
            return self.node0
        if index == 1:
            return self.node1
        if index == 2:
            return self.node2
        if index == 3:
            return self.node3

    def insert(self, NodeItem item):
        if self.node0:
            self.subnode(item.pos).insert(item)
            return

        self.items.add(item)
        item.node = self

        if len(self.items) >= 5 and self.box.hwidth >= 2:
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
        assert bool(self.node0)

        # do not collapse nodes with subnodes
        if self.node0.node0 or self.node1.node0 or self.node2.node0 or self.node3.node0:
            return

        items = self.node0.items | self.node1.items | self.node2.items | self.node3.items

        if len(items) < 5:
            self.items = items

            for i in items:
                i.node = self

            self.node0 = self.node1 = self.node2 = self.node3 = None

    cdef void q_aabb(self, AABB aabb, set output, int flags):
        # completely outside of this quad
        if not self.box.intersects(aabb):
            return

        if self.items:
            output |= {i for i in self.items if flags & i.flags == flags and aabb.contains(i.pos)}
            return

        if self.node0:
            self.node0.q_aabb(aabb, output, flags)
            self.node1.q_aabb(aabb, output, flags)
            self.node2.q_aabb(aabb, output, flags)
            self.node3.q_aabb(aabb, output, flags)
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

    cdef query_aabb(self, AABB aabb, int flags):
        cdef set result = set()
        self.root.q_aabb(aabb, result, flags)
        return result

    cpdef query_aabb_ents(self, AABB aabb, set exclude, int flags):
        cdef set result = {i.ent for i in self.query_aabb(aabb, flags)}

        if exclude:
            result -= exclude

        return result
