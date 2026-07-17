# Independent logical referee report

## Verdict: ACCEPT

I found no logical gap in `PROOF.md`.  This review treats the proof as a
standalone argument and does not use either atlas computation as evidence.

## Detailed checks

1. **Existence and maximality of `T`.**  A shortest `x`--`y` path is induced:
   any edge joining two nonconsecutive path vertices would shorten it.  Its
   induced subgraph is therefore a tree containing `x,y`.  Finiteness then
   permits a maximum-order member `T=G[S]` of this nonempty class.  The proof
   only needs maximum *order* among trees containing this fixed leaf pair,
   which is exactly what is chosen.

2. **Boundary vertex `z`.**  Because `G` is cyclic while `G[S]` is a tree,
   `S` cannot equal `V(G)`.  Since `S` is nonempty and `G` is connected, an
   edge crosses from `S` to its complement; its outside endpoint supplies the
   asserted `z`.

3. **Number of neighbours of `z` in `T`.**  The chosen `z` has at least one
   neighbour in `S`.  If it had exactly one, the *induced* graph on
   `S union {z}` would consist of `T` plus one pendant vertex, hence would be a
   larger induced tree still containing `x,y`.  This contradicts maximality,
   so `z` has at least two distinct neighbours in `S`.  No unspoken
   inclusion-maximality assumption is used here.

4. **The cycle through `P`.**  For distinct neighbours `a,b`, the tree `T`
   has a unique simple `a`--`b` path `P`.  As `z` is outside `S`, the edges of
   `P` together with `za,zb` form a simple cycle with
   `|V(P)|+1` edges.  Extra edges from `z` to internal vertices of `P` do not
   destroy this cycle.  Consequently `g(G) <= |V(P)|+1`.

5. **Why both leaves are outside `P`.**  Each internal vertex of `P` has two
   incident path edges.  Each endpoint has one incident path edge and its edge
   to `z`; these are distinct even when `a,b` are adjacent.  Thus every vertex
   of `P` has degree at least two in `G`, whereas `x,y` have degree one.
   Therefore `V(P), {x}, {y}` are pairwise disjoint subsets of `S`, giving
   `|S| >= |V(P)|+2 >= g(G)+1`.  This proves the two-leaf lemma.

6. **The two main cases.**  In a finite connected cyclic simple graph every
   degree is a positive integer, so the second-smallest degree is either `1`
   or at least `2`.  A shortest cycle is chordless, since either arc together
   with a chord would give a shorter cycle.  Removing one cycle vertex thus
   leaves an induced path of order `g-1`; hence in the second case
   `t delta' >= 2(g-1) >= g+1`, using `g>=3`.  In the first case the first two
   entries of the degree sequence are both `1`, so there are two distinct
   leaves and the lemma gives the desired inequality.  The split is exhaustive.

7. **Trees and the `girth=0` convention.**  The current formal-conjectures
   declaration assumes a nontrivial vertex type and explicitly assumes
   `0 < secondSmallestDegree G`.  For a connected tree in this domain, the
   whole graph is an induced tree, `t=|V(G)|>=2`, `delta'>=1`, and `g=0`;
   therefore `t delta'>=2>=1=g+1`.  The one-vertex graph is excluded by the
   formal `Nontrivial` hypothesis, so there is no omitted zero-denominator
   corner case.

8. **Sharpness family.**  The two pendant vertices give two degree-one entries,
   so `delta'=1`.  Their attachment points occupy at most two vertices of
   `C_g`; because `g>=3`, choose a cycle vertex supporting neither leaf.
   Deleting it leaves an induced tree consisting of a path on `g-1` cycle
   vertices plus both leaves, of total order `g+1`.  An induced tree cannot
   use all `g+2` vertices because the full induced graph contains `C_g`.
   Hence `t=g+1`, establishing equality exactly as claimed.  This also covers
   the case in which the two leaves share an attachment point.

## Editorial issue (not a mathematical defect)

Before circulation, repair the damaged math escapes in `PROOF.md`.  The file
contains a form-feed byte on line 20 (the intended `frac`) and two backspace
bytes on line 65 (the intended `bigl`/`bigr`), and other backslashes such as
those in `notin` and `cup` have disappeared.  These encoding artifacts make
the displayed formulas malformed but do not change the recoverable argument
reviewed above.
