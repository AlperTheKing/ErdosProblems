# A1 General Proper-Mask: Uniform Reduction to SIX ConeCert Identities (GPT-Pro, 2026-07-03)

Thread: main 6a450f06. Statement: gamma-min max cut, tri-free, all-l5 C5-hom row Q,
x_i = s(q_i) - tau (tau = 5m/N), X(A) = sum_{i in A} x_i, etabar = (N^2-25m)/25:
  (A1)  X(A) <= (25/N + 2/3) etabar   for every nonempty proper mask A,
  with the STRONGER (25/N + 7/30) for |A| = 4 (feeds AM-5 five-mask absorption).

## 1. Row-atom compression
y_J (J nonempty subset of Z5) = fractional mass of shortest C5-rows meeting Q exactly in
pattern J; y_J >= 0; s(q_i) = sum_{J ni i} y_J; X(A) = sum_J |A cap J| y_J - 5|A|m/N.
Cleared numerator (beta = 2/3, x75N):
  D_A^{2/3} = (75+2N)(N^2-25m) - 75N sum_J |A cap J| y_J + 375|A|m
(4-mask, beta = 7/30, x750N):
  D_{M4}^{7/30} = (750+7N)(N^2-25m) - 750N sum_J |M4 cap J| y_J + 15000m
A1 <=> D_A^beta >= 0.

## 2. Six canonical masks (dihedral symmetry)
M1={0}, M2a={0,1}, M2b={0,2}, M3a={0,1,2}, M3b={0,1,3}, M4={0,1,2,3};
M4 gets the 7/30 target (implies its 2/3 version since 7/30 < 2/3, etabar >= 0).

## 3. PMTSCone(A)
Anchor h in A^c; cut the 5-cycle at h -> linear order h+1<h+2<h+3<h+4; I(A,h) = nonempty
intervals contained in A. S_{h,I} = PMTS_h(I) = completed proper-mask terminal shadow
(completion: B-connected closure, terminal prefix/suffix closure, noncrossing, twin,
anchor exclusion, protected-cell handoff). Generators of PMTSCone(A):
  sigma(h,I) >= 0  (max-cut switch values of the S_{h,I}),
  y_J >= 0         (row atoms),
  rho_term, rho_nc, rho_tw, rho_anchor, rho_prot >= 0 (completion residuals).
ConeCert identity (3.2), per mask:
  D_A^beta = P_A^+ + sum_{h,I} P_{h,I} sigma(h,I) + sum_r Q_r rho_r,
all multipliers coefficient-nonneg polynomials (N-parametric). GRAPH-UNIFORM: no N<=50.

## 4. Why 4-mask does NOT imply smaller masks
For A with complement C, b=|C|: sum_{c in C} X(Omega\{c}) = X(A) + (b-1)X(Omega) (4.1);
bounding X(A) from 4-masks needs a LOWER bound on X(Omega) - unavailable. Hence per-size
certificates.

## 6. ConeCert emission format (Codex)
Per canonical mask: {mask, beta (2/3 or 7/30 for M4), lhs = D_A^beta, terms: P_plus,
(coeff poly)*sigma(h,I), (coeff poly)*rho_...}; all coefficient lists explicit,
already-normalized for rfl checking (Lean blueprint format).

## 7-8. Assembly
By ConeCert identity + nonneg of all generators: D_A^beta >= 0 => A1 per canonical mask
=> (dihedral symmetry) A1 all proper masks. THEOREM (conditional): six verified ConeCert
identities => A1 uniform in N, all graphs, all proper masks.

## STATUS
- Theory: DONE (this reply). Certificates: Codex to emit/solve the six N-parametric LPs
  over PMTSCone generators (same machinery as CERT-2 LP: shifted-coefficient-nonneg).
- Consumers: C5-RS P-proper branch (2/3 version) + AM-5 five-mask absorption (7/30, M4).
- With A1 six-cone + CERT-2 + tau_0/V2 M-certs + S7 24 gates: Branch-A theory fully
  reduced to finite machine certificates.
