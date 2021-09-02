### Calculate I and I_e group
def calculate_inference_group(cpc):
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

def cpc_response_time(cpc, core_num):
    calculate_inference_group(cpc)

def cpc_budget(cpc, deadline, core_num):
    cpc_response_time(cpc, core_num)