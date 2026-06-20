import curses
import asyncio
from httpx_ws import aconnect_ws
from pycrdt import Doc, Text
from pycrdt import Provider
from pycrdt.websocket.websocket import HttpxWebsocket


async def app(stdscr: curses.window, ydoc: Doc):
    buffer = ydoc.get("text", type=Text)
    y, x = 0, 0
    loop = asyncio.get_event_loop()

    def lines() -> list[str]:
        return str(buffer).split("\n")

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
        stdscr.refresh()

        key = await loop.run_in_executor(None, stdscr.getch)
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
                buffer.delete(offset - 1, 1)
                if x > 0:
                    x -= 1
                else:
                    y -= 1
                    x = len(lines()[y])
        elif key in (curses.KEY_ENTER, 10, 13):
            offset = cursor_to_offset()
            buffer.insert(offset, "\n")
            y += 1
            x = 0
        elif 32 <= key <= 126:
            offset = cursor_to_offset()
            buffer.insert(offset, chr(key))
            x += 1


async def client():
    ydoc = Doc()
    room_name = "my-roomname"

    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    try:
        async with (
            aconnect_ws(f"http://localhost:1234/{room_name}") as websocket,
            Provider(ydoc, HttpxWebsocket(websocket, room_name)),
        ):
            await app(stdscr, ydoc)
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.endwin()


if __name__ == "__main__":
    asyncio.run(client())