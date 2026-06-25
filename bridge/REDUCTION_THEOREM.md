# Reduction Theorem: Step 1 + Peeling Lemma ⟹ Erdős #23 (multiples of 5)

Status: **PROVED** (conditional on H1, H2). Fully audited below.
Owner: Step-2 lead. Last updated 2026-06-19.

## Notation

- All graphs are finite, simple, **triangle-free**.
- `e(G)` = number of edges, `maxcut(G)` = max edges in a bipartite subgraph
  (= max over 2-colourings of cut edges).
- `beta(G) = e(G) - maxcut(G)` = minimum number of edges whose deletion makes
  `G` bipartite (= min over 2-colourings of monochromatic edges).
- `a(N) = max { beta(G) : G triangle-free, |V(G)| = N }`.
- `a` is non-decreasing in `N` (add isolated vertices), and `a(N) >= 0`.

## Target (this project's GOAL)

For every integer `n >= 1` and every triangle-free `G` on `5n` vertices,
`beta(G) <= n^2`.  Equivalently `a(5n) <= n^2` for all `n >= 1`.
(The sharp example `C5[n]`, the balanced blow-up of `C5` with parts of size
`n`, attains `beta = n^2`, so `a(5n) = n^2` once the upper bound is shown.)

## Hypotheses

- **(H1) Base, from Step 1 (Codex):** `a(30) <= 36`.
  [Codex is proving `a(30) = 36` by exact enumeration; we treat `<= 36` as the
  needed half and audit it via `bridge/NEEDED_FROM_STEP1.md`.]
- **(H2) Peeling Lemma [OPEN — the crux]:** for every `n >= 7` and every
  triangle-free `G` on `5n` vertices there exists `S \subseteq V(G)`, `|S| = 5`,
  with `beta(G) <= beta(G - S) + (2n - 1)`.

## Theorem

`(H1) and (H2)  =>  a(5n) <= n^2 for all n >= 1.`

## Proof

Induction on `n`.

**Base cases `n = 1,...,6`** (each is an exact known value; `<= ` holds with
equality, witnessed by `C5[n]`):

