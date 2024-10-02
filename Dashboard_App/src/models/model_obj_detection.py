import numpy as np
from ultralytics import YOLO
import streamlit.config
import toml


app_config = toml.load("config.toml")


class YoloObjectDetector:
    MODEL_PATH = app_config["paths"]["model_path"]
    def __init__(self):
        self.model = YOLO(self.MODEL_PATH)
        self.image_path = ".local/result.jpg"

    def predict(self, image):
        return self.model(image)

    def plot_result(self, results):
        output_images = []
        # Process results list
        for result in results:
            # Create a plot of the results
            result_image = result.plot(
                pil=True,
            )
            # Convert the PIL image to a NumPy array
            output_images.append(np.array(result_image))
        return output_images