import numpy as np
import serial
from PyQt5 import QtCore
from constants import NUM_LINE_POINTS
class DataSource(QtCore.QObject):
    new_data = QtCore.pyqtSignal(dict)
    finished = QtCore.pyqtSignal()

    def __init__(self, port="COM3", baudrate=9600, delim='\n', parent=None):
        super().__init__(parent)
        self.delim = delim
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
            self._should_end = True
        else:
            self._should_end = False
        self.data_buffer = np.zeros(NUM_LINE_POINTS)  # Initialize a buffer
        self.full_data_buffer = []  # Initialize the comprehensive data buffer
        self.recording = False

    def start_recording(self):
        self.recording = True

    def run_data_creation(self):
        if self._should_end or (self.serial_port and not self.serial_port.isOpen()):
            self._close_serial_port()
            self.finished.emit()
            return

        try:
            if self.serial_port and self.serial_port.inWaiting() > 0:
                line = self.serial_port.readline().decode('utf-8').strip()
                value = float(line.split(self.delim)[0])  # Parse the value
                self._update_buffer(value)  # Update the buffer with new value
                if self.recording:
                    self.full_data_buffer.append(value)  # Store the value in the full buffer

                # Prepare data for visualization
                data_dict = {
                    "line": self._prepare_line_data(),
                    # Add other data as needed
                }
                self.new_data.emit(data_dict)
        except Exception as e:
            print(f"Error reading from serial port: {e}")

        QtCore.QTimer.singleShot(0, self.run_data_creation)

    def update_com_port(self, com_port):
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
        self.serial_port = serial.Serial(com_port, self.baudrate, timeout=1)

    def _update_buffer(self, new_value):
        # Roll the buffer and append the new value
        self.data_buffer = np.roll(self.data_buffer, -1)
        self.data_buffer[-1] = new_value

    def _prepare_line_data(self):
        # Prepare line data for visualization
        x = np.arange(NUM_LINE_POINTS)
        y = self.data_buffer
        return np.column_stack((x, y))

    def stop_data(self):
        self._should_end = True
        self._close_serial_port()

    def _close_serial_port(self):
        if self.serial_port and self.serial_port.isOpen():
            print("Closing serial port...")
            self.serial_port.close()
