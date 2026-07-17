# C100: affine renewal obstructions after the C102 gates

## Verdict

No positive-density theorem is proved here. After incorporating C102, three
precise boundaries are now verified.

1. Concatenation and supermultiplicativity do not imply C102 Gate (A). An
   exact integer continuation matches every known support value on the
   favorable `(3,2,1)` ray, obeys all scalar concatenation inequalities, and
   nevertheless has `N_K/360^K -> 0`. A concrete rank-two return language
   gives the same obstruction at the level of concatenation-closed sets.
2. The canonical max-fiber renewal estimate from C29 is false. The exact
   identity `T_322255=T_255232` tensors to \(8^k\) distinct canonical-type
   words with one affine value, whereas the proposed ceiling has exponential
   base \((31/30)^{31}\). The exact base ratio is
   \(8/(31/30)^{31}=2.8949187186\ldots>1\).
3. A scale index does not uniquely decode C102 products: already in the
   single `(2,1,1)`, `K=4`, `i=2` channel there is the exact collision

   \[
   58401\cdot90158=59859\cdot87962=5{,}265{,}317{,}358.
   \]

   This kills an \(L=1\) normal form, not the truncated Gate (T). The later
   C106 audit strengthens it to a cross-channel collision preserving all
   \(2\)-, \(3\)-, and \(5\)-adic valuations and gives the exact coprime-swap
   normal form for every collision.

Thus Gates (A) and (T) themselves remain open. A proof of (A) must verify a
genuinely rank-one orbit statistic, or an equivalent square-root support
gain, rather than appeal only to concatenation. A proof of (T) may use
bounded swap degree, but cannot recover factors from literal uniqueness,
scale, or valuations at the generating primes.

The earlier frozen-orbit computation gives a separate exact obstruction to
the most direct residue-refined overlap mechanism.

Let \(B\) be the least set containing \(2,3,5\) and closed under the licensed
maps

\[
T_d(x)=dx-1,\qquad d\in\{2,3,5\},\qquad x\ne d.
\]

For \(X=10^9\), inside the single ambient cell \(23\bmod 30\), the actual
orbit images \(T_2(B)\) and \(T_3(B)\) have positive rather than negative
correlation:

\[
\begin{aligned}
H&=\#\{n\le X:n\equiv23\pmod {30}\}=33{,}333{,}333,\\
|I_2|&=6{,}687{,}748,\qquad |I_3|=2{,}429{,}884,\\
|I_2\cap I_3|&=607{,}421,
\end{aligned}
\]

and exactly

\[
H|I_2\cap I_3|-|I_2||I_3|
=3{,}996{,}914{,}602{,}961>0.                         \tag{1}
\]

The local correlation ratio is

\[
\frac{H|I_2\cap I_3|}{|I_2||I_3|}
=\frac{20247366464193}{16250451861232}
=1.245957136274854\ldots.                              \tag{2}
\]

Thus a proof cannot replace globally disjoint residue images by a fixed
congruence refinement and a cellwise ambient negative-correlation estimate.
The counterexample uses only members of the positive orbit, not intersections
of whole arithmetic progressions.

An aggregate negative-correlation inequality remains alive: after its last
small exception at \(X=4103\), it passes every cutoff through \(10^{10}\).
That finite fact is not an asymptotic proof. Any successful continuation must
control cancellation between residue cells or use a genuinely nonlocal
overlap theorem.

Code:
[`C100_overlap_scan.cpp`](../../compute/wave5/C100_overlap_scan.cpp) and
[`C100_overlap_verify.py`](../../compute/wave5/C100_overlap_verify.py).

## 1. Exact orbit and collision notation

Put

\[
C(X)=|B\cap[1,X]|,\qquad M_d(X)=\left\lfloor\frac{X+1}{d}\right\rfloor.
\]

For \(X\ge24\), define the three licensed child images

\[
I_d(X)=\{dx-1\le X:x\in B,\ x\ne d\},
\qquad A_d(X)=|I_d(X)|=C(M_d(X))-1.                    \tag{3}
\]

Their pair intersections are

\[
\begin{aligned}
P_{23}(X)&=\#\{t\le(X+1)/6:2t,3t\in B\},\\
P_{25}(X)&=\#\{t\le(X+1)/10:2t,5t\in B\},\\
P_{35}(X)&=\#\{t\le(X+1)/15:3t,5t\in B\}.
\end{aligned}                                         \tag{4}
\]

If \(P_{235}\) is the triple intersection, inclusion-exclusion gives

