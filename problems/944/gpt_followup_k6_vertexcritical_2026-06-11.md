CONTEXT:
We are studying Erdős problem #944 / the existence of a 6-regular (4,1) graph:
a 6-regular graph G with chi(G)=4 such that every vertex deletion is
3-colourable and no edge deletion is 3-colourable. Equivalently, a 6-regular
4-vertex-critical graph with no critical edge.

Verified local facts:
1. For every vertex v and every 3-colouring of G-v, the neighbours of v have
   colour multiplicities (2,2,2).
2. For any two colours A,B and any (A,B)-Kempe component K in G-v, the number
   of A-coloured neighbours of v in K equals the number of B-coloured neighbours
   of v in K.
3. For colour classes A,B,C in G-v,
   sum over (A,B)-Kempe components K of |delta_G(K)| = 6|C| + 2.
4. If there is a touched non-singleton two-colour Kempe component K with
   |delta_G(K)|=6, then G has a nontrivial 6-edge-cut.

We are trying to prove the K6 lemma:
For some v, some 3-colouring of G-v, and some colour pair, a touched
non-singleton two-colour Kempe component K has |delta_G(K)|=6.

STATUS:
Accounting and balance alone do not prove K6. We verified two finite
countermodels to the local reasoning:

A. A 10-vertex 6-regular graph built from K_{3,3,3} minus a rainbow matching
   plus a vertex v joined to two vertices in each part. It is 4-chromatic and
   has no critical edge. At v, all local (2,2,2), balance, and accounting
   conditions hold, all touched two-colour components are giant balanced
   components with |delta|=20, and no touched |delta|=6 component exists.
   What fails is vertex-criticality: deleting any non-v vertex leaves a K4.

B. A stronger 12-vertex 6-regular graph, graph6 `K?rDtr{~BmMw`. It is
   4-chromatic, has no critical edge, has no K4, and no nontrivial 6-cuts.
   Exactly four vertex deletions are 3-colourable (0,1,4,5); the other eight
   are not. For each successful deletion, all 3-colourings satisfy (2,2,2),
   Kempe balance, and K6 fails locally: touched two-colour components have
   |delta| 20 or 26, never 6.

   For each failed deletion, the minimum induced non-3-colourable subgraphs
   have 7 vertices, 13 edges, degree sequence 3,3,4,4,4,4,4, and are
   vertex-critical as induced subgraphs. The listed cores all contain
   {0,1,4,5} plus one choice from pairs among {6,7}, {8,9}, {10,11}.
   Enumerating all connected 7-vertex 4-critical graphs shows these cores have
   graph6 isomorphism type `FUxuo` (one of the two 7-vertex 4-critical types
   with 13 edges).

Additional verified reducibility/data:
5. A 4-vertex-critical graph has no nonadjacent vertices x,y with comparable
   open neighbourhoods. If N(y) subseteq N(x), then any 3-colouring of G-y
   extends by colouring y the same as x.
6. In the n=12 seed `K?rDtr{~BmMw`, the eight bad vertices form four true
   twin pairs `(2,3),(6,7),(8,9),(10,11)`. This exactly explains why those
   deletions cannot be 3-colourable.
7. However, comparable/twin reducibility is not a complete explanation for all
   small no-critical-edge seeds. A census of n<=12 6-regular no-critical-edge
   seeds shows many non-vertex-critical seeds with no comparable non-neighbour.
   Their failed deletions are instead witnessed by proper induced 4-critical
   atoms. At n=12 the minimum failed-deletion cores have sizes distributed as
   `[4]=78511 [6]=8064 [7]=1946 [8]=1 [9]=24`, all vertex-critical as induced
   subgraphs.

QUESTION:
Can full vertex-criticality be used to rule out this n=12 seed pattern or,
more generally, to prove K6? Please focus on a precise lemma of the following
kind:

  If a 6-regular 4-chromatic graph has no critical edge, and for some
  vertex-deleted 3-colouring every touched two-colour Kempe component has
  boundary at least 8, then either
  (i) G contains a proper induced 4-critical subgraph, or
  (ii) G contains nonadjacent vertices with comparable neighbourhoods, or
  (iii) one can find a touched two-colour Kempe component with boundary 6
        after changing the deleted vertex/colouring.

Give a rigorous argument if you can. If this lemma is false, construct or
outline a counterexample mechanism. Please do not repeat the one-pair
accounting; assume it is known and insufficient. End by listing the weakest
steps of your answer.
