# GCD cond3, `|O|=1`: Star-Capacity Target

Status 2026-06-28. This note isolates a concrete sublemma for the remaining
Schur/open-capacity condition.

## Retraction: STAR-O1 Is False

The one-hop omega star sufficient condition below is false outside the small
finite gate.  Exact quotient checker:

```text
python problems/23/writeup/_codex_nonuniform_c5_star.py
```

Counterexample: non-uniform blow-up of `C5` with part sizes

```text
(1,48,6,8,48)
```

and the gamma-min maximum cut whose only bad quotient edge is `V4--V0`.
The unique overloaded vertex is the singleton part `V0`, with

```text
N = 111
T(o) = 240
T(o)-N = 129
a_bar(5) = 125/92
LB1(o) = 1272000/9877
LB1(o) - (T(o)-N) = -2133/9877 < 0.
```

The pure-K full inverse still survives on the same quotient:

```text
g = (94/95, 87/95, 89/95, 94/95)
N - T(o) + K[o,Q] g = 5217/95 > 0.
```

So the `|O|=1` proof must use the full pure-K inverse/Schur response, not the
one-hop omega star lower bound.

## Replacement Candidate: Pure-K One-Hop Star

The same Rayleigh deletion idea is still meaningful in the correct network.
For

```text
A = N I - K = L_K + diag(N-T),
```

the singleton-O Schur condition is effective conductance from `o` to ground
in the `K`-network with ground conductances `R(q)=N-T(q)`.

Define

```text
a_q := K[o,q],        R_q := N-T(q),        D := T(o)-N.
```

The pure-K one-hop star condition is:

```text
STAR-K1:
sum_{q in Q: a_q>0, R_q>0} a_q R_q / (a_q + R_q) >= D.
```

Equivalently,

```text
sum_q a_q^2 / (a_q + R_q) <= N - K[o,o],
```

because `sum_q a_q = T(o)-K[o,o] = N+D-K[o,o]`.

This is exactly the diagonal Schur sufficient condition obtained from

```text
A_QQ = L_{K[Q]} + diag(R_q + a_q) >= diag(R_q + a_q).
```

So

```text
K[o,Q] A_QQ^{-1} K[Q,o]
<= sum_q a_q^2/(a_q+R_q).
```

Exact test script:

```text
python problems/23/writeup/_codex_stark1.py
```

Current local evidence:

```text
Grotzsch N=11: pass, min ratio 3.0839
Myc(C7) N=15: pass, min ratio 1.6555
nonuniform C5(1,48,6,8,48) N=111: pass, ratio 1.4181
lifted blowups J???E?pNu?[2], I?BD@g]Qo[2], G?bF`w[3]: no |O|=1 cuts
census N=7..10: 0 fails, min ratio 1.6083 at I?ABCc]}?
```

This candidate is still only a sufficient `|O|=1` sublemma, not a proof of
general cond3.  It is currently waiting for Claude's independent full gate.

## Dead Appendix: Omega STAR-O1

The former omega-network one-hop condition was:

```text
sum_{w: omega(ow)>0, T(w)<N}
  omega(ow) (N-T(w)) / (omega(ow)+N-T(w))
>= T(o)-N.
```

It passed the small census but is false on the non-uniform `C5` blow-up above.
Do not use it as a proof target.
