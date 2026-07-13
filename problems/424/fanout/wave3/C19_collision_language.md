# C19: exact collision language for the fixed affine orbit

## Verdict

Let `B` be the least set containing `2,3,5` and closed under

\[
T_k(x)=kx-1,\qquad k\in\{2,3,5\},\qquad x\ne k,
\]

and put

\[
\mathcal C_{ij}=\{t\ge1:it,jt\in B\},
\qquad ij\in\{23,25,35\}.
\]

This lane gives an exact automaton and normal-form census, but no finite
relation system proving C09-R.

1. A normalized integer state `(A,B,C)` represents the relation
   \(Ax-By=C\).  Its transitions recognize both orbit-value collisions and
   universal affine collision blocks exactly.
2. Through word depth 12 there are respectively `1845`, `1550`, and `1435`
   distinct paired affine states for channels `23`, `25`, and `35`.
   Map-word multiplicity is kept separate from affine-state multiplicity.
3. Every nonseed collision generates an infinite family.  The smallest
   collision morphisms are \(15t-2\), \(600t-98\), and \(400t-51\).
4. The `25` block monoid is not finitely generated.  At exact depth \(d\)
   it has at least \(d-6\) indecomposable affine states for every \(d\ge7\).
   Hence through depth \(D\) it has at least
   \((D-6)(D-5)/2\) primitive states.
5. This is an obstruction to a finite list of witness-respecting affine
   suborbit generators.  It is not a proof that the projected integer set
   \(\mathcal C_{25}\) has no unrelated finite description: different word
   pairs can meet at one integer.  It also supplies no upper bound for the
   collision tax in C09-R.

All relations and census quantities below were checked with integers.

## 1. Exact linear automaton

For a word \(w=(k_1,\ldots,k_r)\) in application order, write

\[
F_w=T_{k_r}\circ\cdots\circ T_{k_1},\qquad
F_w(x)=P_wx-C_w.
\]

Appending a letter gives

\[
(P,C)\longmapsto(kP,kC+1).                              \tag{1}
\]

Start channel `ij` in the primitive state

\[
S_{ij}=(j,i,0),
\]

meaning \(jx-iy=0\).  Read the two words from their outermost letters, so
from right to left in application notation.  Substitution of
\(x=T_k(x')\), \(y=T_l(y')\) gives the exact transition

\[
(A,B,C)\xrightarrow{(k,l)}(Ak,Bl,C+A-B),                \tag{2}
\]

followed by division by \(\gcd(A,B,C)\).  If only one word has letters
left, (2) uses `(k,blank)` or `(blank,l)` and adds \(A\) or subtracts
\(B\), respectively.

After all letters of \(u,v\) are stripped, roots \(a,b\in\{9,14\}\)
are accepted exactly when

\[
Aa-Bb=C.
\]

This is equivalent, with no congruence relaxation, to

\[
j(P_ua-C_u)=i(P_vb-C_v).                                \tag{3}
\]

A paired word `(u,v)` is a universal collision block precisely when it is
a loop at \(S_{ij}\).  Equivalently, for some integers \(P,e\),

\[
P_u=P_v=P,\qquad C_u=ie,\qquad C_v=je.                  \tag{4}
\]

It then sends a safe collision parameter to

\[
h_{u,v}(t)=Pt-e.                                         \tag{5}
\]

Here safe means \(it,jt>5\), so every subsequent affine letter is licensed.

## 2. Normal forms and census

At each depth, affine maps are normalized by `(P,C)` and represented by the
lexicographically least word.  The exact word fiber is retained.  Thus the
census distinguishes:

- a raw word pair;
- a paired affine state `(P,e)` from (4); and
- a projected integer \(t\).

At depth 12 the map census independently reproduces B04:

\[
3^{12}=531441\text{ words},\quad 518933\text{ maps},
\quad\text{maximum map fiber }4.
\]

In the next table each entry is
`distinct affine states / raw word pairs / primitive affine states`.
Primitivity means no factorization into two nonidentity blocks under

\[
(P_2,e_2)\circ(P_1,e_1)
=(P_2P_1,P_2e_1+e_2).                                   \tag{6}
\]

| depth | `23` | `25` | `35` |
|---:|---:|---:|---:|
| 2 | 1 / 1 / 1 | - | - |
| 4 | 2 / 2 / 1 | - | - |
| 5 | 4 / 4 / 4 | - | - |
| 6 | 5 / 5 / 2 | 1 / 1 / 1 | 2 / 2 / 2 |
| 7 | 15 / 15 / 7 | 4 / 4 / 4 | 4 / 4 / 4 |
| 8 | 37 / 37 / 28 | 14 / 14 / 14 | 18 / 18 / 18 |
| 9 | 79 / 84 / 45 | 47 / 49 / 47 | 55 / 56 / 55 |
| 10 | 251 / 254 / 161 | 152 / 162 / 152 | 152 / 156 / 152 |
| 11 | 664 / 686 / 483 | 490 / 530 / 490 | 501 / 525 / 501 |
| 12 | 1845 / 1955 / 1242 | 1550 / 1710 / 1549 | 1435 / 1532 / 1431 |

