import argparse
import yaml
import math
import csv
from datetime import datetime
from os import makedirs
from os.path import exists
from model.preemptive_dag import generate_random_dag, generate_backup_dag, assign_random_priority, get_critical_path, import_dag_file, generate_from_dict
from sched.classic_budget import classic_budget
from sched.preemptive_classic_budget import ideal_maximum_budget, preemptive_classic_budget
from sched.preemptive_fp import sched_preemptive_fp, calculate_acc, check_acceptance, check_deadline_miss

def random_priority_LS(dag_param):
    dag_idx = 0
    classic_sum = 0
    preemptive_sum = 0
    only_preemptive_can_sched = 0
    ratio = 0

    while dag_idx < dag_param["dag_num"]:
        ### Make DAG
        preemptive_dag = generate_random_dag(**dag_param)
        deadline = int((dag_param["exec_t"][0] * len(preemptive_dag.node_set)) / (dag_param["core_num"] * dag_param["density"]))
        preemptive_dag.dict["deadline"] = deadline

        ### Calculate preemptive Classic budget
        e_s_classic = preemptive_classic_budget(preemptive_dag, deadline, dag_param["core_num"])
        e_s_max = ideal_maximum_budget(preemptive_dag, deadline)
        assign_random_priority(preemptive_dag)
        
        if e_s_max <= 0:
            print('[' + str(dag_idx) + ']', 'not feasible. Retry')
            continue

        for e_s in range(int(e_s_max), max(int(e_s_classic), 0), -int(dag_param["sl_unit"])):
            preemptive_dag.node_set[preemptive_dag.sl_node_idx].exec_t = e_s
            feasible_pri = []
            is_feasible = False
            for _ in range(1000): # Can parameterize
                ### assign random priority and FP
                p_list = assign_random_priority(preemptive_dag)
                make_span = sched_preemptive_fp(preemptive_dag.node_set, dag_param["core_num"])
                if make_span <= deadline:
                    e_s_preempt = e_s
                    feasible_pri = p_list
                    is_feasible = True
                    break
            if is_feasible:
                break

        if not is_feasible:
            e_s_preempt = max(e_s_classic, 0)

        if e_s_classic > 0:
            classic_sum += e_s_classic
            preemptive_sum += e_s_preempt
            ratio += e_s_preempt / e_s_classic
        elif is_feasible:
            only_preemptive_can_sched += 1

        print('[' + str(dag_idx) + ']', e_s_classic, e_s_preempt, feasible_pri)
        dag_idx += 1

    return ratio / dag_param["dag_num"], classic_sum / dag_param["dag_num"], preemptive_sum / dag_param["dag_num"], only_preemptive_can_sched

def accuracy_exp(dag_param):
    dag_idx = 0

    f = open('res/acc.csv', 'w', newline='')
    wr = csv.writer(f)
    wr.writerow(['Base Small', 'Base Large', 'Preemptive Classic'])

    while dag_idx < dag_param["dag_num"]:
        ### Make DAG
        normal_dag = generate_random_dag(**dag_param)
        assign_random_priority(normal_dag)
        backup_dag = generate_backup_dag(normal_dag.dict, dag_param["backup_ratio"])
        deadline = int((dag_param["exec_t"][0] * len(normal_dag.node_set)) / (dag_param["core_num"] * dag_param["density"]))
        normal_dag.dict["deadline"] = deadline
        backup_dag.dict["deadline"] = deadline

        ### TODO: how about priority?

        ### Calculate preemptive Classic budget
        normal_budget = preemptive_classic_budget(normal_dag, deadline, dag_param["core_num"])
        backup_budget = preemptive_classic_budget(normal_dag, deadline, dag_param["core_num"])

        lc = math.floor(min(normal_budget, backup_budget) / dag_param["sl_unit"])

        if lc <= 0:
            print('[' + str(dag_idx) + ']', 'infeasible DAG, retry')
            continue

        lc_list = dag_param["base"] + [lc]

        for _ in range(dag_param["instance_num"]):
            acc_list = []
            for (lc_idx, max_lc) in enumerate(lc_list):
                acc = calculate_acc(max_lc, dag_param["sl_exp"], dag_param["sl_std"], dag_param["acceptance"])
                acc_list.append(acc)
        wr.writerow(acc_list)

        dag_idx += 1
    
    f.close()

