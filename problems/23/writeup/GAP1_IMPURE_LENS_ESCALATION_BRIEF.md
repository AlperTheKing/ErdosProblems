# gap#1 crux — self-contained escalation brief (for GPT-5.6 / Fable-5)

*Distilled 2026-07-08 from the 29-reply GPT-Pro archive (GAP1_FULLSUPPORT_REDUCTION_GPTPRO.md). Reads standalone — no
prior history needed. Goal: hand a stronger model ONE well-posed research theorem plus the map of every dead end.*

---

## 0. The one open theorem

Prove or refute, as a **deductive** theorem about a hypothetical object (see §4 — it is NOT empirically testable):

> **`BalancedNeutralTheta_book_or_reducible`.** Let `C` be a reduced, Γ-minimal, minimal-negative-balance ("deficient")
> cage arising from a triangle-free maximum cut. Let `e, f` be two ℓ=5 rows (bad edges) whose blue supports form a
> **Γ-neutral, non-book theta** with doors `d0, d1` and lens component `W`. Then either the theta is
> **C5-book-parallel** (the two rows are layer-compatible about the doors) **or** `W` admits a **nonnegative prunable
> subcage** (a `ReducibleSubcagePattern`), which contradicts minimality.

If TRUE ⟹ `BalancedNeutralTheta ⟹ book ∨ reducible` ⟹ `P4SharedSupportDichotomy` ⟹ `Ell5SupportExpansion` ⟹ gap#1
(Γ ≤ N²) ⟹ Erdős #23 δ=0 (β ≤ N²/25). If FALSE ⟹ its counter-pattern is the exact obstruction to `Ell5SupportExpansion`.

**The wall is one sub-case:** the **IMPURE** balanced-neutral lens — where `W` carries *extra owned atoms* beyond
`e, f`, so the obvious prunable subcage is not immediately nonnegative. The **pure** lens (`OwnedPositiveSurplus(W)=0`)
is already proven reducible. The impure lens is the sole open content.

---

## 1. Why we care — the reduction chain (each arrow is proven/compiled unless marked)

```
Erdős #23 δ=0  (β = e − maxcut ≤ N²/25, triangle-free, sharp at C5[N/5])
  ⟸ Γ := Σ_rows ℓ² ≤ N²                                    [GERSH aggregation; = "gap#1"]
  ⟸ Ell5SupportExpansion: for every set S of ℓ=5 atoms of a reduced
       triangle-free Γ-min max-cut K2-component, |E_short(S)| ≥ |S|      [single-commodity Gale–Hoffman / Hall]
  ⟸ P4SharedSupportDichotomy  (minimal Hall violator ⟹ shared-support P4 pattern)
  ⟸ BalancedNeutralTheta_book_or_reducible   ← THE OPEN LEMMA (impure lens sub-case)
```

`E_short(S)` = union over atoms in `S` of the cut edges of their shortest blue geodesics. `ℓ(e)` = odd-cycle length of
bad edge `e` = (blue-distance between its endpoints) + 1; triangle-free ⟹ `ℓ ≥ 5` for every blue-connected bad edge.

---

## 2. Definitions (self-contained)

- **Cut / blue graph.** Max cut with sides `Bool`. **Blue** = bichromatic (cross) edges. **Bad edge** = monochromatic
  (same-side) edge. A **row/atom** = a bad edge `e=(u,v)`; its **support** `P_e` = the cut edges of all shortest blue
  geodesics `u⇝v`. `ℓ=5 ⟺ blue-dist = 4 ⟺ P_e` is (a union of) length-4 geodesics; `|P_e| ≥ 4` (tight).
- **Γ and reserve.** `Γ_C = Σ_{e∈C} ℓ(e)²`. `reserve = N² − Γ`. A **deficient / MinimalNegBalance cage** has
  `reserve < 0`, i.e. `Γ > N²` — the negation of what we must prove. **Minimal** = no proper prunable subcage has
  negative balance.
- **θ (theta) of two rows.** Supports of `e, f` sharing a sub-path form a theta graph with two **doors** `d0, d1`
  (branch vertices/edges) and a **lens** `W` = the component of `B∖{d0,d1}` between them.
