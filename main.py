import sys
from PyQt6.QtWidgets import QApplication
from gui import PropagationCalculatorGUI

def main():
    app = QApplication(sys.argv)
    window = PropagationCalculatorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
    
    