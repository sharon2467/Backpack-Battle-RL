Print["VERSION=", $Version];
(* State order: acc = -2,-1,0,1,2. Each raw input has probability 1/5. *)
transition = {{1,1,3,0,0},{1,1,1,2,0},{1,1,1,1,1},{0,2,1,1,1},{0,0,3,1,1}}/5;
emission = {{0,0,1,1,3},{0,1,1,1,2},{1,1,1,1,1},{2,1,1,1,0},{3,1,1,0,0}}/5;
variables = Array[x, 5];
solution = First[Solve[Join[Thread[variables.transition == variables], {Total[variables] == 1}], variables]];
stationary = variables /. solution;
pmf = stationary.emission;
values = Range[0,4];
variance = pmf.(values-2)^2;
(* For each state and raw draw: {next state index, emitted value}. *)
edges = {{{1,2},{2,3},{3,4},{3,4},{3,4}},
         {{1,1},{2,2},{3,3},{4,4},{4,4}},
         {{1,0},{2,1},{3,2},{4,3},{5,4}},
         {{2,0},{2,0},{3,1},{4,2},{5,3}},
         {{3,0},{3,0},{3,0},{4,1},{5,2}}};
nextMean = emission.values;
product = Sum[stationary[[i]] edges[[i,j,2]] nextMean[[edges[[i,j,1]]]]/5, {i,5},{j,5}];
Print["STATIONARY=", InputForm[stationary]];
Print["PMF=", InputForm[pmf]];
Print["VARIANCE=", InputForm[variance]];
Print["LAG1=", InputForm[(product-4)/variance]];
If[pmf == {26,20,23,20,26}/115 && variance == 248/115 && (product-4)/variance == -229/620,
  Print["EXACT_CHECK_PASS"], Print["EXACT_CHECK_FAIL"]; Exit[1]];
