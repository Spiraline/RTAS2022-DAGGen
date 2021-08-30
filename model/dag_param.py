from random import randint
from .model import Node, DAG

# get [mean, stdev] and return mean +- stdev random number
def rand_uniform(arr):
    if arr[1] < 0:
        raise ValueError('should pass positive stdev : %d, %d' % (arr[0], arr[1]))

    return randint(int(arr[0] - arr[1]), int(arr[0] + arr[1]))

def generate_random_dag(kwargs):
    node_num = rand_uniform(kwargs.get('node_num', [10, 3]))
    depth = rand_uniform(kwargs.get('depth', [3.5, 0.5]))
    _exec_t = kwargs.get('exec_t', [50.0, 30.0])
    start_node_num = rand_uniform(kwargs.get('start_node_num', [1, 0]))
    end_node_num = rand_uniform(kwargs.get('end_node_num', [1, 0]))
    _extra_arc_ratio = kwargs.get('extra_arc_ratio', 0.1)

    dag = DAG()

    ### 1. Initialize node
    for i in range(node_num):
        node_param = {
            "name" : "node" + str(i),
            "exec_t" : rand_uniform(_exec_t)
        }

        dag.node_set.append(Node(**node_param))

    extra_arc_num = int(node_num * _extra_arc_ratio)
    
    ### 2. Classify node by randomly-select level
    level_arr = []
    for i in range(depth):
        level_arr.append([])
    
    # put start nodes in level 0 (source node)
    for i in range(start_node_num):
        level_arr[0].append(i)
        dag.node_set[i].level = 0

    # put end nodes in level depth-1 (sink node)
    for i in range(node_num-1, node_num-end_node_num-1, -1):
        level_arr[-1].append(i)
        dag.node_set[i].level = depth-1

    # Each level must have at least one node
        for i in range(1, depth-1):
            level_arr[i].append(start_node_num + i - 1)
            dag.node_set[start_node_num + i - 1].level = i

    # put other nodes in other level randomly
        for i in range(start_node_num+depth-2, node_num-end_node_num):
            level = randint(1, depth-2)
            dag.node_set[i].level = level
            level_arr[level].append(i)

    ## 3. Make arc
    ### make arc from last level
    for level in range(depth-1, 0, -1):
        for node_idx in level_arr[level]:
            parent_idx = level_arr[level-1][randint(0, len(level_arr[level - 1])-1)]

            dag.node_set[parent_idx].child.append(node_idx)
            dag.node_set[node_idx].parent.append(parent_idx)

    ### make sure all node have child except sink node
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

    ### make extra arc
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

    for node in dag.node_set:
        node.child.sort()
        node.parent.sort()

def generate_from_file(dict):
    pass

def export_dag_dict(dag):
    pass

def export_dag_file(dag):
    pass



if __name__ == "__main__":
    dag_param_1 = {
        "node_num" : [20, 0],
        "depth" : [4.5, 0.5],
        "exec_t" : [50.0, 30.0],
        "start_node" : [2, 1],
        "extra_arc_ratio" : 0.4
    }

    dag_param_2 = {
        "node_num" : [20, 0],
        "depth" : [4.5, 0.5],
        "exec_t" : [50.0, 30.0],
        "start_node" : [2, 0],
        "edge_constraint" : True,
        "outbound_num" : [2, 0]
    }

    dag = generate_random_dag(**dag_param_1)

    print(dag)

