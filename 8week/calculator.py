import sys
import operator
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

# 버튼 역할 정의
TYPE_NUMBER = 'number'
TYPE_OPERATOR = 'operator'
TYPE_FUNCTION = 'function'
TYPE_ZERO = 'zero'
TYPE_EQUAL = 'equal'
TYPE_CLEAR = 'clear'

# (텍스트, 행, 열, 행 병합, 열 병합, 버튼 타입)
BUTTON_LAYOUT = [
    ('AC', 0, 0, 1, 1, TYPE_CLEAR), ('+/-', 0, 1, 1, 1, TYPE_FUNCTION),
    ('%', 0, 2, 1, 1, TYPE_FUNCTION), ('/', 0, 3, 1, 1, TYPE_OPERATOR),
    ('7', 1, 0, 1, 1, TYPE_NUMBER), ('8', 1, 1, 1, 1, TYPE_NUMBER),
    ('9', 1, 2, 1, 1, TYPE_NUMBER), ('*', 1, 3, 1, 1, TYPE_OPERATOR),
    ('4', 2, 0, 1, 1, TYPE_NUMBER), ('5', 2, 1, 1, 1, TYPE_NUMBER),
    ('6', 2, 2, 1, 1, TYPE_NUMBER), ('-', 2, 3, 1, 1, TYPE_OPERATOR),
    ('1', 3, 0, 1, 1, TYPE_NUMBER), ('2', 3, 1, 1, 1, TYPE_NUMBER),
    ('3', 3, 2, 1, 1, TYPE_NUMBER), ('+', 3, 3, 1, 1, TYPE_OPERATOR),
    ('0', 4, 0, 1, 2, TYPE_ZERO), ('.', 4, 2, 1, 1, TYPE_NUMBER),
    ('=', 4, 3, 1, 1, TYPE_EQUAL)
]

# 스타일 설정
STYLES = {
    'window': 'background-color: #1C1C1C;',
    'display': 'color: white; font-size: 50px; font-family: Arial; padding: 10px;',
    TYPE_OPERATOR: 'background-color: #FF9500; color: white; border-radius: 30px; font-size: 24px;',
    TYPE_EQUAL: 'background-color: #FF9500; color: white; border-radius: 30px; font-size: 24px;',
    TYPE_FUNCTION: 'background-color: #D4D4D2; color: black; border-radius: 30px; font-size: 20px;',
    TYPE_NUMBER: 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px;',
    TYPE_ZERO: 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px; text-align: left; padding-left: 25px;',
    TYPE_CLEAR: 'background-color: #D4D4D2; color: black; border-radius: 30px; font-size: 20px;'
}


class CalculatorEngine:
    def __init__(self):
        self.current_value = '0'
        self.previous_value = ''
        self.operator = ''
        self.new_input = True
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }

    def input_character(self, char):
        if self.new_input:
            self.current_value = char if char != '.' else '0.'
            self.new_input = False
        else:
            if char == '.' and '.' in self.current_value:
                return self.get_formatted_value()
            if self.current_value == '0' and char != '.':
                self.current_value = char
            else:
                self.current_value += char
        return self.get_formatted_value()

    def input_operator(self, op):
        if not self.new_input and self.previous_value:
            self.calculate()
        self.previous_value = self.current_value
        self.operator = op
        self.new_input = True
        return self.get_formatted_value()

    def calculate(self):
        if not self.operator or not self.previous_value:
            return self.get_formatted_value()
        try:
            num1 = float(self.previous_value.replace(',', ''))
            num2 = float(self.current_value.replace(',', ''))
            operation_func = self.operations.get(self.operator)
            if operation_func:
                if self.operator == '/' and num2 == 0:
                    self.current_value = 'Error'
                else:
                    result = operation_func(num1, num2)
                    if result.is_integer():
                        self.current_value = str(int(result))
                    else:
                        self.current_value = str(result)
        except Exception:
            self.current_value = 'Error'
        self.operator = ''
        self.previous_value = ''
        self.new_input = True
        return self.get_formatted_value()

    def clear(self):
        self.current_value = '0'
        self.previous_value = ''
        self.operator = ''
        self.new_input = True
        return self.get_formatted_value()

    def toggle_sign(self):
        if self.current_value != '0' and self.current_value != 'Error':
            if self.current_value.startswith('-'):
                self.current_value = self.current_value[1:]
            else:
                self.current_value = '-' + self.current_value
        return self.get_formatted_value()

    def get_formatted_value(self):
        if self.current_value == 'Error':
            return self.current_value
        try:
            parts = self.current_value.split('.')
            integer_part = int(parts[0].replace(',', ''))
            formatted_int = f'{integer_part:,}'
            if len(parts) > 1:
                return f'{formatted_int}.{parts[1]}'
            return formatted_int
        except (ValueError, IndexError):
            return self.current_value


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
                lambda checked, t = text, b = btn_type: self.on_button_click(t, b)
            )

    def on_button_click(self, text, btn_type):
        if btn_type == TYPE_NUMBER or text == '.':
            new_text = self.engine.input_character(text)
        elif btn_type == TYPE_OPERATOR:
            new_text = self.engine.input_operator(text)
        elif btn_type == TYPE_EQUAL:
            new_text = self.engine.calculate()
        elif btn_type == TYPE_CLEAR:
            new_text = self.engine.clear()
        elif text == '+/-':
            new_text = self.engine.toggle_sign()
        elif text == '%':
            self.engine.input_operator('/')
            self.engine.input_character('100')
            new_text = self.engine.calculate()
        else:
            new_text = self.display.text()
        self.display.setText(new_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_app = CalculatorUI()
    calc_app.show()
    sys.exit(app.exec_())

