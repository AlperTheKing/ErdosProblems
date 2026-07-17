# C54: dyadic recurrence bypass

## Verdict

There is an exact matching-free dyadic recurrence.  Let `m_j,e_j,r_j`
denote the numbers of holes, splitless holes, and reducible holes in

\[
 I_j=(2^{j-1},2^j].
\]

Let `s_j,h_j,q_j` denote, respectively, the C16 seed-3 holes, hard holes,
and healed seed-2 target events in the same shell.  Then

\[
 \boxed{r_j=m_{j-1}+s_j+h_j-q_j.}                       \tag{1}
\]

Consequently, either of the following eventual estimates would prove
`M(X)=o(X)`:

\[
 r_j\le(2-\varepsilon)m_{j-1}+o(2^j)                    \tag{2}
\]

for one fixed `epsilon>0`, or the analogous estimate after summing any
fixed number of consecutive shells.  Its normalized contraction coefficient
is `1-epsilon/2<1`.  This uses only net annular counts; it requires no
matching, factor choice, component assignment, or rank-compatible transport.

The proposed stronger shell statistic

\[
                         s_j+h_j\le q_j                 \tag{SH}
\]

is exactly false.  Its first tested falsifier is `X=128`:

\[
 (s_7,h_7,q_7)=(4,2,3),\qquad r_7=18>15=m_6.           \tag{3}
\]

Even the relaxed proposed coefficient `r_j <= (5/4)m_(j-1)` is false at
`X=1024`:

\[
 r_{10}=135,\quad m_9=106,\quad 4r_{10}=540>530=5m_9. \tag{4}
\]

The weaker strict-gap condition (2) has no falsifier in the exact dyadic
census through `2^27=134,217,728`.  The largest tested ratio is

\[
 \max_{7\le j\le27}{r_j\over m_{j-1}}
 ={135\over106}=1.2735849056\ldots,                    \tag{5}
\]

at `j=10`; the corresponding normalized coefficient is `135/212`.
At `j=27` the ratio is

\[
 {3,223,210\over4,850,573}=0.6645008744\ldots.         \tag{6}
\]

No proof of (2) follows from C13/C16/C39.  At full rank C39 reduces
algebraically to C16, so its identities supply no upper bound for the defect
`s_j+h_j-q_j`.  Proving any uniform gap in (2) remains a new global
arithmetic incidence statement.  Thus C54 returns a proved conditional
recurrence, two exact falsifiers, and this precise obstruction; it does not
prove a density theorem.

## 1. Exact shell identity

Use the C13/C16 notation

\[
 M(X)=E(X)+R(X),
\]

and partition the reducible holes as `O,S,H`.  C16 proves, with
`Y=floor((X+1)/2)`,

\[
 O(X)+Q(X)=M(Y),\qquad R(X)=O(X)+S(X)+H(X).             \tag{7}
\]

For `X=2^j`, `j>=2`, one has `Y=2^(j-1)`.  Subtract (7) at `2^j` and
`2^(j-1)`.  The seed-2 map sends a parent in `I_(j-1)` to the odd child
`2m-1` in `I_j`, with no endpoint ambiguity because shell endpoints are
even.  Hence

\[
 o_j+q_j=m_{j-1}.                                      \tag{8}
\]

Every missing parent here is greater than `2`, so the pair `(2,m)` has
distinct inputs.  Substituting (8) in `r_j=o_j+s_j+h_j` proves (1).
No diagonal product is used.

Equivalently, with

\[
 d_j=s_j+h_j-q_j,
\]

the exact coefficient is

\[
 \theta_j={r_j\over m_{j-1}}=1+{d_j\over m_{j-1}}.     \tag{9}
\]

Thus (2) asks only for

\[
 d_j\le(1-\varepsilon)m_{j-1}+o(2^j),                 \tag{10}
\]

which is strictly weaker than shell healing (SH), and much weaker than a
pointwise source-target matching.

## 2. Contraction theorem

**Theorem.** Fix `L>=1`.  Define fixed-width annular sums

\[
 m_j^{(L)}=\sum_{i=0}^{L-1}m_{j-i},\quad
 e_j^{(L)}=\sum_{i=0}^{L-1}e_{j-i},\quad
 r_j^{(L)}=\sum_{i=0}^{L-1}r_{j-i}.
\]

If there is a constant `theta<2` such that

\[
 r_j^{(L)}\le\theta m_{j-1}^{(L)}+o(2^j)               \tag{11}
\]

for all sufficiently large `j`, then `M(X)=o(X)` and `G` has natural
density `2/3`.

**Proof.**  C13 gives `E(X)=o(X)`, so
`e_j^(L)<=E(2^j)=o(2^j)`.  Since `m_j^(L)=e_j^(L)+r_j^(L)`, put

\[
 a_j={m_j^{(L)}\over2^j}.
\]

Equation (11) gives

\[
 a_j\le {\theta\over2}a_{j-1}+o(1).
\]

The sequence is bounded by the ambient allowed density.  Taking limsups
and using `theta/2<1` gives `limsup a_j=0`.  In particular
`m_j/2^j -> 0`.  Finally,

