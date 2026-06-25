CONTEXT

We are attacking Erdos problem #23 via the q=14,t=2 low-codegree branch for
a(30)=36.  q=15 is closed.  In q=14,t=2,cap=74:

- the p=12/e_R=25 layer is closed;
- the z2 p=13/e_R=24 row is closed by a defect-budget lemma plus a p=13
  A-B template finite certificate;
- the current frontier is z3 p=13/e_R=24.

Notation:
- C={c1,c2}, A=N(x)\C, B=N(y)\C, |A|=|B|=6, |R|=14.
- R labels: Z label 0, S1 label {1}, S2 label {2}, D label {1,2}.
- Scalar row (z,s1,s2,d,p,e_R,cap).
- Category profile (ZZ,ZS1,ZS2,ZD,S12).
- We are in cap=74 and p+e_R=37.

Solver/hypotheses already enforced:
- maximal triangle-free;
- every nonedge has codegree at least 2;
- exact p=13 A-B template P with row/column degrees (3,2,2,2,2,2);
- exact-M: sum_R (|X_r|+|Y_r|)=74;
- terminal C-tight degree normalization and terminal R-degree cuts;
- full A/A, B/B, A/R, B/R, R/R codegree constraints;
- exact rooted Phi/Psi cuts.

KNOWN p=13 z2 REDUCTION

For z2 row (2,6,6,0,13,24,74), the defect budget kills profiles
(0,5,5,0,14) and (0,6,6,0,12), leaving only (0,4,4,0,16), which was
closed by the 14-template p=13 finite certificate.

The p=13 exact templates are in search23/p13_templates.tsv.  The z3 hard
leaves use only templates:

id rows_hex        state_count
6  7,3,5,18,28,30  306
7  7,3,9,c,30,30   308
10 7,9,9,12,24,30  303
12 7,9,11,6,28,30  303
13 7,9,11,22,24,18 299

CURRENT VERIFIED z3 DATA

For row (z,s1,s2,d,p,e_R,cap)=(3,5,5,1,13,24,74):

Generic RR-codegree exact-M solver left 33 UNKNOWN profiles.
Splitting by the 14 exact p=13 A-B templates and running at 1M conflicts gave:

444 UNSAT, 18 UNKNOWN, SAT=0.

The remaining fixed-template leaves are:

(profile_idx,template,zz,zs1,zs2,zd,s12)
(219,6,0,3,6,3,12)
(283,6,0,4,6,3,11)
(335,12,0,5,3,3,13)
(339,6,0,5,4,3,12)
(343,6,0,5,5,3,11)
(345,6,0,5,6,1,12)
(347,7,0,5,6,3,10)
(399,6,0,6,3,3,12)
(403,6,0,6,4,3,11)
(406,6,0,6,5,2,11)
(407,7,0,6,5,3,10)
(407,10,0,6,5,3,10)
(408,7,0,6,6,0,12)
(408,12,0,6,6,0,12)
(408,13,0,6,6,0,12)
(410,6,0,6,6,2,10)
(410,10,0,6,6,2,10)
(467,13,0,7,4,3,10)

A 10M tail on exactly these 18 leaves is currently running, but we need a
structural cut, not just larger SAT.

QUESTION

Find a rigorous local obstruction that kills or sharply reduces these 18 z3
p=13 fixed-template leaves.

Useful angles:

1. Extend the z2 defect-budget lemma to z3 with one D vertex.  The hard leaves
all have zz=0 and zd often 3; can high Z-D plus high Z-S force terminal defect
>10?

2. Use exact reconstruction of S1-S2 edges.  For u in S1, v in S2,
common neighbours are zeros, D vertices when applicable, and A/B overlaps.
Can the listed profiles force too many K_uv=0 pairs or forbid K_uv=1?

3. Use the p=13 template rows_hex structure.  Do templates 6/7/10/12/13 have
a shared small separator/degree-3 pattern that creates a vertex-cover or
rectangle-cover lower bound exceeding the defect budget?

4. Derive a scalar or semi-scalar cut using only
zz,zs1,zs2,zd,s12 and the terminal tight-defect formula.

5. If no hand proof is visible, specify the next smallest certificate:
additional zero/D skeleton orbits, state variables, and exact leaf checks.

REQUIREMENTS

Give a complete proof if possible.  If not, give the smallest rigorous lemma
or proof-checkable certificate extension.  Explicitly mark any extra
assumption.  End with:
- weakest steps;
- first finite subcase to test among the 18 leaves;
- exact inequalities/variables to implement.
