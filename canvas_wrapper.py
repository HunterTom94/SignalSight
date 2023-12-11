from vispy.scene import SceneCanvas, visuals, AxisWidget, GridLines, Widget
import numpy as np
from constants import CANVAS_SIZE, NUM_LINE_POINTS, LINE_COLOR_CHOICES

import time

class CanvasWrapper:
    def __init__(self):
        self.canvas = SceneCanvas(size=CANVAS_SIZE, keys='interactive')
        self.grid = self.canvas.central_widget.add_grid(spacing=0)

        # Add view for the line plot
        self.view = self.grid.add_view(row=0, col=1)
        self.view.bgcolor = '#c0c0c0'
        self.view.camera = 'panzoom'

        # Create the line plot
        line_data = self._generate_zero_line_positions(NUM_LINE_POINTS)
        self.line = visuals.Line(line_data, color=LINE_COLOR_CHOICES[0])
        self.view.add(self.line)

        self.lower_left_padding = Widget(bgcolor=self.view.bgcolor)
        self.grid.add_widget(self.lower_left_padding, row=1, col=0)

        self.xaxis = AxisWidget(orientation='bottom', axis_color='black', text_color='black', tick_color='black')
        self.xaxis.bgcolor = self.view.bgcolor
        self.xaxis.stretch = (1, 0.1)
        self.grid.add_widget(self.xaxis, row=1, col=1)

        self.yaxis = AxisWidget(orientation='left', axis_color='black', text_color='black', tick_color='black')
        self.yaxis.bgcolor = self.view.bgcolor
        self.yaxis.stretch = (0.1, 1)
        self.grid.add_widget(self.yaxis, row=0, col=0)

        # Link axis with the view
        self.xaxis.link_view(self.view)
        self.yaxis.link_view(self.view)

        # Update view and axes ranges
        self.view.camera.set_range(x=(0, NUM_LINE_POINTS), y=(0, 1))
        self.xaxis.axis.domain = (0, NUM_LINE_POINTS)
        self.yaxis.axis.domain = (0, 1)

        # Create grid lines
        self.grid_lines = GridLines(parent=self.view.scene)
        self.grid_lines.visible = True  # Set initial state of the grid

    def set_line_color(self, color):
        self.line.set_data(color=color)

    def update_data(self, new_data_dict):
        self.line.set_data(new_data_dict["line"])

    def toggle_grid(self, state):
        self.grid_lines.visible = state

    def update_x_axis_range(self, new_range):
        # Update x-axis domain and view camera range
        self.xaxis.axis.domain = (-new_range, 0)
        self.view.camera.set_range(x=(-new_range, 0))

    @staticmethod
    def _generate_zero_line_positions(num_points, dtype=np.float32):
        pos = np.empty((num_points, 2), dtype=dtype)
        pos[:, 0] = np.arange(num_points)
        pos[:, 1] = np.zeros(num_points, dtype=dtype)
        return pos
