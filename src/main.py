#!/usr/bin/env python
"""
Math Tool - Main Entry Point
"""

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # Import the main window
    from ui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    app.setApplicationName("Math Tool")
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())