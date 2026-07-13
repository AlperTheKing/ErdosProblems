# P20: exact support-defect profiles

## Verdict

**EXACT EXPERIMENT; ONE FINITE-CORRECTION CANDIDATE; NO THEOREM.**

For every loaded or generated admissible set and every integer
\(1\le H\le N\), the code computes the occupied thickening, interval
components, gap truncation, duplicate and missing triangular weights,
exceptional multiplicity, and the exact reduced frontier product. The final
snapshot has 193 samples and 1,811,499 profiles. A separate streaming
verifier passed every profile.

The cleanest surviving rule in this snapshot is

\[
 H=\left\lceil N^{2/3}\right\rceil
   =\min\{h\in\mathbb Z_{\ge1}:h^3\ge N^2\}.                 \tag{1}
\]

Writing \(k=|A|\) and

\[
 P_H(A,N)=\frac{M_H}{N}\left(1+\frac{2Z_H}{H^2}\right),
\]

the precise candidate is

\[
 \boxed{
 P_H(A,N)\le \frac43+
 \frac32\left(\frac HN+\frac{k-1}{H}\right)
 \quad\text{for the }H\text{ in (1)}.}                     \tag{C20}
\]

There were no failures of (C20) in the measured corpus. This is only a
candidate inequality extracted from finite data. No structural proof was
found.

## Exact conventions

For \(d>0\), the implementation uses

\[
 \nu_A(d)=|\{(a,b)\in A^2:a-b=d\}|.
\]

Admissibility implies \(\nu_A(d)\in\{0,1,2\}\). For \(1\le d<H\), define

\[
\begin{aligned}
 D_H&=\sum_{d=1}^{H-1}(H-d)\,1_{\{\nu_A(d)=2\}},\\
 Q_H&=\sum_{d=1}^{H-1}(H-d)\,1_{\{\nu_A(d)=0\}}.
\end{aligned}
\]

Then the requested net support defect is computed literally as

\[
 Z_H=\sum_{d=1}^{H-1}(H-d)(\nu_A(d)-1)=D_H-Q_H.             \tag{2}
\]

Thus missing differences contribute negatively; \(Z_H\) is not the
positive duplicate weight alone.

If \(A=\{a_1<\cdots<a_k\}\), with gaps \(g_i=a_{i+1}-a_i\), the code uses

\[
 M_H=\left|A-\{0,\ldots,H-1\}\right|
     =H+\sum_{i=1}^{k-1}\min(H,g_i).                        \tag{3}
\]

It also records

\[
 \#\text{components}=1+\#\{i:g_i>H\},\qquad
 T_H=\sum_i(g_i-H)_+.                                      \tag{4}
\]

Here \(T_H\) is **gap_truncation_weight**, and
\(M_H=(a_k-a_1)+H-T_H\).

Unordered sums are enumerated with \(a\le b\), so every diagonal is included
in admissibility and exceptional multiplicity. Positive differences have no
diagonal term.

At every profile the code verifies by integer cross multiplication

\[
 k^2H^2\le
 M_H\left(H^2+(k-1)H+2Z_H\right),                          \tag{5}
\]

which is the stated exact P02 inequality.

## Corpus

The stable input snapshot consists of 34 JSONL artifacts. SHA-256 hashes for
all 34 are in **compute/p20/results/summary.json**.

The 169 artifact witnesses are:

| Kind | Count |
|---|---:|
| exact census | 55 |
| certified endpoints | 6 |
| reflected Bose | 26 |
| reflected Ruzsa | 18 |
| reflected Singer | 30 |
| natural-cut reflected Singer | 26 |
| natural-cut reflected Ruzsa | 8 |

The code adds 24 deterministic exact samples: 10 shuffled-greedy maximal
admissible sets, 7 partial-core deletions, and 7 index-modulo-three subsets.
Every generated set is independently rechecked before profiling. The final
range is \(1\le N\le74963\) and \(1\le k\le336\).

All 1,811,499 values \(H=1,\ldots,N\) are archived, not sampled. Each row
contains \(M_H,Z_H,D_H,Q_H\), duplicate/missing distance counts, components,
gap truncation, the base factor, and the reduced numerator and denominator
of \(P_H\). Profile rows contain integers and identifiers only. Decimal
fields occur only in the display portions of the summary.

## Candidate certificate

The largest coefficient required by (C20) occurs for
**singer-ff6287916581**, from
**problems/864/compute/p12/singer_exhaustive_large.jsonl:2**:

\[
\begin{split}
A=\{&1,8,14,17,31,39,51,78,97,99,123,141,151,152,156,192,\\
    &227,259,324,356,391,427,431,432,442,460,484,486,505,\\
    &532,544,552,566,569,575,582\}.
\end{split}
\]

Its exact data are

\[
\begin{gathered}
N=582,\quad k=36,\quad e=583,\quad r_A(e)=18,\quad H=70,\\
M_H=651,\quad D_H=2367,\quad Q_H=43,\quad Z_H=2324,\\
\#\text{components}=1,\quad T_H=0,\\
P_H=\frac{10571}{4850},\qquad
\frac HN+\frac{k-1}{H}=\frac{361}{582}.
\end{gathered}
\]

The exact coefficient required at this sample is

\[
 \frac{P_H-4/3}{H/N+(k-1)/H}
 =\frac{12313}{9025}
 \quad\text{(display: }1.364321329640\text{)}.              \tag{6}
\]

Consequently (C20) has exact slack

