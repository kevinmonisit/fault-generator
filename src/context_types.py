import os
import csv
from .helpers import *

class Context:
  def __init__(self, FAULTS_CSV_PATH, ROUTERS_CSV_PATH, TEST_CASES_PATH, EXECUTION_PATH, LOGS_PATH):
    self.FAULTS_CSV_PATH = FAULTS_CSV_PATH
    self.ROUTERS_CSV_PATH = ROUTERS_CSV_PATH
    self.TEST_CASES_PATH = TEST_CASES_PATH
    self.EXECUTION_PATH = EXECUTION_PATH
    self.LOGS_PATH = LOGS_PATH

    if not os.path.exists(self.FAULTS_CSV_PATH):
        raise FileNotFoundError(f"File not found: {self.FAULTS_CSV_PATH}")
    if not os.path.exists(self.ROUTERS_CSV_PATH):
        raise FileNotFoundError(f"File not found: {self.ROUTERS_CSV_PATH}")

    self.fault_list = Context.parse_csv_to_faults(self.FAULTS_CSV_PATH)
    self.fault_groups = get_fault_groups(self.fault_list)
    p_leaf_routers, x_leaf_routers, emux_routers = Context.parse_csv_to_routers(self.ROUTERS_CSV_PATH)

    self.p_leaf_routers = p_leaf_routers
    self.x_leaf_routers = x_leaf_routers
    self.emux_routers = emux_routers

  def get_all_routers(self):
    return self.p_leaf_routers + self.x_leaf_routers + self.emux_routers

  @staticmethod
  def parse_csv_to_routers(file_path):
    p_leaf_routers = []
    x_leaf_routers = []
    emux_routers = []

    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            type, name, ip = row
            router = Router(type, name, ip)
            if type == 'P-LEAF':
                p_leaf_routers.append(router)
            elif type == 'X-LEAF':
                x_leaf_routers.append(router)
            elif type == 'EMUX':
                emux_routers.append(router)
            else:
                print(f"Unknown router type: {type}")

    return p_leaf_routers, x_leaf_routers, emux_routers

  @staticmethod
  def parse_csv_to_faults(filename):
    faults = []
    with open(filename, mode='r') as file:
        csv_reader = csv.reader(file)
        headers = next(csv_reader)
        for row in csv_reader:
            event = row[0]
            command_prefix = row[1]
            router_type = row[2]
            group = row[3]
            n_args = int(row[4])
            args = row[4:4 + n_args]
            fault = Fault(event, command_prefix, router_type, group, n_args, args)
            faults.append(fault)

    return faults

class Router:
    def __init__(self, type, name, ip):
        self.type = type
        self.name = name
        self.ip = ip

    def __repr__(self):
        return self.__str__()

    def __len__(self):
        return len(self.name)

    def __str__(self):
        return f"{self.ip} - {self.name}"

class Fault:

    # Command Prefix is the command string before the arguments
    def __init__(self, event, command_prefix, router_type, group, n_args, args):
        self.router_type = router_type
        self.event = event
        self.command_prefix = command_prefix
        self.group = group
        self.n_args = n_args
        self.args = args

    def __repr__(self):
        return f"Fault(event='{self.event}', router_type='{self.router_type} \
            group='{self.group}', n_args={self.n_args}, args={self.args})"

    def __str__(self):
        return self.event

    def __len__(self):
        return len(self.event)

class Action:
    def __init__(self, fault: Fault, routers: list[Router]):
        self.fault = fault
        self.routers = routers

    def to_csv(self):
        csv = ""

        for router in self.routers:
            csv += f"{router.ip},"
            csv += f"\"{self.fault.command_prefix} "
            for i, arg in enumerate(self.fault.args):
                csv += f"arg{i + 1} {arg} "
            csv += "\"\n"

        return csv

    @staticmethod
    def from_csv(filepath):
        with open(filepath, mode='r') as file:
            csv_reader = csv.reader(file)
            routers = []
            for row in csv_reader:
                ip, action = row
                routers.append(Router(ip, action))
        return routers