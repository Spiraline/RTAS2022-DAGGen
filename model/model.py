class Node(object):
    idx = 0
    def __init__(self, **kwargs):
        self.tid = Node.idx
        Node.idx += 1
        self.name = kwargs.get('name', '')
        self.exec_t = kwargs.get('exec_t', 30.0)

        # Assigned after DAGGen
        self.parent = []
        self.child = []
        self.isLeaf = False
        self.deadline = -1
        self.level = 0

        # Assigned after CPCGen
        self.priority = 0

    def __str__(self):
        res = "%-9s %-5.1f %40s %40s" \
            % ('[' + self.name + ']', self.exec_t, self.parent, self.child)

        if self.isLeaf:
            res += "%7s" % (self.deadline)
        else:
            res += "   ---  "

        return res

    def new_task_set(self):
        Node.idx = 0

class DAG(object):
    def __init__(self, **kwargs):
        self.task_set = []
        self.start_node = kwargs.get('start_node', [2, 1])
        self.sl_idx = kwargs.get('sl_idx', 0)
        self.dangling_idx = kwargs.get('dangling_idx', [])

    def __str__(self):
        print("%-9s %-5s %39s %40s %8s" % ('name', 'exec_t', 'parent node', 'child node', 'deadline'))
        for task in self.task_set:
            print(task)
        
        return ''

class CPC(object):
    def __init__(self, **kwargs):
        self.task_set = []
        self.start_node = kwargs.get('start_node', [2, 1])
        self.sl_idx = kwargs.get('sl_idx', 0)
        self.dangling_idx = kwargs.get('dangling_idx', [])

    def __str__(self):
        print("%-9s %-5s %39s %40s %8s" % ('name', 'exec_t', 'parent node', 'child node', 'deadline'))
        for task in self.task_set:
            print(task)
        
        return ''