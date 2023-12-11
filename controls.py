# controls.py

from PyQt5 import QtWidgets, QtGui, QtCore
from serial.tools import list_ports
from constants import COLORMAP_CHOICES, LINE_COLOR_CHOICES

class Controls(QtWidgets.QWidget):
    data_rate_changed = QtCore.pyqtSignal(float)
    display_duration_changed = QtCore.pyqtSignal(int)
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

        # Data Rate Input Box
        self.data_rate_input = QtWidgets.QLineEdit()
        self.data_rate_input.setValidator(QtGui.QDoubleValidator(0.0, 10000.0, 2))
        self.data_rate_input.setEnabled(False)
        self.data_rate_input.textChanged.connect(self.on_data_rate_input_changed)

        # Auto Detect Data Rate Checkbox
        self.auto_detect_checkbox = QtWidgets.QCheckBox("Auto Detect Data Rate")
        self.auto_detect_checkbox.stateChanged.connect(self.toggle_data_rate_input)
        self.auto_detect_checkbox.setChecked(True)  # Checked by default

        layout.addWidget(self.auto_detect_checkbox)
        layout.addWidget(QtWidgets.QLabel("Data Rate:"))

        # Hz label
        data_rate_layout = QtWidgets.QHBoxLayout()
        data_rate_layout.addWidget(self.data_rate_input)
        data_rate_layout.addWidget(QtWidgets.QLabel("Hz"))
        layout.addLayout(data_rate_layout)

        # Add QComboBox for display range
        self.display_range_selector = QtWidgets.QComboBox()
        self.display_range_selector.addItems(
            ["1", "2", "5", "10", "20", "50", "100"])
        self.display_range_selector.currentTextChanged.connect(self.on_display_range_selection_changed)
        layout.addWidget(QtWidgets.QLabel("Display Range (s):"))
        layout.addWidget(self.display_range_selector)

        layout.addStretch(1)
        self.setLayout(layout)

    def on_data_rate_input_changed(self):
        try:
            data_rate = float(self.data_rate_input.text())
            self.data_rate_changed.emit(data_rate)
        except ValueError:
            pass

    def on_display_range_selection_changed(self):
        duration = int(self.display_range_selector.currentText())
        self.display_duration_changed.emit(duration)

    def toggle_data_rate_input(self):
        # Enable/Disable data rate input based on checkbox
        self.data_rate_input.setEnabled(not self.auto_detect_checkbox.isChecked())

    def update_com_ports(self):
        # Method to populate the dropdown with available COM ports
        self.com_port_chooser.clear()
        com_ports = list_ports.comports()
        for port in com_ports:
            self.com_port_chooser.addItem(port.device)
