# P110: weighted-relation falsifier and strict-label filtration

## Verdict

The P103 weighted relation lemma and equation (14) are false.  The failure is
already forced by dimension: an endpoint-normalized integer Sidon system has

\[
 (p,h,C_S,T_F)=(104,9821,579,1104),
 \qquad T_F-(C_S+4p)=109.                              \tag{1}
\]

Thus its 1,104 vectors `W_tau` lie in a space of dimension only 995 and
cannot be independent over any field.  This row has positive defect 6,352,
but `(V_1,V_2)=(314,315)`, so it does not satisfy a literal hole.

The P105 parity lift `B -> 2B+1`, `h -> 2h` preserves folds, loose
triangles, and the dimension deficit while making `V_1=0`.  It gives the
literal-hole counterexample

\[
 (p,h,C_S,T_F,V_1,\delta)=(104,19642,579,1104,0,-3469). \tag{2}
\]

Hence the weighted lemma is false even under the literal hole, but (2) has
negative defect and does not falsify the positive-defect literal-hole
frontier needed by P82.

The requested strict-label filtration survives this attack.  Partitioning
triangles according to which of their three fold labels is least gives
three classes.  On all 20 direct dimension falsifiers, all 60 class matrices
have full weighted row rank, including fibers with eight triangles sharing
one minimum fold.  This is an exact finite gate, not a proof.

## 1. Smallest and strongest direct falsifiers

The set in (1) is

```text
B={0,25,77,81,121,225,259,317,522,820,831,898,944,972,
1153,1260,1350,1388,1633,1688,1708,1753,1926,2172,2270,
2312,2712,2717,2719,2929,3108,3172,3223,3235,3328,3352,
3554,3604,3886,4022,4152,4313,4373,4550,4634,4725,4744,
5059,5158,5219,5252,5366,5533,5829,5838,5851,5886,6100,
6108,6231,6307,6796,6876,6912,6961,6984,7063,7095,7296,
7327,7422,7525,7554,7568,7607,7637,7893,7910,8011,8197,
8265,8319,8408,8481,8567,8614,8655,8673,8676,8818,8844,
8845,8915,9002,9068,9168,9205,9381,9396,9535,9545,9551,
9670,9820}.
```

Its comma-separated SHA-256 is

```text
078af682f632957904e896735f4c25c54445feb1659cc7cc75c50b07107aca89
```

All `104*105/2` unordered sums and all `104*103/2` positive differences
are distinct, and `max(B)=9820=h-1`.  Independent reconstruction gives 579
folds and 1,104 loose triangles.  Their minimum-label class sizes are

\[
                         (469,384,251).                 \tag{3}
\]

The strongest archived row has

\[
 (p,h,C_S,T_F)=(168,27262,1159,2696),
 \qquad T_F-(C_S+4p)=865.                              \tag{4}
\]

Its SHA-256 is

```text
ba2dd01f79fa2c47023f93203dd45adee0973dfc5b3b2645dc79437f60aeea3e
```

It has positive defect 14,991, class sizes `(1100,917,679)`, and maximum
same-minimum-fold multiplicity seven.  Its parity lift has `V_1=0` and the
same 865-dimensional failure, but defect `-12271`.

An exact census of all 2,526 distinct oriented endpoint rulers loaded by
P86 finds 20 failures of `T_F<=C_S+4p`.  Therefore the direct weighted
lemma is not a near miss confined to one orientation.

## 2. P98 and P105 falsifier gates

Before the P86 failure was found, the weighted vectors were checked on the
following broader generated systems.  Rank was computed modulo 1,000,003;
full rank modulo this prime certifies rational independence.

| domain | systems | support dependent | dependent after `L1,L2` | weighted failures |
|---|---:|---:|---:|---:|
| embedded P98/P105 retained rows | 50 | 15 | 11 | 0 |
| all normalized P98 parent subsets | 261,836 | 16 | 0 | 0 |
| P94/P98 endpoint deletions of size one or two | 5,356 | 5,311 | 2,926 | 0 |
| P105 positive-defect source translations | 1,560 | 308 | 7 | 0 |
| P105 endpoint deletions through size three | 29,316 | 14,928 | 4,089 | 0 |

The P98 subset systems include 2,800 rows with loose triangles.  The P105
deletion lane contains a triangle on every tested row.  These zero-failure
counts explain why P103's initial gate passed, but they do not survive the
denser P86 endpoint systems.

## 3. Strict fold-label filtration

For a P83 triangle write its supporting fold labels as

\[
                 \ell_0=d,\qquad \ell_Z=d+Z,
                 \qquad \ell_X=d+X.                   \tag{5}
\]

They are distinct, but P83 only proves `X,Z != 0`; it does not prove
`d<d+X,d+Z`.  There is nevertheless a unique least label.  Partition the
triangles into three classes according as the least fold is `F_0`, `F_Z`,
or `F_X`.  In each class cyclically reorient the three folds as
`(F,G,H)` so that

