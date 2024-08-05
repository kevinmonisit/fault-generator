
def get_fault_groups(faults):
    return list(set(fault.group for fault in faults))

def get_faults_by_group(faults, group):
    return [str(fault) for fault in faults if fault.group == group]

def get_fault_by_event(faults, event):
    return [fault for fault in faults if fault.event == event]

def get_faults_by_router_type(faults, router_type):
    return [fault for fault in faults if fault.router_type == router_type]

def get_routers_of_type(routers, router_type):
    return [router for router in routers if router.type == router_type]