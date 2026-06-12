CONTEXT:
We are attacking Erdos Problem #944 / Dirac k=4,r=1, focusing now on the
explicit Skottova-Steiner 2025 subproblem: does there exist a 6-regular
(4,1)-graph?

A 6-regular (4,1)-target means a finite simple graph G such that:
- deg_G(v)=6 for all v,
- chi(G)=4,
- chi(G-v)=3 for every vertex v,
- chi(G-e)=4 for every edge e, so no edge is critical.

VERIFIED LEMMAS / DATA:
1. Local multiplicity. For any 3-colouring of G-v, every colour appears at
   least twice in N(v). Since deg(v)=6, the colour multiplicities on N(v) are
   exactly (2,2,2).
2. Triangle bound. Every edge lies in at most 4 triangles.
3. Exact 6-cut conflict count. For any nontrivial 6-edge-cut between proper
   shores and fixed 3-colourings of the two shores, every permutation of one
   side's colours creates exactly two monochromatic cut edges.
4. Cut-matrix restriction. The row/column sum types for such a 6-cut are only
   (6,0,0), (4,1,1), (3,3,0), or (2,2,2), up to permutation, with the five
   canonical matrix types machine/Lean checked.
5. Kempe tether. If a 6-cut gluing has conflict edges {e,f}, then for a
   conflict edge e=xy of colour a and every b!=a, x and y are in the same
   (a,b)-Kempe component of G-{e,f}. Important: this is global in G-{e,f},
   not automatically shore-internal.
6. Vertex-form Kempe tether. In any 3-colouring of G-v, each same-colour pair
   in N(v) must be Kempe-tethered to the two other colour classes; otherwise
   a Kempe swap makes one incident edge critical.
7. Exhaustive verified finite exclusions: no 6-regular target on n<=14. Also
   no nontrivial 6-edge-cut shore of size 2..14 in any 6-regular target. Hence
   any target on n<=29 would be super-6-edge-connected.

STATUS:
The current partial result is not a full solution. We need a general-n
mathematical step, not more blind enumeration. The most promising route seems
to be proving that any hypothetical 6-regular target must have a small
nontrivial 6-edge-cut shore, or otherwise deriving a contradiction from local
(2,2,2) colour-neighbourhoods plus Kempe tethers plus high cyclic
edge-connectivity.

QUESTION:
Find a rigorous route toward proving that no 6-regular (4,1)-target exists.
Please try hard to prove one of the following concrete global lemmas, or
explain precisely why it is false and give a better lemma:

(A) Every 6-regular (4,1)-target has a nontrivial 6-edge-cut with a shore of
    size <=14.
(B) In every 6-regular 4-vertex-critical graph with no critical edge, some
    vertex-deleted 3-colouring violates the forced (2,2,2) neighbourhood
    condition.
(C) Every minimal 6-regular target forces a reducible configuration of bounded
    size, such as a small atom, comparable non-neighbours at a boundary-free
    vertex, or a Kempe-tether contradiction.

REQUIREMENTS:
- Do not answer with computation/enumeration as the main solution.
- Give a complete proof if you see one; otherwise give the single smallest
  sharply stated lemma that you believe is both true and attackable next.
- Be adversarial: list the weakest step(s) of your own reasoning.
- Do not cite a theorem unless you are confident it exists; flag uncertain
  citations.
- Avoid repeating known Proposition 5.1 style edge-connectivity facts unless
  they are used in a new way.
