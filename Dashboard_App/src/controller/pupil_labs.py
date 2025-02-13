import msgpack
import cv2
import numpy as np
import zmq
from PIL import Image
import socket
import toml


app_config = toml.load("config.toml")

def decode_dict(d):
    result = {}
    for key, value in d.items():
        if isinstance(key, bytes):
            key = key.decode()
        if isinstance(value, bytes):
            value = value.decode()
        elif isinstance(value, dict):
            value = decode_dict(value)
        result.update({key: value})
    return result


class PupilLabsController:
    TOPIC_GAZE = app_config["pupil_topics"]["gaze"]
    TOPIC_FRAME_WORLD = app_config["pupil_topics"]["front_camera"]
    SERVICE_HOST = app_config["pupil_service"]["host"]
    SERVICE_PORT = app_config["pupil_service"]["port"]

    def __init__(self):
        if self.is_service_online():
            self.ctx = zmq.Context()
            self.sub_port, self.pub_port = self.__get_sub_pub_ports()

            self.gaze_socket = self.__create_pupil_sub_socket(self.TOPIC_GAZE)
            self.frame_world_socket = self.__create_pupil_sub_socket(self.TOPIC_FRAME_WORLD)

    def reconnect_sockets(self):
        self.gaze_socket.close()
        self.frame_world_socket.close()
        self.gaze_socket = self.__create_pupil_sub_socket(self.TOPIC_GAZE)
        self.frame_world_socket = self.__create_pupil_sub_socket(self.TOPIC_FRAME_WORLD)

    def receive_gaze_data(self, num_gazes=1):
        gazes = []
        for _ in range(num_gazes):
            topic, payload = self.gaze_socket.recv_multipart()
            message = msgpack.loads(payload)

            # Decode the message
            gaze = decode_dict(message)
            gaze["base_data"] = [decode_dict(data) for data in gaze["base_data"]]

            gazes.append(gaze)
        return gazes

    def receive_gaze_data_duration(self, duration):
        gazes = []
        topic, payload = self.gaze_socket.recv_multipart()
        message = msgpack.loads(payload)
        gaze = decode_dict(message)
        gaze["base_data"] = [decode_dict(data) for data in gaze["base_data"]]
        gazes.append(gaze)

        start_time = gaze["timestamp"]
        dur = 0
        while dur < duration:
            topic, payload = self.gaze_socket.recv_multipart()
            message = msgpack.loads(payload)
            gaze = decode_dict(message)
            gaze["base_data"] = [decode_dict(data) for data in gaze["base_data"]]
            gazes.append(gaze)
            dur = gaze["timestamp"] - start_time
        return gazes

    def receive_cam_frames(self, num_frames=1):
        frames = []
        for _ in range(num_frames):
            _, _, payload = self.frame_world_socket.recv_multipart()

            # Decode the image
            frame = cv2.imdecode(np.frombuffer(payload, dtype=np.uint8), cv2.IMREAD_COLOR)

            # Convert the image to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            frame = Image.fromarray(frame)
            frames.append(frame)
        return frames

    def close_connection(self):
        self.ctx.term()

    def is_service_online(self):
        """Check if the service is online by attempting to connect to it."""
        try:
            # Create a socket object
            with socket.create_connection((self.SERVICE_HOST, self.SERVICE_PORT), timeout=5):
                return True  # Service is online
        except (socket.timeout, ConnectionRefusedError):
            return False  # Service is offline or not reachable

    def __create_pupil_sub_socket(self, topic=None):
        pupil_socket = self.ctx.socket(zmq.SUB)
        pupil_socket.connect(f'tcp://{self.SERVICE_HOST}:{self.sub_port}')
        pupil_socket.subscribe(topic)
        return pupil_socket

    def __create_pupil_req_socket(self):
        pupil_socket = self.ctx.socket(zmq.REQ)
        pupil_socket.connect(f'tcp://{self.SERVICE_HOST}:{self.SERVICE_PORT}')
        return pupil_socket

    def __get_sub_pub_ports(self):
        pupil_socket = self.__create_pupil_req_socket()

        pupil_socket.send_string('SUB_PORT')
        sub_port = pupil_socket.recv_string()

        pupil_socket.send_string('PUB_PORT')
        pub_port = pupil_socket.recv_string()

        pupil_socket.close()

        return sub_port, pub_port


