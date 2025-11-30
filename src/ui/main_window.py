"""
Main Window - With Shape Management
FIXED VERSION with quaternion sync and 3D toggle
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPushButton, QLabel, QSplitter, QScrollArea,
    QLineEdit, QCheckBox, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rendering.plotter import QtPlotWidget
from math_engine.environment import MathEnvironment
from math_engine.shape import ShapeManager, Shape


class ShapeWidget(QFrame):
    """Widget for a single shape with controls"""
    
    def __init__(self, shape: Shape, on_update, on_delete, parent=None):
        super().__init__(parent)
        self.shape = shape
        self.on_update = on_update
        self.on_delete = on_delete
        
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.name_label = QLabel(self.shape.name)
        self.name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header.addWidget(self.name_label)
        header.addStretch()
        
        self.visible_checkbox = QCheckBox("Visible")
        self.visible_checkbox.setChecked(self.shape.visible)
        self.visible_checkbox.stateChanged.connect(self.on_visibility_changed)
        header.addWidget(self.visible_checkbox)
        
        self.delete_btn = QPushButton("✕")
        self.delete_btn.setMaximumWidth(30)
        self.delete_btn.clicked.connect(lambda: self.on_delete(self.shape))
        self.delete_btn.setStyleSheet("background-color: #f44336; color: white;")
        header.addWidget(self.delete_btn)
        layout.addLayout(header)
        
        # Equation
        eq_label = QLabel(f"Equation: {self.shape.equation_str}")
        eq_label.setWordWrap(True)
        eq_label.setStyleSheet("color: #666; font-family: monospace;")
        layout.addWidget(eq_label)
        
        # Translation
        trans_layout = QHBoxLayout()
        trans_layout.addWidget(QLabel("Position:"))
        trans_layout.addWidget(QLabel("X:"))
        self.tx_input = QLineEdit(str(self.shape.translation[0]))
        self.tx_input.setMaximumWidth(60)
        self.tx_input.textChanged.connect(self.on_euler_changed)
        trans_layout.addWidget(self.tx_input)
        trans_layout.addWidget(QLabel("Y:"))
        self.ty_input = QLineEdit(str(self.shape.translation[1]))
        self.ty_input.setMaximumWidth(60)
        self.ty_input.textChanged.connect(self.on_euler_changed)
        trans_layout.addWidget(self.ty_input)
        trans_layout.addWidget(QLabel("Z:"))
        self.tz_input = QLineEdit(str(self.shape.translation[2]))
        self.tz_input.setMaximumWidth(60)
        self.tz_input.textChanged.connect(self.on_euler_changed)
        trans_layout.addWidget(self.tz_input)
        trans_layout.addStretch()
        layout.addLayout(trans_layout)
        
        # Euler angles
        euler_label = QLabel("Rotation (Euler):")
        euler_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout.addWidget(euler_label)
        
        euler_layout = QHBoxLayout()
        euler_layout.addWidget(QLabel("P:"))
        self.pitch_input = QLineEdit(str(self.shape.rotation_euler[0]))
        self.pitch_input.setMaximumWidth(50)
        self.pitch_input.textChanged.connect(self.on_euler_changed)
        euler_layout.addWidget(self.pitch_input)
        euler_layout.addWidget(QLabel("R:"))
        self.roll_input = QLineEdit(str(self.shape.rotation_euler[1]))
        self.roll_input.setMaximumWidth(50)
        self.roll_input.textChanged.connect(self.on_euler_changed)
        euler_layout.addWidget(self.roll_input)
        euler_layout.addWidget(QLabel("Y:"))
        self.yaw_input = QLineEdit(str(self.shape.rotation_euler[2]))
        self.yaw_input.setMaximumWidth(50)
        self.yaw_input.textChanged.connect(self.on_euler_changed)
        euler_layout.addWidget(self.yaw_input)
        euler_layout.addWidget(QLabel("°"))
        euler_layout.addStretch()
        layout.addLayout(euler_layout)
        
        # Quaternion
        quat_label = QLabel("Rotation (Quaternion):")
        quat_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        layout.addWidget(quat_label)
        
        quat_layout = QHBoxLayout()
        quat_layout.addWidget(QLabel("w:"))
        self.qw_input = QLineEdit(f"{self.shape.rotation_quat[0]:.4f}")
        self.qw_input.setMaximumWidth(60)
        self.qw_input.textChanged.connect(self.on_quat_changed)
        quat_layout.addWidget(self.qw_input)
        quat_layout.addWidget(QLabel("x:"))
        self.qx_input = QLineEdit(f"{self.shape.rotation_quat[1]:.4f}")
        self.qx_input.setMaximumWidth(60)
        self.qx_input.textChanged.connect(self.on_quat_changed)
        quat_layout.addWidget(self.qx_input)
        quat_layout.addWidget(QLabel("y:"))
        self.qy_input = QLineEdit(f"{self.shape.rotation_quat[2]:.4f}")
        self.qy_input.setMaximumWidth(60)
        self.qy_input.textChanged.connect(self.on_quat_changed)
        quat_layout.addWidget(self.qy_input)
        quat_layout.addWidget(QLabel("z:"))
        self.qz_input = QLineEdit(f"{self.shape.rotation_quat[3]:.4f}")
        self.qz_input.setMaximumWidth(60)
        self.qz_input.textChanged.connect(self.on_quat_changed)
        quat_layout.addWidget(self.qz_input)
        quat_layout.addStretch()
        layout.addLayout(quat_layout)
        
        # Color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_box = QLabel("  ")
        color_box.setStyleSheet(f"background-color: {self.shape.color}; border: 1px solid black;")
        color_layout.addWidget(color_box)
        color_layout.addStretch()
        layout.addLayout(color_layout)
    
    def on_visibility_changed(self, state):
        self.shape.visible = (state == Qt.CheckState.Checked.value)
        self.on_update()
    
    def on_euler_changed(self):
        try:
            tx = float(self.tx_input.text() or 0)
            ty = float(self.ty_input.text() or 0)
            tz = float(self.tz_input.text() or 0)
            self.shape.translation = (tx, ty, tz)
            
            pitch = float(self.pitch_input.text() or 0)
            roll = float(self.roll_input.text() or 0)
            yaw = float(self.yaw_input.text() or 0)
            self.shape.set_rotation_euler(pitch, roll, yaw)
            
            # Sync quaternion
            self.qw_input.blockSignals(True)
            self.qx_input.blockSignals(True)
            self.qy_input.blockSignals(True)
            self.qz_input.blockSignals(True)
            self.qw_input.setText(f"{self.shape.rotation_quat[0]:.4f}")
            self.qx_input.setText(f"{self.shape.rotation_quat[1]:.4f}")
            self.qy_input.setText(f"{self.shape.rotation_quat[2]:.4f}")
            self.qz_input.setText(f"{self.shape.rotation_quat[3]:.4f}")
            self.qw_input.blockSignals(False)
            self.qx_input.blockSignals(False)
            self.qy_input.blockSignals(False)
            self.qz_input.blockSignals(False)
            
            self.on_update()
        except ValueError:
            pass
    
    def on_quat_changed(self):
        try:
            tx = float(self.tx_input.text() or 0)
            ty = float(self.ty_input.text() or 0)
            tz = float(self.tz_input.text() or 0)
            self.shape.translation = (tx, ty, tz)
            
            qw = float(self.qw_input.text() or 1)
            qx = float(self.qx_input.text() or 0)
            qy = float(self.qy_input.text() or 0)
            qz = float(self.qz_input.text() or 0)
            self.shape.rotation_quat = (qw, qx, qy, qz)
            euler = self.shape.quat_to_euler()
            self.shape.rotation_euler = euler
            
            # Sync euler
            self.pitch_input.blockSignals(True)
            self.roll_input.blockSignals(True)
            self.yaw_input.blockSignals(True)
            self.pitch_input.setText(f"{euler[0]:.2f}")
            self.roll_input.setText(f"{euler[1]:.2f}")
            self.yaw_input.setText(f"{euler[2]:.2f}")
            self.pitch_input.blockSignals(False)
            self.roll_input.blockSignals(False)
            self.yaw_input.blockSignals(False)
            
            self.on_update()
        except ValueError:
            pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.env = MathEnvironment()
        self.shape_manager = ShapeManager()
        self.shape_widgets = []
        self.init_ui()
        self.statusBar().showMessage("Ready")
    
    def init_ui(self):
        self.setWindowTitle("Math Tool - Shape Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.create_left_panel())
        splitter.addWidget(self.create_right_panel())
        splitter.setSizes([500, 900])
        main_layout.addWidget(splitter)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title = QLabel("Shapes")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Add shape section
        add_section = QFrame()
        add_section.setFrameStyle(QFrame.Shape.StyledPanel)
        add_layout = QVBoxLayout(add_section)
        
        add_label = QLabel("Add New Shape:")
        add_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        add_layout.addWidget(add_label)
        
        self.equation_input = QLineEdit()
        self.equation_input.setPlaceholderText("Enter equation (e.g., x^2 + y^2 = 25)")
        self.equation_input.setFont(QFont("Courier", 10))
        add_layout.addWidget(self.equation_input)
        
        add_btn = QPushButton("➕ Add Shape")
        add_btn.clicked.connect(self.on_add_shape)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                font-size: 12px;
                border-radius: 4px;
            }
        """)
        add_layout.addWidget(add_btn)
        layout.addWidget(add_section)
        
        # Shape list
        list_label = QLabel("Current Shapes:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(list_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.shapes_container = QWidget()
        self.shapes_layout = QVBoxLayout(self.shapes_container)
        self.shapes_layout.addStretch()
        scroll.setWidget(self.shapes_container)
        layout.addWidget(scroll)
        
        # Update button
        update_btn = QPushButton("🔄 Update Plot")
        update_btn.clicked.connect(self.update_plot)
        update_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(update_btn)
        
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Header with 2D/3D toggle
        header_layout = QHBoxLayout()
        title = QLabel("Plot Viewport")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.mode_toggle_btn = QPushButton("Switch to 3D")
        self.mode_toggle_btn.clicked.connect(self.toggle_plot_mode)
        self.mode_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
            }
        """)
        header_layout.addWidget(self.mode_toggle_btn)
        layout.addLayout(header_layout)
        
        # Plot container
        self.plot_container = QWidget()
        self.plot_container_layout = QVBoxLayout(self.plot_container)
        self.plot_container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.current_mode = '2d'
        self.plot_widget = QtPlotWidget(bounds=(-10, 10, -10, 10), mode=self.current_mode)
        self.plot_container_layout.addWidget(self.plot_widget)
        layout.addWidget(self.plot_container)
        
        return panel
    
    def toggle_plot_mode(self):
        self.current_mode = '3d' if self.current_mode == '2d' else '2d'
        self.mode_toggle_btn.setText(f"Switch to {'2D' if self.current_mode == '3d' else '3D'}")
        
        self.plot_container_layout.removeWidget(self.plot_widget)
        self.plot_widget.deleteLater()
        
        self.plot_widget = QtPlotWidget(bounds=(-10, 10, -10, 10), mode=self.current_mode)
        self.plot_container_layout.addWidget(self.plot_widget)
        
        self.update_plot()
        self.statusBar().showMessage(f"Switched to {self.current_mode.upper()}")
    
    def on_add_shape(self):
        equation_str = self.equation_input.text().strip()
        if not equation_str:
            QMessageBox.warning(self, "Error", "Please enter an equation")
            return
        
        try:
            equation = self.env.parse(equation_str)
            shape = self.shape_manager.add_shape(equation_str, equation)
            widget = ShapeWidget(shape, on_update=self.update_plot, on_delete=self.on_delete_shape)
            
            self.shapes_layout.insertWidget(len(self.shape_widgets), widget)
            self.shape_widgets.append(widget)
            self.equation_input.clear()
            self.update_plot()
            self.statusBar().showMessage(f"Added: {shape.name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse:\n{str(e)}")
    
    def on_delete_shape(self, shape: Shape):
        self.shape_manager.remove_shape(shape)
        for i, widget in enumerate(self.shape_widgets):
            if widget.shape == shape:
                self.shapes_layout.removeWidget(widget)
                widget.deleteLater()
                self.shape_widgets.pop(i)
                break
        self.update_plot()
        self.statusBar().showMessage(f"Deleted: {shape.name}")
    
    def update_plot(self):
        visible_shapes = self.shape_manager.get_visible_shapes()
        if len(visible_shapes) == 0:
            self.plot_widget.clear_plot()
            self.statusBar().showMessage("No visible shapes")
        else:
            self.plot_widget.plot_shapes(visible_shapes)
            self.statusBar().showMessage(f"Plotted {len(visible_shapes)} shape(s)")


def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()