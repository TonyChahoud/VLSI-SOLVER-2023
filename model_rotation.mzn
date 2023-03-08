%include "chuffed.mzn";
include "gecode.mzn";
include "globals.mzn";

int: w;  % width
int: N;  % n. of circuits to be placed
set of int: NUM = 1..N; % Set with indeces of circuitsersect


array[NUM] of int: x_dim_orig;
array[NUM] of int: y_dim_orig;
array[NUM] of var bool : rotated;


%-------------------------------------
% Inferior and Superior limits for width and height
%-------------------------------------
int: limit_dim = min(w, sum(i in NUM)(max(x_dim_orig[i], y_dim_orig[i])));  %circuits can rotate
int: limit_H = sum([max(x_dim_orig[i],y_dim_orig[i]) | i in 1..N]);
int: min_limit_H = ceil(sum([x_dim_orig[i]*y_dim_orig[i] | i in NUM]) / limit_dim); %minimum height is derived from the area of a rectangle composed by all the circuits, because rectangle is the shape with minimum area that can be buildt


array[NUM] of var 0..max([x_dim_orig[i] | i in NUM] ++ [y_dim_orig[i] | i in NUM]): x_dim = [(x_dim_orig[i]*(1-rotated[i]))+(y_dim_orig[i]*rotated[i]) | i in NUM];
array[NUM] of var 0..max([x_dim_orig[i] | i in NUM] ++ [y_dim_orig[i] | i in NUM]): y_dim = [(y_dim_orig[i]*(1-rotated[i]))+(x_dim_orig[i]*rotated[i]) | i in NUM];



%-------------------------------------
% Output coordinates of circuits 
%------------------------------------- 

array[NUM] of var 0..limit_dim-min([x_dim_orig[i] | i in NUM] ++ [y_dim_orig[i] | i in NUM]): x_coord;  
array[NUM] of var 0..limit_H-min([x_dim_orig[i] | i in NUM] ++ [y_dim_orig[i] | i in NUM]): y_coord; 

array[NUM] of var int: y_end_pos = [y_coord[i]+y_dim[i] | i in NUM];
array[NUM] of var int: x_end_pos = [x_coord[i]+x_dim[i] | i in NUM];

%-------------------------------------
% Objective value 
%-------------------------------------
var min_limit_H..limit_H: sol;

%-------------------------------------
% Domain reduction
%-------------------------------------
constraint forall(i in NUM) (x_coord[i]<=limit_dim-x_dim[i])::domain;
constraint forall(i in NUM) (y_coord[i]<=limit_H-y_dim[i])::domain;

% All circuits must be inside the chip
constraint forall (i in NUM) (x_coord[i]>=0);
constraint forall (i in NUM) (y_coord[i]<=sol);

constraint forall (i in NUM) (x_end_pos[i]<=limit_dim);
constraint forall (i in NUM) (y_end_pos[i]<=sol);

% non-overlapping (both axis):
constraint diffn(x_coord, y_coord, x_dim, y_dim);
constraint cumulative(y_coord, y_dim, x_dim, w);  
constraint cumulative(x_coord, x_dim, y_dim, sol);

% SYMMETRY BREAKING:
%constraint lex_less(x_pos, [W-x_end_pos[i]| i in NUM]);
array[NUM] of var int: symm = [sol-y_end_pos[i] | i in NUM ];
constraint lex_less(y_coord, symm);
%square circuits are not rotated
constraint symmetry_breaking_constraint(forall (i in NUM) (x_dim_orig[i] = y_dim_orig[i] -> rotated[i] = 0));



solve 
    :: int_search([], dom_w_deg, indomain_random)
    :: restart_luby(400)
    % relax_and_reconstruct doesn't work well here
minimize sol;

%To be used with satisfy: output ["\(H)"];

output ["N=\(N)\nW=\(w)\n\(x_coord)\n\(y_coord)\n"];
