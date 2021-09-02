import argparse
import math
import os
from model.dag import export_dag_file, generate_random_dag, generate_backup_dag_dict, generate_from_dict, import_dag_file
from model.cpc import construct_cpc, assign_priority
from sched.fp import check_acceptance, check_deadline_miss
from sched.classic_budget import classic_budget
from sched.cpc_budget import cpc_budget

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='argparse for test')
    parser.add_argument('--dag_num', type=int, help='Test DAG number', default=100)
    parser.add_argument('--iter_size', type=int, help='#iterative per 1 DAG', default=100)

    parser.add_argument('--core_num', type=int, help='#cpu', default=4)
    parser.add_argument('--node_num', type=int, help='#node number in DAG', default=40)
    parser.add_argument('--dag_depth', type=float, help='depth of DAG', default=6.5)
    parser.add_argument('--backup', type=float, help='Backup node execution time rate', default=0.8)
    parser.add_argument('--sl_unit', type=float, help='SL node execution unit time', default=2.0)

    parser.add_argument('--node_avg', type=int, help='WCET average of nodes', default=40)
    parser.add_argument('--node_std', type=int, help='WCET std of nodes', default=10)

    parser.add_argument('--sl_exp', type=int, help='exponential of SL node', default=30)
    parser.add_argument('--sl_std', type=float, help='variance for score function', default=0.05)
    parser.add_argument('--acceptance', type=float, help='Acceptance bar for score function', default=0.85)

    parser.add_argument('--base', type=str, help='list for value of base [small, large]', default='100,200')
    parser.add_argument('--density', type=float, help='(avg execution time * node #) / (deadline * cpu #)', default=0.3)
    parser.add_argument('--dangling', type=float, help='dangling DAG node # / total node #', default=0.2)    

    parser.add_argument('--file', type=str, help='DAG csv file')

    args = parser.parse_args()

    ### experiments argument
    dag_num = args.dag_num

    base_loop_count = [int(b) for b in args.base.split(",")]

    dag_param = {
        "node_num": [args.node_num, 0],
        "depth": [args.dag_depth, 1.5],
        "exec_t": [args.node_avg, args.node_std],
        "start_node": [1, 0],
        "end_node": [1, 0],
        "extra_arc_ratio" : 0.1,
        "dangling_node_ratio" : args.dangling
    }

    ### Make DAG and backup DAG
    if args.file and os.path.exists(args.file):
        dag_dict = import_dag_file(args.file)
        normal_dag = generate_from_dict(dag_dict)
    else:
        normal_dag = generate_random_dag(**dag_param)
        export_dag_file(normal_dag, 'dag.csv')

    backup_dag_dict = generate_backup_dag_dict(normal_dag.dict, args.backup)
    backup_dag = generate_from_dict(backup_dag_dict)

    ### Make CPC model and assign priority
    normal_cpc = construct_cpc(normal_dag)
    backup_cpc = construct_cpc(backup_dag)
    assign_priority(normal_cpc)
    assign_priority(backup_cpc)

    ### Budget analysis
    deadline = int((args.node_avg * args.node_num) / (args.core_num * args.density))
    normal_dag.node_set[normal_dag.sl_node_idx].exec_t = args.sl_unit
    backup_dag.node_set[backup_dag.sl_node_idx].exec_t = args.sl_unit

    normal_classic_budget = classic_budget(normal_cpc, deadline, args.core_num)
    backup_classic_budget = classic_budget(backup_cpc, deadline, args.core_num)
    normal_cpc_budget = cpc_budget(normal_cpc, deadline, args.core_num, args.sl_unit)
    backup_cpc_budget = cpc_budget(backup_cpc, deadline, args.core_num, args.sl_unit)

    # If budget is less than 0, DAG is infeasible
    if normal_classic_budget <= 0 or normal_cpc_budget <= 0 or backup_classic_budget <= 0 or backup_cpc_budget <= 0:
        print('infeasible DAG')

    classic_loop_count = math.floor(min(normal_classic_budget, backup_classic_budget) / args.sl_unit)
    cpc_loop_count = math.floor(min(normal_cpc_budget, backup_cpc_budget) / args.sl_unit)

    loop_count_list = base_loop_count + [classic_loop_count, cpc_loop_count]

    for max_lc in loop_count_list:
        unac_one_dag = 0
        miss_one_dag = 0
        both = 0
        for _ in range(args.iter_size):
            isUnacceptable, lc = check_acceptance(max_lc, args.sl_exp, args.sl_std, args.acceptance)
            isMiss = check_deadline_miss(normal_dag, args.core_num, lc, args.sl_unit, deadline) or check_deadline_miss(backup_dag, args.core_num, lc, args.sl_unit, deadline)

            if isUnacceptable and isMiss:
                both += 1
            elif isUnacceptable and not isMiss:
                unac_one_dag += 1
            elif not isUnacceptable and isMiss:
                miss_one_dag += 1
        
        unac_one_dag /= args.iter_size
        miss_one_dag /= args.iter_size
        