\[
 \frac43+\frac32\frac{361}{582}-\frac{10571}{4850}
 =\frac{2449}{29100}>0.                                   \tag{7}
\]

If (C20) were proved, the known \(k=O(\sqrt N)\) bound would give
\(H/N=O(N^{-1/3})\) and \(k/H=O(N^{-1/6})\), hence
\(P_H\le4/3+o(1)\). Combining this with (5) and
\(M_H/N\le1+(H-1)/N\) would close the P20 frontier. This paragraph is a
conditional implication, not evidence of a proof.

## Exact falsifiers

The same 36-element set falsifies coefficient \(4/3\) in place of \(3/2\):

\[
 \frac{10571}{4850}-\frac43-\frac43\frac{361}{582}
 =\frac{839}{43650}>0.                                    \tag{8}
\]

Thus the finite correction in (C20) cannot simply be reduced to \(4/3\) on
this corpus. Coefficient \(1\) fails on 67 of 193 samples.

The strongest falsifier among the other audited natural rules is the
first-connected rule \(H=\max_i g_i\). For
**ruzsa-8cc36a434761** from
**problems/864/compute/p12/ruzsa_exhaustive_xlarge.jsonl:5**,

\[
\begin{gathered}
N=12002,\quad k=140,\quad H=2191,\quad M_H=14192,\\
D_H=2112821,\quad Q_H=286324,\quad Z_H=1826497,\\
P_H=\frac{59985858600}{28807686481},\qquad
\frac HN+\frac{k-1}{H}=\frac{6468759}{26296382}.
\end{gathered}
\]

Its required coefficient is

\[
 \frac{129453659752}{42519152907}
 \quad\text{(display: }3.044596397185\text{)},              \tag{9}
\]

so even coefficient \(3\) is falsified, by the exact gap

\[
 P_H-\frac43-3\left(\frac HN+\frac{k-1}{H}\right)
 =\frac{1896201031}{172846118886}>0.                       \tag{10}
\]

Other rule maxima, using the same correction base, are:

| Rule | Largest exact required coefficient | C=2 failures |
|---|---:|---:|
| \(H=\lceil N^{2/3}\rceil\) | \(12313/9025\) | 0 |
| \(H=\lceil N^{3/4}\rceil\) | \(1572511070/570991779\) | 62 |
| \(H=\lceil\sqrt{Nk}\rceil\) | \(178433286683/61194444480\) | 74 |
| balanced dyadic \(H\) | \(147539180689/53458787328\) | 32 |
| first connected \(H\) | \(129453659752/42519152907\) | 77 |

The adaptive minimizer over
\([\lceil\lceil\sqrt{Nk}\rceil/2\rceil,\,
\min(N,2\lceil\sqrt{Nk}\rceil)]\) changed the lower endpoint on only
1 of 193 samples, improving \(P_H\) by exactly \(1/495\).
This supplies no evidence for a useful structural adaptive rule. The global
minimum is always contaminated by the vacuous \(H=1\) option and was not
treated as a mesoscopic rule. Choosing \(H=\lceil\sqrt N\rceil\) also does
not make \((k-1)/H=o(1)\) in the extremal regime.

## Reproduction and files

From the repository root:

~~~powershell
python problems/864/compute/p20/support_defect_profiles.py
python problems/864/compute/p20/test_support_defect_profiles.py
python problems/864/compute/p20/verify_results.py
~~~

The final verifier output was

~~~text
{"artifact_count": 34, "profile_count": 1811499, "sample_count": 193, "status": "verified"}
~~~

Outputs:

- **compute/p20/results/samples.jsonl**: exact normalized sets and provenance.
- **compute/p20/results/profiles.jsonl.gz**: every exact profile.
- **compute/p20/results/summary.json**: candidate/rule audit and input hashes.

Final output SHA-256 values:

~~~text
a1ed5f869a0911b692d359d5838b9a4a271f37e057947945255ed1e9d4625d31  samples.jsonl
abe9e8270cac543c5d2a394c0eb6ef23dbc829afe02719bd6332e26341b00e83  profiles.jsonl.gz
bb87560035927591278d0bd22e5bccbc58f9d6268fb2d6b9b8a972904728dc3d  summary.json
~~~

The generator hashes inputs before loading and again after the sweep. It
rejects the run if a concurrent artifact changes during computation.

## Post-audit: C20 is false

The later P23 congruence-compressed Ruzsa family disproves C20
asymptotically: at H=ceil(N^(2/3)), its left side has liminf at least 3/2,
whereas the correction on the right tends to zero.

There is already an exact finite falsifier at p=503. The standalone verifier

    problems/864/compute/p20/verify_p23_falsifier.py

uses integer arithmetic, checks literal admissibility including diagonals,
and returns

    N=1010022, k=1004, H=10067,
    M_H=1019964, Z_H=25058720,

with cleared C20 margin

    7065310880607 > 0.

Therefore candidate (C20) is DEAD, not an open proof frontier.

## Correction to the post-audit claim

The preceding post-audit claim used P23's duplicate-only weight as though it
were P20's centered defect. That is incorrect. P20 uses Z_H=D_H-Q_H.

For the p=503 audit,

    D_H=25058720, Q_H=25569511, Z_H=-510791.

The duplicate-only cleared margin is positive, but the actual centered C20
margin is

    -305894457730641 < 0.

Therefore p=503 is not a C20 falsifier, and the P23 family does not
asymptotically falsify centered C20 without an additional proof that
Q_H=o(H^2). Candidate C20 returns to OPEN status. The corrected standalone
audit is compute/p20/verify_p23_falsifier.py.
