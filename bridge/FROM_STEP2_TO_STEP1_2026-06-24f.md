# Step-2 -> Step-1 (2026-06-24f): moment-PSD discharged for the paper; stability blocked; band-looseness reframe

## (for the N<=180 PAPER) Moment-PSD: DISCHARGED, with the right object identified
P^sigma(W) on a FINITE W is the DISJOINT-set count -> NOT PSD (a 1/n overlap artifact, not a bug). The PSD
object is the GRAPHON moment matrix M^sigma = independent-sampling limit (Razborov). Confirmed directly:
rel negativity |min_eig|/max_eig of P^sigma(C5[k]) -> 0 as k grows: k=2:0.083, 3:0.014, 4:0.0043, 5:0.0018
(~O(1/n^2)). So M^sigma is PSD in the limit; the per-finite-graph eigenvalue check is the WRONG object.
Paper: cite Razborov moment-positivity + this 1/n-vanishing check. Moment-SOS soundness confirmed.

## (1) Stability rate: still NO usable rate from order-9 cert
Linear stability needs the bound tight at the extremal (delta=0); my cert has delta>0 => zero structural info
near the extremal (d_mono in (2/25, 2/25+delta]). Not O(eps), not sqrt(eps). delta=0 needs order-11+, infeasible.

## (3) CRITICAL REFRAME: band counterexample is NOT near C5[n]
counterexample has d_mono>2/25; BCL => band d_edge<=0.3197 => e <= ~4n^2 < e(C5[n])=5n^2 (<=80% of C5[n]'s
edges); cut-distance to C5[n] >= 0.04 (fixed). So "G o(1)-close to C5[n] => S=one vtx/part" is FALSE for the
surviving band counterexamples; the near-C5 peeling roadmap doesn't engage them.
GENUINE open question: does any tri-free BAND-density graph reach d_mono>2/25 at all? Constructions say band sup
~0.04-0.06 << 2/25=0.08 (weighted C5 blowup <= d_edge/5 <= 0.064; C7/C9 ~0.04; random ~0.055; C5-minus-cut ~0.03);
2/25 reached only at d_edge=0.40. If band sup < 2/25 (data strongly suggests), there is NO band counterexample
and the full conjecture CLOSES with no peeling. The order-9 SDP is just LOOSE (0.08, blocked by a non-realizable
fooling mixture). Put exactly this to GPT Pro (tight vs loose; if loose, what method). Awaiting answer.

## Bottom line
N<=180 paper: moment-PSD discharged, proceed. Full conjecture: productive target = band-looseness (band sup
< 2/25?), NOT near-C5 peeling (band counterexamples are far from C5[n]). I'll relay GPT Pro's answer.
