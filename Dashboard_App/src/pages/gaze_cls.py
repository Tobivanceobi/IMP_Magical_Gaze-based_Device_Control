import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from ..controller.pupil_labs import PupilLabsController
from ..utils import Page, compute_fixations


class PageGazeCls(Page):
    NAME = "Gaze Classification"
    def __init__(self):
        self.controller = PupilLabsController()

    def write(self):
        st.title(self.NAME)

        st.subheader("Make Recording")

        recording_time = st.number_input("Recording Time (s)", min_value=1, max_value=100, value=5)

        start_btn = st.button("Start Recording")

        if start_btn:
            gaze_data = self._record_gaze_data(recording_time)
            norm_pos = np.array([gd['norm_pos'] for gd in gaze_data])
            timestamps = [gd['timestamp'] for gd in gaze_data]
            print(timestamps[0], timestamps[-1])

            gaze_df = pd.DataFrame(norm_pos, columns=['x', 'y'])
            gaze_df['timestamp'] = timestamps
            # print the total time of the recording
            print(f"Recording time: {timestamps[-1] - timestamps[0]:.2f} seconds")
            self._plot_norm_pos(norm_pos, timestamps)

            fixations = compute_fixations(gaze_df, dur_tr=0.2, spat_tr=0.1)
            print(len(fixations))
            self._plot_fixations(fixations)

    def _plot_norm_pos(self, norm_pos, timestamps):
        fig = plt.figure(figsize=(8, 8))
        plt.scatter(norm_pos[:, 0], norm_pos[:, 1], c=timestamps, cmap='viridis', s=3)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Normalized Gaze Position")
        plt.xlim(0, 1)
        plt.ylim(0, 1)
        # show the plot on streamlit
        st.pyplot(fig)

    def _plot_fixations(self, fixations):
        fig = plt.figure(figsize=(8, 8))

        # Plot fixations
        for idx, fixation in enumerate(fixations):
            fixation_x = [point['x'] for point in fixation]
            fixation_y = [point['y'] for point in fixation]
            plt.scatter(fixation_x, fixation_y, s=3, label=f'Fixation {idx + 1}')

        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xlabel('Normalized X')
        plt.ylabel('Normalized Y')
        plt.legend()
        st.pyplot(fig)

    def _record_gaze_data(self, recording_time):
        self.controller.reconnect_sockets()
        gaze_data = self.controller.receive_gaze_data_duration(recording_time)
        return gaze_data