import curses
from curses import wrapper

def main(stdscr: curses.window):
    stdscr.keypad(True)
    curses.noecho()

    buffer = ""
    y, x = 0, 0

    def lines() -> list[str]:
        return buffer.split("\n")

    def cursor_to_offset() -> int:
        ls = lines()
        return sum(len(ls[i]) + 1 for i in range(y)) + x

    while True:
        max_y, max_x = stdscr.getmaxyx()
        stdscr.clear()

        ls = lines()
        for i, line in enumerate(ls):
            if i < max_y:
                stdscr.addstr(i, 0, line[:max_x])

        stdscr.move(y, x)

        key = stdscr.getch()
        ls = lines()

        if key == curses.KEY_UP:
            y = max(0, y - 1)
            x = min(x, len(lines()[y]))
        elif key == curses.KEY_DOWN:
            y = min(len(ls) - 1, y + 1)
            x = min(x, len(lines()[y]))
        elif key == curses.KEY_LEFT:
            if x > 0:
                x -= 1
            elif y > 0:
                y -= 1
                x = len(lines()[y])
        elif key == curses.KEY_RIGHT:
            if x < len(ls[y]):
                x += 1
            elif y < len(ls) - 1:
                y += 1
                x = 0
        elif key in (curses.KEY_BACKSPACE, 127):
            offset = cursor_to_offset()
            if offset > 0:
                buffer = buffer[: offset - 1] + buffer[offset:]
                if x > 0:
                    x -= 1
                else:
                    y -= 1
                    x = len(lines()[y])
        elif key in (curses.KEY_ENTER, 10, 13):
            offset = cursor_to_offset()
            buffer = buffer[:offset] + "\n" + buffer[offset:]
            y += 1
            x = 0
        elif 32 <= key <= 126:
            offset = cursor_to_offset()
            buffer = buffer[:offset] + chr(key) + buffer[offset:]
            x += 1


if __name__ == "__main__":
    wrapper(main)