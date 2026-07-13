# P87: incidence corners and the punctured-center frontier

## Verdict

This note does **not** prove `T_F=o(p^3)`.  It gives an exact
incidence-geometric normal form for the loose triangles of P82 and isolates
the phase-sensitive configuration which remains to be bounded.

Every loose fold triangle is a three-direction additive grid around one
integer center `K` which is not in `B`.  Two of its arms are the unique Sidon
secants representing `K-a` and `K-c`; the third is the unique Sidon chord
representing `K+u`.  The literal hole forces a correlated six-point phase
stencil around the grid to miss `B`.  In particular, if
`C_S >= epsilon p^2`, then one of eight strict sign chambers contains
`Omega_epsilon(p^3)` such punctured grids.

The resulting exact center-degree bound still permits order `p^3`.  Merely
knowing that `K` and its endpoint reflection miss `B` deletes only `O(p)`
possible centers from an interval of length `O(p^2)`.  Thus the remaining
nontrivial assertion must use the correlation among the three Sidon arms and
the full six-point phase stencil, not just the absence of the center.

## 1. Loose triangles

Retain the hypotheses and notation of P82.  Thus

\[
 B\subseteq[0,h-1],\qquad |B|=p,\qquad \max B=h-1,
 \qquad b\in\{1,2\},                                  \tag{1}
\]

`B` is integer Sidon (diagonal sums included), and

\[
 \Delta^+(B)\cap(B+B+b)=\varnothing.                  \tag{2}
\]

A loose triangle consists of three distinct folds

\[
\begin{array}{rcl}
 a+c+h&=&r+s,\\
 a+z+h&=&u+w,\\
 x+c+h&=&u+y,                                         \tag{3}
\end{array}
\]

with the P82 role orders

\[
 a\le c<r\le s,\qquad a\le z<u\le w,
 \qquad x\le c<u\le y.                               \tag{4}
\]

The corresponding hyperedges are `(a,c,r)`, `(a,z,u)`, and
`(x,c,u)`.  They meet pairwise at the three labelled vertices `a_A`, `c_C`,
and `u_U`.

## 2. Punctured-center normal form

Define

\[
 K=a+c+h-u,\qquad X=x-a,\qquad Z=z-c,
 \qquad R=r-u.                                        \tag{5}
\]

### Lemma P87.1 (exact additive-grid form)

Every loose triangle (3) has

\[
\begin{array}{lll}
 x=a+X,&z=c+Z,&r=u+R,\\
 y=K+X,&w=K+Z,&s=K-R,                                \tag{6}
\end{array}
\]

where

\[
 K+u=a+c+h,qquad K>c,qquad K\notin B,
 \qquad XZR\ne0.                                    \tag{7}
\]

In particular,

\[
 K-a=y-x\in\Delta^+(B),\qquad
 K-c=w-z\in\Delta^+(B),\qquad K+u=r+s.              \tag{8}
\]

The two difference representations and the sum representation in (8) are
unique.

Conversely, suppose (5)--(7) hold, all nine entries displayed in (6) and
`a,c,u` belong to `B`, and

\[
\begin{split}
 &a\le c<u,\\
 &x\le c<u\le y,\qquad a\le z<u\le w,
 \qquad c<r\le s.                                    \tag{9}
\end{split}
\]

Then the three quadruples in (3) are distinct folds and form a loose
triangle.

### Proof

Substitution of (5) into (3) gives (6).  The strict inequalities
`y>x` and `w>z` from (4) give

\[
 K-a=y-x>0,\qquad K-c=w-z>0,                          \tag{10}
\]

so `K>c`.  Sidonicity makes both positive-difference representations in
(8) unique, and it makes the unordered representation of `K+u` unique.

If `X=0`, then `x=a`; the first and third folds have the same low pair
`(a,c)`, so Sidonicity gives `r=u` and the two folds coincide.  If `Z=0`,
the second and third folds have the same `(c,u)` projection, and if `R=0`,
the first and third have that projection.  P82.1 makes the folds coincide in
either case.  Hence `X`, `Z`, and `R` are nonzero.

Suppose `K` were in `B`.  The equality `K+x=a+y` and Sidonicity would give
`{K,x}={a,y}`.  Since `x<y`, this forces either `x=a`, contrary to `X!=0`,
or `x=y`, again impossible.  Thus `K` is not in `B`.

For the converse, (6), (7), and (9) give

\[
 (u+R)+(K-R)=a+c+h,
\]

\[
 u+(K+Z)=a+(c+Z)+h,
 \qquad u+(K+X)=(a+X)+c+h.
\]

