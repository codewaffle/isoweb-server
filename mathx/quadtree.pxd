from mathx.aabb cimport AABB
from mathx.vector2 cimport Vector2

cdef class Node:
    cdef public AABB box
    cdef public int d
    cdef public Node p

    cdef public Node node0, node1, node2, node3
    cdef subdivide(self, int n=*)

    cdef public set items
    cdef void q_aabb(self, AABB aabb, set output, int flags)
    cdef int index(self, Vector2 point)
    cdef Node subnode(self, Vector2 point)

cdef class NodeItem:
    cdef public Node node
    cdef public Vector2 pos
    cdef public int flags

cdef class Quadtree:
    cdef public Node root
    cdef query_aabb(self, AABB aabb, int flags)
    cpdef query_aabb_ents(self, AABB aabb, set exclude, int flags)
