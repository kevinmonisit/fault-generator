import curses
import os

def display_menu_checkboxes(stdscr, question, options):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    selected_indices = set()
    current_index = 0
    max_option_length = max(len(option) for option in options) + 4
    starting_y = 6

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(1, width // 2 - len(question) // 2, question)

        for idx, option in enumerate(options):
            option = str(option)
            x = width // 3 - max_option_length // 2
            y = starting_y - len(options) // 2 + idx + 2
            if idx == current_index:
                stdscr.attron(curses.color_pair(1))
            if idx in selected_indices:
                stdscr.addstr(y, x, "[x] " + option)
            else:
                stdscr.addstr(y, x, "[ ] " + option)
            if idx == current_index:
                stdscr.attroff(curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(options) - 1:
            current_index += 1
        elif key == ord(' '):
            if current_index in selected_indices:
                selected_indices.remove(current_index)
            else:
                selected_indices.add(current_index)
        elif key == ord('\n'):
            break

    return [options[i] for i in selected_indices]

def display_menu_radio(stdscr, question, options):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    selected_index = None
    current_index = 0
    max_option_length = max(len(option) for option in options) + 4

    starting_y = 6
    starting_x = 2

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(1, width // 2 - len(question) // 2, question)

        for idx, option in enumerate(options):
            option = str(option)
            x = width // 2 - max_option_length // 2
            y = starting_y - len(options) // 2 + idx + 2
            if idx == current_index:
                stdscr.attron(curses.color_pair(1))
            if idx == selected_index:
                stdscr.addstr(y, x, "(x) " + option)
            else:
                stdscr.addstr(y, x, "( ) " + option)
            if idx == current_index:
                stdscr.attroff(curses.color_pair(1))

        stdscr.refresh()

        key = stdscr.getch()

        if key == curses.KEY_UP and current_index > 0:
            current_index -= 1
        elif key == curses.KEY_DOWN and current_index < len(options) - 1:
            current_index += 1
        elif key == ord(' '):
            selected_index = current_index
        elif key == ord('\n') and selected_index is not None:
            break

    return options[selected_index] if selected_index is not None else None

def get_user_input(stdscr, prompt):
    curses.echo()
    stdscr.addstr(prompt)
    stdscr.refresh()
    user_input = stdscr.getstr().decode('utf-8')
    curses.noecho()
    return user_input


def load_config_file(config_path):
    with open(config_path) as file_obj:
        lines = file_obj.read().splitlines()

    config_vars = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", maxsplit=1)
        config_vars.setdefault(key.strip(), value.strip())

    return config_vars