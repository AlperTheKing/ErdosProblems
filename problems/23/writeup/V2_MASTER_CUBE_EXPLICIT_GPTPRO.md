# V2-Layer Master-Cube: EXPLICIT Certificate Spec (GPT-Pro, 2026-07-03, sibling thread)

Rational-before-clearing (row denominators depend on mu) => Bernstein on cleared
numerator with sign-fixed positive denominator. EQ bad edges g19=(1,9), g72=(7,2),
g79=(7,9); seed maximizer Q* = R8 = (7,5,8,6,9).

## Construction
Passive V2 attachment: weight t >= 0, pair fractions mu34, mu36, mu54, mu56 in [0,1].
Seed path families: P19 = {(1,5,0,6,9),(1,5,8,4,9),(1,5,8,6,9)};
P72 = {(7,5,0,6,2),(7,5,8,6,2),(7,3,8,6,2)}; P79 = {(7,5,0,6,9),(7,5,8,4,9),
(7,5,8,6,9),(7,3,8,4,9),(7,3,8,6,9)}. omega(i,l,m,r,j) = w_l w_m w_r (interior product).
Delta_h = sum of omega over P_h (seed denominators); Lambda_h^R = sum omega(P) pi_R(P)
(seed numerators; pi_R(P) has 1/w_z factors); attachment increments delta_h^R linear in
mu (e.g. delta_19 = w5 w4 mu54 pi(1,5,*,4,9) + w5 w6 mu56 pi(1,5,*,6,9); delta_79 has
all four mu terms). Theta_h = Lambda_h + t delta_h; I_ext = sum_h (w-pair)_h
Theta_h/Delta-tilde_h. Cleared defect D_R = Q E_R, Q = prod Delta_h prod Delta-tilde_h
> 0; expanded form (8) without division; polynomial numerator P_R = W D_R with
W = prod w_i (clears pi's 1/w_z).

## t-scaling: t=1 NOT SUFFICIENT
Defect affine in t per Theta_h but cleared denominator multiplies three of them =>
NOT linear in t. Compactify tau = t/(1+t) in [0,1]: Theta-tilde_h = (1-tau) Lambda_h +
tau L-tilde_h. Final certificate variables: (mu34, mu36, mu54, mu56, tau) in [0,1]^5.

## Certificate (per row template R0..R10, the 11 audit rows)
P_{R_i} >= 0 on the 5-cube under the EQ seven-cut w-cone; degree <= 3 in mu, <= 4 in
tau; each Bernstein coefficient = polynomial in w, certified in the w-cone; BINDING
ROWS get CERT-2-style seed-vanishing (factor the vanishing ideal at the calibration
point first). R8 = seed row binds at (tau=1?, mu=0) baseline; WHICH OTHER rows bind at
the nontrivial tau_0 must be evaluated by script (exact tau_0 coordinates needed) —
extra zeros route through seed-vanishing, nonzero rows use ordinary positive Bernstein.
GPT-Pro note: build the 11 numerators from the displayed Lambda/delta formulas
programmatically — do NOT hand-expand (transcription risk).
