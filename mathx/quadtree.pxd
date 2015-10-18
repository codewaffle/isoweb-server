from mathx.aabb cimport AABB
from mathx.vector2 cimport Vector2

cdef class Node:
    cdef public AABB box
    cdef public int d
    cdef public Node p

    cdef public Node node0, node1, node2, node3
    cdef subdivide(self, int n=*)
    cdef expand(self)

    cdef Node get_node(self, int index)

    cdef insert(self, NodeItem)
    cdef remove(self, NodeItem)

    cdef check_collapse(self)


    cdef public set items
    cdef void q_aabb(self, AABB aabb, set output, int flags)
    cdef int index(self, Vector2 point)
    cdef Node point_subnode(self, Vector2 point)
    cdef Node aabb_subnode(self, AABB aabb)

cdef class NodeItem:
    cdef public Node node
    cdef public Vector2 pos
    cdef public int flags

cdef class Quadtree:
    cdef public Node root
    cdef query_aabb(self, AABB aabb, int flags)
    cpdef query_aabb_ents(self, AABB aabb, set exclude, int flags, set components)
