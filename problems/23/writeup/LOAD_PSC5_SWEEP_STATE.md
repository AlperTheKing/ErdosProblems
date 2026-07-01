# LOAD-PSC-5: sweep-angle proof state (2026-07-01)

Target (theorem-sufficient; downstream LOAD-PSC-5 => beta<=N^2/25 is established):
for every connected-B gamma-min maximum cut of a triangle-free graph and every
threshold tau>=0, with a=a_tau(v)=min(T(v),tau),

    5 * sum_v a(L-a)  >=  N * ( TV_B(a) - TV_M(a) ),      L = N + N^2/25 - m.

## 1. Exact coarea reformulation (verified)
Let H_s={v:T(v)>s}, sigma_s = delta_B(H_s)-delta_M(H_s). Layer-cake identities
(machine-verified, `_sweep_struct_probe.py`):
  * sum_v a_tau           = int_0^tau |H_s| ds
  * sum_v a_tau(L-a_tau)  = int_0^tau (L-2s)|H_s| ds
  * TV_B(a_tau)-TV_M(a_tau) = int_0^tau sigma_s ds       (signed coarea)
Hence LOAD-PSC-5 <=> the running prefix
  Phi(tau) = int_0^tau I(s) ds >= 0  for all tau,   I(s)=5(L-2s)|H_s| - N*sigma_s.

## 2. PROVEN per-level fact: sigma_s >= 0 for EVERY super-level set
For a GLOBAL max cut and any vertex set S, flipping S changes the cut by
delta_M(S)-delta_B(S) <= 0, so delta_B(S) >= delta_M(S). Taking S=H_s gives
    sigma_s = delta_B(H_s) - delta_M(H_s) >= 0     for all s.
Machine-verified 0 failures over 735,360 super-level sets (`_sigma_sign_gate.py`).
This is stronger than the coarea integral TV_B-TV_M>=0; it is pointwise.

## 3. Why the proof is genuinely a SWEEP, not per-level (all machine-verified)
  * Per-level band < 0 occurs: min single-level band = -67562 (k-lane L18),
    `_codex_prefix_loadpsc_gate.py` `best_band`.
  * Pointwise `sigma_s <= 5|H_s|` is FALSE: sup sigma_s/|H_s| = 6 (k-lane L20),
    `_sigma_5H_gate.py`.
  * The integrand I(s) is NOT single-signed: 5691 gamma-min cuts (N=9..11) have
    I go - then + (Phi non-unimodal), `_psc5_unimodal_gate.py`. So the endpoint
    value does NOT dominate the prefix; intermediate tau must be controlled.
  * No local reservoir closes it: N*sigma_s <= 5(L-2s)|H_s| + c*above(s) fails
    (c=5,10) at high levels, `_reservoir_gate.py`.
Consistent with the stated NEGATIVE CONTROL: any argument must survive two-lane
and be first-moment; spectral rho<=N / ||T||^2<=N*Gamma are false here.

## 4. The exact CRUX (open): running capacity dominates running pressure
Define Cap(tau)=5*int_0^tau (L-2s)|H_s| ds = 5 sum_v a(L-a) and
Pr(tau)=N*int_0^tau sigma_s ds = N(TV_B(a)-TV_M(a)). Machine-verified:
    max_tau Pr(tau)/Cap(tau) = 0.993976 < 1   (`_abel_direction_gate.py`)
i.e. the target holds with running ratio strictly < 1, tight (->1) but never
reached; equality only at balanced C5[t] (D=0, T=N, both sides 0).
Also verified clean auxiliary global bound:
    TV_B(a) - TV_M(a) <= 6 * sum_v a         (exact, ratio-max = 6, k-lane L20).
This bounds pressure by mass with constant 6; but 6 > 5, so it alone does not
close (need domination by capacity 5(L-2s)|H|, which decays at high s).

## 5. Honest obstruction
The single missing step is an Abel/summation-by-parts (or minimal-counterexample
switch) argument turning:
  (a) sigma_s >= 0 (proven), (b) nesting H_s decreasing, (c) the geodesic-flow
  identity T(v)=sum_f ell(f)p_f(v),
into the RUNNING bound Cap(tau) >= Pr(tau). The difficulty is real and is exactly
the point the task flags: pressure at high load levels locally exceeds capacity,
and only the early (low-s, large-|H|, small-sigma) surplus carried forward pays
for it. A correct proof must transport the low-level capacity surplus to the
high-level pressure deficit. The switch route (ANGLE) needs a NEUTRAL (sigma=0)
connected switch at the first-failure level; but sigma_s>0 generically, so the
switch must be a partial/geodesic-local move, not a full flip of H_s -- this
construction is not yet in hand.

## 6. Endpoint does NOT escape the sweep
Only the endpoint Phi(maxT)>=0 is needed downstream (LRS-sufficient), which is
the single inequality 5 sum_v T(L-T) >= N(TV_B(T)-TV_M(T)) (verified 0 viol,
189459 cuts, `_endpoint_psc5_gate.py`, ratio<=0.994). But TV_B(T)-TV_M(T) is
itself the coarea integral int sigma_s ds, so the endpoint = int_0^{maxT} I(s)ds
with I not single-signed. Per-edge flow decomposition FAILS: |T(u)-T(v)|<=mu(e)
and TV_B<=sum_{B}mu both false (two-lane TV_B=432 > sum mu=176,
`_edge_gradient_gate.py`), so no per-edge charging; the max-cut domination must
be used globally through the signed coarea. Conclusion: endpoint and full-prefix
share the identical open crux (Section 4).

Files (all exact Fraction gates): `_sigma_sign_gate.py`, `_psc5_unimodal_gate.py`,
`_endpoint_psc5_gate.py`, `_edge_gradient_gate.py`,
`_sigma_5H_gate.py`, `_reservoir_gate.py`, `_abel_direction_gate.py`,
`_sweep_struct_probe.py`, `_psc5_integrand_probe.py`, `_psc5_dump_one.py`.
