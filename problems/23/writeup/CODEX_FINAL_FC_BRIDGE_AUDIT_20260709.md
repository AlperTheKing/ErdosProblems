# Final Formal-Conjectures Bridge Audit (Codex, 2026-07-09)

This note records the exact current bridge from the local delta=0 package layer
to the official `formal-conjectures` statement for Erdős #23.

## Official Target Shape

The local checkout currently states `FormalConjectures/ErdosProblems/23.lean`
in the following shape, omitting the file's open-answer placeholder:

```lean
theorem erdos_23 : answer(<open-answer-placeholder>) ↔
    ∀ (n : ℕ) (V : Type) [Fintype V], Fintype.card V = 5 * n →
      ∀ (G : SimpleGraph V), G.CliqueFree 3 →
        ∃ (H : SimpleGraph V),
          H ≤ G ∧ H.IsBipartite ∧ (G.edgeFinset \ H.edgeFinset).card ≤ n^2 := by
  <open proof>
```

So the official FC target is the `|V| = 5*n` integer form, not the standalone
rational statement `∀ N, beta ≤ N^2/25`.  The rational local theorem is still a
useful stronger-looking internal bound, but the PR must close the displayed FC
shape exactly.

## Local Bridge Already Present

`Erdos23Delta0/FCBridge.lean` proves:

```lean
theorem erdos23_fcForm_of_bipartization
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (n : ℕ) (hcard : Fintype.card V = 5 * n)
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs) :
    ∃ H : SimpleGraph V, H ≤ Gs ∧ H.IsBipartite ∧
      (Gs.edgeFinset \ H.edgeFinset).card ≤ n ^ 2
```

This theorem uses the package-conditional local delta=0 theorem:

```lean
theorem erdos23_delta0
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hTri : Gs.CliqueFree 3) (P : SimpleGraphCertificatePackage Gs) :
    (betaSimple Gs : ℚ) ≤ (Fintype.card V : ℚ) ^ 2 / 25
```

and the pure SimpleGraph bipartization bridge:

```lean
theorem SimpleGraphBridge.beta_bipartization
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] (K : Nat)
    (h : betaSimple Gs ≤ K) :
    ∃ H : SimpleGraph V,
      H ≤ Gs ∧ H.IsBipartite ∧
        (Gs.edgeFinset \ H.edgeFinset).card ≤ K
```

Therefore the FC arithmetic/bipartization bridge is not the current proof wall.

It also now records the final package-provider wrapper:

```lean
theorem erdos23_fcForm_of_packageProvider
    (packageProvider :
      ∀ {V : Type*} [Fintype V] [DecidableEq V]
        (Gs : SimpleGraph V) [DecidableRel Gs.Adj],
        Gs.CliqueFree 3 → Nonempty (SimpleGraphCertificatePackage Gs)) :
    ∀ (n : ℕ) (V : Type*) [Fintype V],
      Fintype.card V = 5 * n →
        ∀ (Gs : SimpleGraph V), Gs.CliqueFree 3 →
          ∃ H : SimpleGraph V,
            H ≤ Gs ∧ H.IsBipartite ∧
              (Gs.edgeFinset \ H.edgeFinset).card ≤ n^2
```

This theorem is still conditional; it only packages the final wrapper shape.

## Exact Remaining Provider Theorem

To close the official FC theorem, the missing top-level provider is:

```lean
theorem simpleGraphCertificatePackage_exists
    {V : Type*} [Fintype V] [DecidableEq V]
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj]
    (hTri : Gs.CliqueFree 3) :
    Nonempty (SimpleGraphCertificatePackage Gs)
```

or an equivalent constructor usable under the `hcard : Fintype.card V = 5*n`
hypothesis.

Once this exists, the FC statement is a short wrapper:

```lean
theorem erdos_23_closed :
    ∀ (n : ℕ) (V : Type) [Fintype V], Fintype.card V = 5 * n →
      ∀ (G : SimpleGraph V), G.CliqueFree 3 →
        ∃ H : SimpleGraph V,
          H ≤ G ∧ H.IsBipartite ∧
            (G.edgeFinset \ H.edgeFinset).card ≤ n^2 := by
  intro n V _ hcard G hTri
  classical
  obtain ⟨P⟩ := simpleGraphCertificatePackage_exists G hTri
  exact Erdos23Delta0.CertGraph.erdos23_fcForm_of_bipartization
    G n hcard hTri P
```

## What `SimpleGraphCertificatePackage` Contains

The package fields in `CertGraph.lean` are:

```lean
structure SimpleGraphCertificatePackage
    (Gs : SimpleGraph V) [DecidableRel Gs.Adj] : Type where
  enc : SimpleGraphEncodingFacts Gs
  cut : CutData
  rows : RowDB
  hCut : checkCut enc.G cut = true
  good : GoodCutData enc.G cut rows
  delta : Delta0CertBundles enc.G cut rows
```

Thus the remaining full-theorem work is the generic construction of:

- encoding facts for any finite `SimpleGraph`;
- a good connected gamma-min maximum cut and row database;
- all delta=0 bundles for that row database, including O14 EQODL1,
  Branch-B, row partition, and the full-bank wall package.

The current O14/T8/Branch-B work is exactly machinery for the `delta` and
`good` fields of this provider.

## Audit Status

- The FC statement shape and local bridge are aligned on `CliqueFree 3`,
  unbalanced bipartization by arbitrary subgraph `H ≤ G`, and deletion count
  `(G.edgeFinset \ H.edgeFinset).card`.
- The local bridge is still conditional on `SimpleGraphCertificatePackage Gs`.
- No final unconditional official theorem is proved until the generic package
  provider exists and compiles without forbidden shortcuts.
