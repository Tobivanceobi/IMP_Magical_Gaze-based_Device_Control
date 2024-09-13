from time import sleep

import cv2
import numpy as np
import streamlit as st
from ultralytics import YOLO
from PIL import Image
import io
from src.pupil_capture import PupilCapture
from src.model import ObjectDetector

pupil_remote = PupilCapture()
object_detector = ObjectDetector(model_path=".local/yolov8n.pt")

# create a start button in streamlit
start_button = st.button("Start Pupil Capture")
stop_button = st.button("Stop Pupil Capture")

# create a image container in streamlit
image_container = st.empty()

if start_button:
    while not stop_button:
        sleep(0.01)

        # Receive the frame from the Pupil Capture
        frame = pupil_remote.receive_frame_world_image()
        gaze = pupil_remote.receive_gaze_information()

        # Predict the objects in the frame
        results = object_detector.predict(frame)

        # Save the result image
        object_detector.save_result(results)

        # Display the result image
        result_img_path = object_detector.image_path
        result_img = Image.open(result_img_path)

        result_img_array = cv2.cvtColor(np.array(result_img), cv2.COLOR_RGB2BGR)

        if 0 <= gaze[0] <= 1 and 0 <= gaze[1] <= 1:
            # Convert normalized gaze coordinates to pixel coordinates
            # Flip the y-axis as the origin (0, 0) is in the top-left corner in OpenCV
            gaze_x, gaze_y = int(gaze[0] * result_img_array.shape[1]), int((1 - gaze[1]) * result_img_array.shape[0])

            # Draw a circle at the gaze point
            cv2.circle(result_img_array, (gaze_x, gaze_y), 20, (0, 0, 255), -1)

        result_img = Image.fromarray(cv2.cvtColor(result_img_array, cv2.COLOR_BGR2RGB))

        image_container.image(result_img)

