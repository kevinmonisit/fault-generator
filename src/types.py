import os
import csv
from .helpers import *

class Context:
  def __init__(self, FAULTS_CSV_PATH, ROUTERS_CSV_PATH, TEST_CASES_PATH):
    self.FAULTS_CSV_PATH = FAULTS_CSV_PATH
    self.ROUTERS_CSV_PATH = ROUTERS_CSV_PATH
    self.TEST_CASES_PATH = TEST_CASES_PATH

    if not os.path.exists(self.FAULTS_CSV_PATH):
        raise FileNotFoundError(f"File not found: {self.FAULTS_CSV_PATH}")
    if not os.path.exists(self.ROUTERS_CSV_PATH):
        raise FileNotFoundError(f"File not found: {self.ROUTERS_CSV_PATH}")

    self.fault_list = Context.read_csv_to_faults(self.FAULTS_CSV_PATH)
    self.fault_groups = get_fault_groups(self.fault_list)
    p_leaf_routers, x_leaf_routers, emux_routers = Context.parse_csv_to_routers(self.ROUTERS_CSV_PATH)

    self.p_leaf_routers = p_leaf_routers
    self.x_leaf_routers = x_leaf_routers
    self.emux_routers = emux_routers

  @staticmethod
  def parse_csv_to_routers(file_path):
    p_leaf_routers = []
    x_leaf_routers = []
    emux_routers = []

    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
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

class Action:
    def __init__(self, fault: Fault, routers: list[Router]):
        self.fault = fault
        self.routers = routers

    def to_csv(self):
        csv = ""

        for router in self.routers:
            csv += f"{router.ip},"
            csv += f"{self.fault.event} "
            for i, arg in enumerate(self.fault.args):
                csv += f"arg{i + 1} {arg} "
            csv += "\n"

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