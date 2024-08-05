import curses
from src.types import Action
import os
from .helpers import *
from ..helpers import get_faults_by_group, get_fault_by_event

def main_scene(stdscr, context):
    menuOptions = [
        "Create a test scenario",
        "Execute an existing test scenario",
        "Exit",
    ]

    while True:
        question1 = "Choose one of the following menu items and press ENTER:"
        selected_item_radio = display_menu_radio(stdscr, question1, menuOptions)

        if selected_item_radio == "Create a test scenario":
            display_creator(stdscr, context)
        elif selected_item_radio == "Execute an existing test scenario":
            display_scenarios(stdscr, context)
        elif selected_item_radio == "Exit":
            break

def display_arg_setter(stdscr, fault_name, num_args):
    curses.curs_set(1)
    stdscr.clear()

    args = ["" for _ in range(num_args)]

    current_arg = 0
    error_message = ""

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        header = "The arguments for the fault"
        stdscr.addstr(0, (width - len(header)) // 2, header)

        fault_header = f"Fault: {fault_name}"
        stdscr.addstr(1, (width - len(fault_header)) // 2, fault_header)

        start_y = 3
        start_x = 2

        for idx in range(num_args):
            x = start_x
            y = start_y + idx
            stdscr.addstr(y, x, f"arg{idx + 1}:")

            arg_pos = x + len(f"arg{idx + 1}:") + 1
            if arg_pos < width - 8:  # Ensure we do not go beyond the window width
                if idx == current_arg:
                    stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, arg_pos, f"{args[idx]:<10}")
                stdscr.attroff(curses.A_REVERSE)

        stdscr.addstr(start_y + num_args + 1, start_x, "Press Enter to submit, or use up/down keys to navigate.")

        if error_message:
            stdscr.addstr(start_y + num_args + 2, start_x, error_message, curses.color_pair(1))

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            current_arg = (current_arg + 1) % num_args
        elif key == curses.KEY_UP:
            current_arg = (current_arg - 1) % num_args
        elif key == curses.KEY_ENTER or key in [10, 13]:
            if all(args):
                break
            else:
                error_message = "Please fill out all the argument fields"
                curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        elif key == curses.KEY_BACKSPACE or key == 127:  # Handle Backspace key
            if args[current_arg]:
                args[current_arg] = args[current_arg][:-1]
        elif 32 <= key <= 126:  # Printable ASCII range
            if len(args[current_arg]) < 10:
                args[current_arg] = args[current_arg] + chr(key)

        stdscr.refresh()

    stdscr.clear()

    return args

def display_creator(stdscr, context):
    question1 = "Select a set of P-Leaf routers by pressing space to use and press ENTER:"
    selected_p_leaf_routers = display_menu_checkboxes(stdscr, question1, context.p_leaf_routers)

    question2 = "Select a set of X-Leaf routers to use and press ENTER:"
    selected_x_leaf_routers = display_menu_checkboxes(stdscr, question2, context.x_leaf_routers)

    question3 = "Select a set of EMUX routers to use and press ENTER:"
    selected_emux_routers = display_menu_checkboxes(stdscr, question3, context.emux_routers)

    question4 = "Select a fault group and press ENTER:"
    selected_fault_group = display_menu_radio(stdscr, question4, context.fault_groups)

    specific_event_faults = get_faults_by_group(context.fault_list, selected_fault_group)
    select_fault = "Select a fault from {} and press ENTER:".format(selected_fault_group)
    selected_fault = display_menu_radio(stdscr, select_fault, specific_event_faults)

    selected_fault_object = get_fault_by_event(context.fault_list, selected_fault)[0]
    args = display_arg_setter(stdscr, selected_fault, selected_fault_object.n_args)

    selected_fault_object.args = args

    stdscr.clear()
    stdscr.addstr(1, 0, "You selected the following P-Leaf routers:")
    if len(selected_p_leaf_routers) == 0:
        stdscr.addstr(y_offset + 1, 0, "- No P-leaf routers selected")
    for i, item in enumerate(selected_p_leaf_routers):
        stdscr.addstr(2 + i, 0, f"- {item}")

    y_offset = 4 + len(selected_p_leaf_routers)
    stdscr.addstr(y_offset, 0, "You selected the following X-Leaf routers:")
    if len(selected_x_leaf_routers) == 0:
        stdscr.addstr(y_offset + 1, 0, "- No X-leaf routers selected")
    for i, item in enumerate(selected_x_leaf_routers):
        stdscr.addstr(y_offset + 1 + i, 0, f"- {item}")

    y_offset += 3 + len(selected_x_leaf_routers)
    stdscr.addstr(y_offset, 0, "You selected the following EMUX routers:")

    if len(selected_emux_routers) == 0:
        stdscr.addstr(y_offset + 1, 0, "- No EMUX routers selected")

    for i, item in enumerate(selected_emux_routers):
        stdscr.addstr(y_offset + 1 + i, 0, f"- {item}")

    y_offset += 3 + len(selected_emux_routers)
    stdscr.addstr(y_offset, 0, "You selected the following fault:")
    stdscr.addstr(y_offset + 1, 0, f"- {selected_fault}")

    for i, arg in enumerate(args):
        stdscr.addstr(y_offset + 2 + i, 0, f"- arg{i + 1}: {arg}")

    y_offset += 3 + len(args)
    stdscr.addstr(y_offset, 0, "Scenario will be saved to the following path: " + context.TEST_CASES_PATH)
    stdscr.addstr(y_offset + 2, 0, "Please enter the name of this file: ")
    file_name = get_user_input(stdscr, " ")

    # check if user inputted name, if create an error and ask again
    while file_name == "":
        stdscr.refresh()
        stdscr.addstr(y_offset + 3, 0, "Error! Please enter a valid nonempty name:  ")
        file_name = get_user_input(stdscr, " ")
        if file_name != "":
            break

    stdscr.refresh()
    action = Action(selected_fault_object, selected_p_leaf_routers + selected_x_leaf_routers + selected_emux_routers)
    csv = action.to_csv()
    # create a path with saved scenario path and filename
    path = os.path.join(context.TEST_CASES_PATH, file_name + ".csv")

    with open(path, mode='w') as file:
        file.write(csv)

    stdscr.clear()
    stdscr.addstr(0, 0, f"Success! File written to {context.TEST_CASES_PATH}. Press ENTER to conintue.")
    stdscr.refresh()
    stdscr.getch()

def display_scenarios(stdscr, context):
    print("path: \n\n\n", context.TEST_CASES_PATH)
    scenario_names = os.listdir(context.TEST_CASES_PATH)
    scenario_names.append("Back")

    question = "Select a scenario to execute and press ENTER:"
    selected_scenario = display_menu_radio(stdscr, question, scenario_names)

    if selected_scenario == "Back":
        return

    if selected_scenario is not None:
        file_path = os.path.join(context.TEST_CASES_PATH, selected_scenario + ".csv")
        routers = Action.from_csv(file_path)

        stdscr.clear()
        stdscr.addstr(0, 0, f"Executing scenario {selected_scenario}. Press ENTER to continue.")
        stdscr.refresh()

