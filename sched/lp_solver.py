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
        else:
            solver.Add(eq <= coeff[-1])
    
    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())

    obj_eq = 0
    for i, x_i in enumerate(x):
        if objective[i] != 0:
            obj_eq += objective[i] * x_i

    solver.Maximize(obj_eq)

    # Solve the system.
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())
        for i, x_i in enumerate(x):
            print('x' + str(i), '=', x_i.solution_value())
    else:
        print('The problem does not have an optimal solution.')

    print('\nAdvanced usage:')
    print('Problem solved in %f milliseconds' % solver.wall_time())
    print('Problem solved in %d iterations' % solver.iterations())

if __name__ == "__main__":
    const = [[1, 2, 'le', 14], [3, -1, 'ge', 0], [1, -1, 'le', 2]]
    obj = [3, 4]
    LP_solver(obj, const)