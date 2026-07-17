# C36: exact pattern-orbit compression from an affine relation

## Statement

Let `Omega_k` be the set of words over `{2,3,5}` with letter counts

```text
(#2,#3,#5) = (15k,10k,6k),
```

let `M_k=|Omega_k|`, and let `D_k` be the number of distinct affine maps
represented by these words under

```text
L_2(t)=2t,       L_3(t)=3t+1,       L_5(t)=5t+3.
```

Then, for every integer `k>=2`,

```text
D_k/M_k <= (1 - 28000/31^6)^floor(k/2).
```

In particular `D_k/M_k` decays exponentially.

This does **not** falsify the actual R-D mass gate

```text
D_k >= c Q^k/sqrt(k),       Q=2^15 3^10 5^6.
```

Indeed `M_k/Q^k` grows like `(31/30)^(31k)/k`, while the explicit orbit
compression proved here is much weaker than that exponential surplus.

## Equal-map relation

Put

```text
U = 552223,       V = 232552.
```

Both words have count vector `(3,1,2)`. Direct affine composition gives

```text
L_U(t)=600t+218=L_V(t).
```

Consequently one may replace an occurrence of `U` by `V`, or conversely,
inside any word without changing either its letter counts or its affine map.

## Fixed-block action

Set `B=floor(k/2)` and partition the first `6B` positions into `B` fixed
blocks of length six. For `w in Omega_k`, let `r(w)` be the number of these
blocks equal to `U` or `V`.

On each fixed block define an involution that exchanges `U` and `V` and
fixes every other six-letter block. The `B` involutions commute. The orbit of
`w` has exactly `2^r(w)` elements, and every member of the orbit represents
the same affine map. Therefore

```text
D_k <= number of orbits
    = sum_{w in Omega_k} 2^(-r(w)).                         (1)
```

## Uniform conditional block probability

Choose `W` uniformly from `Omega_k` and expose the fixed blocks from left to
right. Before any one of the first `B` blocks is exposed, fewer than `3k`
letters have been removed. If the remaining counts of `2,3,5` are `a,b,c`
and the remaining word length is `R`, then

```text
a >= 12k,       b >= 7k,       c >= 3k,       R <= 31k.
```

Conditioned on the complete past, the next six-letter block is uniform
sampling without replacement. Since `U` and `V` are distinct and have the
same count vector,

```text
Pr(block is U or V | past)
  = 2 (a)_3 b (c)_2 / (R)_6
  >= 2 (10k)^3 (7k) (2k)^2 / (31k)^6
  = 56000/31^6
  =: p_0.                                                  (2)
```

Here `(x)_j=x(x-1)...(x-j+1)`. The displayed lower bounds use
`(a)_3 >= (10k)^3` and `(c)_2 >= (2k)^2`, valid for `k>=2`.

Let `I_j` indicate that fixed block `j` is `U` or `V`, and let `F_{j-1}` be
the previously exposed blocks. Equation (2) gives

```text
E[2^(-I_j) | F_{j-1}]
  = 1 - Pr(I_j=1 | F_{j-1})/2
  <= 1-p_0/2.
```

Iterated conditional expectation now yields

```text
E[2^(-r(W))] <= (1-p_0/2)^B.                              (3)
```

Dividing (1) by `M_k` and using (3) proves the theorem.

## Consequence for the R-D route

The C29 killed-chain local-limit estimate was intended to prove the mass gate
by bounding every affine fiber. C35 already gives a special fiber of size
`8^k`. The fixed-block orbit argument above is stronger in a different sense:
the same local relation compresses the whole fixed-composition word set by an
exponential factor. But its explicit exponent is too small to overcome the
word-count surplus over `Q^k`. Therefore it kills neither the canonical mass
gate nor the weaker asymmetric R-D route. It is an exact collision theorem
and a warning that any successful proof of (M) must work at the slope scale,
not the raw word-count scale.

This does not address the independent grounded-hole route F3 or the
hyperbola-pair route F1.

