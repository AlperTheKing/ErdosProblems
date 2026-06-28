# P5-DEFICIT target for the singleton-overload Schur row

Status: candidate lemma, exact-tested by Codex and Claude Step-2; proof
still open.

## Setup

Use the pure-K objects

```text
K = sum_f p_f p_f^T,
T = K*1,
N = |V|.
```

Assume a gamma-min connected-B maximum cut has singleton overload
`O={o}`. For `q != o`, write

```text
D   = T(o)-N,
a_q = K[o,q],
R_q = N-T(q).
```

## Candidate lemma

```text
P5-DEFICIT:
sum_{q != o, a_q>0, R_q>0} a_q R_q / (N - 4 a_q) >= D.
```

This is exact-testable from `K,T,o`.

## Why P5 implies STAR-K1

Let

```text
h_q = T(q)-a_q = sum_f (ell(f)-p_f(o)) p_f(q).
```

Since `ell(f)>=5` and `0<=p_f(o)<=1`,

```text
ell(f)-p_f(o) >= 4 p_f(o).
```

Therefore `h_q >= 4a_q`. Also

```text
a_q + R_q = a_q + N - T(q) = N - h_q <= N - 4a_q.
```

Thus

```text
a_q R_q/(a_q+R_q) >= a_q R_q/(N-4a_q),
```

so P5 implies

```text
STAR-K1:
sum_q a_q R_q/(a_q+R_q) >= D.
```

STAR-K1 is a diagonal Schur sufficient condition for the singleton pure-K
row because

```text
A_QQ = N I - K_QQ = L_{K[Q]} + diag(R_q+a_q) >= diag(R_q+a_q).
```

## Equivalent weighted-potential form

Define

```text
psi(o)=1,
psi(q)=a_q/(N-4a_q).
```

Then P5 is equivalent to

```text
sum_v psi(v) (T(v)-N) <= 0.
```

This is the form likely suited to a switching/coarea proof.

Using the identity `N psi(q)=a_q(1+4psi(q))`, this is also equivalent
to the per-bad-edge packing inequality

```text
sum_f [ x_f^2 + sum_{q != o} psi(q) (ell(f)-4x_f) p_f(q) ] <= N,
```

where `x_f=p_f(o)`. Equivalently, for a random shortest `B`-geodesic
for `f`, the contribution of `f` is

```text
E[ x_f 1_{o in P} + (ell(f)-4x_f) sum_{q in P\\{o}} psi(q) ].
```

This form keeps the sharp `ell>=5` mechanism visible and may be the
right switching/vertex-capacity target.

## Support-Hall strengthening candidate

For each bad edge `f`, define

```text
c_f = x_f^2 + sum_{q != o} psi(q) (ell(f)-4x_f) p_f(q).
```

Then P5 is implied by the full-set case of the stronger Hall-type
condition

```text
sum_{f in F'} c_f <= | union_{f in F'} supp(p_f) |
```

for every subset `F'` of bad edges. This is exact-testable from the
`p_f` supports and the pure-K singleton potential.

Codex diagnostic:

