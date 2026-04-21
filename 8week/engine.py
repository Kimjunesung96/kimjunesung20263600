# engine.py

class CalculatorEngine:
    def __init__(self):
        self.current_value = '0'
        self.previous_value = ''
        self.operator = ''
        self.new_input = True

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
            result = 0.0
            
            if self.operator == '+':
                result = num1 + num2
            elif self.operator == '-':
                result = num1 - num2
            elif self.operator == '*':
                result = num1 * num2
            elif self.operator == '/':
                if num2 == 0:
                    self.current_value = 'Error'
                    self.new_input = True
                    return self.current_value
                result = num1 / num2

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
                return f'{formatted_int}.{parts[0]}'
            return formatted_int
        except ValueError:
            return self.current_value