# canvas_wrapper.py

from vispy.scene import SceneCanvas, visuals
from constants import CANVAS_SIZE, NUM_LINE_POINTS, LINE_COLOR_CHOICES
import numpy as np

class CanvasWrapper:
    def __init__(self):
        self.canvas = SceneCanvas(size=CANVAS_SIZE)
        self.grid = self.canvas.central_widget.add_grid()

        self.view = self.grid.add_view(0, 0, bgcolor='#c0c0c0')
        line_data = self._generate_zero_line_positions(NUM_LINE_POINTS)
        self.line = visuals.Line(line_data, parent=self.view.scene, color=LINE_COLOR_CHOICES[0])
        self.view.camera = "panzoom"
        self.view.camera.set_range(x=(0, NUM_LINE_POINTS), y=(0, 1))

    def set_line_color(self, color):
        print(f"Changing line color to {color}")
        self.line.set_data(color=color)

    def update_data(self, new_data_dict):
        print("Updating data...")
        self.line.set_data(new_data_dict["line"])

    @staticmethod
    def _generate_zero_line_positions(num_points, dtype=np.float32):
        pos = np.empty((num_points, 2), dtype=dtype)
        pos[:, 0] = np.arange(num_points)
        pos[:, 1] = np.zeros(num_points, dtype=dtype)
        return pos
