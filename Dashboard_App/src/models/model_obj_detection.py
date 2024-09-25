import numpy as np
from ultralytics import YOLO


class YoloObjectDetector:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
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