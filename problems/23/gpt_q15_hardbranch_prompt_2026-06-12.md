CONTEXT:
We are attacking Erdos problem #23, finite target a(30)=36.

Verified reductions so far:

1. A hypothetical counterexample can be maximalized with n=30, e<=139,
   beta>=37.
2. By Wang--Yang--Zhao, if every nonedge has >=4 common neighbours, then the
   graph is C5-homomorphic and beta<=e/5<37.  Therefore a counterexample has a
   nonedge xy of codegree 1..3.
3. Root at a minimum nonedge-codegree pair.  In the q=15 branch this forces:

   t=delta_2(G)=3,
   |C|=3,
   |A|=|B|=5,
   |R|=15.

Let C={c1,c2,c3} and U_i=N_R(c_i).

Certificate-safe constraints:

- |U_i|>=6.
- U_i is independent.
- every r in R\U_i has at least 3 neighbours in U_i.
- U_i cap U_j is nonempty.
- R is triangle-free.

Scalar variables:

p=e(A,B), e_R=e(R), U=sum_i |U_i|.

Scalar feasibility includes:

p+e_R>=37,
L_A,L_B >= max(45-U, 35-p, 34-e_R, 0),
L_A+L_B <= 123-p-U-e_R,
and degree-demand lower bound
L_deg=sum_r max(2(3-w(r)), 8-d_R(r)-w(r), 0)
must fit into the same edge budget.

Computation:

The scalar split found scalar survivors, so scalar inequalities alone do not
kill q=15.

The first hard scalar branch isolated by exact SAT is:

p=25, e_R=34, U=35, cap=29.

The diagnostic blocked 100000 concrete (R,U_i) assignments in this single
branch using type availability and paired rooted-cut tests, but did not close
the branch.

One concrete hard assignment is in:
E:\Projects\ErdosProblems\search23\q15_ru_first_hardjob_500\HARD_JOB.txt

Its label pattern:

labels:
0:7, 1:7, 2:0, 3:7, 4:7, 5:7, 6:7, 7:3,
8:7, 9:7, 10:7, 11:7, 12:0, 13:7, 14:0

That means eleven vertices are in all three U_i, three vertices are in no U_i,
and one vertex is in U_1 cap U_2 only.

QUESTION:
Find a rigorous hand-checkable pruning lemma for the q=15 branch, focused on
the hard scalar region p=25, e_R=34, U=35.

Preferred outcomes:

1. Prove this scalar region is impossible from the pure (R,U_i) constraints
   plus paired rooted-cut inequalities.
2. Or derive a stronger compact certificate condition that blocks whole
   families of label patterns, not individual assignments.
3. Or prove that a label pattern with many full-label vertices, e.g.
   eleven vertices of label 7 and three vertices of label 0, violates a paired
   rooted cut or degree/codegree demand.

Requirements:

- State each lemma precisely.
- Give a complete proof.
- Identify exactly which verified reduction/constraint it uses.
- If you propose a computation, it must be smaller than full assignment
  blocking and must output a compact certificate.
- If no proof is visible, say so and identify the exact obstruction.
