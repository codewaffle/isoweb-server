def try_len(n):
    try:
        return len(n)
    except:
        return n


class Node(object):
    __slots__ = ('x', 'y', 'w', 'hw', 'd', 'p', 'nodes', 'items')

    def __init__(self, x, y, w, d, p):
        self.x = x
        self.y = y
        self.w = w
        self.hw = w/2
        self.d = d
        self.p = p

        self.nodes = None
        self.items = set()

    def __repr__(self):
        return 'Node({}, {}, {}, num_items={}, num_nodes={})'.format(
            self.x, self.y, self.d,
            try_len(self.items),
            try_len(self.nodes)
        )

    def subdivide(self, n=1):
        qw = self.hw / 2
        nd = self.d + 1

        #
        # 2 -/+ | 3 +/+
        # -----
        # 0 -/- | 1 +/-
        #
        self.nodes = True

        self.nodes = [
            Node(self.x - qw, self.y - qw, self.hw, nd, self),
            Node(self.x + qw, self.y - qw, self.hw, nd, self),
            Node(self.x - qw, self.y + qw, self.hw, nd, self),
            Node(self.x + qw, self.y + qw, self.hw, nd, self),
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
        assert self.x == 0
        assert self.y == 0

        self.w *= 2
        self.hw *= 2

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

    def insert(self, item):
        if self.nodes:
            if item.y < self.y:
                if item.x < self.x:
                    return self.nodes[0].insert(item)
                else:
                    return self.nodes[1].insert(item)
            else:
                if item.x < self.x:
                    return self.nodes[2].insert(item)
                else:
                    return self.nodes[3].insert(item)

        self.items.add(item)
        item.node = self

        if len(self.items) >= 5:
            self.subdivide()

    def remove(self, item):
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

class NodeItem(object):
    def __init__(self):
        self.node = None
        self.x = 0
        self.y = 0

    def update_quadtree(self):
        node = self.node

        while node.x + node.hw < self.x or \
            node.x - node.hw > self.x or \
            node.y + node.hw < self.y or \
            node.y - node.hw > self.y:

            if node.p is None:
                node.expand()
            else:
                node = node.p

        if node != self.node:
            self.node.remove(self)
            node.insert(self)


class Quadtree(object):
    def __init__(self):
        self.root = Node(0, 0, 65536, 0, None)

    def insert(self, item):
        self.root.insert(item)
