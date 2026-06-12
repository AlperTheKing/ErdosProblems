# GPT-5.5 Pro cold red-team digest — Erdős #944

Date: 2026-06-10.

Prompt: adversarial audit of the #944 6-regular rigidity package:
local multiplicity, triangle bound, exact 6-cut conflicts, Kempe tether, and
small 6-cut shore exclusion.

## Verdict

GPT-5.5 Pro did not find a mathematical error in claims 1-5, but required
wording and hypothesis corrections.

Accepted after corrections:

1. Local multiplicity is rigorous. State "3-colouring" as a map into a fixed
   3-colour palette; it need not use all colours globally.
2. Triangle bound is rigorous for simple 6-regular targets.
3. Exact 6-cut conflicts is rigorous for a nontrivial partition with both
   shores proper. Each shore is 3-colourable by deleting a vertex on the other
   shore and restricting.
4. Kempe tether is rigorous only in the global graph `G - {e,f}`. Do not
   localize it to one shore without an additional first-crossing argument.
5. Small 6-cut shore exclusion is rigorous. The "proper induced subgraph is
   3-colourable" step must be proved by monotonicity: if `S` is proper, choose
   `v notin S`; then `G[S] subset G-v`, and `G-v` is 3-colourable.

## Single riskiest step

The Kempe tether can be misused. The forced Kempe path is in `G - {e,f}` and
may leave and re-enter a shore. Any later argument treating it as an internal
path of `G[S]` is invalid unless justified by a first-cut-crossing or equivalent
localization argument.

## Literature notes from red-team

- Skottova-Steiner 2025 leave `k=4` open and pose the 6-regular subproblem.
- Their Proposition 5.1 contains the general random-colouring edge-connectivity
  lower-bound idea; cite this for the broad expectation argument.
- Do not cite the local multiplicity, exact 6-cut equality, Kempe tether, or
  small-shore exclusion as named folklore unless a specific source is found.
  They are short enough to prove directly.

Search phrases suggested for final novelty sweep:

- `Kempe chain two monochromatic edges critical graph`
- `vertex-critical graph no critical edge Kempe chain`
- `critical graph edge cut coloring permutation argument`
- `k-vertex-critical no critical edge edge connectivity`

# SECOND cold red-team (wider package) — thread "Cold Review Adversarial Analysis" c/6a29bd3c, 2026-06-10 late

Scope: full Direction-B package (L1.1, C1.2, C1.3, L2.1+C2.2 Kempe tether, L3.1-3.3,
L4.1, T4.3, T5.1-5.3, DICH) + F1-F3 computational facts.

## Verdicts (item-by-item)
- L1.1 VALID/folklore; C1.2 VALID/known (local singleton form of SkSt25 Prop 5.1);
  C1.3 VALID (minor wording); L2.1 VALID ("standard Kempe swap in a new local costume";
  mate-tether possibly new AS A LEMMA but referee sees one-line Kempe argument);
  C2.2 VALID; L3.1 VALID/SkSt idea; L3.2 VALID/known (cut-averaging); L3.3 VALID
  (equality case, "correct and useful"); L4.1 VALID; T4.3 VALID (independently
  reproduced: 21 matrices, 5 types, orbits 3+3+9+3+3); T5.1 VALID (no connectivity
  needed); T5.2 VALID; T5.3 VALID (only type II has row sums (3,3,0)).
- DICH FLAWED AS WRITTEN: "minimum nontrivial atom exactly size 8" NOT proven —
  shores 9,10,... untouched. (NOTE: our twins argument, absent from the audited
  package, kills 8-shores entirely => shores >= 9; sent as follow-up for refereeing.)

## Counterexample hunts (negative = good)
- C1.3: exhaustive n<=6 labelled + atlas n<=7: no failure.
- T5.3: K_{3,3,2}-shore extensions n=9..12 (all outside graphs 1-4 vertices, all
  6-cut-edge placements consistent with T5.2): no target found, no violation.
  K_{3,3,3} (non-target) breaks the rainbow conclusion => target hypothesis essential.

## Novelty layering (per red-team)
- Layer 1 (L1/C1.2/L3.*): known/immediate from SkSt25 Prop 5.1 proof — cite, don't claim.
- Layer 2 (L2.1): valid, technique classical (Kempe-equivalence literature), the
  precise target-local statement may be new as a lemma but is "one-line".
- Layer 3 (T4.3-T5.3): "the genuinely useful part" — elementary but sharp, checkable,
  tailored to SkSt25 Problem 5.2. Kostochka-Yancey / Stiebitz-Tuza-Voigt: no overlap.

## Strongest honest theorem (red-team wording)
Every target has exact 6-cut rigidity (cut matrix = one of the 21 all-diagonals-2
matrices for every cut + side colourings); every nontrivial 6-cut shore >= 8; every
8-shore is induced K_{3,3,2} with both size-3 parts rainbow to the outside.

## Publishability + required fixes
"Partial-progress note: maybe." Fixes: (1) correct DICH wording (or kill 8-shores —
done via twins, pending referee); (2) separate known from new honestly; (3) make
F1-F3 reproducible (graph6 certificates, SMS/nauty commands, verifier code, colouring
count conventions); (4) add a constraint beyond 8-shores (twins => >= 9 + n<=17
super-6-edge-connected corollary is exactly this); (5) Lean cores good, certifying
the enumeration would be the credibility upgrade.
Best framing: "Exact 6-cut obstructions and small-order computations for the
6-regular Dirac k=4 problem."

