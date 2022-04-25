import math
from sched.preemptive_classic_budget import preemptive_classic_budget
from model.dag import export_dag_file, generate_random_dag, generate_backup_dag, generate_from_dict, import_dag_file
from model.cpc import construct_cpc, assign_priority
from sched.fp import calculate_acc, check_acceptance, check_deadline_miss, sched_fp
from sched.classic_budget import classic_budget
from sched.cpc_budget import cpc_budget
import csv

def budget_compare(**kwargs):
    dag_num = kwargs.get('dag_num', 100)
    instance_num = kwargs.get('instance_num', 100)
    core_num = kwargs.get('core_num', 4)
    node_num = kwargs.get('node_num', [40,10])
    depth = kwargs.get('depth', [6.5,1.5])
    backup_ratio = kwargs.get('backup_ratio', 0.5)
    exec_t = kwargs.get('exec_t', [40,10])
    sl_unit = kwargs.get('sl_unit', 5.0)
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('A_acc', 0.95)
    base_loop_count = kwargs.get('base', [100, 200])
    density = kwargs.get('density', 0.3)
    extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)
    dangling_ratio = kwargs.get('dangling_ratio', 0.2)

    dag_param = {
        "node_num": node_num,
        "depth": depth,
        "exec_t": exec_t,
        "start_node": [1, 0],
        "end_node": [1, 0],
        "extra_arc_ratio" : extra_arc_ratio,
        "dangling_node_ratio" : dangling_ratio
    }

    dag_idx = 0
    while dag_idx < dag_num:
        ### Make DAG and backup DAG
        normal_dag = generate_random_dag(**dag_param)

        ### Make CPC model and assign priority
        normal_cpc = construct_cpc(normal_dag)
        assign_priority(normal_cpc)

        ### Budget analysis
        deadline = int((exec_t[0] * len(normal_dag.node_set)) / (core_num * density))
        normal_dag.dict["deadline"] = deadline

        normal_dag.node_set[normal_dag.sl_node_idx].exec_t = sl_unit

        normal_classic_budget = classic_budget(normal_cpc, deadline, core_num)
        normal_pr_classic_budget = preemptive_classic_budget(normal_cpc, deadline, core_num)       
        normal_cpc_budget = cpc_budget(normal_cpc, deadline, core_num, sl_unit)

        print(normal_classic_budget, normal_pr_classic_budget, normal_cpc_budget)

        dag_idx += 1

