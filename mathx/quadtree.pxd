from mathx.aabb cimport AABB
from mathx.vector2 cimport Vector2

cdef class Node:
    cdef public:
        AABB box
        int d
        Node p
        list nodes
        set items

cdef class NodeItem:
    cdef public:
        Node node
        Vector2 pos

cdef class Quadtree:
    cdef public Node root
