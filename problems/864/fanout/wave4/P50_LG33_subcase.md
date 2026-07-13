# P50: a noncircular LG33 subcase

## Verdict

**PROVED:** a sharp gap-envelope condition implies (LG33), and the simpler
condition

\[
4Z_H\le 3N
\]

implies (LG33) at the prescribed scale
\(H=\lceil N^{2/3}\rceil\).  The proof uses only the interval-union formula
for \(M_H\), the definition of \(G_H\), and the two inequalities defining
the ceiling.  It does not assume (LG33), C20, or any unproved incidence
bound.

**NOT PROVED:** (LG33) for all admissible sets.  Exact finite scans leave 78
endpoint-normalized sets through \(N=24\), and 151 of the 193 stored
prescribed profiles, outside the proved sharp envelope.  Their observed
satisfaction of (LG33) is not promoted to a theorem.

The all-scale audit also corrects an ambiguity in the earlier output:
coefficient \(13/6\) has no failures on the 193 prescribed profiles, but it
does **not** survive all 1,811,499 \(H\)-rows.  An exact six-element
falsifier at a nonprescribed scale is given below.

## 1. Definitions and the P33 frontier

Let

\[
A=\{a_1<\cdots<a_k\}\subseteq\{1,\ldots,N\},\qquad H\ge1.
\]

For \(d>0\), put

\[
\nu_A(d)=|\{(a,b)\in A^2:a-b=d\}|.
\]

For an admissible set, \(\nu_A(d)\in\{0,1,2\}\).  Define

\[
\begin{aligned}
D_H&=\sum_{\substack{1\le d<H\\ \nu_A(d)=2}}(H-d),\\
Q_H&=\sum_{\substack{1\le d<H\\ \nu_A(d)=0}}(H-d),\\
Z_H&=D_H-Q_H,\\
M_H&=|A+\{0,\ldots,H-1\}|,\\
G_H&=N+H-1-M_H.
\end{aligned}
\]

P33 proves that, in the high-support case \(3M_H\ge2N\), C20 follows from

\[
8NZ_H\le
12H^2G_H-3H^3+12H^2+9N(k-1)H. \tag{LG33}
\]

The reduction is in
[P33_centered_C20.md](../wave3/P33_centered_C20.md).  The present note proves
a genuine subcase of this displayed inequality.

## 2. Sharp gap envelope

Set

\[
\begin{aligned}
B_{N,H}&=9N(N-1)-3H^3+12H^2,\\
E^\sharp_H&=B_{N,H}+(12H^2-9N)G_H,\\
S_H&=kH-M_H.
\end{aligned} \tag{1}
\]

### Lemma 1 (support defect)

If \(g_i=a_{i+1}-a_i\), then

\[
M_H=H+\sum_{i=1}^{k-1}\min(g_i,H),
\qquad
S_H=\sum_{i=1}^{k-1}(H-g_i)_+\ge0. \tag{2}
\]

**Proof.**  Add the intervals
\([a_i,a_i+H-1]\) from left to right.  The first contributes \(H\) points,
and the next interval contributes \(\min(g_i,H)\) new points.  Subtracting
the resulting formula for \(M_H\) from \(kH\) gives (2).  No admissibility
property is used. \(\square\)

### Lemma 2 (exact envelope identity)

For every nonempty \(A\subseteq[1,N]\) and every positive \(H\),

\[
\begin{aligned}
&12H^2G_H-3H^3+12H^2+9N(k-1)H-E^\sharp_H\\
&\hspace{35mm}=9NS_H. \tag{3}
\end{aligned}
\]

In particular, the right side of (LG33) is at least \(E^\sharp_H\).

**Proof.**  Expanding (1), the left side of (3) is

\[
9N\bigl((k-1)H+G_H-(N-1)\bigr).
\]

Since \(G_H=N+H-1-M_H\), the parenthesis is \(kH-M_H=S_H\).
Lemma 1 gives the claimed sign. \(\square\)

