# P53: shifted sum overlap and the fold-repair incidence gate

Status: **the stated bound is false**.  The smallest falsifier found has
`p=25`.  It is smallest among all endpoint-retaining subsets of the first
26-mark falsifier, but global minimality over all integer rulers is not
claimed.  The optional `3B-B` hole excludes this example.  The direct
`C_4`-free/KST proof of the new scale-repaired inequality also fails; that
inequality remains open.

## 1. Exact interval reformulation

Let

\[
 B\subseteq\{0,\ldots,h-1\},\qquad \max B=h-1,
 \qquad |B|=p,
\]

and suppose that all unordered sums `x+y`, including `x=y`, are distinct.
Write `S=B+B`.  Since `S` is contained in `[0,2h-2]`, every residue modulo
`h` has at most two representatives and hence

\[
 C_S=|\{s\in S:s+h\in S\}|=|S|-|S\bmod h|.              \tag{1}
\]

There is a useful exact graph model for (1).  If

\[
 a+b+h=c+d,\qquad a\leq b,\quad c\leq d,                \tag{2}
\]

then

\[
 c=a+b+h-d\geq a+b+1>b.
\]

Thus every collision has the separated order

\[
                       a\leq b<c\leq d.                 \tag{3}
\]

Moreover,

\[
 c-b=h-d+a,
 \qquad (c-b)+(d-a)=h.                                  \tag{4}
\]

Consequently (2) is a pair of nested intervals

\[
 [b,c]\subseteq[a,d]
\]

whose positive lengths are complementary to `h`.  Conversely every such
complementary nested pair gives (2).

Integer Sidonicity implies that every positive difference has a unique
endpoint pair.  It follows that charging (2) to its central interval `[b,c]`
is injective: `[b,c]` determines `c-b`, then (4) determines `d-a`, and the
unique-difference property determines `[a,d]`.  Hence `C_S` is exactly the
edge count of a simple graph on the ordered marks, with edge `[b,c]` for each
collision.

This reduction does **not** make the graph noncrossing, planar, or
2-degenerate.  The falsifier below has 49 central edges and 304 crossing
edge pairs in mark order.  Thus an outerplanar estimate `e<=2p-3` cannot be
applied to this canonical interval graph.

## 2. Exact 25-mark falsifier

Take

\[
\begin{split}
B=\{&1,2,34,84,105,111,125,164,186,201,204,250,252,259,315,\\
    &344,357,387,431,441,457,465,476,488,493\},
\end{split}                                               \tag{5}
\]

with

\[
                         p=25,\qquad h=494.               \tag{6}
\]

The endpoint condition is exact: `B` is contained in `[0,493]` and
`max B=493=h-1`.  Direct integer enumeration gives

\[
 |S|=325={25\cdot26\over2},
 \qquad |\Delta^+(B)|=300={25\cdot24\over2}.              \tag{7}
\]

Thus all unordered sums, including all 25 diagonal sums, are distinct; all
positive differences are also distinct.  The 49 lower members of the
`h`-shifted sum pairs are

```text
4, 36, 68, 107, 113, 127, 145, 165, 168, 187,
189, 195, 198, 203, 206, 220, 222, 230, 250, 251,
252, 253, 286, 291, 297, 309, 315, 326, 328, 334,
343, 350, 358, 368, 378, 388, 402, 420, 423, 428,
436, 440, 451, 456, 458, 459, 475, 482, 492
```

For every displayed `s`, both `s` and `s+494` have their unique pair labels
in the machine-readable certificate.  Therefore

\[
                       C_S=49>47=2p-3.                   \tag{8}
\]

The 49 collisions comprise 34 off-diagonal/off-diagonal collisions, seven
with a low diagonal, and eight with a high diagonal.  No diagonal was
discarded.  The witness SHA-256 is

```text
a06614ae20bd33558cc54a58ea53604bb40a74965e301bc01e886d514ff6128a
```

