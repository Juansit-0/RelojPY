# RelojPY

Analog clock for the terminal written in pure Python with zero imports.

## Run

```bash
python3 clock.py
```

## Features

- Analog clock drawn with characters and ANSI colors
- Digital time
- Alarm
- Stopwatch
- Timer

Press `Ctrl+C` while the clock is running to open the menu.

## Constraints

The program uses no imports at all, not even from the standard library. Because of that:

- The current time is entered by the user at startup, since Python cannot read the system clock without the `time` module.
- One second is measured with a calibrated busy loop, so the clock may drift slightly over long periods. The menu lets you resync the time.
- Time spent inside the menu is not counted, so the clock asks for the current time again when resuming.
