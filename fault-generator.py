import curses
import csv

class Router:
    def __init__(self, type, name, ip):
        self.type = type
        self.name = name
        self.ip = ip

    def __repr__(self):
        return f"Router(type='{self.type}', name='{self.name}', ip='{self.ip}')"

def read_csv_to_routers(filename):
    routers = []
    with open(filename, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            router = Router(row['type'], row['name'], row['ip'])
            routers.append(router)
    return routers


class Fault:
    def __init__(self, event, group, n_args, args):
        self.event = event
        self.group = group
        self.n_args = n_args
        self.args = args

    def __repr__(self):
        return f"Fault(event='{self.event}', group='{self.group}', n_args={self.n_args}, args={self.args})"

    def __str__(self):
        return self.event

    def __len__(self):
        return len(self.event)

def read_csv_to_faults(filename):
    faults = []
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)  # Skip the header row
        for row in csv_reader:
            event = row[0]
            group = row[1]
            n_args = int(row[2])
            args = row[3:3 + n_args]
            fault = Fault(event, group, n_args, args)
            faults.append(fault)
    return faults


def get_fault_groups(faults):
    return list(set(fault.group for fault in faults))

def get_faults_by_group(faults, group):
    return [str(fault) for fault in faults if fault.group == group]

def get_fault_by_event(faults, event):
    return [fault for fault in faults if fault.event == event]


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
            x = width // 2 - max_option_length // 2
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

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        stdscr.addstr(1, width // 2 - len(question) // 2, question)

        for idx, option in enumerate(options):
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

p_leaf_routers = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8']
x_leaf_routers = ['R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16']
emux_routers = ['R17', 'R18', 'R19', 'R20', 'R21', 'R22', 'R23', 'R24']
faults = ['CPU', 'Memory', 'Link', 'Power', 'Fan']

SAVED_SCENARIO_PATH = "/var/tmp/fault-generator"
OUTPUT_LOGS_PATH = "/var/tmp/fault-generator/logs"
FAULTS_CSV_PATH = "./faults.csv"
ROUTERS_CSVP_PATH = "./routers.csv"

def display_arg_setter(stdscr, fault_name, num_args):
    curses.curs_set(1)
    stdscr.clear()

    args = ["" for _ in range(num_args)]

    current_arg = 0
    error_message = ""

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Print the header
        header = "The arguments for the fault"
        stdscr.addstr(0, (width - len(header)) // 2, header)

        # Print the fault name
        fault_header = f"Fault: {fault_name}"
        stdscr.addstr(1, (width - len(fault_header)) // 2, fault_header)

        start_y = 3  # Adjusted to reduce the space
        start_x = 2  # Center the arguments list

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
            if len(args[current_arg]) < 10:  # Limit argument length
                args[current_arg] = args[current_arg] + chr(key)

        stdscr.refresh()

    stdscr.clear()

    return args

def display_creator(stdscr):
    fault_list = read_csv_to_faults(FAULTS_CSV_PATH)
    fault_groups = get_fault_groups(fault_list)

    question1 = "Select a set of P-Leaf routers by pressing space to use and press ENTER:"
    selected_p_leaf_routers = display_menu_checkboxes(stdscr, question1, p_leaf_routers)

    question2 = "Select a set of X-Leaf routers to use and press ENTER:"
    selected_x_leaf_routers = display_menu_checkboxes(stdscr, question2, x_leaf_routers)

    question3 = "Select a set of EMUX routers to use and press ENTER:"
    selected_emux_routers = display_menu_checkboxes(stdscr, question3, emux_routers)

    question4 = "Select a fault group and press ENTER:"
    selected_fault_group = display_menu_radio(stdscr, question4, fault_groups)

    specific_event_faults = get_faults_by_group(fault_list, selected_fault_group)
    select_fault = "Select a fault from {} and press ENTER:".format(selected_fault_group)
    selected_fault = display_menu_radio(stdscr, select_fault, specific_event_faults)

    selected_fault_object = get_fault_by_event(fault_list, selected_fault)[0]
    args = display_arg_setter(stdscr, selected_fault, selected_fault_object.n_args)

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
    stdscr.addstr(y_offset, 0, "Scenario will be saved to the following path: " + SAVED_SCENARIO_PATH)
    stdscr.addstr(y_offset + 2, 0, "Please enter the name of this file: ")
    stdscr.refresh()
    user_name = get_user_input(stdscr, "")

    stdscr.clear()
    stdscr.addstr(0, 0, f"Thank you, {user_name}!")
    stdscr.refresh()
    stdscr.getch()

def main(stdscr):

    menuOptions = [
        "Create a test scenario",
        "Execute an existing test scenario"
    ]

    options = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    question1 = "Choose one of the following menu items and press ENTER:"
    selected_item_radio = display_menu_radio(stdscr, question1, menuOptions)



    if selected_item_radio == "Create a test scenario":
        display_creator(stdscr)
        return

    selected_items_checkboxes = display_menu_checkboxes(stdscr, question1, options)

    question2 = "Choose from the following options (radio buttons):"


    stdscr.clear()
    stdscr.addstr(1, 0, "You selected (checkboxes):")
    for i, item in enumerate(selected_items_checkboxes):
            stdscr.addstr(2 + i, 0, f"- {item}")

    stdscr.addstr(4 + len(selected_items_checkboxes), 0, "You selected (radio button):")
    if selected_item_radio:
            stdscr.addstr(5 + len(selected_items_checkboxes), 0, f"- {selected_item_radio}")
    else:
            stdscr.addstr(5 + len(selected_items_checkboxes), 0, "- None")

    stdscr.addstr(7 + len(selected_items_checkboxes), 0, "Please enter your name:")
    stdscr.refresh()
    user_name = get_user_input(stdscr, "Name: ")

    stdscr.clear()
    stdscr.addstr(0, 0, f"Thank you, {user_name}!")
    stdscr.refresh()
    stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(main)
