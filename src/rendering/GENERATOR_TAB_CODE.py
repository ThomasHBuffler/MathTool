"""
ADD THIS TO create_left_panel() in MainWindow class
Replace the existing "Add shape section" with this tabbed interface
"""

from PyQt6.QtWidgets import QTabWidget, QComboBox

# ... inside create_left_panel() ...

# Tabs for Manual entry vs Generator
tabs = QTabWidget()

# ===== TAB 1: MANUAL ENTRY =====
manual_tab = QWidget()
manual_layout = QVBoxLayout(manual_tab)

manual_label = QLabel("Enter Equation:")
manual_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
manual_layout.addWidget(manual_label)

self.equation_input = QLineEdit()
self.equation_input.setPlaceholderText("e.g., x^2 + y^2 = 25")
self.equation_input.setFont(QFont("Courier", 10))
manual_layout.addWidget(self.equation_input)

add_manual_btn = QPushButton("➕ Add Shape")
add_manual_btn.clicked.connect(self.on_add_shape_manual)
add_manual_btn.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        color: white;
        padding: 8px;
        border-radius: 4px;
    }
""")
manual_layout.addWidget(add_manual_btn)
manual_layout.addStretch()

# ===== TAB 2: IDENTITY LIBRARY =====
identity_tab = QWidget()
id_layout = QVBoxLayout(identity_tab)

id_label = QLabel("Shape Identity Library:")
id_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
id_layout.addWidget(id_label)

# Identity selector
self.identity_combo = QComboBox()
from math_engine.builder import DimensionAgnosticBuilder
self.builder = DimensionAgnosticBuilder()
for name in self.builder.get_identity_names():
    identity = self.builder.get_identity(name)
    self.identity_combo.addItem(name, identity)
self.identity_combo.currentIndexChanged.connect(self.on_identity_selected)
id_layout.addWidget(self.identity_combo)

# Description
self.identity_desc = QLabel("")
self.identity_desc.setWordWrap(True)
self.identity_desc.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
id_layout.addWidget(self.identity_desc)

# Dimension selector
dim_layout = QHBoxLayout()
dim_layout.addWidget(QLabel("Dimension:"))
self.dimension_combo = QComboBox()
self.dimension_combo.addItems(["2D", "3D", "4D", "5D"])
self.dimension_combo.currentIndexChanged.connect(self.update_identity_preview)
dim_layout.addWidget(self.dimension_combo)
dim_layout.addStretch()
id_layout.addLayout(dim_layout)

# Parameters (dynamic based on identity)
self.param_widgets = {}
self.param_layout = QVBoxLayout()
id_layout.addLayout(self.param_layout)

# Preview
preview_label = QLabel("Preview:")
preview_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
id_layout.addWidget(preview_label)

self.identity_preview = QLabel("")
self.identity_preview.setWordWrap(True)
self.identity_preview.setStyleSheet("color: #000; font-family: monospace; padding: 5px; background: #f0f0f0;")
id_layout.addWidget(self.identity_preview)

add_identity_btn = QPushButton("➕ Add from Library")
add_identity_btn.clicked.connect(self.on_add_identity)
add_identity_btn.setStyleSheet("""
    QPushButton {
        background-color: #2196F3;
        color: white;
        padding: 8px;
        border-radius: 4px;
    }
""")
id_layout.addWidget(add_identity_btn)
id_layout.addStretch()

# ===== TAB 3: CUSTOM GENERATOR =====
custom_tab = QWidget()
custom_layout = QVBoxLayout(custom_tab)

custom_label = QLabel("Custom Expression:")
custom_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
custom_layout.addWidget(custom_label)

help_text = QLabel("Use: sum(Dim^2), sum(|Dim|), max(|Dim|), prod(Dim), etc.")
help_text.setStyleSheet("color: #666; font-size: 9px;")
custom_layout.addWidget(help_text)

self.custom_expr_input = QLineEdit()
self.custom_expr_input.setPlaceholderText("e.g., sum(Dim^2/a^2) = 1")
self.custom_expr_input.setFont(QFont("Courier", 10))
self.custom_expr_input.textChanged.connect(self.update_custom_preview)
custom_layout.addWidget(self.custom_expr_input)

# Dimension for custom
custom_dim_layout = QHBoxLayout()
custom_dim_layout.addWidget(QLabel("Dimension:"))
self.custom_dimension_input = QLineEdit("2")
self.custom_dimension_input.setMaximumWidth(60)
self.custom_dimension_input.textChanged.connect(self.update_custom_preview)
custom_dim_layout.addWidget(self.custom_dimension_input)
custom_dim_layout.addStretch()
custom_layout.addLayout(custom_dim_layout)

# Custom parameters
custom_param_label = QLabel("Parameters (optional):")
custom_layout.addWidget(custom_param_label)

self.custom_param_input = QLineEdit()
self.custom_param_input.setPlaceholderText("e.g., a=2, b=3, r=5")
self.custom_param_input.textChanged.connect(self.update_custom_preview)
custom_layout.addWidget(self.custom_param_input)

# Preview
custom_preview_label = QLabel("Preview:")
custom_preview_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
custom_layout.addWidget(custom_preview_label)

self.custom_preview = QLabel("")
self.custom_preview.setWordWrap(True)
self.custom_preview.setStyleSheet("color: #000; font-family: monospace; padding: 5px; background: #f0f0f0;")
custom_layout.addWidget(self.custom_preview)

add_custom_btn = QPushButton("➕ Generate & Add")
add_custom_btn.clicked.connect(self.on_add_custom)
add_custom_btn.setStyleSheet("""
    QPushButton {
        background-color: #FF9800;
        color: white;
        padding: 8px;
        border-radius: 4px;
    }
""")
custom_layout.addWidget(add_custom_btn)
custom_layout.addStretch()

# Add tabs
tabs.addTab(manual_tab, "Manual")
tabs.addTab(identity_tab, "Library")
tabs.addTab(custom_tab, "Custom")
layout.addWidget(tabs)

# Initialize first identity
self.on_identity_selected(0)

# Rest of panel (shape list, update button, etc.)
# ... continues with shape list code ...
