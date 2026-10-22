PI = 3.141592653589793

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
WHITE = "\033[97m"


def sine(x):
    x = x % (2 * PI)
    if x > PI:
        x -= 2 * PI
    term = x
    total = x
    for n in range(1, 12):
        term *= -x * x / ((2 * n) * (2 * n + 1))
        total += term
    return total


def cosine(x):
    return sine(x + PI / 2)


def parse_time(text):
    parts = text.strip().split(":")
    if len(parts) not in (2, 3):
        return None, "Use HH:MM or HH:MM:SS, for example 14:05"
    for part in parts:
        if not part.isdigit() or len(part) > 2:
            return None, "Use only numbers separated by ':', for example 14:05"
    numbers = [int(part) for part in parts] + [0]
    hours, minutes, seconds = numbers[0], numbers[1], numbers[2]
    if hours > 23:
        return None, "Hours must be between 0 and 23"
    if minutes > 59:
        return None, "Minutes must be between 0 and 59"
    if seconds > 59:
        return None, "Seconds must be between 0 and 59"
    return hours * 3600 + minutes * 60 + seconds, None


def parse_duration(text):
    parts = text.strip().split(":")
    if len(parts) not in (2, 3):
        return None, "Use MM:SS or HH:MM:SS, for example 05:00"
    for part in parts:
        if not part.isdigit() or len(part) > 2:
            return None, "Use only numbers separated by ':', for example 05:00"
    numbers = [int(part) for part in parts]
    if len(numbers) == 2:
        numbers = [0] + numbers
    hours, minutes, seconds = numbers
    if minutes > 59 or seconds > 59:
        return None, "Minutes and seconds must be between 0 and 59"
    total = hours * 3600 + minutes * 60 + seconds
    if total == 0:
        return None, "The timer must be longer than 00:00"
    return total, None


def ask(prompt, parser, allow_empty=False):
    while True:
        text = input(prompt)
        if allow_empty and text.strip() == "":
            return None
        value, error = parser(text)
        if error is None:
            return value
        print(YELLOW + "  " + error + RESET)


def format_seconds(total):
    total = total % 86400
    return "%02d:%02d:%02d" % (total // 3600, total // 60 % 60, total % 60)


def close(a, b):
    return abs(a - b) < 1e-9


def self_test():
    assert close(sine(0), 0)
    assert close(sine(PI / 2), 1)
    assert close(sine(PI), 0)
    assert close(sine(-PI / 2), -1)
    assert close(cosine(0), 1)
    assert close(cosine(PI), -1)
    assert close(sine(13 * PI / 6), 0.5)
    assert parse_time("14:05") == (50700, None)
    assert parse_time("23:59:59") == (86399, None)
    assert parse_time("0:0") == (0, None)
    assert parse_time("24:00")[0] is None
    assert parse_time("12:60")[0] is None
    assert parse_time("ab:10")[0] is None
    assert parse_time("1200")[0] is None
    assert parse_duration("05:00") == (300, None)
    assert parse_duration("01:00:30") == (3630, None)
    assert parse_duration("00:00")[0] is None
    assert format_seconds(50700) == "14:05:00"
    assert format_seconds(86400) == "00:00:00"


if __name__ == "__main__":
    self_test()