### Lemma 3 (the prescribed-scale base)

If \(H=\lceil N^{2/3}\rceil\), then

\[
B_{N,H}>6N^2,
\qquad 12H^2-9N>0. \tag{4}
\]

Consequently

\[
E^\sharp_H>
E^0_H:=6N^2+(12H^2-9N)G_H\ge6N^2. \tag{5}
\]

**Proof.**  The definition of \(H\) gives

\[
(H-1)^3<N^2\le H^3.
\]

Hence

\[
\begin{aligned}
B_{N,H}-6N^2
&=3N^2-9N-3H^3+12H^2\\
&>3\bigl(H^2+3H-1-3N\bigr). \tag{6}
\end{aligned}
\]

Also \(N\le H^{3/2}\).  With \(x=\sqrt H\ge1\),

\[
\begin{aligned}
H^2+3H-1-3N
&\ge H^2+3H-1-3H^{3/2}\\
&=(x-1)\bigl(x(x-1)^2+1\bigr)\ge0.
\end{aligned}
\]

This proves the first part of (4).  Further,
\(H^2\ge N^{4/3}\ge N\), so
\(12H^2-9N\ge3N>0\).  Since \(G_H\ge0\), (5) follows. \(\square\)

### Theorem 4 (noncircular LG33 subcase)

For every positive \(H\),

\[
\boxed{8NZ_H\le E^\sharp_H}\quad\Longrightarrow\quad\text{(LG33)}. \tag{7}
\]

At \(H=\lceil N^{2/3}\rceil\), the simpler condition

\[
\boxed{4Z_H\le3N} \tag{8}
\]

also implies (LG33).

**Proof.**  Implication (7) is immediate from Lemma 2.  Under (8),
\(8NZ_H\le6N^2\); Lemma 3 then gives

\[
8NZ_H\le6N^2<E^\sharp_H\le\operatorname{RHS}(\mathrm{LG33}).
\]

This proves (8).  The high-support assumption is not needed for Theorem 4;
it is needed only when P33 uses (LG33) to conclude C20. \(\square\)

## 3. Exact remaining case

Define the sharp-envelope residual

\[
\rho_H:=8NZ_H-E^\sharp_H. \tag{9}
\]

Theorem 4 handles \(\rho_H\le0\).  Lemma 2 shows that the complementary
case is exactly

\[
\boxed{\rho_H>0,\qquad
\text{(LG33)}\ \Longleftrightarrow\
\rho_H\le9N(kH-M_H).} \tag{10}
\]

Thus the remaining proof obligation is not an unspecified finite pattern:
it is to make the short-gap overlap

\[
kH-M_H=\sum_i(H-g_i)_+
\]

pay for the positive residual \(\rho_H\).  At the prescribed scale,
Lemma 3 also shows that every remaining set must satisfy

\[
4Z_H>3N,
\qquad
(12H^2-9N)G_H<8NZ_H-B_{N,H}. \tag{11}
\]

Equations (10)-(11), not the finite counts below, are the quantified
general frontier.

## 4. Exact finite audits

All comparisons in the P50 scripts are integer comparisons.

### 4.1 Endpoint-normalized census through N=24

The exhaustive script checks all 8,388,608 endpoint-normalized candidate
subsets for \(1\le N\le24\).  Exactly 21,674 are admissible, and all 21,674
meet \(3M_H\ge2N\) at the prescribed scale.

| condition at prescribed H | covered | remaining | LG33 failures among covered |
|---|---:|---:|---:|
| \(4Z_H\le3N\) | 21,507 | 167 | 0 |
| \(8NZ_H\le E^0_H\) | 21,569 | 105 | 0 |
| \(8NZ_H\le E^\sharp_H\) | 21,596 | 78 | 0 |

There are no observed (LG33) failures among all 21,674 admissible sets.
This is a finite computation, not a proof of the remaining 78 cases for
arbitrary \(N\).

The 167 sets outside (8), grouped by \(N\), are

