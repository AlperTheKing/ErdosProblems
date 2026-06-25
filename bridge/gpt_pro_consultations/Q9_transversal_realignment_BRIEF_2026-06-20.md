# Q9 — GPT-Pro consultation brief: the C5-transversal peel realignment crux

**Status:** DRAFT ready to send (user relays). Sharpest framing of the H2 open core,
post the 2026-06-20 exact verification that pinned the peeling object.

## Background (what is now PROVED / VERIFIED — give GPT this context)
- `β(G) = e(G) − MaxCut(G)` for a graph G; `a(N) = max β` over triangle-free N-vtx graphs.
  Erdős #23 (the target): `a(5n) ≤ n²`, sharp at `C5[n]` (balanced C5 blow-up, β=n²).
- **Step 1 (a(30)=36, by exact computation) is being established separately.**
- **Reduction (PROVED):** Step 1 + the **Peeling Lemma H2** ⟹ Erdős #23 ∀n. H2: for
  every triangle-free G on 5n vertices (n≥7), ∃ a 5-set S with `β(G) ≤ β(G−S) + (2n−1)`.
  Induction: β(G−S) ≤ (n−1)² ⟹ β(G) ≤ (n−1)²+2n−1 = n².
- **VERIFIED (exact brute MaxCut over all C(5n,5) 5-sets, n=1,2,3):** at `C5[n]`,
  `min_S [β(C5[n])−β(C5[n]−S)] = 2n−1` EXACTLY, and the minimizers are EXACTLY the
  `n⁵` **C5-transversals** (one vertex per part, inducing a C5). Removing a transversal
  turns C5[n] into C5[n−1], so the drop is `n²−(n−1)² = 2n−1`. So H2 is TRUE and TIGHT
  on the extremal family, and **the correct peeling object is a C5-transversal**, not a
  single vertex, not an arbitrary 5-set.
- **Available proved tools:**
  - **A7:** every `{C3,C5}`-free graph on N vtx has `β ≤ N²/32`; so `β ≥ n²` ⟹ G
    contains an induced C5.
  - **WYZ (Wang–Yang–Zhao, finite N):** if min-codegree over nonedges `δ₂(G) > ⌊N/8⌋`
    then G is homomorphic to C5, hence `β ≤ n²`. (So a counterexample has `δ₂ ≤ ⌊5n/8⌋`.)
  - **MERGE:** a codeg-0 nonedge on a common max-cut side can be contracted preserving β.
  - **CUT3:** for a nonedge uv, `β ≤ min{p+q, t+q+x, t+q+y}` (3 explicit shores).

## The exact crux (this is the question)
Write the drop for removing a 5-set T as
   `β(G) − β(G−T) = e(T,V) − [MaxCut(G) − MaxCut(G−T)]`,
where `e(T,V)` = edges incident to T. H2 ⟺ ∃ T with
   `MaxCut(G) ≥ MaxCut(G−T) + e(T,V) − (2n−1)`,
i.e. **adding T back to an optimal cut of G−T recovers all but ≤ 2n−1 of T's incident
edges.** Greedy placement of T's 5 vertices recovers only `Σ_{v∈T} ⌈d(v)/2⌉` (= 5n on
C5[n]) — a factor ≈ 2.5 too weak. The true bound needs the WHOLE cut to **globally
realign** after T is inserted; on C5[n] this realignment is what brings 5n down to 2n−1.

**Q: Prove H2 — or its minimal-counterexample contrapositive — by a GLOBAL cut-realignment
argument.** Concretely, one of:
1. A discharging / exchange argument that, for any triangle-free G on 5n with β ≥ n²+1,
   exhibits a C5-transversal T and a single global 2-cut of G achieving
   `MaxCut(G−T) + e(T,V) − (2n−1)` (so β(G−T) ≥ β(G)−(2n−1) > (n−1)²: a smaller counterexample).
2. A FINITE stability theorem: ∃ ε,C with "β(G) ≥ n²−εn² ⟹ G is C-close (edit distance)
   to C5[n]", plus a sharp finite extension inequality on the ≤C exceptional vertices,
   so the transversal peel works in the near-extremal regime; couple with a non-extremal
   bound (BCL-type) for β bounded away from n². (BCL is asymptotic — the FINITE stability
   constant is the gap; does BCL's flag-algebra certificate yield an explicit finite ε,C?)
3. A reduction of the realignment gain to the non-C5-hom "exceptional set": WYZ gives a
   real C5 to peel when δ₂ is high; for the low-δ₂ / non-hom core (Petersen β=3, Grötzsch
   β=5 are non-hom), bound the deviation cost of a near-homomorphism on the set S where G
   fails to map to C5, showing it is ≤ the homomorphism-cut slack of G−S.

## What WON'T work (already rigorously excluded — tell GPT to avoid)
- Single-vertex / iterated-V1 deletion (zero slack at C5[n]; gives 5n not 2n−1).
- Uniform averaging over all 5-sets / LP probabilistic deletion: the MEAN 5-set drop is
  3.87 (n=2), 7.19 (n=3), STRICTLY ABOVE 2n−1; only an `n⁵`-thin family achieves the min,
  so no lower-bound-on-the-mean argument can yield the needed minimum.
- δ₂-dichotomy (low-δ₂ ≡ full problem via blow-up; high-δ₂ circular).
- SDP/spectral/local-count (β is not spectral, not a ≤C6-subgraph-count function; SDP is
  a relaxation that UPPER-bounds MaxCut, hence only LOWER-bounds β = e−MaxCut — wrong
  direction; we need a lower bound on MaxCut).
- Per-ball / radius-2 scalar (caps at 1/17.2 < needed 1/25; circular at c=25).

## ★ ADDENDUM (2026-06-20 literature audit, verified vs ar5iv 2103.14179)
- BCL Thm 1.3 (density n²/25 bounds) is ASYMPTOTIC ("n large enough", no explicit n₀); BCL
  Thm 1.4 (density ≥ 0.4 ⟹ ∃ unbalanced C5-blowup H, D₂(G)≤D₂(H)) is a reduction, NOT an
  edit-distance stability theorem. **BCL has NO effective/finite stability or uniqueness.**
- The extremizer C5[n] has density 0.4; blow-up preserves density; so the genuine open core
  is triangle-free graphs with density in **(0.2486, 0.3197)** at finite N. A counterexample
  there is SPARSER than the extremizer yet has HIGHER β than the believed max — implausible
  but unproven. Two equally-good deliverables: (A) an EFFECTIVE stability theorem near C5[n]
  with explicit ε,C; or (B) a direct exact argument that no triangle-free graph of density
  < 0.32 attains β = n² (which, with BCL's tails + blow-up transfer, closes the conjecture).

## Deliverable wanted
A correct proof of H2 (or of the minimal-counterexample contradiction), OR a precise
reduction of H2 to a single clean finite/asymptotic statement that is plausibly provable,
with every inequality justified. If no proof: the sharpest TRUE partial (e.g. H2 for the
C5-homomorphic case, or H2 under an explicit stability hypothesis) plus the exact remaining gap.
