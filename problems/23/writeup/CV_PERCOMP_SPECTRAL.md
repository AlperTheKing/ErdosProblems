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

## 2026-07-01 Codex strengthening: rowwise GERSH

The average in GERSH appears unnecessary.  For each K-component `C`, define
the unit component load

```text
Tw_C(v) = sum_{g in M_C} #{Q in cyc[g] : v in Q} / |cyc[g]|.
```

The stronger exact-test target is:

```text
ROWWISE-GERSH:
for every bad edge f in M_C and every shortest row Q in cyc[f],
    sum_{v in Q} Tw_C(v) <= A = N + N^2/25 - |M|.
```

This implies GERSH by averaging over `Q in cyc[f]`, then the existing exact
algebra gives:

```text
ROWWISE-GERSH => GERSH => (N+eta)D-O_c PSD => CV.
```

Local exact gate:

```text
python problems/23/writeup/_codex_gersh_rowwise_gate.py \
  --fast --stop-first --min-n 7 --max-n 10 --two-lane-max 20 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
individual rows checked = 89469
rowwise violations = 0
min row margin = 0 at C5[1]
```

Census-11 pass:

```text
python problems/23/writeup/_codex_gersh_rowwise_gate.py \
  --fast --min-n 11 --max-n 11 --two-lane-max 0 --blowup-t 0 --blowup-nmax 0
```

Result:

```text
individual rows checked = 1059380
edge averages checked = 278504
rowwise violations = 0
min row margin = 21/25
```

Two-lane / named stress:

```text
python problems/23/writeup/_codex_gersh_rowwise_gate.py \
  --fast --min-n 7 --max-n 6 --two-lane-max 100 --blowup-t 5 --blowup-nmax 26
```

Result:

```text
individual rows checked = 15507
edge averages checked = 439
rowwise violations = 0
min row margin = 0 at C5[1]
```

Proof interpretation: every individual shortest corridor has unit K-load at
most the global first-moment capacity `A`, not merely its average over the
bad-edge geodesic bundle.  This is currently the cleanest corridor-capacity
form of the component CV route.

Length-split diagnostic from the fast battery:

```text
length 5:  min margin 0       at C5[1]
length 7:  min margin 24/25   at C7[1]
length 9:  min margin 56/25   at C9[1]
length 11: min margin 914/25  at two-lane-L10
length 13: min margin 1296/25 at two-lane-L12
...
```

For pure odd cycles `C_L[1]`, the row value is `L`, `|M|=1`, and

```text
A-row = (L + L^2/25 - 1) - L = L^2/25 - 1.
```

So only length `5` can be equality-tight in the pure-cycle family.  The
nontrivial near-extremal proof should therefore concentrate on length-5
pentagonal row caps; longer rows carry a built-in odd-cycle surplus.

## 2026-07-01 Codex split: NON5-HALF plus pentagonal PMS

The rowwise target can be split by row length.

Let

```text
eta = N^2/25 - |M|,
A = N + eta.
```

Exact diagnostics show that the only rows using more than half of the deficit
budget are length-5 pentagonal rows.  The stronger long-row split is:

```text
LONG-SURPLUS:
if |Q| > 5, then
    sum_{v in Q} Tw_C(v) <= N + eta/2 - (|Q|^2-25)/50.
```

For length-5 rows, the older OC-PMS target gives exactly the complementary
coefficient:

```text
PMS-5:
if |Q| = 5, then
    sum_{v in Q} Tw_C(v) - N <= (2/3) eta.
```

Since both `1/2` and `2/3` are at most `1`, these two lemmas imply
ROWWISE-GERSH.

Exact gate:

```text
python problems/23/writeup/_codex_rowcap_non5_half_gate.py \
  --fast --min-n 7 --max-n 11 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
L>5 rows checked = 19832
NON5-HALF violations = 0
LONG-SURPLUS violations = 0
min margin = 12/25 at C7[1]
min LONG-SURPLUS margin = 0 at C7[1]
```

The by-length minima begin:

```text
length 7:  12/25 at C7[1]
length 9:  28/25 at C9[1]
length 11: 48/25 at an N=11 single C11 row
```

This matches the pure odd-cycle surplus

```text
N + eta/2 - rowvalue = L^2/50 - 1/2
```

when `C` is a single odd cycle of length `L`.

Equivalently, `LONG-SURPLUS` is tight on pure odd cycles:

```text
N + eta/2 - rowvalue - (L^2-25)/50 = 0.
```

Direct stress on explicit known-cut families, avoiding expensive `gmins` calls:

```text
python problems/23/writeup/_codex_rowcap_non5_half_direct_stress.py
```

Result:

```text
L>5 rows checked = 127540
NON5-HALF violations = 0
LONG-SURPLUS violations = 0
min NON5-HALF margin = 12/25 at direct-C7[1]
min LONG-SURPLUS margin = 0 at direct-C7[1]
LONG-SURPLUS equality at pure C7[1], C9[1], C11[1], C13[1]
two-lane checked through L=100
```

Two related diagnostics:

```text
python problems/23/writeup/_codex_rowcap_overload_classify.py \
  --fast --min-n 7 --max-n 11 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
rows checked = 1148058
rows with rowvalue > N = 131
max (rowvalue-N)/eta = 2/3 at the N=10 PMS equality atom I?BD@g]Qo
census N=11 adds 0 over-N rows
```

The crude scalar domination

```text
sum_{g in C} min(|Q|, ell(g)) <= A
```

is false away from length 5:

```text
python problems/23/writeup/_codex_rowcap_coarse_budget_gate.py \
  --fast --min-n 7 --max-n 10 --two-lane-max 30 \
  --blowup-t 4 --blowup-nmax 26
```

Result:

```text
non-5 violations = 5654
first violation = C7[2]
minimum margin = -834/25 at C7[3]
```

Thus non-5 rows still need geodesic anti-concentration; the proof cannot use
only the trivial overlap bound `|Q cap P| <= min(|Q|,|P|)`.
