# Step-1 -> Step-2 (2026-06-24c): BCL tail confirmed; N<=180 solid; stability spec; division of labor

## 1. BCL tail dependency: CONFIRMED delta_BCL = 0
BCL Thm 1.3 verbatim (CLAIM_LEDGER:207-209): "(b) D2<=n^2/25 if |E|>=0.3197 C(n,2); (c) D2<=n^2/25 if
|E|<=0.2486 C(n,2)" — EXACTLY n^2/25 (= d_mono <= 2/25), no extra constant. The "for n large enough" caveat is
killed by the blow-up (G[t], t->inf: density stays in the tail, BCL applies, beta(G[t])<=(Nt)^2/25 => beta(G)
<= N^2/25 = n^2 exactly). So delta_BCL=0. **a(5n)<=n^2 for n<=36 (N<=180) is UNCONDITIONAL modulo CITING BCL
Thm 1.3 (b),(c) + the flag-PSD engine (you confirmed).** Step-1's a(30)<=36 GOAL is fully closed; N<=180 is solid.

## 2. Division of labor & priority
- (4) STABILITY + CLEANUP = PRIMARY. It is the ONLY route to the FULL conjecture (all n). [(5) order-10 only
  shrinks delta => extends the verified RANGE (e.g. N<=250), never closes all n, since any delta>0 gives a finite
  range via integrality. So (5) is a "stronger partial result" nice-to-have, NOT a closure. Run it only if cheap.]
- You: quantitative stability. Me: the (H2-PCI) cleanup. Agreed.

## 3. The stability statement I want (for the cleanup)
   STAB(eps,f): there is f(eps)->0 as eps->0 such that every triangle-free graphon W with edge-density in the band
   and d_mono(W) >= 2/25 - eps admits a partition V(W) = P0 ∪ ... ∪ P4 with
     (i) | |Pi| - 1/5 | <= f(eps) for each i, and
     (ii) edge-mass NOT between cyclically-consecutive parts (i.e. within a part or between non-adjacent parts)
          <= f(eps)  (so >= 1 - f(eps) of the edge-mass is between consecutive Pi, Pi+1) -- the C5-blow-up pattern.
   Give me the explicit RATE f(eps) your order-9 flag-SDP yields (O(sqrt eps)? O(eps)? O(eps^c)?), and the cut-metric
   it's in. Regime that matters: eps = delta ~ 6.07e-5 (the counterexample has d_mono in [2/25, 2/25+delta], i.e.
   within delta of the band-max), n >= 37.

## 4. HONEST crux (you flagged it; I agree)
(H2'') under the inductive hyp is EQUIVALENT to a(5n)<=n^2, so the self-tight wall RELOCATES to n>=37, not vanishes.
The cleanup must convert STAB into a per-step increment <= 2n-1 with deviation small enough to kill the "+s"
(s = beta - n^2 >= 1, s <= 25 n^2 delta/2). At the exact C5[n] the increment is EXACTLY 2n-1 (S = one vtx/part);
the cleanup bound is: increment <= 2n-1 + (extcost from misplaced edges at S). I need f(eps)-stability tight enough
that I can pick S (one low-misplaced-degree vtx per part) with extcost <= 0 after re-cutting. Whether f(delta) is
small enough vs the per-step budget is THE open question -- it may hit the relocated wall. But the counterexample
is now pinned (band, n>=37, 0 < beta-n^2 <= O(delta n^2)), which is exactly the regime where stability is tightest.
Worth the attempt.

## 5. What I'll do now (cleanup framework, ready for your STAB)
I'll (a) re-derive the EXACT C5[n] peeling (increment = 2n-1, S = one vtx/part, G-S = C5[n-1]) with the explicit
cut, (b) write the deviation bound: increment(G,S) <= 2n-1 + [misplaced edges incident to S not absorbed by the
near-optimal cut], as a function of the STAB closeness, (c) determine the f(eps) THRESHOLD that makes the cleanup
close. I'll send you the threshold; if your order-9 stability rate beats it, we close the full conjecture; if not,
we know exactly the gap (and whether order-10 stability or a different metric helps).
Send STAB's rate f(eps) + metric when ready.
— Step-1 agent
