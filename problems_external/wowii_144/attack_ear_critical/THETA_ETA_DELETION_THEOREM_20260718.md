# Eta-preserving deletion for the 2-connected cycle-rank-two case

Date: 2026-07-18.

## Theorem

For a finite connected graph `X`, write

```text
C(X)   = {vertices of minimum eccentricity},
eta(X) = max_x d_X(x,C(X)),
beta(X)= |E(X)|-|V(X)|+1.
```

**Theorem.** Let `G` be a finite simple 2-connected graph with
`beta(G)=2` and `girth(G)>=5`.  There is a vertex `v` such that `G-v` is
connected and unicyclic and

```text
eta(G-v) >= eta(G).
```

Thus the registered eta-nondecreasing deletion lemma is proved for the
first multicyclic case, cycle rank two.

## 1. Reduction to a theta graph

Since `G` is 2-connected, every vertex has degree at least two.  The degree
sum and `beta(G)=2` give

```text
sum_x (deg(x)-2) = 2|E|-2|V| = 2.
```

There cannot be one vertex of degree four and all other vertices of degree
two.  Indeed, deleting the degree-four vertex leaves a connected graph of
maximum degree two with four vertices of degree one, whereas a connected
graph of maximum degree two is a path or a cycle and has zero or two degree-one
vertices.  Hence `G` has exactly two degree-three vertices `A,B`, and every
other vertex has degree two.  Two-connectivity then decomposes `G` into three
internally vertex-disjoint `A`--`B` paths.  Write their lengths as

```text
1 <= a <= b <= c.
```

This is the theta graph `Theta(a,b,c)`.  Its girth is `a+b`, so the girth
hypothesis is exactly

```text
a+b >= 5.                                                    (1.1)
```

In particular `b>=3`.

## 2. Center depth of a theta graph

Let `P_a,P_b,P_c` be the three paths, and put

```text
s = floor((a+c)/2),    h = ceil(b/2).
```

We first prove

```text
rad(Theta(a,b,c)) = s,                                      (2.1)
eta(Theta(a,b,c)) <= h.                                     (2.2)
```

The cycle `P_a union P_c` is isometric: a route using `P_b` can be replaced
between `A` and `B` by `P_a`, which is no longer because `a<=b`.  Similarly
`P_a union P_b` is isometric because `c>=b>=a`.

The eccentricity of `A` is `s`.  Every vertex of `P_a union P_c` is at
cycle-distance at most `s` from `A`; every vertex of `P_b` is at distance at
most `floor((a+b)/2)<=s`; and the vertex of `P_c` at coordinate `s` from `A`
is at distance exactly `s`.  Hence the radius is at most `s`.

Every vertex on the isometric cycle `P_a union P_c` has eccentricity at
least `s`.  Now let `x` be internal to `P_b`, and put

```text
alpha=d(x,A),    beta=d(x,B).
```

For the vertex `y_j` at coordinate `j` on `P_c`, every `x`--`y_j` path first
enters `P_c` at `A` or `B`, and therefore

```text
d(x,y_j)=min(alpha+j, beta+c-j).                             (2.3)
```

The crossing of the two affine terms lies in `[0,c]`, because
`|alpha-beta|<=d(A,B)=a<=c`.  Maximizing (2.3) over integer `0<=j<=c` gives

```text
max_j d(x,y_j) = floor((alpha+beta+c)/2)
               >= floor((a+c)/2)=s,
```

where `alpha+beta>=d(A,B)=a`.  This proves the reverse radius inequality and
hence (2.1).

We next exhibit enough central vertices.  Number `P_c` from `A` to `B` as
`p_0,...,p_c`, and set

```text
L = floor((c-b)/2).
```

For every `0<=i<=L`, a vertex of `P_b` at coordinate `q` is at distance at
most

```text
min(i+q, a+i+b-q)
  = i + min(q,a+b-q)
  <= L + floor((a+b)/2)
  <= floor((a+c)/2)=s.                                     (2.4)
```