```text
7:1, 9:1, 11:2, 12:3, 14:2, 15:7, 16:4, 17:7, 18:4,
19:16, 20:15, 21:18, 22:23, 23:32, 24:32.
```

The 78 sets outside the sharp envelope are

```text
15:7, 16:2, 17:4, 19:4, 20:7, 21:10, 22:5, 23:21, 24:18.
```

Among these 78, the largest exact observed ratio in (10) is

\[
\frac{\rho_H}{9N(kH-M_H)}=\frac{139}{555}.
\]

It is attained at the translate of
\(A=\{1,3,6,7,14,15,18,20\}\), with
\((N,H,k,M_H,G_H,Z_H)=(20,8,8,27,0,27)\).  This ratio is a diagnostic only.

### 4.2 Stored P20 profiles at the prescribed scale

The input contains 1,811,499 rows from 193 samples.  Exactly one row per
sample has \(H=\lceil N^{2/3}\rceil\), and all 193 such rows are in the
high-support regime.

| condition at prescribed H | covered | remaining | LG33 failures among covered |
|---|---:|---:|---:|
| \(4Z_H\le3N\) | 32 | 161 | 0 |
| \(8NZ_H\le E^0_H\) | 38 | 155 | 0 |
| \(8NZ_H\le E^\sharp_H\) | 42 | 151 | 0 |

No prescribed profile falsifies (LG33).  Among the 151 sharp-envelope
residuals, the largest observed ratio in (10) is

\[
\frac{1662896}{1760589}
=\frac{914592800}{968323950}<1. \tag{12}
\]

The witness for (12) has

\[
(N,H,k,M_H,G_H,D_H,Q_H,Z_H)
=(4925,290,92,4834,380,39066,2839,36227).
\]

Here \(kH-M_H=21846\), \(\rho_H=914592800\), and the exact (LG33)
slack is

\[
9N(kH-M_H)-\rho_H=53731150.
\]

Again, (12) is corpus evidence, not an asymptotic estimate.

### 4.3 Every stored H-row

The `--all-scales` run evaluates every one of the 1,811,499 rows, of which
1,797,151 meet \(3M_H\ge2N\).  The sharp condition (7) covers 173,898 of
those rows and has zero implication failures, as forced by Lemma 2.  There
are 1,571,073 (LG33) failures at nonprescribed scales.  This does not affect
P33, whose C20 choice is the prescribed scale.

The bare linear condition (8) is not a theorem at arbitrary \(H\): among
the all-scale rows it covers 517,102 high-support profiles but includes
382,731 (LG33) failures.  Lemma 3 is the essential prescribed-scale input.

## 5. Coefficient envelopes and exact falsifiers

Put

\[
X_H=8NZ_H-12H^2G_H+3H^3-12H^2,
\qquad U_H=N(k-1)H. \tag{13}
\]

For this section, a coefficient \(c\) means the proposed inequality

\[
X_H\le4cU_H. \tag{14}
\]

Thus (LG33) is coefficient \(9/4\).  On the 193 prescribed profiles, the
exact failure counts for \(c=2,17/8,13/6,9/4\) are respectively

\[
9,\quad1,\quad0,\quad0. \tag{15}
\]

The largest required prescribed coefficient is

\[
\frac{X_H}{4U_H}=\frac{5580028}{2599415}
\approx2.14664,
\]

at the \(N=4925\) witness above.  For that witness,

\[
X_H=1116005600,\qquad U_H=129970750,
\]

and the exact cleared margins are

\[
\begin{aligned}
2X_H-17U_H&=22508450>0,\\
3X_H-26U_H&=-31222700<0.
\end{aligned}
\]

So this is an exact falsifier to coefficient \(17/8\), while \(13/6\)
survives the prescribed corpus only.

For completeness, the 1-indexed 92-element witness is

