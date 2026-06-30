# (CV) per-component spectral certificate — route + exact gate

Gate: `_wf_cv_perspec.py` (exact Fraction, full standing battery). Reference: `_cv_gate.py`.

## Target (CV)
For a triangle-free max-cut graph, per K-component `c`:
```
w^T O_c w  <=  (N + eta) * Gamma_c ,      eta = N^2/25 - beta ,  A := N + eta.
```
with `O_c[f,g] = <p_f,p_g> = sum_v p_f(v)p_g(v)` (edge-Gram over bad edges f,g of c),
`w_f = ell_f/|cyc_f|`, `Gamma_c = sum_{f in c} ell_f^2`. Equivalent to `sum_{v in c} T_v^2 <= A*Gamma_c`.

## Three candidates tested (exact, full battery 190,317 components)
- **(i) `rho(O_c) <= A`** (PSD of `A I - O_c`). **DEAD: 170,323 violations**, first C5[2].
  Reason: `w^T O_c w <= rho(O_c)||w||^2`, but `||w||^2 = sum w_f^2 << Gamma_c = sum ell_f^2`
  exactly where (CV) is tight (C5[t]), so the `||w||^2<=Gamma` bound is far too lossy.
- **(ii) `A D - O_c` PSD**, `D = diag(|cyc_f|^2)`. **HOLDS: 0 violations.**
  Lossless implication: `w^T O_c w <= A w^T D w = A sum_f w_f^2|cyc_f|^2 = A sum_f ell_f^2 = A Gamma_c`
  (uses `w_f|cyc_f| = ell_f`, and `Gamma_c = w^T D w` is an EXACT identity, gate-verified).
- **(GERSH)** the Gershgorin row-bound of `Dm := D^{-1/2} O_c D^{-1/2}`, i.e. for every bad edge `f`:
  ```
  R_f := sum_{g in c} <p_f,p_g> / (|cyc_f| |cyc_g|)  <=  A = N + eta.
  ```
  **HOLDS: 0 violations.** This is a SINGLE SCALAR inequality per bad edge — the provable target.

## Implication chain  (GERSH) => (ii) => (CV)   [all steps exact]
1. `O_c[f,g] = <p_f,p_g> >= 0` (inner product of nonnegative geodesic-count vectors), symmetric.
2. `Dm = D^{-1/2} O_c D^{-1/2}` is symmetric, **entrywise >= 0**, so `|Dm[f,g]| = Dm[f,g]`.
3. (GERSH) = `max_f sum_g Dm[f,g] <= A`.  Gershgorin: every eigenvalue `lam` of `Dm` lies in some disc
   `|lam - Dm[f,f]| <= sum_{g!=f} Dm[f,g]`, hence `lam <= Dm[f,f] + sum_{g!=f} Dm[f,g] = sum_g Dm[f,g] <= A`.
   So `rho(Dm) <= A`.
4. `A I - Dm` PSD (sym, all eigenvalues <= A).  Conjugate by `D^{1/2} = diag(|cyc_f|) >= 0`:
   `D^{1/2}(A I - Dm)D^{1/2} = A D - O_c` PSD.  = (ii).
5. Evaluate at `w`:  `w^T(A D - O_c)w >= 0`  =>  `w^T O_c w <= A w^T D w = A Gamma_c`. = (CV).  QED chain.

## Why the per-component route survives where the GLOBAL route died
Global `rho(O) <= N` is FALSE (two-lane L=12: rho(O)=40.2 > N=39).  Per-component compares the
Gershgorin row-max against `A = N + eta`, NOT against `N`.  On two-lane L=12: maxR=44 vs A=2396/25=95.84
(beta=4 tiny, eta=1421/25 dominates) — GERSH gap 1296/25.  The `+eta` slack is exactly the margin.

## Binding config / extremal constant
- (CV) and GERSH are simultaneously **tight at the balanced C5 blow-up C5[t]** (eta=0, one component,
  T==N): `R_f = N` for every f, so `max_f R_f = N = A`, Gershgorin gap = 0.  Extremal constant = N+eta,
  achieved with equality. Verified C5[1] (kf=1, R_f=5=N), C5[2] (maxR=10=A), C5[3] (maxR=15=A).
- Smallest positive GERSH gap on census = 24/25 (away from blow-ups). Standing-gate min gaps all > 0,
  incl Myc(Grotzsch) N=23 (maxcyc=65): gap 31393/4550 ≈ 6.9.

## Status / gap
- (CV) <= (ii) <= (GERSH) PROVEN (the chain above is exact algebra; Gershgorin + PSD conjugation).
- (GERSH) itself: exact-gated 0 violations on full battery, tight at C5[t]. NOT yet proven analytically.
  Combinatorial meaning: `R_f = (1/|cyc_f|) sum_{geodesics P of f} sum_{v in P} Tw(v)`,
  `Tw(v) = sum_{g in c} p_g(v)/|cyc_g|` (unit-weighted load).  GERSH = "the average Tw-length of f's
  shortest alternating geodesics is <= N+eta" — an odd-girth>=5 anti-concentration on the unit-weighted load.
```
