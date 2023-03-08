# This may be necessary, depending on the system configuration:
# from minizinc import find_driver;  find_driver(['path/...']).make_default()

import sys, gc, logging, asyncio, pprint
from time import monotonic as clock
from os.path import normpath
sys.path.append(normpath('../../util/'))
from util import timed, parse, load_instance_numbers, save_sol_file, secs

sys.path.append(normpath('../../'))
from commons import *

from minizinc import Instance, Model, Solver
from minizinc.result import Status
from minizinc.model import Method


# SPECIFIC PARAMETERS:
SOLVER = 'gecode'
SOLVER_PARS = {                             # see: https://minizinc-python.readthedocs.io/en/latest/api.html
    'timeout':              secs(300),
    'processes':            4,              # supported by gecode, not chuffed
    #'free_search':          True,          # Allows the solver to ignore the specified search
    #'optimisation_level':   2              # Apparently makes things slower
}
VLSI = Model('model_rotation.mzn' if ROT else 'model.mzn')

# logging.basicConfig(filename="minizinc-python.log", level=logging.DEBUG)


# _____________________________________________________________________________

INSTANCES = load_instance_numbers(sys.argv, INST_PATH)

def pp_sol_stats(result):
    return f'{pprint.pformat(result.statistics)}\n'

async def solve_handle_restart(instance):
    global SOLVER_PARS
    t = clock()
    prev = None
    async for s in instance.solutions(**SOLVER_PARS):
        if s.solution is None: continue
        prev = s
        # print(s.status)
        if s.status==Status.OPTIMAL_SOLUTION:
            return s, clock()-t
    
    if secs(clock()-t) < SOLVER_PARS['timeout'] and prev:
        prev.status = Status.OPTIMAL_SOLUTION   # ??? Dangerous assumption ???
    return prev, clock()-t

# _____________________________________________________________________________

tot = len(INSTANCES)
optimal = 0

try:
    for i in INSTANCES:
        # Create an Instance of the model for the solver:
        instance = Instance(Solver.lookup(SOLVER), VLSI)
        SATISFACTION = True if instance.method is Method.SATISFY else False
        for (k,v) in parse(normpath(f'{INST_PATH}ins-{i}.txt'), rotation=ROT).items():
            instance[k] = v
        
        if SATISFACTION:
            result, t = timed(instance.solve, **SOLVER_PARS)
        else:
            result, t = asyncio.run(solve_handle_restart(instance)) 
            #print(result.status)
        
        def save_result(msg):
            le = len(result['x_coord'])
            #print(result)
            xx = [result['x_coord'][i] for i in range(0,le) if result['rotated'][i]] if ROT else\
                result['x_coord']
            yy = [result['y_coord'][i] for i in range(0,le) if result['rotated'][i]] if ROT else\
                result['y_coord']
            xdim = [(instance['x_dim_orig']+instance['y_dim_orig'])[i] for i in range(0,le) if result['rotated'][i]] if ROT else\
                instance['x']
            ydim = [(instance['y_dim_orig']+instance['x_dim_orig'])[i] for i in range(0,le) if result['rotated'][i]] if ROT else\
                instance['y']
            sol = int(result.solution._output_item) if SATISFACTION else result['objective']
            combo = [f'{d1} {d2} {x1} {y1}' for (d1,d2,x1,y1) in zip(xdim,ydim,xx,yy)]
            print(msg)
            path = f'{SOL_PATH}out-{i}.txt' 
            save_sol_file(normpath(path), instance['w'], sol, combo, DISP)
            print()
            
        if result and result.status == Status.OPTIMAL_SOLUTION:
            optimal += 1
            save_result(f'Solution found for instance {i:2} in {t:5.1f} secs. [{result.status}]')
            # print(result)
        elif result and result.status == Status.SATISFIED:
            if SATISFACTION:
                save_result(f'Solution found for instance {i:2} in {t:5.1f} secs. [{result.status}]')
            else:
                print(f'TIMEOUT FOR INSTANCE {i:2} [{result.status}]\n')
            # print(result.statistics)
        else:
            print(f'UNEXPECTED ENDING STATUS FOR INSTANCE {i:2}')
            if result: print(result.status, pp_sol_stats(result))
            else: print(f'{result}\n')
        del instance
        gc.collect()
        
except KeyboardInterrupt: print('\nAborted by user.')
finally: print(f'{optimal}/{tot}')


# _____________________________________________________________________________
# SOME NOTES FOLLOW

# gc.set_debug(gc.DEBUG_STATS)

# SOLVERS:
# ['api', 'cbc', 'chuffed', 'coin-bc', 'coinbc', 'cp', 'cplex', 'experimental', 'findmus', 'float', 'gecode', 'gist', 'globalizer', 'gurobi', 'int', 'lcg', 'mip', 'org.chuffed.chuffed', 'org.gecode.gecode', 'org.gecode.gist', 'org.minizinc.findmus', 'org.minizinc.globalizer', 'org.minizinc.mip.coin-bc', 'org.minizinc.mip.cplex', 'org.minizinc.mip.gurobi', 'org.minizinc.mip.scip', 'org.minizinc.mip.xpress', 'osicbc', 'restart', 'scip', 'set', 'tool', 'xpress']

'''
Result(status=<Status.SATISFIED: 5>, solution=Solution(x_pos=[0, 0, 3, 3], y_pos=[0, 3, 5, 0], _output_item='8', _checker=''), statistics={'paths': 0, 'flatBoolVars': 24, 'flatIntVars': 16, 'flatBoolConstraints': 6, 'flatIntConstraints': 35, 'evaluatedHalfReifiedConstraints': 24, 'method': 'satisfy', 'flatTime': datetime.timedelta(microseconds=136809), 'time': datetime.timedelta(microseconds=150000), 'initTime': datetime.timedelta(microseconds=974), 'solveTime': datetime.timedelta(microseconds=599), 'solutions': 1, 'variables': 40, 'propagators': 37, 'propagations': 164, 'nodes': 7, 'failures': 1, 'restarts': 0, 'peakDepth': 4, 'nSolutions': 1})
'''

# To retain every solution:
# https://minizinc-python.readthedocs.io/en/latest/getting_started.html#finding-all-solutions
