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


WIDTH = 45
HEIGHT = 23
CENTER_X = 22
CENTER_Y = 11
RADIUS_X = 20
RADIUS_Y = 10

DIGITS = {
    "0": [" _ ", "| |", "|_|"],
    "1": ["   ", "  |", "  |"],
    "2": [" _ ", " _|", "|_ "],
    "3": [" _ ", " _|", " _|"],
    "4": ["   ", "|_|", "  |"],
    "5": [" _ ", "|_ ", " _|"],
    "6": [" _ ", "|_ ", "|_|"],
    "7": [" _ ", "  |", "  |"],
    "8": [" _ ", "|_|", "|_|"],
    "9": [" _ ", "|_|", " _|"],
    ":": [" ", ".", "."],
}


def point(angle, length):
    x = CENTER_X + length * RADIUS_X * sine(angle)
    y = CENTER_Y - length * RADIUS_Y * cosine(angle)
    return int(round(x)), int(round(y))


def put(canvas, x, y, char, color):
    if 0 <= y < HEIGHT and 0 <= x < WIDTH:
        canvas[y][x] = (char, color)


def draw_hand(canvas, angle, length, char, color):
    steps = int(length * 40)
    for step in range(1, steps + 1):
        x, y = point(angle, length * step / steps)
        put(canvas, x, y, char, color)


