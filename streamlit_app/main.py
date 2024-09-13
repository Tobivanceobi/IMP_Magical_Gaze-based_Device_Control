from time import sleep

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

        # Predict the objects in the frame
        results = object_detector.predict(frame)

        # Save the result image
        object_detector.save_result(results)

        # Display the result image
        result_img_path = object_detector.image_path
        result_img = Image.open(result_img_path)
        image_container.image(result_img)

