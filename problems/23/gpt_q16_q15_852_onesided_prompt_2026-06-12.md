CONTEXT: Erdős problem #23. We are working on a finite certificate route for
the q=15 low-codegree branch toward `a(30)=36`. Please do not solve the whole
problem; attack only the finite lemma below.

VERIFIED BACKGROUND:
- In the q=15 branch we have two 5-sets A={a1..a5}, B={b1..b5}, and an
  auxiliary R of size 15. Each r in R has a nonempty label U(r) subset of
  {1,2,3}. R-edges may occur only between disjoint labels.
- Scalar variables: p=e(A,B), eR=e(R), U=sum_r |U(r)|, and M=e(A∪B,R).
  The current hard band is cap M<=52.
- After many shape sweeps, the first remaining profile is `(n1,n2,n3)=(8,5,2)`,
  where n1/n2/n3 count singleton/doubleton/triple labels. All non-one-sided
  support shapes are UNSAT at 100k conflicts. The only hard support shape is,
  up to colour permutation:

    8 vertices S with label {3},
    5 vertices D with label {1,2},
    2 vertices T with label {1,2,3}.

  Hence R-edges are only between S and D; T vertices are isolated in R.
- Shape-family SAT proved p=15 UNSAT. A prior hand cover cut proves p>=19
  impossible. So the live mathematical target is p=16,17,18. It is fine if you
  prove p=16..20 at once.
- For p=16,17,18 we have h=25-p missing A-B edges equal 9,8,7 and
  eR >= 47-p, i.e. eR>=31,30,29 respectively. Since R[S,D] has 8*5=40 possible
  edges, every S has average D-degree at least 29/8 and every D has average
  S-degree at least 29/5 in the weakest p=18 case.

EXACT FINITE CONSTRAINTS FOR THE LEMMA:
Let F be the missing-edge bipartite graph between A and B, so |E(F)|=h.
Each row and column of F has degree at most 2.

Introduce incidence sets X_r subset A and Y_r subset B for each r in R,
meaning r is joined to those A/B vertices. They must satisfy:

1. For every a in A: (5 - deg_F(a)) + |{r: a in X_r}| >= 7.
   For every b in B: (5 - deg_F(b)) + |{r: b in Y_r}| >= 7.
2. For every r with weight w=|U(r)|:
   |X_r| >= 3-w, |Y_r| >= 3-w, and
   |X_r|+|Y_r| >= 8 - deg_R(r) - w.
   In the one-sided shape this means:
   S vertices need |X|,|Y|>=2 and total >= 7-deg_R(s);
   D vertices need |X|,|Y|>=1 and total >= 6-deg_R(d);
   T vertices need total >=5.
3. If a in X_r and b in Y_r then ab must be missing in A-B, i.e. (a,b) in F.
4. If rs is an R-edge then X_r and X_s are disjoint, and Y_r and Y_s are
   disjoint.
5. Colour-hit admissibility: every a in A and b in B has at least two incident
   R-neighbours carrying each colour i. In this one-sided shape:
   - colour 3 hits can come from S or T;
   - colours 1,2 hits can come from D or T.
6. If ab is present in A-B, then a,b have at least 3 common R-neighbours.
7. Any two A-vertices, and any two B-vertices, have at least 2 common
   neighbours, counting shared B/A neighbours through present A-B edges and
   shared R-neighbours.
8. If r is adjacent to a side vertex x in A∪B, then r and x have at least
   3 common neighbours.

QUESTION:
Prove rigorously that no such configuration exists for p=16,17,18
(preferably p=16..20), or identify a smaller lemma that would imply this
case. I need a human-checkable combinatorial argument, not a SAT search.

Please be adversarial about your own answer. If your argument uses an
unstated assumption, flag it. End by listing the weakest steps.
