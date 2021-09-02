### return value : makespan
def sched_fp(node_set, core_num):
    
    ready_queue = []
    # time_table = [[], ] * core_num
    time_table = []
    for _ in range(core_num):
        time_table.append([])
    is_core_idle = [True, ] * core_num
    is_complete = [False, ] * len(node_set)
    ts = 0

    for node in node_set:
        if len(node.pred) == 0:
            ready_queue.append(node)

    while False in is_complete:
        ### new tick

        # check if there is finish node
        for (idx, core_table) in enumerate(time_table):
            if len(core_table) > 0 and core_table[-1][2] <= ts and not is_complete[core_table[-1][0]]:
                completed_node_idx = core_table[-1][0]
                is_complete[completed_node_idx] = True
                is_core_idle[idx] = True

                # Add new ready node
                succ_node_list = node_set[completed_node_idx].succ

                for succ_idx in succ_node_list:
                    isReady = True
                    for pred_idx in node_set[succ_idx].pred:
                        if not is_complete[pred_idx]:
                            isReady = False
                
                    if isReady:
                        ready_queue.append(node_set[succ_idx])
                
                # Sort by Priority
                ready_queue = sorted(ready_queue, key = lambda x : x.priority)

        ### For debug
        # print(ts)
        # print([node.tid for node in ready_queue])

        # for core_table in time_table:
        #     print(core_table)

        # If there is idle core, assign new node
        for (idx, isIdle) in enumerate(is_core_idle):
            if isIdle and len(ready_queue) > 0:
                # get highest priority job
                node = ready_queue.pop()
                time_table[idx].append([node.tid, ts, ts + node.exec_t])
                is_core_idle[idx] = False

        # If not, update ts
        f_t = [core_table[-1][2] for core_table in time_table if len(core_table) > 0 and core_table[-1][2] > ts]
        if len(f_t) > 0:
            ts = min(f_t)

    makespan = 0

    for core_table in time_table:
        if len(core_table) > 0:
            last_f_t_in_core = core_table[-1][2]
            if last_f_t_in_core > makespan:
                makespan = last_f_t_in_core

    return makespan