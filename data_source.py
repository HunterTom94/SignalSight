import struct
import time

import numpy as np
import serial
from PyQt5 import QtCore
from constants import NUM_LINE_POINTS
class DataSource(QtCore.QObject):
    new_data = QtCore.pyqtSignal(dict)
    finished = QtCore.pyqtSignal()
    data_rate_calculated = QtCore.pyqtSignal(float)  # Signal to emit the calculated data rate
    new_yrange = QtCore.pyqtSignal(list)

    def __init__(self, port="COM6", baudrate=921600, delim='\n', parent=None):
        super().__init__(parent)

        self.delim = delim
        self.current_display_range = int(10e3)
        self.data_rate = -1
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            self.serial_port = None
            self._should_end = True
        else:
            self._should_end = False
        self.data_buffer = np.zeros((NUM_LINE_POINTS, 2))
        self.buffer_index = 0
        self.yrange = [0, 1]

        self.recording = False
        self.last_update_time = None

        self.recording_buffer = []

        self.starting_time = time.time()
        self.last_time_data_rate_emit = time.time()

    def start_recording(self):
        self.recording = True

    def run_data_creation(self):
        if self._should_end or (self.serial_port and not self.serial_port.isOpen()):
            self._close_serial_port()
            self.finished.emit()
            return

        try:
            if self.serial_port and self.serial_port.inWaiting() >= 4:
                # Read 4 bytes (size of a float in C/C++)
                # binary_data = self.serial_port.read(4)

                # Unpack the binary data into a float
                # value = struct.unpack('f', binary_data)[0]

                # # Read 2 bytes (size of a 16-bit integer in C/C++)
                # binary_data = self.serial_port.read(2)
                #
                # # Unpack the binary data into a 16-bit integer
                # value = struct.unpack('h', binary_data)[0]  # 'h' format is for short (2 bytes)

                line = self.serial_port.readline().decode('utf-8').strip()
                value = float(line.split(self.delim)[0])  # Parse the value

                self._update_buffer(value)

                if self.recording:
                    self.recording_buffer.append(value)

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
        assert n <= self.data_buffer.shape[0]

        if self.buffer_index < n:
            # Get the part of the buffer that has valid data
            valid_data = self.data_buffer[:self.buffer_index]
            # print(f'valid data: {valid_data}')

            # Calculate average data rate for valid data
            valid_timestamps = valid_data[:, 0]
            valid_timestamps = valid_timestamps[valid_timestamps > 0]  # Filter out zeros
            if len(valid_timestamps) > 1:
                avg_data_rate = np.mean(np.diff(valid_timestamps))
            else:
                avg_data_rate = 1 / self.data_rate  # Fallback to the current data rate

            # Infer timestamps for initial data points
            num_inferred_timestamps = n - len(valid_timestamps)
            inferred_timestamps = valid_timestamps[0] - np.arange(1, num_inferred_timestamps + 1)[::-1] * avg_data_rate
            combined_timestamps = np.concatenate([inferred_timestamps, valid_timestamps])

            # Handle values for inferred timestamps
            values_for_inferred_timestamps = self.data_buffer[-num_inferred_timestamps:, 1]
            combined_values = np.concatenate([values_for_inferred_timestamps, valid_data[:, 1]])
        else:
            combined_timestamps = self.data_buffer[self.buffer_index - n:self.buffer_index, 0]
            combined_values = self.data_buffer[self.buffer_index - n:self.buffer_index, 1]

        # Calculate x values based on timestamps
        x = (combined_timestamps - combined_timestamps[-1])
        y = combined_values

        # print(f'data rate: {self.data_rate}')
        # print(f'x: {x}')
        # print(f'y: {y}')

        return np.column_stack((x, y))

    def update_com_port(self, com_port):
        if self.serial_port and self.serial_port.isOpen():
            self.serial_port.close()
        self.serial_port = serial.Serial(com_port, self.baudrate, timeout=1)

    def _update_buffer(self, new_value):
        def _is_significant_change(old_rate, new_rate):
            # Define a dynamic threshold as a percentage of the old rate
            threshold = abs(old_rate * 0.1)  # 1% of the old rate as threshold
            return abs(new_rate - old_rate) > threshold

        current_timestamp = time.time() - self.starting_time

        self.data_buffer[self.buffer_index] = [current_timestamp, new_value]
        self.buffer_index = (self.buffer_index + 1) % self.data_buffer.size

        if new_value < self.yrange[0]:
            self.yrange[0] = new_value
            self.new_yrange.emit(self.yrange)
        elif new_value > self.yrange[1]:
            self.yrange[1] = new_value
            self.new_yrange.emit(self.yrange)

        # Calculate time difference
        current_time = time.time()
        if self.last_update_time and current_time - self.last_time_data_rate_emit > 1:
            calculated_data_rate = 1 / np.mean(np.diff(self.data_buffer[:self.buffer_index, 0]))
            # Round data rate to 3 significant figures
            # Update only if there is a significant change
            if _is_significant_change(self.data_rate, calculated_data_rate):
                self.data_rate = calculated_data_rate
                self.data_rate_calculated.emit(self.data_rate)
                self.last_time_data_rate_emit = current_time

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
