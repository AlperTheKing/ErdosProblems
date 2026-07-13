# R2 (GPT-5.6 Pro, 2026-07-13, "Worked for 53m 39s", ~22k ch) — VERDICT: case (c); R-C EQUIVALENT to conjecture; new two-gate reduction (M)+(E)
## [CLAUDE GATE HEADER — all displayed inequalities verified by inspection this tick EXCEPT: (19)-(21) iterated-closure
## recursion (plausible, standard dyadic argument, re-derive before use); Shamazov-Talambutsa + Kolpakov-Talambutsa
## citations UNVERIFIED (L11); theta correction log6/log30 = 0.5268025545 VERIFIED by direct computation.]

## 1. R-C EQUIVALENCE THEOREM (verified exact)
A := G0, B := G2, P := AB. For every X: B(floor(X/3)) <= P(X) <= B(X-1)
  (left: 3 in A, b in B => 3b in AB; right: m=ab => ab-1 in B, m -> m-1 injective).
Color equivalences: b in B => 2b-1 in A (b=2 gives seed 3); a in A minus {3} => 3a-1 in B.
  => d(A) >= d(B)/2, d(B) >= d(A)/3, B(3X) >= G(X)/2 - 1 => d(B) >= d(G)/6.
(5): (1/18) d(G) <= d(G0*G2) <= d(G).  R-C IS the conjecture up to constants — not a weaker step.

## 2. What the energy data prove (verified)
rho := E/(MN); Cauchy-Schwarz |UV| >= M^2N^2/E = MN/rho; kappa = rho * X/(MN).
Balanced rows certify: |(AB) cap [1,10^10]| >= 95,669,919 (from the Y=Z=10^5 row); distinct-product
pair fractions 99.15% / 95.12% / 88.92% at 10^3/10^4/10^5. Strong finite; NO asymptotic content.
MISSING CONDITION = LINEAR PAIR MASS: |UV| <= MN always (10); a single block needs MN >> X (11).
Hyperbolic reservoir R_X = {(a,b) in AxB : ab <= X}: P(X) >= N_X^2/E_X (12); sufficient:
N_X >= eta*X and E_X <= K*N_X (13). CONVERSE: N_X = o(X) => NO energy theorem can work (15).
Global floor E_X >= N_X^2/X (16): aggregation to N_X >> X forces cross-window collisions —
bounded E/N (not ratio -> 1) is the right target.

## 3. Barriers for option (a) with accepted objects (verified except 3.2 as noted)
3.1 Tower: theta = log6/log30 = 0.5268025545 (CORRECTS the 0.517 I quoted; recheck B07 at gate).
    Hyperbolic pair count from tower <= X^theta * logX = o(X) (18). No energy estimate can help.
3.2 Bounded product-closure iterations: H[r](X) <= C_r X^theta (log2X)^(2^r - 1); sublinear
    for ALL depths with 2^r = o(logX/loglogX) (21).
3.3 Reciprocal-summable C x zero-density D => CD zero density (22)-(24) — kills shifted-prime
    supplements to the tower.
3.4 T9*B channel CIRCULAR: d(T9*B) > 0 <=> d(B) > 0 (27) — no independent mass.
3.5 Modular saturation certifies NOTHING about counts/windows/slopes/energy.
3.6 Literature (UNVERIFIED): Shamazov-Talambutsa: free affine semigroup, sum 1/a_i = 1 =>
    orbit >= x/(logx)^((n-1)/2); n=2 needs slopes 2,2 — cannot supply our reservoir directly.
    Kolpakov-Talambutsa Thm 3: sum of reciprocal slopes > 1 => NOT free; 1/2+1/3+1/5 = 31/30 > 1
    => collisions forced in the {2,3,5} system.

## 4. Option (b): scalar bootstrap = WRONG INVARIANT (verified)
Correct normalization: B(CX) >= f(delta)X is an increment only if f(delta) > C*delta (32).
Constant-dilation top-window expansion uses only finitely many multipliers (33) — dead by the
finite-multiplier obstruction. Near-Sidon does not raise the pair-count ceiling (34): one
balanced block gives density SQUARING, not increment.
EXACT MULTISCALE BOOTSTRAP (40): B_j := B cap (2^(j-1), 2^j], delta_j := |B_j|/2^j; pairs
(2b-1)c - 1 in B from B_j x B_(J-j-1); N_J = 2^(J-1) sum_j delta_j delta_(J-j-1); if global
E_J <= K N_J then B(2^J)/2^J >= (1/2K) sum delta_j delta_(J-j-1).
CRITICAL THRESHOLD (41)-(43): delta_j >= c/sqrt(j) + bounded E/N => liminf B(2^J)/2^J >= ~c^2/K > 0.
Critical dyadic profile = 2^j/sqrt(j), i.e. X/sqrt(logX) — the Shamazov-Talambutsa scale.
Tower profile delta_j << 2^(-(1-theta)j) is far subcritical (44)-(45).

