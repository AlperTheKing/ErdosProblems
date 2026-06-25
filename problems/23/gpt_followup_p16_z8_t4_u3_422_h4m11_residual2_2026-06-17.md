CONTEXT: Erdős #23 / a(30)=36. Current branch is q14/t2 cap74, p=16, z=8, (ZZ,ZD)=(0,21), P-free verifier only.

We are in t=4 zero-degree profile (4,3,1,0), touched count u=3, tight-pair skeleton u3_422:
  tight pairs (8,10)^2 and (9,10)^2.
Thus tau_8=tau_9=2, tau_10=4.

Encoded constraints:
- local state/codegree/rooted lazy cuts;
- touched-column equality c_d+m_d=6 and c_d<=4;
- full tight-zero reroot scalar closure p*_z+eR*_z=37;
- reroot D' domain {1,2,3,4,6}, D'+L'=D'+R'=6;
- non-isolated tight-pair D'<=4;
- E(8,10)=E(9,10)=0;
- saturated-column cuts at column 10;
- unique degree-4 non-tight zero h4 sees 8 and 9.

We have closed the hard row where h4 misses 11, two degree-3 zeros have row {11,12,13}, and the remaining degree-3 zero has row {8,9,12} or {8,9,13}; GPT gave an M<=72 contradiction.

Remaining h4=miss11 residual type:
- h4 row {8,9,12,13}.
- two degree-3 zeros w1,w2 have row {11,12,13}.
- the remaining degree-3 zero r has row {8,12,13}.
- D-column deltas (delta_8,...,delta_13)=(0,1,0,2,0,0), so c=(4,3,4,2,4,4).
The 8/9 symmetric copy is:
- r row {9,12,13};
- deltas (1,0,0,2,0,0), c=(3,4,4,2,4,4).

Computation:
- The first residual stays UNKNOWN after 300s with 100 workers:
  --d-column-deltas 0,1,0,2,0,0
  --deg3-row-counts 0,0,0,0,0,1,0,0,0,2
- The symmetric copy also stays UNKNOWN after 300s:
  --d-column-deltas 1,0,0,2,0,0
  --deg3-row-counts 0,0,0,0,0,0,0,0,1,2

QUESTION:
Find a mathematically safe P-free strengthening/contradiction for this residual type. Avoid fixed A/B template enumeration. Inspect whether a modified singleton-block/capacity argument gives M<=73 or M<=72, or whether S_8/S_10 plus the two {11,12,13} zeros force enough A/B states. State the lemma, proof, exact CP-SAT encoding, and weakest assumptions.
