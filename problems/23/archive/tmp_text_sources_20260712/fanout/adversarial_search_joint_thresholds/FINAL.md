Derived the exact joint-trade law, but the missing R29 constructor prevents deciding the actual 2,943-vertex global minimum.

For any simultaneous row trade \(\omega\to\omega'\),

\[
\operatorname{Score}(\omega)
=2C(\omega)+2\sum_D e(D),
\]

where \(C\) is total collision excess and \(D\) ranges over active off-support components. Hence

\[
\Delta\operatorname{Score}=2(G+E_+-E_-),
\]

with:

- \(G=C(\omega')-C(\omega)\), including collisions both created and destroyed;
- \(E_+\): active-edge weight activated or created;
- \(E_-\): active-edge weight deactivated or destroyed.

Thus a bulk trade improves exactly when

\[
G+E_+<E_-.
\]

Component splitting has no separate cost. If child component \(i\) has edge weight \(e_i\), surviving lock arms \(l_i\), and exact activity indicator \(A_i(l_i)\), its contribution is \(2A_i(l_i)e_i\).

For a vertex whose row multiplicity changes from \(r\) to \(r+d\), its exact diagonal collision change is

\[
(r+d-1)_+-(r-1)_+.
\]

Therefore joint multiplicities must be evaluated after the entire trade; summing Hamming-one penalties is generally invalid.

I also exactly tested the monotone selector surrogate

\[
S(k)=2dk+2B\,\mathbf1[L-qk>0],
\qquad k_0=\lceil L/q\rceil.
\]

When \(k_0\) is feasible:

- Every global minimizer is Hall-failing iff \(B<dk_0\).
- Both failing and repaired states minimize when \(B=dk_0\).
- The bulk repair strictly wins iff \(B>dk_0\).

Exact `Fraction` grid:

- Selector rows: 1–12
- Lock arms: 1–8
- Arms destroyed per changed row: 1–4
- Active-edge weight: 1–50
- Collision units per changed row: 0–6
- Parameter families: 134,400
- Threshold-law failures: 0

This surrogate exhibits both requested regimes, but it is not a graph-realizability certificate.

Proof gap: the workspace contains no labeled R29 graph, row database, selected tuple, or deterministic constructor. Consequently the true collision function, lock-arm survival predicates, component splits, and Hall status under bulk trades cannot be reconstructed. The claim that the 2,943-vertex state is or is not globally minimal remains ungated.

No files were modified: both mandated patch mechanisms failed inside the authorized directory. Existing input hashes:

- Onboarding: `e3012793accde4e8f8fa3ed3e514a794a7d006a07e4bdc23e4239d14c9d61ad0`
- R29 wall: `fff06d97f2e574fe2d66b9cea4f3bc4244037a92eb8ed5bd363eca73c8591b04`
- Exact-ILP report: `68bf94b4854ec40904c6341c62742622070377d901571e54fd23818578b653df`
- Component-split report: `117432f6a1c0e336a8919f89b0297bf6ee9b46f72b0dbcdc945675145e87a97`