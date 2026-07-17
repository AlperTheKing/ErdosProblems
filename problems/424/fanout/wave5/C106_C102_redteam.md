# C106: exact red-team of the C102 scale-varying decoder

## Verdict

C102 Theorem 1 is correct, including its distinct-input condition, color
separation, scale bounds, and lower-density constant.  I found no
counterexample to the truncated-multiplicity gate (T).

The collision geometry does, however, rule out the simplest proposed proof
mechanisms.  Cross-scale collisions already occur at `K=5`, and one such
collision preserves the complete `2`-, `3`-, and `5`-adic valuation vector of
each factor.  Thus neither magnitude nor valuations at the generating primes
recover the channel.  The exact replacement is a coprime factor-swap count
given below.

The exact census was extended to the first three-channel block, `K=6`, with
`307,692,465` labelled edges.  Exactly `307,691,821` of these edges lie in
fibres of multiplicity at most two.  This is finite evidence only; (T) remains
unproved.

## 1. Verification of C102 Theorem 1

Let `G` be generated from `2,3` under `xy-1` for distinct inputs.  First,

\[
  5=2\cdot3-1,\qquad 9=2\cdot5-1,
\]

so `2,3,5,9` belong to `G`.  In the coordinate `t=x-1`, multiplication of a
current value `x>5` by `m in {2,3,5}` is legal and gives

\[
 t\longmapsto mt+(m-2),
\]

which is exactly `L_2,L_3,L_5` in C102.  Hence every value in `H_k` is in
`G`; every intermediate value is greater than five, so no use of a seed
multiplier violates distinctness.

The residue classes `0,2 (mod 3)` are closed under `xy-1`, and contain both
seeds.  Therefore every `H_k` value is in one of those two classes and the
majority class `C_k` has size at least `|D_k|/2`.

For `h in C_k`, all operations defining `U_k,V_k` are legal.  Directly,

\[
 U_k\subset 3\mathbb N,\qquad V_k\subset 3\mathbb N+2.
\]

Thus the two final inputs in every edge are distinct, even when the two scale
indices coincide.

There is a useful sharp version of the crude scale calculation.  If a word
has multiplier product `P>=2`, its offset satisfies

\[
 0\le d\le P-2.                                           \tag{1}
\]

This follows by induction from `2d`, `3d+1`, and `5d+3`, including each
one-letter base case.  Consequently

\[
 8Q^k+1\le h\le9Q^k-1.                                  \tag{2}
\]

If the selected residue is two, then

\[
 16Q^k+1\le u\le18Q^k-3;
\]

if it is zero, then

\[
 32Q^k+1\le u\le36Q^k-7.
\]

In both cases

\[
 24Q^k+2\le v\le27Q^k-4.                                \tag{3}
\]

This proves the advertised upper bounds and puts every product in
`E_K` below `972Q^K`.

The remaining density argument has no overlap or quantifier gap.  If (A) and
(T) hold, then the number of retained products in block `K` is at least

\[
 {1\over L}\sum_{r_K(z)\le L}r_K(z)
 \ge {c_0\eta\over L}Q^K.                               \tag{4}
\]

For every sufficiently large `X`, choose `K>=K_0` with

\[
 972Q^K\le X<972Q^{K+1}.
\]

The single block in (4) is contained in `[1,X]`, so its density there is
strictly greater than `c_0 eta/(972LQ)`.  Taking the lower limit proves C102
(10).

The four reported C102 hashes match the files, and both supplied replays are
byte-identical to their originals.

## 2. Exact collision normal form

Consider two different representations in the same total block:

\[
 (i,u,v),\quad (j,u',v'),\qquad uv=u'v'.
\]

Put