def draw_face(seconds_of_day):
    canvas = [[(" ", "") for _ in range(WIDTH)] for _ in range(HEIGHT)]
    for step in range(240):
        x, y = point(2 * PI * step / 240, 1)
        put(canvas, x, y, ".", DIM)
    for minute in range(0, 60, 5):
        x, y = point(2 * PI * minute / 60, 1)
        put(canvas, x, y, "+", WHITE)
    for hour in range(1, 13):
        label = str(hour)
        x, y = point(2 * PI * hour / 12, 0.82)
        for index in range(len(label)):
            put(canvas, x - len(label) // 2 + index, y, label[index], BOLD + WHITE)
    hours = seconds_of_day / 3600 % 12
    minutes = seconds_of_day % 3600 / 60
    seconds = seconds_of_day % 60
    draw_hand(canvas, 2 * PI * seconds / 60, 0.7, ".", RED)
    draw_hand(canvas, 2 * PI * minutes / 60, 0.65, "*", GREEN)
    draw_hand(canvas, 2 * PI * hours / 12, 0.42, "#", CYAN)
    put(canvas, CENTER_X, CENTER_Y, "o", BOLD + WHITE)
    lines = []
    for row in canvas:
        line = ""
        for char, color in row:
            line += color + char + RESET if color else char
        lines.append(line)
    return lines


def big_text(text):
    rows = ["", "", ""]
    for char in text:
        for index in range(3):
            rows[index] += DIGITS[char][index] + " "
    return rows


def center(text, visible_length, width=WIDTH):
    return " " * max(0, (width - visible_length) // 2) + text


RING_SECONDS = 30
REVERSE = "\033[7m"


def new_state(now, synced=False):
    return {"now": now, "synced": synced, "alarm": None, "alarm_ring": 0, "stopwatch": 0, "stopwatch_on": False, "timer": None, "timer_ring": 0}


def advance(state, seconds=1):
    start = state["now"]
    state["now"] = (start + seconds) % 86400
    state["alarm_ring"] = max(0, state["alarm_ring"] - seconds)
    state["timer_ring"] = max(0, state["timer_ring"] - seconds)
    if state["alarm"] is not None and 0 < (state["alarm"] - start) % 86400 <= seconds:
        state["alarm_ring"] = RING_SECONDS
    if state["stopwatch_on"]:
        state["stopwatch"] += seconds
    if state["timer"] is not None:
        state["timer"] -= seconds
        if state["timer"] <= 0:
            state["timer"] = None
            state["timer_ring"] = RING_SECONDS


def status_line(label, value, color):
    return "     " + BOLD + (label + ":").ljust(12) + RESET + color + value + RESET


def status_lines(state):
    if state["synced"]:
        source = status_line("Time", "synced with your computer", GREEN)
    else:
        source = status_line("Time", "manual, may drift", DIM)
    if state["alarm"] is None:
        alarm = status_line("Alarm", "off", DIM)
    else:
        alarm = status_line("Alarm", format_seconds(state["alarm"]), YELLOW)
    if state["stopwatch_on"]:
        stopwatch = status_line("Stopwatch", format_seconds(state["stopwatch"]) + "  running", GREEN)
    else:
        stopwatch = status_line("Stopwatch", format_seconds(state["stopwatch"]) + "  stopped", DIM)
    if state["timer"] is None:
        timer = status_line("Timer", "off", DIM)
    else:
        timer = status_line("Timer", format_seconds(state["timer"]) + "  left", YELLOW)
    return [source, alarm, stopwatch, timer]


def banner(text, now):
    style = YELLOW + BOLD + (REVERSE if now % 2 == 0 else "")
    return center(style + "  " + text + "  " + RESET, len(text) + 4)


def build_screen(state):
    now = state["now"]
    lines = [center(BOLD + CYAN + "PYTHON CLOCK" + RESET, 12), ""]
    lines += draw_face(now)
    lines.append("")
    for row in big_text(format_seconds(now)):
        lines.append(center(BOLD + WHITE + row + RESET, len(row)))
    lines.append("")
    legend = CYAN + "# hour" + RESET + "   " + GREEN + "* minute" + RESET + "   " + RED + ". second" + RESET
    lines.append(center(legend, 28))
    lines.append("")
    lines += status_lines(state)
    lines.append("")
    if state["alarm_ring"] > 0:
        lines.append(banner("ALARM!  Press Ctrl+C to stop", now))
    elif state["timer_ring"] > 0:
        lines.append(banner("TIME UP!  Press Ctrl+C to stop", now))
    else:
        lines.append("")
    lines.append(center(DIM + "Press Ctrl+C to open the menu" + RESET, 29))
    return "\n".join(lines)


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
    state = new_state(86399)
    state["alarm"] = 0
    advance(state)
    assert state["now"] == 0 and state["alarm_ring"] == RING_SECONDS
    advance(state)
    assert state["alarm_ring"] == RING_SECONDS - 1
    toggle_stopwatch(state)
    advance(state)
    assert state["stopwatch"] == 1
    reset_stopwatch(state)
    advance(state)
    assert state["stopwatch"] == 0
    state["timer"] = 2
    advance(state)
    assert state["timer"] == 1 and state["timer_ring"] == 0
    advance(state)
    assert state["timer"] is None and state["timer_ring"] == RING_SECONDS
    state = new_state(100)
    state["alarm"] = 103
    state["timer"] = 3
    toggle_stopwatch(state)
    advance(state, 5)
    assert state["now"] == 105 and state["stopwatch"] == 5
    assert state["alarm_ring"] == RING_SECONDS and state["timer_ring"] == RING_SECONDS
    advance(state, 86300)
    assert state["now"] == 5 and state["alarm_ring"] == 0


LOOPS_PER_SECOND = 165000000

CLEAR = "\033[H\033[2J\033[3J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


SYNC_FILE = ".now"
POLLS_PER_SECOND = 20


def spin(loops):
    for _ in range(loops):
        pass


def read_computer_time():
    try:
        with open(SYNC_FILE) as file:
            return parse_time(file.read())[0]
    except OSError:
        return None


def wait_for_computer_time(previous, seconds):
    for _ in range(seconds * POLLS_PER_SECOND):
        spin(LOOPS_PER_SECOND // POLLS_PER_SECOND)
        now = read_computer_time()
        if now is not None and now != previous:
            return now
    return None


def elapsed_until(state, now):
    elapsed = (now - state["now"]) % 86400
    if elapsed > 43200:
        state["now"] = now
        return 0
    return elapsed


def wait_next_second(state):
    if state["synced"]:
        now = wait_for_computer_time(state["now"], 2)
        if now is not None:
            return elapsed_until(state, now)
        state["synced"] = False
    spin(LOOPS_PER_SECOND)
    return 1


def run_clock(state):
    print(HIDE_CURSOR, end="")
    try:
        while True:
            bell = "\a" if state["alarm_ring"] > 0 or state["timer_ring"] > 0 else ""
            print(CLEAR + build_screen(state) + bell, flush=True)
            advance(state, wait_next_second(state))
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR + RESET)


def menu_options(state):
    return [
        ("Set alarm" if state["alarm"] is None else "Change alarm", set_alarm),
        ("Remove alarm", remove_alarm),
        ("Stop stopwatch" if state["stopwatch_on"] else "Start stopwatch", toggle_stopwatch),
        ("Reset stopwatch", reset_stopwatch),
        ("Set timer" if state["timer"] is None else "Change timer", set_timer),
        ("Cancel timer", cancel_timer),
        ("Back to clock", None),
        ("Quit", None),
    ]


def set_alarm(state):
    state["alarm"] = ask("Alarm time (HH:MM, e.g. 07:30): ", parse_time)
    return "Alarm set to " + format_seconds(state["alarm"])


def remove_alarm(state):
    if state["alarm"] is None:
        return "There is no alarm to remove"
    state["alarm"] = None
    return "Alarm removed"


def toggle_stopwatch(state):
    state["stopwatch_on"] = not state["stopwatch_on"]
    return "Stopwatch started" if state["stopwatch_on"] else "Stopwatch stopped at " + format_seconds(state["stopwatch"])


def reset_stopwatch(state):
    state["stopwatch"] = 0
    state["stopwatch_on"] = False
    return "Stopwatch reset to 00:00:00"


def set_timer(state):
    state["timer"] = ask("Timer length (MM:SS or HH:MM:SS, e.g. 05:00): ", parse_duration)
    return "Timer set to " + format_seconds(state["timer"])


def cancel_timer(state):
    if state["timer"] is None:
        return "There is no timer to cancel"
    state["timer"] = None
    return "Timer cancelled"


def menu(state):
    state["alarm_ring"] = 0
    state["timer_ring"] = 0
    message = ""
    while True:
        options = menu_options(state)
        note = "the clock keeps running" if state["synced"] else "the clock is paused while the menu is open"
        print(CLEAR + BOLD + CYAN + "MENU" + RESET + "  " + DIM + "(" + note + ")" + RESET + "\n")
        print("\n".join(status_lines(state)) + "\n")
        for number in range(len(options)):
            print("  " + BOLD + str(number + 1) + ")" + RESET + " " + options[number][0])
        print()
        if message:
            print(GREEN + "  " + message + RESET + "\n")
        choice = input("Choose an option (1-%d): " % len(options)).strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(options):
            message = YELLOW + "Please type a number from 1 to %d" % len(options)
            continue
        label, action = options[int(choice) - 1]
        if label == "Quit":
            return False
        if label == "Back to clock" and state["synced"]:
            now = read_computer_time()
            if now is None:
                state["synced"] = False
            else:
                advance(state, elapsed_until(state, now))
                return True
        if label == "Back to clock":
            text = "Current time (HH:MM or HH:MM:SS, Enter to keep " + format_seconds(state["now"]) + "): "
            now = ask(text, parse_time, True)
            if now is not None:
                state["now"] = now
            return True
        message = action(state)


def main():
    self_test()
    print(CLEAR + BOLD + CYAN + "PYTHON CLOCK" + RESET + "\n")
    try:
        print(DIM + "Looking for your computer time..." + RESET)
        now = wait_for_computer_time(read_computer_time(), 2)
        if now is None:
            print(YELLOW + "Not found. Run ./start.sh to sync automatically." + RESET + "\n")
            state = new_state(ask("Current time (HH:MM or HH:MM:SS, e.g. 14:05): ", parse_time))
        else:
            print(GREEN + "Time synced with your computer: " + format_seconds(now) + RESET + "\n")
            state = new_state(now, True)
        state["alarm"] = ask("Alarm time (HH:MM, e.g. 07:30, or Enter for no alarm): ", parse_time, True)
        while True:
            run_clock(state)
            if not menu(state):
                break
    except (KeyboardInterrupt, EOFError):
        print()
    print(SHOW_CURSOR + RESET + "Goodbye!")


if __name__ == "__main__":
    main()
