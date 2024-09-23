import logging

import streamlit as st
from firebase_admin import firestore

from src.auth import FirebaseAuth
from src.pupil_capture import PupilCapture
from src.model import ObjectDetector
from time import sleep
import numpy as np
from PIL import Image
import cv2

# Initialize Firebase Auth (Provide the path to your Firebase Admin SDK JSON file)
auth = FirebaseAuth(".local/firebase-adminsdk.json")

# Set up logging
logging.basicConfig(level=logging.ERROR)

# Function to control page navigation
def set_page(page_name):
    st.session_state['page'] = page_name

def save_gaze_data(user_id, gaze_points, detected_object):
    # Convert gaze points into a list of dictionaries
    formatted_gaze_points = [{'x': float(gaze[0]), 'y': float(gaze[1])} for gaze in gaze_points]

    doc_ref = auth.db.collection('gaze_data').document(user_id).collection('gaze_sessions').add({
        'timestamp': firestore.SERVER_TIMESTAMP,
        'gaze_points': formatted_gaze_points,  # List of gaze points as dictionaries
        'detected_object': detected_object,  # Object name detected by YOLO
    })
    st.success("Gaze data saved successfully!")

# Navigation logic
def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'Login'

    if st.session_state['page'] == 'Login':
        login_page()
    elif st.session_state['page'] == 'Register':
        register_page()
    elif st.session_state['page'] == 'Gaze Tracker':
        if 'id_token' in st.session_state:
            gaze_tracker_page()
        else:
            st.error("You need to log in to access this page.")

# Login Page
def login_page():
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        success = auth.login(email, password)
        if success:
            st.session_state['page'] = 'Gaze Tracker'  # Redirect to Gaze Tracker

    # Redirect to registration page
    if st.button("Not signed up yet? Register here"):
        st.session_state['page'] = 'Register'

# Registration Page
def register_page():
    st.title("Register")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        success = auth.register(email, password)
        if success:
            st.session_state['page'] = 'Login'  # Redirect to Login page after registration

    # Redirect to login page
    if st.button("Already have an account? Login here"):
        st.session_state['page'] = 'Login'

# Gaze Tracker Page with Error Handling
def gaze_tracker_page():
    try:
        pupil_remote = PupilCapture()
        object_detector = ObjectDetector(model_path=".local/yolov8n.pt")

        # Streamlit button controls
        start_button = st.button("Start Pupil Capture")
        stop_button = st.button("Stop Pupil Capture")

        # Streamlit containers for displaying text and images
        text_container = st.empty()
        image_container = st.empty()

        if start_button:
            gaze_colors = [(55, 155, 255), (79, 55, 255), (170, 55, 255), (255, 55, 255), (0, 0, 255)]
            while not stop_button:
                sleep(0.01)

                # Receive frame from Pupil Labs and gaze information
                frame = pupil_remote.receive_frame_world_image()
                gaze_points = []
                for _ in range(3):
                    gaze = pupil_remote.receive_gaze_information()
                    gaze_points.append(gaze)

                # Filter gaze points
                gaze_points = np.array(gaze_points)
                mean_gaze = np.mean(gaze_points, axis=0)
                std_gaze = np.std(gaze_points, axis=0)
                gaze_points = gaze_points[np.all(np.abs(gaze_points - mean_gaze) < 2 * std_gaze, axis=1)]

                # Detect objects in the frame using YOLO
                curr_object = "Nothing"
                results = object_detector.predict(frame)
                for result in results:
                    boxes = result.boxes
                    classes = boxes.cls
                    mean_gaze_point = np.mean(gaze_points, axis=0)
                    for i, box in enumerate(boxes.xyxyn):
                        if box[0] <= mean_gaze_point[0] <= box[2] and box[1] <= (1 - mean_gaze_point[1]) <= box[3]:
                            curr_object = result.names[int(classes[i])]

                # Display the current object
                text_container.text(f"Current Object: {curr_object}")

                # Save the gaze data into Firestore for the logged-in user
                user_id = st.session_state['user']  # User's Firebase ID
                save_gaze_data(user_id, gaze_points.tolist(), curr_object)

                # Save the result image and display it
                object_detector.save_result(results)
                result_img_path = object_detector.image_path
                result_img = Image.open(result_img_path)
                result_img_array = cv2.cvtColor(np.array(result_img), cv2.COLOR_RGB2BGR)

                # Draw gaze points on the image
                for i, gaze_p in enumerate(gaze_points[-5:]):
                    if 0 <= gaze_p[0] <= 1 and 0 <= gaze_p[1] <= 1:
                        gaze_x, gaze_y = int(gaze_p[0] * result_img_array.shape[1]), int((1 - gaze_p[1]) * result_img_array.shape[0])
                        cv2.circle(result_img_array, (gaze_x, gaze_y), 10, gaze_colors[-1*i], -1)

                result_img = Image.fromarray(cv2.cvtColor(result_img_array, cv2.COLOR_BGR2RGB))
                image_container.image(result_img)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        st.error(f"An error occurred: {str(e)}")


# Run the app
if __name__ == "__main__":
    main()