\[
 g=(u,u'),\qquad a=u/g,\qquad b=u'/g.
\]

Then `(a,b)=1`, so Euclid's lemma gives a unique positive integer `c` with

\[
 \boxed{u=ga,\quad u'=gb,\quad v=bc,\quad v'=ac.}        \tag{5}
\]

Conversely, every quadruple in (5) satisfying the four layer-membership
conditions gives a collision.  This is a bijective normal form, not just a
necessary condition.

It has four exact refinements.

1. The product intervals for left color two lie strictly between
   `384Q^K` and `486Q^K`; those for left color zero lie strictly between
   `768Q^K` and `972Q^K`.  Therefore a collision forces the two left layers
   to have the same selected color.

2. If `i>=j`, (2)-(3) imply

\[
 {8\over9}Q^{i-j}\le {a\over b}\le {9\over8}Q^{i-j}.    \tag{6}
\]

   After reversing `a,b`, the same statement holds when `j>i`.

3. Every `v` is prime to three.  Hence

\[
 v_3(u)=v_3(u')=v_3(g),\qquad 3\nmid abc.               \tag{7}
\]

4. A right-layer value is `5 (mod 9)` when its selected `h`-color is two,
   and `8 (mod 9)` when that color is zero.  Thus

\[
 bc\equiv r_{K-i},\qquad ac\equiv r_{K-j}\pmod9,        \tag{8}
\]

   where each `r` is five or eight.  In particular, equal right colors force
   `a=b (mod 9)`.  For a same-channel collision this strengthens (7) to
   `v_3(u-u')>=v_3(u)+2`.

The affine-offset form contains no further automatic cancellation.  Writing
`alpha_i=2` for left color two and `alpha_i=4` for left color zero gives

\[
 u=8\alpha_iQ^i+\alpha_i d+1,
 \qquad v=24Q^{K-i}+3e+2.                               \tag{9}
\]

Substitution of (9) into (5) is an exact finite system in the two reachable
offset sets, but the coprime factors `a,b` are unbounded with `K`.

## 3. Exact obstruction to scale and p-adic decoding

On the `(2,1,1)` ray, `Q=60`, the following is an exact `K=5` collision:

\[
 \boxed{57987\cdot5224910=3475701\cdot87170
       =302976856170.}                                  \tag{10}
\]

The first edge is in `U_2 x V_3` and the second in `U_3 x V_2`.  Its normal
form is

\[
 g=153,\quad c=230,\quad a=379,\quad b=22717.           \tag{11}
\]

Indeed,

\[
\begin{array}{ll}
57987=3^2\cdot17\cdot379,&
3475701=3^2\cdot17\cdot22717,\\
5224910=2\cdot5\cdot23\cdot22717,&
87170=2\cdot5\cdot23\cdot379.
\end{array}
\]

Thus both U-factors have identical `(v_2,v_3,v_5)=(0,2,0)`, and both
V-factors have identical `(v_2,v_3,v_5)=(1,0,1)`, although the scale channel
changes.  The ratio `22717/379` lies in the annulus around `Q=60` from (6).
This disproves channel recovery by magnitude or by any combination of the
three generator-prime valuations.

Within-channel injectivity is false as well; at `K=4`,

\[
 59859\cdot87962=58401\cdot90158=5265317358.             \tag{12}
\]

In the full `K=5` census, there are 1,828 unordered collision pairs: 658 are
within-channel and 1,170 are cross-channel.  Hence the cross-scale issue is
already the majority of the collision count when the second channel first
appears.

## 4. A product-free exact statement of gate (T)

For a labelled edge `e=(i,u,v)`, define its swap degree by

\[
\begin{aligned}
 s_K(e):={}&
 \sum_{j\in I_K}\#\{(a,b):
 a\mid u,\ b\mid v,\ (a,b)=1,\\
 &\hspace{34mm}(u/a)b\in U_j,
 (v/b)a\in V_{K-j}\}-1.                                \tag{13}
\end{aligned}
\]

The subtracted term is `(j,a,b)=(i,1,1)`.  Uniqueness in (5) proves the exact
identity

\[
 \boxed{s_K(i,u,v)=r_K(uv)-1.}                          \tag{14}
\]

Therefore (T) is exactly the following finite statement:

\[
 \boxed{
 \#\{e\in\mathcal E_K:s_K(e)\le L-1\}\ge\eta N_K
 \quad(K\ge K_0).}                                     \tag{T'}
\]

Equations (6)-(8) delete all swaps outside narrow scale annuli and prescribed
congruence classes.  This is the sharp reduced target produced by C106.  It
does not assume the stronger bounded-energy condition.

## 5. First exact three-channel census

The earlier large C102 row `(3,2,1), K=4` has only the channel `i=2`; it does
not test accumulation across scale indices.  C106 computed the `(2,1,1)` ray
at `K=6`, whose channels are `(2,4),(3,3),(4,2)`:

```text
edges                 307692465
support               307498017
histogram             1:307303785, 2:194018, 3:212, 4:2
edge mass with r <= 2 307691821 / 307692465
max multiplicity      4
```

Thus the exact light-edge fraction at cutoff two is

\[
 {307691821\over307692465}=0.99999790700107\ldots.       \tag{15}
\]

Normal and optimized runs are byte-identical.  The calculation uses exact
`uint64` products; the script independently rechecks every structural
normal-form assertion with arbitrary-precision Python integers.

Artifact hashes:

```text
B077BCABAF84572F78392901D27A26AA846AAD0D74BE0B7432B154A79B12E2A6  C106_collision_audit.py
4EA66E327E71B167B1B91EF542DAF3EE31BF32223ED143BE414ECBC93119CB5C  C106_collision_audit.json
4EA66E327E71B167B1B91EF542DAF3EE31BF32223ED143BE414ECBC93119CB5C  C106_collision_audit_O.json
61B63B96F2B12A39A04BBE2F17C1F70892624DFEEF5776CC7087115EBB65FC25  C106_K6_summary.json
61B63B96F2B12A39A04BBE2F17C1F70892624DFEEF5776CC7087115EBB65FC25  C106_K6_summary_O.json
```

Reproduction:

```powershell
python problems/424/compute/wave5/C106_collision_audit.py `
  --output problems/424/compute/wave5/C106_collision_audit.json --k-max 5

python problems/424/compute/wave5/C106_collision_audit.py `
  --output problems/424/compute/wave5/C106_K6_summary.json --summary-K 6
```

## 6. Final assessment

No asymptotic counterfamily to (T) was found.  The `K=6` result strengthens
its finite evidence, but does not prove a uniform `eta,L`.  The proved
normal form shows exactly what remains: control the bounded-degree mass in
the scale-annular coprime-swap graph (13).  Any proof based only on product
size, channel magnitude, or valuations at `2,3,5` is ruled out by (10).
