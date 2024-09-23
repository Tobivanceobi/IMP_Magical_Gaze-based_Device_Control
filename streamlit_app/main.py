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

# create a streamlit text container
text_container = st.empty()

# create a image container in streamlit
image_container = st.empty()



if start_button:

    gaze_colors = [(55, 155, 255), (79, 55, 255), (170, 55, 255), (255, 55, 255), (0, 0, 255)]
    while not stop_button:
        sleep(0.01)

        # Receive the frame from the Pupil Capture
        frame = pupil_remote.receive_frame_world_image()
        gaze_points = []
        for _ in range(3):
            gaze = pupil_remote.receive_gaze_information()
            gaze_points.append(gaze)

        # remove point if distance two mean is grater than 2 times the standard deviation
        gaze_points = np.array(gaze_points)
        mean_gaze = np.mean(gaze_points, axis=0)
        std_gaze = np.std(gaze_points, axis=0)
        gaze_points = gaze_points[np.all(np.abs(gaze_points - mean_gaze) < 2 * std_gaze, axis=1)]



        # Predict the objects in the frame
        curr_object = "Nothing"
        results = object_detector.predict(frame)
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            masks = result.masks  # Masks object for segmentation masks outputs
            keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            obb = result.obb
            # print(f"Boxes: {boxes.xyxyn}")
            # print the names of the objects detected
            classes = boxes.cls
            # print the names of the objects detected
            for c in classes:
                print(f"Names: {result.names[int(c)]}")

            # if the mean gaze of the last 5 points is within the bounding box, print the name of the object
            mean_gaze_point = np.mean(gaze_points, axis=0)
            for i, box in enumerate(boxes.xyxyn):
                if box[0] <= mean_gaze_point[0] <= box[2] and box[1] <= (1 - mean_gaze_point[1]) <= box[3]:
                    curr_object = result.names[int(classes[i])]

        # Display the current object
        text_container.text(f"Current Object: {curr_object}")

        # Save the result image
        object_detector.save_result(results)

        # Display the result image
        result_img_path = object_detector.image_path
        result_img = Image.open(result_img_path)

        result_img_array = cv2.cvtColor(np.array(result_img), cv2.COLOR_RGB2BGR)
        for i, gaze_p in enumerate(gaze_points[-5:]):
            if 0 <= gaze[0] <= 1 and 0 <= gaze[1] <= 1:
                # Convert normalized gaze coordinates to pixel coordinates
                # Flip the y-axis as the origin (0, 0) is in the top-left
                # corner in OpenCV
                gaze_x, gaze_y = int(gaze_p[0] * result_img_array.shape[1]), int((1 - gaze_p[1]) * result_img_array.shape[0])

                # Draw a circle at the gaze point
                cv2.circle(result_img_array, (gaze_x, gaze_y), 10, gaze_colors[-1*i], -1)

        result_img = Image.fromarray(cv2.cvtColor(result_img_array, cv2.COLOR_BGR2RGB))

        image_container.image(result_img)

