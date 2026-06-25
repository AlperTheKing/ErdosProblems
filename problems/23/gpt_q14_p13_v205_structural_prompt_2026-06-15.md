CONTEXT

We are attacking Erdos problem #23 via the low-codegree route for a(30)=36.
q=15 is closed.  In q=14,t=2,cap=74, the p=12/e_R=25 layer is closed.
The active frontier is p=13/e_R=24.

Notation:
- Root at a nonedge xy of minimum nonedge-codegree t=2.
- C={c1,c2}, A=N(x)\C, B=N(y)\C, |A|=|B|=6, |R|=14.
- R vertices carry labels recording adjacency to C.
- Scalar row is (z,s1,s2,d,p,e_R,cap):
  z unlabeled R vertices, s1/s2 singleton-label counts, d doubleton count,
  p=e(A,B), e_R=e(R).
- We are in cap=74 with p+e_R=37.

Solver already enforces:
- maximal triangle-free;
- every nonedge has codegree at least 2;
- A/A, B/B, A/R, B/R, and full R/R nonedge-codegree;
- exact rooted Phi/Psi lazy cuts;
- q-minimal terminal C-tight degree cut;
- terminal R-degree cut;
- optional exact-M equality for the A/B incidence total.

The p=12/e_R=25 layer was closed.  Your p=12 orientation-defect lemma for
the 3C4 A-B case was useful: states become orientations on three K2,2
components plus 10 total deletions.

VERIFIED p=13/e_R=24 DATA

z2 row: (2,6,6,0,13,24,74)
- 10k: 333 UNSAT, 4 UNKNOWN, SAT=0.
- 100k tail: 1 additional UNSAT, 3 UNKNOWN, SAT=0.
- 1M tail: 0 additional UNSAT, 3 UNKNOWN, SAT=0.
- exact-M 1M: 0 additional UNSAT, 3 UNKNOWN, SAT=0.
Remaining profiles:
  (zz,zs1,zs2,zd,s12)=(0,4,4,0,16),
  (0,5,5,0,14),
  (0,6,6,0,12).

z3 row: (3,5,5,1,13,24,74)
- 10k: 3321 UNSAT, 35 UNKNOWN, SAT=0.
- 100k tail: 2 additional UNSAT, 33 UNKNOWN, SAT=0.
- 1M tail: 0 additional UNSAT, 33 UNKNOWN, SAT=0.
- exact-M 1M: 0 additional UNSAT, 33 UNKNOWN, SAT=0.
The 33 remaining profiles all have zz=0 and lie in high Z-S / high S1-S2
terminal bands.

z4 row: (4,4,4,2,13,24,74)
- 10k: 9914 UNSAT, 208 UNKNOWN, SAT=0.
- 100k tail: 11 additional UNSAT, 197 UNKNOWN, SAT=0.
Remaining UNKNOWN distribution:
- by zz: 0:148, 1:44, 2:5.
- by zd: 0:1, 1:2, 2:7, 3:14, 4:25, 5:37, 6:43, 7:33, 8:35.
- by s12: 8:57, 9:51, 10:39, 11:27, 12:18, 13:4, 14:1.
An exact-M 1M tail on the 197 UNKNOWN profiles is currently running, but
z2/z3 suggest generic conflict limits and exact-M are not the main lever.

QUESTION

Find the next rigorous p=13 structural obstruction.  I do not want another
generic SAT sweep.  I need a lemma or finite certificate reduction that is
small enough to be proof-checkable and is targeted to the observed hard core.

Possible directions:

1. p=13 A-B structure.
Classify the 13-edge bipartite graph P=G[A,B] on 6+6 enough to generalize the
p=12 orientation/deletion certificate.  Is every hard p=13 type a one-edge
extension of a p=12 2-factor with a small defect budget?  If yes, state the
exact orientation/deletion variables and the total defect identity/inequality.

2. z2 contradiction.
Under zz=0 and profiles
  (0,4,4,0,16), (0,5,5,0,14), (0,6,6,0,12),
derive a contradiction from the two zero vertices, terminal C-tight degree
constraints, R/R nonedge-codegree, and rooted Phi/Psi cuts.  This would close
the first p=13 row.

3. high-ZD z4 obstruction.
For z4, the hard profiles concentrate at high zd and low s12.  Can high Z-D
edge count force too much A/B deletion overlap or violate R/R nonedge-codegree
when p=13,e_R=24,cap=74?

4. cut inequality.
Find a scalar or semi-scalar Phi/Psi cut inequality that all p=13 hard profiles
must violate, using only z,s1,s2,d,zz,zs1,zs2,zd,s12 and terminal constraints.

5. proof-checkable finite certificate.
If no hand contradiction is visible, specify the smallest next certificate:
canonical P types, R skeleton orbit data, orientation/deletion variables,
vertex-cover inequalities, and exact leaf checks.  It should be much smaller
than raw fixed-R SAT and should explain why z2/z3/z4 are hard.

REQUIREMENTS

Give a rigorous complete proof if possible.  If not, give the smallest rigorous
lemma/certificate format that can be implemented next.  Explicitly mark every
extra assumption.  End with:
- weakest steps in your answer;
- the first finite subcase to test;
- exact inequalities or variables the checker should implement.