and the full certificate is
[counterexample_p25_h494.json](../../compute/p53/counterexample_p25_h494.json).

### Strongest hypotheses actually falsified

The positive-defect condition also holds:

\[
 \delta={3p^2-p+2\over2}-h=926-494=432>0.               \tag{9}
\]

Thus (8) disproves `C_S<=2p-3` under exactly the hypotheses in Section 1,
even after adding positive defect.  It does **not** disprove the stronger
hole-restricted statement.  Indeed

\[
 1+1+201-204=-1,
 \qquad 1+2+488-493=-2,                                  \tag{10}
\]

so both `-1` and `-2` lie in `3B-B`.  No `3B-B` assumption was used to find
or verify (8).  Whether `C_S<=2p-3` follows after imposing
`-b notin 3B-B` remains open.

## 3. Broader-search scope and minimality

All searches use integer decisions.  The verifier constructs every
unordered pair with `i<=j`, aborts on a repeated sum, independently checks
all positive differences, and records every collision label.

1. Exhaustive generation through width 45 checked every normalized Sidon
   ruler and every translation `0<=gamma<width`.  Larger translations have
   `h>2*width` and hence `C_S=0`.  The scan covered 745,733 rulers and
   30,326,669 translations, with no failure.  Its ruler-stream SHA-256 is
   `772e239cc1a5d1a02f7f2d9a63f5e53fab579cb472834c14446d3bd97e2e9e53`.

2. A structurally separate scan used listed dense rulers of orders 20
   through 28, both orientations, and every translation capable of an
   overlap.  The first failure was the 26-mark translated ruler at `h=494`,
   with `C_S=51>49`.

3. Exact CP-SAT optimization over every subset of that 26-mark ruler which
   retains `493` proved that the maximum `C_S` at cardinalities 24, 25, and
   26 is respectively 44, 49, and 51.  Deleting the mark `319` gives (5).
   All cardinality optimizations returned `OPTIMAL`.

The resulting `p=25` witness is therefore the smallest found and is proved
smallest inside this complete induced-subset domain.  It is not a proof that
no unrelated `p<=24` ruler of larger width fails.  An unrestricted fixed
`(p,h)=(24,494)` CP-SAT run did not finish within 300 seconds and produced no
certificate.

The exact artifacts are

* [exhaustive_width45_all_translations.json](../../compute/p53/exhaustive_width45_all_translations.json),
* [dense_optimal_rulers_scan.json](../../compute/p53/dense_optimal_rulers_scan.json),
* [counterexample_subset_minimization.json](../../compute/p53/counterexample_subset_minimization.json), and
* [shifted_sum_overlap.py](../../compute/p53/shifted_sum_overlap.py).

## 4. The scale-repaired fold gate

Put

\[
 C=C_S+C_D,
 \qquad R=\max(\delta-5C,0).                              \tag{11}
\]

The new exact candidate is

\[
                         R^2\leq4p^3.                    \tag{12}
\]

P46's support identity is

\[
 \delta=U_1+U_2+C_{out}-H_0,
 \qquad C_{out}=C-\#both.
\]

Therefore the quantity in (11) has the exact form

\[
 \delta-5C
   =U_1+U_2-H_0-4C-\#both.                               \tag{13}
\]

In particular, the following incidence statement would suffice for (12):

\[
 U_1+U_2
 \leq H_0+4C+\#both+2p^{3/2}.                            \tag{14}
\]

### The direct KST graph

For `k in {1,2}`, let `T_k=kh-b` and form a bipartite graph `G_k` on two
copies of `B` by

\[
 (z,w)\in E(G_k)
 \quad\Longleftrightarrow\quad T_k-(z-w)\in S.           \tag{15}
\]

For a nonzero difference, integer Sidonicity gives a unique ordered pair
`(z,w)`, so (15) is the canonical graph realization of the support carry
pairs.  If these graphs were `C_4`-free after deleting only the correction
terms in (13), a KST estimate would have the desired `p^(3/2)` scale.
Standard balanced KST also carries an additive `O(p)` term, so obtaining the
exact constant in (14) would require a further sharpening even under that
false premise.

