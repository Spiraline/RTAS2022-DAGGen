import math

if __name__ == "__main__":
    from models import Node, DAG, CPC
    from dag import calculate_critical_path
else:
    from .models import Node, DAG, CPC
    from .dag import calculate_critical_path

priority = 0

def construct_cpc(dag):
    cpc = CPC()
    cpc.node_set = dag.node_set
    cpc.critical_path = dag.critical_path
    cpc.sl_node_idx = dag.sl_node_idx

    ### 0. anc, desc group
    for node in cpc.node_set:
        curr_level_node = [node.tid]
        while len(cpc.node_set[curr_level_node[0]].succ) > 0:
            next_level_node = []
            for node_idx in curr_level_node:
                for child in cpc.node_set[node_idx].succ:
                    if child not in next_level_node:
                        next_level_node.append(child)
            
            for node_idx in next_level_node:
                if node_idx not in node.desc:
                    node.desc.append(node_idx)
            curr_level_node = next_level_node
        node.desc.sort()

    for node in cpc.node_set:
        curr_level_node = [node.tid]
        while len(cpc.node_set[curr_level_node[0]].pred) > 0:
            prev_level_node = []
            for node_idx in curr_level_node:
                for parent in cpc.node_set[node_idx].pred:
                    if parent not in next_level_node:
                        prev_level_node.append(parent)
            
            for node_idx in prev_level_node:
                if node_idx not in node.anc:
                    node.anc.append(node_idx)
            curr_level_node = prev_level_node
        node.anc.sort()

    # Make concurrent_group
    for node in cpc.node_set:
        node.C = [i for i in range(len(cpc.node_set)) if i not in node.anc and i not in node.desc and i != node.tid]

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
    non_critical_node = [i for i in range(len(cpc.node_set)) if i not in dag.critical_path]

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

def assign_subDAG_priority(node_set, subdag_list):
    global priority
    subDAG = DAG()
    for node_idx in subdag_list:
        node_param = {
            "name" : "node" + str(node_idx),
            "exec_t" : node_set[node_idx].exec_t
        }
        new_node = Node(**node_param)
        subDAG.node_set.append(new_node)

        for succ_idx in node_set[node_idx].succ:
            if succ_idx in subdag_list:
                new_succ_idx = subdag_list.index(succ_idx)
                new_node.succ.append(new_succ_idx)
        
        for pred_idx in node_set[node_idx].pred:
            if pred_idx in subdag_list:
                new_pred_idx = subdag_list.index(pred_idx)
                new_node.pred.append(new_pred_idx)

    dummy_src_param = {
        "name" : "d_src",
        "exec_t" : 0.1
    }
    d_src = Node(**dummy_src_param)

    dummy_sink_param = {
        "name" : "d_sink",
        "exec_t" : 0.1
    }
    d_sink = Node(**dummy_sink_param)

    d_src_idx = len(subdag_list)
    d_sink_idx = len(subdag_list) + 1

    for (node_idx, node) in enumerate(subDAG.node_set):
        if len(node.pred) == 0:
            node.pred.append(d_src_idx)
            d_src.succ.append(node_idx)
        if len(node.succ) == 0:
            node.succ.append(d_sink_idx)
            d_sink.pred.append(node_idx)

    subDAG.node_set.append(d_src)
    subDAG.node_set.append(d_sink)

    subDAG.critical_path = calculate_critical_path(subDAG)

    subCPC = construct_cpc(subDAG)

    print(subCPC)

    if len(subCPC.provider_group) == 1:
        for node_idx in subdag_list:
            node_set[node_idx].priority = priority
        
        priority -= 1
        return
    else:
        print(subDAG.critical_path)
        for node_idx in subDAG.critical_path[1:-1]:
            node_set[node_idx].priority = priority
        priority -= 1
        for f_idx in subCPC.F:
            if len(f_idx) > 0:
                new_f = []
                for i in f_idx:
                    new_f.append(subdag_list[i])
                assign_subDAG_priority(node_set, new_f)

    return subDAG

def assign_priority(cpc):    
    ### 1. Assign max priority to critical path
    global priority
    priority = len(cpc.node_set) # p_max
    for node_idx in cpc.critical_path:
        cpc.node_set[node_idx].priority = priority
    
    priority -= 1

    ### 2. Find longest local path in F group
    for (idx, f_) in enumerate(cpc.F):

        if len(f_) != 0:
            f = f_.copy()
            assign_subDAG_priority(cpc.node_set, f)
    

