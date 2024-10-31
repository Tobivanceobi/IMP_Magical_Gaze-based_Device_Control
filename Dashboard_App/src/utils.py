import numpy as np
import streamlit as st
from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
import random

class Page(ABC):
    @abstractmethod
    def write(self):
        pass


def add_custom_css():
    sidebar_button_style = """
            <style>
            /* Remove rounded corners from sidebar buttons */
            div[data-testid="stSidebarContent"] button[kind="secondary"] {
                border-radius: 0 !important;
            }
            </style>
        """
    # Apply CSS style for square corners
    st.sidebar.markdown(sidebar_button_style, unsafe_allow_html=True)

def create_smiley_grid(size, cell_size=100):
    # Create a new image with white background
    image_size = size * cell_size
    image = Image.new('RGB', (image_size, image_size), 'white')
    draw = ImageDraw.Draw(image)

    # Randomly select position for sad smiley
    sad_row = random.randint(0, size - 1)
    sad_col = random.randint(0, size - 1)

    for row in range(size):
        for col in range(size):
            x = col * cell_size
            y = row * cell_size

            # Draw face circle
            draw.ellipse([x + 10, y + 10, x + cell_size - 10, y + cell_size - 10], outline='black', width=2)

            # Draw eyes
            eye_radius = cell_size // 10
            left_eye_center = (x + cell_size // 3, y + cell_size // 3)
            right_eye_center = (x + 2 * cell_size // 3, y + cell_size // 3)

            draw.ellipse([left_eye_center[0] - eye_radius, left_eye_center[1] - eye_radius,
                          left_eye_center[0] + eye_radius, left_eye_center[1] + eye_radius], fill='black')
            draw.ellipse([right_eye_center[0] - eye_radius, right_eye_center[1] - eye_radius,
                          right_eye_center[0] + eye_radius, right_eye_center[1] + eye_radius], fill='black')

            # Draw mouth (happy or sad)
            if row == sad_row and col == sad_col:
                # Sad mouth (downturned arc)
                draw.arc([x + cell_size // 4, y + cell_size // 2, x + 3 * cell_size // 4, y + 3 * cell_size // 4],
                         180, 0, fill='black', width=2)
            else:
                # Happy mouth (upturned arc)
                draw.arc([x + cell_size // 4, y + cell_size // 2, x + 3 * cell_size // 4, y + 3 * cell_size // 4],
                         0, 180, fill='black', width=2)


    return image


# Function to compute fixations
def compute_fixations(df, dur_tr=1, spat_tr=0.1):
    fixations = []
    current_fixation = []

    for i in range(len(df)):
        if not current_fixation:
            current_fixation.append(df.iloc[i])
            continue

        last_fixation = current_fixation[-1]
        current_point = df.iloc[i]

        # Check if the current point is within spatial threshold and duration threshold
        time_diff = current_point['timestamp'] - last_fixation['timestamp']

        mean_x = np.mean([point['x'] for point in current_fixation])
        mean_y = np.mean([point['y'] for point in current_fixation])
        spatial_diff = np.linalg.norm(current_point[['x', 'y']] - np.array([mean_x, mean_y]))

        if time_diff <= dur_tr and spatial_diff <= spat_tr:
            current_fixation.append(current_point)
        else:
            if len(current_fixation) > 1:  # Only consider fixations with more than 1 point
                fixations.append(current_fixation)
            current_fixation = [current_point]  # Start a new fixation

    # Check if there is a remaining fixation to save
    if len(current_fixation) > 1:
        fixations.append(current_fixation)

    return fixations

