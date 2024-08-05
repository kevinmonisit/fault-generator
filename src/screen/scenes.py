import curses
from ..context_types import Action
import os
from .helpers import *
from ..helpers import *

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

def display_error_message(stdscr, message):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)

    stdscr.clear()
    stdscr.attron(curses.color_pair(1))
    stdscr.addstr(0, 0, message)
    stdscr.attroff(curses.color_pair(1))
    stdscr.refresh()
    stdscr.getch()

def display_creator(stdscr, context):
    router_types = ["P-LEAF", "X-LEAF", "EMUX"]

    # 1. ASK the user for ROUTER TYPE
    question = "Select a router type to use and press ENTER:"
    selected_router_type = display_menu_radio(stdscr, question, router_types)

    # 2. ASK the user to select ROUTERS of the selected ROUTER TYPE
    question = f"Select a set of {selected_router_type} routers to use and press ENTER:"
    filtered_routers = get_routers_of_type(context.get_all_routers(), selected_router_type)

    if len(filtered_routers) == 0:
        display_error_message(stdscr, "No routers found for the selected type. Press ENTER to continue.")
        return

    selected_routers = display_menu_checkboxes(stdscr, question, filtered_routers)

    # 3. ASK the user to select a FAULT GROUP of the selected ROUTER TYPE
    faults_of_router_type = get_faults_by_router_type(context.fault_list, selected_router_type)
    question = f"Select a fault group of {selected_router_type} routers and press ENTER:"
    fault_groups_of_router_type = get_fault_groups(faults_of_router_type)

    if len(fault_groups_of_router_type) == 0:
        display_error_message(stdscr, "No fault groups found for the selected router type. Press ENTER to continue.")
        return

    selected_fault_group = display_menu_radio(stdscr, question, fault_groups_of_router_type[:10])

    # 4. ASK the user to select a FAULT from the selected FAULT GROUP
    question = f"Select a fault from {selected_fault_group} and press ENTER:"
    specific_event_faults = get_faults_by_group(faults_of_router_type, selected_fault_group)

    if len(specific_event_faults) == 0:
        display_error_message(stdscr, "No faults found for the selected group. Press ENTER to continue.")
        return

    selected_fault = display_menu_radio(stdscr, question, specific_event_faults)

    # 5. ASK the user to set the ARGUMENTS for the selected FAULT
    selected_fault_object = get_fault_by_event(faults_of_router_type, selected_fault)[0]
    args = display_arg_setter(stdscr, selected_fault, selected_fault_object.n_args)
    selected_fault_object.args = args

    # 6. ASK the user to enter a FILENAME to save the scenario
    stdscr.clear()
    stdscr.addstr(0, 0, f"You selected the following {selected_router_type} routers:")
    for i, item in enumerate(selected_routers):
        stdscr.addstr(1 + i, 0, f"- {item}")

    y_offset = 3 + len(selected_routers)
    stdscr.addstr(y_offset, 0, f"You selected the following fault: {selected_fault}")
    y_offset += 1
    for i, arg in enumerate(args):
        stdscr.addstr(y_offset + i, 0, f"- arg{i + 1}: {arg}")

    y_offset += 3 + len(args)
    stdscr.addstr(y_offset, 0, "Scenario will be saved to the following path: " + context.TEST_CASES_PATH)
    stdscr.addstr(y_offset + 2, 0, "Please enter the name of this file: ")
    file_name = get_user_input(stdscr, " ")

    # check if user inputted name, if create an error and ask again
    while file_name == "":
        display_error_message(stdscr, "Error! Please enter a valid nonempty name. Press ENTER to continue.")
        file_name = get_user_input(stdscr, " ")
        if file_name != "":
            break

    stdscr.refresh()
    action = Action(selected_fault_object, selected_routers)
    csv = action.to_csv()
    # create a path with saved scenario path and filename
    path = os.path.join(context.TEST_CASES_PATH, file_name + ".csv")

    with open(path, mode='w') as file:
        file.write(csv)

    stdscr.clear()
    stdscr.addstr(0, 0, f"Success! File written to {context.TEST_CASES_PATH}. Press ENTER to continue.")
    stdscr.refresh()
    stdscr.getch()


def display_scenarios(stdscr, context):
    scenario_names = os.listdir(context.TEST_CASES_PATH)
    scenario_names.append("Back")

    question = "Select a scenario to execute and press ENTER:"
    selected_scenario = display_menu_radio(stdscr, question, scenario_names)

    if selected_scenario == "Back":
        return

    if selected_scenario is not None:

        import subprocess
        file_path = os.path.join(context.TEST_CASES_PATH, selected_scenario)

        options = ['Continue', 'Back']
        selected_option = display_menu_radio(stdscr, f"Execute scenario {selected_scenario} in {file_path}?", options)

        if selected_option == 'Back':
            return

        subprocess.run([context.EXECUTION_PATH, file_path])

        stdscr.clear()
        stdscr.addstr(0, 0, f"Executing scenario {selected_scenario}. Press ENTER to continue.")
        stdscr.refresh()
