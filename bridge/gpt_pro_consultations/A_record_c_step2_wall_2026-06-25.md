# GPT Pro FINAL DECISION (2026-06-25): record (c) — Step-2 band is the sharply isolated open wall

chat 6a3b5aba. After I reported the audited order-10 selective-lift result (eta: 6.559e-5 -> E10 6.031e-5 ->
+C5-diagonal 6.010e-5, stays POSITIVE; fooling 10-extendable AND C5-multiplicative), GPT's verdict:

## Decision: record (c). The present route is EXHAUSTED.
"order-9 cone + 10-vertex marginal extension + t(C5⊔C5)=t(C5)^2  STILL admits an exact feasible pseudo-state with
d_mono > 2/25. Therefore no certificate formed solely from those constraints can close Step-2." The public frontier
is unchanged: BCL prove the bound OUTSIDE the normalized edge-density band [0.2486,0.3197]; the best unrestricted
published bound is n^2/23.5 (a June 2026 paper still identifies n^2/23.5 as the best known triangle-free bound;
Erdős #23 remains listed open).

## The ONLY plausible path (option b) — but a MAJOR new attack, NOT a routine lemma
A quantitative STABILITY theorem:
   d_mono(W) >= 2/25 - eps  =>  W is close to a balanced C5-blow-up  =>  d_edge(W) >= 2/5 - o_eps(1),
contradicting the medium band. "But I do not have a proof or a finite local inequality producing that stability.
Establishing it would itself be a major new attack on the conjecture, rather than a missing routine lemma."
(= exactly the option-C analytic-stability / self-tight wall the project already identified as research-open.)

## What the deliverable should claim (record SEPARATELY)
1. PROVED RESULT:  a(5n) <= n^2 for every 5n <= 180, via the exact rational order-9 certificate + uniform blow-up
   + BCL density tails + integer rounding. [G1 moment-PSD now CLOSED + sound, [[erdos23-step1-g1-moment-psd-closed]].]
2. EXACT ASYMPTOTIC NEAR-THEOREM:  d_mono(W) <= 2/25 + 6.07e-5  on the band. INCLUDE the exact rational PRIMAL
   WITNESS attaining d_mono ~ 2/25 + 6.0e-5 -- "that establishes rigorously that this entire certificate cone is
   insufficient."
3. SOLE REMAINING STATEMENT (the wall):  d_mono(W) <= 2/25  for triangle-free W with d_edge in [0.2486,0.3197].
   "That is now the sharply isolated Step-2 wall. Recording it is the correct strategic endpoint rather than
   spending substantial computation on a full order-10 or order-11 hierarchy without a newly diagnosed separating
   constraint."

## CONCLUSION (mine, following GPT per [[gpt-pro-decides-path]])
The GPT-Pro Step-2 path (disjunctive multiplicativity -> order-9 kill criterion -> selective 9->10 C5-lift ->
stopping rule) is followed to its honest end: the SDP-hierarchy route CANNOT close Step-2. The band is the genuine
open wall (= the unresolved BCL medium-density barrier). Step-2 full closure needs a major new attack (the
stability theorem), beyond the current machinery. LOOP ENDED. Deliverable = (1)+(2)+(3) above.
