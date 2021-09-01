from random import randint, shuffle
import math
import csv

if __name__ == "__main__":
    from models import Node, DAG
else:
    from .models import Node, DAG

# get [mean, stdev] and return mean +- stdev random number
def randuniform(arr):
    if arr[1] < 0:
        raise ValueError('should pass positive stdev : %d, %d' % (arr[0], arr[1]))

    return randint(int(arr[0] - arr[1]), int(arr[0] + arr[1]))

def randarr(arr):
    return arr[randint(0, len(arr)-1)]

def argmax(value_list, index_list=None):
    if index_list is None :
        index_list = list(range(len(value_list)))
    max_index, max_value = index_list[0], value_list[index_list[0]]
    for i in index_list :
        if value_list[i] > max_value :
            max_index = i
            max_value = value_list[i]
    return max_index

def calculate_critical_path(dag):
    distance = [0,] * len(dag.node_set)
    indegree = [0,] * len(dag.node_set)
    task_queue = []

    for i in range(len(dag.node_set)) :
        if len(dag.node_set[i].pred) == 0 :
            task_queue.append(dag.node_set[i])
            distance[i] = dag.node_set[i].exec_t

    for i, v in enumerate(dag.node_set):
        indegree[i] = len(v.pred)

    while task_queue :
        vertex = task_queue.pop(0)
        for v in vertex.succ :
            distance[v] = max(dag.node_set[v].exec_t + distance[vertex.tid], distance[v]) 
            indegree[v] -= 1
            if indegree[v] == 0 :
                task_queue.append(dag.node_set[v])

    cp = []
    cv = argmax(distance)

    while True :
        cp.append(cv)
        if len(dag.node_set[cv].pred) == 0 :
            break
        cv = argmax(distance, dag.node_set[cv].pred)
    
    cp.reverse()
    return cp

