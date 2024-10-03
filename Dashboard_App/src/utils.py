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