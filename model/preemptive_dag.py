from random import randint, shuffle, choice
import math
import csv
from collections import deque

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
    ready_queue = []
    is_complete = [False, ] * len(dag.node_set)
    longest = {}
    max_len = {}

    for node in dag.node_set:
        if len(node.pred) == 0:
            is_complete[node.tid] = True
            longest[node.tid] = [node.tid]
            max_len[node.tid] = node.exec_t

            for succ_idx in node.succ:
                if is_complete[succ_idx]:
                    isReady = False
                else:
                    isReady = True
                for pred_idx in dag.node_set[succ_idx].pred:
                    if not is_complete[pred_idx]:
                        isReady = False
            
                if isReady:
                    ready_queue.append(dag.node_set[succ_idx])
    
    while False in is_complete:
        node = ready_queue.pop()
        longest_idx = node.pred[0]
        longest_len = max_len[node.pred[0]]
        for pred_idx in node.pred[1:]:
            if longest_len < max_len[pred_idx]:
                longest_idx = pred_idx
                longest_len = max_len[pred_idx]
        
        longest[node.tid] = longest[longest_idx] + [node.tid]
        max_len[node.tid] = max_len[longest_idx] + node.exec_t

        is_complete[node.tid] = True

        for succ_idx in node.succ:
            if is_complete[succ_idx]:
                isReady = False
            else:
                isReady = True
            for pred_idx in dag.node_set[succ_idx].pred:
                if not is_complete[pred_idx]:
                    isReady = False
        
            if isReady:
                ready_queue.append(dag.node_set[succ_idx])

    longest_idx = argmax(max_len)
    return longest[longest_idx]

def assign_random_priority(dag):
    priority = [i for i in range(len(dag.node_set))]
    shuffle(priority)
    for idx, p in enumerate(priority):
        dag.node_set[idx].priority = p
    
    return priority

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
            "name" : "node" + str(i),
            "exec_t": randuniform(_exec_t)
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

    Q = deque()
    rev_Q = deque()

    for node_idx in dag.start_node_idx:
        Q.append(node_idx)

    for node_idx in level_arr[-1]:
        dag.node_set[node_idx].isLeaf = True
        rev_Q.append(node_idx)

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

    # sort index
    for node in dag.node_set:
        node.succ.sort()
        node.pred.sort()

    # Assign self-looping node and dangling nodes
    dag.sl_node_idx = randint(0, node_num-1)
    dangling_node_num = round(node_num * _dangling_node_ratio)
    dan_Q = deque([dag.sl_node_idx])
    while dan_Q and len(dag.dangling_idx) < dangling_node_num:
        node_idx = dan_Q.popleft()
        if dag.node_set[node_idx].isLeaf:
            break
        else:
            for succ_idx in dag.node_set[node_idx].succ:
                if succ_idx not in dag.dangling_idx:
                    dag.dangling_idx.append(succ_idx)
                    dan_Q.append(succ_idx)

    # calculate est (earliest start time)
    while Q:
        node_idx = Q.popleft()
        node = dag.node_set[node_idx]
        if len(node.pred) == 0:
            node.est = 0
        else:
            est = 0
            for pred_idx in node.pred:
                if dag.node_set[pred_idx].est + dag.node_set[pred_idx].exec_t > est:
                    est = dag.node_set[pred_idx].est + dag.node_set[pred_idx].exec_t
            node.est = est
        
        for succ_idx in node.succ:
            if dag.node_set[succ_idx].est >= 0:
                continue
            shouldAdd = True
            for succ_pred_idx in dag.node_set[succ_idx].pred:
                if dag.node_set[succ_pred_idx].est == -1:
                    shouldAdd = False
                    break
            if shouldAdd:
                Q.append(succ_idx)

    # calculate ltc (least time to completion)
    while rev_Q:
        node_idx = rev_Q.popleft()
        node = dag.node_set[node_idx]
        if len(node.succ) == 0:
            node.ltc = 0
        else:
            ltc = 0
            for succ_idx in node.succ:
                if dag.node_set[succ_idx].ltc + dag.node_set[succ_idx].exec_t > ltc:
                    ltc = dag.node_set[succ_idx].ltc + dag.node_set[succ_idx].exec_t
            node.ltc = ltc
        
        for pred_idx in node.pred:
            if dag.node_set[pred_idx].ltc >= 0:
                continue
            shouldAdd = True
            for pred_succ_idx in dag.node_set[pred_idx].succ:
                if dag.node_set[pred_succ_idx].ltc == -1:
                    shouldAdd = False
                    break
            if shouldAdd:
                rev_Q.append(pred_idx)

    ### 5. Saving DAG info
    # dag.dict["isBackup"] = False
    dag.dict["node_num"] = node_num
    dag.dict["start_node_idx"] = dag.start_node_idx
    dag.dict["dangling_idx"] = dag.dangling_idx
    dag.dict["sl_node_idx"] = dag.sl_node_idx
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

