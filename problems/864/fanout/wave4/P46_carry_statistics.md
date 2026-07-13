# P46: exact carry statistics and falsification study

Status: exact finite study.  No asymptotic conclusion is inferred from the
finite census.

## 1. Objects and conventions

Let

\[
 B\subseteq\{0,\ldots,h-1\},\qquad \max B=h-1,
 \qquad |B|=p,\qquad b\in\{1,2\},
\]

be integer Sidon with diagonal sums retained, and assume

\[
                         -b\notin 3B-B.                 \tag{1}
\]

Write `S=B+B` for the distinct integer sum support and `D=B-B` for the
distinct integer difference support.  Thus

\[
 |S|={p(p+1)\over2},\qquad |D|=p(p-1)+1,
 \qquad |S|+|D|={3p^2-p+2\over2}.                       \tag{2}
\]

Bars denote reduction modulo `h`, and

\[
 I=\bar S\cap(-b-\bar D),\qquad
 H_0=h-|\bar S\cup(-b-\bar D)|.                         \tag{3}
\]

The two modular collision defects are

\[
 C_S=|S|-|\bar S|,\qquad C_D=|D|-|\bar D|.              \tag{4}
\]

Since `S` lies in `[0,2h-2]` and `D` lies in `[-h+1,h-1]`, every modular
fiber has size at most two.  Hence `C_S` and `C_D` are literally the numbers
of sum-collision and difference-collision residues.  The JSON records every
such collision in the 137 P20 profiles, including its two integer values,
pair labels, ordered multiplicities, translated overlap residue, and whether
it lies in `I`.

For `r in I`, let `u_k(r)` count distinct literal support-label pairs
`(s,d)` with

\[
                         s+d=kh-b,\qquad k\in\{1,2\}.
\]

Let `w_k(r)` use the ordered-representation weight

\[
 r_{B+B}(s)r_{B-B}(d).
\]

Integer Sidonicity makes `r_{B+B}(s)` equal to 1 on a diagonal and 2 off a
diagonal; `r_{B-B}(0)=p`, and every nonzero difference has weight 1.  Put

\[
 U_k=\sum_{r\in I}u_k(r),\qquad W_k=\sum_{r\in I}w_k(r). \tag{5}
\]

Thus `W_k` is the exact number of ordered quadruples
`(x,y,z,t) in B^4` satisfying `x+y+z-t=kh-b`.

The recorded signed moments, for `j=0,1,2`, are

\[
 M_j^U=\sum_{r\in I}r^j(u_1(r)-u_2(r)),\qquad
 M_j^W=\sum_{r\in I}r^j(w_1(r)-w_2(r)),                 \tag{6}
\]

and the cut-coordinate versions replace `r^j` by
`(2r-(h-b))^j`.  Carry 1 has positive sign and carry 2 negative sign.

Finally,

\[
                   \delta={3p^2-p+2\over2}-h.           \tag{7}
\]

## 2. Exact enumeration and P44 cross-check

The executable artifact is

```text
problems/864/compute/p46/carry_statistics.py
```

and its exact output is

```text
problems/864/compute/p46/carry_statistics.json
```

The program reconstructed all 137 fully reflected P20 samples and compared
17 legacy P44 fields per row.  All 2,329 comparisons agree; mismatch count
is zero.  P46 then adds the ordered weights, collision records, overlap
collision types, and all signed moments in (6).

The new exhaustive domain is every positive-defect pair `(B,b)` for which
`max(B)-min(B)<=30`.  Completeness is as follows.  Put

\[
 \gamma=\min B,\quad Z=B-\gamma,\quad W=\max Z,
 \quad F=W-Z.
\]

Then `F` is an endpoint-normalized Sidon ruler in `[0,W]`, and

\[
 -b\notin3B-B
 \quad\Longleftrightarrow\quad
 2W+2\gamma+b\notin3F-F.                                \tag{8}
\]

