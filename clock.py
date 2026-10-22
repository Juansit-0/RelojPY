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


class ClockFace:
    HEIGHT = 23
    CENTER_X = 22
    CENTER_Y = 11
    RADIUS_X = 20
    RADIUS_Y = 10

    def __init__(self):
        self.canvas = []

    def point(self, angle, length):
        x = self.CENTER_X + length * self.RADIUS_X * sine(angle)
        y = self.CENTER_Y - length * self.RADIUS_Y * cosine(angle)
        return int(round(x)), int(round(y))

    def put(self, x, y, char, color):
        if 0 <= y < self.HEIGHT and 0 <= x < WIDTH:
            self.canvas[y][x] = (char, color)

    def draw_hand(self, angle, length, char, color):
        steps = int(length * 40)
        for step in range(1, steps + 1):
            x, y = self.point(angle, length * step / steps)
            self.put(x, y, char, color)

    def draw_border(self):
        for step in range(240):
            x, y = self.point(2 * PI * step / 240, 1)
            self.put(x, y, ".", DIM)
        for minute in range(0, 60, 5):
            x, y = self.point(2 * PI * minute / 60, 1)
            self.put(x, y, "+", WHITE)

    def draw_numbers(self):
        for hour in range(1, 13):
            label = str(hour)
            x, y = self.point(2 * PI * hour / 12, 0.82)
            for index in range(len(label)):
                self.put(x - len(label) // 2 + index, y, label[index], BOLD + WHITE)

    def draw_hands(self, seconds_of_day):
        hours = seconds_of_day / 3600 % 12
        minutes = seconds_of_day % 3600 / 60
        seconds = seconds_of_day % 60
        self.draw_hand(2 * PI * seconds / 60, 0.7, ".", RED)
        self.draw_hand(2 * PI * minutes / 60, 0.65, "*", GREEN)
        self.draw_hand(2 * PI * hours / 12, 0.42, "#", CYAN)
        self.put(self.CENTER_X, self.CENTER_Y, "o", BOLD + WHITE)

    def render(self, seconds_of_day):
        self.canvas = [[(" ", "") for _ in range(WIDTH)] for _ in range(self.HEIGHT)]
        self.draw_border()
        self.draw_numbers()
        self.draw_hands(seconds_of_day)
        lines = []
        for row in self.canvas:
            line = ""
            for char, color in row:
                line += color + char + RESET if color else char
            lines.append(line)
        return lines


CLEAR = "\033[H\033[2J\033[3J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
REVERSE = "\033[7m"
DAY = 86400


def spin(loops):
    for _ in range(loops):
        pass


def center(text, visible_length, width=WIDTH):
    return " " * max(0, (width - visible_length) // 2) + text


class Feature:
    name = ""

    def advance(self, start, seconds):
        pass

    def status(self):
        return "", DIM


class Ringer(Feature):
    RING_SECONDS = 30
    message = ""

    def __init__(self):
        self.ring_left = 0

    def ring(self):
        self.ring_left = self.RING_SECONDS

    def silence(self):
        self.ring_left = 0

    def is_ringing(self):
        return self.ring_left > 0

    def advance(self, start, seconds):
        self.ring_left = max(0, self.ring_left - seconds)


class Alarm(Ringer):
    name = "Alarm"
    message = "ALARM!  Press Ctrl+C to stop"

    def __init__(self):
        super().__init__()
        self.time = None

    def set(self, time):
        self.time = time

    def remove(self):
        if self.time is None:
            return False
        self.time = None
        return True

    def advance(self, start, seconds):
        super().advance(start, seconds)
        if self.time is not None and 0 < (self.time - start) % DAY <= seconds:
            self.ring()

    def status(self):
        if self.time is None:
            return "off", DIM
        return format_seconds(self.time), YELLOW


class Timer(Ringer):
    name = "Timer"
    message = "TIME UP!  Press Ctrl+C to stop"

    def __init__(self):
        super().__init__()
        self.remaining = None

    def set(self, seconds):
        self.remaining = seconds

    def cancel(self):
        if self.remaining is None:
            return False
        self.remaining = None
        return True

    def advance(self, start, seconds):
        super().advance(start, seconds)
        if self.remaining is not None:
            self.remaining -= seconds
            if self.remaining <= 0:
                self.remaining = None
                self.ring()

    def status(self):
        if self.remaining is None:
            return "off", DIM
        return format_seconds(self.remaining) + "  left", YELLOW


class Stopwatch(Feature):
    name = "Stopwatch"

    def __init__(self):
        self.elapsed = 0
        self.running = False

    def toggle(self):
        self.running = not self.running
        return self.running

    def reset(self):
        self.elapsed = 0
        self.running = False

    def advance(self, start, seconds):
        if self.running:
            self.elapsed += seconds

    def status(self):
        if self.running:
            return format_seconds(self.elapsed) + "  running", GREEN
        return format_seconds(self.elapsed) + "  stopped", DIM


class TimeSource:
    synced = False
    menu_note = ""

    def status(self):
        return "", DIM

    def start_time(self):
        return 0

    def next_time(self, now):
        return None

    def after_menu(self, now):
        return now, False


class ManualTime(TimeSource):
    LOOPS_PER_SECOND = 165000000
    menu_note = "the clock is paused while the menu is open"

    def status(self):
        return "manual, may drift", DIM

    def start_time(self):
        return ask("Current time (HH:MM or HH:MM:SS, e.g. 14:05): ", parse_time)

    def next_time(self, now):
        spin(self.LOOPS_PER_SECOND)
        return (now + 1) % DAY

    def after_menu(self, now):
        text = "Current time (HH:MM or HH:MM:SS, Enter to keep " + format_seconds(now) + "): "
        typed = ask(text, parse_time, True)
        return (now if typed is None else typed), False


class SyncedTime(TimeSource):
    FILE = ".now"
    POLLS_PER_SECOND = 20
    synced = True
    menu_note = "the clock keeps running"

    def __init__(self):
        self.first = None

    def status(self):
        return "synced with your computer", GREEN

    def read(self):
        try:
            with open(self.FILE) as file:
                return parse_time(file.read())[0]
        except OSError:
            return None

    def wait_for_change(self, previous, seconds):
        for _ in range(seconds * self.POLLS_PER_SECOND):
            spin(ManualTime.LOOPS_PER_SECOND // self.POLLS_PER_SECOND)
            now = self.read()
            if now is not None and now != previous:
                return now
        return None

    def connect(self):
        self.first = self.wait_for_change(self.read(), 2)
        return self.first is not None

    def start_time(self):
        return self.first

    def next_time(self, now):
        return self.wait_for_change(now, 2)

    def after_menu(self, now):
        current = self.read()
        if current is None:
            return None, False
        return current, True


class Screen:
    def __init__(self):
        self.face = ClockFace()

    def big_text(self, text):
        rows = ["", "", ""]
        for char in text:
            for index in range(3):
                rows[index] += DIGITS[char][index] + " "
        return rows

    def status_line(self, label, value, color):
        return "     " + BOLD + (label + ":").ljust(12) + RESET + color + value + RESET

    def status_lines(self, app):
        value, color = app.source.status()
        lines = [self.status_line("Time", value, color)]
        for feature in app.features:
            value, color = feature.status()
            lines.append(self.status_line(feature.name, value, color))
        return lines

    def banner(self, text, now):
        style = YELLOW + BOLD + (REVERSE if now % 2 == 0 else "")
        return center(style + "  " + text + "  " + RESET, len(text) + 4)

    def build(self, app):
        lines = [center(BOLD + CYAN + "PYTHON CLOCK" + RESET, 12), ""]
        lines += self.face.render(app.now)
        lines.append("")
        for row in self.big_text(format_seconds(app.now)):
            lines.append(center(BOLD + WHITE + row + RESET, len(row)))
        lines.append("")
        legend = CYAN + "# hour" + RESET + "   " + GREEN + "* minute" + RESET + "   " + RED + ". second" + RESET
        lines.append(center(legend, 28))
        lines.append("")
        lines += self.status_lines(app)
        lines.append("")
        ringing = app.ringing()
        lines.append(self.banner(ringing.message, app.now) if ringing else "")
        lines.append(center(DIM + "Press Ctrl+C to open the menu" + RESET, 29))
        return "\n".join(lines)


class Menu:
    def __init__(self, app):
        self.app = app

    def options(self):
        app = self.app
        return [
            ("Set alarm" if app.alarm.time is None else "Change alarm", self.set_alarm),
            ("Remove alarm", self.remove_alarm),
            ("Stop stopwatch" if app.stopwatch.running else "Start stopwatch", self.toggle_stopwatch),
            ("Reset stopwatch", self.reset_stopwatch),
            ("Set timer" if app.timer.remaining is None else "Change timer", self.set_timer),
            ("Cancel timer", self.cancel_timer),
            ("Back to clock", None),
            ("Quit", None),
        ]

    def set_alarm(self):
        self.app.alarm.set(ask("Alarm time (HH:MM, e.g. 07:30): ", parse_time))
        return "Alarm set to " + format_seconds(self.app.alarm.time)

    def remove_alarm(self):
        return "Alarm removed" if self.app.alarm.remove() else "There is no alarm to remove"

    def toggle_stopwatch(self):
        if self.app.stopwatch.toggle():
            return "Stopwatch started"
        return "Stopwatch stopped at " + format_seconds(self.app.stopwatch.elapsed)

    def reset_stopwatch(self):
        self.app.stopwatch.reset()
        return "Stopwatch reset to 00:00:00"

    def set_timer(self):
        self.app.timer.set(ask("Timer length (MM:SS or HH:MM:SS, e.g. 05:00): ", parse_duration))
        return "Timer set to " + format_seconds(self.app.timer.remaining)

    def cancel_timer(self):
        return "Timer cancelled" if self.app.timer.cancel() else "There is no timer to cancel"

    def show(self, options, message):
        note = DIM + "(" + self.app.source.menu_note + ")" + RESET
        print(CLEAR + BOLD + CYAN + "MENU" + RESET + "  " + note + "\n")
        print("\n".join(self.app.screen.status_lines(self.app)) + "\n")
        for number in range(len(options)):
            print("  " + BOLD + str(number + 1) + ")" + RESET + " " + options[number][0])
        print()
        if message:
            print(GREEN + "  " + message + RESET + "\n")

    def run(self):
        self.app.silence()
        message = ""
        while True:
            options = self.options()
            self.show(options, message)
            choice = input("Choose an option (1-%d): " % len(options)).strip()
            if not choice.isdigit() or not 1 <= int(choice) <= len(options):
                message = YELLOW + "Please type a number from 1 to %d" % len(options)
                continue
            label, action = options[int(choice) - 1]
            if label == "Quit":
                return False
            if label == "Back to clock":
                return True
            message = action()


class ClockApp:
    def __init__(self, source, now):
        self.source = source
        self.now = now
        self.alarm = Alarm()
        self.stopwatch = Stopwatch()
        self.timer = Timer()
        self.features = [self.alarm, self.stopwatch, self.timer]
        self.screen = Screen()
        self.menu = Menu(self)

    def move_to(self, new_now, count=True):
        elapsed = (new_now - self.now) % DAY
        if count and elapsed <= DAY // 2:
            for feature in self.features:
                feature.advance(self.now, elapsed)
        self.now = new_now

    def ringing(self):
        for feature in self.features:
            if isinstance(feature, Ringer) and feature.is_ringing():
                return feature
        return None

    def silence(self):
        for feature in self.features:
            if isinstance(feature, Ringer):
                feature.silence()

    def fall_back_to_manual(self):
        self.source = ManualTime()

    def tick(self):
        new_now = self.source.next_time(self.now)
        if new_now is None:
            self.fall_back_to_manual()
            new_now = self.source.next_time(self.now)
        self.move_to(new_now)

    def run_clock(self):
        print(HIDE_CURSOR, end="")
        try:
            while True:
                bell = "\a" if self.ringing() else ""
                print(CLEAR + self.screen.build(self) + bell, flush=True)
                self.tick()
        except KeyboardInterrupt:
            pass
        finally:
            print(SHOW_CURSOR + RESET)

    def resume(self):
        new_now, count = self.source.after_menu(self.now)
        if new_now is None:
            self.fall_back_to_manual()
            new_now, count = self.source.after_menu(self.now)
        self.move_to(new_now, count)

    def run(self):
        while True:
            self.run_clock()
            if not self.menu.run():
                return
            self.resume()


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
    app = ClockApp(TimeSource(), 86399)
    app.alarm.set(0)
    app.move_to(0)
    assert app.ringing() is app.alarm and app.alarm.ring_left == Ringer.RING_SECONDS
    app.move_to(1)
    assert app.alarm.ring_left == Ringer.RING_SECONDS - 1
    app.silence()
    assert app.ringing() is None
    app.stopwatch.toggle()
    app.timer.set(3)
    app.move_to(6)
    assert app.stopwatch.elapsed == 5 and app.ringing() is app.timer and app.timer.remaining is None
    app.stopwatch.reset()
    app.move_to(5)
    assert app.now == 5 and app.stopwatch.elapsed == 0
    app.move_to(10, False)
    assert app.now == 10 and app.timer.ring_left == Ringer.RING_SECONDS


def main():
    self_test()
    print(CLEAR + BOLD + CYAN + "PYTHON CLOCK" + RESET + "\n")
    try:
        print(DIM + "Looking for your computer time..." + RESET)
        source = SyncedTime()
        if source.connect():
            print(GREEN + "Time synced with your computer: " + format_seconds(source.start_time()) + RESET + "\n")
        else:
            print(YELLOW + "Not found. See README.md to sync automatically." + RESET + "\n")
            source = ManualTime()
        ClockApp(source, source.start_time()).run()
    except (KeyboardInterrupt, EOFError):
        print()
    print(SHOW_CURSOR + RESET + "Goodbye!")


if __name__ == "__main__":
    main()