These are exactly (3) with the required orders.  The nonzero conditions on
`X`, `Z`, and `R` make the three labelled hyperedges distinct and make each
pairwise intersection exactly the prescribed one.  QED.

The geometry in (8) is a punctured three-arm star: the absent point `K` is
joined to `a` and `c` by two differences represented inside `B`, while the
third arm is the chord `r+s=K+u`.  The base relation `K+u=a+c+h` couples the
three arms to the endpoint shift.

## 3. The endpoint phase stencil

Put

\[
 \tau=h-b-K=u-a-c-b,
 \qquad \lambda=h-b-u.                               \tag{11}
\]

### Lemma P87.2 (six forced holes)

For every loose triangle satisfying the literal hole (2),

\[
 \boxed{
 \{\tau,\ \tau-X,\ \tau-Z,\ \tau+R,
       \ \lambda,\ \lambda-R\}\cap B=\varnothing .}
                                                               \tag{12}
\]

In particular, both the grid center and its endpoint reflection miss `B`:

\[
 K\notin B,qquad h-b-K=\tau\notin B.                 \tag{13}
\]

### Proof

The definitions and (6) give the six exact identities

\[
\begin{array}{rcl}
 u&=&a+c+\tau+b,\\
 u&=&x+c+(\tau-X)+b,\\
 u&=&a+z+(\tau-Z)+b,\\
 r&=&a+c+(\tau+R)+b,\\
 w&=&a+z+\lambda+b,\\
 s&=&a+c+(\lambda-R)+b.                              \tag{14}
\end{array}
\]

Every displayed left side and every other summand on the right belongs to
`B`.  If any parenthesized phase value belonged to `B`, (14) would be a
literal solution of `q_1+q_2+q_3+b=q_4`, contradicting (2).  Repeated
summands are allowed, so this also covers diagonal cases.  QED.

The six values in (12) need not be distinct and some can lie outside
`[0,h-1]`.  The assertion is their literal exclusion from `B`, not a claim
that they are six distinct holes of the ambient interval.

## 4. Incidence count and exact remaining estimate

For an integer `K`, define its Sidon-secant degree

\[
 d_K=|\{q\in B:K-q\in\Delta^+(B)\}|.                 \tag{15}
\]

### Lemma P87.3 (center-degree bound)

For every endpoint-normalized Sidon set satisfying (2),

\[
 T_F(B,h)\le
 \sum_{K=1}^{2h-2}
 \mathbf 1_{K\notin B}\,\mathbf 1_{h-b-K\notin B}
 \min\left\{p,{d_K+1\choose2}\right\}.              \tag{16}
\]

### Proof

By P87.1, a corner of center `K` has `a,c` in the set counted by `d_K`.
There are at most `binom(d_K+1,2)` choices with `a<=c`.  Once `K,a,c` are
fixed,

\[
 u=a+c+h-K                                             \tag{17}
\]

is fixed.  The two secants `(x,y)` and `(z,w)` are then fixed by difference
uniqueness, and `(r,s)` is fixed by sum uniqueness.  Thus each choice gives
at most one corner.

Alternatively, for fixed `K` and `u`, the sum

\[
 a+c=K+u-h                                             \tag{18}
\]

has at most one unordered representation, so there are at most `p` corners
at that center.  P87.1 and P87.2 give the two indicators.  Finally,
`K>c>=0`, while `u>c` gives
`K=a+c+h-u<=a+h-1<=2h-2`.  QED.

The first moment of these degrees is already cubic:

\[
 \sum_K d_K=p|\Delta^+(B)|={p^2(p-1)\over2}.          \tag{19}
\]

Indeed, each pair `(q,d)` in `B x Delta^+(B)` contributes once at
`K=q+d`.  Positive defect only gives `h=O(p^2)`.  Also the two center
indicators in (16) exclude at most `2p` integer values of `K`.  Consequently
(16), its first moment, and center exclusion alone are compatible with
`Theta(p^3)` corners.

The exact incidence frontier is therefore to prove

\[
 \sum_{K=1}^{2h-2} N_K=o(p^3),                        \tag{20}
\]

where `N_K` counts the pairs `a<=c` in the secant set (15) for which (17)
lies in `B`, the three unique arms satisfy (9), and the correlated stencil
(12) is absent.  The degree data (15)--(19) and the two center exclusions
alone permit order `p^3`; a proof of (20) must retain additional correlation
among the simultaneous arm and stencil conditions.

## 5. Asymptotic chamber reduction

