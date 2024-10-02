import cv2
import numpy as np
import streamlit as st
from PIL import Image
from ..controller.pupil_labs import PupilLabsController
from ..models.model_obj_detection import YoloObjectDetector
from ..utils import Page


class PageObjectDetection(Page):
    NAME = "Object Detection"

    def __init__(self):
        self.controller = PupilLabsController()
        self.obj_detector = YoloObjectDetector()

        # Set the session state for detecting
        if 'detecting' not in st.session_state:
            st.session_state['detecting'] = False

    def write(self):
        """Render the Object Detection page."""
        st.title(self.NAME)

        # Check if the Pupil Labs service is online
        if not self.controller.is_service_online():
            st.subheader("Connection to EyeTracker cannot be established.")
            st.text("Please start the Pupil Core and Pupil Service before running the object detection.")
            return

        st.subheader("Pupil Core Object Detection")

        col11, col12 = st.columns(2)

        with col11:
            enable_gaze_point = st.checkbox("Enable Gaze Point", value=True)

        with col12:
            num_points = st.number_input(
                "Number of Gaze Points",
                min_value=3, max_value=10,
                value=5) if enable_gaze_point else 0

        col21, col22 = st.columns(2)

        with col21:
            start_detection = st.button("Start Object Detection")

        with col22:
            stop_detection = st.button("Stop Object Detection")

        # Placeholders for dynamic content
        text_container = st.empty()
        image_container = st.empty()

        if start_detection and not st.session_state.detecting:
            st.session_state.detecting = True
            self._run_detection(text_container, image_container, num_points, enable_gaze_point)

        if stop_detection:
            st.session_state.detecting = False
            text_container.text("Detection stopped.")

    def _run_detection(self, text_container, image_container, num_points, enable_gaze_point):
        """Run the detection process, updating UI in real time."""
        while st.session_state.get('detecting', False):
            # Ensure sockets stay connected
            self.controller.reconnect_sockets()

            # Get gaze data and frames
            gaze_data = self._process_gaze_data(num_points) if enable_gaze_point else []
            frame = self.controller.receive_cam_frames(num_frames=1)

            # Detect objects in the frame
            results = self.obj_detector.predict(frame)
            current_object = self._get_object_in_gaze(results, gaze_data)

            # Display the current object name
            text_container.text(f"Current Object: {current_object}")

            # Plot detection results
            image = self._plot_detection_results(results, gaze_data)
            image_container.image(image)

            # Break the loop gracefully if detection is stopped
            if not st.session_state.get('detecting', False):
                break

    def _process_gaze_data(self, num_points):
        """Receive and filter gaze data."""
        gaze_data = self.controller.receive_gaze_data(num_gazes=num_points)
        gaze_points = np.array([gd['norm_pos'] for gd in gaze_data])

        # Filter out noisy gaze points based on standard deviation
        mean_gaze = np.mean(gaze_points, axis=0)
        std_gaze = np.std(gaze_points, axis=0)
        filtered_gaze_points = gaze_points[np.all(np.abs(gaze_points - mean_gaze) < 2 * std_gaze, axis=1)]

        return np.mean(filtered_gaze_points, axis=0) if len(filtered_gaze_points) > 0 else mean_gaze

    def _get_object_in_gaze(self, results, mean_gaze):
        """Check if any object is within the gaze region."""
        for result in results:
            boxes = result.boxes
            classes = boxes.cls
            for i, box in enumerate(boxes.xyxyn):
                # Check if the gaze point lies within the bounding box of detected objects
                if box[0] <= mean_gaze[0] <= box[2] and box[1] <= (1 - mean_gaze[1]) <= box[3]:
                    return result.names[int(classes[i])]
        return "Nothing"

    def _plot_detection_results(self, results, mean_gaze=None):
        """Render the object detection results and draw gaze point if enabled."""
        image = self.obj_detector.plot_result(results)[0]
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        if mean_gaze is not None and 0 <= mean_gaze[0] <= 1 and 0 <= mean_gaze[1] <= 1:
            # Calculate the gaze point coordinates and draw it on the image
            gaze_x, gaze_y = int(mean_gaze[0] * image.shape[1]), int((1 - mean_gaze[1]) * image.shape[0])
            cv2.circle(image, (gaze_x, gaze_y), 10, (250, 0, 0), -1)

        return image
