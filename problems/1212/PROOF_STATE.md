# Erdős #1212 — PROOF_STATE  (updated 2026-06-10 ~02:10)

## Verified lemmas
- [T1] Parity/forcing: if 2 | g (period radical), both-even vertices are banned, so valid certificate paths
  decompose into xx/yy doubles between both-odd vertices; even columns are vertically untraversable.
- [T1] Periodic Certificate Lemma (from GPT consult 1; independently re-derived): a finite NN-path Gamma
  closing to (x0+gh, y0+gv), with for all i: Delta_i = h*y_i - v*x_i != 0, rad(Delta_i) | g; no p|g divides
  both coords; some p|g divides exactly one coord => the (gh,gv)-translates of Gamma concatenate into the
  desired infinite path (YES). Reduces the YES direction to a finite search.
- [T1] Odd-g impossibility: rad(Delta)|g odd => Delta odd at every vertex; steps change Delta by v or h,
  one of which is odd (gcd(h,v)=1) => that step type is banned => 1-D movement => no certificate. So 2|g.
- [T1] Witness tightness: q|h and q|x_i => q | h*y_i - v*x_i = Delta_i => (C1) q|g. No witness primes can
  be smuggled via h or v; the lemma's conditions are tight.
- [T1] P={2,3} certificate nonexistence (mod-3 deadlock: x-moves need 3|y, y-moves need 3|x, handoff forces
  (0,0)-mod-3 or witness-free vertex; survives backtracking).
- [T0-strong] s=0 law: exhaustive SCC searches over P in {{2,3},{2,3,5},{2,3,5,7},{2,3,5,7,11}},
  all coprime (h,v) <= 10, |Delta| <= 2000, WITH backtracking edges: every cycle in the certificate state
  graph has zero net displacement (pure oscillation). Code: search1212/ (several programs).
- [T1] Localization: the Delta-graph alone admits s=1 cells (three consecutive smooth values), so the s=0
  obstruction lives in the residue coupling (per-prime protection handoffs), not in Delta-dynamics.
- [T0] Recon: both-prime-deleted visible graph is shattered at small scales; giant components grow with
  scale (~21.5% of valid vertices in [2,3000]^2). Suggests answer YES with large-coordinate start.

- [T1/T2-grade, NEW 2026-06-10 ~02:20] s=0 law UPGRADED TO PROVEN-BY-EXHAUSTION for P ⊆ {2,3,5,7,11},
  coprime (h,v) ≤ 10: (i) every certificate-cycle edge needs a smooth 3-term-AP window {Δ, Δ±d, Δ±2d}
  (d = v or h ≤ 10); (ii) enumeration of ALL 11-smooth numbers ≤ 10^15 (120,895 of them) shows every such
  window has top ≤ 1000 — the extremal windows are exactly d·{98,99,100} (98=2·7², 99=3²·11, 100=2²·5²);
  (iii) the DMAX=20000 sweep therefore covered every possible cycle; it found all cycles oscillating (s=0).
  Hence NO periodic certificate exists with P ⊆ {2,3,5,7,11} and h,v ≤ 10. (Tail 10^15→∞ closable via
  Størmer/S-unit finiteness if needed for writeup; windows are S-unit-bounded.)

- [T1, NEW 2026-06-10 ~02:30] **NO-PERIODIC-CERTIFICATE THEOREM** (GPT consult 2, 23m27s; independently
  re-derived and verified): For ANY g,h,v (gcd(h,v)=1), the Periodic Certificate Lemma has no instantiation.
  Case 1 (g odd): Delta-parity argument (mine, adopted). Case 2 (2|g): let m = rad(g) = prod P. Any vertex
  with x ≡ 0 (mod m) is ISOLATED in the protected residue graph: the vertex itself is valid (every p|m
  splits x vs y, C2 forces y coprime to m), but x±1-neighbors have both coords coprime to m and both odd
  (no witness, C3 fails) and y±1-neighbors are both-even (C2 fails). A certificate needs net x-advance
  gh ≥ g ≥ m; ±1 steps + intermediate-value force the path through some vertex with x ≡ 0 (mod m) —
  isolated or invalid. Contradiction. Explains the s=0 law exactly; independent of (h,v), Delta-range,
  smoothness. THE PERIODIC ROUTE IS DEFINITIVELY CLOSED.

