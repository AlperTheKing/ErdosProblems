# W144-IND2 large-order falsification audit

## Exact statement audited

For a connected cyclic graph `X`, write

```text
eta(X) = max_x d_X(x, C(X)),
phi(X) = girth(X) + eta(X),
beta(X) = |E(X)| - |V(X)| + 1.
```

The audited multicyclic deletion lemma is

```text
beta(G) >= 2 and girth(G) >= 5
  ==> there is v such that G-v is connected and cyclic
      and phi(G-v) >= phi(G).
```

This is the parameter-only W144-IND2 frontier.  It is not asserted here as a
theorem.

## Reproducible audit

Run

```text
python problems_external/wowii_144/attack_ind2_multicycle/verify_ind2_large_audit.py \
  --seed 14420260718 --random-trials 12000 \
  --output problems_external/wowii_144/attack_ind2_multicycle/ind2_large_audit_results.json
```

The verifier recomputes, from each graph itself:

1. connectivity and cycle rank;
2. girth by breadth-first search from every vertex;
3. every vertex eccentricity, the complete center set, and `eta`;
4. admissibility and all invariants after a candidate deletion.

It stops at the first nonnegative-slack deletion.  If no such deletion exists,
it recomputes and writes the complete deletion table, including adjacency
list, graph6, centers, radii, girths, etas, phis, and slacks.  Therefore the
reported slack distribution is the distribution of the *first witness*, not
the maximum deletion slack.

The deterministic corpus has 4,590 labelled records of orders 14 through 40:

- three-path theta cores with one or two asymmetric tails;
- two-cycle handcuff/figure-eight block configurations with bridges and tails;
- a shortest-cycle core with a second high-girth ear and one or two tails.

The seeded corpus has 12,000 records of orders 14 through 40, alternating:

- a cycle with randomly accepted girth-preserving ears and attached trees;
- a random labelled tree with randomly accepted long-distance chords;
- a random connected multicyclic core with every edge subdivided, followed by
  attached trees.

Every order from 14 through 40 occurs at least 429 times in the combined
corpus.  All 16,590 records had a valid deletion witness.  Of the first
witnesses, 14,070 had slack zero.  No counterexample was found.

The exact result file has SHA-256

```text
420C2BF3E173A4BA98B52FA95ACD85766AF014093A95D27DE521CEDFFC7068D6
```

This is falsification evidence only, not a finite proof of the unrestricted
lemma.

## One structural reduction: a shortest-cycle exterior deletion

**Lemma (exterior deletion).** Let `G` be a finite connected simple graph,
let `K` be a shortest cycle of `G`, and suppose `beta(G) >= 2`.  Then there is
a vertex `v` outside `K` for which `G-v` is connected, contains `K`, and hence
is cyclic with

```text
girth(G-v) = girth(G).
```

Moreover, `v` may be chosen from the following direct candidate class: if
`G` has a leaf, choose a leaf; otherwise choose a non-cut vertex outside `K`,
which then lies in the 2-core of `G`.

**Proof.** A shortest cycle is induced.  If every vertex of `G` lay on `K`,
simplicity and inducedness would give `G=K` and `beta(G)=1`, a contradiction.
Thus `V(G)-V(K)` is nonempty.

If `G` has a leaf, that leaf is outside every cycle.  Deleting it leaves a
connected graph still containing `K`, so it has the required properties.

Now assume that `G` has no leaf.  Delete one edge of `K` and extend the
resulting tree on `V(K)` to a spanning tree `T` of `G`.  Root `T` in
`V(K)`, and choose an exterior vertex `v` of maximum distance from `V(K)` in
`T`.  Since the tree already connects all vertices of `K` internally, `v`
has no child in `V(K)`; maximality gives no exterior child.  Hence `v` is a
leaf of `T`.  Consequently `T-v` is a spanning tree of `G-v`, so `G-v` is
connected.  It still contains `K`, and deletion cannot create a shorter
cycle, proving equality of the girths.  Finally, the no-leaf assumption gives
minimum degree at least two, so every vertex, in particular `v`, lies in the
2-core.  QED.

## Exact consequence for a phi-critical graph

Call `G` phi-critical if every admissible deletion has smaller `phi`.  The
lemma shows that a multicyclic phi-critical graph cannot be protected by a
connectivity or girth change: for every shortest cycle it has a leaf or an
exterior 2-core deletion that preserves the girth exactly.  Therefore every
such candidate would have to satisfy the strict metric drop

```text
eta(G-v) < eta(G).
```

Thus the single remaining structural issue is whether simultaneous
`eta`-criticality of all these shortest-cycle exterior candidates forces
`beta(G)=1`.  Proving that statement would make every minimal phi-critical
graph unicyclic and close the multicyclic IND2 frontier.  The present audit
does not prove that metric assertion.

## Exact limit of the exterior lemma

**Correction to the preceding proposed metric issue.**  Simultaneous eta-criticality
of the girth-preserving exterior candidates does **not** force `beta(G)=1`.
The exact graph6 record `K??CA?_sDOEg` has `n=12`, `beta=2`,
`girth=5`, and `eta=3`.  Its four girth-preserving admissible leaf
deletions `v=4,5,6,8` all have `girth=5`, `eta=2`, and `phi=7<8`.
Thus the exterior lemma cannot be upgraded to an eta-preserving deletion lemma.

The same graph verifies why the full `phi` tradeoff remains the correct direct
frontier: deleting `v=1` gives `girth=6`, `eta=2`, and `phi=8`, while
deleting `v=3` gives `girth=7`, `eta=3`, and `phi=10`.  Therefore a proof
that a minimal phi-critical graph is unicyclic must permit deletion on a
shortest cycle and use the compensating girth increase.  The proved exterior
lemma is retained only as a connectivity/girth certificate; it does not close
or reduce away that metric tradeoff.
