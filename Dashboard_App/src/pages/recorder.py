import matplotlib.pyplot as plt
import streamlit as st
from ..controller.firebase import FirebaseController
from ..controller.pupil_labs import PupilLabsController
from ..utils import Page


class PageRecorder(Page):
    NAME = "Gaze Recorder"
    SAVE_PATH = "../.local/gaze_data/"
    FIREBASE_CRED_PATH = "../.local/firebase-adminsdk.json"

    def __init__(self):
        self.controller = PupilLabsController()
        self.firebase_controller = FirebaseController(self.FIREBASE_CRED_PATH)
        if 'gaze_data' not in st.session_state:
            st.session_state['gaze_data'] = []

    def write(self):
        st.title(self.NAME)
        st.write("With the Gaze Recorder, you can record your gaze data and save it to Firebase")

        st.subheader("Subject Information")
        col11, col12, col13 = st.columns(3)

        with col11:
            subject_name = st.text_input("Subject Name")

        with col12:
            subject_age = st.number_input("Subject Age", min_value=1, max_value=100)

        with col13:
            subject_sex = st.selectbox("Subject Gender", ["Male", "Female", "Diverse"])

        st.subheader("Make Recording")
        col21, col22 = st.columns([1, 1])

        with col21:
            subject_task = st.selectbox("Performed Task", ["No Interaction", "Interact",], index=1)

        with col22:
            recording_time = st.number_input("Recording Time (s)", min_value=1, max_value=100, value=5)

        # Place the start and save buttons next to each other
        start_btn, save_btn = st.columns([1, 1])

        with start_btn:
            if st.button("Start Recording"):
                st.session_state['gaze_data'] = self._record_gaze_data(recording_time)
                fig = self._create_gaze_figure(st.session_state['gaze_data'])
                st.pyplot(fig)
                print(st.session_state['gaze_data'][10])

        with save_btn:
            if st.button("Save Recording"):
                session_info = {
                    "name": subject_name,
                    "age": subject_age,
                    "gender": subject_sex,
                    "task": subject_task
                }

                # Create session and save gaze data
                session_id = self.firebase_controller.create_session(session_info)
                gaze_counter = 0
                print("Saving gaze data...")
                for gaze_point in st.session_state['gaze_data']:
                    self.firebase_controller.save_gaze_point(session_id, gaze_point)
                    gaze_counter += 1

                print(f"Saved {gaze_counter} gaze points in session {session_id}.")
                st.success(f"Successfully saved {gaze_counter} gaze points in session {session_id}!")

    def _create_gaze_figure(self, gaze_data):
        gaze_points = [g['norm_pos'] for g in gaze_data]
        # Plot the gaze points and connect them with lines
        fig, ax = plt.subplots()
        for i in range(1, len(gaze_points)):
            x = [gaze_points[i - 1][0], gaze_points[i][0]]
            y = [gaze_points[i - 1][1], gaze_points[i][1]]
            ax.plot(x, y, color='blue', linewidth=1)
        ax.scatter(*zip(*gaze_points), color='lightblue', s=2)
        ax.set_xlim(min(g[0] for g in gaze_points) - 0.1, max(g[0] for g in gaze_points) + 0.1)
        ax.set_ylim(min(g[1] for g in gaze_points) - 0.1, max(g[1] for g in gaze_points) + 0.1)
        ax.set_aspect('equal')
        return fig

    def _record_gaze_data(self, recording_time):
        self.controller.reconnect_sockets()
        num_samples = recording_time * 120
        gaze_data = self.controller.receive_gaze_data(num_samples)
        return gaze_data