\[
                       \ell(F)<\ell(G),\ell(H).         \tag{6}
\]

Put

\[
 A_\tau=q(G)-q(H),\qquad B_\tau=q(F)-q(G),
 \qquad m_\tau=\ell(F),                                \tag{7}
\]

and define the filtered vector

\[
 W^\min_\tau=(e_F+e_G+e_H,A_\tau,B_\tau,
               m_\tau A_\tau,m_\tau B_\tau).          \tag{8}
\]

Changing the cyclic difference basis in (7) is an invertible fixed change
of the two relation blocks in each class.  Thus (8) is the reoriented form
of the P103 construction with the genuinely least phase as weight.

### Filtered weighted lemma (open)

Within each of the three minimum-label classes, the vectors (8) are
linearly independent over `Q`.

If true, the three separate dimension counts give

\[
             T_F\le 3C_S+12p=O(p^2),                  \tag{9}
\]

which is already enough to close P82.2.  The 20 direct falsifiers give 60
class tests.  Among them, support incidence fails 33 times and the
unweighted relation matrix fails 23 times, while both the original P103
weight and the minimum-label weight have zero failures.  Maximum same-base
multiplicity is eight.

## 4. Same-base fiber lemma

The triangular route cannot assume one triangle per base fold.  The
following exact lemma handles arbitrary multiplicity.

### Lemma P110.1

Fix an `F_0`-minimum base fold `F_0=(a,c,r,s)`.  Let `tau_i` be any distinct
loose triangles in this class having base `F_0`, and let

\[
             F_{Z,i}=(a,z_i,u_i,w_i),\qquad
             L_{2,i}=q(F_0)-q(F_{Z,i}).                \tag{10}
\]

Then the vectors `(e_{F_0},L_{2,i})` are linearly independent.  Equivalently,
if

\[
              \sum_i\lambda_i=0,qquad
              \sum_i\lambda_iL_{2,i}=0,               \tag{11}
\]

then every `lambda_i` is zero.

### Proof

The marks `z_i` are distinct: `(a,z_i)` fixes `F_{Z,i}`, and together with
the fixed base fold it fixes the triangle.  From (10)--(11),

\[
 0=-\sum_i\lambda_iq(F_{Z,i})
   =-\sum_i\lambda_i(e_{z_i}-e_{u_i}-e_{w_i}),         \tag{12}
\]

because the common `e_a` term cancels.  If a coefficient is nonzero, choose
the least `z_i` among its active indices.  Canonical fold order gives
`a<=z_i<u_i<=w_i`.  No active column with larger `z` can have `z_i` as a
high mark, and there is no active column with smaller `z`.  Hence the
coefficient of `e_{z_i}` in (12) is exactly `-lambda_i`, a contradiction.
QED.

The other two minimum roles are identical after cyclic reorientation.  For
a fixed `F_Z`, use the varying low mark `c_i` in
`F_{0,i}=(a,c_i,r_i,s_i)`.  For a fixed `F_X`, use the varying low mark
`a_i` in `F_{0,i}=(a_i,c,r_i,s_i)`; all corresponding high marks exceed
the common `c`.  Thus P110.1 handles every same-base fiber and does not use
a multiplicity bound.

P110.1 does not finish the filtered lemma.  In a global dependence, the row
of the least active base fold gives the first equation in (11), but the
mark-relation equations give only sums over all later base fibers and their
first phase moments.  They do not separately give the second equation in
(11) for the least fiber.  Isolating that fiber, or constructing a balanced
cross-fiber trade that survives the first moment, is the remaining exact
triangular frontier.

## 5. Reproduction and claim boundary

Run

```powershell
python -m py_compile `
  problems/864/compute/p110/audit_weighted_frontier.py `
  problems/864/compute/p110/census_dimension_falsifiers.py `
  problems/864/compute/p110/audit_filtered_classes.py `
  problems/864/compute/p110/verify_dimension_falsifier.py
python -B problems/864/compute/p110/audit_weighted_frontier.py `
  --workers 16 `
  --domains embedded p98_subsets p94_deletions p105_translations p105_deletions `
  --output problems/864/compute/p110/generated_gate.json
python -B problems/864/compute/p110/census_dimension_falsifiers.py `
  --output problems/864/compute/p110/dimension_falsifiers.json
python -B problems/864/compute/p110/audit_filtered_classes.py `
  --workers 16 `
  --input problems/864/compute/p110/dimension_falsifiers.json `
  --output problems/864/compute/p110/filtered_classes.json
python -B problems/864/compute/p110/verify_dimension_falsifier.py `
  --input problems/864/compute/p110/dimension_falsifiers.json `
  --output problems/864/compute/p110/verification.json
```

The proved outputs are the direct dimension falsifiers (1)--(4), their
literal-hole parity lifts, and the arbitrary-multiplicity fiber lemma
P110.1.  The filtered weighted lemma, (9), the positive-defect literal-hole
weighted bound, and the P82 conclusion remain unproved.
