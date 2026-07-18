# WOWII / Graffiti.pc Conjecture 141 — Approach Registry

Status: ACTIVE after novelty gate (2026-07-18)

Deadline: 2026-07-18T21:57:27+03:00

## DIRECT ROUTE — R1 star plus short geodesic

1. **Exact final deliverable.** Prove for every finite nontrivial connected
   simple graph `G`

   ```text
   floor(girth(G) / 2) - 1 + max_v indepNeighborsCard(G,v)
     <= largestInducedTreeSize(G).
   ```

   Deliver a referee-checkable proof, an exhaustive small-graph check of the
   theorem and construction, and a compiling Lean 4 proof of
   `WrittenOnTheWallII.GraphConjecture141.conjecture141` if the available
   graph-distance/girth API permits completion within the deadline.

2. **Current frontier lemma or finite certificate.** Let `v` maximize local
   independence, let `I` be a maximum independent subset of `N(v)`, and put
   `r = floor(girth(G)/2)-1`.  For cyclic `G` with girth at least four, there
   is a geodesic `v=x0,...,xr`, and the subgraph induced by
   `I union {x0,...,xr}` is a tree of order at least `|I|+r`.

3. **Explicit logical bridge.** A BFS tree rooted at `v` has a non-tree edge,
   whose fundamental cycle proves `girth(G) <= 2*ecc(v)+1`; hence the required
   geodesic exists.  Geodesicity forbids path chords.  Independence forbids
   edges within `I`.  Any other edge from `I` to `xj` closes a cycle of length
   at most `j+2 <= floor(girth/2)+1 < girth`, so the union is induced and
   acyclic.  Its order is at least `|I|+r`, exactly the claimed right-to-left
   bound.  For girth zero or three, the induced star on `{v} union I` is
   already stronger than the target.

4. **Next falsifiable action.** Enumerate every connected graph in the
   NetworkX graph atlas, compute girth, maximum local independence, and maximum
   induced-tree order, then independently construct the star-geodesic witness
   for every cyclic graph.  Exit R1 immediately on a failed inequality or
   failed construction and preserve the smallest graph certificate.

5. **Exit condition.** R1 succeeds only after the written proof passes an
   independent referee check and the exhaustive computation passes; Lean is
   additionally required for a Formal Conjectures submission.  R1 is DEAD on
   a counterexample, a prior proof/PR, a missing logical bridge, or three
   consecutive cycles with no new verifiable fact.  No surrogate asymptotic
   bound or unrelated induced-subgraph reformulation is allowed.