## 5. NEW PRIMARY ROUTE R-D: growing-block common-slope affine-offset reservoir
Translate t = x-1: the G-maps become L2(t)=2t, L3(t)=3t+1, L5(t)=5t+3 (46) (verified).
Word with counts (a,b,c): t -> Mt + d, M = 2^a 3^b 5^c, 0 <= d < M (47).
OFFSET RECURSION (48, exact, no injectivity assumed):
  D_{a,b,c} = 2*D_{a-1,b,c}  UNION  (3*D_{a,b-1,c} + 1)  UNION  (5*D_{a,b,c-1} + 3).
Canonical ray: Q = 2^15 3^10 5^6 = 30233088000000; D_k := |D_{15k,10k,6k}| (words W_k =
(31k)!/((15k)!(10k)!(6k)!) exceed Q^k exponentially: log(W_k/Q^k) = 31k log(31/30) + O(logk);
Kolpakov-Talambutsa forces collisions, so no contradiction).
G-blocks: H_k = {8Q^k + d + 1} SUBSET G cap (8Q^k, 9Q^k] (seed x=9, t=8; verified).
Color split + maps 2c-1 / 3c-1 give unconditional U_k SUBSET A, V_k SUBSET B, |U_k|=|V_k| >= D_k/2
in dyadic-type ranges (57)-(59).
GATE (M): D_k >= c Q^k / sqrt(k) for k >= k0  [= the critical 1/sqrt(logX) profile].
  Second-moment sufficient form (63): E^off_{15k,10k,6k} <= W_k^2 sqrt(k)/(c Q^k), where
  E^off = sum_d R(d)^2, R = word-multiplicity of offset d (exact recursion (60)).
  FALSIFIER (64): liminf sqrt(k) D_k / Q^k = 0 (an asymptotic sequence tending to 0; a single
  small value does not falsify since k0 may grow).
GATE (E): aggregated reservoir R_K = union_{k in I_K} U_k x V_{K-k} (central k in [K/4, 3K/4]);
  N_K >= (c^2/8) Q^K under (M); E_K = the GLOBAL cross-k energy (70) — includes all cross-k
  collisions; individual-window energies do NOT imply it.
  Requirement: E_K <= C_E N_K for all large K.  FALSIFIER (73): limsup E_K/N_K = infinity.
THEOREM (verified arithmetic): (M) + (E) => d(G0*G2) >= c^2/(3888 C_E Q) > 0 => d(G) > 0.
Uses: no periodic cover, no fixed automaton, no word injectivity, no poly-growth inference,
no modular decoding — consistent with all six obstructions + R1 barriers.
WEAKER ASYMMETRIC GATE (75): liminf sum_{k in I_K} u_k v_{K-k} > 0 suffices (u_k = |U_k|/Q^k etc.);
symmetric (M) failure does NOT kill the route.

## 6. Fallback: canonical smooth-rough cross-cover (77) — refines R1 (21)
Unique factorization m = s_z(m) r_z(m) (smooth part <= z < least prime factor of rough part):
|A# B cap [1,X]| >= X - E0(s>y) - EA(smooth not in A#) - EB(rough not in B), A# = A/3.
No energy input needed. Needs weighted smooth-membership + rough-membership theorems.

## Final dichotomy (R2's own table)
Energy collision gate: passed at tested scales. Tower/iterations/shifted-primes/T9B: all fail
pair-mass. Scalar bootstrap: invalid. Critical threshold: |B cap (2^(j-1),2^j]| ~ 2^j/sqrt(j).
Next campaign: prove (M) and (E) for the growing affine blocks. Fallback: (77).
SHARP BARRIER: "The accepted constructions provide o(X) admissible factor pairs below product
scale X." Success region: liminf sqrt(k) D_k/Q^k > 0 AND sup E_K/N_K < infinity.
