import sys
from PyQt5 import QtWidgets, QtCore
from canvas_wrapper import CanvasWrapper
from controls import Controls
from data_source import DataSource
from vispy.app import use_app


class MyMainWindow(QtWidgets.QMainWindow):
    closing = QtCore.pyqtSignal()

    def __init__(self, canvas_wrapper: CanvasWrapper, data_source: DataSource, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._controls = Controls()
        self.data_source = data_source
        self.data_source.data_rate_calculated.connect(self.update_data_rate_input)


        self._controls.start_button.clicked.connect(self.start_recording)

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        self._canvas_wrapper = canvas_wrapper

        self._controls.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self._canvas_wrapper.canvas.native.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                         QtWidgets.QSizePolicy.Expanding)

        self.data_source.new_yrange.connect(self._canvas_wrapper.update_y_axis_range)

        main_layout.addWidget(self._controls)
        main_layout.addWidget(self._canvas_wrapper.canvas.native)
        self._controls.grid_toggle.stateChanged.connect(self.toggle_grid)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self._connect_controls()

        self._controls.display_duration_changed.connect(self.on_display_duration_changed)

        self._controls.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self._canvas_wrapper.canvas.native.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                                         QtWidgets.QSizePolicy.Expanding)
        self.resizeEvent = self.onResize

    def onResize(self, event):
        # Calculate new font size based on window size
        new_font_size = int(self.width() * 0.01)
        self._controls.update_font_size(new_font_size)

        super().resizeEvent(event)

    def toggle_grid(self, state):
        # state is an integer (0 for unchecked, 2 for checked)
        self._canvas_wrapper.toggle_grid(state == 2)

    def _connect_controls(self):
        self._controls.com_port_chooser.currentTextChanged.connect(self.update_data_source_com_port)

    def start_recording(self):
        self.data_source.start_recording()

    def closeEvent(self, event):
        print("Closing main window!")
        self.closing.emit()
        return super().closeEvent(event)

    def update_data_source_com_port(self, com_port):
        if self.data_source:
            self.data_source.update_com_port(com_port)

    def camera_on_view_changed(self):
        self._canvas_wrapper.view.camera.view_changed()

    def update_data_rate_input(self, data_rate):
        self.update_display_range(data_rate)
        self._controls.update_data_rate_display(data_rate)


    def on_display_duration_changed(self, duration):
        print(f"Display duration changed to {duration} seconds")
        self.update_display_range(self.data_source.data_rate)

    def update_display_range(self, data_rate):
        # Use the latest data rate and display duration to calculate the new range
        duration = self._controls.display_range_input.text()
        new_range = data_rate * float(duration)
        # self.data_source.current_display_range = int(new_range)
        self._canvas_wrapper.update_x_axis_range(new_range/self.data_source.data_rate)


if __name__ == "__main__":
    app = use_app("pyqt5")
    app.create()

    canvas_wrapper = CanvasWrapper()
    data_source = DataSource()
    win = MyMainWindow(canvas_wrapper, data_source)
    data_thread = QtCore.QThread(parent=win)
    data_source.moveToThread(data_thread)

    # update the visualization when there is new data
    data_source.new_data.connect(canvas_wrapper.update_data)
    # start data generation when the thread is started
    data_thread.started.connect(data_source.run_data_creation)
    # if the data source finishes before the window is closed, kill the thread
    # to clean up resources
    data_source.finished.connect(data_thread.quit)
    # if the window is closed, tell the data source to stop
    win.closing.connect(data_source.stop_data)
    # when the thread has ended, delete the data source from memory
    data_thread.finished.connect(data_source.deleteLater)

    win.show()
    win.camera_on_view_changed()  # Manually update the axis display range
    data_thread.start()
    app.run()

    print("Waiting for data source to close gracefully...")
    data_thread.quit()
    data_thread.wait(5000)