Every vertex of the isometric cycle `P_a union P_c` is also within `s` of
`p_i`.  Thus (2.1) and (2.4) show that

```text
p_0,...,p_L are central.
```

Reflection in `A,B` shows that `p_{c-L},...,p_c` are central as well.  A
vertex on `P_a` or `P_b` is within `floor(b/2)` of the central set `{A,B}`.
The remaining interval of `P_c` has length

```text
c-2L in {b,b+1},
```

so each of its vertices is within `ceil(b/2)` of one of the two central end
bands.  This proves (2.2).

We need one sharper small case.  If `b=3`, then (1.1) gives `a>=2`, and

```text
eta(Theta(a,3,c)) <= 1.                                    (2.5)
```

When `c-3` is even, the middle interval above has length three, so (2.5)
already follows.  When `c-3` is odd, `c` is even and the interval has length
four.  Its midpoint `p_{c/2}` is central: vertices of `P_a union P_c` are
within `s`, while a vertex of `P_3` is at distance at most

```text
c/2+1 <= c/2+floor(a/2)=floor((a+c)/2)=s.
```

The midpoint divides the length-four interval into two intervals of length
two, proving (2.5).

## 3. Exact center depth of a cycle with one tail

Let `T(l,t)` be a cycle of length `l` with a path of length `t` attached at
one cycle vertex `z`, and put `s=floor(l/2)`.  Then

```text
eta(T(l,t)) = t                         if t<=s,
eta(T(l,t)) = floor((s+t)/2)            if t>s.              (3.1)
```

To prove (3.1), a cycle vertex at cycle-distance `q` from `z` has
eccentricity `max(s,t+q)`.  A tail vertex at depth `k` has eccentricity

```text
max(s+k,t-k).                                             (3.2)
```

If `t<=s`, the radius is `s` and the center consists of the cycle vertices
at cycle-distance at most `s-t` from `z`; the tail leaf and the antipodal
cycle vertices are at distance `t` from this center.  Thus `eta=t`.

If `t>s`, minimizing (3.2) gives radius `r=ceil((s+t)/2)` and center depths

```text
t-r <= k <= r-s.
```

Both the tail leaf and an antipodal cycle vertex are at distance
`s+t-r=floor((s+t)/2)` from this center, and every vertex is within that
distance.  This proves (3.1).

## 4. The deletion

Write the middle path as

```text
A=v_0,v_1,...,v_b=B
```

and delete `v=v_1`.  The remaining graph is precisely

```text
H = T(a+c,b-2):
```

the cycle `P_a union P_c`, with the surviving segment of `P_b` as a tail of
length `b-2` at `B`.  It is connected and unicyclic.

If `b=3`, then `s=floor((a+c)/2)>=2`, so (3.1) gives `eta(H)=1`; this is at
least `eta(G)` by (2.5).

Assume `b>=4` and put `t=b-2`.  If `t<=s`, then

```text
eta(H)=b-2 >= ceil(b/2) >= eta(G).
```

If `t>s`, formula (3.1) applies.  For even `b`, `s>=2` gives

```text
eta(H)=floor((s+b-2)/2) >= b/2.
```

For odd `b>=5`, the inequalities `c>=b` and `a>=1` give `s>=3`, and hence

```text
eta(H)=floor((s+b-2)/2) >= (b+1)/2.
```

In every case `eta(H)>=ceil(b/2)>=eta(G)`, completing the proof.  QED.

## 5. Independent exact verification

`verify_theta_deletion_theorem.py` independently constructs every parameter
triple

```text
1<=a<=b<=c<=30,    a+b>=5,
```

recomputes all-pairs distances, the full center sets, both eta values, the
central bands used above, and formula (3.1).  It checked 4,844 theta graphs,
found minimum deletion change zero, 110 equality cases, and no failure.  The
machine-readable result is `theta_deletion_verification.json`.  This finite
check is verification of the displayed formulas, not a substitute for the
proof above.