The number of distinct normalized states `(A,B,C)` lying on the canonical
accepting paths also grows in this truncation:

| maximum depth | `23` states | `25` states | `35` states |
|---:|---:|---:|---:|
| 6 | 11 | 6 | 11 |
| 8 | 41 | 11 | 38 |
| 10 | 132 | 34 | 97 |
| 12 | 324 | 110 | 284 |

This finite table is a state census, not a proof that no finite quotient of
the two-tape language exists.

The orbit-value normal form starts with the two roots `9,14`, includes all
words up to the stated depth, and adjoins the seeds.  In each channel entry
below, the first number is the number of distinct \(t\), and the second is
the raw representation-pair mass.

| maximum depth | raw representations | orbit values | `23` | `25` | `35` |
|---:|---:|---:|---:|---:|---:|
| 0 | 5 | 5 | 1 / 1 | 1 / 1 | 1 / 1 |
| 4 | 245 | 242 | 5 / 5 | 6 / 6 | 4 / 4 |
| 6 | 2189 | 2095 | 30 / 31 | 41 / 48 | 26 / 27 |
| 8 | 19685 | 18289 | 261 / 311 | 327 / 421 | 209 / 246 |
| 10 | 177149 | 159786 | 2416 / 3112 | 2763 / 3913 | 1851 / 2414 |
| 12 | 1594325 | 1396833 | 19665 / 28010 | 23123 / 36272 | 15504 / 22293 |

The first nonseed witnesses in these normal forms are

\[
\begin{aligned}
F_{25}(14)&=134=2\cdot67,&F_{3222}(9)&=201=3\cdot67,\\
F_3(9)&=26=2\cdot13,&F_{222}(9)&=65=5\cdot13,\\
F_{55}(9)&=219=3\cdot73,&F_{333}(14)&=365=5\cdot73.
\end{aligned}                                            \tag{7}
\]

The cross-multiplied checks in (3) are respectively `402=402`, `130=130`,
and `1095=1095`.

## 3. Infinite collision families

The first paired block in each channel is:

| channel | left word and map | right word and map | collision morphism |
|---:|---|---|---|
| `23` | `53`: \(15x-4\) | `35`: \(15x-6\) | \(h(t)=15t-2\) |
| `25` | `532225`: \(600x-196\) | `225523`: \(600x-490\) | \(h(t)=600t-98\) |
| `35` | `522252`: \(400x-153\) | `255222`: \(400x-255\) | \(h(t)=400t-51\) |

Every displayed map equality follows from (1).  Therefore every safe
\(t\in\mathcal C_{ij}\) gives the infinite family

\[
h^n(t)=P^nt-e\frac{P^n-1}{P-1}\in\mathcal C_{ij}.        \tag{8}
\]

For example, (7) gives exact word witnesses

\[
\begin{array}{c|c|c}
ij&it_n&jt_n\\ \hline
23&F_{25(53)^n}(14)&F_{3222(35)^n}(9)\\
25&F_{3(532225)^n}(9)&F_{222(225523)^n}(9)\\
35&F_{55(522252)^n}(9)&F_{333(255222)^n}(14).
\end{array}                                               \tag{9}
\]

Thus the observed collisions are not isolated map coincidences.

## 4. Infinite primitive affine states

In the word formulas below, \(2^r\) denotes a run of \(r\) letters `2`.

### Proposition 4.1

For every \(m\ge4\) and \(0\le q\le m-4\), define

\[
\begin{aligned}
u_{m,q}&=5\,2^q\,3\,2^{m-q}\,3,\\
v_{m,q}&=2^{q+2}\,5\,3\,2^{m-q-4}\,3\,2^2.
\end{aligned}                                            \tag{10}
\]

Put

\[
P_m=45\cdot2^m,
\qquad
e_{m,q}=9\cdot2^m-3\cdot2^{m-q-1}-1.                   \tag{11}
\]

Then, exactly,

\[
(P_{u_{m,q}},C_{u_{m,q}})=(P_m,2e_{m,q}),\qquad
(P_{v_{m,q}},C_{v_{m,q}})=(P_m,5e_{m,q}).                \tag{12}
\]

Hence every pair in (10) is a `25` collision block.  All these blocks are
indecomposable in the monoid of nonidentity `25` collision blocks.

