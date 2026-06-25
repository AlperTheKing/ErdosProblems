CONTEXT

We are attacking Erdos problem #23 via the low-codegree route for a(30)=36.
The already verified part: q=15 is closed.  The active branch is q=14, t=2,
cap=74, p=12, e_R=25.

Notation:
- We root at a nonedge xy of minimum nonedge-codegree t=2.
- C={c1,c2}, A=N(x)\C, B=N(y)\C, |A|=|B|=6, |R|=14.
- R vertices carry labels recording adjacency to C.  The scalar row is
  (z,s1,s2,d,p,e_R,cap), where z is unlabeled R vertices, s1/s2 singleton
  label counts, d doubleton count, p=e(A,B), e_R=e(R).
- We are in the extremal p+e_R=37 layer.
- p=12 implies the bipartite complement of G[A,B] is a 2-regular graph on
  6+6 vertices.  We split into three templates:
  p0 = C8+C4, p1 = C6+C6, p2 = 3C4.

VERIFIED LEMMAS / CONDITIONS ALREADY IN THE SOLVER

1. Maximal triangle-free and minimum nonedge-codegree 2:
   every nonedge has at least two common neighbours.

2. All A/A, B/B, A/R, B/R, and R/R nonedge-codegree constraints are encoded.
   R/R nonedges count common neighbours from label overlap, R common
   neighbours, and A/B incidence overlap.

3. q-minimal terminal normalization:
   if r is not in U_i and d_R(r,U_i)=2, then rerooting at c_i r gives
   q' = 28 - |U_i| - deg(r).  Since q=14 is chosen minimal, deg(r)<=14-|U_i|.
   In the current p=12 cap=74 terminal rows |U_i|=6, hence such a C-tight
   vertex has deg(r)<=8.  Branch degree lower gives deg(r)>=8, so deg(r)=8.

4. Singleton Phi cut:
   for singleton W={r}, m_R(r)+|label(r)| >= d_R(r).
   Combined with (3), in the terminal rows this gives d_R(r)<=4 for C-tight
   vertices.

COMPUTATIONAL STATUS

Rows closed:
- z=3,s1=s2=5,d=1,p=12,e_R=25 closed.
- z=4,s1=s2=4,d=2,p=12,e_R=25 closed, but p2=3C4 required an R/R
  codegree tail.

Current z=2 row:
- scalar row (z,s1,s2,d,p,e_R,cap)=(2,6,6,0,12,25,74).
- p0 and p1 templates: all 21 residual categories UNSAT at 100k.
- p2=3C4:
  100k closed 16/21, 5 UNKNOWN.
  5M closed 3/5, 2 UNKNOWN.
  20M closed both remaining UNKNOWNs.
- The last profile was extremely hard:
  (zz,zs1,zs2,zd,s12)=(0,4,4,0,17).
  This profile is now computationally UNSAT, but it looks like the central
  mathematical obstruction.

Current z=5 row:
- scalar row (z,s1,s2,d,p,e_R,cap)=(5,3,3,3,12,25,74).
- p0=C8+C4: all 14740 categories UNSAT at 10k.
- p1=C6+C6: all 14740 categories UNSAT at 10k.
- p2=3C4 is running.  At the interrupted 126-worker point:
  valid done=12368/14740, UNSAT=12160, SAT=0, UNKNOWN=208, pending=2372.
  It is now continuing at 100 workers.
- UNKNOWN p2 categories have the form low zz and relatively high zd/s12.
  Early examples:
  (zz,zs1,zs2,zd,s12)
  (0,1,3,13,8), (0,1,4,12,8), (0,1,4,13,7),
  (0,1,5,10,9), (0,1,5,11,8), ...
  plus similar shifts with zz=1.

QUESTION

Find a rigorous mathematical lemma, preferably local and hand-checkable, that
explains the p2=3C4 terminal obstruction and would reduce or eliminate the
remaining hard categories without broad SAT.

Target one of these:

A. A direct contradiction for the z=2 central profile
   (zz,zs1,zs2,zd,s12)=(0,4,4,0,17) under the listed conditions.

B. A structural lemma for p=12, 3C4 template, p+e_R=37 terminal rows:
   for example, show that some C-tight vertex violates the deg=8/d_R<=4
   terminal constraints, or that an R/R nonedge has codegree <=1, or that a
   rooted Phi/Psi cut is violated.

C. A sharper counting inequality involving the 3C4 A-B complement and the
   R-label edge profile (zz,zs1,zs2,zd,s12) that rules out the low-zz,
   high-zd/s12 UNKNOWN band seen in z=5.

REQUIREMENTS

Give a complete proof, not a sketch.  Use only the hypotheses stated above.
If you need an extra hypothesis, state it explicitly and explain whether it is
already part of the low-codegree setup.  End by listing the weakest steps of
your answer and any finite subcase that should be tested first.
