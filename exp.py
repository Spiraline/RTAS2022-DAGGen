import argparse
import math
from numpy.random import normal
from model.dag import generate_random_dag, generate_backup_dag_dict, generate_from_dict
from model.cpc import construct_cpc, assign_priority
from sched.fp import sched_fp

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

    parser.add_argument('--function', type=str, help='function type for score', default='e')
    parser.add_argument('--function_std', type=float, help='variance for score function', default=0.05)
    parser.add_argument('--acceptance', type=float, help='Acceptance bar for score function', default=0.85)

    parser.add_argument('--base', type=str, help='list for value of base [small, large]', default='100,200')
    parser.add_argument('--density', type=float, help='(avg execution time * node #) / (deadline * cpu #)', default=0.3)
    parser.add_argument('--dangling', type=float, help='dangling DAG node # / total node #', default=0.2)
    parser.add_argument('--SL_exp', type=int, help='exponential of SL node', default=30)

    args = parser.parse_args()

    ### experiments argument
    dag_num = args.dag_num
    iter_size = args.iter_size
    core_num = args.core_num
    density = args.density
    sl_unit = args.sl_unit
    func_std = args.function_std

    def get_noise():
        return normal(0, func_std, 1)

    if args.function == 'log':
        def count2score(x) :
            return math.log(x+1) * get_noise()
    elif args.function == 'e':
        def count2score(x, std=True):
            delta = get_noise()
            if std :
                return max(1 - pow(math.e, -x/args.SL_exp) - math.fabs(delta), 0)
            else :
                return 1 - pow(math.e, -x/args.SL_exp)

        def score2count(score) :
            return (-args.SL_exp) * math.log(-score+1)
    else :
        raise NotImplementedError

    base_small, base_large = [int(b) for b in args.base.split(",")]

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
    normal_dag = generate_random_dag(**dag_param)
    backup_dag_dict = generate_backup_dag_dict(normal_dag.dict, args.backup)
    backup_dag = generate_from_dict(backup_dag_dict)

    ### Make CPC model and assign priority

    normal_cpc = construct_cpc(normal_dag)
    backup_cpc = construct_cpc(backup_dag)
    assign_priority(normal_cpc)
    assign_priority(backup_cpc)

    ### Check feasibility with FP
    normal_makespan = sched_fp(normal_dag.node_set, core_num)
    backup_makespan = sched_fp(backup_dag.node_set, core_num)
    
