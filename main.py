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
        self.data_source = data_source

        central_widget = QtWidgets.QWidget()
        main_layout = QtWidgets.QHBoxLayout()

        self._controls = Controls()
        main_layout.addWidget(self._controls)
        self._canvas_wrapper = canvas_wrapper
        main_layout.addWidget(self._canvas_wrapper.canvas.native)

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self._connect_controls()

    def _connect_controls(self):
        # self._controls.line_color_chooser.currentTextChanged.connect(self._canvas_wrapper.set_line_color)
        self._controls.com_port_chooser.currentTextChanged.connect(self.update_data_source_com_port)

    def closeEvent(self, event):
        print("Closing main window!")
        self.closing.emit()
        return super().closeEvent(event)

    def update_data_source_com_port(self, com_port):
        if self.data_source:
            self.data_source.update_com_port(com_port)




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
    data_thread.start()
    app.run()

    print("Waiting for data source to close gracefully...")
    data_thread.quit()
    data_thread.wait(5000)