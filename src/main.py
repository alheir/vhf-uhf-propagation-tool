"""
This script initializes and runs a PyQt6 application.

It imports the necessary modules, creates an instance of the QApplication,
creates and shows the main window, and starts the event loop.

Modules:
    gui (MainWindow): Custom module containing the main window class.
    sys: Provides access to some variables used or maintained by the interpreter.
    PyQt6.QtWidgets (QApplication): Provides the QApplication class to manage application-wide resources.

Usage:
    Run this script directly to start the PyQt6 application.
"""

from gui import MainWindow
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application    
    window = MainWindow()         # Create an instance of your MainWindow
    window.show()                 # Show the window
    sys.exit(app.exec())          # Start the event loop    