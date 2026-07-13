# P82: subquadratic folds and the loose-triangle frontier

## Verdict

The requested terminal dichotomy is **not closed** here.  I do not have a
proof that `C_S=o(p^2)`, and I do not have an infinite admissible family with
`C_S=Omega(p^2)`.

There is, however, a rigorous uniform reduction to one concrete asymptotic
configuration count.  Every endpoint fold gives an edge of a linear
3-partite 3-graph.  The triangle-removal lemma then shows that a positive
quadratic density of folds forces a positive cubic density of loose triangles
in that 3-graph.  Thus the remaining removal-theoretic frontier is not a fixed
biclique exclusion: it is to prove that the literal hole makes this particular
six-vertex configuration count `o(p^3)`.

The P75 admissible ruler already has such loose triangles.  Consequently they
cannot simply be declared forbidden; their **density** or their phase must be
controlled.  This also prevents the argument below from being misreported as
a proof of the desired little-oh estimate.

## 1. Uniform formulation

For an integer `p>=1`, let `A_p` be the class of triples `(B,h,b)` satisfying

\[
 B\subseteq\{0,\ldots,h-1\},\qquad |B|=p,\qquad \max B=h-1,
 \qquad b\in\{1,2\},                                      \tag{1}
\]

such that all diagonal-inclusive unordered sums from `B` are distinct,

\[
 \delta(B,h):={3p^2-p+2\over2}-h>0,                       \tag{2}
\]

and the full literal hole holds:

\[
 \Delta^+(B)\cap(B+B+b)=\varnothing .                    \tag{3}
\]

Put

\[
 C_S(B,h)=|\{s\in B+B:s+h\in B+B\}|.                    \tag{4}
\]

The desired assertion, with its quantifiers made explicit, is

\[
 \boxed{\quad
 \forall\varepsilon>0\ \exists p_0\ \forall p\ge p_0\
 \forall(B,h,b)\in A_p:\quad C_S(B,h)\le\varepsilon p^2.
 \quad}                                                   \tag{5}
\]

Neither a rate nor a bound with an absolute linear right side is part of (5).
P75 and P80 rule out the latter interpretation.

Every fold has a unique presentation

\[
 a+c+h=u+v,\qquad a\le c<u\le v.                         \tag{6}
\]

Indeed, if `u<=c`, then `v-a=h+c-u>=h`, contrary to (1).
This ordering, and not a forbidden `K_{r,r}`, is the only geometric input in
the reduction below.

## 2. The linear fold hypergraph

Make three disjoint labelled copies `B_A,B_C,B_U` of `B`.  To the fold (6)
associate

\[
             e(a,c,u)=\{a_A,c_C,u_U\}.                   \tag{7}
\]

Let `H_F` be the resulting 3-partite 3-graph.

### Lemma P82.1 (linearity)

Any two distinct edges of `H_F` meet in at most one vertex.

### Proof

The pair `(a,c)` fixes the low sum and hence, by integer Sidonicity, its
unique high pair `(u,v)`.  The pair `(c,u)` fixes the positive difference
`u-c`; its complement `h-(u-c)=v-a` then fixes `(a,v)` by uniqueness of
positive differences.

Finally, suppose two folds have the same `(a,u)`:

\[
 a+c+h=u+v,\qquad a+c'+h=u+v'.
\]

Then `v-c=v'-c'`.  This is a positive difference, so Sidonicity gives
`(c,v)=(c',v')`.  Thus each of the three two-coordinate projections is
injective.  QED.

Let `G_F` be the tripartite shadow graph of `H_F`: for every edge (7), put in
the three graph edges `a_Ac_C`, `c_Cu_U`, and `u_Ua_A`.  By P82.1, every graph
edge belongs to one and only one hyperedge.  In particular, the `C_S`
canonical triangles supplied by the folds are pairwise edge-disjoint.

A noncanonical triangle of `G_F` is equivalent to three distinct folds

