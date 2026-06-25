CONTEXT:
We are attacking Erdos problem #23, the finite value a(30)=36, via the
low-codegree q=14/t=2 branch.  The q=15 branch is closed.  The active scalar
row is

  z=4, s1=s2=4, d=2, p=12, e_R=25, U=12, cap=74.

Verified reductions:

1. Root nonedge chosen q-minimal among t=2 roots.  Therefore any C-tight
   vertex r notin U_i with d_R(r,U_i)=2 satisfies deg(r)<=14-|U_i|.  In this
   z4 row, |U_i|=6, so such vertices have deg(r)=8.

2. Combining terminal deg=8 with singleton Phi gives the R-side cut

   d_R(r,U_i)=2  =>  d_R(r)<=4.

3. Since p=12, G[A,B] is a 2-regular bipartite graph on 6+6 vertices.
   The C12 template is impossible; only C8+C4, C6+C6, and 3C4 remain.

4. Fixed-template SAT certificates:
   - C8+C4: all remaining z4 categories UNSAT.
   - C6+C6: all remaining z4 categories UNSAT.
   - 3C4: all but 11 categories UNSAT after 10M conflict runs.

The remaining 11 category profiles are exactly:

  (zz,zs1,zs2,zd,s12) =
  (0,5,5,4,11), (0,5,6,4,10), (0,5,7,4,9),
  (0,6,5,4,10), (0,6,6,4,9), (0,7,5,4,9),
  (0,5,5,5,10), (0,5,6,5,9), (0,6,4,5,10),
  (0,6,5,5,9), (1,5,5,4,10).

All are under the 3C4 A-B template.  There are no SAT witnesses; these are
solver-UNKNOWN categories.

QUESTION:
Find a rigorous structural lemma, preferably using the 3C4 component structure,
that eliminates these 11 profiles or further reduces them.

Useful 3C4 facts:
- A and B split into three K_{2,2} components.
- An R-vertex neighbourhood in A union B is an independent set in this 3C4
  graph, so in each component it may use A-side vertices, or B-side vertices,
  or neither, but not both.
- Maximal states of size 6 correspond to choosing one side in each of the
  three components.

Requirements:
- Do not assume the SAT UNKNOWN rows are feasible.
- Track which constraints you use: triangle-free R, disjoint labels, local
  domination d_R(r,U_i)>=2, terminal C-tight cuts, degree lower bound, p=12
  3C4 template, missing nonedge codegree constraints, rooted cut constraints.
- If you propose a finite check, make it smaller than the existing full SAT:
  e.g. a component-state inequality, a dominance/compression rule, or a
  category-level R obstruction.
- End with the weakest step.
