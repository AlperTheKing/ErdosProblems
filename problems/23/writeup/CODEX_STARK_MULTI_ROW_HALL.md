# STAR-K-multi row-Hall diagnostics

Status: **support row-Hall and truncated-mass are false proof routes**.
Codex's first tests started at `N=11`, where they passed. Claude's
small-`|M|` adversarial gate found an `N=9` counterexample. ROWSUM itself
remains valid there; the failure is only in replacing the true `N`
budget by support-only capacity.

## Setup

Use the pure-K objects

```text
K = sum_f p_f p_f^T,
T = K*1,
N = |V|.
```

Let

```text
O = {v : T(v)>N},
Q = V\O,
R_q = N-T(q),
s_q = sum_{o in O} K[o,q].
```

For a fixed overloaded row `o in O`, define

```text
psi_o(q) = K[o,q] / (R_q+s_q).
```

For each bad edge `f`, define

```text
X_f = sum_{o' in O} p_f(o')
c_f(o) = X_f * ( p_f(o) + sum_{q in Q} psi_o(q) p_f(q) ).
```

## False candidate row-Hall lemma

For every `o in O` and every subset `F'` of bad edges,

```text
sum_{f in F'} c_f(o) <= | union_{f in F'} supp(p_f) |.
```

This is exact-testable as a Fraction max-flow from bad-edge demands
`c_f(o)` to unit-capacity support vertices.

Diagnostic:

```text
problems/23/writeup/_codex_stark_row_hall.py
```

It is false. Exact witness:

```text
script: problems/23/writeup/_rowhall_debug.py
g6=H?AFBo], side=000111100, N=9,
O={6,7,8}, T(6)=T(7)=T(8)=10,
M={(1,7),(2,7)}, ell=5 for both,
row o=6, H=M,
sum_{f in H} c_f(o)=54/7,
|union supp(p_f)|=7.
```

The actual ROWSUM full-set budget is still satisfied:

```text
54/7 <= N=9.
```

The missing capacity is exactly the geodesically idle vertices outside
the support union. Thus support-Hall is over-strong.

## False stronger truncated-mass target

For a subset `H` of bad edges, define

```text
A_H(v) = sum_{f in H} X_f p_f(v).
```

Then the row-Hall demand for row `o` is

```text
D_o(H) = sum_{f in H} c_f(o)
       = A_H(o) + sum_{q in Q} psi_o(q) A_H(q).
```

Candidate stronger inequality:

```text
D_o(H) <= sum_v min(1, A_H(v)).
```

This would imply row-Hall because `A_H` is supported on
`union_{f in H} supp(p_f)`, so

```text
sum_v min(1,A_H(v)) <= | union_{f in H} supp(p_f) |.
```

Diagnostic:

```text
problems/23/writeup/_codex_stark_row_truncmass.py
```

Local exact result:

```text
N=11 connected triangle-free census, workers=61:
row/subset configs=71525, fails=0.

Myc2(C5), exact subset enumeration:
row/subset configs=131070, fails=0.
```

This also fails on the same `N=9` witness, so it is not a valid proof
route for ROWSUM. The surviving useful fragment is the `Q`-side
collective inequality `Q-CAP` recorded below.

## Why it implies STAR-K-multi

Taking `F'` to be all bad edges gives

```text
sum_f c_f(o) <= N.
```

But

```text
sum_f X_f p_f(o) = sum_{o' in O} K[o,o'],
sum_f X_f p_f(q) = s_q.
```

So the full-set inequality is

```text
sum_{o' in O} K[o,o'] + sum_{q in Q} K[o,q] s_q/(R_q+s_q) <= N.
```

Equivalently,

```text
sum_{q in Q} K[o,q] R_q/(R_q+s_q) >= T(o)-N.
```

These are exactly the nonnegative row sums of Claude's matrix

```text
Z = N I_O - K_OO - sum_{q in Q} k_q k_q^T/(R_q+s_q),
```

where `k_q=(K[o,q])_{o in O}`.

Since `Z` has nonpositive off-diagonal entries, nonnegative row sums make
`Z` symmetric diagonally dominant, hence PSD. Therefore:

```text
row-Hall => row sums of Z >= 0 => Z PSD => STAR-K-multi => cond3.
```

## Earlier N=11 evidence that missed the N=9 obstruction

```text
_codex_stark_row_hall.py:
N=11 connected triangle-free census, workers=61:
configs=10323, fails=0.
```

Named multi-overload checks:

```text
Myc2(C5): rows=2, fails=0.
J???E?pNu?[2]: rows=464, fails=0.
I?BD@g]Qo[2]: rows=800, fails=0.
```

These checks are retained only as landscape diagnostics. They do not make
support row-Hall a valid target, because the `N=9` witness above fails.

Claude Step-2 independent gate:

```text
2026-06-28T14:08:00Z:
ROW-SUM exact 0-fail on full gate:
  census N=9/10/11,
  Myc N=23,
  overloaded blowups with |O| up to 8,
  glued battery,
  31 non-uniform C5 |O|>=2.
No ROWSUM-fail-but-STARK-multi-ok cases.
```

So the live proof target is:

```text
ROWSUM => STAR-K-multi by Z-matrix diagonal dominance => cond3.
```

The support row-Hall and truncated-mass lemmas below are therefore
negative/landscape data, not proof mechanisms for ROWSUM.

## Bottleneck census

Diagnostic:

```text
problems/23/writeup/_codex_stark_row_hall_masks.py
```

N=11 connected triangle-free census, 61 workers:

