# P30: Ruzsa carry theorem lane

Status: no direct infinite sub-\(3\) Ruzsa reflection family is proved.
The CRT congruence route is rigorously obstructed: every modular target has
at least \((p-1)(p-3)\) ordered \(3B-B\) representations with nonzero
difference. Two natural explicit center rules are exactly falsified, including
their diagonal cases. An exhaustive natural-cut extension at \(p=257\) also
falsifies the coefficient \(14/5=3-1/5\) for that parameter.

The surviving frontier is purely an integer carry/cyclic-order statement.
Nothing here rules out a smaller fixed epsilon along an infinite subsequence.

## 1. CRT form of every natural cut

Let \(p\) be an odd prime, let \(g\) be a primitive root modulo \(p\), and put

\[
    n=p(p-1), \qquad b=p-1.
\]

For \(i\in\mathbb Z/(p-1)\mathbb Z\), the standard Ruzsa residue \(c_i\)
is the CRT solution

\[
    c_i\equiv i\pmod {p-1},\qquad
    c_i\equiv g^i\pmod p.                                  \tag{1}
\]

Its least representative is

\[
    c_i=[g^i]_p+p[i-[g^i]_p]_{p-1}.                        \tag{2}
\]

Cut at \(c_k\), reindex by \(h=i-k\), and set \(e=g^k\). The normalized
cyclic lift is

\[
    B_e=\{b_h: h\in\mathbb Z/(p-1)\mathbb Z\},
    \qquad b_h=[c_{k+h}-c_k]_n,                             \tag{3}
\]

with CRT coordinates

\[
    b_h\equiv h\pmod {p-1},\qquad
    b_h\equiv e(g^h-1)\pmod p.                             \tag{4}
\]

Conversely every \(e\in\mathbb F_p^*\) is \(g^k\), so (4) parametrizes
exactly all natural cuts, without affine multipliers. Explicitly, if

\[
    \delta_h=[e(g^h-1)]_p,\qquad
    q_h=[h-\delta_h]_{p-1},
\]

then the least representative is

\[
    b_h=\delta_h+p q_h.                                    \tag{5}
\]

In particular \(b_0=0\), and \(B_e\subset[0,n-1]\) has \(b=p-1\) points.

## 2. Exact Ruzsa difference rectangle

### Lemma 2.1 (support and uniqueness)

For every cut \(e\),

\[
 \{b_u-b_v\pmod n:u\ne v\}
 =
 \{r\pmod n:r\not\equiv0\pmod {p-1},\
                r\not\equiv0\pmod p\},                    \tag{6}
\]

and every residue on the right has exactly one ordered representation.

#### Proof

Write \(u=v+h\), where \(h\ne0\pmod {p-1}\). By (4), the two CRT
coordinates of the difference are

\[
    h,\qquad e g^v(g^h-1).                                 \tag{7}
\]

Both are nonzero. For fixed \(h\ne0\), the second coordinate runs exactly
once through \(\mathbb F_p^*\) as \(v\) runs through
\(\mathbb Z/(p-1)\mathbb Z\). CRT now gives (6), with uniqueness. QED.

Thus the nonzero difference support has size

\[
    (p-2)(p-1),                                             \tag{8}
\]

and its complement consists exactly of the two punctured CRT axes, of total
size \(2p-3\).

### Corollary 2.2 (strong modular and literal Sidon)

Every \(B_e\) is strongly modular Sidon: all unordered pair sums modulo
\(n\), including all diagonals, are distinct. Its least representatives are
therefore a literal integer Sidon set, again including diagonals.

#### Proof

Suppose

\[
    b_a+b_b=b_c+b_d\pmod n.
\]

Then \(b_a-b_c=b_d-b_b\). If this residue is zero, distinctness of the
\(b_h\) gives \(a=c\) and \(d=b\). If it is nonzero, Lemma 2.1 gives
\((a,c)=(d,b)\). In either case the unordered pairs are equal.

This argument also covers a putative diagonal collision
\(2b_a=2b_c\): if \(a\ne c\), the same nonzero difference would have the
two ordered representations \((a,c)\) and \((c,a)\), contrary to Lemma 2.1.
Equivalently, the only possible self-negative residue \(n/2\) lies on the
missing \(p\)-coordinate axis.

An integer pair-sum collision would remain a collision modulo \(n\), so
every cyclic lift is literal Sidon. QED.