\[
C(X)=C(M_2)+C(M_3)+C(M_5)-1-\Delta(X),                \tag{5}
\]

\[
\Delta=P_{23}+P_{25}+P_{35}-P_{235}.                  \tag{6}
\]

All quantities in the computation are evaluated from the exact Boolean
parent recurrence. No word, orbit point, parent, or cutoff is sampled.

## 2. A quadratic orbit-overlap lemma

The following explains why an ambient pair-correlation estimate is a
load-bearing target rather than a numerical curiosity.

**Lemma 1 (quadratic collision bootstrap).** Suppose that for constants
\(K<\infty\) and \(X_0\ge24\),

\[
X\Delta(X)\le K C(X)^2\qquad(X\ge X_0).                \tag{7}
\]

Then \(B\) has positive lower density. More precisely, with

\[
c=\min\left\{
\min_{5\le Y<X_0}\frac{C(Y)-1/2}{Y+1},\,
\frac1{45K}
\right\}>0,                                            \tag{8}
\]

one has

\[
C(X)-\frac12\ge c(X+1)\qquad(X\ge5).                   \tag{9}
\]

**Proof.**
Set \(F=C-1/2\) and \(S=1/2+1/3+1/5=31/30\). Equation (5) becomes

\[
F(X)+\Delta(X)=F(M_2)+F(M_3)+F(M_5).                  \tag{10}
\]

Use strong induction, with (8) as the finite base. If (9) holds below
\(X\), then

\[
\sum_dF(M_d)\ge c\sum_d(M_d+1)\ge cS(X+1).             \tag{11}
\]

Suppose, for a contradiction, that \(q=F(X)/(X+1)<c\). Since \(X\ge24\)
and \(C(X)\ge3\), one has \(C(X)\le(6/5)F(X)\). Equations (7), (10), and
\((X+1)/X\le25/24\) give

\[
cS\le q+\frac{K C(X)^2}{X(X+1)}
\le q+\frac32Kq^2.                                    \tag{12}
\]

But \(q<c\le1/(45K)\), so

\[
q+\frac32Kq^2<q\left(1+\frac1{30}\right)=Sq<Sc,
\]

contradicting (12). This proves the induction and the lemma. \(\square\)

Consider the aggregate ambient negative-correlation gates

\[
\boxed{\,XP_{ij}(X)\le A_i(X)A_j(X)\,},\qquad
ij\in\{23,25,35\}.                                    \tag{NC}
\]

If all three hold eventually, then \(A_d(X)\le C(X)\) and

\[
\Delta(X)\le\sum_{ij}P_{ij}(X)\le\frac{3C(X)^2}{X}.    \tag{13}
\]

Lemma 1 applies with \(K=3\). Thus an eventual proof of (NC) would prove

\[
\underline d(B)\ge
\min\left\{\min_{5\le Y<X_0}\frac{C(Y)-1/2}{Y+1},\frac1{135}\right\}>0.
\tag{14}
\]

This argument uses actual orbit overlaps and no disjoint residue classes.

## 3. Exact all-cutoff gate

The scanner tested (NC) after every integer cutoff, using 128-bit
cross-products. The complete results through \(10^{10}\) are:

| pair | failures | first failure | last failure | largest positive excess |
|---:|---:|---:|---:|---:|
| \(23\) | 107 | 24 | 130 | 36 at \(X=76\) |
| \(25\) | 2,945 | 24 | 4,103 | 4,193 at \(X=3,853\) |
| \(35\) | 319 | 24 | 383 | 91 at \(X=203\) |

Consequently, all three gates hold at every

\[
4104\le X\le10^{10}.                                   \tag{15}
\]

The weaker direct consequence

\[
X\Delta(X)\le3C(X)^2                                  \tag{16}
\]

has no failure at any tested \(24\le X\le10^{10}\).

At the endpoint,

\[
\begin{aligned}
C(10^{10})&=1{,}849{,}014{,}105,\\
(A_2,A_3,A_5)&=(928{,}854{,}714,\ 620{,}716{,}978,\
373{,}804{,}719),\\
(P_{23},P_{25},P_{35})&=(30{,}224{,}698,\ 27{,}715{,}788,\
16{,}466{,}778).
\end{aligned}
\]

The three endpoint ratios \(XP_{ij}/(A_iA_j)\) are respectively

\[
0.5242284133\ldots,\quad
0.7982421594\ldots,\quad
0.7096925174\ldots.
\]

