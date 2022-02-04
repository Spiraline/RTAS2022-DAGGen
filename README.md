# DAGGen
Random DAG Generator

## Requirement
```
python3 -m pip install PyYAML matplotlib pandas
```

## Usage

### Accuracy Experiment
```
python3 main.py -c acc.yaml
```

For `dag_num` = 10,000, 

### Density Experiment
```
python3 main.py --c density.yaml
```

### Std Experiment
```
python3 main.py --c std.yaml
```

### Visualization
- Accuracy plot: `python3 viz/acc.py`
- Density plot: `python3 viz/density.py`

## Parameter

* `exp` (str): select experiment type (`acc`, `density`, `std`)
* `exp_range` ([start, end, step]): same as python `range()`
    - `density_range`: The values are on a scale of 100 times (Required in `density` experiment)
    - `std_range`: The values are on a tenfold scale (Required in `std` experiment)
* `dag_num` (int): set the number of DAGs
* `instance_num` (int): set the number of instances
* `core_num` (int): set the number of cores
* `node_num` ([mean, dev]): set the number of nodes between `[mean-dev, mean+dev]`
* `depth` ([mean, dev]): set the depth of DAG between `[mean-dev, mean+dev]`
* `exec_t` ([mean, dev]): set the execution time of task between `[mean-dev, mean+dev]`

* `backup_ratio` (float): execution time ratio of backup node
* `sl` : Self-looping node's accuracy function is $A(L) = 1 - e^{-L/sl\_exp + ln0.3} - \left| N(0, sl\_std) \right|$
    * `sl_unit` (float) : $e_{S, 1}$
    * `sl_exp` (float)
    * `sl_std` (float): (Not required in `std` experiment)

* `acceptance_threshold` (int): Acceptance threshold for score function
* `baseline` ([small, large]): loop count for `BaseLine Small` and `BaseLine Large`
* `density` (float): (Not required in `density` experiment)
* `dangling_ratio` (float): dangling DAG node # / total node #