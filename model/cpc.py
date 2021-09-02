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
        desc_candidate = node.succ.copy()
        while len(desc_candidate) > 0:
            node_idx = desc_candidate.pop()
            node.desc.append(node_idx)
            for child in cpc.node_set[node_idx].succ:
                if child not in node.desc and child not in desc_candidate:
                    desc_candidate.append(child)
        node.desc.sort()

    for node in cpc.node_set:
        anc_candidate = node.pred.copy()
        while len(anc_candidate) > 0:
            node_idx = anc_candidate.pop()
            node.anc.append(node_idx)
            for parent in cpc.node_set[node_idx].pred:
                if parent not in node.anc and parent not in anc_candidate:
                    anc_candidate.append(parent)
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

    if len(subCPC.provider_group) == 1:
        for node_idx in subdag_list:
            node_set[node_idx].priority = priority
        
        priority -= 1
        return
    else:
        for idx in subDAG.critical_path[1:-1]:
            node_set[subdag_list[idx]].priority = priority
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
    
### Calculate I group
def calculate_I(cpc):
    ready_queue = []
    is_complete = [False, ] * len(cpc.node_set)

    for node in cpc.node_set:
        if len(node.pred) == 0:
            ready_queue.append(node)

    # Calculate inference group
    non_critical_node = [i for i in range(len(cpc.node_set)) if i not in cpc.critical_path]

    while False in is_complete:
        node = ready_queue.pop()

        I_list = list(set(node.C) & set(non_critical_node))
        for anc_idx in node.anc:
            I_list = list(set(I_list) - set(cpc.node_set[anc_idx].I))

        node.I = I_list
        
        is_complete[node.tid] = True
        succ_node_list = node.succ

        for succ_idx in succ_node_list:
            isReady = True
            for pred_idx in cpc.node_set[succ_idx].pred:
                if not is_complete[pred_idx]:
                    isReady = False
        
            if isReady:
                ready_queue.append(cpc.node_set[succ_idx])

def get_path_num(node_set, subdag_list):
    subDAG = DAG()
    all_path = []
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

    tmp_path = []

    for node in subDAG.node_set:
        if len(node.pred) == 0:
            tmp_path.append([node.tid])

    while len(tmp_path) > 0:
        path = tmp_path.pop()

        if len(subDAG.node_set[path[-1]].succ) == 0:
            all_path.append(path)
        else:
            for succ_idx in subDAG.node_set[path[-1]].succ:
                tmp_path.append(path + [succ_idx])

    return len(all_path)

def calculate_finish_time_bound(cpc, core_num):
    ready_queue = []
    is_complete = [False, ] * len(cpc.node_set)

    for node in cpc.node_set:
        if len(node.pred) == 0:
            ready_queue.append(node)
    
    while False in is_complete:
        node = ready_queue.pop()

        if len(node.pred) == 0:
            max_pred = 0
        else:
            max_pred = max([cpc.node_set[node_idx].f_t for node_idx in node.pred])

        C_minus_critical = list(set(node.C) - set(cpc.critical_path))
        inf_path_num = get_path_num(cpc.node_set, C_minus_critical)

        if node.tid in cpc.critical_path:
            inf = 0
        elif inf_path_num < core_num - 1:
            inf = 0
        else:
            inf = math.ceil(sum([cpc.node_set[node_idx].exec_t for node_idx in node.I_e]) / (core_num - 1))

        node.f_t = node.exec_t + max_pred + inf
        
        # Handle complete node
        is_complete[node.tid] = True
        succ_node_list = node.succ

        for succ_idx in succ_node_list:
            isReady = True
            for pred_idx in cpc.node_set[succ_idx].pred:
                if not is_complete[pred_idx]:
                    isReady = False
        
            if isReady:
                ready_queue.append(cpc.node_set[succ_idx])

