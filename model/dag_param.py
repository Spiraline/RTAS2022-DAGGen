from random import randint
from models import Node, DAG
import math

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
    max_index, max_value = [index_list[0], value_list[index_list[0]]]
    for i in index_list :
        if value_list[i] > max_value :
            max_index = i
            max_value = value_list[i]
    return max_index

def calculate_critical_path(dag):
    distance = [0,] * len(dag.node_set)
    indegree = [0,] * len(dag.node_set)
    node_queue = []
    for i in range(len(dag.node_set)):
        if dag.node_set[i].level == 0:
            node_queue.append(dag.node_set[i])
            distance[i] = dag.node_set[i].exec_t

    for i, v in enumerate(dag.node_set):
        indegree[i] = len(v.parent)

    while node_queue:
        vertex = node_queue.pop(0)
        for v in vertex.child:
            distance[v] = max(dag.node_set[v].exec_t + distance[vertex.tid], distance[v]) 
            indegree[v] -= 1
            if indegree[v] == 0:
                node_queue.append(dag.node_set[v])

    cp = []
    cv = argmax(distance)

    while True :
        cp.append(cv)
        if len(dag.node_set[cv].parent) == 0 :
            break
        cv = argmax(distance, dag.node_set[cv].parent)

    cp.reverse()
    return cp

def assign_looping(dag, critical_path, dangling_num):
    dangling_len = math.ceil(dangling_num / 3)
    sl_node_idx_in_cp = randint(1, len(critical_path)/2)

    start_idx = critical_path[sl_node_idx_in_cp]
    end_idx = critical_path[sl_node_idx_in_cp + dangling_len - 1]





    dangling_node = []

    dag.sl_node_idx = sl_node_idx
    dag.dangling_idx = dangling_node

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
            "exec_t" : randuniform(_exec_t)
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

    ### 3. Assign critical path, dangling nodes
    # Add edge for critical path
    for level in range(len(level_arr)):
        dag.critical_path.append(randarr(level_arr[level]))

    print(dag.critical_path)
    
    for idx in range(len(dag.critical_path)-1):
        parent_node = dag.node_set[dag.critical_path[idx]]
        child_node = dag.node_set[dag.critical_path[idx+1]]
        parent_node.child.append(dag.critical_path[idx+1])
        child_node.parent.append(dag.critical_path[idx])

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

    print(dangling_level_dag)

    # Make arc among dangling nodes
    for level in range(dangling_len, 0, -1):
        for child_idx in dangling_level_dag[level]:
            child_node = dag.node_set[child_idx]
            if len(child_node.parent) == 0:
                parent_idx = randarr(dangling_level_dag[level-1])
                parent_node = dag.node_set[parent_idx]
                child_node.parent.append(parent_idx)
                parent_node.child.append(child_idx)

    ### 3. Make arc
    # make arc from last level
    for level in range(depth-1, 0, -1):
        for node_idx in level_arr[level]:
            if node_idx not in dangling_dag:
                parent_idx = randarr(level_arr[level-1])
                dag.node_set[parent_idx].child.append(node_idx)
                dag.node_set[node_idx].parent.append(parent_idx)

    # make sure all node have child except sink node
    for level in range(0, depth-1):
        for node_idx in level_arr[level]:
            if len(dag.node_set[node_idx].child) == 0 :
                child_idx = level_arr[level+1][randint(0, len(level_arr[level+1])-1)]
                dag.node_set[node_idx].child.append(child_idx)
                dag.node_set[child_idx].parent.append(node_idx)

    for node_idx in level_arr[depth-1] :
        if len(dag.node_set[node_idx].parent) == 0 :
            parent_idx = level_arr[depth-2][randint(0, len(level_arr[depth-2])-1)]
            dag.node_set[parent_idx].child.append(node_idx)
            dag.node_set[node_idx].parent.append(parent_idx)

    # make extra arc
    for i in range(extra_arc_num):
        arc_added_flag = False
        failCnt = 0
        while not arc_added_flag and failCnt < 10:
            node1_idx = randint(0, node_num-2)
            node2_idx = randint(0, node_num-2)

            if dag.node_set[node1_idx].level < dag.node_set[node2_idx].level and node2_idx not in dag.node_set[node1_idx].child:
                dag.node_set[node1_idx].child.append(node2_idx)
                dag.node_set[node2_idx].parent.append(node1_idx)
                arc_added_flag = True
            elif dag.node_set[node1_idx].level > dag.node_set[node2_idx].level and node1_idx not in dag.node_set[node2_idx].child:
                dag.node_set[node2_idx].child.append(node1_idx)
                dag.node_set[node1_idx].parent.append(node2_idx)
                arc_added_flag = True
            
            failCnt += 1

    # sort index
    for node in dag.node_set:
        node.child.sort()
        node.parent.sort()

    ### 5. Saving DAG info

    return dag

def generate_from_file(dict):
    pass

def export_dag_dict(dag):
    pass

def export_dag_file(dag):
    pass

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

    print(dag)
    # print(cp)

