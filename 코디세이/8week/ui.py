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
        self.setWindowTitle('Calculator')
        self.setFixedSize(320, 500)
        self.setStyleSheet(STYLES['window'])
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 20, 15, 20)
        self.setLayout(layout)
        
        self.display = QLabel('0')
        self.display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.display.setStyleSheet(STYLES['display'])
        layout.addWidget(self.display)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        layout.addLayout(grid_layout)
        
        for text, row, col, row_span, col_span, btn_type in BUTTON_LAYOUT:
            button = QPushButton(text)
            button.setMinimumHeight(60)
            
            style = STYLES.get(btn_type, '')
            button.setStyleSheet(style)
            
            grid_layout.addWidget(button, row, col, row_span, col_span)
            button.clicked.connect(
                lambda checked, t=text, b=btn_type: self.on_button_click(t, b)
            )

    def update_display(self, text):
        """보너스 과제: 출력 길이에 따른 동적 폰트 크기 조절"""
        length = len(text)
        if length > 12:
            font_size = 30
        elif length > 9:
            font_size = 40
        else:
            font_size = 50
            
        self.display.setStyleSheet(f'color: white; font-size: {font_size}px; font-family: Arial; padding: 10px;')
        self.display.setText(text)

    def on_button_click(self, text, btn_type):
        if btn_type in ['number', 'zero'] or text == '.':
            new_text = self.engine.input_character(text)
            
        elif btn_type == 'operator':
            new_text = self.engine.input_operator(text)
            
        elif btn_type == 'equal':
            new_text = self.engine.equal()
            
        elif btn_type in ['function', 'clear']:
            new_text = self.engine.execute_function(text)
            
        else:
            new_text = self.display.text()
            
        self.update_display(new_text)