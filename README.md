# RelojPY

Analog clock for the terminal written in pure Python with zero imports.

## Run

```bash
python3 clock.py
```

You type the current time yourself and the clock keeps it.

### Run synced with your computer time

From this folder, paste this line in the terminal:

```bash
(while true; do date +%H:%M:%S > .now.tmp && mv .now.tmp .now; sleep 0.1; done) & python3 clock.py; kill $!; rm -f .now .now.tmp
```

It writes the computer time to a `.now` file ten times per second, and the clock reads it with the built-in `open()` function. The clock is then exact, and it keeps running while the menu is open.

## Features

- Analog clock drawn with characters and ANSI colors
- Digital time
- Alarm
- Stopwatch
- Timer

Press `Ctrl+C` while the clock is running to open the menu.

## Constraints

The program uses no imports at all, not even from the standard library. When it is not synced:

- The current time is entered by the user at startup, since Python cannot read the system clock without the `time` module.
- One second is measured with a calibrated busy loop, so the clock may drift slightly over long periods. The menu lets you resync the time.
- Time spent inside the menu is not counted, so the clock asks for the current time again when resuming.
