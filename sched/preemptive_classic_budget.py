# Can apply for critical path case and non-critical path case
def preemptive_classic_budget(cpc, D, M):
    W_G = sum([node.exec_t for node in cpc.node_set])

    L_G = cpc.node_set[0].ltc + cpc.node_set[0].exec_t
    L_v_s = cpc.node_set[cpc.sl_node_idx].ltc + cpc.node_set[cpc.sl_node_idx].est + cpc.node_set[cpc.sl_node_idx].exec_t
    delta = L_G - L_v_s
    slack = D - (W_G / M + L_G * (1 - 1/M))

    # critical node case
    if L_G == L_v_s:
        return cpc.node_set[cpc.sl_node_idx].exec_t + slack
    else:
        return cpc.node_set[cpc.sl_node_idx].exec_t + delta + slack - delta / M