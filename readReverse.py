log_file = 'mission_computer_main.log'
problem_file = 'problem_logs.txt'
keyword = 'explosion'

try:
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in reversed(lines):
        print(line.strip())

    problems = []
    for i, line in enumerate(lines):
        if keyword in line:
            problems = lines[max(0, i - 3):i + 1]
            break

    with open(problem_file, 'w', encoding='utf-8') as f:
        for p in problems:
            f.write(p)

except Exception as e:
    print(e)