Also `h=gamma+W+1`; the condition `delta>0` is exactly

\[
 0\leq\gamma\leq {3p^2-p+2\over2}-W-2.                 \tag{9}
\]

The recursion enumerates every Sidon `F` by adding a mark only when all new
positive differences are unused, then loops over exactly the two values of
`b` and the full interval (9).  It therefore tests the stated domain without
sampling.

Exact width-30 census:

| quantity | exact count |
|---|---:|
| endpoint-normalized Sidon rulers | 29,952 |
| positive-defect `(F,gamma,b)` candidates | 919,484 |
| candidates satisfying (1) | 464,981 |
| combined unique profiles after adding P20 | 465,086 |
| combined profiles with `delta>0` used in tests | 465,083 |

Admissible enumerated holes by cardinality:

| `p` | 2 | 3 | 4 | 5 | 6 | 7 |
|---:|---:|---:|---:|---:|---:|---:|
| count | 17 | 259 | 5,033 | 87,111 | 325,482 | 47,079 |

The deterministic enumeration certificate SHA-256 stored in the JSON is

```text
cdb251566b96dbe22463b61a24cf7f472b452b425be164c8ef65e6e36268fd6b
```

## 3. Surviving exact identities

### 3.1 Defect identity

Every profile satisfies the identity

\[
 \boxed{\delta=|I|+C_S+C_D-H_0.}                        \tag{10}
\]

This is a proof, not a finite-data conjecture.  From (3),

\[
 |I|-H_0=|\bar S|+|-b-\bar D|-h.
\]

Adding `(4)` and using (2) gives (10).  In particular, the always-valid
inequality

\[
 \boxed{\delta\leq |I|+C_S+C_D}                        \tag{11}
\]

reduces the desired `o(p^2)` conclusion to controlling both the overlap and
the two modular collision defects.  The data do not supply those asymptotic
controls.

### 3.2 Exclusive/both identity

The literal range allows only carries 0, 1, and 2, and (1) removes carry 0.
If both the sum fiber and matching difference fiber collided at one overlap
residue, their four literal totals would have consecutive carry pattern

\[
                         q,\ q+1,\ q+1,\ q+2,
\]

which cannot all belong to `{1,2}`.  Therefore simultaneous sum-and-
difference collisions on an overlap residue are impossible.

A residue with no collision has one literal pair and is exclusive.  A
residue with exactly one collision has two literal pairs differing by `h`,
one at each carry.  If `R_S` and `R_D` count the sum and difference collision
residues lying in `I`, respectively, then