They increase from \(10^8\) to \(10^{10}\); no monotonicity or limiting
claim is inferred.

## 4. Residue-local counterexample

For a modulus \(q\), residue \(r\), and pair \(ij\), the natural cellwise
replacement for disjoint decoding is

\[
H_{q,r}(X)\,
|I_i(X)\cap I_j(X)\cap(r\bmod q)|
\le
|I_i(X)\cap(r\bmod q)|\,|I_j(X)\cap(r\bmod q)|,         \tag{LNC}
\]

where \(H_{q,r}(X)=|\{n\le X:n\equiv r\pmod q\}|\).

Equation (1) is an exact counterexample to (LNC) for

\[
(q,r,ij,X)=(30,23,23,10^9).                            \tag{17}
\]

The same cell already fails at \(X=2{,}000{,}000\):

\[
(H,|I_2|,|I_3|,|I_2\cap I_3|)
=(66{,}666,14{,}092,5{,}091,1{,}306),
\]

with cross-product excess \(15{,}323{,}424\). An independent Python
implementation reproduces every one of these small-range integers.

This obstruction is quantitative and orbit-relative. It differs from B03:
B03 uses intersections of whole two-sided residue classes to rule out global
unique decoding, whereas (17) concerns the finite positive orbit itself and
allows overlap. It also differs from the C18 witness at \(t=547\): (17)
falsifies a normalized correlation inequality, not merely branch
disjointness.

## 5. Boundary

The counterexample kills the following mechanism:

1. refine the orbit into fixed congruence cells;
2. bound every pair overlap in each cell by the product of its two local
   image densities;
3. sum the cell estimates to obtain a critical renewal.

It does **not** falsify the aggregate gate (NC), a nonlocal covariance
estimate, a scale-dependent partition whose positive local covariances are
explicitly compensated, or positive density of \(B\) itself.

The computation through \(10^{10}\) cannot verify an eventual hypothesis.
Accordingly Lemma 1 is not a positive-density result for \(B\); its unproved
hypothesis is exactly (7), with (NC) as one sufficient route.

The 23-multiplier enlargement was not used. The obstruction and the surviving
gate already occur in the required frozen \(\{2,3,5\}\) subsystem.

## 6. C102 support reduction

Use C102's notation for a fixed ray \((a,b,c)\), slope
\(Q=2^a3^b5^c\), offset supports \(D_k\), and majority-color sizes \(s_k\).
Put

\[
d_k=|D_k|,\qquad a_k=\frac{d_k}{Q^k}.
\]

C29's concatenation injection and C102's majority choice give exactly

\[
a_{m+n}\ge a_ma_n,\qquad \frac{d_k}{2}\le s_k\le d_k.              \tag{18}
\]

Consequently C102's averaged mass satisfies

\[
\frac14\sum_{i\in I_K}a_i a_{K-i}
\le \frac{N_K}{Q^K}
\le \sum_{i\in I_K}a_i a_{K-i}.                                  \tag{19}
\]

The lower inequality shows why a pointwise bound
\(a_k\gg k^{-1/2}\) proves Gate (A). It does not make that pointwise bound a
consequence of supermultiplicativity: \(a_k=(k+1)^{-1}\) is already
supermultiplicative and its central convolution tends to zero.

## 7. Exact scalar obstruction to Gate A

The preceding toy sequence can be made integer-valued and made to match all
five exact `(3,2,1)` support values. Set \(Q=360\), retain

\[
(d_1,\ldots,d_5)
=(60,13068,3542949,1054111467,330159210305),                       \tag{20}
\]

and, for \(k\ge6\), define

\[
d_k=\left\lfloor\frac{5\,360^k}{k+100}\right\rfloor.              \tag{21}
\]

For the selected sizes retain C102's measured values

\[
(s_1,s_2,s_3)=(36,7779,2111340),                                  \tag{22}
\]

and put \(s_k=d_k\) thereafter. These choices satisfy
\(d_k/2\le s_k\le d_k\).

**Lemma 2 (finite-data supermultiplicative countermodel).** The integers
in (20)-(21) satisfy

\[
d_{m+n}\ge d_md_n\qquad(m,n\ge1),                                \tag{23}
\]

but the resulting C102 central mass obeys

\[
\frac{N_K}{360^K}
\le\frac{225(K+1)}{(K+300)^2}\longrightarrow0.                    \tag{24}
\]

**Proof.** All prefix-prefix cases with sum at most five are the actual
concatenation inequalities, and the remaining finitely many prefix-prefix
cases were checked exactly. If \(m\le5\) and \(n\ge6\), then

