# ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from engine import CalculatorEngine
from constants import BUTTON_LAYOUT, STYLES

class CalculatorUI(QWidget):
    def __init__(self):
        super().__init__()
        self.engine = CalculatorEngine()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Emergency Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet(STYLES['window'])
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(15, 20, 15, 20)
        self.setLayout(self.layout)
        
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.display.setStyleSheet(STYLES['display'])
        self.layout.addWidget(self.display)
        
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.layout.addLayout(self.grid_layout)
        
        # constants.py에서 배열을 가져와서 UI 생성 (하드코딩 제거)
        for text, row, col, row_span, col_span in BUTTON_LAYOUT:
            button = QPushButton(text)
            button.setMinimumHeight(60)
            
            if text in ['/', '*', '-', '+', '=']:
                button.setStyleSheet(STYLES['operator'])
            elif text in ['AC', '+/-', '%']:
                button.setStyleSheet(STYLES['function'])
            elif text == '0':
                button.setStyleSheet(STYLES['zero'])
            else:
                button.setStyleSheet(STYLES['number'])
                
            self.grid_layout.addWidget(button, row, col, row_span, col_span)
            button.clicked.connect(lambda checked, t=text: self.on_button_click(t))

    def on_button_click(self, text):
        if text.isdigit() or text == '.':
            new_text = self.engine.input_character(text)
            self.display.setText(new_text)
        elif text in ['+', '-', '*', '/']:
            new_text = self.engine.input_operator(text)
            self.display.setText(new_text)
        elif text == '=':
            new_text = self.engine.calculate()
            self.display.setText(new_text)
        elif text == 'AC':
            new_text = self.engine.clear()
            self.display.setText(new_text)
        elif text == '+/-':
            new_text = self.engine.toggle_sign()
            self.display.setText(new_text)
        elif text == '%':
            new_text = self.engine.input_operator('/')
            self.display.setText(new_text)
            new_text = self.engine.input_character('100')
            self.display.setText(new_text)
            new_text = self.engine.calculate()
            self.display.setText(new_text)