CONTEXT: Erdős #23 / a(30)=36 proof attempt, q=14,t=2 branch.

Known verified setup:
- C={c1,c2}, A=N(x)\C, B=N(y)\C, |A|=|B|=6, |R|=14.
- Labels on R are subsets of {1,2}. R-edges occur only between disjoint labels.
- p=e(A,B), eR=e(R), U=sum label sizes, cap=e(A∪B,R)=123-p-eR-U.
- q15 is closed. q14/t2 is closed for cap<=42 by exact fixed-label verifier.
- Clean-shadow/C-tight dichotomy verified:
  clean means every r in R\U_i has d_R(r,U_i)>=3.
  On clean side, eR >= 3 max(s1,s2)+eta(d)z, eta(0)=6, eta(1)=5, eta(2)=4, eta(d>=3)=3.
  If not clean, there is a C-tight vertex; rerooting gives q'<=14 and q'<14 unless |U_i|=6 and deg(r)=8.

Current obstruction:
Clean cap74 collapses to six scalar rows. Four are exact UNSAT. The only hard clean rows are:
  z=8,d=6,s1=s2=0,U=12,
  (p,eR)=(13,24) and (12,25).

I ran the exact verifier with rooted cuts disabled for (p,eR)=(13,24), and got a SAT model. But this model is not valid under exact rooted cuts. An analyzer over all 2^14 R-masks reports:
  badCuts=241.
Worst violations:
  Phi=25 on D-only mask {8,12,13};
  Phi=27 on D-only mask {8,11,12,13};
  Phi=28 on D-only masks {8,12} and {8,13};
  Psi=29 on mask {0,1,2,3,4,5,6,7,9}, containing all 8 zero vertices and one D vertex;
  Psi=29 on mask {8,9,11,12,13}, containing five D vertices.

In z=8,d=6 clean case:
- labels are 8 zero vertices Z and 6 doubleton vertices D.
- Clean condition forces every zero vertex to have at least 3 R-neighbours in D for each colour; since D contains both colours, this just says each zero vertex has at least 3 R-neighbours in D.
- R-edges are only Z-D and Z-Z; no D-D.
- The clean cap74 rows have very sparse p/eR:
  eR=24,p=13 or eR=25,p=12, and cap=74.

QUESTION:
Can you prove a rigorous hand lemma eliminating the clean z=8,d=6 cap74 family using exact rooted-cut inequalities, especially D-only Phi cuts?

Please focus on one of these targets:
1. Show that in any clean z=8,d=6 row with (p,eR)=(13,24) or (12,25), some D-only mask W has Phi(W)<37, contradiction.
2. Or derive a scalar/structural inequality from requiring Phi(W)>=37 for all W subset D and Psi(W)>=37 for all W subset R, strong enough to force eR or p outside the two rows.
3. Or, if this cannot be proved from current constraints, identify the exact additional finite compatibility condition involving A/B-R incidences and A-B edges that must be encoded.

REQUIREMENTS:
- Do not claim q14/t2 is solved.
- Be adversarial. Do not assume random-like distribution.
- Every counted quantity must be defined precisely.
- If using D-only masks, write Phi(W) explicitly in terms of p, internal Z-D edges, A/B incidences from W, and label constants.
- End with weakest steps and any extra assumptions.