\[
 {M(2^J)\over2^J}
 =\sum_{j\le J}2^{j-J}{m_j\over2^j}\longrightarrow0
\]

by a geometric-tail argument.  Monotonicity extends this from dyadic
endpoints to every `X`.  The allowed set has counting function
`2X/3+O(1)`, proving the density assertion.  QED.

For `L=1`, condition (10) gives (11) with `theta=2-epsilon`, hence the
normalized contraction `1-epsilon/2` stated above.

## 3. Exact coefficient census

The audit rebuilt the least grounded set independently at every endpoint
`2^j`, `5<=j<=27`, by exact ascending divisor recursion.  Every admissible
pair was required to satisfy `2<=a<b`; in particular, squares were never
accepted as closure witnesses.  It checked (1) with integer arithmetic at
every reported shell.

Selected one-shell rows are:

| `j` | `2^j` | `r_j` | `m_(j-1)` | `d_j` | `theta_j` | `theta_j/2` |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 128 | 18 | 15 | 3 | `6/5` | `3/5` |
| 10 | 1,024 | 135 | 106 | 29 | `135/106` | `135/212` |
| 16 | 65,536 | 4,591 | 4,602 | -11 | `4591/4602` | `4591/9204` |
| 20 | 1,048,576 | 45,629 | 54,172 | -8,543 | `45629/54172` | `45629/108344` |
| 24 | 16,777,216 | 502,102 | 687,297 | -185,195 | `502102/687297` | `251051/687297` |
| 27 | 134,217,728 | 3,223,210 | 4,850,573 | -1,627,363 | `3223210/4850573` | `1611605/4850573` |

Within the audited range `j>=7`, the shell defect first becomes nonpositive
at `j=16` and remains nonpositive at every tested dyadic endpoint through
`j=27`.  This is a finite statement only.

For consecutive-window averages, the largest and terminal exact ratios in
the computed range were:

| width `L` | maximum tested ratio | endpoint of maximum | ratio at `2^27` |
|---:|---:|---:|---:|
| 2 | `200/161` | 1,024 | `2474917/3685414` |
| 4 | `253/206` | 1,024 | `580031/851994` |
| 8 | `3217/2864` | 16,384 | `6930793/10078576` |

All three maxima are below `2`, but no finite row is extrapolated.

## 4. Why C39 does not close (10)

At a rank cutoff `d`, C39 has the exact potential identity

\[
 H_{\le d}-Q_{\le d}
 =M_d-E-M_d(Y)-O_d(Z)+A_{2,d}+A_{3,d}+R_{3,d}.          \tag{12}
\]

For a fixed coordinate, take `d` beyond all hole ranks.  The two transient
terms vanish.  The full seed-3 trichotomy is

\[
 O(Z)=S(X)+R_3(X).                                      \tag{13}
\]

Substitution of (13) into (12) gives exactly

\[
 R(X)=M(Y)+S(X)+H(X)-Q(X),                              \tag{14}
\]

which is C16 again.  Subtracting (14) at consecutive dyadic endpoints is
precisely (1).  Thus C39 contributes rank resolution but no second scalar
constraint on `d_j` after ranks are removed.  Rank averaging only reweights
the unsigned transient and seed-3 boundary terms in (12); no available sign
bounds their sum.

This is a logical, not numerical, obstruction.  For example, the abstract
shell counts

\[
 e_j=q_j=s_j=0,\quad o_j=h_j=m_{j-1},\quad
 m_j=r_j=2m_{j-1}                                      \tag{15}
\]

satisfy all scalar identities (1), (7), and `E=o(X)`, but have
`theta_j=2` forever.  They can be scaled below the ambient residue-class
capacities.  Equation (15) is not an arithmetic countermodel to the actual
least `G`; it proves that the cited count identities alone cannot yield a
strict coefficient.  Grounded multiplication-table incidence must exclude
this count profile.

The C39 source `74` gives the corresponding local obstruction: its critical
component has no rank-compatible target before the source, while its actual
credits come from unrelated components.  Annular pooling removes the need
to identify those credits, but it does not prove that enough pooled credit
exists.  The missing theorem is exactly (10), or its fixed-window version.

## 5. Reproduction

From the repository root:

```powershell
python problems/424/fanout/wave5/C54_exact_dyadic.py `
  --min-power 7 --max-power 27 --block-widths 2 4 8
```

The script compiles the accepted C16 source into a temporary directory and
writes all census JSON there; it prints the C54 result to standard output.
The exact run took 42 seconds.  An independent C13 executable replay at
`10^8` returned

```text
M=14,767,537  E=9,395,726  R=5,371,811
```

and all three integers equal the C16 snapshot.  SHA-256 values were

```text
C16 engine             AA0430765F8AB4F82223A53F0FDA21D2BAC592727231F1942F47F7745BF7087A
C54_exact_dyadic.py    0E6D636F14F84494929C2AD6E10BF0A9939FDA0B268812BDE2AF6C0F986BB928
```

No claim of (2), (10), (11), `M(X)=o(X)`, or positive lower density is made
without the displayed conditional hypothesis.