## 3. Exact carry hole and reflection, with diagonals

For a normalized lift \(B\subset[0,L]\), define

\[
 \begin{aligned}
 S(B)&=\{x+y:x,y\in B,\ x\le y\},\\
 \Delta^+(B)&=\{z-w:z,w\in B,\ z>w\},\\
 \Sigma_1(B)&=\{x+y-n:x,y\in B,\ x\le y,\ x+y>n\}.
 \end{aligned}
\]

The definition of \(S(B)\) includes \(x=y\).

For \(0\le t<n\), put

\[
 R_B(t)=\#\{s\in\Sigma_1(B):s>t,\
                         n+t-s\in\Delta^+(B)\}.            \tag{9}
\]

### Lemma 3.1 (top carry)

For every strongly modular Sidon lift \(B\),

\[
    2n+t\notin S(B)+\Delta^+(B)
    \quad\Longleftrightarrow\quad R_B(t)=0.                \tag{10}
\]

#### Proof

A hit is an equality

\[
    x+y+z-w=2n+t,\qquad x\le y,\quad z>w.                  \tag{11}
\]

Since \(0<z-w<n\), (11) forces \(x+y>n\). Put \(s=x+y-n\).
Then (11) is equivalent to

\[
    z-w=n+t-s,
\]

and this is in \([1,n-1]\) exactly when \(s>t\). The converse reverses
these steps. Diagonal choices \(x=y\) were never removed. QED.

### Lemma 3.2 (diagonal-safe reflected construction)

Let \(B\subset[0,L]\) be literal Sidon with \(0,L\in B\). If

\[
    M>2L,\qquad M\notin S(B)+\Delta^+(B),                  \tag{12}
\]

then

\[
    A=B\mathbin\cup(M-B)                                   \tag{13}
\]

has \(2|B|\) points. Its only repeated unordered sum is \(M\), with exactly
\(|B|\) representations.

#### Proof

The two blocks are disjoint because \(M>2L\). Low internal sums are below
\(M\), high internal sums are above \(M\), and each class is simple by
literal Sidonicity, including diagonal sums.

Every cross sum is \(M+x-y\). Positive nonzero differences in a Sidon set
are unique, while the \(|B|\) choices \(x=y\) give exactly the exceptional
sum \(M\). A low internal sum \(s\) collides with a cross sum \(M-d\)
exactly when \(M=s+d\), with \(d\in\Delta^+(B)\). Reflecting gives the
identical criterion for high internal sums and cross sums \(M+d\).
Condition (12) excludes all such collisions. QED.

For \(M=2n+t\), one automatically has \(M>2L\), and Lemmas 3.1-3.2 reduce
the construction to the single exact condition \(R_{B_e}(t)=0\).

Since \(b=p-1\) and \(n=b^2+b\),

\[
    {2n+t\over b^2}
      =2+{2\over b}+{t\over b^2}.                          \tag{14}
\]

Thus a rule \(t\le\alpha n\) with fixed \(\alpha<1\) would give coefficient
\(2+\alpha+o(1)<3\) and hence a fixed positive epsilon for all sufficiently
large supplied primes.

## 4. Uniform modular saturation obstruction

The modular equation behind (11) is never sparse.

### Theorem 4.1 (every target has quadratically many CRT solutions)

Fix an odd prime \(p\ge5\) and a cut \(e\), and let
\(\tau\in\mathbb Z/n\mathbb Z\) have CRT coordinates

\[
    H=\tau\pmod {p-1},\qquad T=\tau\pmod p.
\]

There are at least

\[
    (p-1)(p-3)                                              \tag{15}
\]

ordered quadruples \((a,b,c,d)\) satisfying

\[
    b_a+b_b+b_c-b_d=\tau\pmod n,\qquad c\ne d.             \tag{16}
\]

In particular \(3B_e-B_e=\mathbb Z/n\mathbb Z\) for every natural cut.

#### Proof

Put

\[
 X=g^a,\quad Y=g^b,\quad Z=g^c,\quad
 \lambda=g^{-H},\quad K=2+T/e.
\]

The first CRT coordinate in (16) determines

\[
    d=a+b+c-H,\qquad g^d=\lambda XYZ.                      \tag{17}
\]

The second coordinate then becomes the affine cubic equation

\[
    X+Y+Z-\lambda XYZ=K.                                   \tag{18}
\]

