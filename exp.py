import math
from model.dag import export_dag_file, generate_random_dag, generate_backup_dag_dict, generate_from_dict, import_dag_file
from model.cpc import construct_cpc, assign_priority
from sched.fp import check_acceptance, check_deadline_miss
from sched.classic_budget import classic_budget
from sched.cpc_budget import cpc_budget

def syn_exp(**kwargs):
    dag_num = kwargs.get('dag_num', 100)
    instance_num = kwargs.get('instance_num', 100)
    core_num = kwargs.get('core_num', 4)
    node_num = kwargs.get('node_num', 40)
    depth = kwargs.get('depth', 6.5)
    backup_ratio = kwargs.get('backup_ratio', 0.5)
    sl_unit = kwargs.get('sl_unit', 5.0)
    exec_avg = kwargs.get('exec_avg', 40)
    exec_std = kwargs.get('exec_std', 10)
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('A_acc', 0.95)
    base_loop_count = kwargs.get('base', [100, 200])
    density = kwargs.get('density', 0.3)
    extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)
    dangling_ratio = kwargs.get('dangling_ratio', 0.2)

    dag_param = {
        "node_num": [node_num, 0],
        "depth": [depth, 1.5],
        "exec_t": [exec_avg, exec_std],
        "start_node": [1, 0],
        "end_node": [1, 0],
        "extra_arc_ratio" : extra_arc_ratio,
        "dangling_node_ratio" : dangling_ratio
    }

    total_unaccept = [0, ] * (len(base_loop_count) + 2)
    total_deadline_miss = [0, ] * (len(base_loop_count) + 2)
    total_both = [0, ] * (len(base_loop_count) + 2)

    dag_idx = 0
    while dag_idx < dag_num:
        ### Make DAG and backup DAG
        normal_dag = generate_random_dag(**dag_param)

        backup_dag_dict = generate_backup_dag_dict(normal_dag.dict, backup_ratio)
        backup_dag = generate_from_dict(backup_dag_dict)

        ### Make CPC model and assign priority
        normal_cpc = construct_cpc(normal_dag)
        backup_cpc = construct_cpc(backup_dag)
        assign_priority(normal_cpc)
        assign_priority(backup_cpc)

        ### Budget analysis
        deadline = int((exec_avg * node_num) / (core_num * density))
        normal_dag.node_set[normal_dag.sl_node_idx].exec_t = sl_unit
        backup_dag.node_set[backup_dag.sl_node_idx].exec_t = sl_unit

        normal_classic_budget = classic_budget(normal_cpc, deadline, core_num)
        backup_classic_budget = classic_budget(backup_cpc, deadline, core_num)
        normal_cpc_budget = cpc_budget(normal_cpc, deadline, core_num, sl_unit)
        backup_cpc_budget = cpc_budget(backup_cpc, deadline, core_num, sl_unit)

        classic_loop_count = math.floor(min(normal_classic_budget, backup_classic_budget) / sl_unit)
        cpc_loop_count = math.floor(min(normal_cpc_budget, backup_cpc_budget) / sl_unit)

        # If budget is less than 0, DAG is infeasible
        if classic_loop_count <= 0 or cpc_loop_count <= 0:
            # print('[' + str(dag_idx) + ']', 'infeasible DAG, retry')
            continue

        loop_count_list = base_loop_count + [classic_loop_count, cpc_loop_count]

        for (lc_idx, max_lc) in enumerate(loop_count_list):
            unac_one_dag = 0
            miss_one_dag = 0
            both_one_dag = 0
            for _ in range(instance_num):
                isUnacceptable, lc = check_acceptance(max_lc, sl_exp, sl_std, A_acc)
                isMiss = check_deadline_miss(normal_dag, core_num, lc, sl_unit, deadline) or check_deadline_miss(backup_dag, core_num, lc, sl_unit, deadline)

                if isUnacceptable and isMiss:
                    both_one_dag += 1
                elif isUnacceptable and not isMiss:
                    unac_one_dag += 1
                elif not isUnacceptable and isMiss:
                    miss_one_dag += 1

            total_unaccept[lc_idx] += unac_one_dag / instance_num
            total_deadline_miss[lc_idx] += miss_one_dag / instance_num
            total_both[lc_idx] += both_one_dag / instance_num

            if lc_idx == len(loop_count_list) - 1:
                if both_one_dag > 0 or miss_one_dag > 0:
                    export_dag_file(normal_dag, 'dag.csv')

        # print('[' + str(dag_idx) + ']', loop_count_list)
        dag_idx += 1
    
    for lc_idx in range(len(loop_count_list)):
        total_unaccept[lc_idx] /= dag_num
        total_deadline_miss[lc_idx] /= dag_num
        total_both[lc_idx] /= dag_num

    return total_unaccept, total_deadline_miss, total_both

def debug(file, **kwargs):
    core_num = kwargs.get('core_num', 4)
    node_num = kwargs.get('node_num', 40)
    backup_ratio = kwargs.get('backup_ratio', 0.5)
    sl_unit = kwargs.get('sl_unit', 5.0)
    exec_avg = kwargs.get('exec_avg', 40)
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('A_acc', 0.95)
    base_loop_count = kwargs.get('base', [100, 200])
    density = kwargs.get('density', 0.3)

    dag_dict = import_dag_file(file)
    normal_dag = generate_from_dict(dag_dict)
    backup_dag_dict = generate_backup_dag_dict(normal_dag.dict, backup_ratio)
    backup_dag = generate_from_dict(backup_dag_dict)

    normal_cpc = construct_cpc(normal_dag)
    backup_cpc = construct_cpc(backup_dag)
    assign_priority(normal_cpc)
    assign_priority(backup_cpc)

    ### Budget analysis
    deadline = int((exec_avg * node_num) / (core_num * density))
    normal_dag.node_set[normal_dag.sl_node_idx].exec_t = sl_unit
    backup_dag.node_set[backup_dag.sl_node_idx].exec_t = sl_unit

    normal_classic_budget = classic_budget(normal_cpc, deadline, core_num)
    backup_classic_budget = classic_budget(backup_cpc, deadline, core_num)
    normal_cpc_budget = cpc_budget(normal_cpc, deadline, core_num, sl_unit)
    backup_cpc_budget = cpc_budget(backup_cpc, deadline, core_num, sl_unit)

    classic_loop_count = math.floor(min(normal_classic_budget, backup_classic_budget) / sl_unit)
    cpc_loop_count = math.floor(min(normal_cpc_budget, backup_cpc_budget) / sl_unit)
    
    loop_count_list = base_loop_count + [classic_loop_count, cpc_loop_count]

    print(normal_classic_budget / sl_unit, backup_classic_budget / sl_unit, normal_cpc_budget / sl_unit, backup_cpc_budget / sl_unit)

    for lc in range(300):
        if check_deadline_miss(backup_dag, core_num, lc, sl_unit, deadline):
            print('maximum possible budget in FP :', lc)
            break

    print(loop_count_list)

    for (lc_idx, max_lc) in enumerate(loop_count_list):
        isUnacceptable, lc = check_acceptance(max_lc, sl_exp, sl_std, A_acc)
        isMiss = check_deadline_miss(normal_dag, core_num, lc, sl_unit, deadline) or check_deadline_miss(backup_dag, core_num, lc, sl_unit, deadline)

        if isUnacceptable and isMiss:
            print(lc_idx, lc, 'both')
        elif isUnacceptable and not isMiss:
            print(lc_idx, lc, 'unacceptable')
        elif not isUnacceptable and isMiss:
            print(lc_idx, lc, 'deadline miss')