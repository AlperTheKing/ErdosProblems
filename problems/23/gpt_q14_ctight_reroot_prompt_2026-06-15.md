CONTEXT:
We are attacking Erdos problem #23, the finite value a(30)=36, through a
low-codegree rooted branch. The q=15 branch is closed. The active branch is
q=14/t=2.

Notation for the q=14/t=2 branch:
- There are two root-common-neighbour colour classes C1,C2.
- R has q=14 vertices labelled by subsets of {1,2}: Z=00, S1=10, S2=01,
  D=11.
- U_i is the set of R-vertices whose label contains i.
- R-edges only join disjoint labels.
- p=e(A,B), e_R=e(R), cap=123-p-U-e_R.

Verified facts:
1. Clean/C-tight dichotomy (V131):
   If every r notin U_i has d_R(r,U_i)>=3, we are in the clean side and
   scalar counting leaves only clean z8/d6 rows; these are already closed.
   Otherwise there is a C-tight vertex r notin U_i with d_R(r,U_i)=2.
   Rerooting at the nonedge c_i r gives residual
      q' = 28 - |U_i| - deg(r).
   Therefore if q'<14, the case should reduce to a smaller-q branch.

2. After closing the hard z=3 row, the remaining cap74 scalar frontier contains
   z4=(z,s1,s2,d)=(4,4,4,2), p=12,e_R=25.

3. Generic A-only SAT triage for this z4 row found five relaxed SAT category
   witnesses:
   (zz,zs1,zs2,zd,s12)=
   (0,5,8,4,8), (0,6,5,4,10), (0,6,6,3,10),
   (0,6,8,3,8), (0,8,6,3,8).
   These are not real counterexamples; they are relaxed generic-model SAT rows.

4. Retesting these five rows with the clean-shadow condition gives UNSAT=5.
   Hence they are all on the C-tight side.

5. Direct extraction from the relaxed SAT witnesses shows many C-tight vertices
   with d_R(r,U_i)=2.  In every such extracted certificate, total degree
   deg(r)>=9.  Since |U_i|=6 in z4, this gives q'=28-6-deg(r)<=13.

6. I added a conditional terminal-degree SAT cut:
   if d_R(r,U_i)=2 then deg(r)<=14-|U_i|.
   This removes the visible SAT models, but at 5M conflicts the five categories
   remain UNKNOWN, so the cut alone is not an efficient certificate.

QUESTION:
Give a rigorous way to close the C-tight side for q=14/t=2, or identify the
exact missing hypothesis.

Specifically, prove or refute the following lemma:

Lemma C-tight-reroot:
In a terminal q=14/t=2 counterexample for the a(30)=36 branch, if
r notin U_i and d_R(r,U_i)=2, then deg(r)=8 and |U_i|=6.
Equivalently, any C-tight vertex with 28-|U_i|-deg(r)<14 is impossible because
rerooting at c_i r lands in an already closed q<14 branch.

I need the proof to be operational:
- State exactly what "terminal" must include.
- Explain what the rerooted q' branch is and which parameters are preserved.
- If q<14 closure is required, specify the exact finite statement/certificate
  needed to justify it.
- If the lemma is false, give a concrete obstruction pattern.

REQUIREMENTS:
Do not handwave the reroot. Track the vertex partition after rerooting, the
new R size q', and which cut/degree/beta assumptions survive. End by listing
the weakest step of your argument.
