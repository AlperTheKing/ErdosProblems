# C06: prime-frontier canonical factor partition

## Verdict

No positive-density theorem is proved.  There is, however, a collision-free
full-set mechanism which is genuinely outside every bounded multiplier
alphabet.

For a generated cofactor `q`, let `ell(q)` be its least generated divisor.
Pairs `(p,q)` in which `p` is an ordinary prime in `G` and

```
Y < p < q,             p <= ell(q)
```

map injectively to `pq-1 in G`.  Moreover, none of these outputs belongs to
the subsystem using all generated multipliers at most `Y`.  Thus a uniform
lower bound of `cX` for these pairs would prove positive lower density by a
scale-recursive mechanism that necessarily uses new multipliers.

The exact census through `2,000,000` does not falsify the natural moving
frontier `Y=floor(X^(1/3))`: its contribution on the four tested intervals is
between `0.002333` and `0.007638` of the interval length.  This is finite data,
not an asymptotic lower bound.

There is also an exact obstruction to extending the decoder from prime to
arbitrary divisibility-minimal generated multipliers:

```
77 * 437 = 161 * 209 = 33649.
```

All four factors are in `G` and none has a proper divisor in `G`.  Composite
primitive factors can therefore collide by splitting and recombining their
ordinary prime factors.  A broader canonical-factor proof must control these
cross-split rectangles; checking only the least generated divisor of each
cofactor is invalid.

## 1. Exact setup

Use the exact recurrence, for `n >= 4`,

```
n in G  iff  n+1=dq for some distinct d<q with d,q in G.       (1)
```

For `q in G`, define

```
ell(q) = min {e in G : e divides q}.                            (2)
```

The set in (2) is nonempty because it contains `q`.  Its least element has
no proper divisor in `G`; otherwise that divisor would be a smaller member
of the set.

For `Y >= 2`, let `D_Y=G intersect [2,Y]`, and let `S_Y` be the least set
containing `D_Y` and closed under

```
r -> d*r-1,       d in D_Y, d != r.                            (3)
```

Thus `S_Y subset G` is the fixed-multiplier subsystem with every multiplier
known through `Y`.  It is introduced only as the baseline which the moving
prime frontier escapes; no density claim about `S_Y` is used.

## 2. Prime-frontier lemma

For `X>Y>=2`, set

```
F(X,Y) = {(p,q):
  p is an ordinary prime, p in G,
  Y < p < q, q in G, p <= ell(q), and p*q <= X+1}.
```

**Lemma.**  The map

```
Phi : F(X,Y) -> G intersect [1,X],       Phi(p,q)=p*q-1          (4)
```

is injective, and its image is disjoint from `S_Y`.  Consequently

```
|G intersect [1,X] \ S_Y| >= |F(X,Y)|.                          (5)
```

In particular, if some function `Y(X) -> infinity` and constants `c>0,X0`
satisfy

```
|F(X,Y(X))| >= cX        for every X>=X0,                        (6)
```

then `G` has lower density at least `c`.

**Proof.**  For `(p,q) in F(X,Y)`, the operands are distinct members of `G`,
so (1) gives `pq-1 in G`; the size bound is immediate.

Suppose `pq=p'q'` for two pairs and, without loss of generality, `p<p'`.
The distinct ordinary primes `p,p'` are coprime, so `p` divides `q'`.  Since
`p in G`, (2) gives `ell(q')<=p<p'`, contradicting `p'<=ell(q')`.  Hence
`p=p'` and then `q=q'`, proving injectivity.

Finally suppose `pq-1 in S_Y`.  It exceeds `Y`, so it is not a seed in
`D_Y`; the last step of a finite derivation in (3) writes

```
pq-1=d*r-1
```

with `d in D_Y`.  Thus `d` divides `pq`.  Since `d<=Y<p` and `p` is prime,
`gcd(d,p)=1`, whence `d` divides `q`.  But then
`ell(q)<=d<p`, contrary to `p<=ell(q)`.  This proves disjointness and (5).
Condition (6) now gives the asserted lower-density bound.  QED.

The point of `p<=ell(q)` is exact decoding.  It says that `p` is the least
generated divisor of `pq`, so a product cannot migrate to an earlier prime
branch.  Unlike a finite affine subsystem, (6) explicitly asks for a
frontier `Y(X)` tending to infinity.

## 3. Exact moving-scale test

The accepted ascending divisor generator
`problems/424/compute/wave1/A06/divisor_generator.py` was run with
`B=2,000,000`.  Its SHA-256 was

```
f3795de6e20b111a336f4924101b0ea0c76da4cae13f2dcd80451cbb55af40f5
```

and the resulting membership bytearray (indices `0` through `B`) had
SHA-256

