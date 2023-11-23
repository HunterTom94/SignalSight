# controls.py

from PyQt5 import QtWidgets
from serial.tools import list_ports
from constants import COLORMAP_CHOICES, LINE_COLOR_CHOICES

class Controls(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()

        # self.line_color_label = QtWidgets.QLabel("Line color:")
        # layout.addWidget(self.line_color_label)
        # self.line_color_chooser = QtWidgets.QComboBox()
        # self.line_color_chooser.addItems(LINE_COLOR_CHOICES)
        # layout.addWidget(self.line_color_chooser)

        self.com_port_label = QtWidgets.QLabel("Select COM Port:")
        layout.addWidget(self.com_port_label)
        self.com_port_chooser = QtWidgets.QComboBox()
        self.update_com_ports()  # Method to populate COM port options
        layout.addWidget(self.com_port_chooser)

        # Grid toggle checkbox
        self.grid_toggle = QtWidgets.QCheckBox("Show Grid")
        self.grid_toggle.setChecked(True)  # Default to showing the grid
        layout.addWidget(self.grid_toggle)

        self.start_button = QtWidgets.QPushButton("Start Recording")
        layout.addWidget(self.start_button)

        layout.addStretch(1)
        self.setLayout(layout)

    def update_com_ports(self):
        # Method to populate the dropdown with available COM ports
        self.com_port_chooser.clear()
        com_ports = list_ports.comports()
        for port in com_ports:
            self.com_port_chooser.addItem(port.device)
