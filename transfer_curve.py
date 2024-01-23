import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from template_class import MeasurementDevice

matplotlib.use("QtAgg")

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig, self.axes = plt.subplots(figsize=(width, height), dpi=dpi)
        super().__init__(fig)
        self.setParent(parent)

    def plot_line(self, slope, intercept):
        self.axes.clear()
        x = np.linspace(-10, 10, 100)
        y = slope * x + intercept
        self.axes.plot(x, y)
        self.axes.set_xlabel('X-axis')
        self.axes.set_ylabel('Y-axis')
        self.draw()

class LinePlotterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        # Widgets for left side
        slope_label = QLabel('Slope:')
        self.slope_input = QLineEdit()

        intercept_label = QLabel('Intercept:')
        self.intercept_input = QLineEdit()

        go_button = QPushButton('Go')
        go_button.clicked.connect(self.plot_line)

        # Layout for left side
        left_layout = QGridLayout()
        left_layout.addWidget(slope_label, 0, 0)
        left_layout.addWidget(self.slope_input, 0, 1, 1, 2)
        left_layout.addWidget(intercept_label, 1, 0)
        left_layout.addWidget(self.intercept_input, 1, 1, 1, 2)
        left_layout.addWidget(go_button)

        # Widgets for right side
        self.plot_canvas = PlotCanvas(self)

        # Layout for right side
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.plot_canvas)

        # Main layout
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('Line Plotter')

    def plot_line(self):
        try:
            slope = float(self.slope_input.text())
            intercept = float(self.intercept_input.text())
        except ValueError:
            print("Invalid input. Please enter numeric values for slope and intercept.")
            return

        self.plot_canvas.plot_line(slope, intercept)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LinePlotterApp()
    window.show()
    sys.exit(app.exec())