\[
\begin{array}{rcl}
 a+c+h&=&r+s,\\
 a+z+h&=&u+w,\\
 x+c+h&=&u+y,                                      \tag{8}
\end{array}
\]

whose hyperedges `(a,c,r)`, `(a,z,u)`, `(x,c,u)` meet pairwise in the three
distinct shadow vertices `a_A,c_C,u_U`.  Thus they span exactly six vertices
of `H_F`; call (8) a **loose fold triangle**.  Let `T_F(B,h)` denote their
number, with each shadow triangle counted once.

### Lemma P82.2 (uniform removal dichotomy)

For every `epsilon>0` there are `eta=eta(epsilon)>0` and `p_0(epsilon)` such
that, for every `p>=p_0` and every endpoint-normalized integer Sidon set in
(1),

\[
 C_S(B,h)\ge\varepsilon p^2
 \quad\Longrightarrow\quad
 T_F(B,h)\ge\eta p^3.                                  \tag{9}
\]

No defect or hole hypothesis is needed for this implication.

### Proof

The graph `G_F` has `n=3p` vertices and contains `C_S` pairwise edge-disjoint
canonical triangles.  Hence at least `C_S` graph edges must be deleted to
make it triangle-free.  Apply the contrapositive form of the triangle-removal
lemma with deletion parameter `epsilon/9`.  If `C_S>=epsilon*p^2`, then
`G_F` contains at least

\[
                 \rho(\varepsilon/9)(3p)^3              \tag{10}
\]

triangles, where `rho(alpha)>0` depends only on `alpha`.

Because every shadow edge has a unique supporting hyperedge, the three
supporting hyperedges of a shadow triangle are either all the same or all
distinct.  The first case is one of the `C_S<=p(p+1)/2` canonical triangles;
the second case is exactly (8).  For all sufficiently large `p`, subtracting
the canonical triangles from (10) leaves at least
`(27*rho(epsilon/9)/2)*p^3` loose fold triangles.  This proves (9), for
example with `eta=27*rho(epsilon/9)/2`.  QED.

Consequently, the following density statement would prove (5):

\[
 \forall\varepsilon>0\ \exists p_0\ \forall p\ge p_0\
 \forall(B,h,b)\in A_p:\quad T_F(B,h)<eta(\varepsilon)p^3.
                                                               \tag{11}
\]

This is a genuine structure theorem rather than a fixed-biclique condition.
It is the exact point at which the phase information in (3) still has to be
used.

## 3. Why bare removal does not finish

The P75 ruler gives an exact admissible falsifier to the claim that `H_F` is
`(6,3)`-free.  Three of its folds are

```text
403+501+988=915+977
169+689+988=915+931
169+501+988=775+883
```

Their hyperedges are

```text
(403,501,915), (169,689,915), (169,501,775).
```

They meet pairwise in `915_U`, `169_A`, and `501_C`, respectively, and hence
form a loose fold triangle.  The same ruler satisfies `delta=14>0` and the
full `b=1` literal hole by P75.  Exact enumeration gives

\[
                     C_S=51,\qquad T_F=25.              \tag{12}
\]

Thus (3) does not forbid (8) pointwise.  It must instead imply a density
bound such as (11), or be combined with an additional phase-sensitive
identity.

In fact, subtracting the three equations in (8) only gives

\[
\begin{array}{rcl}
 a+z+y&=&x+c+w,\\
 c+u+w&=&z+r+s,\\
 a+u+y&=&x+r+s.                                      \tag{8a}
\end{array}
\]

Both `h` and `b` have disappeared.  These are translation-invariant
triple-sum collisions, which a Sidon hypothesis does not exclude.  This is
the precise algebraic reason that uncoloured triangle removal stops at
P82.2; a completion must retain the carry or phase attached to each shadow
edge.

There is a second finite obstruction to a shortcut.  For the P75 fold list,
take any two of the four raw roles `(a,c,u,v)` as the two parts of a
bipartite edge and any third role as one of the at most `p` colours.  All 12
such role projections give colour classes that are matchings, but none gives
induced matchings in the full projected graph.  The smallest exact number of
same-colour inducedness violations is 19.  Hence the usual
"partition into `p` induced matchings" proof cannot be obtained merely by
choosing three raw fold roles.  This finite check only falsifies those 12
specific encodings; it is not an exclusion theorem.

