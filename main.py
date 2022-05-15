import argparse
import os
import csv
import yaml
from exp import acc_exp, budget_compare, debug, original_error_ratio, syn_exp
from datetime import datetime
from os import makedirs
from os.path import exists

if __name__ == '__main__':
    start_ts = datetime.now()
    parser = argparse.ArgumentParser(description='argparse for synthetic test')
    parser.add_argument('--config', '-c', type=str, help='config yaml file path', default='cfg.yaml')

    args = parser.parse_args()

    if not exists('cfg/' + args.config):
        print('Should select appropriate config file in cfg directory')
        exit(1)

    makedirs("res", exist_ok=True)

    with open('cfg/' + args.config, 'r') as f:
        config_dict = yaml.load(f, Loader=yaml.FullLoader)

    exp_param = {
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

    if config_dict["exp"] == 'budget':
        pr_cl, cpc = budget_compare(**exp_param)
        print(pr_cl, cpc)
    elif config_dict["exp"] == 'density':
        for d in range(config_dict["density_range"][0], config_dict["density_range"][1], config_dict["density_range"][2]):
            d_f = round(d / 100, 2)
            print('Density %f start' % d_f)
            exp_param["density"] = d_f
            exp_param["sl_std"] = config_dict["sl_std"]
            un, dm, both = syn_exp(**exp_param)

            file_name = 'res/density_' + str(d) + '.csv'
            with open(file_name, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(['Failure Type', 'Base Small', 'Base Large', 'Ours Classic', 'Ours CPC'])
                wr.writerow(['Unacceptable Result'] + un)
                wr.writerow(['Deadline Miss'] + dm)
                wr.writerow(['Both'] + both)
    elif config_dict["exp"] == 'std':
        for s in range(config_dict["std_range"][0], config_dict["std_range"][1], config_dict["std_range"][2]):
            s_f = round(s / 10, 1)
            print('Density %f start' % s_f)
            
            exp_param["density"] = config_dict["density"]
            exp_param["sl_std"] = s_f
            un, dm, both = syn_exp(**exp_param)

            file_name = 'res/std_' + str(s) + '.csv'
            with open(file_name, 'w', newline='') as f:
                wr = csv.writer(f)
                wr.writerow(un)
                wr.writerow(dm)
                wr.writerow(both)
    elif config_dict["exp"] == 'acc':
        exp_param["density"] = config_dict["density"]
        exp_param["sl_std"] = config_dict["sl_std"]
        acc_exp(**exp_param)
    elif config_dict["exp"] == "debug":
        if not exists(config_dict["dag_file"]):
            print('Should select appropriate dag file')
            exit(1)
        debug(config_dict["dag_file"], **exp_param)
    else:
        print('Select appropriate exp (density, std, acc, debug)')
        exit(1)

    end_ts = datetime.now()
    print('[System] Execution time : %s' % str(end_ts - start_ts))