def generate_random_dag(**kwargs):
    node_num = randuniform(kwargs.get('node_num', [20, 3]))
    depth = randuniform(kwargs.get('depth', [3.5, 0.5]))
    _exec_t = kwargs.get('exec_t', [50.0, 30.0])
    start_node_num = randuniform(kwargs.get('start_node_num', [1, 0]))
    end_node_num = randuniform(kwargs.get('end_node_num', [1, 0]))
    _extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)
    _dangling_node_ratio = kwargs.get('dangling_node_ratio', 0.2)

    dag = DAG()

    ### 1. Initialize node
    for i in range(node_num):
        node_param = {
            "name" : "node" + str(i)
        }

        dag.node_set.append(Node(**node_param))

    extra_arc_num = int(node_num * _extra_arc_ratio)
    
    ### 2. Classify node by randomly-select level
    level_arr = []
    for i in range(depth):
        level_arr.append([])

    # assign each level's node number
    level_node_num_arr = [1 for _ in range(depth)]
    level_node_num_arr[0] = start_node_num
    level_node_num_arr[-1] = end_node_num

    while sum(level_node_num_arr) < node_num:
        level = randint(1, depth-2)
        level_node_num_arr[level] += 1
    
    # put nodes in order of index
    idx = 0
    for level in range(depth):
        while len(level_arr[level]) < level_node_num_arr[level]:
            level_arr[level].append(idx)
            dag.node_set[idx].level = level
            idx += 1

    dag.start_node_idx = level_arr[0]

    for node_idx in level_arr[-1]:
        dag.node_set[node_idx].isLeaf = True

    ### 3. Assign critical path, dangling nodes
    # Add edge for critical path
    for level in range(len(level_arr)):
        dag.critical_path.append(randarr(level_arr[level]))
    
    for idx in range(len(dag.critical_path)-1):
        pred_node = dag.node_set[dag.critical_path[idx]]
        succ_node = dag.node_set[dag.critical_path[idx+1]]
        pred_node.succ.append(dag.critical_path[idx+1])
        succ_node.pred.append(dag.critical_path[idx])

    # Assign dangling nodes 

    dangling_node_num = round(node_num * _dangling_node_ratio)
    average_width = math.ceil(node_num / depth)
    dangling_len = math.ceil(dangling_node_num / average_width * 1.5)

    while min(math.ceil(depth/2), depth - dangling_len - 2) < 1:
        dangling_len -= 1

    start_level = randint(1, min(math.ceil(depth/2), depth - dangling_len - 2))
    end_level = start_level + dangling_len

    # Assign self-looping node
    sl_node_idx = dag.critical_path[start_level]
    dag.sl_node_idx = sl_node_idx

    dangling_dag = [sl_node_idx]
    dangling_level_dag = [[sl_node_idx]]
    
    for level in range(start_level+1, end_level+1):
        dangling_dag.append(dag.critical_path[level])
        dangling_level_dag.append([dag.critical_path[level]])

    failCnt = 0
    while len(dangling_dag) < dangling_node_num and failCnt < 10:
        level = randint(start_level+1, end_level)
        new_node = randarr(level_arr[level])
        if new_node not in dangling_level_dag[level - start_level]:
            dangling_dag.append(new_node)
            dangling_level_dag[level - start_level].append(new_node)
            failCnt = 0
        else:
            failCnt += 1

    # Make arc among dangling nodes
    for level in range(dangling_len, 0, -1):
        for succ_idx in dangling_level_dag[level]:
            succ_node = dag.node_set[succ_idx]
            if len(succ_node.pred) == 0:
                pred_idx = randarr(dangling_level_dag[level-1])
                pred_node = dag.node_set[pred_idx]
                succ_node.pred.append(pred_idx)
                pred_node.succ.append(succ_idx)

    dag.dangling_idx = dangling_dag

    ### 4. Make arc
    # make arc from last level
    for level in range(depth-1, 0, -1):
        for node_idx in level_arr[level]:
            if len(dag.node_set[node_idx].pred) == 0 :
                pred_idx = randarr(level_arr[level-1])
                dag.node_set[pred_idx].succ.append(node_idx)
                dag.node_set[node_idx].pred.append(pred_idx)

    # make sure all node have succ except sink node
    for level in range(0, depth-1):
        for node_idx in level_arr[level]:
            if len(dag.node_set[node_idx].succ) == 0 :
                succ_idx = level_arr[level+1][randint(0, len(level_arr[level+1])-1)]
                dag.node_set[node_idx].succ.append(succ_idx)
                dag.node_set[succ_idx].pred.append(node_idx)

    # make extra arc
    for i in range(extra_arc_num):
        arc_added_flag = False
        failCnt = 0
        while not arc_added_flag and failCnt < 10:
            node1_idx = randint(0, node_num-2)
            node2_idx = randint(0, node_num-2)

            if dag.node_set[node1_idx].level < dag.node_set[node2_idx].level and node2_idx not in dag.node_set[node1_idx].succ:
                dag.node_set[node1_idx].succ.append(node2_idx)
                dag.node_set[node2_idx].pred.append(node1_idx)
                arc_added_flag = True
            elif dag.node_set[node1_idx].level > dag.node_set[node2_idx].level and node1_idx not in dag.node_set[node2_idx].succ:
                dag.node_set[node2_idx].succ.append(node1_idx)
                dag.node_set[node1_idx].pred.append(node2_idx)
                arc_added_flag = True
            else:
                failCnt += 1

    ### 5. Make critical path's length longest
    exec_t_arr = [randuniform(_exec_t) for _ in range(node_num)]
    exec_t_arr.sort()
    critical_list = [i for i in range(node_num) if i in dag.critical_path]
    non_critical_list = [i for i in range(node_num) if i not in dag.critical_path]
    shuffle(critical_list)
    shuffle(non_critical_list)

    for i in range(node_num):
        dag.node_set[(non_critical_list + critical_list)[i]].exec_t = exec_t_arr[i]

    # sort index
    for node in dag.node_set:
        node.succ.sort()
        node.pred.sort()

    ### 5. Saving DAG info
    # dag.dict["isBackup"] = False
    dag.dict["node_num"] = node_num
    dag.dict["start_node_idx"] = dag.start_node_idx
    dag.dict["sl_node_idx"] = dag.sl_node_idx
    dag.dict["dangling_idx"] = dag.dangling_idx
    dag.dict["critical_path"] = dag.critical_path
    dag.dict["exec_t"] = [node.exec_t for node in dag.node_set]
    adj_matrix = []
    
    for node in dag.node_set:
        adj_row = [0 for _ in range(node_num)]
        for succ_idx in node.succ:
            adj_row[succ_idx] = 1
        
        adj_matrix.append(adj_row)
    
    dag.dict["adj_matrix"] = adj_matrix

    return dag

def generate_from_dict(dict):
    dag = DAG()
    dag.dict = dict
    node_num = dict["node_num"]

    ### 1. Initialize node
    for i in range(node_num):
        node_param = {
            "name" : "node" + str(i),
            "exec_t" : dict["exec_t"][i]
        }

        dag.node_set.append(Node(**node_param))

    dag.start_node_idx = dict["start_node_idx"]
    dag.critical_path = dict["critical_path"]
    dag.sl_node_idx = dict["sl_node_idx"]
    dag.dangling_idx = dict["dangling_idx"]

    for pred_idx in range(node_num):
        for succ_idx in range(node_num):
            if dict["adj_matrix"][pred_idx][succ_idx] == 1:
                dag.node_set[pred_idx].succ.append(succ_idx)
                dag.node_set[succ_idx].pred.append(pred_idx)

    for node in dag.node_set:
        if len(node.succ) == 0:
            node.isLeaf = True

    return dag

