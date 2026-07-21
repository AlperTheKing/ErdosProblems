# WOWII 142 — Bridge Oracle Report (2026-07-18)

Exact falsifier tests for the candidate bridges R1/R2/R4 and the structure map
R3, BEFORE any prover investment. Target: the hard branch of C142
(`G` connected cyclic, `f >= 1`): `t >= (2/3)g + f`, with
`t` = largestInducedTreeSize, `g` = girth, `f` = eccSet(periphery), `D` = diam.

All arithmetic exact integers; slacks recorded in THIRDS
(`slack3 = 3*slack`, so `slack3 = 0` means exactly tight). No floats anywhere.

- Script: `bridge_oracle/bridge_oracle.py` (+ `bridge_oracle/r3_scan.py`)
- Results: `bridge_oracle/bridge_oracle_results.json`
  (sha256 `FB0AA15C…E6C9BA`), `bridge_oracle/equality_slacks.json`
  (sha256 `4881AC5…982810`), `bridge_oracle/r3_scan_results.json`,
  log `bridge_oracle/run_log.txt`
- Corpus: 10,663 distinct connected graphs (atlas n<=7 exhaustive; wowii_141
  sweep families + 2,900 random G(n,p) n=8..14; wowii_144 adversarial (n<=40),
  trap family; 1,500 cycle_random_legs, 1,000 cycle_random_trees, 800
  chorded_cycle, 600 gen_theta, 800 forced-girth g>=5 + 300 g>=4 random;
  girth-4-heavy bipartite block: crowns, K_{a,b}, grids up to 28 vtx, 700
  random bipartite, 250 even-chorded even cycles, 150 full subdivisions).
  182 acyclic skipped => **10,481 cyclic graphs evaluated**, girths 3..24.
- Plus ALL 113 equality cases from `oracle/equality_cases.json`, evaluated
  separately (tightness table below).

## Method integrity

- `M_P(P)` / `M(K)` computed EXACTLY by per-component enumeration of
  `G - V(P)` / `G - V(K)` (components are pairwise non-adjacent, so for a
  fixed base the optimum is additive across components; for `M(K)` the shared
  `z` is handled by per-z vectors, max over z at the end). Pruning only
  discards candidates that provably cannot beat the running max over
  geodesics/cycles, so reported maxima are exact.
- Validation pass (before the sweep): 287 small graphs, **1,513 per-geodesic
  `M_P` checks vs brute-force subset enumeration and 800 per-cycle `M(K)`
  checks vs `wowii_144/wave2/lemma_e_tests.M_of_cycle` — 0 mismatches**, plus
  collection-max cross-checks.
- Diametral geodesics: exact enumeration of ALL geodesics between ALL
  diametral pairs via the shortest-path DAG for **n <= 14** (superset of the
  required n <= 11); for n > 14 capped at 500 geodesic vertex-sets and
  flagged. Components larger than 17 vertices fall back to a greedy LOWER
  bound and are flagged. Caps only UNDER-report max M, i.e. under-report
  slack, so capped graphs can produce false "violations" but never false
  passes; capped negative slacks are classified "suspect" and re-verified
  with raised caps. **Zero suspects occurred, so no capped result needed
  rescue.**

## Per-bridge verdicts (10,481 cyclic graphs)

### R1 (geodesic-base) — ALIVE, sharp

`(2/3)g + f <= D + 1 + max_P M_P(P)` over diametral geodesics `P`;
`M_P(P)` = max induced forest in `G - V(P)` whose every component sends
exactly one edge (with multiplicity) into `P`. Consumer = Lemma M-P
(rigorous), so R1 => hard branch of C142.

- graphs: 10,481; **violations: 0; suspects: 0**
- min slack3 = **0** (witness `atlas [Bw]` n=3 g=3 D=1 f=0); tight on 83
  corpus graphs; next slack3 values 1 (43x), 2 (33x), 3 (422x)
- capped (lower-bound M or capped geodesic list, n>14 only): 307 graphs, all
  with slack3 >= 0 anyway
- **equality cases: 113/113 evaluated, slack3 = 0 on ALL of them**
  (hist `{0: 113}`) — R1 is exactly sharp precisely where C142 is sharp.

### R2 (cycle-base) — ALIVE, sharp

`f <= g/3 - 1 + max_K M(K)` over shortest cycles `K`, `M(K)` with the
z-deletion exactly as in `lemma_e_tests.M_of_cycle`. Consumer = Lemma M
(`t >= g - 1 + M(K)`), so R2 => hard branch of C142.

