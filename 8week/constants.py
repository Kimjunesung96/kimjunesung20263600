# constants.py

# (버튼 텍스트, 행, 열, 행 병합, 열 병합)
BUTTON_LAYOUT = [
    ('AC', 0, 0, 1, 1), ('+/-', 0, 1, 1, 1), ('%', 0, 2, 1, 1), ('/', 0, 3, 1, 1),
    ('7', 1, 0, 1, 1), ('8', 1, 1, 1, 1), ('9', 1, 2, 1, 1), ('*', 1, 3, 1, 1),
    ('4', 2, 0, 1, 1), ('5', 2, 1, 1, 1), ('6', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
    ('1', 3, 0, 1, 1), ('2', 3, 1, 1, 1), ('3', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
    ('0', 4, 0, 1, 2), ('.', 4, 2, 1, 1), ('=', 4, 3, 1, 1)
]

# UI 스타일 설정
STYLES = {
    'window': 'background-color: #1C1C1C;',
    'display': 'color: white; font-size: 50px; font-family: Arial;',
    'operator': 'background-color: #FF9500; color: white; border-radius: 30px; font-size: 24px;',
    'function': 'background-color: #D4D4D2; color: black; border-radius: 30px; font-size: 20px;',
    'number': 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px;',
    'zero': 'background-color: #505050; color: white; border-radius: 30px; font-size: 24px; text-align: left; padding-left: 25px;'
}