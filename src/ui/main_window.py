"""
Main Window - With Shape Management
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
    """
    Widget for a single shape with controls
    """
    
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
        
        # Header row: Name, Visible checkbox, Delete button
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
        
        # Translation controls
        trans_layout = QHBoxLayout()
        trans_layout.addWidget(QLabel("Position:"))
        
        trans_layout.addWidget(QLabel("X:"))
        self.tx_input = QLineEdit(str(self.shape.translation[0]))
        self.tx_input.setMaximumWidth(60)
        self.tx_input.textChanged.connect(self.on_transform_changed)
        trans_layout.addWidget(self.tx_input)
        
        trans_layout.addWidget(QLabel("Y:"))
        self.ty_input = QLineEdit(str(self.shape.translation[1]))
        self.ty_input.setMaximumWidth(60)
        self.ty_input.textChanged.connect(self.on_transform_changed)
        trans_layout.addWidget(self.ty_input)
        
        trans_layout.addStretch()
        layout.addLayout(trans_layout)
        
        # Rotation controls (dimension-aware)
        if self.shape.dimension == 2:
            # 2D: Single angle (yaw only)
            rot_layout = QHBoxLayout()
            rot_layout.addWidget(QLabel("Rotation:"))
            self.rot_input = QLineEdit(str(self.shape.get_rotation_angle_2d()))
            self.rot_input.setMaximumWidth(60)
            self.rot_input.textChanged.connect(self.on_transform_changed)
            rot_layout.addWidget(self.rot_input)
            rot_layout.addWidget(QLabel("°"))
            rot_layout.addStretch()
            layout.addLayout(rot_layout)
        else:
            # 3D: Pitch, Roll, Yaw
            rot_layout = QVBoxLayout()
            rot_label = QLabel("Rotation (Euler):")
            rot_layout.addWidget(rot_label)
            
            # Pitch
            pitch_layout = QHBoxLayout()
            pitch_layout.addWidget(QLabel("Pitch:"))
            self.pitch_input = QLineEdit(str(self.shape.rotation_euler[0]))
            self.pitch_input.setMaximumWidth(60)
            self.pitch_input.textChanged.connect(self.on_transform_changed)
            pitch_layout.addWidget(self.pitch_input)
            pitch_layout.addWidget(QLabel("°"))
            pitch_layout.addStretch()
            rot_layout.addLayout(pitch_layout)
            
            # Roll
            roll_layout = QHBoxLayout()
            roll_layout.addWidget(QLabel("Roll:"))
            self.roll_input = QLineEdit(str(self.shape.rotation_euler[1]))
            self.roll_input.setMaximumWidth(60)
            self.roll_input.textChanged.connect(self.on_transform_changed)
            roll_layout.addWidget(self.roll_input)
            roll_layout.addWidget(QLabel("°"))
            roll_layout.addStretch()
            rot_layout.addLayout(roll_layout)
            
            # Yaw
            yaw_layout = QHBoxLayout()
            yaw_layout.addWidget(QLabel("Yaw:"))
            self.yaw_input = QLineEdit(str(self.shape.rotation_euler[2]))
            self.yaw_input.setMaximumWidth(60)
            self.yaw_input.textChanged.connect(self.on_transform_changed)
            yaw_layout.addWidget(self.yaw_input)
            yaw_layout.addWidget(QLabel("°"))
            yaw_layout.addStretch()
            rot_layout.addLayout(yaw_layout)
            
            layout.addLayout(rot_layout)
        
        # Color indicator
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        color_box = QLabel("  ")
        color_box.setStyleSheet(f"background-color: {self.shape.color}; border: 1px solid black;")
        color_layout.addWidget(color_box)
        color_layout.addStretch()
        layout.addLayout(color_layout)
    
    def on_visibility_changed(self, state):
        """Handle visibility checkbox"""
        self.shape.visible = (state == Qt.CheckState.Checked.value)
        self.on_update()
    
    def on_transform_changed(self):
        """Handle translation and rotation input changes"""
        try:
            tx = float(self.tx_input.text() or 0)
            ty = float(self.ty_input.text() or 0)
            
            self.shape.translation = (tx, ty, 0.0)
            
            # Handle rotation based on dimension
            if self.shape.dimension == 2:
                rot = float(self.rot_input.text() or 0)
                self.shape.set_rotation_euler(yaw=rot)
            else:
                pitch = float(self.pitch_input.text() or 0)
                roll = float(self.roll_input.text() or 0)
                yaw = float(self.yaw_input.text() or 0)
                self.shape.set_rotation_euler(pitch, roll, yaw)
            
            self.on_update()
        except ValueError:
            pass  # Ignore invalid input


class MainWindow(QMainWindow):
    """
    Main window with shape management
    """
    
    def __init__(self):
        super().__init__()
        
        self.env = MathEnvironment()
        self.shape_manager = ShapeManager()
        self.shape_widgets = []
        
        self.init_ui()
        self.statusBar().showMessage("Ready - Add shapes to begin")
    
    def init_ui(self):
        self.setWindowTitle("Math Tool - Shape Manager")
        self.setGeometry(100, 100, 1400, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel - Shape list + editor
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Plot
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([500, 900])
        main_layout.addWidget(splitter)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
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
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_layout.addWidget(add_btn)
        
        layout.addWidget(add_section)
        
        # Shape list (scrollable)
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
        
        # Update all button
        update_all_btn = QPushButton("🔄 Update Plot")
        update_all_btn.clicked.connect(self.update_plot)
        update_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-size: 13px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(update_all_btn)
        
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title = QLabel("Plot Viewport")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        self.plot_widget = QtPlotWidget(bounds=(-10, 10, -10, 10))
        layout.addWidget(self.plot_widget)
        
        return panel
    
    def on_add_shape(self):
        """Add a new shape"""
        equation_str = self.equation_input.text().strip()
        
        if not equation_str:
            QMessageBox.warning(self, "Error", "Please enter an equation")
            return
        
        try:
            # Parse equation
            equation = self.env.parse(equation_str)
            
            # Add to manager
            shape = self.shape_manager.add_shape(equation_str, equation)
            
            # Create widget
            widget = ShapeWidget(
                shape, 
                on_update=self.update_plot,
                on_delete=self.on_delete_shape
            )
            
            # Add to layout (before the stretch)
            self.shapes_layout.insertWidget(len(self.shape_widgets), widget)
            self.shape_widgets.append(widget)
            
            # Clear input
            self.equation_input.clear()
            
            # Update plot
            self.update_plot()
            
            self.statusBar().showMessage(f"Added: {shape.name}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse equation:\n{str(e)}")
    
    def on_delete_shape(self, shape: Shape):
        """Delete a shape"""
        # Remove from manager
        self.shape_manager.remove_shape(shape)
        
        # Find and remove widget
        for i, widget in enumerate(self.shape_widgets):
            if widget.shape == shape:
                self.shapes_layout.removeWidget(widget)
                widget.deleteLater()
                self.shape_widgets.pop(i)
                break
        
        # Update plot
        self.update_plot()
        
        self.statusBar().showMessage(f"Deleted: {shape.name}")
    
    def update_plot(self):
        """Update the plot with all visible shapes"""
        visible_shapes = self.shape_manager.get_visible_shapes()
        
        if len(visible_shapes) == 0:
            self.plot_widget.clear_plot()
            self.statusBar().showMessage("No visible shapes")
        else:
            self.plot_widget.plot_shapes(visible_shapes)
            self.statusBar().showMessage(f"Plotted {len(visible_shapes)} shape(s)")


def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()