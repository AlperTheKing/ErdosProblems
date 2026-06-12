CONTEXT:
We are working on Erdős problem #944 / the Dirac k=4,r=1 question:
does there exist a 6-regular 4-vertex-critical graph with no critical edge?
Call such a graph a target.

VERIFIED FACTS:
1. In any target, for every vertex v and every 3-colouring of H=G-v, each
   colour appears exactly twice in N(v).
2. If a two-colour Kempe component K in H has unequal counts of the two
   colours among N(v), swapping K creates a singleton colour in N(v), hence a
   critical edge. Thus every Kempe component is balanced at N(v).
3. Exact accounting: for colour classes A,B,C in H,
      sum_{K an (A,B)-Kempe component} |delta_G(K)| = 6|C|+2,
   cyclically.
4. Comparable non-neighbours are impossible in a 4-vertex-critical graph:
   if x,y are nonadjacent and N(y) subset N(x), a 3-colouring of G-y extends
   by colouring y like x.
5. Local Kempe balance/accounting alone does not force K6. We found small
   6-regular no-critical-edge seeds where all touched Kempe components have
   boundary >=8, but the graphs fail vertex-criticality.

TERMINAL LIST-BLOCKER SETUP:
Fix v and a 3-colouring phi of H=G-v. Let colour A occur on exactly two
neighbours a,a' of v. Since edge va is not critical, G-va is not 3-colourable.
Define a list assignment L_a on H:
  L_a(a) = {A,B,C};
  L_a(x) = {B,C} for x in N(v)\{a};
  L_a(x) = {A,B,C} otherwise.
Then H is not L_a-colourable. Since G-a is 3-colourable, after permuting
colours so v receives A, H-a is L_a-colourable. Therefore a minimal induced
L_a-uncolourable blocker Q_a exists and contains both terminals a,a'.

NEW LOCAL DATA:
I wrote an exact C++ blocker extractor. For the best n=12 6-regular
no-critical-edge seed K?rDtr{~BmMw, the target-like cases (those with H-a
L_a-colourable) all have minimum terminal blockers of size 6. Every such
blocker:
  - contains a and a';
  - is ordinary 3-colourable as a graph;
  - is inclusion-minimal as an L_a-uncolourable induced subgraph;
  - has 9 internal edges;
  - has degree sequence 2,3,3,3,3,4;
  - has boundary 18 in the full seed;
  - has graph6 E\xO.
One labelled representative has vertices p,q,r,s,t,u and edges
  pr, ps, pt, qr, qt, qu, rs, rt, su.
In the seed this is still not a target because other vertex deletions fail
through true twins / 7-vertex 4-critical cores.

QUESTION:
Please attack the following sharply-scoped lemma.

Lemma TB6-to-K6 candidate:
Let G be a genuine 6-regular target. Assume for contradiction that G is
Kempe-expanding: for every v, every 3-colouring of G-v, and every touched
non-singleton two-colour Kempe component K, |delta_G(K)| >= 8. Fix v, phi,
and terminals a,a' as above, and let Q_a be a minimal L_a-uncolourable blocker.

Can Q_a be a 6-vertex blocker of the labelled type
  edges pr, ps, pt, qr, qt, qu, rs, rt, su
with terminals a,a' in Q_a?

Either:
  (A) prove this shape is impossible in a genuine target under Kempe-expansion;
  (B) prove this shape forces a touched boundary-6 Kempe component (K6);
  (C) or give a concrete consistent local configuration showing why this
      finite sublemma is false.

REQUIREMENTS:
Give a rigorous argument, not a sketch. Use only the facts listed above unless
you explicitly prove additional lemmas. If you cannot close the lemma, identify
the exact obstruction and propose the next smaller lemma. End by listing the
weakest steps of your answer.
