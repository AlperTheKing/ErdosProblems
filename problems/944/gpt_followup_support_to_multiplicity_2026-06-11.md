CONTEXT:
We are attacking Erdős #944 / Dirac k=4,r=1. A target is a finite 6-regular
graph G that is 4-vertex-critical and has no critical edge. We want to prove
no target exists.

VERIFIED FACTS:
1. In every deleted-vertex 3-colouring phi of H=G-v, the neighbours of v have
colour multiplicities (2,2,2).
2. Kempe balance: every two-colour Kempe component has equal counts of the two
corresponding terminal colours in N(v).
3. Accounting: sum over (A,B)-Kempe components of |delta_G(K)| = 6|C|+2,
cyclically.
4. Global terminal-list-criticality: for terminal a, list assignment L_a on
H=G-v is not colourable, but every proper induced subgraph of H is L_a-colourable.
5. Boundary-support obstruction (verified paste proof):
   Let a,a' be the A-terminals and let K be the (A,B)-Kempe component containing
   a'. Let R_C(K) be the vertices of K with at least one neighbour outside K
   coloured C. If M_{a,K} is L_a restricted to K with colour C additionally
   forbidden on R_C(K), then K is not M_{a,K}-colourable.
   Equivalently: every L_a-colouring of K must use colour C somewhere on R_C(K).

LOCAL DIAGNOSTIC:
A C++ diagnostic on the n=12 no-critical-edge seed confirms that
boundary-support-criticality alone is too weak: mate components have
M-colourable=0 but boundary 20 or 26. However that seed is not
vertex-critical/global-list-critical: each L_a unlocks only 3/11 or 4/11
one-vertex deletions, while a genuine target requires H-y to be L_a-colourable
for every y in H.

QUESTION:
Attack the following narrowed lemma.

Support-to-multiplicity lemma:
In a genuine 6-regular target, with the setup above, if K is a touched
boundary-support-critical (A,B)-Kempe component containing a', then:

- if K has terminal type (1,1), prove e_H(K,C) <= 4;
- if K has terminal type (2,2), prove e_H(K,C) <= 2.

This would imply |delta_G(K)| <= 6; combined with the nontrivial 6-edge-cut
lower bound, it gives K6.

Please either:
1. give a rigorous proof of this support-to-multiplicity lemma using
   6-regularity, vertex-criticality, no-critical-edge, comparable-neighbour
   exclusion, and all six L_a global-criticalities; or
2. construct a genuine obstruction showing the lemma is false even under these
   target-level hypotheses; or
3. isolate a still smaller lemma whose proof would imply support-to-multiplicity
   and is not merely a restatement of K6.

REQUIREMENTS:
- Do not repeat the boundary-support paste proof; it is already verified.
- Do not use quotient-only countermodels unless you explain exactly which
  target-level hypothesis they fail.
- Focus on converting support size/list-forcing into the number of third-colour
  boundary edges e_H(K,C).
- Pay special attention to the global one-deletion condition:
  for every y in H, H-y is L_a-colourable.
- End with weakest steps and a route assessment.
