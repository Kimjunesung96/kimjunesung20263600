# engine.py
import operator

class CalculatorEngine:
    def __init__(self):
        self.current_value = '0'
        self.previous_value = ''
        self.operator = ''
        self.new_input = True
        
        # 🌟 핵심 1: 연산자 매핑 (if-elif 박멸)
        self.operations = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv
        }
        
        # 🌟 핵심 2: 특수기능 매핑 (UI 하드코딩 박멸)
        self.functions = {
            '+/-': self.toggle_sign,
            '%': self.calculate_percentage,
            'AC': self.clear
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
            
            # 딕셔너리에서 함수 포인터(?) 가져오기
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

    # UI에 있던 % 계산 로직을 엔진으로 납치!
    def calculate_percentage(self):
        self.input_operator('/')
        self.input_character('100')
        return self.calculate()

    # 특수 버튼(Function, Clear) 처리를 위한 통합 창구
    def execute_function(self, func_name):
        action = self.functions.get(func_name)
        if action:
            return action()
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
            # 박사님의 절대 규칙(index 0) 적용!
            integer_part = int(parts[0].replace(',', ''))
            formatted_int = f'{integer_part:,}'
            
            # 소수점 버그 완벽 수정 (정수부가 아닌 소수부인 인덱스 1번 연결)
            if len(parts) > 1:
                return f'{formatted_int}.{parts}'
            return formatted_int
        except (ValueError, IndexError):
            return self.current_value