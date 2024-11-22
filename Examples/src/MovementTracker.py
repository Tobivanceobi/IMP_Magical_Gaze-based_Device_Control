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

    def __init__(self, fixation, threshold, min_dist, max_dist, epsilon=None):
        """
        Initializes the movement tracker.

        Parameters:
            origin_point (tuple): The (x, y) coordinates of the origin.
            threshold (int): accepted number of points out of min_dist and max_dist.
            epsilon (float): Tolerance for checking if the final point returns to the origin.
            min_dist (float): Minimum distance for a significant movement.
            max_dist (float): Maximum distance for a significant movement.
        """
        self.origin = np.array(fixation['norm_pos'])
        self.origin_time = fixation['timestamp']

        # Areal markings for a box around the origin
        self.l_1 = [self.origin[0] - 2, self.origin[1] + 2]
        self.l_2 = [self.origin[0] - 2, self.origin[1] - 2]
        self.r_1 = [self.origin[0] + 2, self.origin[1] + 2]
        self.r_2 = [self.origin[0] + 2, self.origin[1] - 2]

        self.threshold = threshold
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.epsilon = epsilon
        self.direction = None
        self.data_buffer = [self.origin]
        self.distances = []
        self.movement_detected = False
        self.out_of_bounds_count = 0

    def _detect_direction(self, point):
        if is_point_in_triangle(self.l_2, self.l_1, self.origin, point):
            return "right"
        elif is_point_in_triangle(self.r_2, self.r_1, self.origin, point):
            return "left"
        elif is_point_in_triangle(self.l_1, self.r_1, self.origin, point):
            return "down"
        elif is_point_in_triangle(self.l_2, self.r_2, self.origin, point):
            return "up"
        else:
            return self.direction

    def update(self, new_point, timestamp):
        """
        Updates the tracker with a new point and analyzes movement.

        Parameters:
            new_point (tuple): The (x, y) coordinates of the new data point.
            timestamp (int): The timestamp of the new data point.

        Returns:
            dict: A dictionary with keys:
                - 'moved': True if a significant movement was detected, False otherwise.
                - 'direction': The detected direction of movement ('up', 'down', 'left', 'right', or None).
                - 'returned': True if the movement is complete, False otherwise.
        """

        new_point = np.array(new_point)
        displacement = self.origin - new_point
        distance = np.linalg.norm(displacement)

        displacement = self.data_buffer[-1] - new_point
        distance_last = np.linalg.norm(displacement)
        if self.min_dist > distance_last or distance_last > self.max_dist:
            timm_dif = timestamp - self.origin_time
            if timm_dif >= self.threshold:
                return None
            return {'moved': False, 'direction': None, 'returned': False}

        self.origin_time = timestamp
        self.data_buffer.append(new_point)
        self.distances.append(distance)

        if max(self.distances) > 0.2:
            self.movement_detected = True
            self.direction = self._detect_direction(new_point)
            if np.linalg.norm(new_point - self.origin) <= self.epsilon:
                return {'moved': True, 'direction': self.direction, 'returned': True}

            return {'moved': True, 'direction': self.direction, 'returned': False}

        return {'moved': False, 'direction': None, 'returned': False}