- **Balanced / neutral.** The recut swapping `W` changes Γ by `|δ_M(W)| − |δ_B(W)|`. **Neutral** = this is `0`
  (`5²+5² → 5²+5²`, ΔΓ=0 — the two rows stay ℓ=5). This is why a Γ-decrease argument CANNOT fire (see §5).
- **Book vs lens.** **C5-book-parallel**: the two rows are layer-compatible about the doors (`|B_C| = 4|M_C|`, local
  density ≈ 0.4) — provably reducible. **Non-book lens**: order-inverted P4 pair, not layer-compatible.
- **Pure vs impure lens.** **Pure**: `W` owns only `e, f` (`OwnedPositiveSurplus(W)=0`) — proven reducible.
  **Impure**: `W` owns extra atoms ⟹ pruning `W` doesn't obviously give a nonnegative subcage. **← THE WALL.**

---

## 3. What is already PROVEN / compiled (do not redo)

- **Abstract Hall/CS skeleton** — `Ell5CSReduction.lean`, 10 axiom-clean theorems (`{propext,Classical.choice,Quot.sound}`):
  `card_support_ge_of_mQ_le_Tsq` (Cauchy–Schwarz `m·Q ≤ T² ⟹ Hall`), `minimal_hall_obstruction_no_private_edge`,
  `hall_le_five` (the `|S| ≤ 5` base case from hypotheses `h4`,`hpair`), `c5book_support_expansion`,
  `pair_union_ge_five`, `support_card_ge_four`, `cross_flip_bool`, `ell5_geodesic_four_edges`, …
- **Capacity lemma** — `MaxCutVertexIneq.lean`: `|δ_M(U)| ≤ |δ_B(U)|` for a maximum cut (discharges the C5-book chain).
- **Graph wiring** — `Ell5GraphBridge.lean`: `ell = 5 ⟹ blue-dist = 4` and `|P_e| ≥ 4` at the real `blueGraph`.
- **Path rigidity (`hpair`), PROVEN in Lean** — `PathRigidity.lean`, 5 axiom-clean theorems: `edges_determine_badedge`
  (two paths with the same edge set + distinct endpoints ⟹ same bad edge `s(u,v)=s(u',v')`), via endpoint
  incidence-degree 1 (`IsPath.eq_snd_of_mem_edges`) + internal incidence-degree ≥ 2. So distinct ℓ=5 atoms have distinct
  4-edge geodesic supports — the graph content of `hpair`, now a compiled theorem, not just an empirical fact.
- **The `|S| ≤ 5` BASE CASE, FULLY COMPILED end-to-end** — `Ell5AtomBase.lean` (`ell5_base_case`) + `Ell5AtomGraph.lean`
  (`ell5_atom_of_badEdge`, from a real `blueGraph` ℓ=5 bad edge). Both hypotheses of the Hall bound are now discharged
  (`h4` from geodesic length, `hpair` from rigidity), axiom-clean. **This is the compiled endpoint the open lemma must
  reduce the general case to** (via `P4SharedSupportDichotomy`). The exact gate `_claude_hpair_rigidity_gate.py` had
  already confirmed both facts true + tight (0 fails / 71815 cages; rigidity 0/247), so the formalization is grounded.
- **Pure lens** reducible (GPT-Pro §B): `|B^W|−|B| = |δ_M(W)|−|δ_B(W)| = 0`, neutral, and `OwnedPositiveSurplus=0`
  gives the nonnegative prunable subcage.
- **`m·Q ≤ T²`** empirically holds (127014 checks, min margin 2.29×) — but is **sufficient, not necessary** (see §5).

---

## 4. ⚠ Why this is NOT empirically testable (critical — read before proposing a "gate")

The impure lens lives inside a **deficient cage** (`Γ > N²`, negative reserve). **No deficient cage exists in any real
triangle-free graph** — that is exactly the conjecture we are proving. So, like the earlier "switch premise" and
"ViolatesShortestGeodesicHall" premises, the impure balanced-neutral lens is a **counterfactual object**: it cannot be
exhibited or checked on any real graph. Every empirical Hall/expansion battery shows feasibility everywhere (0 fails on
70k+ cages) precisely because no gate can reach the binding case. **The lemma must be proven deductively in the
hypothetical deficient-cage world; a passing battery is not evidence for it.** This is the single most important framing
for a fresh model — do not ask for a counterexample search on real graphs; there is none by construction.

---

## 5. DEAD ENDS — every angle tried, with the falsifying fact (do NOT re-tread)