\[
 \boxed{
 U_1=\#\text{only1}+\#\text{both},\quad
 U_2=\#\text{only2}+\#\text{both},\quad
 \#\text{both}=R_S+R_D.}                               \tag{12}
\]

Let `C_out=C_S+C_D-#both`.  Combining (10) and (12) gives the second exact
form

\[
 \boxed{\delta=U_1+U_2+C_{out}-H_0.}                   \tag{13}
\]

All six asserted identities in each JSON profile are checked during
execution; any failure aborts the run.

## 4. Falsification results

Every inequality below was tested on all 465,083 unique positive-defect
profiles.  `U1,U2` are support-label counts and `W1,W2` are the ordered
multiplicity-weighted counts.  The listed witness is the smallest in
lexicographic order `(p,h,b,B,source_id)`.  The last two columns give the
exact failure count and the maximum observed value of `LHS-RHS`; they are
finite-corpus statistics only.

| candidate | smallest exact falsifier | LHS > RHS | failures | max violation (source) |
|---|---|---:|---:|---:|
| `delta <= |I|` | `p=2,h=2,b=2,B={0,1}` | `4 > 2` | 64,060 | 63 (`singer-597b7f1d0a50`) |
| `delta <= U1+U2` | `p=2,h=4,b=1,B={1,3}` | `2 > 0` | 25,040 | 14 (`singer-ba11c5f99fd1`) |
| `delta <= U1` | `p=2,h=2,b=2,B={0,1}` | `4 > 2` | 181,709 | 177 (`bose-bef5be76717b`) |
| `delta <= only1+only2` | `p=2,h=2,b=2,B={0,1}` | `4 > 0` | 117,382 | 126 (`singer-597b7f1d0a50`) |
| `delta <= |U1-U2|` | `p=2,h=2,b=2,B={0,1}` | `4 > 0` | 323,490 | 1,107 (`singer-61ed86e11f2c`) |
| `delta <= both+|U1-U2|` | `p=2,h=2,b=2,B={0,1}` | `4 > 2` | 263,829 | 668 (`singer-30c72c7ef34e`) |
| `p*delta <= |W1-W2|` | `p=2,h=2,b=2,B={0,1}` | `8 > 0` | 412,155 | 796,071 (`singer-442f9f248c7f`) |
| `delta <= C_S+C_D` | `p=2,h=2,b=2,B={0,1}` | `4 > 2` | 355,322 | 3,706 (`singer-442f9f248c7f`) |
| `C_S+C_D <= H_0` | `p=2,h=2,b=2,B={0,1}` | `2 > 0` | 64,060 | 63 (`singer-597b7f1d0a50`) |
| `|I|^2 <= p^3` | `p=2,h=3,b=1,B={0,2}` | `9 > 8` | 152,345 | 97,187,584 (`singer-801ada713888`) |
| `|U1-U2|^2 <= p^3` | `p=2,h=3,b=1,B={0,2}` | `9 > 8` | 1,214 | 28,137,124 (`singer-801ada713888`) |
| `(C_S+C_D)^2 <= p^3` | `p=4,h=14,b=1,B={1,3,9,13}` | `81 > 64` | 60 | 113 (`endpoint-880e26f89ced`) |

The first two scale failures disprove only the displayed unit-constant
inequalities.  They do not disprove `|I|=O(p^(3/2))`,
`|U1-U2|=O(p^(3/2))`, or any other asymptotic statement.

### 4.1 Small collision-only falsifier

The most informative finite witness is

\[
                 p=4,\quad h=14,\quad b=1,
                 \quad B=\{1,3,9,13\}.                 \tag{14}
\]

Its ten unordered sums are

\[
 S=\{2,4,6,10,12,14,16,18,22,26\},
\]

and its six positive differences are

\[
 D^+=\{2,4,6,8,10,12\}.
\]

These lists verify integer Sidonicity, including diagonals.  If `s+d=-1`,
then the magnitude of the negative difference would lie in

\[
 S+1=\{3,5,7,11,13,15,17,19,23,27\},
\]

which is disjoint from `D^+`; hence `-1 notin 3B-B` exactly.

Modulo 14,

\[
 \bar S=\{0,2,4,6,8,10,12\},\qquad
 -1-\bar D=\{1,3,5,7,9,11,13\}.
\]

Thus `I` is empty and `H_0=0`.  There are three sum-collision residues and
six difference-collision residues, so

\[
 \delta=23-14=9=0+3+6-0.
\]

Every carry count and every signed carry moment is zero.  Consequently, an
unconditional defect inequality depending only on carry counts and vanishing
when they vanish is already false at (14).  A collision term or an additive
correction is unavoidable.  This finite example says nothing by itself
about the size of such a correction as `p` tends to infinity.

For a nontrivial small witness with nonempty overlap,

\[
 p=4,\ h=10,\ b=1,\ B=\{2,6,8,9\}
\]

has

\[
 \delta=13,\quad |I|=7,\quad C_S+C_D=6,\quad H_0=0,
 \quad (U_1,U_2)=(6,5),\quad(W_1,W_2)=(10,7).
\]

It simultaneously falsifies `delta<=|I|`, `delta<=U1+U2`,
`delta<=U1`, `delta<=|U1-U2|`, and `delta<=C_S+C_D`.

## 5. Exact finite extrema

All extrema in this section range over the 465,083 unique profiles with
`delta>0`.  Witness IDs resolve to complete `B` lists and collision records
in `carry_statistics.json`; no decimal comparison was used.

### 5.1 Counts

| statistic | minimum (witness) | maximum (witness) |
|---|---|---|
| `delta` | 1 (`enum-W4-F0_4-b1-g0`) | 4,916 (`singer-442f9f248c7f`) |
| `|I|` | 0 (`enum-W2-F0_2-b1-g1`) | 10,096 (`singer-801ada713888`) |
| `C_S` | 0 (`enum-W2-F0_2-b1-g0`) | 256 (`singer-e82f2d6a63ca`) |
| `C_D` | 0 (`enum-W2-F0_2-b1-g0`) | 988 (`singer-e82f2d6a63ca`) |
| `C_S+C_D` | 0 (`enum-W2-F0_2-b1-g0`) | 1,244 (`singer-e82f2d6a63ca`) |
| `H_0` | 0 (`census-e8866fffe77f`) | 6,547 (`singer-801ada713888`) |
| `only1` | 0 (`census-e8866fffe77f`) | 7,622 (`singer-801ada713888`) |
| `only2` | 0 (`census-e8866fffe77f`) | 1,930 (`singer-442f9f248c7f`) |
| `both` | 0 (`enum-W2-F0_2-b1-g0`) | 595 (`singer-e82f2d6a63ca`) |
| `only1+only2` | 0 (`census-e8866fffe77f`) | 9,510 (`singer-801ada713888`) |
| `U1` | 0 (`enum-W2-F0_2-b1-g1`) | 8,208 (`singer-801ada713888`) |
| `U2` | 0 (`enum-W2-F0_2-b1-g0`) | 2,515 (`singer-e82f2d6a63ca`) |
| `U1+U2` | 0 (`enum-W2-F0_2-b1-g1`) | 10,682 (`singer-801ada713888`) |
| `W1` | 0 (`enum-W2-F0_2-b1-g1`) | 16,659 (`singer-801ada713888`) |
| `W2` | 0 (`enum-W2-F0_2-b1-g0`) | 5,074 (`singer-801ada713888`) |
| `W1+W2` | 0 (`enum-W2-F0_2-b1-g1`) | 21,733 (`singer-801ada713888`) |

### 5.2 Signed moments

Here `M` uses the residue coordinate in (6), and `K` uses the cut coordinate
`2r-(h-b)`.

| statistic | exact minimum (witness) | exact maximum (witness) |
|---|---|---|
| `M_0^U` | -15 (`enum-W29-F0_2_3_8_18_25_29-b2-g37`) | 5,734 (`singer-801ada713888`) |
| `M_0^W` | -34 (`enum-W30-F0_1_3_7_12_22_30-b2-g37`) | 11,585 (`singer-801ada713888`) |
| `M_1^U` | -74,154 (`singer-natural-aaccd2fd8048`) | 66,511,163 (`singer-801ada713888`) |
| `M_2^U` | -1,169,728,306 (`singer-natural-aaccd2fd8048`) | 1,564,452,492,699 (`singer-801ada713888`) |
| `M_1^W` | -11,936 (`ruzsa-b303884089ad`) | 138,761,492 (`singer-801ada713888`) |
| `M_2^W` | -94,927,528 (`bose-bef5be76717b`) | 3,353,028,529,948 (`singer-801ada713888`) |
| `K_0^U` | -15 (`enum-W29-F0_2_3_8_18_25_29-b2-g37`) | 5,734 (`singer-801ada713888`) |
| `K_1^U` | -81,882,260 (`singer-801ada713888`) | 262 (`enum-W30-F0_18_23_27_29_30-b2-g15`) |
| `K_2^U` | -35,060 (`enum-W27-F0_1_5_7_15_18_27-b2-g42`) | 4,341,131,437,182 (`singer-801ada713888`) |
| `K_0^W` | -34 (`enum-W30-F0_1_3_7_12_22_30-b2-g37`) | 11,585 (`singer-801ada713888`) |
| `K_1^W` | -158,152,412 (`singer-442f9f248c7f`) | 2,245 (`bose-7db1b84a1ac7`) |
| `K_2^W` | -86,408 (`enum-W30-F0_1_3_7_12_20_30-b2-g39`) | 8,882,711,269,105 (`singer-801ada713888`) |

### 5.3 Exact ratios

| statistic | minimum | maximum |
|---|---:|---:|
| `delta/p^2` | `1/49` | `1` |
| `|I|/p^2` | `0` | `3/4` |
| `(C_S+C_D)/p^2` | `0` | `9/16` |
| `|U1-U2|/p^2` | `0` | `3/4` |
| `|I|^2/p^3` | `0` | `398161/18522` |

These are exact extrema of this finite corpus, not limiting constants.

## 6. The `p=168` P44 record with added statistics

For `singer-801ada713888`,

\[
 p=168,\ h=37481,\ b=2,\ \delta=4772,\ |I|=10096.
\]

The new collision data are

\[
 C_S=253,\quad C_D=970,\quad H_0=6547.
\]

Of the collision residues, 207 sum collisions and 379 difference collisions
lie in the overlap, giving `both=586` exactly.  The residue partition and
carry counts are

\[
 (\text{only1},\text{only2},\text{both})=(7622,1888,586),
\]

\[
 (U_1,U_2)=(8208,2474),\qquad (W_1,W_2)=(16659,5074).
\]

The two defect identities read

\[
 4772=10096+253+970-6547
\]

and

\[
 4772=(8208+2474)+(253+970-586)-6547.
\]

Its residue-coordinate signed moments are

\[
 (M_0^U,M_1^U,M_2^U)
 =(5734,66511163,1564452492699),
\]

\[
 (M_0^W,M_1^W,M_2^W)
 =(11585,138761492,3353028529948).
\]

Its cut-coordinate moments are

\[
 (K_0^U,K_1^U,K_2^U)
 =(5734,-81882260,4341131437182),
\]

\[
 (K_0^W,K_1^W,K_2^W)
 =(11585,-156671231,8882711269105).
\]

## 7. Conclusion and scope

The robust output is (10)-(13), especially

\[
 \delta=|I|+C_S+C_D-H_0.
\]

The finite search falsifies all tested bridges from `delta` to overlap,
exclusive carry count, support signed mass, or ordered signed mass alone.
The collision-only witness (14) shows why: modular collisions can hold the
entire defect while `I`, `U1`, `U2`, `W1`, `W2`, and all signed moments are
zero.

A viable asymptotic carry argument must therefore control the modular
collision defects as well as the carry overlap, or exploit a separate
structure not represented by these counts.  This study neither proves nor
falsifies that any of `|I|`, `C_S+C_D`, or a signed moment is `o(p^2)` along
an infinite family.

## 8. Reproduction

All decisions use integers; there is no floating-point gate.

```powershell
python -m py_compile problems/864/compute/p46/carry_statistics.py
python -B problems/864/compute/p46/carry_statistics.py `
  --max-width 30 `
  --output problems/864/compute/p46/carry_statistics.json
python -c "import json; j=json.load(open('problems/864/compute/p46/carry_statistics.json')); print(j['cross_check'], j['enumeration']['admissible_holes'], j['enumeration']['reports_sha256'])"
```

The full run completed with exit code 0.  Its summary is:

```text
P44 reports checked: 137
legacy field mismatches: 0
Sidon rulers: 29,952
positive-defect candidates: 919,484
admissible holes: 464,981
combined unique profiles: 465,086
enumeration certificate: cdb251566b96dbe22463b61a24cf7f472b452b425be164c8ef65e6e36268fd6b
```
