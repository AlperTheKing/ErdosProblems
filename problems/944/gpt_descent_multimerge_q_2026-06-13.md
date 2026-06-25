# GPT-5.5 Pro question — descent-correspondence merge count (Erdős #944, staged 2026-06-13 ~07:05)

**Send in the interactive Chrome MCP session (deviceId cb342d47). This is the DECISIVE, proof-only blocker identified by the multi-agent coverage audit.**

## Context (self-contained)
Erdős #944 = Skottová–Steiner Problem 5.2: does a 6-regular 4-vertex-critical graph exist?
We attack nonexistence by a minimal-counterexample DESCENT. A nontrivial 6-edge-cut of such a
hypothetical target G splits it into shores; a shore K is a connected graph with total deficiency 6
(six "stubs" to the cut), Δ(K) ≤ 6, e(K) = 3|K|−3.

**Established base salvage lemma (proved, clean):** difference-rigidity on a non-adjacent pair
z₁,z₂ of K ⟺ the contraction K/(z₁=z₂) is non-3-colourable, and a minimal such non-3-colourable
contraction is 4-vertex-critical.

We call K **trace-hypo-rigid** when its interface trace is blocking-rigid yet every single vertex
deletion K−x restores compatibility (the shore-level analogue of 4-criticality). The working
**descent correspondence** says: a trace-hypo-rigid shore yields a 4-critical Δ≤6-ish QUOTIENT
core M (obtained by contracting forced-equal vertex classes), with |V(M)| < |V(K)|.

**Computational fact we have (P3pass=0, ~30×10⁹ candidates, fully validated):** there is NO
4-vertex-critical graph on 14 vertices of any SINGLE-MERGE descent profile — i.e. no 14-vertex
4-critical quotient with one merged (contracted-pair) vertex of degree d_u ∈ {6,7,8,9,10} and all
other vertices ≤6 (residual deficiency d_u−6 distributed, e = 42). This is the first descent rung
beyond Theorem A (no 6-regular 4-critical graph on n ≤ 14).

## The question
For a trace-hypo-rigid shore K of size 15:

**(Q) Is the minimal 4-critical rigidity-core quotient M ALWAYS reachable by a SINGLE non-adjacent
pair-contraction (|V(M)| = 14)? Or can the minimal M require contracting a larger independent set —
a triple — giving |V(M)| = 13 (a non-6-regular 4-critical quotient with one high-degree merged
vertex)?**

Equivalently: prove or refute that for every size-15 trace-hypo-rigid shore the minimal
non-3-colourable contraction has exactly 14 vertices. If TRUE, our completed single-merge n=14 hunt
(P3pass=0) excludes ALL size-15 trace-hypo-rigid shores and we have a genuine descent rung. If
multi-merge is possible, a size-15 shore can contract a 3-vertex forced colour class to a 13-vertex
non-6-regular 4-critical quotient that BOTH our n=14 hunt and Theorem A (6-regular only) miss — so
the rung is incomplete and we must hunt the 13-vertex multi-merge quotient class too.

## What would help most
1. A proof that the minimal rigidity core is a single pair-contraction (bounding the size of the
   forced-equal class to 2), OR
2. A construction/argument showing a forced 3-vertex colour class (triple-merge) is realizable for a
   genuine trace-hypo-rigid shore, OR
3. The precise bound on |forced-equal class| / |V(K)| − |V(M)| in terms of the cut structure
   (deficiency-6, the 6 stub endpoints, the (2,2,2) interface), so we know exactly which quotient
   sizes (13? 12?) the finite hunt must cover for an all-size-15-shore exclusion.

(We are running the 13-vertex two-merge quotient hunt computationally in parallel; this question is
the proof side that determines what coverage that hunt needs.)

---
## SHARPENING (added 2026-06-13 ~07:56, after triple-merge D'<=8 closed with P3=0)
Computational status: BOTH the single-merge n=14 quotients (d_u 6..10, ~30e9) AND the
triple-merge n=13 quotients (D'<=8, ~72e9) are exhausted with P3pass=0 (no 4-critical descent
core). So the question reduces to a clean structural one:

**(Q') For a trace-hypo-rigid shore K (6-cut, deficiency 6, the (2,2,2) interface), bound the size
of a maximal FORCED-EQUAL colour class (set of vertices receiving the same colour in every proper
3-colouring of the relevant restriction). Equivalently, across the 5 cut-matrix types
{(6,0,0),(3,3,0),(4,1,1),(2,2,2)} (the proven row-sum classification), which types can force a
colour class of size >= 3?**

Theorem C / cor:diag already forces a PAIR (p=l) in the 3+3 diagonal case (a single pair-contraction
-> 14-vertex quotient, EXCLUDED). If every forced-equal class has size <= 2, then every minimal
rigidity core is a single pair-contraction (14-vertex quotient) and the completed single-merge n=14
hunt excludes ALL size-15 trace-hypo-rigid shores => descent rung COMPLETE. If some type forces a
size-3 class, identify it (we have then closed its near-stub realisations D'<=8 computationally; only
the high-deficiency interior-triple case D'>8 would remain).
