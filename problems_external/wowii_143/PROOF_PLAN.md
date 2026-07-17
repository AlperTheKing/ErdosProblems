# Proof Plan — WOWII / Graffiti.pc Conjecture 143

## Target

For every finite simple connected non-tree graph G,

t(G) δ′(G) ≥ g(G)+1,

where t(G) is the maximum number of vertices inducing a tree, g(G) is the girth, and δ′(G) is the second entry of the nondecreasing degree sequence.

## Minimal lemma tree

### L0 — Cyclic edge cases

A connected non-tree finite simple graph contains a cycle, hence g(G)≥3 and has at least three vertices.

### L1 — Degree split

Because G is connected and nontrivial, every degree is positive. Therefore:

- δ′(G)≥2; or
- δ′(G)=1, in which case at least two vertices have degree one.

No third case exists.

### L2 — Shortest-cycle tree

A shortest cycle C of length g is chordless. Deleting any one vertex of C leaves an induced path on g−1 vertices. Consequently t(G)≥g−1.

This closes the δ′≥2 case:

tδ′ ≥ 2(g−1) ≥ g+1,

where the final inequality is g≥3.

### L3 — Two-leaf induced-tree lemma (frontier)

If G is connected, cyclic, has girth g, and has two distinct leaves x,y, then t(G)≥g+1.

Proof skeleton:

1. A shortest x–y path is induced, so there is at least one induced tree containing x,y.
2. Choose such a tree T with maximum order among induced trees containing x,y.
3. T is not spanning, because an induced spanning tree would equal G, contradicting that G is cyclic.
4. Connectivity gives a vertex z outside T adjacent to T.
5. If z has exactly one neighbor in T, then T+z is a larger induced tree containing x,y. Hence z has distinct neighbors a,b in T.
6. Let P be the unique a–b path in T. The simple closed walk z-a-P-b-z contains a cycle of length at most |V(P)|+1. Therefore g≤|V(P)|+1.
7. Neither x nor y lies on P: each endpoint of P is adjacent both along P and to z, while each internal vertex has two P-neighbors; all have degree at least two in G.
8. Thus |V(T)|≥|V(P)|+2≥g+1.

### L4 — Assembly

If δ′=1, L1 supplies x,y and L3 gives t≥g+1=tδ′. Together with L2 and the δ′≥2 arithmetic, this proves the target.

## Falsification computation

Enumerate every unlabeled graph in NetworkX's graph atlas (all graphs through seven vertices). For each connected cyclic graph:

1. compute exact girth by shortest cycles;
2. sort exact vertex degrees and take the second entry;
3. enumerate all nonempty vertex subsets and compute the maximum cardinality inducing a connected acyclic graph;
4. test tδ′≥g+1;
5. separately test L3 whenever at least two leaves exist.

The output must include counts, minimum slack, equality witnesses, and a SHA-256 hash of a machine-readable results file. Any violation is preserved as a graph6 certificate and kills W143-A.

## Verification boundary

- Referee pass: independently check L0–L4, including the maximality quantifier in L3 and the fact that extra z–P chords can only shorten the produced cycle.
- Numeric pass: replay the atlas computation with Python optimization disabled.
- Lean 4: first formalize the finite maximal-extension lemma underlying L3; then connect it to the existing definitions of girth, secondSmallestDegree, and largestInducedTreeSize. Use no native_decide.
- Novelty recheck after the proof is complete.
