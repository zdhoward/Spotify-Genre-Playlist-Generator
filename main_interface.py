#!/usr/bin/env python3
import curses
from main import run
from manage import manage


def draw_menu(stdscr):
    response = True
    mode = "main"
    while response:
        if mode == "main":
            stdscr.clear()

            stdscr.addstr(0, 0, "=== SPOTIFY PLAYLIST GENERATOR ===")
            stdscr.addstr(1, 0, "=====       MAIN  MENU       =====")

            stdscr.addstr(2, 2, "[q] = quit")
            stdscr.addstr(3, 2, "[g] = generate playlists")
            stdscr.addstr(4, 2, "[m] = manage categorization")
            stdscr.addstr(5, 2, "[d] = display")

            msg = "Press a key to select an option:"
            if str(response) != "True":
                msg = response

            stdscr.addstr(7, 0, "> " + msg)

            c = stdscr.getch()

            response = process_menu_input(c)

            if response == "GENERATE_PLAYLIST":
                mode = "generate"
                response = True
            elif response == "MANAGE_CATEGORIES":
                mode = "manage"
                response = True
            elif response == "DISPLAY_DATA":
                mode = "display"
                response = True

        elif mode == "display":
            stdscr.clear()

            stdscr.addstr(0, 0, "=== SPOTIFY PLAYLIST GENERATOR ===")
            stdscr.addstr(1, 0, "=====      DISPLAY DATA      =====")

            stdscr.addstr(2, 2, "[q] = quit")
            stdscr.addstr(3, 2, "[t] = display tracks")
            stdscr.addstr(4, 2, "[a] = display analysis")
            stdscr.addstr(5, 2, "[d] = display definitions")

            msg = "Press a key to select an option:"
            if str(response) != "True":
                msg = response

            stdscr.addstr(7, 0, "> " + msg)

            c = stdscr.getch()

            response = process_display_input(c)

            if response == "DISPLAY_DATA_TRACKS":
                pass
            elif response == "DISPLAY_DATA_ANALYSIS":
                pass
            elif response == "DISPLAY_DATA_DEFINITIONS":
                pass
        elif mode == "generate":
            stdscr.clear()
            stop_curses()
            run()
            mode = "main"
        elif mode == "manage":
            stdscr.clear()
            stop_curses()
            manage()
            mode = "main"

        else:
            break


def process_menu_input(_char):
    if _char == ord("g"):
        msg = "GENERATE_PLAYLIST"
    elif _char == ord("m"):
        msg = "MANAGE_CATEGORIES"
    elif _char == ord("d"):
        msg = "DISPLAY_DATA"
    elif _char == ord("q"):
        msg = False
    else:
        msg = "This program doesn't know that key, try again!"
    return msg


def process_display_input(_char):
    if _char == ord("t"):
        msg = "DISPLAY_DATA_TRACKS"
    elif _char == ord("a"):
        msg = "DISPLAY_DATA_ANALYSIS"
    elif _char == ord("d"):
        msg = "DISPLAY_DATA_DEFINITIONS"
    elif _char == ord("q"):
        msg = False
    else:
        msg = "This program doesn't know that key, try again!"
    return msg


def main():
    curses.wrapper(draw_menu)


def stop_curses():
    # curses.nocbreak()
    # curses.echo()
    curses.endwin()
    pass


if __name__ == "__main__":
    main()