def export_dag_file(dag, file_name):
    with open(file_name, 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow([dag.dict["node_num"]])
        wr.writerow(dag.dict["start_node_idx"])
        wr.writerow([dag.dict["sl_node_idx"]])
        wr.writerow(dag.dict["dangling_idx"])
        wr.writerow(dag.dict["critical_path"])
        wr.writerow(dag.dict["exec_t"])
        wr.writerows(dag.dict["adj_matrix"])

def generate_backup_dag_dict(dict, backup_ratio):
    backup_dict = {}

    dangling_idx = dict["dangling_idx"]
    sl_node_idx = dict["sl_node_idx"]
    dangling_idx.remove(sl_node_idx)
    node_list = [i for i in range(dict["node_num"]+1) if i not in dangling_idx]
    # last node is backup_node

    node_num = len(node_list)
    backup_dict["node_num"] = node_num
    backup_dict["start_node_idx"] = dict["start_node_idx"]
    backup_dict["sl_node_idx"] = dict["sl_node_idx"]
    backup_dict["dangling_idx"] = [dict["sl_node_idx"]]

    backup_dict["critical_path"] = [i for i in dict["critical_path"] if i not in dangling_idx]
    backup_dict["critical_path"].append(dict["node_num"])

    # Calculate backup node execution time
    backup_exec_t = 0
    for idx in dangling_idx:
        backup_exec_t += dict["exec_t"][idx]
    backup_exec_t = round(backup_exec_t * backup_ratio)

    exec_t_arr = []
    for idx in node_list[:-1]:
        exec_t_arr.append(dict["exec_t"][idx])
    exec_t_arr.append(backup_exec_t)

    backup_dict["exec_t"] = exec_t_arr

    # Regenerate adj matrix
    adj_matrix = []
    for _ in range(node_num):
        adj_matrix.append([0, ] * node_num)

    for pred_idx in range(dict["node_num"]):
        for succ_idx in range(dict["node_num"]):
            if dict["adj_matrix"][pred_idx][succ_idx] == 1:
                new_p_idx = pred_idx
                new_c_idx = succ_idx
                if pred_idx in dangling_idx:
                    new_p_idx = dict["node_num"]
                if succ_idx in dangling_idx:
                    new_c_idx = dict["node_num"]
                
                if new_p_idx != new_c_idx:
                    i = node_list.index(new_p_idx)
                    j = node_list.index(new_c_idx)
                    adj_matrix[i][j] = 1
    
    backup_dict["adj_matrix"] = adj_matrix

    return backup_dict

if __name__ == "__main__":
    dag_param_1 = {
        "node_num" : [10, 0],
        "depth" : [4.5, 0.5],
        "exec_t" : [50.0, 30.0],
        "start_node" : [1, 0],
        "end_node" : [1, 0],
        "extra_arc_ratio" : 0.1,
        "dangling_node_ratio" : 0.2,
    }

    dag_param_2 = {
        "node_num" : [40, 5],
        "depth" : [5.5, 1.5],
        "exec_t" : [50.0, 30.0],
        "start_node" : [1, 0],
        "end_node" : [1, 0],
        "extra_arc_ratio" : 0.1,
        "dangling_node_ratio" : 0.2,
    }

    dag = generate_random_dag(**dag_param_1)
    dag2 = generate_from_dict(dag.dict)

    export_dag_file(dag2, 'hi.csv')

    with open('hi.csv', 'r', newline='') as f:
        rd = csv.reader(f)
        dag_dict = {}

        dag_dict["node_num"] = int(next(rd)[0])
        dag_dict["start_node_idx"] = [int(e) for e in next(rd)]
        dag_dict["sl_node_idx"] = int(next(rd)[0])
        dag_dict["dangling_idx"] = [int(e) for e in next(rd)]
        dag_dict["critical_path"] = [int(e) for e in next(rd)]
        dag_dict["exec_t"] = [int(e) for e in next(rd)]
        adj = []
        for line in rd:
            adj.append([int(e) for e in line])
        dag_dict["adj_matrix"] = adj

        dag3 = generate_from_dict(dag_dict)

    print(dag)
    print(dag3)