Choose \(X,Y\in\mathbb F_p^*\) such that

\[
    1-\lambda XY\ne0,\qquad K-X-Y\ne0.                    \tag{19}
\]

There are at least

\[
    (p-1)^2-(p-1)-(p-1)=(p-1)(p-3)
\]

such pairs: each excluded equation removes at most \(p-1\) pairs. For every
remaining pair, (18) has the unique nonzero solution

\[
    Z={K-X-Y\over 1-\lambda XY}.                           \tag{20}
\]

Discrete logarithms recover a unique \((a,b,c,d)\). Moreover \(c=d\)
would imply \(Z=\lambda XYZ\), hence \(\lambda XY=1\), contradicting
(19). QED.

This theorem is the rigorous obstruction to a congruence-only Ruzsa attack.
Even before orientation and carry are imposed, every target has
\(\Omega(p^2)\) nonzero-difference representations. Any actual hole must
discard all of them through the order of the least representatives in (5)
and the layer-two inequalities in (11).

The standalone audit enumerates (18) for \(p=5,7,11\). Its exact minimum
over every \((\lambda,K)\) is respectively \(8,24,80\), equal to the lower
bound (15) in each case.

## 5. Exact falsifiers to explicit center rules

### 5.1 Fixed rational top offsets

The most direct rule is

\[
    M_\alpha=2n+\lfloor\alpha n\rfloor                    \tag{21}
\]

with a fixed \(\alpha<1\), choosing the cut \(e\) if necessary.

This already fails at modest parameters.

* At \(p=71\), \(\alpha=2/3\), \(n=4970\), and \(M=13253\), every one of
  the 70 natural cuts is hit. For \(e=1\), an exact witness is

  \[
      3870+4846+4893-356=13253.                            \tag{22}
  \]

* At \(p=191\), \(\alpha=4/5\), \(n=36290\), and \(M=101612\), every one
  of the 190 natural cuts is hit. For \(e=1\), an exact witness is

  \[
      30148+35751+35751-38=101612.                         \tag{23}
  \]

The independent witness audit found 2 diagonal pair-sum witnesses among its
70 chosen \(p=71\) witnesses and 1 among its 190 chosen \(p=191\)
witnesses. Thus the all-cut claims were checked with diagonals present.

The full fixed-offset scan covers every natural cut for all 53 primes
\(5\le p\le257\) and

\[
    \alpha\in\{1/2,3/5,2/3,7/10,3/4,4/5\}.
\]

At the exact offset \(2/3\), no cut is a hole already at \(p=71\). At
the exact offset \(4/5\), no cut is a hole at \(p=191,193\), or at any
tested prime \(p\ge227\). Hence a fixed real fraction of \(n\) is not the
hidden rule behind the moving first holes.

### 5.2 Singular Cayley-cubic rule

A less naive algebraic choice makes (18) singular. Take

\[
    t=(p-1)r,\qquad e=r/4\pmod p.                          \tag{24}
\]

Then \(H=0\), \(T=-r\), and \(K=-2\), so the modular equation is the
singular Cayley cubic

\[
    X+Y+Z-XYZ=-2.                                          \tag{25}
\]

Choosing \(r=\lfloor2p/3\rfloor\) would give asymptotic coefficient
\(8/3\). It does not give a carry hole. At \(p=19\),

\[
    r=12,\quad e=3,\quad n=342,\quad M=900,
\]

and the exact witness is

\[
    307+307+307-21=900.                                    \tag{26}
\]

Here the pair sum \(307+307\) is diagonal. Omitting diagonals would therefore
produce a false positive at the first nontrivial falsifier.

The scan through \(p=257\) finds this \(2/3\) singular rule to be a hole
only at \(p=5,7,17\); every tested prime \(p\ge19\) is hit. Theorem 4.1
explains the structural failure: singularity does not remove the
two-dimensional regular component, and (25) still has at least
\((p-1)(p-3)\) nonzero-difference modular solutions.

### 5.3 Canonical cuts and coefficient drift

The canonical choices \(e=1\) and \(e=-1\) were scanned for all 53 primes
\(5\le p\le257\). All 106 cuts have an exact center below \(3b^2\), but
their first-hole coefficient is not uniformly close to the earlier
\(2.6\) data.

The delayed canonical example is