Since `X`, `Z`, and `R` are nonzero, every punctured grid belongs to one of
the eight sign chambers

\[
 (\operatorname{sgn}X,\operatorname{sgn}Z,
   \operatorname{sgn}R)\in\{-,+\}^3.                 \tag{21}
\]

### Corollary P87.4 (one dense ordered grid chamber)

For every `epsilon>0`, there are `eta=eta(epsilon)>0` and `p_0` such that,
if `p>=p_0` and

\[
 C_S(B,h)\ge\varepsilon p^2,                          \tag{22}
\]

then one of the eight chambers in (21) contains at least

\[
 {\eta(\varepsilon)\over8}p^3                        \tag{23}

\]

punctured-center configurations satisfying (6)--(14).

### Proof

P82.2 gives at least `eta(epsilon)p^3` loose triangles.  P87.1 and P87.2
put each one in exactly one of the eight chambers, so (23) follows by the
pigeonhole principle.  Along any countersequence, an infinite subsequence
has the same chamber.  QED.

Thus an incidence proof does not need to handle arbitrary uncoloured
three-sum collisions.  It must rule out positive cubic density of one
specific ordered object: three unique Sidon arms around `K`, the endpoint
relation `K+u=a+c+h`, and the six simultaneous phase exclusions (12).

## 6. Exact P75 audit

The following integer-only audit reconstructs the 51 folds and all 25 loose
triangles of P75, and verifies P87.1--P87.2 on each one.

```python
from collections import Counter

B = [
    3, 5, 69, 169, 211, 223, 251, 329, 373, 403, 409,
    501, 505, 519, 631, 639, 689, 715, 775, 863, 883,
    915, 931, 953, 977, 987,
]
h, b = 988, 1

pairs = {
    q + r: (q, r)
    for i, q in enumerate(B) for r in B[i:]
}
assert len(pairs) == len(B) * (len(B) + 1) // 2
assert not any(
    q + r + t + b == v
    for q in B for r in B for t in B for v in B
)
folds = []
for t, (a, c) in pairs.items():
    if t + h in pairs:
        folds.append((a, c, *pairs[t + h]))

AC = {(a, c): (r, s) for a, c, r, s in folds}
AU = {(a, u): (z, w) for a, z, u, w in folds}
CU = {(c, u): (x, y) for x, c, u, y in folds}
assert len(AC) == len(AU) == len(CU) == len(folds)

chambers = Counter()
triangles = 0
for (a, c), (r, s) in AC.items():
    for u in B:
        if (a, u) not in AU or (c, u) not in CU or u == r:
            continue
        z, w = AU[a, u]
        x, y = CU[c, u]
        K = a + c + h - u
        X, Z, R = x - a, z - c, r - u
        tau, lam = h - b - K, h - b - u

        assert (x, z, r, y, w, s) == (
            a + X, c + Z, u + R, K + X, K + Z, K - R
        )
        assert X != 0 and Z != 0 and R != 0
        assert K > c and K not in B
        assert all(q not in B for q in (
            tau, tau - X, tau - Z, tau + R, lam, lam - R
        ))

        chamber = ''.join(
            '+' if q > 0 else '-' for q in (X, Z, R)
        )
        chambers[chamber] += 1
        triangles += 1

assert len(folds) == 51
assert triangles == 25
print(dict(sorted(chambers.items())))
```

It prints

```text
{'+++': 2, '++-': 11, '+--': 4, '-+-': 2, '--+': 5, '---': 1}
```

Thus neither punctured grids nor any of the six displayed sign chambers can
be forbidden pointwise.  The P75 data also show that phase values can be
negative, so replacing (12) by a count of six ambient holes would be false.

## 7. Claim boundary and prior art

The proved statements are the exact normal form P87.1, the phase stencil
P87.2, the center-degree bound P87.3, and the chamber reduction P87.4.  They
do not prove (20), `T_F=o(p^3)`, or `C_S=o(p^2)`.

General loose-triangle and linear-hypergraph theorems treat the unphased
hypergraph configuration; examples include Nie--Spiro--Verstraete,
[*Triangle-free Subgraphs of Hypergraphs*](https://arxiv.org/abs/2004.10992),
and Timmons,
[*On r-uniform linear hypergraphs with no Berge-K_{2,t}*](https://arxiv.org/abs/1609.03401).
Those results do not include the integer center relation or the stencil
(12), and therefore do not supply (20).  Searches of the Sidon/incidence and
linear-hypergraph literature did not locate a theorem for this punctured,
endpoint-phased three-arm configuration.
