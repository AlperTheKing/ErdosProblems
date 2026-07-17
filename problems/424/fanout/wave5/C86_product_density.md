# C86: a collision-free 2-adic product recurrence, and its exact capacity obstruction

## Verdict

There is a canonical correlated product family whose collisions can be
removed without looking at the represented products: separate the affine
support maps by the 2-adic valuation of their outputs.  This gives the exact
recurrence in Lemma 1 below.  It is genuinely non-Cartesian and is not the
one-edge-per-product transversal ruled out by C10.

The route is nevertheless subcritical.  The general class of recurrences
which proves disjointness only by assigning each channel a distinct output
2-adic valuation has profile-free renewal capacity at most

\[
                         \boxed{\frac{23}{45}<1}.             \tag{1}
\]

This is an arithmetic obstruction, not an extrapolation from the census.
It applies to arbitrary, finite or infinite, collections of the two
closure-generated support maps and allows different maps on different
source valuation classes.  Thus a product-density proof must retain more
correlation than the single statistic \(v_2\).

The exact census through \(10^6\) confirms the obstruction.  The strongest
simple valuation-separated recurrence available from the actual closure has
inverse-slope load

\[
 \frac{6388439}{17054400}=0.374591835538043\ldots,            \tag{2}
\]

and its image covers `79079/239195` of the product support at \(10^6\).
These finite values are checks of the identities only; (1) is the uniform
proof.

## 1. Exact support maps

Write

\[
 G_0=G\cap3\mathbb N,\qquad
 G_2=G\cap\{n:n\equiv2\pmod3\},\qquad
 S=G_0G_2,
\]

and let \(Q(X)=|S\cap[1,X]|\).  If \(n\in S\), then the two factors
have different residues modulo three and hence are distinct.  Closure gives

\[
 n-1\in G_2.
\]

Since \(n\ge6\), the elements \(2\) and \(n-1\) are distinct, so another
closure step gives

\[
 2n-3\in G_0.
\]

Consequently, for every \(a\in G_0\), \(b\in G_2\),

\[
 F_a(n)=a(n-1)\in S,
 \qquad
 H_b(n)=b(2n-3)\in S.                                      \tag{3}
\]

Both maps are injective.  Moreover,

\[
 v_2(F_a(n))=v_2(a)+v_2(n-1),
 \qquad
 v_2(H_b(n))=v_2(b),                                       \tag{4}
\]

because \(2n-3\) is odd.

For \(r\ge0\), put

\[
 S_r=\{n\in S:v_2(n-1)=r\},
 \qquad Q_r(X)=|S_r\cap[1,X]|.                              \tag{5}
\]

## 2. Valuation-separated recurrence

Choose the following data.

* A set \({\cal B}\subseteq G_2\) in which the values \(v_2(b)\) are
  pairwise distinct.  Every \(H_b\) is applied to all of \(S\).
* A set \({\cal C}\) of channels \((r,a)\), with \(r\ge0\) and
  \(a\in G_0\).  The map \(F_a\) in this channel is applied only to
  \(S_r\).
* The target labels

  \[
  \{v_2(b):b\in{\cal B}\}
  \quad\text{and}\quad
  \{r+v_2(a):(r,a)\in{\cal C}\}                            \tag{6}
  \]

  are all distinct.

The data are fixed before any product is inspected.

**Lemma 1 (exact disjoint recurrence).**  Every such scheme satisfies, for
every integer \(X\ge1\),

\[
\boxed{
 Q(X)\ge
 \sum_{b\in{\cal B}}
 Q\!\left(\left\lfloor\frac{\lfloor X/b\rfloor+3}{2}\right\rfloor\right)
 +
 \sum_{(r,a)\in{\cal C}}
 Q_r\!\left(\left\lfloor\frac Xa\right\rfloor+1\right).
}                                                            \tag{7}
\]

