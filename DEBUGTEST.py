import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtCore import Qt

class ShapeWindow(QMainWindow):
    def __init__(self, func, scale=200, resolution=500):
        """
        func : callable
            A function f(x, y) that returns 0 on the shape
        scale : float
            How many pixels per unit
        resolution : int
            Number of points along each axis
        """
        super().__init__()
        self.setWindowTitle("Math Shape Plotter")
        self.setGeometry(100, 100, 1280, 720)
        self.func = func
        self.scale = scale
        self.resolution = resolution

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.black, 1)
        painter.setPen(pen)

        width, height = self.width(), self.height()
        cx, cy = width // 2, height // 2

        # Create a grid in "math coordinates"
        x_vals = np.linspace(-1.5, 1.5, self.resolution)
        y_vals = np.linspace(-1.5, 1.5, self.resolution)

        # Draw points where |f(x, y)| is small
        threshold = 0.01
        for x in x_vals:
            for y in y_vals:
                if abs(self.func(x, y)) < threshold:
                    px = cx + x * self.scale
                    py = cy - y * self.scale  # invert y for screen
                    painter.drawPoint(int(px), int(py))

# Example usage: unit circle
def circle(x, y):
    return x**2 + y**2 - 1  # x^2 + y^2 = 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ShapeWindow(circle)
    window.show()
    sys.exit(app.exec())
