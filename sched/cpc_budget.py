from math import floor
from sys import path

path.insert(0, '..')

from model.cpc import calculate_cpc_res_t
from sched.fp import sched_fp

def get_e_s_max(cpc, deadline):
    return deadline - sum([cpc.node_set[i].exec_t for i in cpc.critical_path if i != cpc.sl_node_idx])

def cpc_budget(cpc, deadline, core_num, sl_unit):
    # calculate e_s_max
    e_s_max = deadline - sum([cpc.node_set[i].exec_t for i in cpc.critical_path if i != cpc.sl_node_idx])

    # # calculate e_s_init
    # cpc.node_set[cpc.sl_node_idx].exec_t = e_s_max
    # calculate_cpc_res_t(cpc, core_num)

    # for (idx, theta) in enumerate(cpc.provider_group):
    #     if cpc.sl_node_idx in theta:
    #         theta_idx_with_sl = idx
    #         break

    # e_s_init = deadline - sum([cpc.res_t[i] for i in range(len(cpc.provider_group)) if i != theta_idx_with_sl])
    # e_s_init -= sum([cpc.node_set[i].exec_t for i in cpc.provider_group[theta_idx_with_sl] if i != cpc.sl_node_idx])
    # e_s_init -= sum([cpc.node_set[i].exec_t for i in cpc.F[theta_idx_with_sl]]) / core_num

    # if e_s_init <= 0:
    #     return 0

    # binary search for optimal L
    # L_low = floor(e_s_init / sl_unit)
    L_low = 0
    L_high = floor(e_s_max / sl_unit)

    while L_low < L_high:
        L_mid = floor((L_high + L_low + 1) / 2)
        e_s = int(L_mid * sl_unit)
        cpc.node_set[cpc.sl_node_idx].exec_t = e_s
        calculate_cpc_res_t(cpc, core_num)

        # print(cpc)
        # print(deadline)

        W = sum([node.exec_t for node in cpc.node_set])
        L = sum([cpc.node_set[i].exec_t for i in cpc.critical_path])
        # print('classic :', L + (W - L) / core_num)
        # print('CPC :', sum(cpc.res_t))
        # print('actual makespan :', sched_fp(cpc.node_set, core_num))

        if sum(cpc.res_t) == deadline:
            L_low = L_mid
            L_high = L_mid
        elif sum(cpc.res_t) > deadline:
            L_high = L_mid - 1
        else:
            L_low = L_mid
    
    return int(L_low * sl_unit)
        