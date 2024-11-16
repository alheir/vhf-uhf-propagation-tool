from gui import MainWindow
import sys
from PyQt6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Create the application
    window = MainWindow()         # Create an instance of your MainWindow
    window.show()                 # Show the window
    sys.exit(app.exec())          # Start the event loop