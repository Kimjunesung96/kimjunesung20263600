# constants.py

# (텍스트, 행, 열, 행 병합, 열 병합, 버튼 타입)
BUTTON_LAYOUT = [
    ('AC', 0, 0, 1, 1, 'clear'), ('+/-', 0, 1, 1, 1, 'function'),
    ('%', 0, 2, 1, 1, 'function'), ('/', 0, 3, 1, 1, 'operator'),
    ('7', 1, 0, 1, 1, 'number'), ('8', 1, 1, 1, 1, 'number'),
    ('9', 1, 2, 1, 1, 'number'), ('*', 1, 3, 1, 1, 'operator'),
    ('4', 2, 0, 1, 1, 'number'), ('5', 2, 1, 1, 1, 'number'),
    ('6', 2, 2, 1, 1, 'number'), ('-', 2, 3, 1, 1, 'operator'),
    ('1', 3, 0, 1, 1, 'number'), ('2', 3, 1, 1, 1, 'number'),
    ('3', 3, 2, 1, 1, 'number'), ('+', 3, 3, 1, 1, 'operator'),
    ('0', 4, 0, 1, 2, 'zero'), ('.', 4, 2, 1, 1, 'number'),
    ('=', 4, 3, 1, 1, 'equal')
]

STYLES = {
    'window': 'background-color: #1C1C1C;',
    'display': 'color: white; font-size: 50px; font-family: Arial; padding: 10px;',
    'operator': 'background-color: #FF9500; color: white; border-radius: 30px; font-size: 24px;',
    'equal': 'background-color: #FF9500; color: white; border-radius: 30px; font-size: 24px;',
    'function': 'background-color: #D4D4D2; color: black; border-radius: 30px; font-size: 20px;',
    'clear': 'background-color: #D4D4D2; color: black; border-radius: 30px; font-size: 20px;',
    'number': 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px;',
    'zero': 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px; text-align: left; padding-left: 25px;'
}