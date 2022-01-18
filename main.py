import argparse
import os
import csv
from exp import acc_exp, debug, syn_exp
from datetime import datetime

if __name__ == '__main__':
    start_ts = datetime.now()
    parser = argparse.ArgumentParser(description='argparse for synthetic test')
    parser.add_argument('--dag_num', type=int, help='Test DAG number', default=100)
    parser.add_argument('--instance_num', type=int, help='#iterative per 1 DAG', default=100)

    parser.add_argument('--core_num', type=int, help='#cpu', default=4)
    parser.add_argument('--node_num', type=int, help='#node number in DAG', default=40)
    parser.add_argument('--depth', type=float, help='depth of DAG', default=6.5)
    parser.add_argument('--backup_ratio', type=float, help='Backup node execution time rate', default=0.2)
    parser.add_argument('--sl_unit', type=float, help='SL node execution unit time', default=8.0)

    parser.add_argument('--exec_avg', type=int, help='WCET average of nodes', default=40)
    parser.add_argument('--exec_std', type=int, help='WCET std of nodes', default=20)

    parser.add_argument('--sl_exp', type=int, help='exponential of SL node', default=5)
    parser.add_argument('--sl_std', type=float, help='variance for score function', default=1.0)
    parser.add_argument('--acceptance', type=float, help='Acceptance bar for score function', default=0.95)

    parser.add_argument('--base', type=str, help='list for value of base [small, large]', default='50,100')
    parser.add_argument('--density', type=float, help='(avg execution time * node #) / (deadline * cpu #)', default=0.3)
    parser.add_argument('--dangling', type=float, help='dangling DAG node # / total node #', default=0.2)

    parser.add_argument('--file', type=str, help='DAG csv file')
    parser.add_argument('--exp', type=str, help='what exp')

    args = parser.parse_args()

    exp_param = {
        "dag_num" : args.dag_num,
        "instance_num" : args.instance_num,
        "core_num" : args.core_num,
        "node_num" : args.node_num,
        "depth" : args.depth,
        "backup_ratio" : args.backup_ratio,
        "sl_unit" : args.sl_unit,
        "exec_avg" : args.exec_avg,
        "exec_std" : args.exec_std,
        "sl_exp" : args.sl_exp,
        "sl_std" : args.sl_std,
        "acceptance" : args.acceptance,
        "base" : [int(b) for b in args.base.split(",")],
        "density" : args.density,
        "dangling" : args.dangling
    }    

    # Debug Mode
    if args.file and os.path.exists(args.file):
        debug(args.file, **exp_param)
    elif args.exp == 'density':
        for d in range(20, 71, 5):
            d_f = round(d / 100, 2)
            print('Density %f start' % d_f)
            exp_param["density"] = d_f
            un, dm, both = syn_exp(**exp_param)

            file_name = 'res/density_' + str(d) + '.csv'
            with open(file_name, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(['Failure Type', 'Base Small', 'Base Large', 'Ours Classic', 'Ours CPC'])
                wr.writerow(['Unacceptable Result'] + un)
                wr.writerow(['Deadline Miss'] + dm)
                wr.writerow(['Both'] + both)

    elif args.exp == 'std':
        for s in range(6, 15, 2):
            s_f = round(s / 10, 1)
            print('Density %f start' % s_f)
            exp_param["sl_std"] = s_f
            un, dm, both = syn_exp(**exp_param)

            file_name = 'res/std_' + str(s) + '.csv'
            with open(file_name, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(un)
                wr.writerow(dm)
                wr.writerow(both)

    elif args.exp == 'acc':
        acc_exp(**exp_param)

    end_ts = datetime.now()
    print('[System] Execution time : %s' % str(end_ts - start_ts))