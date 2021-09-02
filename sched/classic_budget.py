def classic_budget(cpc, deadline, core_num):
    total_workload = sum([node.exec_t for node in cpc.node_set])
    critical_path_workload = sum([node.exec_t for node in cpc.node_set if node.tid in cpc.critical_path])
    sl_workload = cpc.node_set[cpc.sl_node_idx].exec_t

    budget = deadline - (critical_path_workload - sl_workload) - (total_workload - critical_path_workload) / core_num

    return budget