This premise is false even at zero modular fold count.  For the exact Bose
profile

```text
p=17, h=288, b=2, gamma=80,
Z={0,7,37,48,52,68,76,101,110,111,123,161,167,188,190,193,207}
```

one has

\[
 C_S=C_D=0,\quad (U_1,U_2)=(94,51),\quad H_0=7,
 \quad R=138,
\]

and hence `R^2/p^3=19044/4913`.  The direct graphs have the following exact
statistics.

| carry | expanded edges | max left codegree | left pairs with codegree >=2 | `C_4` copies | max `C_4`-free edges | min deletions |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 94 | 6 | 93 | 294 | 60 | 34 |
| 2 | 67 | 6 | 26 | 102 | 50 | 17 |

The carry-2 expanded graph has 16 extra edges because the one support value
`d=0` has 17 ordered realizations.  Carry 1 has no such issue:
`|E(G_1)|=U_1=94`, and it alone needs at least 34 deletions to become
`C_4`-free.  The entire deletion budget visible in (13) is only
`H_0+4C+#both=7`.

A literal carry-1 `K_{2,2}` already uses left vertices `80,87` and right
vertices `128,132`.  Its four edges have complementary sum labels

| `(z,w)` | `z-w` | `286-(z-w)` | unique sum pair |
|---|---:|---:|---|
| `(80,128)` | -48 | 334 | `(87,247)` |
| `(80,132)` | -52 | 338 | `(148,190)` |
| `(87,128)` | -41 | 327 | `(80,247)` |
| `(87,132)` | -45 | 331 | `(128,203)` |

The audit also checks all six fixed projections obtained by choosing two of
the low-sum endpoint, high-sum endpoint, difference-left, and
difference-right roles.  Every injective projection still contains a
`K_{2,2}`; the remaining projections lose relations through duplicate
edges.

Thus a **direct** KST proof based on codegree one, or on deleting the explicit
penalty mass and then applying a `C_4`-free bound, does not prove (12).  This
does not falsify (12).  A viable incidence proof would need a new weighted or
global lemma proving (14) without reducing the carry relations to a
`C_4`-free subgraph.  The exact obstruction is preserved in
[kst_bose_p17_audit.json](../../compute/p53/kst_bose_p17_audit.json), generated
by [incidence_kst_audit.py](../../compute/p53/incidence_kst_audit.py).

## 5. Reproduction

```powershell
python -m py_compile problems/864/compute/p53/shifted_sum_overlap.py
python -m py_compile problems/864/compute/p53/incidence_kst_audit.py
python -m py_compile problems/864/compute/p53/verify_p53_artifacts.py

python -B problems/864/compute/p53/shifted_sum_overlap.py verify `
  --h 494 `
  --B 1,2,34,84,105,111,125,164,186,201,204,250,252,259,315,344,357,387,431,441,457,465,476,488,493 `
  --output problems/864/compute/p53/counterexample_p25_h494.json

python -B problems/864/compute/p53/shifted_sum_overlap.py exhaustive `
  --max-width 45 `
  --output problems/864/compute/p53/exhaustive_width45_all_translations.json

python -B problems/864/compute/p53/shifted_sum_overlap.py dense `
  --output problems/864/compute/p53/dense_optimal_rulers_scan.json

python -B problems/864/compute/p53/shifted_sum_overlap.py minimize `
  --h 494 `
  --B 1,2,34,84,105,111,125,164,186,201,204,250,252,259,315,319,344,357,387,431,441,457,465,476,488,493 `
  --seconds 300 --workers 64 `
  --output problems/864/compute/p53/counterexample_subset_minimization.json

python -B problems/864/compute/p53/incidence_kst_audit.py
python -B problems/864/compute/p53/verify_p53_artifacts.py
```
