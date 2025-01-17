import numpy as np


def cross_product(v1, v2):
    return v1[0] * v2[1] - v1[1] * v2[0]

def is_point_in_triangle(p1, p2, p3, p):
    def sign(a, b, c):
        return (a[0] - c[0]) * (b[1] - c[1]) - (b[0] - c[0]) * (a[1] - c[1])

    b1 = sign(p, p1, p2) < 0.0
    b2 = sign(p, p2, p3) < 0.0
    b3 = sign(p, p3, p1) < 0.0

    return ((b1 == b2) and (b2 == b3))

class MovementTracker:

    def __init__(self, fixation_pos, origin_radius):
        self.fixation = np.array(fixation)

    def update(self, new_point, timestamp):