| Angle | Killed by |
|---|---|
| **Switch premise** (over-congested ⟹ switch exists) | Counterfactual, 0/71910; odd cycle `C_N` rigid but = base leaf. |
| **Path-routing** | Reduces to the *same* open expansion inequality. |
| **Cut-cover** (separating cut per atom, `δ_B ⊆ E_short`) | **FALSIFIED** exactly: infeasible with ALL 2ⁿ cuts on 19 N=11 comps while Hall holds; atom (5,9) has no separating cut. Strictly stronger than Hall. |
| **`m·Q ≤ T²`** (Cauchy–Schwarz sufficient cond.) | SUFFICIENT, not necessary — a sunflower violates `m·Q≤T²` while Hall still holds. Can't be the theorem. |
| **`S1ThetaPattern_eliminates` via Γ-decrease** | **FALSE** for balanced ℓ=5: the theta is Γ-NEUTRAL (`5²+5²→5²+5²`, ΔΓ=0). The `−(4L+4)` drop was for UNEQUAL `{L,L+2}`, not the balanced case. Any monovariant must be non-Γ. |
| **Neutral-recut monovariant `BookDefect`** | Reduces `BookDefect` in the pure two-row lens but can INCREASE globally — **may CYCLE**; no proven monovariant Φ. (Open sub-question — a real Φ would close it.) |
| **Medium-band BCL bypass** (counterexample must be medium-density; deficient ⟹ high-density ⟹ BCL closes it) | **REJECTED** (reply 29): deficiency is *length-square* density (`Σℓ²`), NOT edge-density — one long odd cycle has `Γ=n²` with `O(n)` edges. And local density ↛ global BCL tail. Required lemmas (`deficientCage_forces_global_high_density` / `mediumDensity_no_deficient_cage`) are each **as hard as the original**. The impure lens is *exactly* the non-book case where the `|B_C|=4|M_C|` density-forcing FAILS. |

---

## 6. Fresh angles NOT yet tried (candidates for the stronger model)

1. **A genuine non-Γ monovariant Φ** for the neutral recut that provably strictly decreases and breaks ties globally
   (the `BookDefect` idea, but with a proven Φ — lexicographic on (Γ, book-defect, something)?). This is the most
   direct route: it would turn "book ∨ reducible" into "always reducible unless book" by well-founded descent.
2. **Direct reducibility of the impure lens**: show the extra owned atoms in `W` themselves contribute *nonnegative*
   surplus that the prune absorbs — i.e. `OwnedPositiveSurplus(W) ≥ 0` is compatible with the neutral door balance, so
   the prunable subcage is nonnegative after all. (GPT-Pro's angle B, unresolved for the impure case.)
3. **`ReducedShell` / minimality forbids the impure lens outright** (GPT-Pro's angle C, unresolved): does the reduced +
   MinimalNegBalance hypothesis force `W` to own nothing extra? If reducedness already excludes extra owned atoms, the
   impure case is vacuous.
4. **Induced-P3:P4-ratio spectral** (arXiv 2204.00093, signless-Laplacian `q_n ≤ 15n/94`): the ℓ=5 geodesic is a P4;
   its sub-paths are P3. A spectral/ratio bound on the shortest-support hypergraph could replace the combinatorial lens
   argument entirely. Untried — worth a from-scratch look.

---

## 7. The specific ask

Pick angle §6.1, §6.2, or §6.3 (they are the three faces of the same lemma) — or §6.4 as an orthogonal route — and
either **prove** `BalancedNeutralTheta_book_or_reducible` for the impure lens, or **exhibit the exact counter-pattern**
(a consistent impure balanced-neutral lens in a reduced minimal-neg-balance shell with no nonnegative prunable subcage),
which would be the decisive obstruction to `Ell5SupportExpansion`. Remember §4: reason deductively in the deficient-cage
world; do not look for real-graph counterexamples. The Lean scaffolding in §3 is ready to consume the result: the
`|S| ≤ 5` base case is now **fully compiled** (`ell5_base_case`, axiom-clean), so the only remaining piece to close
gap#1 is the general-`|S|` reduction to that base — i.e. `P4SharedSupportDichotomy`, which is exactly this open lemma.
Proving it closes the whole `Ell5SupportExpansion` ⟹ Γ ≤ N² chain.