def critical_failure_exp(dag_param):
    dag_idx = 0

    total_unaccept = [0, ] * (len(dag_param["base"]) + 1)
    total_deadline_miss = [0, ] * (len(dag_param["base"]) + 1)
    total_both = [0, ] * (len(dag_param["base"]) + 1)

    while dag_idx < dag_param["dag_num"]:
        ### Make DAG
        normal_dag = generate_random_dag(**dag_param)
        assign_random_priority(normal_dag)
        backup_dag = generate_backup_dag(normal_dag.dict, dag_param["backup_ratio"])
        deadline = int((dag_param["exec_t"][0] * len(normal_dag.node_set)) / (dag_param["core_num"] * dag_param["density"]))
        normal_dag.dict["deadline"] = deadline
        backup_dag.dict["deadline"] = deadline

        ### TODO: how about priority?

        ### Calculate preemptive Classic budget
        normal_budget = preemptive_classic_budget(normal_dag, deadline, dag_param["core_num"])
        backup_budget = preemptive_classic_budget(normal_dag, deadline, dag_param["core_num"])

        lc = math.floor(min(normal_budget, backup_budget) / dag_param["sl_unit"])

        if lc <= 0:
            # print('[' + str(dag_idx) + ']', 'infeasible DAG, retry')
            continue

        lc_list = dag_param["base"] + [lc]

        for (lc_idx, max_lc) in enumerate(lc_list):
            unac_one_dag = 0
            miss_one_dag = 0
            both_one_dag = 0
            for _ in range(dag_param["instance_num"]):
                isUnacceptable, lc = check_acceptance(max_lc, dag_param["sl_exp"], dag_param["sl_std"], dag_param["acceptance"])
                isMiss = check_deadline_miss(normal_dag, dag_param["core_num"], lc, dag_param["sl_unit"], deadline) or check_deadline_miss(backup_dag, dag_param["core_num"], lc, dag_param["sl_unit"], deadline)

                if isUnacceptable and isMiss:
                    both_one_dag += 1
                elif isUnacceptable and not isMiss:
                    unac_one_dag += 1
                elif not isUnacceptable and isMiss:
                    miss_one_dag += 1
            
            total_unaccept[lc_idx] += unac_one_dag / dag_param["instance_num"]
            total_deadline_miss[lc_idx] += miss_one_dag / dag_param["instance_num"]
            total_both[lc_idx] += both_one_dag / dag_param["instance_num"]

        dag_idx += 1

    for lc_idx in range(len(lc_list)):
        total_unaccept[lc_idx] /= dag_param["dag_num"]
        total_deadline_miss[lc_idx] /= dag_param["dag_num"]
        total_both[lc_idx] /= dag_param["dag_num"]

    return total_unaccept, total_deadline_miss, total_both

def original_classic_failure(dag_param):
    dag_idx = 0

    diff_num = 0

    while dag_idx < dag_param["dag_num"]:
        ### Make DAG
        normal_dag = generate_random_dag(**dag_param)
        normal_dag.critical_path = get_critical_path(normal_dag, normal_dag.sl_node_idx)
        deadline = int((dag_param["exec_t"][0] * len(normal_dag.node_set)) / (dag_param["core_num"] * dag_param["density"]))
        normal_dag.dict["deadline"] = deadline

        ori_budget = classic_budget(normal_dag, deadline, dag_param["core_num"])
        new_budget = preemptive_classic_budget(normal_dag, deadline, dag_param["core_num"])

        if ori_budget <= 0 or new_budget <= 0:
            continue

        if ori_budget != new_budget:
            diff_num += 1

        dag_idx += 1
    
    return diff_num / dag_param["dag_num"]

if __name__ == '__main__':
    start_ts = datetime.now()
    parser = argparse.ArgumentParser(description='Preemptive Exp')
    parser.add_argument('--config', '-c', type=str, help='config yaml file path', default='cfg.yaml')

    args = parser.parse_args()

    if not exists('cfg/' + args.config):
        print('Should select appropriate config file in cfg directory')
        exit(1)

    makedirs("res", exist_ok=True)

    with open('cfg/' + args.config, 'r') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

    dag_param = {
        "dag_num" : config_dict["dag_num"],
        "instance_num" : config_dict["instance_num"],
        "core_num" : config_dict["core_num"],
        "node_num" : config_dict["node_num"],
        "depth" : config_dict["depth"],
        "exec_t" : config_dict["exec_t"],
        "backup_ratio" : config_dict["backup_ratio"],
        "sl_unit" : config_dict["sl_unit"],
        "sl_exp" : config_dict["sl_exp"],
        "sl_std" : config_dict["sl_std"],
        "acceptance" : config_dict["acceptance_threshold"],
        "base" : config_dict["baseline"],
        "density" : config_dict["density"],
        "dangling_node_ratio" : config_dict["dangling_ratio"]
    }

    if config_dict["exp"] == "random_pri":
        print(random_priority_LS(dag_param))
    elif config_dict["exp"] == "acc":
        accuracy_exp(dag_param)
    elif config_dict["exp"] == "fail":
        for d in range(config_dict["density_range"][0], config_dict["density_range"][1], config_dict["density_range"][2]):
            dag_param["density"] = d / 100
            file_name = 'res/density_' + str(d) + '.csv'
            un, dm, both = critical_failure_exp(dag_param, d)
            with open(file_name, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(['Failure Type', 'Base Small', 'Base Large', 'Preemptive Classic'])
                wr.writerow(['Unacceptable Result'] + un)
                wr.writerow(['Deadline Miss'] + dm)
                wr.writerow(['Both'] + both)
    elif config_dict["exp"] == "error":
        f = open('res/error_ratio.csv', 'w')
        wr = csv.writer(f)
        for d in range(config_dict["density_range"][0], config_dict["density_range"][1], config_dict["density_range"][2]):
            dag_param["density"] = round(d / 100, 2)
            wr.writerow([dag_param["density"], original_classic_failure(dag_param)])
        f.close()
    else:
        # For debugging Autoware DAG
        # dict_from_file = import_dag_file('custom_dag/classic_fail.dag')
        # normal_dag = generate_from_dict(dict_from_file)
        # print(normal_dag)

        # ori_budget = classic_budget(normal_dag, 20, 3)
        # new_budget = preemptive_classic_budget(normal_dag, 20, 3)

        # print(ori_budget, new_budget)
        
        print('[System] Invalid exp type')
        exit(1)

    end_ts = datetime.now()
    print('[System] Execution time : %s' % str(end_ts - start_ts))