- [T1, 2026-06-10 ~03:00] Clearance formula: clr(a_n; a_{n+1}) = p_min(a_n) − gap_n; (V_n) ⟺
  a_{n+2} − a_n < p_min(a_n). Chain conditions crisp (rough-composite anchors, p_min > next two gaps, H-dodge).
- [T0, 2026-06-10 ~04:10] FULL machine verification: 797,568-anchor chain (10^7 → 6.7e7), ZERO backtracks,
  every L-path vertex of all 797,566 triples checked: 0 violations (experiments/anchor_tree/build_chain.log,
  chain.json). Also earlier: 40k-anchor chain to 1.07e8.
- [T1, consult 4 verdict, 2026-06-10 ~04:30] SUPPLY WALL CONFIRMED (3rd independent angle): the
  composite-anchor route reduces #1212-YES to the OPEN target: ∃θ<δ<1/2 such that every [x, x+x^θ]
  contains a composite b with P⁻(b) > x^δ. Known every-interval P₂/E₂ theorems lack P⁻-control or need
  exponent >1/2; a.a. theorems (closest: Matomäki JLMS 2022 Thm 1.1 — a.a. x: (x−h log X, x] contains
  Ω≤2 numbers with all prime factors > X^{1/8}, exceptional measure O(X/h); Matomäki–Teräväinen TAMS 2023:
  E₂ in a.a. (x, x+log^{2.1}x]) give measure bounds, not non-clumping; no explicit family survives block
  transitions. My h-tradeoff check: no choice of h closes it (spacing vs budget mismatch at every h).
- COROLLARY (conditional resolution, T1-ready): under a Maier–Pomerance/Cramér-type max-gap hypothesis for
  rough composites (gaps between X^δ-rough composites below X are O(X^θ), θ<δ), Erdős #1212 holds (YES).

## Pending claims
- Matomäki Thm 1.1 exact constants (X^{1/8}, O(X/h)) — verify from PDF at writeup time.

## DECISION (2026-06-10 ~04:35): full resolution blocked by ONE precise open analytic problem.
Execute SECONDARY-OUTCOME pipeline: (1) Lean-formalize core lemmas (isolation lemma; L-path/anchor lemma);
(2) fresh-thread GPT red-team of the package; (3) exhaustive novelty gate; (4) writeup repo + PR
(teorth/erdosproblems per CONTRIBUTING.md) + forum note. Then Phase 1 with next problem.

## Open subgoals
1. Resolve the periodic-certificate dichotomy (consult 2, chat c/6a2890e5).
2. If the periodic route dies: alternatives = (a) multi-affine short-Jacobsthal (consult 1 verdict: R=1
   case is already Maier–Pomerance strength — a wall), (b) substitution/self-similar path schemes,
   (c) compactness/percolation on component growth (needs a density input we do not have).

## Active strategy
Periodic-certificate dichotomy via consult 2; state freshly migrated to ERDOS HUNTER structure.

## Failed approaches (do not retry without a new idea)
1. Near-diagonal lane-1 staircase: anchors isolated at twins/evens (verified).
2. Bounded-band staircases (H <= 96): do not span; small-scale shattering (verified).
3. Prime-square highway + local dodge menus: 60% dodge failure; nested transit pollution unbounded (verified).
4. Two-scale rough-line architecture: needs rough supply in windows ~z => Maier–Pomerance-strength
   Jacobsthal (open); fundamental-lemma wall at z^2 (GPT consult 1 concurs: structural).
5. Witness smuggling via h,v: impossible (C3 tightness).
6. Odd-g certificates: impossible.
7. P={2,3} certificates: impossible (mod-3 deadlock).

## Budgets
- ATTACK iterations: ~8/40. Stall: 2/10 (last verified lemmas: odd-g + C3-tightness, iter 7-8).
- GPT consults since last verified lemma: 1/12 (consult 2 pending).
