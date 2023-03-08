from pysmt.shortcuts import Symbol, And, GE, LE, Ite, Or, Equals, Solver, AllDifferent, Iff, FALSE, Int, Bool, TRUE
from pysmt.typing import INT, BOOL
import utils
import os
import time

def cumulative(start, duration, resources, total):
    decomposition = []
    for r in resources:
            decomposition.append(sum([Ite(And(start[i] <= Int(r), Int(r) < start[i] + Int(duration[i])), Int(resources[i]), Int(0)) for i in range(len(start))]) <= (Int(total)))
    return decomposition


def solve_problem(input_file, out_dir, fig_dir, instance_name, solver, symmetry, timeout = 300):
    width, n_circuits, x, y, l_min, l_max, index_max_area, circuits = utils.read_file(input_file)
    out_file = os.path.join(out_dir, str(instance_name) + 'rot' + '-out.txt')
    fig_path = os.path.join(fig_dir, str(instance_name) + 'rot' + '-fig.png')

    x_rot = [Symbol(f'x_pos_{str(i+1)}', INT) for i in range(n_circuits)]
    y_rot = [Symbol(f'y_pos{str(i+1)}', INT) for i in range(n_circuits)]
    rot = [Symbol(f'rot{str(i+1)}',INT) for i in range(n_circuits)]

    l_goal = Symbol('Length',INT)

    rot_domain = [Or(Equals(rot[i], Int(0)), Equals(rot[i], Int(1))) for i in range(n_circuits)]
    limit_constraints_x = [LE(x_rot[i] + (rot[i] * (y[i])) + (Int(1) - rot[i]) * Int(x[i]), Int(width)) for i in range(n_circuits)]
    limit_constraints_y = [LE(y_rot[i] +(rot[i] * Int(x[i])) + (Int(1) - rot[i]) * Int(y[i]), l_goal) for i in range(n_circuits)]

    x_domain = [And(GE(x_rot[i], Int(0)), LE(x_rot[i], Int(width) - Int(min(x)))) for i in range(n_circuits)]
    y_domain = [And(GE(y_rot[i], Int(0)), LE(y_rot[i], Int(l_max) - Int(min(y)))) for i in range(n_circuits)]

    l_goal_domain = And(GE(l_goal, Int(l_min)), LE(l_goal, Int(l_max)))

    overlapping_constraints = []

    symmetry_constraints = []

    if symmetry:
        symmetry_constraints.append(And(Equals(x_rot[index_max_area], Int(0)), Equals(y_rot[index_max_area],Int(0))))
        for i in range(n_circuits):
            if (x[i] == y[i]):
                symmetry_constraints.append(Iff(Equals(rot[i], Int(0)), TRUE()))
            if (y[i] > width):
                symmetry_constraints.append(Iff(Equals(rot[i], Int(0)), TRUE()))

    for i in range(n_circuits):
        for j in range(n_circuits):
            if i < j:
                overlapping_constraints.append(Or(LE(x_rot[i] + (rot[i] * y[i]) + ((Int(1)-rot[i])*x[i]), x_rot[j]),
                                               LE(x_rot[j] + (rot[j] * y[j]) + ((Int(1)-rot[j]) * x[j]), x_rot[i]),
                                               LE(y_rot[i] + (rot[i]*x[i]) + ((Int(1)-rot[i]) * y[i]), y_rot[j]),
                                               LE(y_rot[j] + (rot[j]*x[j]) + ((Int(1)-rot[j])*y[j]), y_rot[i])))


    cumulative_x = cumulative(x_rot, x, y, l_max)
    cumulative_y = cumulative(y_rot, y, x, width)
    domains = And(*x_domain, *y_domain, *rot_domain, l_goal_domain, *limit_constraints_x, *cumulative_x, *cumulative_y, *limit_constraints_y, *symmetry_constraints, *overlapping_constraints)
    k = l_min
    problem = Equals(l_goal, Int(k))
    formula = And(domains, problem)

    start_time = time.time()
    with Solver(name = 'z3', solver_options = {'timeout':timeout*1000, 'auto_config':True} ) as solver:
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
    get_solution(t, n_circuits, model, x_rot, y_rot, rot, width, x, y, final_length, instance_name, l_max, out_file, l_goal, circuits, fig_path)

    return

def get_solution(t, n_circuits, model, x_rot, y_rot, rot, width, x, y, final_length, instance_name, l_max, out_file, l_goal, circuits, fig_path):

    x_sol = []
    y_sol = []

    solution = {}

    for i in range(n_circuits):
        x_sol.append(model.get_value(x_rot[i]).constant_value())
        y_sol.append(model.get_value(y_rot[i]).constant_value())
        if model.get_value(rot[i]).constant_value() == 1:
            circuits[i] = y[i], x[i]
    corners = []

    for i in range(0, len(x_rot)):
        corners.append([model.get_value(x_rot[i]).constant_value(), model.get_value(y_rot[i]).constant_value()])
    solution['corners'] = corners
    utils.write_file(width, n_circuits, x, y, corners, final_length, instance_name, l_max, out_file, t, status = 1)
    utils.plot_solution(width, int(model.get_value(l_goal).constant_value()), n_circuits, circuits, solution, fig_path)

    return