import argparse
from sched.fp import sched_fp
import yaml
from datetime import datetime
from os import makedirs
from os.path import exists
from model.preemptive_dag import generate_random_dag, assign_random_priority
from sched.preemptive_classic_budget import ideal_maximum_budget, preemptive_classic_budget

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
        "acceptance" : config_dict["acceptance_threshold"],
        "base" : config_dict["baseline"],
        "density" : config_dict["density"],
        "dangling" : config_dict["dangling_ratio"]
    }

    dag_idx = 0

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
                make_span = sched_fp(preemptive_dag.node_set, dag_param["core_num"])
                if make_span <= deadline:
                    e_s_preempt = e_s
                    feasible_pri = p_list
                    is_feasible = True
                    break
            if is_feasible:
                break

        if not is_feasible:
            e_s_preempt = max(e_s_classic, 0)
        
        print('[' + str(dag_idx) + ']', e_s_classic, e_s_preempt, feasible_pri)
        dag_idx += 1


    end_ts = datetime.now()
    print('[System] Execution time : %s' % str(end_ts - start_ts))