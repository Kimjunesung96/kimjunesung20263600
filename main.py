print('Hello Mars')

file_name = 'mission_computer_main.log'

try:
    with open(file_name, 'r') as file:
        for line in file:
            print(line.strip())

except FileNotFoundError:
    print('File not found.')

except Exception as e:
    print('Error:', e)
