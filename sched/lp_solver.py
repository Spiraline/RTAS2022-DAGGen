from ortools.linear_solver import pywraplp

def LP_solver(objective, constraint):
    # Instantiate a GLOP solver
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Create the variables and let them take on any non-negative value.
    x = [solver.NumVar(0, solver.infinity(), 'x' + str(i)) for i in range(len(objective))]

    # Constraints
    for coeff in constraint:
        eq = 0
        for i, x_i in enumerate(x):
            if coeff[i] != 0:
                eq += coeff[i] * x_i
        if coeff[-2] == 'ge':
            solver.Add(eq >= coeff[-1])
        elif coeff[-2] == 'le':
            solver.Add(eq <= coeff[-1])
        else:
            solver.Add(eq == coeff[-1])
    
    # print('Number of variables =', solver.NumVariables())
    # print('Number of constraints =', solver.NumConstraints())

    obj_eq = 0
    for i, x_i in enumerate(x):
        if objective[i] != 0:
            obj_eq += objective[i] * x_i

    solver.Maximize(obj_eq)

    # Solve the system.
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        pass
        # print('Solution:')
        # print('Objective value =', solver.Objective().Value())
        # for i, x_i in enumerate(x):
        #     print('x' + str(i), '=', x_i.solution_value())
    else:
        return []
        # print('The problem does not have an optimal solution.')

    # print('\nAdvanced usage:')
    # print('Problem solved in %f milliseconds' % solver.wall_time())
    # print('Problem solved in %d iterations' % solver.iterations())

    return [x_i.solution_value() for x_i in x]

def calculate_multiple_budget(dag, D, M):
    sl_num = len(dag.sl_nodes)
    node_num = len(dag.node_set)
    sl_dict = {}
    for idx, sl_idx in enumerate(dag.sl_nodes):
        sl_dict[sl_idx] = node_num + idx

    ### var
    # est(v_i), c(v_s), W, L
    # var #: sl_num + node_num + 2 (W, L)

    const_list = []
    leaf_node_idx = 0

    # est constraint
    for i, node in enumerate(dag.node_set):
        if len(node.succ) == 0:
            leaf_node_idx = i
        if len(node.pred) == 0:
            if i in sl_dict:
                continue
            const = [0] * (sl_num + node_num + 2)
            const[i] = 1
            const += ['eq', node.exec_t]
            const_list.append(const)
        else:
            for pred_idx in node.pred:
                const = [0] * (sl_num + node_num + 2)
                const[i] = 1
                const[pred_idx] = -1
                if pred_idx in sl_dict:
                    const[sl_dict[pred_idx]] = -1
                    const += ['ge', 0]
                else:
                    const += ['ge', dag.node_set[pred_idx].exec_t]
                const_list.append(const)

    # total work
    const = [0] * (sl_num + node_num + 2)
    W = sum([node.exec_t for node in dag.node_set if node.tid not in sl_dict])
    for i in range(sl_num):
        const[node_num + i] = -1
    const[-2] = 1
    const += ['eq', W]
    const_list.append(const)

    # span
    const = [0] * (sl_num + node_num + 2)
    const[-1] = 1
    const[leaf_node_idx] = -1
    const += ['ge', dag.node_set[leaf_node_idx].exec_t]
    const_list.append(const)
    
    # deadline
    const = [0] * (sl_num + node_num + 2)
    const[-2] = 1/M
    const[-1] = (1 - 1/M)
    const += ['le', D]
    const_list.append(const)

    ### Objective
    obj = [0] * (sl_num + node_num + 2)
    for i in range(sl_num):
        obj[node_num + i] = 1

    sol = LP_solver(obj, const_list)
    if len(sol) == 0:
        return []

    return [round(v) for v in sol[node_num:node_num+sl_num]]
        

if __name__ == "__main__":
    const = [[1, 2, 'le', 14], [3, -1, 'ge', 0], [1, -1, 'le', 2]]
    obj = [3, 4]
    LP_solver(obj, const)