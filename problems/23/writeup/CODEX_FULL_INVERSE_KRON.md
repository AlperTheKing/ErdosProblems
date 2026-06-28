# Full-Inverse / Kron Pivot

Status: **retired as a universal route**.  This note records the pivot after
the large non-uniform `C7` blow-up refuted the overloaded-vertex diagonal
surrogate, and the subsequent correction: the canonical full-inverse
superharmonic certificate is also non-universal.  The live target is again
the original bad-edge `ROWSUM-O / SPEC` inequality.

## Verified Surrogate Counterexample

Script:

```text
problems/23/writeup/_gptpro_c7_check.py
```

Instance:

```text
C7 parts = (3,423,173,7,176,7,423)
N = 1212
bad edge class = V2-V3
```

Exact result:

```text
ROWSUM margin = -3540476630161/3271659686685
STAR-K-multi min eigenvalue = same margin
full-inverse cond3 margin = +39947678772/63012307
```

So every proof route replacing `A_QQ^{-1}` by the diagonal bound
`diag(R_q+s_q)^{-1}` is false.

## Former Correct Object

Use the full Schur/Kron row deficit:

```text
r_o^Kron = N - T(o) + K[o,Q] A_QQ^{-1} (N-T)_Q,
A_QQ = (N I - K)_QQ.
```

Eliminating a single `q in Q` performs the positive Kron update:

```text
K^+_{uv} = K_{uv} + K_{uq}K_{qv}/(N-K_{qq}),
r^+_u = r_u + K_{uq}r_q/(N-K_{qq}).
```

Any induction has to work in this positive Kron closure, not in the
original geodesic-incidence kernel class alone.

This statement remains algebraically correct for that certificate, but the
certificate itself is not universal.

## Caution: Cond3 Is Not Universal On Slack Graphs

The diagnostic

```text
problems/23/writeup/_codex_odd_blowup_full_inverse.py
```

found odd-cycle blow-ups where the canonical full-inverse row condition
with `O={T>N}` fails even though `rho(K)<=N`.  Example:

```text
C7 parts = (5,715,303,12,304,12,715)
N = 2066
bad edge class = V0-V1 or V6-V0
O parts = (0,3,5)
canonical full-inverse min row = -21420273538/187212247
rho(K) = 123834625/92112 < N
Gamma = 49*3575 << N^2
```

This does not threaten the conjecture because `rho(K)<N`; it shows that the
canonical `phi=1` on all overloaded vertices is a sufficient certificate,
not a universal route to `SPEC`.

Therefore future diagnostics must state their frontier hypothesis
explicitly.  For odd-cycle blow-ups with one bad edge class,

```text
Gamma = m^2 * min_i n_i n_{i+1} <= (sum_i n_i)^2 = N^2
```

by averaging adjacent products, with equality only in the uniform case.
The large non-uniform `C7` examples are useful for killing surrogate
certificates, but they are not themselves counterexample candidates.

## Restored Target

The live route is the original bad-edge Gram row-sum:

```text
ROWSUM-O:  (O 1)_f = sum_g <p_f,p_g> <= N  for every bad edge f.
```

For odd-cycle blow-ups this is now proved in
`CODEX_ODD_BLOWUP_ROWSUM.md`.  The diagonal overloaded-row surrogate fails
on the GPT-Pro `C7` example, but the actual bad-edge row has large positive
margin:

```text
SPEC row margin = +32960131/74448.
```
