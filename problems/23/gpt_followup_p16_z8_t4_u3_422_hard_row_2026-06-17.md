CONTEXT: Erdős #23 / a(30)=36. Current branch is q14/t2 cap74, p=16, z=8, (ZZ,ZD)=(0,21), P-free verifier only.

We are inside t=4 zero-degree profile n2,n3,n4,n5=(4,3,1,0), touched count u=3, tight-pair skeleton u3_422:
  tight pairs (8,10)^2 and (9,10)^2.
Thus tau_8=tau_9=2, tau_10=4, tau_11=tau_12=tau_13=0.

Encoded constraints:
- all previous local state/codegree/rooted lazy cuts;
- touched-column equality c_d+m_d=6 and c_d<=4;
- full tight-zero reroot p*_z+eR*_z=37;
- reroot D' domain {1,2,3,4,6}, D'+L'=D'+R'=6;
- non-isolated tight-pair D'<=4;
- E(8,10)=E(9,10)=0;
- saturated-column cuts at column 10:
  n[h,v] >= y[v,10] for non-tight h;
  y[v,10]+y[v,d]<=1 for d != 10;
- unique degree-4 non-tight zero h4 sees 8 and 9.

Current hard residual branch:
- h4 misses 11, so N_D(h4)={8,9,12,13}.
- D-column deltas (delta_8,...,delta_13)=(0,0,0,2,0,1), so column degrees c=(4,4,4,2,4,3).
- The three degree-3 non-tight zero rows are fixed as:
  one row {8,9,12};
  two rows {11,12,13}.
Equivalently row-count vector over 3-subsets of [8,9,11,12,13] in lex order
[(8,9,11),(8,9,12),(8,9,13),(8,11,12),(8,11,13),(8,12,13),(9,11,12),(9,11,13),(9,12,13),(11,12,13)]
is:
  0,1,0,0,0,0,0,0,0,2.

Computation:
- This exact branch stays UNKNOWN after 900s with 100 CP-SAT workers.
- Nearby branches with the same cuts often close in 80-220s, so this is the remaining structural obstruction.

QUESTION:
Find the next mathematically safe P-free strengthening for this exact residual branch. Prefer a direct contradiction or a small CP-SAT constraint/branch. Use the explicit zero rows above. Avoid fixed A/B template enumeration. In particular inspect:
- the two degree-3 zeros with row {11,12,13};
- the row {8,9,12};
- h4 row {8,9,12,13};
- saturated column 10 with its two A/B neighbours S_10 adjacent to all four non-tight zeros and no other D-neighbour;
- R/R nonedge codegrees among these zero rows and tight zeros.
State a rigorous lemma, proof, exact encoding, and weakest assumptions.
