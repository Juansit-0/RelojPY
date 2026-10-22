# RelojPY

Analog clock for the terminal written in pure Python with zero imports.

## Run

```bash
./start.sh
```

`start.sh` writes the computer time to a `.now` file ten times per second using the `date` command, and the clock reads it with the built-in `open()` function. This keeps the clock exact without importing anything.

You can also run `python3 clock.py` alone. In that case you type the current time yourself.

## Features

- Analog clock drawn with characters and ANSI colors
- Digital time
- Alarm
- Stopwatch
- Timer

Press `Ctrl+C` while the clock is running to open the menu.

## Constraints

The program uses no imports at all, not even from the standard library. Without `start.sh`:

- The current time is entered by the user at startup, since Python cannot read the system clock without the `time` module.
- One second is measured with a calibrated busy loop, so the clock may drift slightly over long periods. The menu lets you resync the time.
- Time spent inside the menu is not counted, so the clock asks for the current time again when resuming.
