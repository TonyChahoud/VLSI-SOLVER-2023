  %include "chuffed.mzn";
include "gecode.mzn";
include "globals.mzn";

%------------------------------------
% Inputs coming from data file (.dzn)  
%------------------------------------
int: w; %given width
int: N; %number of circuits to be placed
array[NUM] of int: x; %width for each circuit
array[NUM] of int: y; %height for each circuit
%circuit i has width x[i] and height y[i]  

%represent circuits by their lower left coordinates
set of int: NUM = 1..N; % Set with indeces of circuits


%-------------------------------------
% Upper and Lower limits for chips's width and height
%-------------------------------------

%-------------------------------------
% Max limit for chip's width
%-------------------------------------
%if the plate is larger than the sum of circuits' widths, then only a part is required
int: max_width_limit = min(w, sum([x[i] | i in NUM]));


%-------------------------------------
% Min limit for chip's width
%-------------------------------------
% The shape with minimum height is a rectangle with base equal to the maximum limit of the chip's width, 
% so the minimum height is the one of this rectangle, computed as area/base
int: min_height_limit = ceil(sum([x[i]*y[i] | i in NUM]) / max_width_limit); 


%-------------------------------------
% Max limit for chip's width
%-------------------------------------
%If there is no gaps between the circuits on the chip then the height would be equal to the sum of heights of all the circuits
int: max_height_limit = sum([y[i] | i in NUM]);



%------------------
% Output variables  
%------------------
% for each i-th module, its x and y coordinates (lower left) on the plate,
% x coordinate go beyond maximm width minus the minimum width of the circuit.
array[NUM] of var 0..max_width_limit-min([x[i] | i in NUM]): x_coord;

% y coordinate cannot go beyond maximum height limit minum the minimum height of the circuit.
array[NUM] of var 0..max_height_limit-min([y[i] | i in NUM]): y_coord;

%Top right coordinates of each circuit
array[NUM] of var int: x_end_coord = [x_coord[i] + x[i] | i in NUM];
array[NUM] of var int: y_end_coord = [y_coord[i] + y[i] | i in NUM];



%-------------------------------------
% Objective function
%-------------------------------------
%Chip: bottom left corner (0,0), upper right corner (max_width_limit,sol)
var min_height_limit..max_height_limit: sol= max(y_end_coord);


%-------------------------------------
% Constraints
%-------------------------------------

%constraints for placing circuits in the field
constraint forall(i in NUM) (0 <= x_coord[i]);
constraint forall(i in NUM) (x_end_coord[i] <= max_width_limit);
constraint forall(i in NUM) (0 <= y_coord[i]);
constraint forall(i in NUM) (y_end_coord[i] <= sol);


% non-overlapping (both axis):
constraint diffn(x_coord, y_coord, x, y);

% We have used coomulative constraints for both x and y axis. They ensure that circuit doesn't go beyond the chip.
% For the y axis the "starting time" is the y coordinate, the duration is how much it extends in the y axis and the resources occupied is the extension on the x axis, which, cumulative, must not be over the superior bound of the width
constraint cumulative(y_coord, [y[i] | i in NUM], [x[i] | i in NUM], max_width_limit);  
%for x axis
constraint cumulative(x_coord, [x[i] | i in NUM], [y[i] | i in NUM], sol);  


% SYMMETRY BREAKING:
%constraint lex_less(y_coord, [max_width_limit-x_end_coord[i]| i in NUM]);
%constraint lex_less(y_coord, [sol-(y_end_coord[i]) | i in NUM ]);
%constraint lex_less(x_coord ++ y_coord, [w - x_end_coord[i] | i in NUM] ++ [sol - y_end_coord[i] | i in NUM]);


%--------------------------------------
% Search
%--------------------------------------

%minimize solve ?
solve 
    :: int_search(x_coord, dom_w_deg, indomain_min)
    :: restart_luby(300)
    :: relax_and_reconstruct(x, 70)
minimize sol;
output [
         "Height of the chip is ", show(sol) , "\n",
         "X Coord = ", show(x_coord), "\n",
         "Y Coord = ", show(y_coord), "\n"
         
];