\[
\frac{d_m}{360^m}
\le\frac{n+100}{m+n+100};                                         \tag{25}
\]

the right side is smallest at \(n=6\), where every case has a strict exact
margin. For \(m,n\ge6\),

\[
(m+100)(n+100)\ge5(m+n+100),                                      \tag{26}
\]

whose minimum margin on this quadrant is \(10676\), at \((6,6)\).
Equations (25)-(26) prove the unfloored density inequality. Since
\(d_md_n\) is an integer bounded by the unfloored target for \(d_{m+n}\), it
is bounded by its floor, proving (23).

For \(K\ge18\), every central index is at least six. Hence

\[
\frac{N_K}{360^K}
\le\sum_{i\in I_K}
\frac{25}{(i+100)(K-i+100)}
\le\frac{225(K+1)}{(K+300)^2},
\]

which proves (24). \(\square\)

This is a scalar countermodel, not a claim about the actual affine supports.
It proves that the known exact values, capacity \(d_k\le Q^k\), majority
bound, and concatenation supermultiplicativity cannot establish Gate (A).
Its normalized supports are decreasing, including across \(k=5\) to \(k=6\).

There is also a set-level version. Label the \(360\) base-\(360\) digits by
five equal classes carrying increments

\[
(0,0),(1,0),(-1,0),(0,1),(0,-1).
\]

Let \({\cal L}_k\) be the length-\(k\) digit strings whose increment sum is
zero. Then \({\cal L}_m{\cal L}_n\subseteq{\cal L}_{m+n}\), exactly the
base-\(Q\) concatenation law behind (18). If
\(\ell_k=|{\cal L}_k|\), the Fourier formula for the lazy planar walk has
characteristic function

\[
\phi(x,y)=\frac{1+2\cos x+2\cos y}{5}.
\]

The only point with \(|\phi|=1\) is the origin; near it
\(|\phi(x,y)|\le e^{-c(x^2+y^2)}\), and off a fixed neighborhood
\(|\phi|\le\rho<1\). Integrating \(|\phi|^k\) gives

\[
\frac{\ell_k}{360^k}=O(k^{-1}).                                  \tag{27}
\]

Its central convolution is therefore \(O(K^{-1})\). Thus even a concrete
graded concatenation-closed offset language can have a rank-two renewal law
and fail (A). The missing hypothesis is precisely a rank-one return or
square-root gain, and it must be proved from the affine collision geometry.

## 8. Tensor collision falsifies the max-fiber renewal

In frozen notation, direct affine composition gives

\[
T_{322255}(x)=T_{255232}(x)=600x-381.                              \tag{28}
\]

Both words have count vector \((3,1,2)\). For a canonical block parameter
\(k\), concatenate \(3k\) independently chosen copies of either side of
(28), then append a common word with \(6k\) letters `2` and \(7k\) letters
`3`. The resulting words are distinct, have count vector

\[
(9k,3k,6k)+(6k,7k,0)=(15k,10k,6k),                               \tag{29}
\]

and evaluate to one affine map. Fixed block length makes the binary block
encoding injective, so this one fiber has at least

\[
2^{3k}=8^k                                                        \tag{30}
\]

words.

C29's proposed local-limit estimate `(LL)` would imply, for some fixed
\(C_0\), that every such fiber is at most

\[
C_0\frac{(31/30)^{31k}}{\sqrt{k}}.                                \tag{31}
\]

But the exact integer comparison is

\[
8\cdot30^{31}
=49413871702715760000000000000000000000000000000
>
31^{31}
=17069174130723235958610643029059314756044734431.                 \tag{32}
\]

Thus (30)/(31) grows as
\(2.8949187186376224^k\sqrt{k}/C_0\), and `(LL)` is false for every
constant \(C_0\). This is an actual affine-orbit collision cube, not an
abstract sequence.

The obstruction does not falsify C102 Gate (A): all \(8^k\) words collapse
to one member of \(D_k\), and Gate (A) starts after that quotient. It does
falsify any proof of (A) based on a uniform max-fiber estimate at the C29
critical scale, or on a renewal theorem that treats overlap clusters as
non-tensoring.

## 9. Gate T after the C106 collision classification

C102's crude intervals give a useful exact first classification. If the
left color is \(2\), every product in channel \(i\) lies between
\(384Q^K\) and \(486Q^K\). If the left color is \(0\), it lies between
\(768Q^K\) and \(972Q^K\). Hence two equal C102 products must use left
layers with the same majority color. This removes all cross-color
collisions without globally disjoint residue classes.