\[
 \begin{aligned}
 p&=199,& e&=-1,& b&=198,& L&=39365,\\
 M_{\rm first}&=114445,&
 {M_{\rm first}\over b^2}&={114445\over39204}
   =2.919217\ldots .
 \end{aligned}                                             \tag{27}
\]

Every integer from \(2L+1=78731\) through \(114444\) lies in
\(S(B)+\Delta^+(B)\). In particular this cut has no admissible center at
coefficient at most \(2.9\). The fresh reflected census has 396 points and
only the sum \(114445\) repeats, exactly 198 times.

More decisively, all 256 natural cuts at \(p=257\) were scanned independently:

\[
 \begin{array}{c|c|c|c}
 &e&M_{\rm first}&M_{\rm first}/256^2\\ \hline
 \text{best}&23&183950&2.806854248\ldots\\
 \text{worst}&120&193873&2.958267211\ldots
 \end{array}                                                \tag{28}
\]

All 256 reflected censuses pass. Since

\[
    183950>\left\lfloor {14\over5}\,256^2\right\rfloor
          =183500,                                         \tag{29}
\]

no natural cut at \(p=257\) has a reflected center with coefficient at most
\(14/5=3-1/5\). This is an exact finite falsifier to epsilon \(=1/5\)
as a universal natural-cut theorem. It does not rule out a smaller fixed
epsilon on infinitely many primes.

## 6. Reproduction and independent checks

The targeted scanners use only the standard library and do not read Singer
records.

~~~text
python -B problems/864/compute/p30/scan_canonical_cuts.py --prime-min 5 --prime-max 257 --output problems/864/compute/p30/canonical_cuts_p257.json

python -B problems/864/compute/p30/scan_canonical_cuts.py --prime-min 257 --prime-max 257 --all-cuts --output problems/864/compute/p30/all_cuts_p257.json

python -B problems/864/compute/p30/scan_fixed_offsets.py --prime-min 5 --prime-max 257 --offsets 1/2 3/5 2/3 7/10 3/4 4/5 --output problems/864/compute/p30/fixed_offsets_p257.json

python -B problems/864/compute/p30/audit_falsifiers.py --output problems/864/compute/p30/audit_falsifiers.json
~~~

The last program is independent: it imports no P12 or other P30 code. It
reconstructs CRT cuts, materializes diagonal-aware unordered sums and
positive differences, emits actual integer witnesses for every cut in the
\(p=71\) and \(p=191\) falsifiers, checks the difference rectangle at
\(p=19,71\), enumerates the small cubic surfaces, and reruns the complete
reflected census for (27).

## 7. Prior-art comparison and frontier

The classical Ruzsa construction and its generalized variants establish
the modular Sidon property; see Martin--O'Bryant, *Constructions of
Generalized Sidon Sets* (JCTA 113 (2006), 591--607),
https://arxiv.org/abs/math/0408081, and Cilleruelo--Ruzsa--Vinuesa,
*Generalized Sidon sets*, https://arxiv.org/abs/0909.5024.

Lam--Ling, *A Construction of Modular Generalized Sidon Sets*,
Ars Combinatoria 114 (2014), 65--71, explicitly records that no Ruzsa
difference is a multiple of \(p\) or \(p-1\):
https://combinatorialpress.com/ars-articles/volume-114-ars-articles/a-construction-of-modular-generalized-sidon-sets/.
Thus the punctured-axis exclusion in (6) is prior art. Lemma 2.1 records
the stronger exact equality and uniqueness in the natural-cut coordinates;
it is not presented as a globally new axis observation.

The local and primary-source novelty search found no prior theorem selecting
an integer cut and reflected center with a uniform sub-\(3\) coefficient.
No source was located for the uniform modular-surface lower bound (15) in
this carry setting. The theorem-grade outputs of this lane are the
self-contained exact form of (6), bound (15), and the diagonal-safe
falsifiers above.

The remaining statement is now sharply isolated:

> Do there exist a fixed \(\eta>0\) and infinitely many primes \(p\) for
> which some \(e\in\mathbb F_p^*\) and
> \(0\le t\le(1-\eta)n\) satisfy \(R_{B_e}(t)=0\)?

A positive answer gives a literal reflected family with coefficient
\(3-\epsilon\) for some fixed epsilon by (14). Theorem 4.1 proves that no
CRT congruence exclusion, including a singular target surface, can answer
it. A proof must control the simultaneous least-representative order and
layer-two carry in (5), (9), and (11). No such infinite carry theorem is
proved here.