def calculate_node_I_e(cpc, core_num):
    for node in cpc.node_set:
        high_p_list = [i for i in node.I if cpc.node_set[i].priority > node.priority]
        low_p_list = [i for i in node.I if cpc.node_set[i].priority < node.priority]

        low_p_list = sorted(low_p_list, key = lambda idx : cpc.node_set[idx].exec_t * (-1))

        if len(low_p_list) > core_num - 1:
            low_p_list = low_p_list[:core_num-1]

        node.I_e = high_p_list + low_p_list

def calculate_beta_and_lambda_v_e(cpc):
    cpc.beta = []
    cpc.lambda_v_e = []
    for (idx, f_group) in enumerate(cpc.F):
        f_theta = cpc.node_set[cpc.provider_group[idx][-1]].f_t
        if len(f_group) == 0:
            cpc.lambda_v_e.append([])
            cpc.beta.append(0)
            continue
        
        # calculate lambda_v_e
        v_e_idx = f_group[0]
        for node_idx in f_group[1:]:
            if cpc.node_set[node_idx].f_t > cpc.node_set[v_e_idx].f_t:
                v_e_idx = node_idx

        lambda_v_e = [v_e_idx]

        while len(cpc.node_set[v_e_idx].pred) > 0:
            v_j_idx = -1
            for pred_idx in cpc.node_set[v_e_idx].pred:
                if pred_idx in f_group and cpc.node_set[pred_idx].f_t > f_theta and cpc.node_set[pred_idx].f_t > cpc.node_set[v_j_idx].f_t:
                    v_j_idx = pred_idx

            if v_j_idx == -1:
                break
            else:
                lambda_v_e.append(v_j_idx)
                v_e_idx = v_j_idx

        lambda_v_e.reverse()
        cpc.lambda_v_e.append(lambda_v_e)

        # calculate beta
        beta = 0
        for v_idx in lambda_v_e:
            if cpc.node_set[v_idx].f_t - cpc.node_set[v_idx].exec_t >= f_theta:
                beta += cpc.node_set[v_idx].exec_t
            else:
                beta += cpc.node_set[v_idx].f_t - f_theta
        
        cpc.beta.append(beta)

def calculate_R_e(cpc, core_num):
    cpc.res_t = []
    for (idx, theta_i) in enumerate(cpc.provider_group):
        L_i = sum([cpc.node_set[node_idx].exec_t for node_idx in theta_i])

        f_theta = cpc.node_set[theta_i[-1]].f_t
        I_e_of_lambda_v_e = []

        for node_idx in cpc.lambda_v_e[idx]:
            node = cpc.node_set[node_idx]
            high_p_list = [i for i in node.I if cpc.node_set[i].f_t > f_theta and cpc.node_set[i].priority > node.priority]
            low_p_list = [i for i in node.I if cpc.node_set[i].f_t > f_theta and cpc.node_set[i].priority < node.priority]

            if len(low_p_list) > core_num:
                low_p_list = low_p_list[:core_num]
            
            I_e_of_lambda_v_e = list(set(I_e_of_lambda_v_e) | set(high_p_list) | set(low_p_list))

        inf_path_num = get_path_num(cpc.node_set, I_e_of_lambda_v_e)

        R_e = L_i + cpc.beta[idx]

        if inf_path_num >= core_num:
            inf_workload = 0
            for v_idx in I_e_of_lambda_v_e:
                if cpc.node_set[v_idx].f_t - cpc.node_set[v_idx].exec_t >= f_theta:
                    inf_workload += cpc.node_set[v_idx].exec_t
                else:
                    inf_workload += cpc.node_set[v_idx].f_t - f_theta
            R_e += math.ceil(inf_workload / core_num)

        cpc.res_t.append(R_e)

def calculate_cpc_res_t(cpc, core_num):
    calculate_I(cpc)
    calculate_node_I_e(cpc, core_num)
    calculate_finish_time_bound(cpc, core_num)
    calculate_beta_and_lambda_v_e(cpc)
    calculate_R_e(cpc, core_num)
