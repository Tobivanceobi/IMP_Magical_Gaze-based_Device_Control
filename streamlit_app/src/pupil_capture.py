import zmq
import cv2
import numpy as np
from PIL import Image


class PupilCapture:

    def __init__(self, ip='localhost', port=50020):
        self.ctx = zmq.Context()
        # The REQ talks to Pupil remote and receives the session unique IPC SUB PORT
        self.pupil_remote = self.ctx.socket(zmq.REQ)
        self.ip = ip

        self.pupil_remote.connect(f'tcp://{self.ip}:{port}')

        # Request 'SUB_PORT' for reading data
        self.pupil_remote.send_string('SUB_PORT')
        self.sub_port = self.pupil_remote.recv_string()

        # Request 'PUB_PORT' for writing data
        self.pupil_remote.send_string('PUB_PORT')
        self.pub_port = self.pupil_remote.recv_string()



    def receive_frame_world_image(self):
        sub_frame_world = self.ctx.socket(zmq.SUB)
        sub_frame_world.connect(f'tcp://{self.ip}:{self.sub_port}')
        sub_frame_world.subscribe("frame.world")
        frame = sub_frame_world.recv_multipart()
        image_bytes = frame[2]
        decoded_frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        rgb_frame = cv2.cvtColor(decoded_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        return img