from pysmt.shortcuts import Symbol, And, GE, LE, Ite, Or, Equals, Solver, AllDifferent, Int, Implies
from pysmt.typing import INT
import utils
import os
import time


def cumulative(start, duration, resources, total):
    decomposition = []
    for r in resources:
        decomposition.append(sum([Ite(And(start[i] <= Int(r), Int(r) < start[i] + Int(duration[i])), Int(resources[i]), Int(0)) for i in range(len(start))]) <= (Int(total)) )
    return decomposition

def solve_problem(input_file, out_dir, fig_dir, instance_name, solver_name, symmetry = True, timeout = 300):
    width, n_circuits, x, y, l_min, l_max, index_max_area, circuits = utils.read_file(input_file)
    out_file = os.path.join(out_dir, str(instance_name) + '-out.txt')
    fig_path = os.path.join(fig_dir, str(instance_name) + '-fig.png')

    # definition of variables
    x_pos = [Symbol(f"x_pos_{str(i+1)}", INT) for i in range(n_circuits)]
    y_pos = [Symbol(f'y_pos{str(i+1)}', INT) for i in range(n_circuits)]

    l_goal = Symbol('Length', INT)

    x_domain = [And(GE(x_pos[i], Int(0)), LE(x_pos[i], Int(width) - Int(min(x)))) for i in range(n_circuits)]
    y_domain = [And(GE(y_pos[i], Int(0)), LE(y_pos[i], Int(l_max) - Int(min(y)))) for i in range(n_circuits)]

    l_goal_domain = And(GE(l_goal, Int(l_min)), LE(l_goal, Int(l_max)))

    limit_constraint_x = [LE(Int(x[i]) + x_pos[i], Int(width)) for i in range(n_circuits)]
    limit_constraint_y = [LE(Int(y[i]) + y_pos[i], l_goal) for i in range(n_circuits)]

    overlapping_constraints = []

    for i in range(n_circuits):
        for j in range(n_circuits):
            if i < j:
                overlapping_constraints.append(Or(LE(x_pos[i] + x[i], x_pos[j]),
                                                  LE(x_pos[j] + x[j], x_pos[i]),
                                                  LE(y_pos[i] + y[i], y_pos[j]),
                                                  LE(y_pos[j] + y[j], y_pos[i])))

    symmetry_constraints = []
    if symmetry:
        symmetry_constraints.append(And(Equals(x_pos[index_max_area], Int(0)), Equals(y_pos[index_max_area], Int(0))))
        for i in range(n_circuits):
            for j in range(n_circuits -1):

                symmetry_constraints.append(Implies(And(Equals(Int(x[i]),Int(x[j])), Equals(Int(y[i]),Int(y[j]))),
                                     Or(GE(x_pos[j],x_pos[i]),
                                        And(Equals(x_pos[j], x_pos[i]),
                                            GE(y_pos[j], y_pos[i])))))


    cumulative_x = cumulative(x_pos, x, y, l_max)
    cumulative_y = cumulative(y_pos, y, x, width)

    domains = And(*y_domain, *x_domain, l_goal_domain, *limit_constraint_x, *limit_constraint_y, *cumulative_x, *cumulative_y, *overlapping_constraints, *symmetry_constraints)
    k = l_min
    problem = Equals(l_goal, Int(k))
    formula = And(domains, problem)

    start_time = time.time()
    with Solver(name = 'z3', solver_options= {'timeout':timeout*1000, 'auto_config':True} ) as solver:
        solver.add_assertion(formula)
        try:
            while not solver.is_sat(formula):
                k += 1
                problem = (Equals(l_goal, Int(k)))
                formula = And(problem, domains)
                solver.reset_assertions()
                solver.add_assertion(formula)
            if solver.solve():
                model = solver.get_model()
                final_length = model.get_value(l_goal).constant_value()
        except:
            print('no solution')
            return
    t = time.time() - start_time
    get_solution(t, n_circuits, model, x_pos, y_pos, width, x, y, final_length, instance_name, l_max, out_file,
                 l_goal, circuits, fig_path)
    return

def get_solution(t, n_circuits,model,x_pos, y_pos, width, x, y, final_length, instance_name, l_max, out_file, l_goal, circuits, fig_path):

    x_sol = []
    y_sol = []

    solution = {}

    for i in range(n_circuits):
        x_sol.append(model.get_value(x_pos[i]).constant_value())
        y_sol.append(model.get_value(y_pos[i]).constant_value())
    corners = []
    for i in range(0, len(x_sol)):
        corners.append([model.get_value(x_pos[i]).constant_value(), model.get_value(y_pos[i]).constant_value()])
    solution['corners'] = corners
    utils.write_file(width, n_circuits, x, y, corners, final_length, instance_name, l_max, out_file, t, status=1)
    utils.plot_solution(width, int(model.get_value(l_goal).constant_value()), n_circuits, circuits, solution, fig_path)

    return






