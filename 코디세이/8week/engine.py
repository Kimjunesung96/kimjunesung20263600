# engine.py

class CalculatorEngine:
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.current_value = '0'
        self.previous_value = ''
        self.operator = ''
        self.new_input = True
        return self.current_value

    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0.0:
            raise ZeroDivisionError
        return a / b

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
        if self.current_value == 'Error':
            return self.current_value
        if not self.new_input and self.previous_value:
            self.equal()
        self.previous_value = self.current_value
        self.operator = op
        self.new_input = True
        return self.get_formatted_value()

    def equal(self):
        if not self.operator or not self.previous_value or self.current_value == 'Error':
            return self.get_formatted_value()
        try:
            num1 = float(self.previous_value.replace(',', ''))
            num2 = float(self.current_value.replace(',', ''))
            result = 0.0
            
            if self.operator == '+':
                result = self.add(num1, num2)
            elif self.operator == '-':
                result = self.subtract(num1, num2)
            elif self.operator == '*':
                result = self.multiply(num1, num2)
            elif self.operator == '/':
                result = self.divide(num1, num2)

            # 보너스 과제: 소수점 6자리 이하 반올림 적용
            result = round(result, 6)

            if result.is_integer():
                self.current_value = str(int(result))
            else:
                self.current_value = str(result)
                
        except ZeroDivisionError:
            self.current_value = 'Error'
        except OverflowError:
            self.current_value = 'Error'
        except Exception:
            self.current_value = 'Error'
            
        self.operator = ''
        self.previous_value = ''
        self.new_input = True
        return self.get_formatted_value()

    def percent(self):
        if self.current_value == 'Error':
            return self.current_value
        try:
            val = float(self.current_value.replace(',', '')) / 100
            val = round(val, 6)
            if val.is_integer():
                self.current_value = str(int(val))
            else:
                self.current_value = str(val)
            self.new_input = True
        except Exception:
            self.current_value = 'Error'
        return self.get_formatted_value()

    def negative_positive(self):
        if self.current_value != '0' and self.current_value != 'Error':
            if self.current_value.startswith('-'):
                self.current_value = self.current_value[1:]
            else:
                self.current_value = '-' + self.current_value
        return self.get_formatted_value()

    def execute_function(self, func_name):
        if func_name == 'AC':
            return self.reset()
        elif func_name == '+/-':
            return self.negative_positive()
        elif func_name == '%':
            return self.percent()
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