**Proof.**  Equations (3)--(4) show that every summand in (7) counts an
injective image in \(S\cap[1,X]\).  The labels in (6) are the exact
2-adic valuations of those images.  Distinct labels make all images
pairwise disjoint.  The displayed cutoffs are obtained by solving
\(b(2n-3)\le X\) and \(a(n-1)\le X\), respectively.  QED.

This is a valid selected correlated family in the sense surviving C05:
the coordinate projections span incompatible scales, and no Cartesian
completion is made.

## 3. A sharp profile-free obstruction for this mechanism

Define the formal inverse-slope loads

\[
 W_H=\sum_{b\in{\cal B}}\frac1{2b},
 \qquad
 c_r=\sum_{(r,a)\in{\cal C}}\frac1a.                         \tag{8}
\]

A profile-free renewal proof from (7) would need a number \(\lambda>1\)
such that

\[
 W_H+c_r\ge\lambda\qquad\text{for every }r.                  \tag{9}
\]

This is the coefficient that survives when no lower bound for the
individual valuation profiles \(Q_r\) is assumed.  The following theorem
rules it out with fixed slack.

**Theorem 2 (2-adic capacity obstruction).**  Every valuation-separated
scheme satisfies

\[
 \boxed{W_H+\inf_{r\ge0}c_r\le\frac{23}{45}.}                \tag{10}
\]

**Proof.**  First note the residue-forced size bounds.  If \(a\in G_0\)
and \(v_2(a)=k\), then

\[
                       a\ge3\,2^k.                           \tag{11}
\]

If \(b\in G_2\) and \(v_2(b)=k\), write \(b=2^ku\) with \(u\) odd.
For even \(k\), one needs \(u\equiv2\pmod3\), hence \(u\ge5\).  For
odd \(k\), one needs \(u\equiv1\pmod3\), hence \(u\ge1\).  Therefore a
target valuation \(k\) used by an \(H\)-channel contributes at most

\[
 h_k=
 \begin{cases}
  1/(10\,2^k),&k\text{ even},\\
  1/(2\,2^k),&k\text{ odd}.
 \end{cases}                                                  \tag{12}
\]

Use the probability weights

\[
 \pi_0=\frac3{10},
 \qquad
 \pi_r=\frac7{10\,2^r}\quad(r\ge1).                         \tag{13}
\]

They sum to one, so

\[
 \inf_rc_r\le\sum_r\pi_rc_r.                                \tag{14}
\]

Consider one target valuation \(j\).  If it is assigned to an \(F\)-channel
from source class \(r\), then \(j=r+v_2(a)\), and (11) bounds its
contribution to the right side of (14) by

\[
 \frac{\pi_r}{3\,2^{j-r}}.                                   \tag{15}
\]

For \(j=0\), this is at most \(1/10\).  For every \(j\ge1\), maximizing
over \(0\le r\le j\) gives

\[
 \max_{r\le j}\frac{\pi_r}{3\,2^{j-r}}
 =\frac7{30\,2^j}.                                          \tag{16}
\]

Each target is assigned to at most one channel.  It therefore contributes
at most the larger of its \(H\)-bound (12) and its \(F\)-bound
(15)--(16).  Summing by parity gives

\[
\begin{aligned}
 W_H+\sum_r\pi_rc_r
 &\le \frac1{10}
 +\sum_{m\ge0}\frac1{2\,2^{2m+1}}
 +\sum_{m\ge1}\frac7{30\,2^{2m}}\\
 &=\frac1{10}+\frac13+\frac7{90}
 =\frac{23}{45}.
\end{aligned}                                                \tag{17}
\]

Equations (14) and (17) prove (10).  QED.

The proof allowed arbitrary actual members of \(G\), infinitely many
channels, and arbitrary assignment of \(F\)-channels to source valuation
classes.  It used only the requirement that distinctness be certified by a
single output valuation.  Thus adding more known multipliers cannot repair
this mechanism.

## 4. The simplest exact recurrence and its stronger envelope

There is a useful transparent subfamily.  Fix \(t\ge0\), choose

\[
 a_t\in G_0,\quad v_2(a_t)=t,
\]

