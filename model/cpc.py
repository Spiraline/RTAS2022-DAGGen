import math

if __name__ == "__main__":
    from models import Node, DAG, CPC
else:
    from .models import Node, DAG, CPC

def construct_cpc(dag):
    cpc = CPC()
    cpc.node_set = dag.node_set

    ### 0. anc, desc group
    for node in cpc.node_set:
        level = node.level
        curr_level_node = [node.tid]
        while level < len(dag.critical_path):
            next_level_node = []
            for node_idx in curr_level_node:
                for child in cpc.node_set[node_idx].succ:
                    if child not in next_level_node:
                        next_level_node.append(child)
            
            for node_idx in next_level_node:
                if node_idx not in node.desc:
                    node.desc.append(node_idx)
            curr_level_node = next_level_node
            level += 1
        node.desc.sort()

    for node in cpc.node_set:
        level = node.level
        curr_level_node = [node.tid]
        while level > 0:
            prev_level_node = []
            for node_idx in curr_level_node:
                for parent in cpc.node_set[node_idx].pred:
                    if parent not in next_level_node:
                        prev_level_node.append(parent)
            
            for node_idx in prev_level_node:
                if node_idx not in node.anc:
                    node.anc.append(node_idx)
            curr_level_node = prev_level_node
            level -= 1
        node.anc.sort()

    # Make concurrent_group
    for node in cpc.node_set:
        node.C = [i for i in range(dag.dict["node_num"]) if i not in node.anc and i not in node.desc and i != node.tid]

    ### 1. Make provider group
    theta = []
    for node_idx in dag.critical_path:
        if len(theta) == 0:
            theta.append(node_idx)
        elif len(cpc.node_set[node_idx].pred) == 1:
            theta.append(node_idx)
        else:
            cpc.provider_group.append(theta)
            theta = [node_idx]
    cpc.provider_group.append(theta)

    ### 2. Make F, G group
    non_critical_node = [i for i in range(dag.dict["node_num"]) if i not in dag.critical_path]

    for (idx, theta) in enumerate(cpc.provider_group):
        f = []
        g = []
        # For sink node, F, G group is empty
        if idx == len(cpc.provider_group) - 1:
            cpc.F.append(f)
            cpc.G.append(g)
        else:
            for node_idx in cpc.provider_group[idx+1]:
                f = list(set(cpc.node_set[node_idx].anc) | set(f))

            f = list(set(f) & set(non_critical_node))
            cpc.F.append(f)

            # G equation in Algorithm 1 is wrong
            # We will use union of {C(v_j) & V^{not}} for provider group theta, not F group
            for node_idx in theta:
                g = list(set(cpc.node_set[node_idx].C) & set(non_critical_node))
                g = list(set(g) - set(f))

            cpc.G.append(g)
            
            non_critical_node = list(set(non_critical_node) - set(f))

    return cpc