The scale channel itself is not a normal form. In the `(2,1,1)` ray at
\(K=4,i=2\), the four factors in the verdict factor as

\[
\begin{aligned}
58401&=81\cdot721,&90158&=122\cdot739,\\
59859&=81\cdot739,&87962&=122\cdot721.
\end{aligned}                                                     \tag{33}
\]

Thus the collision is an exact coprime-factor swap inside one channel. The
C100 witness extractor independently recovers all five double collisions in
that layer while importing C102's offset generator.

[C106](C106_C102_redteam.md), which landed during this audit, gives the
stronger and complete classification. For any collision \(uv=u'v'\), put

\[
g=(u,u'),\qquad a=u/g,\qquad b=u'/g.
\]

Then \((a,b)=1\), and there is a unique \(c\) such that

\[
u=ga,\qquad u'=gb,\qquad v=bc,\qquad v'=ac.                         \tag{34}
\]

Conversely, every quadruple satisfying (34) and the four layer-membership
conditions is a collision. C106 also gives the exact cross-channel witness

\[
57987\cdot5224910
=3475701\cdot87170
=302976856170,                                                       \tag{35}
\]

from channels \(U_2\times V_3\) and \(U_3\times V_2\). The two left factors
have the same \((v_2,v_3,v_5)=(0,2,0)\), and the two right factors have the
same \((v_2,v_3,v_5)=(1,0,1)\). Therefore neither magnitude nor any
combination of generating-prime valuations recovers the channel.

The surviving exact formulation of Gate (T) is bounded-degree mass in this
coprime-swap graph: a labelled edge is light exactly when it has at most
\(L-1\) nontrivial admissible swaps. C106 finds no asymptotic counterexample;
at the first three-channel block, \(K=6\), exactly
\(307691821/307692465\) edges have multiplicity at most two. This remains
finite evidence, not a proof of (T).

## 10. Reproduction

From the repository root:

```powershell
g++ -O3 -march=native -fopenmp -std=c++20 -Wall -Wextra -Wconversion -Wshadow problems/424/compute/wave5/C100_overlap_scan.cpp -o problems/424/compute/wave5/C100_overlap_scan.exe
problems/424/compute/wave5/C100_overlap_scan.exe 2000000 problems/424/compute/wave5/C100_overlap_scan_2e6.json 8
python problems/424/compute/wave5/C100_overlap_verify.py problems/424/compute/wave5/C100_overlap_scan_2e6.json
problems/424/compute/wave5/C100_overlap_scan.exe 1000000000 problems/424/compute/wave5/C100_overlap_scan_1e9.json 32
```

The hardened \(10^{10}\) run used the same executable and 32 workers. Its
generation and exhaustive audit times were 1.431781 and 73.540532 seconds.

The C102-facing obstructions reproduce with:

```powershell
python problems/424/compute/wave5/C100_c102_support_gate_obstruction.py --output problems/424/compute/wave5/C100_c102_support_gate_obstruction.json --finite-check 200
python problems/424/compute/wave5/C100_tensor_collision_verify.py --output problems/424/compute/wave5/C100_tensor_collision_verify.json --max-k 5
python problems/424/compute/wave5/C100_c102_collision_classify.py --output problems/424/compute/wave5/C100_c102_collision_classify.json
```

Normal and `python -O` outputs are byte-identical for the support and tensor
verifiers. SHA-256 values are:

```text
3B1A021F4C5662B23158EF894EAF0DDFBBCC352D9185FCF29751170CBDF23220  C100_c102_support_gate_obstruction.py
D815C9C4DE83387ACE89428848CF4B8017E987619EBFE82F8CB31FC048AE299E  C100_c102_support_gate_obstruction.json
04C9CDBD57EB614DFD48A09F0961797D0E51F3E073AD691870C4C300F0780D99  C100_tensor_collision_verify.py
2423283DBB3E56A482D4167C7E765B61F0123F5BB2C303C6FD336EC3F4DC19E1  C100_tensor_collision_verify.json
A36820EF5AAC353D511A5EFA59CD2D5E1EA21A6F2D42D4E16397A29DC944BC34  C100_c102_collision_classify.py
5AC5F80A27963E6D2C4D0040E6626FC10AA2CDA7DA029A7F99AF9ACB723A6820  C100_c102_collision_classify.json
```