and choose \(b_k\in G_2\), \(v_2(b_k)=k\), for \(0\le k<t\).  Apply
\(F_{a_t}\) to all parents and apply every \(H_{b_k}\) to all parents.
Then

\[
\boxed{
 Q(X)\ge Q(\lfloor X/a_t\rfloor+1)
 +\sum_{k<t}
 Q\!\left(\left\lfloor\frac{\lfloor X/b_k\rfloor+3}{2}\right\rfloor\right).
}                                                            \tag{18}
\]

Here the \(H\)-images occupy valuations below \(t\), whereas the
\(F\)-image occupies valuations at least \(t\).  Its formal load is

\[
 L_t=\frac1{a_t}+\sum_{k<t}\frac1{2b_k}.                     \tag{19}
\]

Equations (11)--(12) give the exact residue-only bounds

\[
 L_{2m}\le\frac7{15}-\frac2{15\,4^m},
 \qquad
 L_{2m+1}\le\frac7{15}-\frac1{5\,4^m}.                      \tag{20}
\]

In particular, every recurrence (18) has \(L_t<7/15\).

## 5. Exact finite gate

The checker independently reconstructs the least closure by the ascending
factor recurrence, forms the entire product support \(S\cap[1,10^6]\),
chooses the least actual \(G_0\) and \(G_2\) multiplier in every available
2-adic class, and verifies all claims with integers and `Fraction` values.
For every tested scheme it checks:

1. every generated image belongs to the exact product support;
2. the image pieces are pairwise disjoint;
3. their cardinality equals the right side of (18); and
4. their output valuations are the claimed ones.

The best exact image counts are:

| \(X\) | best \(t\) | generated images | \(Q(X)\) | coverage |
|---:|---:|---:|---:|---:|
| `1000` | 5 | 39 | 118 | 0.3305084746 |
| `10000` | 7 | 483 | 1591 | 0.3035826524 |
| `100000` | 7 | 6331 | 20391 | 0.3104801138 |
| `1000000` | 7 | 79079 | 239195 | 0.3306047367 |

For \(t=7\), the least actual multipliers through \(10^6\) are

\[
 a_7=384,
 \qquad
 (b_0,\ldots,b_6)=(5,2,44,152,80,800,1088),                  \tag{21}
\]

which give the exact load (2).  This is the maximum among all simple
schemes whose required multiplier classes occur below \(10^6\).

Normal Python and `python -O` outputs are byte-identical.

Reproduction:

```powershell
python problems\424\compute\wave5\C86_valuation_disjoint.py `
  --limit 1000000 --checkpoints 1000,10000,100000,1000000 `
  --output problems\424\compute\wave5\C86_valuation_disjoint_1e6.json

python -O problems\424\compute\wave5\C86_valuation_disjoint.py `
  --limit 1000000 --checkpoints 1000,10000,100000,1000000 `
  --output problems\424\compute\wave5\C86_valuation_disjoint_1e6_replay.json
```

SHA-256:

```text
B58B9C0BB8FBDF628DAF233AFFE9A25793DA77C70E9E9D2F771D39F55FE2B9BF  C86_valuation_disjoint.py
F2318E770CA0C7564B9DE7E74700A339B774F77FF07FBBDE0C4CF5636F98AF1A  C86_valuation_disjoint_1e6.json
F2318E770CA0C7564B9DE7E74700A339B774F77FF07FBBDE0C4CF5636F98AF1A  C86_valuation_disjoint_1e6_replay.json
```

## Route consequence

The candidate supplies exact collision control but not enough mass.  It is
therefore the complementary failure mode to the Cartesian route in C05:

* Cartesian boxes can have enough raw pairs, but Ford forces too many
  product collisions.
* A 2-adically separated correlated family has zero collisions, but Theorem
  2 forces its profile-free renewal mass below one.

Any surviving product-density recurrence must use a genuinely richer
correlation which permits controlled overlap between output valuation
classes, or must exploit quantitative information about the full vector of
profiles \((Q_r)_r\).  Merely adding further affine stars while preserving
2-adic disjointness cannot close the density theorem.
