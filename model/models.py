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

        self.est = -1
        self.ltc = -1

        # Assigned after CPCGen
        self.priority = -1                          # v_j's priority
        self.anc = []                               # A list of v_j's ancestor nodes
        self.desc = []                              # A list of v_j's descendent nodes
        self.C = []                                 # A list of nodes that can concurrently executes
        
        # Assigned after CPC budget analysis
        self.I = []                                 # A list of interfering nodes
        self.I_e = []                               # A list of interfering nodes considering priority
        self.f_t = -1

        self.actual_delay = 0                       # v_j's actual delay from interference group considering priority

    def __str__(self):
        res = "%-9s %-3d %-4d %40s %40s %4d %40s %40s %4d %4d" \
            % ('[' + self.name + ']', self.priority, self.exec_t, self.pred, self.succ,
                self.f_t, self.I, self.I_e, self.est, self.ltc)

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
        print("%-9s %-3s %-5s %38s %40s %4s %40s %40s" % ('name', 'pri', 'exec_t', 'pred node', 'succ node', 'f_t', 'I', 'I_e'))
        for node in self.node_set:
            print(node)

        print('critical path : ', self.critical_path)
        print('sl_node : ', self.sl_node_idx)
        print('dangling : ', self.dangling_idx)
        
        return ''

class CPC(object):
    def __init__(self, **kwargs):
        self.node_set = []
        self.core_num = kwargs.get('core_num', 4.0)
        self.critical_path = []
        self.sl_node_idx = []
        self.provider_group = []
        self.F = []
        self.G = []
        self.beta = []
        self.lambda_v_e = []
        self.res_t = []

    def __str__(self):
        print("%-9s %-3s %-5s %38s %40s %4s %40s %40s %4d %4d" % ('name', 'pri', 'exec_t', 'pred node', 'succ node', 'f_t', 'I', 'I_e', 'est', 'ltc'))
        for task in self.node_set:
            print(task)

        print('provider : ', self.provider_group)
        print('F : ', self.F)
        print('beta : ', self.beta)
        print('res_t : ', self.res_t)
        print('lambda_v_e : ', self.lambda_v_e)
        
        return ''