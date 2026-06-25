# Novelty gate — #944 result package (2026-06-11, pre-PR sweep)

Target package: (A) no 6-regular 4-vertex-critical graph on n<=12 or n=14; unique one
at n=13 (critical edges = Hamilton cycle); (B) shore exclusion: every nontrivial
6-edge-cut shore in a 6-regular (4,1)-graph has >= 14 vertices => n<=27
super-6-edge-connected; plus the 21-matrix classification and the boundary-shortfall
lemma as method.

## Searches executed (headless, logged)
1. arXiv API `all:"vertex-critical" AND all:"critical edges"`, newest-first:
   only SkSt25 (2508.08703, 2025-08-12) + one 2022 Schrijver-fractional paper. NO overlap.
2. arXiv API `abs:"Dirac" AND abs:"4-vertex-critical"`: EMPTY result set.
3. arXiv API `abs:"6-regular" AND abs:"critical"`: EMPTY result set.
4. arXiv API `abs:"vertex-critical" AND cat:math.CO` newest 12 (2025-02..2026-06):
   all hereditary-class (P5-free etc.), S-packing, shift-graph papers; none touch
   Dirac k=4 / (4,1)-graphs / regular 4-critical enumeration / cut rigidity.
5. Semantic Scholar citations of arXiv:2508.08703: **zero citing papers** (2026-06-11).
6. erdosproblems.com/944 (curl -A Mozilla): STATUS OPEN; reference list exactly
   {La02 Lattanzio, Je02 Jensen, MaSt25 Martinsson-Steiner (k large), SkSt25 (k>=5)};
   "only remaining open case is k=4 (even k=4, r=1)". No computational or structural
   partial results listed for the 6-regular subcase.
7. OpenAI mass-sweep check: arXiv:2604.06609 "Short proofs ... II" quintet covers a
   DIFFERENT 4-critical question (K4-free 4-critical, few chords per cycle) — not #944.

## Verdict
GATE PASSED for both theorems and the method (exact 6-cut matrix classification,
boundary-shortfall shore machine). Closest prior art = SkSt25 Prop 5.1 (delta>=6,
lambda>=6, cut averaging) and Problem 5.2 (explicitly open, invites this exact attack);
our results are the equality-case collapse + exhaustive small-order closures, absent
from all swept sources. Caveats: zbMATH and Google Scholar not directly queryable
headless (arXiv + S2 + problem page swept); GPT-5.5 Pro literature cross-checks
(2 cold threads, 2026-06-10/11) independently found no overlap.

Re-run this gate immediately before PR/arXiv submission (the slice is AI-raced).

## Novelty gate RE-RUN for Theorem C (2026-06-13, before PR consolidation)
Statement gated: "In a 6-regular (4,1)-graph, no shore of a nontrivial 6-edge-cut
induces a bipartite graph; a shore with deficiency concentrated on two vertices
forces equal colours on them in every 3-colouring." Plus supporting Lemma E
(pair-rigidity) and the cut_row_forcing matrix corollary.
Searches: arXiv + web (surfaces Scholar/ScienceDirect/Springer/zbMATH-indexed).
- Only papers on THIS exact problem: SkSt25 (arXiv:2508.08703, isolates Problem
  5.2; delta>=6, lambda>=6; NO 6-edge-cut structure theorem) and MaSt25
  (arXiv:2310.12891, large-k far-from-edge-criticality). Both already cited.
- Disambiguation: "6-regular 4-CRITICAL graphs exist (r=6,8,10)" (Erdős 1989 conj;
  researchgate 262256207) refers to EDGE-critical graphs (every edge critical) —
  the OPPOSITE of (4,1)-graphs (no critical edge). No conflict; consistent with
  our Theorem A (unique n=13 graph is itself edge-critical, Hamilton-cycle).
- No theorem on bipartiteness / cut-matrix rigidity of shores in the (4,1) case.
VERDICT: Theorem C, Lemma E, cut_row_forcing are NOVEL. Gate PASSED.