- graphs: 10,481; **violations: 0; suspects: 0**
- min slack3 = **0** (witness `atlas [Bw]`); tight on 78 corpus graphs
- capped: 438 graphs (cycle list > 250 or big component), all slack3 >= 0
- **equality cases: 113/113, slack3 = 0 on ALL** (hist `{0: 113}`).

### R4 (max of P2-arm and cycle-arm) — ALIVE

`(2/3)g + f <= max(D + ceil(g/2) - 1, g - 1 + max_K M(K))`.

- graphs: 10,481; **violations: 0; suspects: 0**; min slack3 = **0**;
  tight on 78; equality cases 113/113 slack3 = 0.
- Caveat: the first arm's consumer is P2 (`t >= D + ceil(g/2) - 1`), which is
  tested-true but UNPROVED; the second arm's consumer is Lemma M (proved).
  R4 adds nothing over R2 on this corpus at the min-slack level.

### R3 (structure map of the T1-hard set)

Membership: `2g + 3f > 3(D+1)`, i.e. graphs where `t >= D+1` alone does NOT
close C142. **3,927 / 10,481 members.**

- Girth histogram of members: g=4:133, 5:570, 6:203, 7:224, 8:289, 9:194,
  10:254, 11:205, 12:210, 13:166, 14:205, 15:143, 16:177, 17:154, 18:192,
  19:135, 20:184, 21:72, 22:79, 23:66, 24:72. **No girth-3 member.**
- Excess (`f - (D + 1 - 2g/3)`, stored as `excess3 = 3*excess`) ranges 1..36
  thirds, mode at excess3 = 1 (596 graphs); full histogram in the JSON.
- On members: R1 min slack3 = 0, **0 violations**; R2 min slack3 = 0,
  **0 violations** (joint min witness `atlas [FK_h_]` n=7 g=6 D=4 f=2, an
  equality case). Both bridges cover the entire hard set with equality-sharp
  margin.

**Why no girth-3 member — a PROVED mini-lemma (T4), not just data:**
`f <= D - 1` for every connected graph with `D >= 1`. Proof: if
`d(x, B) = D` then in particular `d(x, b0) = D` for a peripheral `b0`, so
`ecc(x) >= D`, hence `ecc(x) = D`, hence `x` is itself peripheral and
`d(x, B) = 0 < D` — contradiction. (Sharper than the `f <= D` noted in
INTEL_142.) Consequence: for `g = 3`,
`(2/3)*3 + f = f + 2 <= D + 1 <= t` by T1 alone — **the whole g=3 case of the
hard branch closes rigorously with no bridge.** Corpus corroboration
(`r3_scan_results.json`): `f = D` occurs on 0/10,481 graphs; min `D - f` is 1
at every girth 3..11, so `f <= D - 1` is tight and closes ONLY g=3
(g=4 members with `f = D - 1` exist, e.g. `atlas [FMoG_]` n=7 D=4 f=3).

## Recommendation for the prover

**Take R1 (geodesic-base) as the primary route**, with the g=3 case peeled
off first:

1. Prove T4 (`f <= D - 1`; one line, Lean-trivial) and close `g = 3` via T1.
   This also removes the entire Q4-falsifier zone's worst girth.
2. Main lemma to prove (the bridge): for some diametral geodesic `P`,
   `M_P(P) >= ceil(2g/3 + f) - D - 1` — equivalently R1. Feed it to the
   already-rigorous Lemma M-P. Corpus says this holds with 0 violations on
   10,481 graphs and is EXACTLY tight on all 113 equality cases (g in {3,6}),
   so there is no slack to give away: any proof must construct, per unit of
   `f` beyond `D + 1 - 2g/3`, one forest component with exactly one edge
   into `P`. Natural construction: hang the `f`-realizer's geodesic-to-`B`
   tail plus far-cycle arcs as single-attachment components; the known Q4
   failure mode (double attachment at g<=4) is exactly what the
   "prune to one edge" freedom of forests fixes — and g=3 is already gone
   via step 1, g=4 has only 133 hard-set members to guide the argument.
3. R2 is an equally alive, equally sharp fallback (`f <= g/3 - 1 + max_K
   M(K)`), and shares Lemma-M machinery with the parallel 144 lane (Lemma E:
   `e <= max_K M(K)`); if 144's Lemma E lands first, compare `f` vs `e`
   before duplicating work. R4 is alive but its P2 arm is an unproved
   consumer — do not build on it.

Falsified bridges Q3/Q4/Q5 were NOT retested (counterexamples already on
file). Nothing in this run contradicts C142: no corpus violation of the
conjecture itself was observed at any point.
