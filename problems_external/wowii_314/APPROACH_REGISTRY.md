# WOWII / Graffiti.pc Conjecture 314 — Approach Registry

Selected: 2026-07-18
Deadline: 2026-07-18T21:57:27+03:00
Status: FROZEN — user redirected the search outside WOWII and Erdős lists

## DIRECT ROUTE

### 1. Exact final deliverable

Give a complete proof of the exact theorem in
`FormalConjectures/WrittenOnTheWallII/GraphConjecture314.lean`: every finite,
nontrivial, connected, triangle-free graph whose largest induced path has at
most four vertices is well totally dominated.  The certificate is a Lean 4
proof of `WrittenOnTheWallII.GraphConjecture314.conjecture314`, followed by a
one-file `research solved` metadata PR if the final novelty gate still passes.

### 2. Current frontier lemma

`L314-Structure`: If a finite connected graph is triangle-free and has no
induced path on five vertices, then exactly one of the following usable
descriptions holds.

1. It is bipartite and admits a bipartition `X ⊔ Y` in which the open
   neighborhoods on each side are linearly ordered by inclusion (a connected
   chain graph).
2. It admits five nonempty independent bags `A₀,…,A₄` partitioning the vertex
   set, with two vertices adjacent exactly when their bags are consecutive
   modulo five (a blow-up of `C₅`).

The literature supplies this dichotomy at paper level; the frontier is to
reproduce the exact form needed by the target and make every implication
explicit enough for Lean.

### 3. Explicit logical bridge to the final deliverable

1. `largestInducedPathSize G ≤ 4` excludes every induced five-vertex path.
2. Apply `L314-Structure`.
3. In a connected chain graph, a set totally dominates iff its intersection
   with each bipartition class dominates the opposite class.  Nested
   neighborhoods force every inclusion-minimal such intersection to be one
   universal vertex.  Hence every minimal total dominating set has size `2`.
4. In a `C₅` blow-up, vertices in one bag are false twins, so a minimal total
   dominating set contains at most one vertex per bag.  Its occupied bags are
   exactly a minimal total dominating set of `C₅`; all of those have size `3`.
5. Thus every two minimal total dominating sets have equal cardinality, which
   is exactly `IsWellTotallyDominated G`.

No asymptotic or restricted-family surrogate is accepted: both branches of
the dichotomy must close the stated theorem.

### 4. Next falsifiable action

The exhaustive test through nine vertices and Lean lemmas `L0`, `L1c`, `L4`,
and `L5` are complete.  The current falsifiable action is to compile a generic
certificate: any chordless walk of at least four edges induces a `pathGraph 5`
embedding through its first five vertices.  This certificate closes the
fixed obstructions in `L1e`, `L2`, and `L3`; in parallel `L1d` must show that
the minimum odd cycle is chordless.  Exit this formal route if either cannot
be expressed as one finite lemma with the existing `Walk` API; do not replace
it by an expanding family of hand-enumerated path cases.

### 5. Exit condition

Exit this route immediately if any enumerated graph satisfies the conjecture's
hypotheses but either has minimal total dominating sets of different sizes or
fails the stated dichotomy; if a prior complete resolution or active proof
claim is found; or if the dichotomy cannot be stated with a finite lemma tree
that closes both branches.  Log the single falsifying fact and do not replace
the theorem by a weaker bound or an expanding family of exclusions.

## Novelty gate evidence at selection

- Upstream file at commit `c252a41054125b5fd9c8356e2137cd9b55337657` is
  tagged `research open`.
- Exact GitHub issue/PR search found only merged statement PR #3820 and no
  proof PR.
- The 348-fork audit found no proof on any recently active default branch.
- Exact-phrase and WTD/`P₅` literature searches found no resolution.
- Hammersen–Randerath, *Australasian Journal of Combinatorics* 55 (2013),
  263–272, records the structural classification; Bahadır–Ekim–Gözüpek,
  arXiv:2010.02341, studies WTD graphs but does not state this result.

## Lemma tree

- `L0`: the Lean bound on `largestInducedPathSize` forbids an explicit induced
  `P₅`.
- `L1`: odd-cycle analysis gives an induced `C₅` in the nonbipartite case.
- `L2`: vertices relative to that `C₅` form the five blow-up bags.
- `L3`: a connected bipartite `P₅`-free graph is a chain graph.
- `L4`: all minimal total dominating sets of a connected chain graph have
  cardinality `2`.
- `L5`: all minimal total dominating sets of a nonempty `C₅` blow-up have
  cardinality `3`.
- `L6`: `L0`–`L5` imply `IsWellTotallyDominated G`.
