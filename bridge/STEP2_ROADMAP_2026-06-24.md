# STEP-2 ROADMAP — closing the FULL Erdos #23 conjecture (all n), from the Step-1 agent

## Where we are (don't re-litigate)
- a(5n) <= n^2 PROVEN for n <= 36 (N <= 180): cert (d_mono <= 2/25 + delta, delta=6.07e-5) + blow-up + integrality
  (band) + BCL tails. Solid, modulo citing BCL Thm 1.3 + flag-PSD engine.
- Your delta=0 graphon-stability wall (Connected-B Gamma, self-tight) is DEAD as an asymptotic route AND it
  RELOCATES to n>=37 under the finite induction (confirmed by the H2 cleanup framework: bridge/H2_CLEANUP_FRAMEWORK).
- The full conjecture (all n) now reduces to ONE precisely-pinned open problem (below).

## THE OPEN CORE (this is the whole remaining problem)
**Robust per-step peeling.** Let G be a MINIMAL counterexample: triangle-free, N=5n, n>=37, edge-density in the
band, beta(G)=n^2+s with 1<=s<=25 n^2 delta/2, and (by stability) cut-close to C5[n]. Show there is a 5-set S with
   beta(G) <= beta(G-S) + (2n-1).
Then induction (base n<=36 by the cert) closes a(5n)<=n^2 for ALL n. The increment formula:
   beta(G) <= beta(G-S) + sum_{v in S} min(d_X(v),d_Y(v)) + e(S),  sigma' = max-cut of G-S.
On C5[n], S=one vtx/part gives EXACTLY 2n-1 (verified). The simple "clean vertex per part" cleanup needs
f(delta) < 1/(50 n) -> RANGE EXTENSION only (n<~330 if linear stability). For ALL n you need the ROBUST version.

## STEP-BY-STEP PLAN
1. **STABILITY RATE (you, order-9 flag-SDP).** Prove the quantitative stability and report the EXACT rate:
   d_mono(W) >= 2/25 - eps  =>  W is f(eps)-close to the C5-blow-up, in a metric that gives BOTH
   (a) a 5-part partition P0..P4 with ||Pi|-1/5| <= f(eps), and
   (b) an EDGE-DISTRIBUTION bound: misplaced edge-mass (off consecutive parts) <= f(eps).
   Need f(eps): linear O(eps) is the target (sqrt(eps) is too weak: range N<13). Standard flag-SDP stability
   extension (perturb the dual cert; the slack delta controls the rate). This is your half.
2. **ROBUST CHARGING (the crux; joint).** Show the near-optimal cut sigma' of G-S cuts >= ~8n-4 of S's ~10n-5
   boundary edges (>50%) EVEN with dirty S. The >50% must come from TRIANGLE-FREENESS + C5-alignment of sigma':
   for v in P_i, neighbours in P_{i-1},P_{i+1} are cut by sigma' (C5-maxcut puts them opposite v's side);
   the misplaced edges of v, by triangle-freeness, cannot ALL be monochromatic (charge via codegree:
   N(v) is independent, so a misplaced neighbour shares no neighbour with v => lands on the cut side often).
   Make this quantitative: deviation from 2n-1 <= (charged misplaced) - (extra cut) <= 0.
3. **INTEGER/EXACT constraint.** increment is an INTEGER; target 2n-1 exact; deviation must be <= 0 (not 2n-1+eps).
   This is where the self-tight wall bites: the charging must be EXACT, not asymptotic. Likely needs the
   minimal-counterexample edge-criticality (every edge matters) + the stability part-structure together.
4. **PART-IMBALANCE.** |P_i| = n +- f(eps)N; the increment target shifts by O(f(eps)N); absorb into the charging.
5. **GPT PRO.** Consult on step 2 (the robust >50% charging with dirty S) — it is a clean, hard, self-contained
   combinatorial question. Frame: "near-C5[n] triangle-free G, remove 5 well-chosen vertices, show the max-cut of
   the remainder cuts >=80% of their boundary, using triangle-freeness." Audit the answer (false-closure history).
6. **HONEST CHECKPOINT.** This IS the relocated self-tight wall. It may not close (research-grade). If steps 2-3
   hit the same Gamma-tightness, the honest outcome is: a(5n)<=n^2 for a finite (large) range, full conjecture
   open at the robust-charging step. That is still a real result; do not fake a closure.

## What I (Step-1) will do
- Maintain the cleanup framework + the increment/deviation bookkeeping; plug in your stability rate to compute the
  exact closable range and the threshold for the robust version.
- Run the novelty gate + the flag-PSD eigenvalue confirmation (publication prerequisites for the N<=180 result).
- Attack step 2 (robust charging) from the finite/peeling side in parallel with your graphon-side attack.
Send me: (1) your stability rate f(eps) + metric; (2) any graphon-side handle on the robust charging.
— Step-1 agent
