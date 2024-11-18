import numpy as np
import zmq
import msgpack


class MovementTracker:

    def __init__(self, origin_point, threshold, min_move_dist=None, epsilon=None):
        """
        Initializes the movement tracker.

        Parameters:
            origin_point (tuple): The (x, y) coordinates of the origin.
            threshold (float): Minimum distance between two points to be considered a movement.
            epsilon (float): Tolerance for checking if the final point returns to the origin.
            min_move_dist (list): Minimum distance for a movement to be considered significant.
        """
        self.origin = np.array(origin_point)
        self.threshold = threshold
        self.min_move_dist = min_move_dist
        self.epsilon = epsilon
        self.direction = None
        self.data_buffer = [self.origin]
        self.displacements = []
        self.movement_detected = False
        self.out_of_bounds_count = 0

    def _detect_direction(self, displacement):
        """
        Detects the direction of movement based on the displacement.

        Parameters:
            displacement (np.ndarray): The x, y displacement vector.

        Returns:
            str: 'up', 'down', 'left', 'right', or None.
        """
        if abs(displacement[0]) > abs(displacement[1]):  # Horizontal movement
            return 'left' if displacement[0] > 0 else 'right'
        else:  # Vertical movement
            return 'down' if displacement[1] > 0 else 'up'

    def update(self, new_point):
        """
        Updates the tracker with a new point and analyzes movement.

        Parameters:
            new_point (tuple): The (x, y) coordinates of the new data point.

        Returns:
            dict: A dictionary with keys:
                - 'moved': True if a significant movement was detected, False otherwise.
                - 'direction': The detected direction of movement ('up', 'down', 'left', 'right', or None).
                - 'returned': True if the movement is complete, False otherwise.
        """

        new_point = np.array(new_point)
        self.data_buffer.append(new_point)

        # Calculate the last displacement
        displacement_last = new_point - self.data_buffer[-2]
        distance_last = np.linalg.norm(displacement_last)

        # Determine direction of movement
        displacement_origin = new_point - self.origin
        self.displacements.append(displacement_origin)

        distances = [np.linalg.norm(displacement) for displacement in self.displacements]
        self.direction = self._detect_direction(self.displacements[distances.index(max(distances))])
        if self.direction in ['up', 'down']:
            if max(distances) > self.min_move_dist[0] and np.linalg.norm(displacement_origin) <= self.epsilon:
                return {'moved': True, 'direction': self.direction, 'returned': True}
        else:
            if max(distances) > self.min_move_dist[1] and np.linalg.norm(displacement_origin) <= self.epsilon:
                return {'moved': True, 'direction': self.direction, 'returned': True}

        return {'moved': True, 'direction': self.direction, 'returned': False}
