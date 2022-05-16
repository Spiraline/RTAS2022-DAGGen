# Can apply for critical path case and non-critical path case
def preemptive_classic_budget(dag, D, M):
    W_G = sum([node.exec_t for node in dag.node_set])

    L_G = dag.node_set[0].ltc + dag.node_set[0].exec_t
    L_v_s = dag.node_set[dag.sl_node_idx].ltc + dag.node_set[dag.sl_node_idx].est + dag.node_set[dag.sl_node_idx].exec_t
    delta = L_G - L_v_s
    slack = D - (W_G / M + L_G * (1 - 1/M))

    # critical node case
    if L_G == L_v_s:
        return dag.node_set[dag.sl_node_idx].exec_t + slack
    elif delta >= M * slack:
        return dag.node_set[dag.sl_node_idx].exec_t + M * slack
    else:
        return dag.node_set[dag.sl_node_idx].exec_t + delta + slack - delta / M

def ideal_maximum_budget(dag, D):
    return D - (dag.node_set[dag.sl_node_idx].ltc + dag.node_set[dag.sl_node_idx].est)