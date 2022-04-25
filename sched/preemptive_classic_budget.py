# Can apply for critical path case and non-critical path case
def preemptive_classic_budget(cpc, deadline, core_num):
    total_workload = sum([node.exec_t for node in cpc.node_set])

    L_G = cpc.node_set[0].ltc + cpc.node_set[0].exec_t
    print(L_G)
    print(cpc.node_set[cpc.sl_node_idx].ltc, cpc.node_set[cpc.sl_node_idx].est)

    return 0