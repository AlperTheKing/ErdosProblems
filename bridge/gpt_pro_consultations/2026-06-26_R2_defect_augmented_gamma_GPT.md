# GPT Pro: R2 = the DEFECT-AUGMENTED GAMMA inequality (chat 6a3e68cf) — the chosen proof route for delta=0

GPT Pro (Comprehensive). Drove browser myself. Answer to "which route, R1 (descent) or R2 (Gamma>=N^2 kills
obstructions directly)?". VERDICT: **Formalize R2, not R1.**

## Why R1 is rejected
My N=8 example has NO safe peel, so any universal "unsafe => successor => terminal safe peel" is FALSE unless
the descent terminates in a low-Gamma sink. That needs a separate "terminal unsafe => Gamma<N^2" theorem — which
IS R2. So R1 reduces back to R2. R1 stays a diagnostic tool, not the theorem to formalize first.

## THE MASTER INEQUALITY (R2)
   Gamma(G) + D*(G) <= N^2 ,   where D*(G) := min over shortest bad-geodesic peels C of D(C).
D(C) = residual CD-defect = max_{S subset R=V\C} (delta_{M[R]}(S) - delta_{B[R]}(S))_+  ; D(C)=0 <=> CD preserved.
Stronger LOCAL version (R2-local): D(C) <= N^2 - Gamma(G) for EVERY shortest bad geodesic C. Min-version suffices
for safe-peel existence. If Gamma>=N^2 then D*(G)=0 => some shortest peel preserves CD. (Tight: D=0, equality.)

## Mechanism — prefix defect
From CD on S U P_i (w_R(S)=-eta): e^sigma(C\P_i,S) + e^sigma(P_i,R\S) >= eta for all i  [PREFIX DEFECT].
The SAME residual defect eta appears for every zero-prefix of the geodesic. In the clean single-block proof each
prefix inequality gives a shell product a_i a_{i+1} >= q. With the residual defect it upgrades to
   a_i a_{i+1} >= q + eta/h^2     (h=|C|; the block contributes h^2 q to Gamma; normalization h^-2 is correct).
Do NOT force a_i a_{i+1} >= q+eta — too strong; the N=8 unsafe example shows that would be false. (For C5: the
honest bound is the shell-product, NOT the false 50+25<=64.)

## DEFECTIVE SHELL EXTRACTION LEMMA (first proof target)
Let C=v_0..v_{h-1} be a SHORTEST bad geodesic, S subset R=V\C a residual CD-obstruction with
   eta = delta_{M[R]}(S) - delta_{B[R]}(S) > 0.
Then the bad mass controlled by the C-block admits cyclic shell sizes a_0..a_{h-1} with
   sum_i a_i <= n_block ,   normalized bad mass q = Gamma_block / h^2 ,
   and   a_i a_{i+1} >= q + eta/h^2   for all i (mod h).
Consequently   Gamma_block + eta <= n_block^2 . After square-gluing over remaining blocks:
   Gamma(G) + eta <= N^2 . This proves D(C) <= N^2 - Gamma(G); in particular Gamma>=N^2 => eta=0 => C CD-preserving.

## Shortestness is exactly the needed hypothesis (3 uses)
1. C is B-isometric: no B-chord jumps along C; an outside vertex cannot have B-attachments to widely-separated
   vertices of C (else not shortest).
2. Triangle-freeness prevents mixed adjacent attachments: z v_i in B => z v_{i-1}, z v_{i+1} NOT bad edges. Keeps
   the shell products honest (no overcounting).
3. Prefix P_i has zero signed internal boundary only when the geodesic is shortest / B-metric-induced. The N=11
   non-shortest counterexample deletes cut-capacity NOT part of the metric shell certificate — that is exactly why
   defective shell extraction fails there.
So shortestness lets the residual defect -eta be transported uniformly into the cyclic AM-GM inequalities.

## RECOMMENDATION
Formalize R2 as the defect-augmented Gamma lemma  Gamma + D*(G) <= N^2 . First nontrivial proof target = the
Defective Shell Extraction Lemma above. (My N=8 / C5 computations already see the tight D=0 equality cases.)

## MY VALIDATION PLAN (audit+compute)
1. EXHAUSTIVELY verify the master inequality Gamma(G)+D*(G) <= N^2 for ALL connected-B triangle-free max-cut
   configs N<=11/12 (and the local D(C)<=N^2-Gamma). A single violation kills R2.
2. Test the intermediate a_i a_{i+1} >= q + eta/h^2 shell bound on the obstruction instances.
