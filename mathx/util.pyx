from pymunk import Vec2d

def lerp_vec2d(a, b, t):
    return Vec2d(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)