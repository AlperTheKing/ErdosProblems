CONTEXT:
We are attacking Erdos #23 / a(30)=36, q14/t2/cap74 branch, currently p=16,e_R=21,z=8,d=6, category (ZZ,ZD)=(0,21).
The verifier is P-free exact A/B-state CP-SAT:
- 8 zeros Z, 6 doubletons D.
- A_i states X_i subset R and B_j states Y_j subset R.
- A/B edge iff X_i cap Y_j = empty; |X_i cap Y_j|=1 forbidden; total p=16.
- full R/R, A/R, B/R, A/A, B/B codegrees; root-to-R zero side visibility a_z,b_z>=2.
- checkerboard beta cuts + 489 ordinary rooted lazy cuts from previous SAT survivors.
- max 100 workers.

NEW CONSTRAINTS ADDED FROM YOUR LAST ANSWER:
For every tight zero z with d_D(z)=2 and touched D-column d:
  c_d + m_d = 6, c_d <= 4.
Added footprint/excess cuts:
  2t <= 4u, u<=5, if t=6 then u<=4,
  sum untouched tau_d >= 2t-5.
Also added full tight-zero reroot scalar equality:
  p*_z + eR*_z = 37
for every d_D(z)=2 zero, using the P-free formulas from your answer.

RESULTS:
Degree profile branches for zero D-degrees:
1. (n2,n3,n4,n5)=(6,0,1,1), t=6:
   u=3 INFEASIBLE in 9.4s.
   u=4 INFEASIBLE in 35.1s.
   So t=6 profile is closed.
2. (5,2,0,1), t=5:
   u=3 INFEASIBLE in 131s.
   u=4 UNKNOWN in 306s; project8 still UNKNOWN in 634s.
   u=5 INFEASIBLE in 80s.
3. (5,1,2,0), t=5:
   u=3 INFEASIBLE in 185s.
   u=4 UNKNOWN in 307s.
   u=5 INFEASIBLE in 91s.
4. (4,3,1,0), t=4:
   u=2 INFEASIBLE in 57s.
   u=3 UNKNOWN in 307s.
   u=4 UNKNOWN in 308s.
   u=5 UNKNOWN in 307s.
5. (3,5,0,0), t=3:
   u=2,3,4,5 all UNKNOWN in 307s each.
   Previously without new reroot constraints this profile produced SAT; separator found MIN_MONO=22 and added 128 rooted cuts. With reroot constraints and 489 cuts, no SAT found in 900s.

I also tried branching t=5,u=4,(5,2,0,1) by tight-zero A-side counts n24,n33,n42 (21 branches, 60s each): all UNKNOWN, no SAT.

QUESTION:
What is the next smallest mathematically safe strengthening that should close or sharply reduce the remaining UNKNOWN branches?
Please avoid broad fixed-P enumeration. Prefer a P-free row/skeleton/state lemma.
Candidates I am considering:
1. touched-column propagation c_d=4 => N_AB(d) subset N_AB(z) for every zero non-neighbour z;
2. outside-pair visibility for tight zeros: x_iz=1 => some outside D in X_i, similarly Y;
3. branch by exact tight footprint incidence vector on D columns;
4. add projected outer-root cut families more aggressively;
5. derive a new scalar contradiction for t=5,u=4 or t=3/u=2..5.

Give one concrete next lemma/cut with exact CP-SAT constraints and a proof sketch. Also flag if any of the added reroot equalities look unsafe.