## Follow-up sent (pending)
Twins-kill referee request + n=14-in-flight publishability + next-theorem triage
(A: exclude 9-shores; B: Kempe-global for super-6-ec candidates; C: n=15-16 with
cut-free pruning).

## Follow-up verdicts (same thread, reply 2)
- TWINS KILL OF 8-SHORES: **VALID**, "no hidden assumption". The no-false-twins lemma is
  folklore (stronger form also folklore: no nonadjacent u,v with N(u) subseteq N(v) in a
  vertex-critical graph; appears in k-critical P5-free literature). The application to
  8-shores in this Dirac/SkSt setting "looks likely new" as a corollary — frame as a
  useful sharpening, not a major lemma.
- Corrected theorem (red-team wording): "No target has a 6-edge cut with an 8-vertex
  shore. Consequently every nontrivial 6-edge-cut shore in a target has size at least 9."
  Holds for non-regular targets too (degree equality forced internally). n<=17 =>
  super-6-edge-connected CONFIRMED ("turns the 8-shore theorem from classification of an
  exceptional atom into exclusion of the first possible atom").
- Publishability: with F1-F3 + n=14 + matrix classification + no-8-shore => "coherent
  note", arXiv threshold = reusable certified dataset + clean structural obstruction.
  Title framing: "Exact 6-cut rigidity and small-order computations for the 6-regular
  k=4 Dirac problem". MUST include: graph6 certificates; colouring-count convention
  (proper maps to {1,2,3}, NOT mod S3); independent verification scripts; theory
  separated from computation; no novelty inflation.
- NEXT THEOREM RANKING: **A (exclude 9-shores) > C (n=15,16 cut-free pruning) > B
  (Kempe-global: highest ceiling, too unconstrained now)**. Practical route for A:
  computationally enumerate all possible 9-shore induced graphs + boundary patterns;
  if the finite local classification collapses => strong theorem; else survivors =
  next exact obstruction list.
- 9-shore regime (6-regular case): G[A] has exactly 24 edges (2e+6=54), 9 vertices,
  Delta<=6, 3-colourable, deficiency vector b(v)=6-d_A(v)>=0 summing to 6 (b(v)<=5
  else disconnect), and EVERY proper 3-colouring of G[A] must give a boundary
  colour-vector in {(6,0,0),(3,3,0),(4,1,1),(2,2,2)} by T4.3. Finite, enumerable.

## Q1/Q2/Q3 consult results (reply 4, 2026-06-11 ~01:50)
- Q1 TERMINATION: do NOT claim analytic all-a kill. [C] neutralizable by tiny support
  gadgets (triangle b=2,2,2; K_{2,2,2} b=1x6; unique-colouring gadgets); binding filter
  is [K] = "full-degree vertices must be deletion-unfrozen" ("frozen-full-vertex
  obstruction" - good writeup name). Referee leans: large artificial shore LIKELY exists
  => machine = finite theorem-generator. Bridge needed for all-a: "[C] forces colour
  rigidity incompatible with [K] at all full-degree vertices".
- Q2 8-CUT LAYER: DEAD END for shores. 1071 labelled matrices / 51 row-col types with
  total 8 + all diagonals >=2, BUT every row-sum vector occurs => [C8] vacuous at
  row-sum level; additive-rank-1 survives only as slack budget sum delta_pi = 4.
  Do NOT build the 8-cut shore machine.
- Q3 ENDGAME INVARIANT: "Kempe-component cut charge". CHARGE LEMMA (arithmetic
  self-verified ✓): super-6-ec 6-regular target, deletion-colouring (v,phi), pair {i,j},
  third colour k: c_ij <= |V_k| - sigma_ij, where c_ij = #components of G[V_i u V_j],
  sigma_ij = 1 if the four N(v)-boundary vertices split (1,1)+(1,1), 0 if (2,2).
  Proof: V_k independent => e(V_i,V_k)+e(V_j,V_k) = 6|V_k|-2; sum of component cuts
  = 6|V_k|+2; every component cut >=6, boundary components nontrivial >=8 (even cuts +
  super-6-ec). Summing pairs: c_12+c_13+c_23 <= n-1-Sigma. NEXT LEMMA TARGET: opposing
  bound c_12+c_13+c_23 >= n-1 (+ at least one split pair) => CONTRADICTION kills all
  super-6-ec 6-regular targets. Instrument future searches to record
  (c_12,c_13,c_23;sigma_12,sigma_13,sigma_23).
- UPDATED HEADLINE: "Every 6-regular (4,1)-graph on n<=27 is super-6-edge-connected" +
  "No 6-regular 4-VC graph on n=14". Framing: "Exact 6-cut rigidity and small-order
  superconnectivity for the 6-regular Dirac k=4 problem". K333-minus-rainbow-matching
  demoted to explanatory near-miss.

## Charge-lemma instrumentation data (charge_data.py, 2026-06-11 ~02:05) — NEGATIVE
- Random 6-regular chi>=4 graphs, all (v,phi) with 2+2+2 splits: n=14: 54 instances,
  n=16: 36. In EVERY tether-ok instance all three bicolour graphs are CONNECTED
  (c_12=c_13=c_23=1, csum=3) and Sigma=0 (no split pairs at all). 22% of instances are
  tether-violations (=> critical edges; consistent with Lemma 2.1's strength).
- Consequence: the hoped-for opposing bound csum >= n-1 is NOT supported (3 << n-1,
  no saturation); "at least one split pair" also unsupported. The Kempe-charge route
  AS SKETCHED looks weak; needs a different fragmentation source or a different
  invariant. FEED BACK to GPT next round.
