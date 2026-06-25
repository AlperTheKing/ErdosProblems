CONTEXT:
We are trying to prove the finite theorem a(30)=36 for Erdos Problem #23:
no triangle-free graph G on 30 vertices has beta(G)=e(G)-MaxCut(G) >= 37.

This question concerns a small residual branch of the q=13, k=3, t=2,
r0=8 rooted reduction.  In this branch the residual R has 13 vertices labelled
by subsets of {1,2,3}; labels are encoded as bitmasks 0..7.  Only five label
classes occur in the rows below:

  2 = S2, 3 = D12, 4 = S3, 5 = D13, 7 = T.

There are original sides A and B with |A|=6 and |B|=7.  For r in R,
alpha_r = |N_A(r)|, beta_r = |N_B(r)|, dR(r) is degree inside R, and
D(r)=alpha_r+beta_r+dR(r)+|L(r)| is the original degree of r.
The cap is EDGE_CAP=111 in this local model:

  ROOT_EDGES + U + p + eR + M <= 111,
  M=sum_r(alpha_r+beta_r).

The exact four rows currently tested are:

  row 43, profile 4971:
    cnt = (0,0,2,2,2,3,0,4)
    fixed_eR = 12
    fixed_p = 25, M in [54,57]
    fixed_p = 26, M in [54,56]

  row 52, profile 5164:
    cnt = (0,0,2,3,2,2,0,4)
    fixed_eR = 12
    fixed_p = 25, M in [54,57]
    fixed_p = 26, M in [54,56]

The current exact-state CP-SAT verifier is:

  search23/verify_q13_t3_r9_profile_cpsat.py

and the row runner is:

  search23/run_q13_exact_rows_parallel.py

VERIFIED / TRUSTED CONSTRAINTS USED:

1. R-edge legality:
   R-edges occur only between disjoint labels.

2. R triangle-freeness:
   no triangle inside R.

3. Local domination:
   for every r missing colour i,
   d_R(r,U_i) >= 2.

4. Root-to-R side codegree:
   alpha_r + |L(r)| >= 2,
   beta_r + |L(r)| >= 2.

5. Degree lower bound:
   D(r)=alpha_r+beta_r+dR(r)+|L(r)| >= 8.

6. Safe H14 anti-tightness cut:
   for every r missing colour i,
   D(r) + |U_i| + d_R(r,U_i) >= 17.
   This is the replacement for an earlier, unsafe terminal-reroot equality.

7. Full R/R edge and nonedge codegrees:
   if rr' is an R-edge, common-neighbour count is 0;
   if rr' is an R-nonedge, common-neighbour count is at least 2.
   Common neighbours include label overlap, A, B, and R-common-neighbours.

8. A/B law:
   an A-B pair is an edge iff its R-state intersection is empty;
   intersection size 1 is forbidden;
   intersection size >=2 is a nonedge with enough R common neighbours.

9. A-root/B-root opposite constraints:
   every A vertex has at least t=2 neighbours in B,
   every B vertex has at least t=2 neighbours in A.

10. A/R, B/R, A/A, B/B codegree constraints.

11. Rooted cut inequalities phi/psi for all R-masks, requiring at least 37
    monochromatic edges in the corresponding rooted cuts.

12. Additional safe but local cuts currently enabled:
    class cuts, isolated-support cuts, mixed-codegree aggregate,
    rectangle wedge cuts, rectangle complete-block cuts, rectangle global cuts,
    state-separator capacity cuts.

ATTEMPTED AND FAILED:

A run with the experimental flag --terminal-closure closed two p=26 rows quickly,
but this is NOT trusted.  GPT Pro previously found that terminal-reroot equality
does not follow from the stated frontier closure.  Therefore this flag is now
forbidden for proof certificates.

The trusted rerun without --terminal-closure used:

  python search23/run_q13_exact_rows_parallel.py
    --rows search23/q13_t2_r8_a6b7_small4_non6195.tsv
    --out search23/q13_t2_r8_a6b7_small4_safe_anti_300.tsv
    --q 13 --k 3 --na 6 --nb 7 --r0 8 --t 2
    --timeout 300 --jobs 4 --workers-per-job 16 --max-total-workers 64
    --anti-tightness
    --class-cuts --isolated-support
    --mixed-codegree-aggregate
    --rectangle-wedge-cuts
    --rectangle-complete-block-cuts
    --rectangle-global-cuts
    --state-separator-capacity

Result:

  all 4 rows UNKNOWN after 300 seconds each.

The output file is:

  search23/q13_t2_r8_a6b7_small4_safe_anti_300.tsv

QUESTION:

Find the shortest rigorous next path to close these four rows without using
the unsafe terminal-closure / terminal-touch equality.

Please do one of the following:

1. Give a new sound structural lemma/cut, preferably P-free or count-level,
   that applies to one or both profiles above.

2. Give a stronger exact encoding that is still a necessary condition and can
   be added to the CP-SAT verifier.  Concrete variable definitions and linear
   constraints are preferred.

3. Find a reason these four rows are actually outside the valid search space
   due to an already-stated constraint being missing from the row generator.

4. Produce a falsification route: a small candidate quotient/model that shows
   why the current constraints are too weak, and identify the missing global
   condition.

Requirements:

- Do not use terminal-reroot degree equalities for the tight vertex or its
  terminal neighbours.
- You may use the safe anti-tightness inequality D(r)+|U_i|+d_R(r,U_i)>=17.
- Every claim should be checkable from the row data and constraints above.
- End by listing the weakest steps of your own answer.
