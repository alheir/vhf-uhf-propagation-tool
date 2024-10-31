import sys
from PyQt6.QtWidgets import QApplication
from gui import PropagationCalculator

def main():
    app = QApplication(sys.argv)
    window = PropagationCalculator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()