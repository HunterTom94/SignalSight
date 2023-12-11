import time

import numpy as np
import serial
from PyQt5 import QtCore
from constants import NUM_LINE_POINTS
class DataSource(QtCore.QObject):
    new_data = QtCore.pyqtSignal(dict)
    finished = QtCore.pyqtSignal()
    data_rate_calculated = QtCore.pyqtSignal(float)  # Signal to emit the calculated data rate

    def __init__(self, port="COM3", baudrate=9600, delim='\n', parent=None):
        super().__init__(parent)
        self.delim = delim
        self.current_display_range = NUM_LINE_POINTS
        self.data_rate = 1
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
            self._should_end = True
        else:
            self._should_end = False
        self.data_buffer = np.zeros(NUM_LINE_POINTS)
        self.buffer_index = 0
        self.recording = False
        self.last_update_time = None

        self.recording_buffer = []


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
                    self.recording_buffer.append(value)  # Store the value in the full buffer

                # Prepare data for visualization
                data_dict = {
                    "line": self._prepare_line_data(),
                    # Add other data as needed
                }
                self.new_data.emit(data_dict)
        except Exception as e:
            print(f"Error reading from serial port: {e}")

        QtCore.QTimer.singleShot(0, self.run_data_creation)

    def _prepare_line_data(self):
        n = self.current_display_range + 1
        assert n < self.data_buffer.size
        if self.buffer_index < n:
            # If current index is less than n, circle back to the end of the buffer
            y = np.concatenate((self.data_buffer[self.buffer_index - n:], self.data_buffer[:self.buffer_index]))
        else:
            y = self.data_buffer[self.buffer_index - n:self.buffer_index]

        x = (np.arange(-n, 0) + 1) / self.data_rate
        return np.column_stack((x, y))

    def update_com_port(self, com_port):
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
        self.serial_port = serial.Serial(com_port, self.baudrate, timeout=1)

    def _update_buffer(self, new_value):
        # Update the buffer at the current index
        self.data_buffer[self.buffer_index] = new_value
        # Increment the index using modulo for circular behavior
        self.buffer_index = (self.buffer_index + 1) % self.data_buffer.size

        # Calculate time difference
        current_time = time.time()
        if self.last_update_time:
            time_diff = current_time - self.last_update_time
            # Update the data rate based on the average time difference
            if time_diff > 0:
                self.data_rate = 1 / time_diff
                self.data_rate_calculated.emit(self.data_rate)
        self.last_update_time = current_time

    def adjust_buffer_size(self, max_data_rate, display_duration):
        new_buffer_size = int(max_data_rate * display_duration)

    def stop_data(self):
        self._should_end = True
        self._close_serial_port()

    def _close_serial_port(self):
        if self.serial_port and self.serial_port.isOpen():
            print("Closing serial port...")
            self.serial_port.close()
