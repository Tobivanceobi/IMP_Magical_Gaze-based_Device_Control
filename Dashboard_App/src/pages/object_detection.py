import cv2
import numpy as np
import streamlit as st
from PIL import Image

from ..controller.pupil_labs import PupilLabsController
from ..models.model_obj_detection import YoloObjectDetector
from ..utils import Page


class PageObjectDetection(Page):
    NAME = "Object Detection"
    MODEL_PATH = '../.local/yolov8n.pt'
    def __init__(self):
        self.controller = PupilLabsController()

    def write(self):
        st.title(self.NAME)
        if not self.controller.is_service_online():
            st.subheader("Connection to EyeTracker can not be established.")
            st.text("Start the Pupil Core and Pupil Service before running the object detection.")
            return

        st.subheader("Pupil Core Object Detection")


        # create a two column row
        col1, col2 = st.columns(2)

        with col1:
            enable_gaze_point = st.checkbox("Enable Gaze Point", value=True)

        with col2:
            if enable_gaze_point:
                num_points = st.number_input("Number of Points", min_value=1, max_value=10, value=1)

        col1, col2 = st.columns(2)

        with col1:
            start_btn = st.button("Start Object Detection")

        with col2:
            stop_btn = st.button("Stop Object Detection")

        text_container = st.empty()
        image_container = st.empty()

        if start_btn:
            obj_detector = YoloObjectDetector(model_path=self.MODEL_PATH)
            while not stop_btn:
                self.controller.reconnect_sockets()
                gaze_data = self.controller.receive_gaze_data(num_gazes=num_points)
                frame = self.controller.receive_cam_frames(num_frames=1)

                gaze_points = [gd['norm_pos'] for gd in gaze_data]

                gaze_points = np.array(gaze_points)
                mean_gaze = np.mean(gaze_points, axis=0)
                std_gaze = np.std(gaze_points, axis=0)
                gaze_points = gaze_points[np.all(np.abs(gaze_points - mean_gaze) < 2 * std_gaze, axis=1)]
                mean_gaze = np.mean(gaze_points, axis=0)

                results = obj_detector.predict(frame)
                curr_object = "Nothing"
                for result in results:
                    boxes = result.boxes
                    # print the names of the objects detected
                    classes = boxes.cls
                    # print the names of the objects detected
                    for c in classes:
                        print(f"Names: {result.names[int(c)]}")
                    for i, box in enumerate(boxes.xyxyn):
                        if box[0] <= mean_gaze[0] <= box[2] and box[1] <= (1 - mean_gaze[1]) <= box[3]:
                            curr_object = result.names[int(classes[i])]

                # Display the current object
                text_container.text(f"Current Object: {curr_object}")

                image = obj_detector.plot_result(results)[0]
                # convert the image to PLI image
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                if 0 <= mean_gaze[0] <= 1 and 0 <= mean_gaze[1] <= 1:
                    # Calculate the gaze point coordinates (flip the y-axis)
                    gaze_x, gaze_y = int(mean_gaze[0] * image.shape[1]), int(
                        (1 - mean_gaze[1]) * image.shape[0])

                    # Draw a circle at the gaze point
                    cv2.circle(image, (gaze_x, gaze_y), 10, (250, 0, 0), -1)

                image_container.image(image)

