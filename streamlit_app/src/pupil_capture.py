import pandas as pd
import zmq
import cv2
import numpy as np
from PIL import Image
import msgpack


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



    def receive_frame_world_image(self, num_frames=1):
        sub_frame_world = self.ctx.socket(zmq.SUB)
        sub_frame_world.connect(f'tcp://{self.ip}:{self.sub_port}')
        sub_frame_world.subscribe("frame.world")

        frames = []
        for _ in range(num_frames):
            frame = sub_frame_world.recv_multipart()
            image_bytes = frame[2]
            decoded_frame = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            rgb_frame = cv2.cvtColor(decoded_frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb_frame)
            frames.append(img)
        return frames

    def receive_gaze_position_information(self, num_gazes=1):
        subscriber = self.ctx.socket(zmq.SUB)
        subscriber.connect(f'tcp://{self.ip}:{self.sub_port}')
        subscriber.subscribe('gaze.')  # receive all gaze messages

        gazes = []
        for _ in range(num_gazes):
            topic, payload = subscriber.recv_multipart()
            message = msgpack.loads(payload)
            gaze = message['norm_pos'.encode()]
            gazes.append(gaze)
        return gazes

    def receive_gaze_information(self, num_gazes=1):
        subscriber = self.ctx.socket(zmq.SUB)
        subscriber.connect(f'tcp://{self.ip}:{self.sub_port}')
        subscriber.subscribe('gaze.')

        topic, payload = subscriber.recv_multipart()
        message = msgpack.loads(payload)

        data = {
            'gazeOrigin_x': message[b'eye_centers_3d'][b'0'][0],
            'gazeOrigin_y': message[b'eye_centers_3d'][b'0'][1],
            'gazeOrigin_z': message[b'eye_centers_3d'][b'0'][2],
            'gazeDirection_x': message[b'gaze_normals_3d'][b'0'][0],
            'gazeDirection_y': message[b'gaze_normals_3d'][b'0'][1],
            'gazeDirection_z': message[b'gaze_normals_3d'][b'0'][2],
            'gazePoint_x': message[b'gaze_point_3d'][0],
            'gazePoint_y': message[b'gaze_point_3d'][1],
            'gazePoint_z': message[b'gaze_point_3d'][2]
        }
        gaze_info = pd.DataFrame(data, index=[0])

        for _ in range(num_gazes - 1):
            topic, payload = subscriber.recv_multipart()
            message = msgpack.loads(payload)
            data = pd.DataFrame({
                'gazeOrigin_x': message[b'eye_centers_3d'][b'0'][0],
                'gazeOrigin_y': message[b'eye_centers_3d'][b'0'][1],
                'gazeOrigin_z': message[b'eye_centers_3d'][b'0'][2],
                'gazeDirection_x': message[b'gaze_normals_3d'][b'0'][0],
                'gazeDirection_y': message[b'gaze_normals_3d'][b'0'][1],
                'gazeDirection_z': message[b'gaze_normals_3d'][b'0'][2],
                'gazePoint_x': message[b'gaze_point_3d'][0],
                'gazePoint_y': message[b'gaze_point_3d'][1],
                'gazePoint_z': message[b'gaze_point_3d'][2]
            }, index=[0])
            gaze_info = pd.concat([gaze_info, data], ignore_index=True)
        return gaze_info