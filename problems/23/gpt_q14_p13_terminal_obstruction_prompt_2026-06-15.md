CONTEXT

We are attacking Erdos problem #23 via the low-codegree route for a(30)=36.
q=15 is closed.  In q=14,t=2, cap74, the p=12/e_R=25 layer is now closed
computationally.  The current frontier has p>=13.

Notation:
- Root at a nonedge xy of minimum nonedge-codegree t=2.
- C={c1,c2}, A=N(x)\C, B=N(y)\C, |A|=|B|=6, |R|=14.
- R vertices carry labels recording adjacency to C.
- Scalar row is (z,s1,s2,d,p,e_R,cap), where z is unlabeled R vertices,
  s1/s2 singleton label counts, d doubleton count, p=e(A,B), e_R=e(R).
- We are in cap=74 with p+e_R=37.
- Solver already enforces:
  maximal triangle-free;
  every nonedge has codegree at least 2;
  A/A, B/B, A/R, B/R, and R/R nonedge-codegree constraints;
  exact rooted Phi/Psi lazy cuts;
  q-minimal terminal C-tight degree cut;
  terminal R-degree cut;
  R/R nonedge-codegree including label overlap, R common neighbours, and A/B
  incidence overlap.

RECENT VERIFIED COMPUTATIONAL FACTS

The p=12/e_R=25 cap74 layer is closed:
- z2 (2,6,6,0,12,25,74): closed.
- z3 (3,5,5,1,12,25,74): closed earlier.
- z4 (4,4,4,2,12,25,74): closed.
- z5 (5,3,3,3,12,25,74): closed.
- z6 (6,2,2,4,12,25,74): closed.

The p=12 proof was helped by the p=12 A-B 2-factor split.  In the 3C4 case,
your orientation-defect lemma explained the hard band:
actual A/B states can be encoded by orientations on 3 K2,2 components plus
10 total deletions.

NOW ACTIVE: p=13/e_R=24 cap74.

z2 row:
(z,s1,s2,d,p,e_R,cap)=(2,6,6,0,13,24,74)
Generic RR-codegree solver:
- 10k: 333 UNSAT, 4 UNKNOWN, 0 SAT.
- 100k tail: 1 more UNSAT, 3 UNKNOWN, 0 SAT.
- 1M tail: 0 more UNSAT, 3 UNKNOWN, 0 SAT.
- exact-M 1M tail: 0 more UNSAT, 3 UNKNOWN, 0 SAT.
Remaining profiles:
(zz,zs1,zs2,zd,s12)=(0,4,4,0,16), (0,5,5,0,14), (0,6,6,0,12).

z3 row:
(z,s1,s2,d,p,e_R,cap)=(3,5,5,1,13,24,74)
Generic RR-codegree solver:
- 10k: 3321 UNSAT, 35 UNKNOWN, 0 SAT.
- 100k tail: 2 more UNSAT, 33 UNKNOWN, 0 SAT.
- 1M tail is currently running.
The 33 UNKNOWN profiles are all zz=0 and include:
(0,3,3,3,15), (0,3,4,3,14), (0,3,5,3,13),
(0,3,6,3,12), (0,4,3,3,14), (0,4,4,2,14),
(0,4,4,3,13), ..., (0,7,5,2,10).

QUESTION

We need a structural cut for p=13/e_R=24 analogous in spirit to the p=12
orientation-defect lemma.

In p=13, G[A,B] has 13 edges, so the complement on 6+6 has 23 missing cells.
Equivalently, relative to a p=12 row, there is one extra A-B edge and one
fewer R-edge.  The remaining hard profiles are zero-edge-free inside Z
(zz=0), with high Z-S and S1-S2 counts.

Please find a rigorous local lemma that rules out or sharply reduces the z2
remaining profiles:

  (0,4,4,0,16), (0,5,5,0,14), (0,6,6,0,12)

under the listed q=14/t=2 terminal hypotheses.

Useful target forms:

A. A p=13 analogue of the p=12 orientation-defect certificate: classify
   the possible 13-edge A-B graphs or their missing-cell structure enough to
   get a small deletion/cover inequality.

B. A direct contradiction for the z2 profiles using the two zero vertices:
   no ZZ edge, exact ZS1/ZS2 counts, high S1S2 count, terminal C-tight
   degree constraints, and R/R nonedge-codegree.

C. A rooted Phi/Psi cut that must be violated by one of these profiles after
   summing over singleton/zero classes, without enumerating A/B states.

D. A finite certificate reduction smaller than raw SAT: e.g. enumerate
   canonical p=13 A-B graph types, orientation/deletion states, or vertex-cover
   constraints, with a proof-checkable inequality.

REQUIREMENTS

Give a complete proof if possible.  If not, give the smallest rigorous lemma
or certificate format that we can implement next.  Use only the stated
hypotheses, or explicitly flag any extra assumption.  End by listing the
weakest steps and the first finite subcase to test.
