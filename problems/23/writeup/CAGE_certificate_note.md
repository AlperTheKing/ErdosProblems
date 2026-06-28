# CAGE Certificate Implication

This note records the exact statement checked by
`_codex_cage_exact.py`.  It is not a proof that CAGE certificates always
exist; it is the audited implication from a certificate to the Hellinger
Hall / LPD inequality.

Fix a connected-B max-cut configuration.  For every bad edge `f`, let
`P_f` be the set of shortest B-geodesics between the endpoints of `f`,
`L_f=ell(f)`, and

```text
p_{f,i}(v) = #{P in P_f : P[i]=v} / |P_f|.
```

For every gap `t` and B-edge `e`, let

```text
pi_{f,t,e} = #{P in P_f : {P[t],P[t+1]}=e} / |P_f|,
H_{f,t} = sum_{0<=i<=t<j<L_f} 1/(j-i).
```

A CAGE certificate consists of nonnegative variables

```text
alpha_{f,i,j,t,e} >= 0       (0 <= i <= t < j < L_f)
r_{f,t,e} > 0
```

satisfying

```text
(R1)  sum_{t=i}^{j-1} sum_{e in gap(f,t)}
      alpha_{f,i,j,t,e} = 1                         for each f,i<j,

(R2)  sum_{i<=t<j} alpha_{f,i,j,t,e}
      = H_{f,t} pi_{f,t,e}                          for each f,t,e.
```

Define the left and right vertex loads routed through gate `g=(f,t,e)`:

```text
A_g(v) = sum_{i<=t<j} alpha_{f,i,j,t,e} p_{f,i}(v),
B_g(v) = sum_{i<=t<j} alpha_{f,i,j,t,e} p_{f,j}(v).
```

The budget inequalities are

```text
sum_g ( r_g A_g(v) + r_g^{-1} B_g(v) ) <= N - S(v)
```

for every vertex `v`, where `S(v)=sum_f sum_i p_{f,i}(v)`.

## Lemma

If a CAGE certificate exists, then the CORR / Hellinger-Hall inequality
holds:

```text
sum_f sum_{0<=i<j<L_f} sqrt(w_{f,i} w_{f,j})
<= 1/2 sum_v (N-S(v)) y_v
```

for all nonnegative vertex weights `y`, where

```text
w_{f,i} = sum_v p_{f,i}(v) y_v.
```

## Proof

By (R1),

```text
sqrt(w_{f,i} w_{f,j})
= sum_{t,e} alpha_{f,i,j,t,e} sqrt(w_{f,i} w_{f,j}).
```

For each gate term, weighted AM-GM gives

```text
sqrt(w_{f,i} w_{f,j})
<= 1/2 ( r_g w_{f,i} + r_g^{-1} w_{f,j} ).
```

Summing over `f,i,j,t,e` and expanding
`w_{f,i}=sum_v p_{f,i}(v)y_v` gives

```text
LHS <= 1/2 sum_v y_v
       sum_g ( r_g A_g(v) + r_g^{-1} B_g(v) ).
```

The CAGE budget inequality bounds the inner sum by `N-S(v)`, proving
the displayed CORR inequality.

All equalities and inequalities in `_codex_cage_exact.py` are checked with
exact rational arithmetic after the floating solve has only supplied a
candidate certificate.