```text
configs=10323
worst subset sizes:
  singleton: 4688
  pair:      2402
  triple:      10
  full:      3223
```

For the false support-Hall certificate, the N=11 bottlenecks include
rare triple cases.

Focused dump:

```text
problems/23/writeup/_codex_stark_row_hall_triples.py
```

After filtering out cases where `|M|=3` and the triple is just the full
set, the N=11 census has exactly:

```text
non-full triple hits = 10.
```

Every non-full triple hit has:

```text
|M| = 4,
worst subset size = 3,
union size = 10.
```

The examples are represented by two graph6 families:

```text
J?BD?{]uFo?       O={0,10}, two row choices.
J?`Db_{N?]?       O={10}, eight gamma-min sides.
```

Thus the rare triple obstruction seen at N=11 is specifically a
`3-of-4 bad edges` bottleneck, not a general large-family Hall
phenomenon. This remains useful only as a diagnostic of why the
over-strong support-Hall certificate looked plausible at N=11.

Restricted-family exact comparison:

```text
problems/23/writeup/_codex_stark_row_hall_family.py
```

This compares the true minimum Hall slack over all nonempty bad-edge
subsets with the minimum over only:

```text
singletons,
pairs,
the full set,
3-of-4 subsets when |M|=4.
```

N=11 connected triangle-free census, 61 workers:

```text
configs=10323
restricted_family_fail=0
best_size_hist={'full': 3223, 2: 2402, 1: 4688, 3: 10}
```

Thus, at least through N=11, this restricted family attains the exact
minimum of the false support-Hall certificate. The `N=9` witness shows
that this restricted-family route does not prove ROWSUM.

## Dead strengthening: direct split allocation

The algebraic split

```text
c_f(o)=sum_{u in O} p_f(o)p_f(u)
       +sum_{q in Q} X_f psi_o(q)p_f(q)
```

does not itself give a feasible allocation by sending each summand to
its displayed vertex. It overfills overloaded vertices.

First small census failure:

```text
graph6 = H?AAF_}
side   = 111110000
max split-load = 2
```

Thus the proof needs real redistribution across supports, not just the
formal expansion.

## Dead strengthening: Q-only capacity

It is false that the row-Hall demand can always be routed using only
vertices in `Q={T<=N}`.

Diagnostic:

```text
problems/23/writeup/_codex_stark_row_hall_qonly.py
```

First N=11 failure:

```text
graph6 = J???E?pNu\?
side   = 00111111000
row o  = 7
O      = {7,9,10}
bad subset = [(0,10),(1,10)]
Q-only slack = -521/237
```

Thus the valid row-Hall certificate genuinely spends capacity on
overloaded support vertices as well; it is not a pure `Q`-side transport.

## Truncated-mass split diagnostics

The stronger truncated-mass inequality can be written as

```text
A_H(o) + sum_{q in Q} psi_o(q) A_H(q)
<=
sum_{v in O} min(1,A_H(v)) + sum_{q in Q} min(1,A_H(q)).
```

Codex split diagnostic:

```text
problems/23/writeup/_codex_truncmass_split_tests.py
```

N=11 connected triangle-free census, 61 workers:

```text
configs=71515
Q_fail=0
O_fail=37260
```

So the `Q` side appears to satisfy the standalone collective inequality

```text
sum_{q in Q} psi_o(q) A_H(q) <= sum_{q in Q} min(1,A_H(q)),
```

while the overloaded-side split

```text
A_H(o) <= sum_{v in O} min(1,A_H(v))
```

is very false. First O-split failure:

```text
g6=J???CBoBz{?, side=11111110000, o=8, subset edges=(7,9),(8,9),
O={8,9,10}, lhs=6, rhs=3.
```

The obvious pointwise Q strengthening is also false:

```text
psi_o(q) * s_q <= 1
```

fails 6612 times on the N=11 census. First failure:

```text
g6=J???E?pNu\?, side=11000000110, o=9, q=7,
s_q=18/5, R_q=2, K[o,q]=9/5,
psi_o(q)*s_q=81/70>1.
```

Thus the live Q-side sublemma, if true, is genuinely collective:

```text
Q-CAP(H,o):
sum_{q in Q} psi_o(q) A_H(q) <= sum_{q in Q} min(1,A_H(q)).
```

It does not by itself prove ROWSUM, but it cleanly separates the `Q`
contribution from the remaining overloaded-capacity compensation.

Q-CAP bottleneck diagnostic:

```text
problems/23/writeup/_codex_qcap_masks.py
```

N=11 connected triangle-free census, 61 workers:

```text
configs=10323
fails=0
best subset histogram:
  singleton: 10239
  pair:          6
  full:         78
```

So Q-CAP is much simpler than the full row-Hall family on this gate:
there are no triple bottlenecks, and almost every minimum is a singleton.

## Dead full-set capped-support simplification

For the full bad-edge set `H=M`, write

```text
s_v = A_M(v) = sum_{o' in O} K[o',v].
```

A tempting simplification of ROWSUM would be:

```text
s_o + sum_{q in Q} min(1,s_q) <= N.
```

This would combine the row's overloaded coupling with raw capped Q
support, avoiding the `psi` denominator. It is false.

N=11 connected triangle-free census:

```text
configs=10323
fails=5642
```

First failure:

```text
g6=J???CBoBz{?, side=11111110000, o=8,
s_o=6, sum_Q min(1,s_q)=8, total=14>N=11.
```

Thus the denominator-weighted Q response in ROWSUM is load-bearing; raw
capped Q support is far too weak.