def generate_backup_dag(dict, backup_ratio=0.5):
    backup_dict = {}

    dangling_idx = dict["dangling_idx"]

    # last node is backup_node
    node_list = [i for i in range(dict["node_num"]+1) if i not in dangling_idx]

    # remove cycle node (dangling -> A -> dangling)
    has_cycle = []
    for node_idx in node_list[:-1]:
        exist_outcoming = exist_incoming = False
        for dang_idx in dangling_idx:
            if dict["adj_matrix"][node_idx][dang_idx] == 1:
                exist_outcoming = True
            if dict["adj_matrix"][dang_idx][node_idx] == 1:
                exist_incoming = True
        
        if exist_incoming and exist_outcoming:
            has_cycle.append(node_idx)
    
    for node_idx in has_cycle:
        node_list.remove(node_idx)

    node_num = len(node_list)
    backup_dict["node_num"] = node_num
    backup_dict["start_node_idx"] = dict["start_node_idx"]
    backup_dict["sl_node_idx"] = dict["sl_node_idx"]
    backup_dict["dangling_idx"] = []

    # Calculate backup node execution time
    backup_exec_t = 0
    if "backup_exec_t" in dict:
        backup_exec_t = dict["backup_exec_t"]
    else:
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
                
                if new_p_idx != new_c_idx and new_p_idx in node_list and new_c_idx in node_list:
                    i = node_list.index(new_p_idx)
                    j = node_list.index(new_c_idx)

                    # check if there 
                    adj_matrix[i][j] = 1
    
    backup_dict["adj_matrix"] = adj_matrix

    backup_dag = generate_from_dict(backup_dict)

    backup_dag.dict["backup_exec_t"] = backup_exec_t

    # Calculate est, lst
    Q = deque()
    rev_Q = deque()

    for node_idx, node in enumerate(backup_dag.node_set):
        if not node.pred:
            Q.append(node_idx)
        if not node.succ:
            rev_Q.append(node_idx)

    # calculate est (earliest start time)
    while Q:
        node_idx = Q.popleft()
        node = backup_dag.node_set[node_idx]
        if len(node.pred) == 0:
            node.est = 0
        else:
            est = 0
            for pred_idx in node.pred:
                if backup_dag.node_set[pred_idx].est + backup_dag.node_set[pred_idx].exec_t > est:
                    est = backup_dag.node_set[pred_idx].est + backup_dag.node_set[pred_idx].exec_t
            node.est = est
        
        for succ_idx in node.succ:
            if backup_dag.node_set[succ_idx].est >= 0:
                continue
            shouldAdd = True
            for succ_pred_idx in backup_dag.node_set[succ_idx].pred:
                if backup_dag.node_set[succ_pred_idx].est == -1:
                    shouldAdd = False
                    break
            if shouldAdd:
                Q.append(succ_idx)

    # calculate ltc (least time to completion)
    while rev_Q:
        node_idx = rev_Q.popleft()
        node = backup_dag.node_set[node_idx]
        if len(node.succ) == 0:
            node.ltc = 0
        else:
            ltc = 0
            for succ_idx in node.succ:
                if backup_dag.node_set[succ_idx].ltc + backup_dag.node_set[succ_idx].exec_t > ltc:
                    ltc = backup_dag.node_set[succ_idx].ltc + backup_dag.node_set[succ_idx].exec_t
            node.ltc = ltc
        
        for pred_idx in node.pred:
            if backup_dag.node_set[pred_idx].ltc >= 0:
                continue
            shouldAdd = True
            for pred_succ_idx in backup_dag.node_set[pred_idx].succ:
                if backup_dag.node_set[pred_succ_idx].ltc == -1:
                    shouldAdd = False
                    break
            if shouldAdd:
                rev_Q.append(pred_idx)

    return backup_dag