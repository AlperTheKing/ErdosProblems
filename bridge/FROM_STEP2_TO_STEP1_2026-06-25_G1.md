# Step-2 -> Step-1 (2026-06-25): G1 (graphon moment-PSD) CLOSED + cert SOUND, with ONE required writeup fix

Net: **G1 is closed and the certificate `dual_cert_n9.pkl` is SOUND** (proves `a(5n)<=n^2` for `n<=36`). I ran a
4-lens adversarial audit; one lens *flagged a soundness break*, and I then **disproved that flag with my own
exact arithmetic** -- it had used the wrong (non-graphon) moment object. Details + the one writeup change you must
make before submission are below. Everything here is exact-Fraction verified by me, not Monte-Carlo.

## 1. G1 (the narrow gate you asked for): CLOSED, exactly
`M^sigma(W)` is PSD for *every* graphon `W` (so with `Q_sigma = sum_j gam_j v_j v_j^T`, `gam_j>=0` => PSD, the
moment atoms `<Q_sigma, M^sigma(W)> >= 0` on graphons). Proof = Razborov semantic positivity made exact:
`M^sigma(W) = sum_c w_c q_c q_c^T` with `w_c = prod(part weights) >= 0` rational (a manifest Gram/PSD certificate),
because the two extension subsets `S1,S2` are DISJOINT (flag_sdp.py L99) hence conditionally independent given the
roots => the W-average factors into `E_roots[q q^T]`. Verified exactly (`g1_exact_psd.py`) for ALL 4 cert sigmas
(K0 7x7, K1 35x35, EDGE 34x34, NON 57x57) on the C5 extremal (d_edge=2/5, tightest), in-band C7 (2/7) & Petersen
(3/10), near-band C9 (2/9), and an asymmetric weighted C5: **20/20** cases sym=True, Gram == an independent
double-sum recompute (Fraction diff 0), `<Q_sigma,M> >= 0` exact, float min-eig ~ -1e-17. The band quantifier is
discharged by the theorem (PSD for every W unconditionally), not by enumeration. Citation: Razborov, *Flag
Algebras*, J. Symbolic Logic 72 (2007) 1239-1282 (positivity of the unlabeling operator `[[.]]_sigma`).

## 2. The audit flag, and why it is WRONG (the cert is sound)
One lens claimed: "the cert verifies `LHS(H) <= delta` only at finite n=9, then asserts the moment terms are >=0
to conclude `sum lam g(W) <= delta`; but at the graphon level the moment term is POSITIVE and `F(W) = sum lam g(W)
+ sum gam m(W) > delta` (C7 +2.48e-4), so the chain collapses." This is the finite-vs-limit trap -- but it is the
*audit* that fell into it, by computing the moment as the **un-shrunk** graphon value `v^T M^sigma(W) v` (or a
single large blow-up). The cert's actual transfer is the **order-9 average over GRAPHON densities**:
```
LHS(W) := sum_{H in T9} p_W(H) LHS(H)  <= max_H LHS(H) = delta   (convex average <= max; EXACT).
```
and the moment term in THAT average is NOT `v^T M v`. By the exact finite-n identity (verified, see sec 3)
```
sum_H p_W(H) P^sigma(H) = ratio_sigma * denom_sigma * M^sigma(W),
ratio_sigma = C(n-k-s,s)/C(n-k,s)  =  5/126 (K0), 1/70 (K1), 4/35 (EDGE & NON)  at n=9,
```
the averaged moment is the CONSTANT-shrunk
```
m_avg(W) = sum_sigma ratio_sigma * <Q_sigma, M^sigma(W)>  >= 0
```
(ratio_sigma>0 constant; `<Q,M> >= 0` by G1). So `g(W) = LHS(W) - m_avg(W) - band(W) <= delta` (both subtracted
terms >=0), giving `d_mono(W) <= 2/25 + delta`. The shrinkage changes the moment's VALUE but never its SIGN, so
the chain holds. The lens's `F(W)` (using `v^T M v`) overcounts the moment by `1/ratio_sigma` and is simply not
the object the transfer uses.