```text
{1, 32, 59, 85, 100, 148, 180, 191, 208, 298, 305, 319,
 374, 386, 563, 566, 582, 586, 636, 638, 738, 767, 803, 865,
 889, 907, 929, 966, 1062, 1075, 1199, 1277, 1278, 1286,
 1311, 1316, 1360, 1421, 1431, 1534, 1591, 1676, 1721, 1727,
 1885, 2128, 2798, 3041, 3199, 3205, 3250, 3335, 3392, 3495,
 3505, 3566, 3610, 3615, 3640, 3648, 3649, 3727, 3851, 3864,
 3960, 3997, 4019, 4037, 4061, 4123, 4159, 4188, 4288, 4290,
 4340, 4344, 4360, 4363, 4540, 4552, 4607, 4621, 4628, 4718,
 4735, 4746, 4778, 4826, 4841, 4867, 4894, 4925}.
```

It has the unique repeated unordered sum \(4926\).

### All-scale falsifier to 13/6

The statement that \(13/6\) survives all 1,811,499 rows is false.  Take

\[
A=\{1,2,4,8,10,11\},\quad N=H=11.
\]

The only repeated unordered sum is

\[
12=1+11=2+10=4+8,
\]

so the set is admissible.  Exact metrics are

\[
(k,M_H,G_H,D_H,Q_H,Z_H)=(6,21,0,38,6,32).
\]

Consequently

\[
X_H=5357,\qquad U_H=605,
\qquad 3X_H-26U_H=341>0. \tag{16}
\]

Equation (16) is an exact falsifier to coefficient \(13/6\) at \(H=11\).
It does not falsify (LG33), since

\[
9U_H-X_H=88>0.
\]

Nor does it touch the prescribed-scale candidate: for \(N=11\), the
prescribed scale is \(H=5\), not \(H=11\).  Across all high-support rows,
the exact failure counts for \(2,17/8,13/6,9/4\) are

\[
1577683,\quad1574351,\quad1573253,\quad1571073.
\]

## 6. Reproduction

Run from the repository root:

```powershell
python -m py_compile problems/864/compute/p50/audit_lg33_subcase.py problems/864/compute/p50/audit_profile_coefficients.py

python problems/864/compute/p50/audit_lg33_subcase.py `
  --max-n 24 `
  --output problems/864/compute/p50/audit_results.json

python problems/864/compute/p50/audit_profile_coefficients.py `
  --input problems/864/compute/p20/results/profiles.jsonl.gz `
  --output problems/864/compute/p50/profile_coefficient_gates.json

python problems/864/compute/p50/audit_profile_coefficients.py `
  --all-scales `
  --input problems/864/compute/p20/results/profiles.jsonl.gz `
  --output problems/864/compute/p50/profile_all_scale_gates.json
```

The profile corpus SHA-256 recorded before and after each profile scan is

```text
abe9e8270cac543c5d2a394c0eb6ef23dbc829afe02719bd6332e26341b00e83
```

The generated result files are:

* `problems/864/compute/p50/audit_results.json`;
* `problems/864/compute/p50/profile_coefficient_gates.json`;
* `problems/864/compute/p50/profile_all_scale_gates.json`.

The exhaustive script also reconstructs the stored \(N=4925\) witness from
`problems/864/compute/p36/admissible_bridge_obstruction.json` and checks its
admissibility, reflection involution, gap identity, centered \(D_H-Q_H\)
identity, envelope identity, and all displayed integer margins.

## 7. Prior-art and claim boundary

The official [problem page](https://www.erdosproblems.com/864) still marks
Problem 864 open, and its
[discussion thread](https://www.erdosproblems.com/forum/thread/864) contains
no claim of the threshold (7) or (8).  A local search likewise found no
earlier `4Z_H <= 3N` statement.  This is a limited novelty check, not a
complete literature certification.

The proved contribution of this note is exactly Theorem 4 and the identities
supporting it.  The 78-set census, the 151 stored residuals, the observed
ratio (12), and the prescribed-scale survival of coefficient \(13/6\) are
finite facts only.  None is asserted as a theorem for arbitrary admissible
sets.
