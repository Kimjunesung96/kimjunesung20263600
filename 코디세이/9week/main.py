# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui import CalculatorUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_app = CalculatorUI()
    calc_app.show()
    sys.exit(app.exec_())