```
0e1628bfdc0952265f6a4d9cc0bfd446dd4fc033486ef25076ac72054551f669
```

For each generated `n`, the generator's witness is the first valid smaller
divisor of `n+1`.  Independently, multiples of every generated
`d<=sqrt(B+1)` were marked in increasing `d` order.  Therefore `n` is in the
image of (4), with `p` in a requested range, exactly when

1. the first valid witness `p` equals the marked least generated divisor of
   `n+1`;
2. `p` is an ordinary prime; and
3. `p` is above the requested frontier.

Integer arithmetic, including an integer cube root, gave:

| output interval `(L,U]` | `Y=floor(cuberoot(U))` | prime-frontier outputs with `p>Y` | fraction of `U-L` |
|---:|---:|---:|---:|
| `(1,000,10,000]` | 21 | 21 | 0.002333333333 |
| `(10,000,100,000]` | 46 | 349 | 0.003877777778 |
| `(100,000,1,000,000]` | 100 | 5,632 | 0.006257777778 |
| `(1,000,000,2,000,000]` | 125 | 7,638 | 0.007638000000 |

As an independent check of the lemma rather than its witness criterion, at
`X=100,000` and `Y=100` all pairs in `F(X,Y)` were enumerated directly, and
`S_Y` was built by the ascending recurrence (3).  Here `|D_Y|=23`; the run
found `240` pairs, `240` distinct outputs, all `240` in `G`, zero in `S_Y`,
and exact set equality with the canonical-witness test above.

At the last interval there are `484,195` members of `G`.  The full
least-generated-divisor decoder retains `384,499`; prime branches retain
`381,371`.  Of the latter, `18,913`, `8,487`, and `497` use respectively
`p>5`, `p>100`, and `p>1000`.  These counts show that the certificate is not
merely relabelling the branches `2,3,5`.  They do not prove (6), even along
the tested choice `Y(X)=floor(X^(1/3))`.

## 4. Composite-primitive falsifier

Call `a in G` divisibility-minimal if no proper divisor of `a` belongs to
`G`.  The following four values have explicit derivations:

```
5=2*3-1          9=2*5-1          26=3*9-1       77=3*26-1
14=3*5-1         41=3*14-1        81=2*41-1      161=2*81-1
27=2*14-1        53=2*27-1        105=2*53-1     209=2*105-1
44=5*9-1         219=5*44-1       437=2*219-1
```

Their ordinary factorizations are

```
77=7*11,       161=7*23,       209=11*19,       437=19*23.       (7)
```

The exact recurrence (1) excludes `7,11,19,23`:

- `7+1=8` has only the candidate `(2,4)`, and `4` is absent;
- `11+1=12` has `(2,6),(3,4)`, and `4,6` are absent;
- `19+1=20` has `(2,10),(4,5)`, and `4,10` are absent;
- `23+1=24` has `(2,12),(3,8),(4,6)`, and `4,6,8,12` are absent.

Here `4+1` and `6+1` are prime, `8+1=3^2` has only the forbidden equal
pair, and `10+1` and `12+1` are prime.  Hence each proper nontrivial divisor
in (7) is outside `G`, proving that all four values are divisibility-minimal.

Nevertheless,

```
77*437 = (7*11)*(19*23)
       = (7*23)*(11*19)
       = 161*209
       = 33649.                                                   (8)
```

Thus both distinct pairs generate `33648`.  The least generated divisor of
`33649` is `77`; the tempting `161` branch must be rejected even though
`ell(209)=209>=161` and neither `77 | 161` nor `77 | 209`.  The earlier
generated divisor `77` is assembled across the two proposed factors.

This exactly falsifies both statements

```
products of distinct divisibility-minimal elements of G are unique;
ell(q)>=d is sufficient for a composite minimal multiplier d.
```

The prime hypothesis in the lemma is what prevents cross-splitting: every
smaller divisor is coprime to `p` and must divide `q` in its entirety.

## 5. Sharp remaining obstruction

The sufficient frontier is now explicit.  A positive-density proof in this
lane needs a uniform lower bound for generated primes `p` in moving ranges,
weighted by generated cofactors `q` having no generated divisor below `p`:

```
sum over generated primes Y(X)<p<=sqrt(X+1)
  #{q in G : p<q<=(X+1)/p and ell(q)>=p}  >= cX.                  (9)
```

No current accepted growth theorem controls either factor in (9): the known
power-law construction need not produce primes, while a cardinality bound
for `G` does not control the `G`-rough condition `ell(q)>=p`.  Allowing
composite minimal multipliers enlarges (9), but (8) shows that it introduces
cross-split collision states not visible from `ell(q)` alone.  This is the
precise obstruction left by the canonical-factor mechanism.
