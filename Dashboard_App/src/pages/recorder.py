import os
import pickle
import time

import matplotlib.pyplot as plt
import streamlit as st
import random
import toml
from PIL import Image

from ..controller.pupil_labs import PupilLabsController
from ..utils import Page, create_smiley_grid


class PageRecorder(Page):
    NAME = "Gaze Recorder"
    SAVE_PATH = "../.local/gaze_data/"

    def __init__(self):
        self.controller = PupilLabsController()

    def write(self):
        st.title(self.NAME)
        st.write("With the Gaze Recorder, you can record your gaze data and save it to a csv file.")

        st.subheader("Subject Information")
        col11, col12, col13 = st.columns(3)

        with col11:
            subject_name = st.text_input("Subject Name")

        with col12:
            subject_age = st.number_input("Subject Age", min_value=1, max_value=100)

        with col13:
            subject_sex = st.selectbox("Subject Gender", ["Male", "Femail", "Diverse"])

        st.subheader("Make Recording")
        col21, col22, col13 = st.columns(3)

        with col21:
            subject_task = st.selectbox("Performed Task", ["Interact", "Search", "Read"])


        with col22:
            recording_time = st.number_input("Recording Time (s)", min_value=1, max_value=100, value=5)

        start_btn = st.button("Start Recording")

        if subject_task == "Search":
            grid = create_smiley_grid(20)
            st.image(grid, caption="Search Task")

        elif subject_task == "Interact":
            # read the image
            task_img = Image.open("assets/Interact.png")
            st.image(task_img, caption="Interact Task")

        elif subject_task == "Read":
            # read the image
            task_img = Image.open("assets/read.png")
            st.image(task_img, caption="Read Task")

        if start_btn:
            image_task = st.empty()
            gaze_data = self._record_gaze_data(recording_time)
            image_task.empty()
            fig = self._create_gaze_figure(gaze_data)
            st.pyplot(fig)

        if st.button("Save Recording"):

            gaze_data_file = {
                "name": subject_name,
                "age": subject_age,
                "gender": subject_sex,
                "task": subject_task,
                "gaze_data": gaze_data
            }

            gaze_files = [f for f in os.listdir(self.SAVE_PATH) if subject_task in f]

            f_name = f"{len(gaze_files)}_{subject_task}.pkl"

            # Save the gaze data to a pickle file
            with open(os.path.join(self.SAVE_PATH, f_name), "wb") as f:
                pickle.dump(gaze_data_file, f)




    def _create_gaze_figure(self, gaze_data):
        gaze_points = [g['norm_pos'] for g in gaze_data]
        # Plot the gaze points and connect them with thine lightblue lines
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

