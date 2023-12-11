# controls.py

from PyQt5 import QtWidgets, QtGui, QtCore
from serial.tools import list_ports
from constants import COLORMAP_CHOICES, LINE_COLOR_CHOICES

class Controls(QtWidgets.QWidget):
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

        # Data Rate Display
        self.data_rate_display = QtWidgets.QLabel("Data Rate: -- Hz")
        layout.addWidget(self.data_rate_display)

        # Display Range Input
        layout.addWidget(QtWidgets.QLabel("Display Range (s):"))
        self.display_range_input = QtWidgets.QLineEdit("10")  # Default value set to 10
        self.display_range_input.setValidator(QtGui.QDoubleValidator(0.0, 10000.0, 2))
        self.display_range_input.textChanged.connect(self.on_display_range_input_changed)
        layout.addWidget(self.display_range_input)

        layout.addStretch(1)
        self.setLayout(layout)

    def on_display_range_input_changed(self):
        try:
            duration = float(self.display_range_input.text())
            self.display_duration_changed.emit(duration)
        except ValueError:
            pass  # Handle invalid input here if needed

    def update_com_ports(self):
        # Method to populate the dropdown with available COM ports
        self.com_port_chooser.clear()
        com_ports = list_ports.comports()
        for port in com_ports:
            self.com_port_chooser.addItem(port.device)

    def update_data_rate_display(self, data_rate):
        if data_rate < 1e3:  # Less than 1 kHz
            display_rate = data_rate
            unit = "Hz"
            text = f"Data Rate: {display_rate:.1f} {unit}"
        elif data_rate < 1e6:  # 1 kHz to 1 MHz
            display_rate = data_rate / 1e3  # Convert to kHz
            unit = "kHz"
            text = f"Data Rate: {display_rate:.1f} {unit}"
        else:  # 1 MHz or higher
            display_rate = data_rate / 1e6  # Convert to MHz
            unit = "MHz"
            text = f"Data Rate: {display_rate:.1f} {unit}"  # No decimal places

        self.data_rate_display.setText(text)