| n | 5n | a(5n) | n^2 | source                                   |
|---|----|-------|-----|------------------------------------------|
| 1 |  5 |   1   |  1  | OEIS A389646 (entry 5)                    |
| 2 | 10 |   4   |  4  | OEIS A389646 (entry 10)                   |
| 3 | 15 |   9   |  9  | OEIS A389646 (entry 15)                   |
| 4 | 20 |  16   | 16  | OEIS A389646 (entry 20)                   |
| 5 | 25 |  25   | 25  | this project (a(25)=25 proof; PR #4216)    |
| 6 | 30 |  36   | 36  | Step 1 / Codex (H1 gives `<= 36`)         |

So `a(5n) <= n^2` for `n <= 6`.

**Inductive step `n >= 7`.** Assume `a(5(n-1)) <= (n-1)^2`. Let `G` be any
triangle-free graph on `5n` vertices. By (H2) pick `S`, `|S| = 5`, with
`beta(G) <= beta(G - S) + (2n - 1)`. The graph `G - S` is triangle-free on
`5n - 5 = 5(n-1)` vertices, hence `beta(G - S) <= a(5(n-1)) <= (n-1)^2`.
Therefore
```
beta(G) <= (n-1)^2 + (2n - 1) = n^2 - 2n + 1 + 2n - 1 = n^2.
```
Taking the maximum over all such `G` gives `a(5n) <= n^2`. ∎

## Audit notes (independently checked)

1. **Lattice stays on multiples of 5.** Removing exactly `|S| = 5` vertices
   sends `5n -> 5(n-1)`; this is why `|S| = 5` (not 1) is forced — single-vertex
   peeling would leave `5n - 1` vertices, off the lattice on which `a` is
   controlled. ✓
2. **Telescoping is exact, no rounding.** `(n-1)^2 + (2n-1) = n^2` identically;
   there is zero slack. Equivalently, summing the per-step increments from the
   base anchors: with base `a(25) = 25` (n=5),
   `a(5n) <= 25 + sum_{k=6}^{n}(2k-1) = 25 + (n^2 - 25) = n^2`; with base
   `a(30)=36` (n=6), `a(5n) <= 36 + sum_{k=7}^{n}(2k-1) = 36 + (n^2-36) = n^2`.
   Both are consistent. ✓
3. **Base data really equals `m^2`.** OEIS A389646 list (n=1..23):
   `0,0,0,0,1,1,1,2,2,4,4,5,6,7,9,9,10,12,13,16,16,17,20`. Entries
   5,10,15,20 are `1,4,9,16` = `1^2,2^2,3^2,4^2`. ✓
4. **(H2) is the only open MATHEMATICAL input;** but the base cases rest on
   external numerical inputs (see DEPENDENCIES below) — in particular `a(25)=25`
   (project) and `a(30)<=36` (Codex/H1) are NOT OEIS-listed and must be tracked
   as dependencies, not taken as folklore. The exactness of the `2n-1` increment
   is forced by the extremal family: for `G = C5[n]`, `S` = one vertex per part
   gives `beta(C5[n]) - beta(C5[n-1]) = n^2 - (n-1)^2 = 2n - 1`, so (H2) is tight
   and cannot be improved to `2n - 2`. (Derivation in `bridge/PEELING_LEMMA.md`.)
5. **Why `n >= 7` in (H2) suffices.** The induction only invokes (H2) for the
   step into `5n` with `n >= 7`; steps into `5n`, `n <= 6`, are the base cases
   anchored by data + Step 1. If (H2) were additionally proved for `n = 6` it
   would re-derive `a(30) <= a(25)+11 = 36` and Step 1 would be unnecessary; we
   do NOT assume that. ✓

## DEPENDENCIES (explicit accounting of every external input)

The reduction `a(5n) <= n^2 ∀n` rests on EXACTLY these inputs; nothing else.

| n | a(5n) used | source | audit status (by Step-2) |
|---|-----------|--------|--------------------------|
| 1 | a(5)=1   | OEIS A389646 entry 5  | trusted (public); spot-checkable: β(C5)=1, and no 5-vertex triangle-free graph has β≥2 (5 vtx exhaustive) |
| 2 | a(10)=4  | OEIS A389646 entry 10 | INDEPENDENTLY CONFIRMED by Step-2 (`peel_test` over all 12172 graphs gave max β=4) |
| 3 | a(15)=9  | OEIS A389646 entry 15 | ✓ VERIFIED 2026-06-20: direct OEIS b-file fetch (curl) confirms a(15)=9, and the %N definition is EXACTLY "max edges to remove from a triangle-free graph on n vtx to make it bipartite" (= our a(N)). Step-2 H2 searches (794500 random + agent-exhaustive 286699 ≥42-edge, N=15) found NO graph with β>9 (corroborates upper bound; not a from-scratch exhaustive re-proof). |
| 4 | a(20)=16 | OEIS A389646 entry 20 | ✓ VERIFIED 2026-06-20: OEIS b-file a(20)=16 (same definition). Step-2 n=4 search (16143 high-β + structured hard cores incl. Petersen[2], N=20) found NO graph with β>16. |
| 5 | a(25)=25 | **THIS PROJECT** (docs_newmath/erdos23_a25_proof.md; PR #4216) | ⚠️ **GAP** — the proof's two-vertex-deletion + McKay-catalogue argument is sound, BUT it applies BCL high-density AT n=25 to force `e<=95`, and BCL Thm 1.3 holds only "for n>=n0" (asymptotic, n0 unspecified; verified 2026-06-20). Invalid unless n0<=25. See ledger DEP-a25. |
| 6 | a(30)<=36 | **Step 1 / Codex** (H1) | DEPENDENCY — in progress. ⚠️ Same BCL-finiteness issue: the edge-range reduction `109<=e<=139` uses BCL at n=30. See HANDOFF_TO_CODEX (URGENT) + NEEDED_FROM_STEP1. |
| >=7 | inductive | (H2) Peeling Lemma | OPEN — the mathematical core. |

⚠️ **BCL-FINITENESS GAP (2026-06-20):** Balogh–Clemen–Lidický Thm 1.3 (all parts:
global `n^2/23.5`, high-density `|E|>=0.3197C(n,2)`, low-density
`|E|<=0.2486C(n,2)` ⟹ `D2<=n^2/25`) is stated "for n large enough" and §2.3 says
it "only holds for n>=n0 for some n0 large enough" with NO explicit n0. Both
finite base cases that invoke BCL (n=5: a(25); n=6: a(30) via Codex) therefore
have an unjustified step at finite n. Resolving this (a finite-n density bound, a
direct argument, or extended enumeration) is now a tracked requirement.

Rounding/lattice: the induction is exact integer arithmetic
(`(n-1)^2+(2n-1)=n^2`), `|S|=5` keeps the vertex count on the `5Z` lattice, and
`β` is integer-valued; there is NO rounding anywhere. The inductive chain for
`n>=7` only consumes the `n=6` base (a(30)<=36); the `n<=5` bases are needed only
to STATE the theorem at those `n` and hold by the data above. n=1..5 and all
rounding are thus fully accounted for.

**To CLOSE the bridge unconditionally, three things must all hold:**
(i) (H2)/MC4 proved [OPEN]; (ii) `a(25)=25` audited [project dependency];
(iii) `a(30)<=36` closed + audited [Codex/H1, in progress].

## What remains

The entire mathematical difficulty is concentrated in **(H2)**. See
`bridge/PEELING_LEMMA.md` for the analysis, the proof that the trivial
greedy "half-cut" extension is too weak (factor ~3), the equivalence of (H2)
to the open medium-density regime of the Erdős `n^2/25` conjecture, the
attempted exact routes, and the GPT-Pro consultation log.