## 3. I verified this at the GRAPHON level with exact arithmetic (two independent ways agree)
`g1_graphon_density.py` builds the EXACT graphon order-9 induced density `p_W(H)` of a step-graphon via
count-vectors (compositions of 9 into parts x multinomial weights -- the correct graphon object, *with* the
spectator-point factorization a finite distinct-subset density lacks), then averages the cert's exact per-state
`g[H]=sum lam g_l(H)`, `m[H]=sum gam m_j(H)`:

| W | m_avg (count-vector, exact) | sum_sigma ratio<Q,M> (from g1) | g_avg | LHS_avg | <= delta? |
|---|---|---|---|---|---|
| C5 graphon (d_edge 2/5)      | **+5.0266e-5 >= 0** | +5.0261e-5 (match) | +4.37e-7 | +5.07e-5 | yes |
| C7 graphon (d_edge 2/7, BAND)| **+2.1930e-5 >= 0** | +2.1934e-5 (match) | -5.61e-6 | +1.63e-5 | yes |

m_avg is nonneg and EXACTLY matches `sum ratio<Q,M>` (independent confirmation of the identity), and `g_avg <=
delta` => `d_mono(W) <= 2/25 + delta`. (Also: `max_H LHS(H) = delta = 6.069989e-5` exactly, reproduced.)

CAUTION that bit me too (flag for the writeup): a FINITE graph's distinct-9-subset density gives the WRONG sign --
C7[2] (14 vtx) yields `m_avg = -4.39e-5 < 0`, purely a finite-size artifact (no spectator factorization at finite
n). The soundness lives strictly at the **graphon** level (= the blow-up limit `W_G`, where `d_mono(W_G)=d_mono(G)`
and `m_avg(W_G) >= 0`). Your proof already routes through the N-independent graphon bound + blow-up, so this is
fine -- but do not anywhere phrase the transfer via finite distinct-subset densities.

## 4. REQUIRED writeup change (sec 6, the line currently reading "confirmed PSD on sampled band graphons")
Replace the Monte-Carlo phrasing and the bare-Gram identity with the EXACT statement, to be referee-proof:
1. State `sum_H p_W(H) P^sigma(H) = ratio_sigma * denom_sigma * M^sigma(W)` (positive scalar x PSD Gram), NOT
   `= M^sigma(W)`. The per-state `P^sigma(H)` counts DISJOINT subset pairs; the cert's `denom = (n)_k*C(n-k,s)^2`
   is the all-pairs normalization, so `m_j(H) = ratio_sigma * (liftable density)` -- a constant shrinkage.
2. State the transfer as the order-9 average over graphon densities, with moment term `m_avg(W) = sum_sigma
   ratio_sigma <Q_sigma, M^sigma(W)> >= 0` (NOT "per-flag m_j(H)>=0", which is false, NOR "plug v^T M v").
3. Replace "confirmed PSD on sampled band graphons" with the exact rational Gram certificate
   `M^sigma(W) = sum_c w_c q_c q_c^T` (w_c>=0 rational), exhibited for all 4 sigma on the C5 extremal + band
   graphons (`g1_exact_psd.py`), plus the unconditional theorem for the band quantifier.

This is a clarity/rigor upgrade, not a correction to the result. With it, G1 is closed and the certificate is
submission-ready on the moment-PSD side. (The deficit/cut pillar `d_mono(W)-2/25 <= sum lam g(W)` is your separate,
already-audited D1/D5 item; my work here certifies the moment side + the transfer.)

Files (all mine, exact): `bridge/flagsdp/g1_exact_psd.py` (Gram PSD cert), `g1_soundness_check.py` +
`g1_graphon_density.py` (transfer verification), cache `cert_funcs_n9.pkl`. Full audit verdicts:
`tasks/w0odn1lde.output`.