def syn_exp(**kwargs):
    dag_num = kwargs.get('dag_num', 100)
    instance_num = kwargs.get('instance_num', 100)
    core_num = kwargs.get('core_num', 4)
    node_num = kwargs.get('node_num', [40,10])
    depth = kwargs.get('depth', [6.5,1.5])
    backup_ratio = kwargs.get('backup_ratio', 0.5)
    exec_t = kwargs.get('exec_t', [40,10])
    sl_unit = kwargs.get('sl_unit', 5.0)
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('A_acc', 0.95)
    base_loop_count = kwargs.get('base', [100, 200])
    density = kwargs.get('density', 0.3)
    extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)
    dangling_ratio = kwargs.get('dangling_ratio', 0.2)

    dag_param = {
        "node_num": node_num,
        "depth": depth,
        "exec_t": exec_t,
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
        backup_dag = generate_backup_dag(normal_dag.dict, backup_ratio)

        ### Make CPC model and assign priority
        normal_cpc = construct_cpc(normal_dag)
        backup_cpc = construct_cpc(backup_dag)
        assign_priority(normal_cpc)
        assign_priority(backup_cpc)

        ### Budget analysis
        deadline = int((exec_t[0] * len(normal_dag.node_set)) / (core_num * density))
        normal_dag.dict["deadline"] = deadline
        backup_dag.dict["deadline"] = deadline
        normal_dag.dict["backup_exec_t"] = backup_dag.dict["backup_exec_t"]

        normal_dag.node_set[normal_dag.sl_node_idx].exec_t = sl_unit
        backup_dag.node_set[backup_dag.sl_node_idx].exec_t = sl_unit

        normal_classic_budget = classic_budget(normal_cpc, deadline, core_num)
        backup_classic_budget = classic_budget(backup_cpc, deadline, core_num)
        normal_cpc_budget = cpc_budget(normal_cpc, deadline, core_num, sl_unit)
        backup_cpc_budget = cpc_budget(backup_cpc, deadline, core_num, sl_unit)

        classic_loop_count = math.floor(min(normal_classic_budget, backup_classic_budget) / sl_unit)
        cpc_loop_count = math.floor(min(normal_cpc_budget, backup_cpc_budget) / sl_unit)

        # If budget is less than 0, DAG is infeasible
        if check_deadline_miss(normal_dag, core_num, cpc_loop_count, sl_unit, deadline) or check_deadline_miss(backup_dag, core_num, cpc_loop_count, sl_unit, deadline) or classic_loop_count <= 0 or cpc_loop_count <= 0:
            print('[' + str(dag_idx) + ']', 'infeasible DAG, retry')
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

            # if lc_idx == len(loop_count_list) - 1:
            #     if both_one_dag > 0 or miss_one_dag > 0:
            #         print(both_one_dag, miss_one_dag)
            #         print(deadline)
            #         print(density)
            #         export_dag_file(normal_dag, 'dag.csv')

        print('[' + str(dag_idx) + ']', loop_count_list)
        dag_idx += 1
    
    for lc_idx in range(len(loop_count_list)):
        total_unaccept[lc_idx] /= dag_num
        total_deadline_miss[lc_idx] /= dag_num
        total_both[lc_idx] /= dag_num

    return total_unaccept, total_deadline_miss, total_both

def acc_exp(**kwargs):
    dag_num = kwargs.get('dag_num', 100)
    instance_num = kwargs.get('instance_num', 100)
    core_num = kwargs.get('core_num', 4)
    node_num = kwargs.get('node_num', [40,10])
    depth = kwargs.get('depth', [6.5,1.5])
    backup_ratio = kwargs.get('backup_ratio', 0.5)
    sl_unit = kwargs.get('sl_unit', 5.0)
    exec_t = kwargs.get('exec_t', [40,10])
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('acceptance', 0.9)
    base_loop_count = kwargs.get('base', [100, 200])
    density = kwargs.get('density', 0.3)
    extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)
    dangling_ratio = kwargs.get('dangling', 0.2)

    dag_param = {
        "node_num": node_num,
        "depth": depth,
        "exec_t": exec_t,
        "start_node": [1, 0],
        "end_node": [1, 0],
        "extra_arc_ratio" : extra_arc_ratio,
        "dangling_node_ratio" : dangling_ratio
    }

    with open('res/acc.csv', 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['Base Small', 'Base Large', 'Ours Classic', 'Ours CPC'])

        dag_idx = 0
        while dag_idx < dag_num:
            ### Make DAG and backup DAG
            normal_dag = generate_random_dag(**dag_param)
            backup_dag = generate_backup_dag(normal_dag.dict, backup_ratio)

            ### Make CPC model and assign priority
            normal_cpc = construct_cpc(normal_dag)
            backup_cpc = construct_cpc(backup_dag)
            assign_priority(normal_cpc)
            assign_priority(backup_cpc)

            ### Budget analysis
            deadline = int((exec_t[0] * len(normal_dag.node_set)) / (core_num * density))
            normal_dag.dict["deadline"] = deadline
            backup_dag.dict["deadline"] = deadline
            normal_dag.dict["backup_exec_t"] = backup_dag.dict["backup_exec_t"]
            
            normal_dag.node_set[normal_dag.sl_node_idx].exec_t = sl_unit
            backup_dag.node_set[backup_dag.sl_node_idx].exec_t = sl_unit

            normal_classic_budget = classic_budget(normal_cpc, deadline, core_num)
            backup_classic_budget = classic_budget(backup_cpc, deadline, core_num)
            normal_cpc_budget = cpc_budget(normal_cpc, deadline, core_num, sl_unit)
            backup_cpc_budget = cpc_budget(backup_cpc, deadline, core_num, sl_unit)

            classic_loop_count = math.floor(min(normal_classic_budget, backup_classic_budget) / sl_unit)
            cpc_loop_count = math.floor(min(normal_cpc_budget, backup_cpc_budget) / sl_unit)

            # If budget is less than 0, DAG is infeasible
            if check_deadline_miss(normal_dag, core_num, cpc_loop_count, sl_unit, deadline) or check_deadline_miss(backup_dag, core_num, cpc_loop_count, sl_unit, deadline) or classic_loop_count <= 0 or cpc_loop_count <= 0:
                print('[' + str(dag_idx) + ']', 'infeasible DAG, retry')
                continue

            loop_count_list = base_loop_count + [classic_loop_count, cpc_loop_count]

            for _ in range(instance_num):
                acc_list = []
                for (lc_idx, max_lc) in enumerate(loop_count_list):
                    acc = calculate_acc(max_lc, sl_exp, sl_std, A_acc)
                    acc_list.append(acc)
                wr.writerow(acc_list)

            dag_idx += 1

            print('[' + str(dag_idx) + ']', 'Complete')

    return

def debug(file, **kwargs):
    core_num = kwargs.get('core_num', 4)
    sl_unit = kwargs.get('sl_unit', 8.0)
    sl_exp = kwargs.get('sl_exp', 30)
    sl_std = kwargs.get('sl_std', 1.0)
    A_acc = kwargs.get('A_acc', 0.95)
    base_loop_count = kwargs.get('base', [100, 200])

    dag_dict = import_dag_file(file)
    normal_dag = generate_from_dict(dag_dict)
    backup_dag = generate_backup_dag(normal_dag.dict)

    deadline = dag_dict["deadline"]

    print(normal_dag)
    print(backup_dag)

    normal_cpc = construct_cpc(normal_dag)
    backup_cpc = construct_cpc(backup_dag)
    assign_priority(normal_cpc)
    assign_priority(backup_cpc)

    ### Budget analysis
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
            print('maximum possible budget in FP :', lc-1)
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