from pulp import *
import utils


def solve_problem(input_file, out_dir, fig_dir, instance_name, solver, path_to_cplex, symmetry, timeout = 300):
    width, n_circuits, x, y, l_min, l_max, index_max_area, circuits = utils.read_file(input_file)
    out_file = os.path.join(out_dir, str(instance_name) + '-out.txt')
    fig_path = os.path.join(fig_dir, str(instance_name) + '-fig.png')

    vlsi_no_rotation = LpProblem('VLSI', LpMinimize)

    x_pos = LpVariable.dict("x_pos", [i for i in range(n_circuits)], lowBound = 0, upBound = width - min(x), cat = LpInteger)
    y_pos = LpVariable.dict("y_pos", [i for i in range(n_circuits)], lowBound = 0, upBound = l_max - min(y), cat = LpInteger)

    l_goal = LpVariable('Length', lowBound = l_min, upBound = l_max, cat = LpInteger)

    binary_variable = [
        [[LpVariable(name=f'd_{i}_{j}_{k}', cat = LpBinary) for k in range(4)] for j in range(i+1,n_circuits)]
        for i in range(n_circuits - 1)]

    vlsi_no_rotation += l_goal

    #non oltre plate
    for i in range(n_circuits):
        vlsi_no_rotation += x[i] + x_pos[i] <= width
        vlsi_no_rotation += y[i] + y_pos[i] <= l_goal

    for i in range(n_circuits):
        for j in range(n_circuits):
            if i < j:
                vlsi_no_rotation += x_pos[i] + x[i] <= x_pos[j] + width*binary_variable[i][n_circuits-j-1][0]
                vlsi_no_rotation += x_pos[j] + x[j] <= x_pos[i] + width*binary_variable[i][n_circuits-j-1][1]
                vlsi_no_rotation += y_pos[i] + y[i] <= y_pos[j] + l_max*binary_variable[i][n_circuits-j-1][2]
                vlsi_no_rotation += y_pos[j] + y[j] <= y_pos[i] + l_max*binary_variable[i][n_circuits-j-1][3]
                vlsi_no_rotation += binary_variable[i][n_circuits-j-1][0] + binary_variable[i][n_circuits-j-1][1] + binary_variable[i][n_circuits-j-1][2] + binary_variable[i][n_circuits-j-1][3] <= 3

    if symmetry:
        #larger plate in(0,0)
        vlsi_no_rotation += x_pos[index_max_area] == 0
        vlsi_no_rotation += y_pos[index_max_area] == 0

        if solver == 'cplex':
            solver = CPLEX_CMD(path=path_to_cplex, msg = True, timeLimit=timeout,
                               options=["set preprocessing symmetry 5", "set threads 8", "set mip strategy probe 3" ,"set emphasis mip 1"])
    if solver == 'cplex':
        #path_to_cplex = 'C:/Program Files/IBM/ILOG/CPLEX_Studio221/cplex/bin/x64_win64/cplex.exe'
        solver = CPLEX_CMD(path=path_to_cplex, msg=True, timeLimit=timeout,
                           options=["set threads 8", "set mip strategy probe 3",
                                    "set emphasis mip 1"])


    if solver == 'gurobi':
        solver = GUROBI(timeLimit = timeout)

    if solver == 'pulp':
        solver = PULP_CBC_CMD(timeLimit=timeout)

    vlsi_no_rotation.solve(solver)


    x_sol = []
    y_sol = []

    solution = {}

    status = vlsi_no_rotation.sol_status


    if vlsi_no_rotation.status == 1:
        for i in range(n_circuits):
            x_sol.append(int(x_pos[i].varValue))
            y_sol.append(int(y_pos[i].varValue))
        final_length = int(l_goal.varValue)
        corners = []
        for i in range(0, len(x_sol)):
            corners.append([int(x_pos[i].varValue), int(y_pos[i].varValue)])
        solution['corners'] = corners
        time = vlsi_no_rotation.solutionTime
        utils.write_file(width, n_circuits, x, y, corners, final_length, instance_name, l_max, out_file, time, status)
        utils.plot_solution(width, int(l_goal.varValue), n_circuits, circuits, solution, fig_path)

    else:
        try:
            final_length = round(vlsi_no_rotation.solverModel.getVarByName("height").X)
            for i in range(n_circuits):
                x_sol.append(round(vlsi_no_rotation.solverModel.getVarByName(f"x{i + 1:02d}").X))
                y_sol.append(round(vlsi_no_rotation.solverModel.getVarByName(f"y{i + 1:02d}").X))
            corners = []
            for i in range(0, len(x_sol)):
                corners.append([int(x_pos[i].varValue), int(y_pos[i].varValue)])
            utils.write_file(width, n_circuits, x, y, corners, final_length, instance_name, l_max, out_file, vlsi_no_rotation.solutionTime, status)
            utils.plot_solution(width, int(l_goal.varValue), n_circuits, circuits, solution, fig_path)

        except:
            utils.write_file(width, n_circuits, x, y, [], 0, instance_name, l_max, out_file, time = vlsi_no_rotation.solutionTime,
                             status = -1)




