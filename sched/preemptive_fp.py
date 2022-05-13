import math
from collections import deque
from numpy.random import normal

# return value : makespan


def sched_preemptive_fp(node_set, core_num):
    ready_queue = deque()
    # tid, start_ts, end_ts
    time_table = [[] for _ in range(core_num)]
    dedicated_node = [-1] * core_num
    is_complete = [False] * len(node_set)
    remain_exec = [node.exec_t for node in node_set]
    ts = 0
    ts_diff = 0

    for node in node_set:
        if len(node.pred) == 0:
            ready_queue.append(node)

    while False in is_complete:
        # new tick

        # check if there is finish node
        for (idx, core_table) in enumerate(time_table):
            if len(core_table) > 0 and core_table[-1][2] <= ts and not is_complete[core_table[-1][0]]:
                completed_node_idx = core_table[-1][0]
                is_complete[completed_node_idx] = True
                dedicated_node[idx] = -1

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
                ready_queue = sorted(ready_queue, key=lambda x: x.priority)

        # For debug
        # print(ts)
        # print([node.tid for node in ready_queue])

        # for core_table in time_table:
        #     print(core_table)

        victim_cand = [(core_idx, node_set[node_idx]) for core_idx,
                       node_idx in enumerate(dedicated_node) if node_idx >= 0]
        victim_cand = sorted(victim_cand, key=lambda x: -x[1].priority)

        # assign new node to idle core
        for (core_idx, node_idx) in enumerate(dedicated_node):
            if node_idx != 0 and len(ready_queue) > 0:
                # get highest priority job
                node = ready_queue.pop()
                dedicated_node[core_idx] = node.tid

        # Preempt if lower priority node is executing
        while len(ready_queue) > 0 and len(victim_cand) > 0 and ready_queue[0].priority > victim_cand[-1][1].priority:
            core_idx, victim_node = victim_cand.pop()
            preemption_node = ready_queue.pop()
            ready_queue.appendleft(victim_node)
            dedicated_node[core_idx] = preemption_node.tid

        # Update ts and
        # If not, update ts
        min_exec = min([remain_exec[node_idx]
                        for node_idx in dedicated_node if node_idx >= 0])
        for (core_idx, node_idx) in enumerate(dedicated_node):
            if node_idx >= 0:
                remain_exec[node] -= min_exec
                if len(time_table[core_idx]) > 0 and time_table[core_idx][-1][0] == node_idx:
                    time_table[core_idx][-1][2] += min_exec
                else:
                    time_table[core_idx].append([node_idx, ts, ts + min_exec])

        ts += min_exec

    makespan = 0

    for core_table in time_table:
        if len(core_table) > 0:
            last_f_t_in_core = core_table[-1][2]
            if last_f_t_in_core > makespan:
                makespan = last_f_t_in_core

    return makespan


def get_noise(std):
    return normal(0, std, 1)


def count2score(x, sl_exp, std):
    delta = get_noise(std)
    return max(1 - pow(math.e, -x/sl_exp+math.log(0.3)) - math.fabs(delta), 0)


def score2count(score, sl_exp):
    return math.floor((-1) * sl_exp * math.log(-score+1))

# return value : (unacceptable flag, loop count)


def check_acceptance(max_lc, sl_exp, std, acceptable):
    minimum_lc = score2count(acceptable, sl_exp)

    if max_lc < minimum_lc:
        return True, max_lc

    for lc in range(minimum_lc, max_lc+1):
        if count2score(lc, sl_exp, std) > acceptable:
            return False, lc

    return True, max_lc


def calculate_acc(max_lc, sl_exp, std, acceptable):
    max_tmp_acc = 0

    for lc in range(1, max_lc+1):
        tmp_acc = count2score(lc, sl_exp, std)
        if max_tmp_acc < tmp_acc:
            max_tmp_acc = tmp_acc
        if tmp_acc > acceptable:
            return max_tmp_acc

    return max_tmp_acc


def check_deadline_miss(dag, core_num, lc, sl_unit, deadline):
    dag.node_set[dag.sl_node_idx].exec_t = lc * sl_unit
    makespan = sched_fp(dag.node_set, core_num)

    return makespan > deadline
