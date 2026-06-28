# Direct-ROWSUM-O multi-angle workflow — honest findings (2026-06-28)

5 agents (4 finders + adversarial synthesizer), 373k tokens, exact-Fraction throughout. Net: NO new lever
that CLOSES #23; one genuinely-new-but-insufficient inequality (M-avg); a concrete charging reformulation;
SOTA literature. The synthesizer correctly flagged 3 of 4 angles as exact RE-STATEMENTS of ROWSUM-O.

## Exact identities (verified on witness + census + blow-ups)
- GRAM-TRACE:  sum_f ROWSUM(f) = sum_v S(v)^2 = 1^T O 1  (O=P^T P, P[v,f]=p_f(v)).
- LOAD-CONSERVATION:  sum_v S(v) = sum_f ell(f).
- sum_v p_f(v) = ell(f) for EVERY bad edge (single AND multi-geodesic).
- O[f,f] = sum_v p_f(v)^2 <= ell(f), equality iff f single-geodesic.

## The one genuinely new inequality: M-avg
   **sum_v S(v)^2 <= N * |M|**   (equivalently: AVERAGE ROWSUM over bad edges <= N).
- Exact-verified 0 failures: census N<=11, witness K??CE@A{?]Fc (all 11 cuts), blow-ups C5/C7/C9[t].
- TIGHT (ratio exactly 1) at every odd-cycle blow-up extremal (S(v)=N/ell uniform).
- BUT strictly WEAKER than ROWSUM-O: bounds the AVERAGE row-sum, not the max. rho(O) <= MAX row-sum, NOT
  avg, so **M-avg does NOT bound rho(O) and does NOT close #23.** Witness: avg=39/4=9.75 < max=56/5=11.2 < 12.
- Caution (mine): the obvious proof route sum S^2 <= (max S)(sum S) needs max_v S(v) <= N/5-ish, which is the
  DEAD overloaded-vertex bound (false at N=1212). So M-avg's own proof is non-trivial; it is a clean true
  fact but not on the critical (spectral) path.

## The charging reformulation -- DEAD (my exact gate refuted it; the synthesizer's "avenue" was wrong)
Identity: N - ROWSUM(f) = sum_v (1 - p_f(v)S(v)) = (N - |supp(f)|) + sum_{v in supp(f)}(1 - p_f(v)S(v)).
ROWSUM-O <=> sum_{v in supp}(p_f S - 1) <= N - |supp| -- but the |supp| cancels, so this is JUST ROWSUM-O
(no reduction). The CHARGING interpretation drops the underloaded corridor vertices (keep only overloaded
hubs): sum_{v in supp} max(0, p_f S - 1) <= N - |supp|. **EXACT-FALSE on my uncapped gate**
(_mavg_charge_verify.py: census charge-FAIL N=8:27, N=9:90, N=10:754, while ROWSUM-O 0 fails). => the
UNDERLOADED corridor vertices (p_f S < 1) supply ESSENTIAL negative credits; you CANNOT drop them. A pure
cardinality-injection of overload-units to off-corridor vertices CANNOT prove ROWSUM-O. The proof must use
the FULL SIGNED accounting (overload at hubs offset by underload elsewhere in the corridor AND the off-corridor
count). Cardinality-charging joins the graveyard.

## CONFIRMED on my uncapped gate (_mavg_charge_verify.py)
M-avg: 0 fails census N<=11. Gram-trace identity: 0 fails. ROWSUM-O: 0 fails. CHARGE(max): FAILS (see above).

## Dead Gram routes (exact counterexamples, do not retry)
- Cauchy-Schwarz ell(f)*sum_v p_f(v)S(v)^2 <= N^2 : FALSE (J???E?pNu\? N=11, CSQ=1145/9>121).
- diagonal/off-diagonal split offd(f) <= N-ell(f) : FALSE (N=8 G?bF`w, N=10 I?rFf_{N?).
- per-support sum_{v in supp(f)} S(v) <= N : FALSE (12.5,13 > 12 on witness multi-geo edges).

## Literature (SOTA on the actual problem; different route)
- Balogh, Clemen, Lidicky, "Max Cuts in Triangle-free Graphs," arXiv:2103.14179: bipartite by deleting
  <= n^2/23.5 edges; Erdos n^2/25 verified for edge-density <=0.2486 and >=0.3197. Method = FLAG ALGEBRAS.
- Erdos-Gyori-Simonovits (1992): proved for >= 5n^2 edges.
- Estrada-Higham-Hatano betweenness spectral bounds: scalar betweenness vs Laplacian, does NOT specialize to
  per-bad-edge Gram row sums. No importable inequality.

## ⭐ LITERATURE IMPLICATION (honesty checkpoint)
Balogh-Clemen-Lidicky 2021 (flag algebras) is SOTA on the ACTUAL conjecture and only reaches n^2/23.5 in
general (n^2/25 only for edge-density <=0.2486 or >=0.3197; the middle range OPEN). So **the full Erdos
n^2/25 / delta=0 conjecture is OPEN in the literature** -- the best researchers with heavy flag-algebra
machinery have NOT closed it. Our ROWSUM-O route is a NOVEL attack on a genuinely open research problem, which
recontextualizes the difficulty: closing it = a research-level breakthrough, not a formalization. (Step-1, the
FINITE a(5n)=n^2 for N<=200, is separately DONE+published; delta=0 is the general/asymptotic conjecture.)

## Verdict (post-verification)
Real open core unchanged: prove MAX O-row-sum <= N. AVG (M-avg) is provable-looking but does NOT bound rho(O).
The charging/injection avenue is DEAD (underload credits essential). Remaining honest leads: (a) is M-avg
independently provable, and if so can the avg->max SPREAD of O-row-sums be bounded? (b) a global signed
accounting (not injection). This is research-frontier hard (conjecture open in literature). Chance of a full
proof via this route: LOW (~12-18%, recalibrated down by the literature finding).