```text
problems/23/writeup/_codex_p5_support_hall.py
N=11 connected triangle-free census:
configs=5683, skips=0, fails=0, worst=1219/4233 at J?`Db_{N?]? side 00001111000.
```

Exact max-flow diagnostic:

```text
problems/23/writeup/_codex_p5_hall_flow.py
```

This checks the same support-Hall condition as a Fraction max-flow from
bad-edge demands to unit-capacity support vertices, so it avoids `2^|M|`
subset enumeration. It verified the nonuniform C5 blow-up family cases
that were too large for brute-force subset enumeration, including
`(1,48,6,8,48)` with 48 bad edges and `(1,64,16,7,64)` with 64 bad
edges.

For a C5 blow-up with part sizes `(1,b,c,d,e)` and the cut omitting the
edge `V4--V0`, every bad edge has the same demand

```text
c = 1 + psi(V1) + psi(V2) + psi(V3) + psi(V4_endpoint),
```

and any subset of `k` bad edges has support-union size

```text
1 + b + c + d + k.
```

Thus support-Hall for this family reduces to the full-set case (P5);
there is no hidden intermediate subset obstruction in the sharp C5
family.

## Local evidence

Script:

```text
problems/23/writeup/_codex_stark1_p5_parallel.py
```

Results:

```text
N=11 connected triangle-free census:
graphs=90842, singleton cuts=5683, fails=0, minratio=11096/9877.
```

Other local checks: named Myc/Grotzsch cases, nonuniform C5
`(1,48,6,8,48)`, configured lifted blowups, and census `N=7..10` all had
zero failures.

Claude Step-2 independent gate:

```text
2026-06-28T12:40:00Z:
P5-DEFICIT, STAR-K1, and STAR-K1-6/5 exact-verified 0-fail.
census N=9/10/11: |O|=1 cuts 170/76/5683, P5-FAIL=0.
Mycielskians: 12 |O|=1 cuts, 0 fails.
glued battery: 292 |O|=1 cuts, 0 fails.
C5(1,m,m/2,2,m): P5/D = STAR-K1/D, decreasing to 6/5.
```

This makes P5 the current singleton-overload proof target.

## Coarea form and switch guardrail

The exact threshold identity for P5 uses superlevel sets, not sublevel
sets. With

```text
psi(o)=1,
psi(q)=a_q/(N-4a_q),
U_t={o} union {q: psi(q) >= t}, 0<t<1,
```

P5 is exactly

```text
integral_0^1 [N|U_t|-T(U_t)] dt >= 0.
```

Equivalently, if the distinct positive `psi` values are

```text
1=r_0 > r_1 > ... > r_m > r_{m+1}=0,
U_i={o} union {q: psi(q) >= r_i},
```

then

```text
sum_i (r_i-r_{i+1}) [N|U_i|-T(U_i)] >= 0.
```

The sublevel family `{o} union {q: psi(q)<t}` gives the wrong
complement and should not be used as a proof object.

Pointwise nonnegative switching is also false. Exact guardrail:

```text
problems/23/writeup/_codex_p5_coarea_guardrail.py
```

For the C5 blow-up `(1,4,2,2,4)` with the cut omitting `V4--V0`, the
top superlevel set is `U={o}` and

```text
N|U|-T(U)=-7.
```

At the same set, the natural switch terms all vanish:

```text
cut-defect = 0,
gamma switch change = 0,
cycle-transition surplus for each bad edge = 0.
```

The cumulative coarea sum is nevertheless positive:

```text
coarea_total = P5_total = 221/45.
```

Thus any successful switching proof for P5 must be cumulative along the
whole superlevel chain, explaining cancellation between the negative
top interval and the lower intervals where high-`psi` deficit vertices
enter. It cannot prove pointwise nonnegativity of the threshold
integrand from cut-defect, gamma-tightness, or shortest-cycle surplus.

## Omega-local reductions are dead

The nonuniform C5 blow-up `(1,48,6,8,48)` also proves that the omega
network is not an equivalent replacement for the pure-K inverse.

Exact script:

```text
problems/23/writeup/_codex_nonuniform_c5_star.py
```

It verifies:

```text
LB1(o)-(T(o)-N) = -2133/9877 < 0,
omega_Ceff(o to grounded Q)-(T(o)-N)
  = -15533526475119/78611364292436 < 0,
pureK O-row margin = 5217/95 > 0.
```

So both the one-hop omega star bound and the full omega effective
conductance bound fail on a valid gamma-min connected-B maximum cut.
The surviving certificate is genuinely the pure-K inverse response;
the compensation from the internal geodesic layers cannot be compressed
to an omega conductance-to-ground statement.

## Dead stronger variants

Pointwise dominance

```text
D a_q <= (N-K[o,o]-s) R_q
```

after removing saturated coupling `s=sum_{R_q=0}a_q` is false.
First Codex witness:

```text
J??CE@a}?z?, side 01111111000.
```

Aggregate Jensen/moment dominance

```text
D * sum_{R_q>0} a_q^2/R_q <= (N-K[o,o]-s) * sum_{R_q>0} a_q
```

is false. First Codex witness:

```text
J??ED?]Fvw?, side 00011111000.
```

The linear sufficient shortcut

```text
sum_q a_q R_q >= N D
```

is false, so the rational denominator in P5 is essential. First Codex
witness:

```text
J?BEF_m}@{?, side 00111111000.
lhs=4333/200, rhs=55/2.
```

So P5 should not be replaced by these stronger Cauchy shortcuts.
