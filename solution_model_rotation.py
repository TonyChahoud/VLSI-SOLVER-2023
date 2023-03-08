from pulp import *
import utils



def solve_problem(input_file, out_dir, fig_dir, instance_name, solver, path_to_cplex, symmetry, timeout = 300):
    w, n, x, y, l_min, l_max, index_max_area, circuits = utils.read_file(input_file)
    out_file = os.path.join(out_dir, str(instance_name) + 'rot' + '-out.txt')
    fig_path = os.path.join(fig_dir, str(instance_name) + 'rot' + '-fig.png')

    vlsi_rotation = LpProblem('VLSI', LpMinimize)
    x_rot = LpVariable.dict("x_pos", [i for i in range(n)], lowBound=0, upBound=w - min(x), cat = LpInteger)
    y_rot = LpVariable.dict("y_pos", [i for i in range(n)], lowBound=0, upBound=l_max - min(y), cat = LpInteger)

    Y_goal = LpVariable('length', lowBound = l_min, upBound = l_max, cat = LpInteger)

    binary_variable = [
        [[LpVariable(name=f'd_{i}_{j}_{k}', cat=LpBinary) for k in range(4)] for j in range(i + 1, n)]
        for i in range(n - 1)]

    vlsi_rotation += Y_goal

    rot = [LpVariable(name=f'binary_var_{i}', cat = LpBinary) for i in range(n)]

    #non oltre plate
    for i in range(n):
        vlsi_rotation += x_rot[i] + rot[i]*y[i] + (1-rot[i])*x[i] <= w
        vlsi_rotation += y_rot[i] + rot[i]*x[i] + (1-rot[i])*y[i] <= Y_goal

    for i in range(n):
        for j in range(n):
            if i<j:
                vlsi_rotation += x_rot[i] + rot[i]*y[i] + (1-rot[i])*x[i] <= x_rot[j] + w * binary_variable[i][n - j - 1][0]
                vlsi_rotation += x_rot[j] + rot[j]*y[j] + (1-rot[j])*x[j] <= x_rot[i] + w * binary_variable[i][n - j - 1][1]
                vlsi_rotation += y_rot[i] + rot[i]*x[i] + (1-rot[i])*y[i] <= y_rot[j] + l_max * binary_variable[i][n - j - 1][2]
                vlsi_rotation += y_rot[j] + rot[j]*x[j] + (1-rot[j])*y[j] <= y_rot[i] + l_max * binary_variable[i][n - j - 1][3]
                vlsi_rotation += binary_variable[i][n - j - 1][0] + binary_variable[i][n - j - 1][1] + \
                                    binary_variable[i][n - j - 1][2] + binary_variable[i][n - j - 1][3] <= 3


    #larger plate in(0,0)
    if symmetry == True:
        vlsi_rotation += x_rot[index_max_area] == 0
        vlsi_rotation += y_rot[index_max_area] == 0

        if solver == 'cplex':
            # path_to_cplex = 'C:/Program Files/IBM/ILOG/CPLEX_Studio221/cplex/bin/x64_win64/cplex.exe'
            solver = CPLEX_CMD(path=path_to_cplex, msg=True, timeLimit=timeout,
                               options=["set preprocessing symmetry 5", "set threads 8", "set mip strategy probe 3",
                                        "set emphasis mip 1"])
    if solver == 'cplex':
        # path_to_cplex = 'C:/Program Files/IBM/ILOG/CPLEX_Studio221/cplex/bin/x64_win64/cplex.exe'
        solver = CPLEX_CMD(path=path_to_cplex, msg=True, timeLimit=timeout,
                           options=["set threads 8", "set mip strategy probe 3",
                                    "set emphasis mip 1"])

    if solver == 'gurobi':
        solver = GUROBI(timeLimit=timeout)

    if solver == 'pulp':
        solver = PULP_CBC_CMD(timeLimit=timeout)

    vlsi_rotation.solve(solver)

    x_sol = []
    y_sol = []

    corners = []

    solution = {}
    status = vlsi_rotation.sol_status

    if vlsi_rotation.status == 1:
        for i in range(n):
            (x_sol.append(int(x_rot[i].varValue)))
            y_sol.append(int(y_rot[i].varValue))
            if rot[i].varValue == 1:
                circuits[i] = y[i], x[i]
        length = int(Y_goal.varValue)
        solution['corners'] = corners
        for i in range(0, len(x_sol)):
            corners.append([int(x_sol[i]), int(y_sol[i])])
        time = vlsi_rotation.solutionTime
        utils.write_file(w,n,x,y,circuits,length, instance_name, l_max, out_file, time, status)
        utils.plot_solution(w, int(Y_goal.varValue), n, circuits, solution, fig_path)


    else:
        try:
            length = round(vlsi_rotation.solverModel.getVarByName("height").X)
            for i in range(n):
                x_sol.append(round(vlsi_rotation.solverModel.getVarByName(f"x{i + 1:02d}").X))
                y_sol.append(round(vlsi_rotation.solverModel.getVarByName(f"y{i + 1:02d}").X))
            corners = []
            for i in range(0, len(x_sol)):
                corners.append([int(x_rot[i].varValue), int(y_rot[i].varValue)])
            utils.write_file(w, n, x, y, corners, length, instance_name, l_max, out_file,
                             vlsi_rotation.solutionTime, status)
            utils.plot_solution(w, int(length), n, circuits, solution, fig_path)

        except:
            utils.write_file(w, n, x, y, [], 0, instance_name, l_max, out_file,
                             time=vlsi_rotation.solutionTime,
                             status=-1)