#### Proof

Iteration of (1) gives (12); both words have the same multiset
`2^m 3^2 5`, so their common slope is \(45\cdot2^m\).  The offsets obtained
from (1) are the two integer multiples in (12).

It remains to prove indecomposability.  Suppose a `25` block used no letter
`5`.  Its two words would have the same multiset with \(a\) letters `2` and
\(b\) letters `3`.  Write \(R_w=C_w/P_w\).  Swapping an adjacent `32` to
`23` increases \(R_w\), so the minimum and maximum for this multiset are

\[
R_{\min}=\frac12+\frac1{2\cdot3^b}-\frac1{2^a3^b},
\qquad
R_{\max}=1-\frac{1+3^{-b}}{2^{a+1}}.                    \tag{13}
\]

For every nonempty multiset, direct subtraction gives
\(R_{\max}<2R_{\min}\).  But a `25` block requires

\[
\frac{C_v}{C_u}=\frac52,
\]

which is impossible under (13).  Therefore every nonidentity `25` block
contains a letter `5`.

The slope of a composition is the product of the slopes.  A composition of
two nonidentity `25` blocks is therefore divisible by \(25\).  In contrast,
\(P_m=45\cdot2^m\) is divisible by \(5\) but not by \(25\).  Thus no block
in (10) factors. \(\square\)

At depth \(d=m+3\), the allowed values of \(q\) give \(m-3=d-6\) distinct
shifts.  Consequently the exact affine generator count is unbounded, with

\[
\#\{\text{primitive states of depth}\le D\}
\ge\sum_{d=7}^D(d-6)
=\frac{(D-6)(D-5)}2.                                    \tag{14}
\]

The whole explicit family has finite reciprocal slope mass:

\[
\sum_{m=4}^{\infty}\frac{m-3}{45\cdot2^m}=\frac1{180}.  \tag{15}
\]

Thus (14) is a finite-generator obstruction, not evidence that this family
alone is too large for C09-R.  Formula (10) is itself parametrically
compressible.

## 5. Projected collision test

The Boolean recurrence for `B` was evaluated through `5,000,000`, giving a
complete collision scan for \(t\le10^6\).  A collision is marked covered at
depth \(D\) if it is \(Pt-e\) for a smaller safe collision and one of the
distinct paired affine states of depth at most \(D\).

| channel | collision \(t\le10^6\) | block states through 12 | covered | not covered |
|---:|---:|---:|---:|---:|
| `23` | 19555 | 2903 | 2181 | 17374 |
| `25` | 29587 | 2258 | 870 | 28717 |
| `35` | 26211 | 2167 | 452 | 25759 |

Every marked image was checked again against the two membership bytes.  The
large uncovered columns show that bounded-depth universal blocks do not
give a useful finite decomposition at this cutoff.  They do not prove that
the uncovered populations remain infinite, because deeper blocks and
alternative representations can project to the same integers.

## 6. Consequence for C09-R

The finite-list route fails in its natural exact form.  There is no finite
set of universal paired affine blocks whose composition monoid contains all
exact `25` block relations: Proposition 4.1 supplies infinitely many
indecomposable elements.  The depth-12 projected test also leaves most
collisions outside the suborbits generated by the enumerated block states.

Two stronger conclusions are not justified:

1. Proposition 4.1 does not rule out a finite automaton with parameterized
   cycles; (10) is one such compressible family.
2. It does not rule out a finite description of the projected set using
   accidental alternative witnesses.  A relation system for an upper bound
   only needs to cover each integer once, not every word relation.

No estimate here proves

\[
\Delta(X)\le\tau_{1/2}(X)F(X).
\]

The usable next object would be a weighted, possibly countable-state
automaton that groups families such as (10) and controls the remaining
primitive mass.  The present result is the requested explicit growing-state
obstruction, not a proof of C09-R.

## 7. Reproduction

Code:
[collision_language.py](../../compute/wave3/C19_collision_language/collision_language.py)
and
[test_collision_language.py](../../compute/wave3/C19_collision_language/test_collision_language.py).

```powershell
cd problems/424/compute/wave3/C19_collision_language
python -m unittest -v test_collision_language.py
python collision_language.py --max-depth 12 --t-limit 1000000
```

The focused suite has 11 tests.  It checks the automaton/direct-equation
equivalence, the first three collision blocks, the B04 map collision, the
normal-form census, the primitive decomposition law, the complete scan
through \(t=1000\), and (12) for all \(4\le m\le15\).

Related supplied work:
[C09 fixed-subsystem threshold](C09_fixed_subsystem_threshold.md) and
[B04 collision-exact affine renewal](../wave2/B04_affine_renewal.md).
