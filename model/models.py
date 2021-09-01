class Node(object):
    idx = 0
    def __init__(self, **kwargs):
        self.tid = Node.idx
        Node.idx += 1
        self.name = kwargs.get('name', '')
        self.exec_t = kwargs.get('exec_t', 30.0)

        # Assigned after DAGGen
        self.pred = []
        self.succ = []
        self.isLeaf = False
        self.level = 0

        # Assigned after CPCGen
        self.priority = 0
        self.anc = []                                           # A list of v_j's ancestor nodes
        self.desc = []                                          # A list of v_j's descendent nodes
        self.C = []                                             # A list of nodes that can concurrently executes
        self.non_critical_group = []                            # Intersection of non critical nodes and concurrent nodes
        self.interference_group = []                            # A list of interfering nodes
        self.interference_group_priority = []                   # A list of interfering nodes considering priority

        self.priority = -1                                      # v_j's priority
        self.actual_delay = 0                                   # v_j's actual delay from interference group considering priority
        self.finish_time = -1

    def __str__(self):
        res = "%-9s %-3d %-5.1f %40s %40s" \
            % ('[' + self.name + ']', self.priority, self.exec_t, self.pred, self.succ)

        return res

    def new_task_set(self):
        Node.idx = 0

class DAG(object):
    def __init__(self, **kwargs):
        Node.idx = 0
        self.node_set = []
        self.start_node_idx = kwargs.get('start_node_idx', 0)
        self.critical_path = []
        self.sl_node_idx = kwargs.get('sl_node_idx', 0)
        self.dangling_idx = kwargs.get('dangling_idx', [])
        # For saving dag info
        self.dict = {}

    def __str__(self):
        print("%-9s %-3s %-5s %39s %40s" % ('name', 'pri', 'exec_t', 'pred node', 'succ node'))
        for node in self.node_set:
            print(node)
        
        return ''

class CPC(object):
    def __init__(self, **kwargs):
        self.node_set = []
        self.critical_path = []
        self.sl_node_idx = []
        self.provider_group = []
        self.F = []
        self.G = []
        self.core_num = kwargs.get('core_num', 4.0)
        self.res_t = []

    def __str__(self):
        print("%-9s %-3s %-5s %39s %40s" % ('name', 'pri', 'exec_t', 'pred node', 'succ node'))
        for task in self.node_set:
            print(task)

        print('provider : ', self.provider_group)
        print('F : ', self.F)
        print('G : ', self.G)
        
        return ''