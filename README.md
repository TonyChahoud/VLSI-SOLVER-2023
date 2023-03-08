# Cobinatorial-
Very large-scale integration (VLSI) is the process of creating an integrated circuit by combining millions 
or billions of transistors onto a single chip. A typical example is the smartphone. The modern trend 
of shrinking transistors sizes, allowing engineers to fit more and more transistors into the same area 
of silicon, has pushed the integration of more and more functions of cellphone circuitry into a single 
silicon plate. This enables the modern cellphone to mature into a powerful tool that shrank from the 
size of a large brick-sized unit to a device small enough to comfortably carry in a pocket or purse, with 
a video camera, touchscreen and other advanced features.
We will describe in this report our approach to design the VLSI of the circuits defining their electrical 
device: given a fixed-width plate and a list of rectangular circuits, decide how to place them on the 
plate so that the length of the final device is minimized, therefore improving its portability.

this Solver , it was based on 4 Different PRocedure 
1-Constraint Promgraming
2-SAT Model
3-SMT Model 
4-MIT Model





CP:

This code uses the Python3 "minizinc" module. It can be installed using "pip3 install minizinc" or "snap install minizinc --classic"; further details here: https://minizinc-python.readthedocs.io/en/latest/getting_started.html

To launch It on a specific list of instances ins-m.txt, ins-n.txt ... ins-o.txt:
python3 main.py m n ... o

Otherwise just the following to launch it on all instances in the "instances" folder:
python3 main.py

Some parameters can be set in the "commons.py" file in the root directory.

Solutions are generated in instances/solutions.

Set DISP to False to avoid svg generation(DrawSVG).
SAT MODEL
This code use the z3 solver  that can be installed using:
pip3 install z3-solver
The aim is to place some blocks (given width and height) in a rectangle (silicon chip), minimizing its height.
Given a file in the following format:
-maximum width of the rectangle
-number of blocks
exceuting it as input is the form of :
[list of positions of  left corner of each reactabgle inside the plate]
To solve instances:
python main.py <model_name> <instance_path> <dest_path>
2 solvers:-SAT (sat without roration)
          -SATrot (sat with rotation)

the solvers return:
maximum width and height of the rectangle
number of blocks
output of each instance is saved as txt.file in the 2 Files:
  1-SAToutput (without rotation)
  2-SAToutRot (with Rotation)

The SAT version can be launched just by executuing(run) the python notebook through jupyter.

Please check the full REPORT for more details about SAT model in solving the VLSI problem


SMT + MIP:

To execute one of the two models run:
python main.py -model -solver

Example:
python main.py -m smt -s z3
will run the smt model with z3.

Other arguments available:
-i Path to the directory containing the initial instances
-o Path to the directory that will contain the output solutions
-f Path to the directory that will containing the figures
-m Model (required), either 'smt' or 'mip'
-s Solver (required), 'z3','cplex','pulp','gurobi'
-c Path to cplex solver
-r Specify if it is possible to use rotated circuits, default = False
-sym Specify if symmetry breaking constraints are enables, default = True
