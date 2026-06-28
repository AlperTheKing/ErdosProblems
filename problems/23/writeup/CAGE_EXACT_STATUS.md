# CAGE Exact Status

This file summarizes the current exact-rational evidence for the CAGE
certificate class.  It is evidence for a proof route, not a proof of
universal existence.

## Fixed-Configuration Implication

The implication

```text
CAGE certificate => CORR / Hellinger-Hall / LPD for that configuration
```

is recorded in `CAGE_certificate_note.md`.  The checker
`_codex_cage_exact.py` verifies the certificate inequalities with exact
`Fraction` arithmetic after a floating solve has only supplied a candidate.

## Named Cases

The following hard cases have exact rational CAGE certificates:

```text
I?BD@g]Qo[1]
I?ABCc]}?[1]
J???E?pNu?[2]
J?AEB?oE?W?[2]
H?bB@_W[2]
I?rFf_{N?[2]
```

In particular, the N=22 witness `J???E?pNu?[2]` certifies with exact
positive slack.

## Census Batches

Exact repair has been run on census slices:

```text
N=8:  total=85,   ok=85,   fail=0
N=9:  total=650,  ok=650,  fail=0
N=10: total=5800, ok=5800, fail=0
N=11: first 100 load-bearing cases, ok=100, fail=0
```

Logs:

```text
problems/23/writeup/cage_exact_n9_full.log
problems/23/writeup/cage_exact_n10_full.log
problems/23/writeup/cage_exact_n11_first100.log
```

The first ten N=8 certificates were also saved as JSON proof objects and
one was reload-checked:

```text
python problems/23/writeup/_codex_cage_exact.py \
  --g6 'G?AFbw' \
  --load-cert problems/23/writeup/cage_certs_n8_first10/G_AFbw_1_.cage.json
```

## Alpha0 Diagnostic

Uniform CAGE routing `alpha0` is not enough in general.  It succeeds on the
standard equality blow-ups and the first N=8 slice, but fails on strict hard
cases:

```text
I?BD@g]Qo[1]:       alpha0_ratio = 1.027634728
J???E?pNu?[2]:      alpha0_ratio = 1.144055985
```

The adaptive alpha step is therefore mathematically load-bearing.

## KKT-Core Diagnostic

The diagnostic `_codex_cage_kkt.py` inspects the LP dual of the adaptive
routing step at the optimized gate ratios.  It is not an exact checker, but
it helps identify the obstruction a proof of CAGE existence must exclude.
The proof-oriented dual object is recorded in `CAGE_dual_obstruction.md`.

For `I?BD@g]Qo[1]`, the alpha LP has seven active budget vertices and three
large-slack vertices.  For `J???E?pNu?[2]`, it has eleven positive dual
vertices among twenty-two vertices.  This supports the current proof target:
exclude a finite KKT core / corridor-allocation obstruction rather than seek
a uniform routing rule.

## Equality-Characterization Target

Parsing the exact CAGE logs for all load-bearing census cases with
`N=8,9,10` gives:

```text
rows = 6535
zero-slack exact certificates = 2
zero-slack non-extremal certificates = 0
positive-slack extremal certificates = 0
```

The two zero-slack certificates are exactly the `Gamma=N^2` equality cases
`H?bB@_W[1]` and `I?rFf_{N?[1]`.  Every non-extremal case in these exact
logs has positive slack; the smallest non-extremal exact slack occurs at
`I?BD@g]Qo[1]`.

This suggests a possible proof strategy: show universal CAGE feasibility and
characterize the tight KKT system as the odd-cycle blow-up extremal.  This is
still a conjectural proof hook, not a theorem.

## Total-Surplus Identity

The exact algebraic identity in `CAGE_surplus_identity.md` has been recorded
and checked against all saved JSON certificates:

```text
13/13 saved exact certificates matched.
```

For any CAGE certificate `(alpha,r)`,

```text
total vertex slack
= N^2 - Gamma - sum_g m_g (r_g + r_g^{-1} - 2).
```

In particular, equality cases `Gamma=N^2` force every positive-mass gate
ratio to be `r_g=1` and force all vertex budgets tight.  Thus any strict
case obstruction must be distributional rather than a shortage of total
capacity.

## Negative Structural Diagnostic

A test of whether optimized gate log-ratios are per-bad-edge vertex-potential
differences failed on named hard cases.  Least-squares residuals for
`log r_g = phi(tail)-phi(head)` reached:

```text
I?BD@g]Qo[1]:       max residual about 0.305
I?ABCc]}?[1]:       max residual about 0.287
J???E?pNu?[2]:      max residual about 1.132
```

So the ratio freedom is genuinely gate-local; a proof should not assume a
hidden potential/gradient representation of the CAGE ratios.

## Fixed-Ratio Farkas/Hall Form

The exact fixed-ratio obstruction is now recorded in
`CAGE_farkas_hall.md`.  For fixed positive gate ratios `r_g`, CAGE
feasibility is equivalent to:

```text
sum_f OT_f(lambda,r) <= sum_v lambda_v (N-S(v))
```

for every nonnegative vertex weight `lambda`, where `OT_f` is the
transportation problem sending each layer pair `i<j` to the gate marginals
`m_g=H_{f,t}pi_{f,t,e}` with cost

```text
r_g <lambda,p_{f,i}> + r_g^{-1}<lambda,p_{f,j}>.
```

The floating diagnostic `_codex_cage_farkas.py` confirms the identity
`sum_f OT_f(lambda,r)=eta(r)` at the alpha-LP dual on hard named cases.  The
N=22 witness has a small active lambda support and a symmetric bad-edge OT
decomposition, suggesting that the universal proof should attack this
weighted transport Hall family directly.

On the two equality cases checked (`H?bB@_W[1]` and `I?rFf_{N?[1]`), the
diagnostic returns `eta=1` with singleton dual support.  This confirms the
dual degeneracy warning: equality should be characterized through primal
budget/ratio tightness, not through uniqueness or shape of the dual lambda.

## Y-Dependent Variant

The weaker y-dependent CAGE form is recorded in `CAGE_y_dependent.md`.  For
a fixed `y` and a fixed routing alpha, the optimal gate ratios give the
conic cost

```text
sum_g 2 sqrt((A_g.y)(B_g.y)).
```

Uniform routing `alpha0` still fails this weaker test on hard cases:

```text
I?BD@g]Qo[1]:       alpha0 y-gap = +0.027634728
J???E?pNu?[2]:      alpha0 y-gap = +0.144055985
```

The adaptive alpha from the fixed CAGE solver passes the same diagnostics.
Thus the proof cannot be reduced to choosing y-dependent gate ratios for the
uniform harmonic routing; adaptive interval-pair transport is mathematically
load-bearing.

## Remaining Mathematical Gap

The current evidence supports the following route:

```text
prove every connected-B triangle-free max-cut configuration admits
a CAGE certificate.
```

Once existence is proved, the AM-GM implication gives CORR/LPD, hence the
one remaining scalar inequality.  The present files provide exact finite
certificates and a verifier, but not the universal existence proof.