The `K_{5,5}` from P79 is irrelevant to P82.2 and (11).  No fixed biclique is
excluded or assumed anywhere above.

## 4. Phase-sensitive form of the frontier

Write `H=h-1=max(B)`.  For `b=1`, reflection of the high pair in a fold gives

\[
 a+c+(H-u)+(H-v)=H-1.                                  \tag{13}
\]

On the other hand, the endpoint instance of the literal hole is

\[
                 H-1\notin B+B+B.                      \tag{14}
\]

Thus a fold represents `H-1` as two elements of `B` and two elements of the
reflected set `H-B`, while (14) forbids replacing the reflected pair by one
element of `B`.  For `b=2`, the forbidden target is `H-2`, whereas the fold
target in (13) remains `H-1`; this one-unit phase discrepancy must be retained.

Equivalently, if `q(s)` is the ordered pair-sum multiplicity, then

\[
 \sum_s q(s)q(s+h)
   =[x^h]P(x)^2P(x^{-1})^2,\qquad P(x)=\sum_{t\in B}x^t, \tag{15}
\]

while the literal hole is the vanishing coefficient

\[
                 [x^{-b}]P(x)^3P(x^{-1})=0.             \tag{16}
\]

The support count `C_S` and the weighted coefficient (15) differ only by
factors in `{1,2,4}`.  A successful phase-energy argument may therefore work
with (15), but it must connect the coefficient at the endpoint frequency `h`
to the **integer**, not merely modular, zero in (16).  Parseval or fourth
moment alone does not make that connection; P77 already records the resulting
`O(p^2)` barrier.

## 5. Counterfamily lane and exact falsifiers

There is one plausible infinite-family template that is not settled by the
removal reduction.  Start with a normalized Sidon ruler `A` of width `W`, put

\[
 \gamma=\lfloor W/2\rfloor+1,\qquad
 B=A+\gamma,\qquad h=W+\gamma+1.                       \tag{17}
\]

Then, for both `b=1,2`,

\[
 \min(B+B+b)=2\gamma+b>W=\max\Delta^+(B),              \tag{18}
\]

so the full literal hole is automatic.  Near-optimal Singer rulers have
`W=p^2+O(p)`, making (17) lie within only `O(p)` of the positive-defect
threshold.  Proving an `Omega(p^2)` shifted-sum correlation in that short
window would give the requested counterfamily.

As a finite falsifier check, applying (17) to the 26
`reflected-singer-natural` rulers stored in
`problems/864/compute/p46/carry_statistics.json`, with `38<=p<=129`, gives
positive defect in every row (minimum 161).  The largest fold count is `118`
at `p=104`, also the largest ratio in this finite table,

\[
                       {C_S\over p^2}={118\over10816}.
\]

This falsifies the stronger guess that automatic range separation in (18)
forces `C_S<=p`.  The exact rows prove neither decay nor a positive limiting
density and are not evidence for either asymptotic conclusion.  Resolving the
template requires a uniform carry-sensitive autocorrelation estimate, not
more finite enumeration.

## 6. Claim boundary and prior art

The new proved statement is P82.2.  It reduces any failure of the uniform
little-oh assertion to a positive cubic density of the explicit systems (8).
It does not prove that the literal hole suppresses those systems, and it does
not construct an infinite family.

The removal input is the standard triangle-removal lemma; see Conlon--Fox,
[*Graph removal lemmas*](https://arxiv.org/abs/1211.3487).  The local Problem
864 notes, the [Erdos Problems #864 page](https://www.erdosproblems.com/864),
and searches of the Sidon/removal literature did not reveal the specific fold
hypergraph reduction (7)--(11) or an existing theorem that supplies (11).
The general removal theorem is prior art; the application and the remaining
phase-density question are the only claims made here.
