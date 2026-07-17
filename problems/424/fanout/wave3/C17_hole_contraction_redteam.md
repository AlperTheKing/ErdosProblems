# C17: grounded hole-contraction red team

## Verdict

C13's implication is correct: if

\[
 R(X)\le \lambda M\!\left(\left\lfloor{X+1\over2}\right\rfloor\right),
 \qquad \lambda<2,
\]

eventually, then the splitless estimate `E(X)=o(X)` gives `M(X)=o(X)`.
For the actual least set generated from `2,3`, an exact all-cutoff scan through
`10^9` does not falsify this inequality. The largest required coefficient is
still

\[
 {101\over80}\quad\hbox{at }X=362.
\]

This finite survival is not a closure theorem. The C22 CP-SAT certificate is
an exact forward-closed superset at `X=5000` with

\[
 R-M(2500)-M(1667)=105-41-21=43.
\]

An independent replay below finds `1384` members of that certificate with no
derivation tree from the seeds. Replacing it by its grounded core changes the
same excess to `-515`. Thus any universal closure-only contraction is false;
grounded derivation trees are load-bearing.

There are two further negative results.

1. A capacity-one all-factor matching fails first at `X=54`: the two holes
   `21,54` have the single missing neighbor `11`. Hence every local
   per-factor load theorem with a universal coefficient below `2` is already
   false on the true generated set.
2. Uniform reciprocal weighting over every admissible factor pair gives an
   exact multiscale recurrence, but its finite composite-factor envelope moves
   from `1.745951216` at `10^6` to `1.929990036` at `10^9`. The all-factor
   envelope is `3.625676648` at `10^9`. This route supplies no uniform margin.

The useful surviving statement is rank-grounded. Define `Q_r(X)` to count
missing parents `m <= floor((X+1)/2)` whose child `2m-1` has a derivation tree
of rank at most `r`. Exact enumeration gives

```text
Q_9(X) >= H(X) for every integer X <= 1,000,000,000,
```

where `H` is the hard reducible-hole class. Rank `8` is not enough: its first
failure is `X=6,989,400`. These are finite facts, not a bounded-rank theorem.

The weakest rank-visible sufficient residual isolated here is `D_r` in
equation (18). Proving `D_r(X)=o(X)` for an explicit rank schedule, or a
multiscale bound whose exact normalized budget is below `1/6`, would imply
`M(X)=o(X)` and hence density `2/3` for `G`. No such asymptotic estimate is
proved here, so no solution of Problem 424 is claimed.

## 1. Exact setup and audit of C13

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\},\qquad
 \mathcal M=\mathcal A\setminus G.
\]

Write `M(X)` for the number of holes in `mathcal M` through `X`. For an
allowed `n`, let

\[
 \mathcal P(n)=\{(a,b):n+1=ab,\ 2\le a<b,\ a,b\in\mathcal A\}. \tag{1}
\]

The ascending membership recursion is

\[
 n\in G\quad\Longleftrightarrow\quad n\in\{2,3\}
 \quad\hbox{or}\quad
 (a,b)\in\mathcal P(n)\hbox{ for some }a,b\in G.             \tag{2}
\]

Every endpoint in (1) is smaller than `n`, so (2) is an exact finite
algorithm. Let `E(X)` count missing `n` for which `P(n)` is empty and put

\[
 R(X)=M(X)-E(X).                                             \tag{3}
\]

C13's proof that `E(X)=o(X)` checks out. Its exceptional successors are
contained in integers with no prime divisor `2 mod 3`, their threefold
dilates, and `O(sqrt(X))` prime squares. A finite-prime sieve followed by the
divergence of the reciprocal primes `2 mod 3` gives density zero.

The independent C17 scan uses every admissible pair in (1), integer gates,
and exact rational reduction. It extends C13 by one decade:

| `X` | `M(X)` | `E(X)` | `R(X)` | `M(floor((X+1)/2))` |
|---:|---:|---:|---:|---:|
| `10^6` | 209,067 | 108,651 | 100,416 | 112,283 |
| `10^8` | 14,767,537 | 9,395,726 | 5,371,811 | 7,690,740 |
| `10^9` | 131,390,048 | 88,550,127 | 42,839,921 | 67,876,334 |

At every integer cutoff through `10^9`, `R(X)<2M(floor((X+1)/2))`. The
maximum exact ratio is `101/80` at `X=362`; this is a finite maximum only.

## 2. Grounding is equivalent to finite derivation rank

Define the minimum derivation rank on the true generated set by

\[
 \rho(2)=\rho(3)=0,
\]

\[
 \rho(n)=1+\min_{\substack{(a,b)\in\mathcal P(n)\\a,b\in G}}
                 \max(\rho(a),\rho(b)).                     \tag{4}
\]

**Lemma 1 (rank characterization).** An allowed integer belongs to `G` if
and only if it has a finite rooted derivation tree whose leaves are `2,3`
and whose internal node `n` has two distinct children `a,b` with
`n=ab-1`. Its minimum tree height is (4).

**Proof.** A finite tree evaluates upward by the generation rule, so its root
is in `G`. Conversely, every stage at which `n` is generated supplies two
earlier-stage children. Recursing terminates at a seed and gives a finite
tree. Minimizing the maximum child height gives (4). QED.

The same observation gives an exact finite-set test.

**Corollary 2.** Let `S` be an allowed finite prefix containing `2,3`.

* If `S` is forward closed, then `G` in that prefix is contained in `S`.
* If every nonseed member of `S` has a witness pair in `S` with smaller
  assigned ranks, rooted at rank-zero seeds, then `S` is contained in `G`.

Thus a forward-closed `S` equals the least generated set exactly when it is
also grounded. The second implication is strong induction on rank (or on
the value, since both factors are smaller).

### Replay of the C22 countermodel

The script `grounding_audit.py` first verifies C22's forward-closure clauses,
then independently computes the least closure and the ranks (4).

| quantity at `X=5000` | C22 closed certificate | grounded core |
|---|---:|---:|
| members | 2,880 | 1,496 |
| holes | 453 | 1,837 |
| reducible holes `R` | 105 | 1,136 |
| `Mhalf` | 41 | 977 |
| `Mthird` | 21 | 674 |
| `R-Mhalf-Mthird` | **43** | **-515** |

There are `427` certificate members with no local witness pair at all and
`1384` with no seed-rooted derivation. The first ungrounded values are

```text
18, 20, 21, 30, 32, 35, 38, 39, 45, 48, 56, 57, ...
```

The true grounded rank histogram through `5000` is

```text
[2, 1, 2, 7, 53, 279, 460, 403, 233, 47, 9].
```

This pinpoints the logical failure in a closure-only proof: forward closure
can add unsupported members, remove small holes, and leave many reducible
holes above them. Such members cannot be used as generated witnesses.

## 3. Exact all-pair reciprocal recurrence

For a reducible hole `n`, put `t(n)=|P(n)|`. Every pair in `P(n)` has at
least one missing endpoint, since a generated-generated pair would generate
`n`. Give each missing endpoint of every pair weight `1/t(n)` and define

\[
 L_X(m)=\sum_{\substack{n\le X,\ n\in\mathcal M\\t(n)>0}}
 {\#\{(a,b)\in\mathcal P(n):m\in\{a,b\}\}\over t(n)}.       \tag{5}
\]

All endpoints satisfy `m <= floor((X+1)/2)`. Summing one output at a time
gives the exact all-pair inequality

\[
 R(X)\le C(X):=
 \sum_{\substack{m\le\lfloor(X+1)/2\rfloor\\m\in\mathcal M}}L_X(m). \tag{6}
\]

No factor choice is hidden in (6); all admissible pairs are present.

For machine verification set `W=2^30` and replace `1/t` by the integer
majorant

\[
 w_t=\left\lceil{W\over t}\right\rceil.                    \tag{7}
\]

If `C_W(X)` is the resulting integer charge, then

\[
 WR(X)\le C_W(X).                                           \tag{8}
\]

Every multiplication and comparison used for (8) is integer-valued. The
maximum of `C_W(X)/(W M(floor((X+1)/2)))` through `10^9` is

\[
 {15232220827\over10334765056}=1.473881675\ldots
 \quad\hbox{at }X=1080.                                    \tag{9}
\]

Thus even the ceiling-majorized all-pair charge remains below `2` on the
finite prefix. It does not provide a proof beyond the prefix.

### The local dual obstruction

Form a bipartite graph whose left vertices are odd reducible holes and hard
holes. An odd hole `n` has its forced seed-2 parent `(n+1)/2` as neighbor; a
hard hole has every missing endpoint from every pair in `P(n)`. Seed-3 holes
are omitted because they inject into the third-scale copy.

At `X=54`,

\[
 21+1=2\cdot11,\qquad 54+1=5\cdot11,                        \tag{10}
\]

and both factorizations are unique. Therefore

\[
 N(\{21,54\})=\{11\}.                                      \tag{11}
\]

Hall's condition fails, and a fractional per-factor capacity must be at
least `2`. At `X=10^6` the exact graph has `90,329` left vertices,
`132,483` edges, and maximum matching `46,856`. The extracted Hall witness
has `48,662` left vertices and only `5,189` neighbors, a deficit of `43,473`.
Consequently, neither a canonical factor nor a capacity-one flow can prove
the aggregate contraction.

## 4. Dyadic multiscale envelope

The fixed-point loads from (7) give an exact multiscale diagnostic. Put

\[
 U_j=\left\lfloor{X+1\over2^j}\right\rfloor
\]

and let `W_j` be the monotone envelope of the largest integer load in the
first `j` dyadic factor shells. Abel summation gives

\[
 C_W(X)\le W_1M(U_1)+
 \sum_{j\ge2}(W_j-W_{j-1})M(U_j).                           \tag{12}
\]

For a frozen finite envelope, its normalized scale budget is

\[
 \Theta_X={W_1\over2W}+
 \sum_{j\ge2}{W_j-W_{j-1}\over 2^jW}.                      \tag{13}
\]

Separating prime and composite missing endpoints gives the following exact
composite-envelope values.

| `X` | exact `Theta_X` for composite endpoints | decimal |
|---:|---:|---:|
| `10^6` | `30715098617777/17592186044416` | 1.745951216 |
| `10^7` | `250343487123947/140737488355328` | 1.778797462 |
| `10^8` | `16653070506599425/9007199254740992` | 1.848862231 |
| `10^9` | `278140877091303193/144115188075855872` | 1.929990036 |

This finite sequence presses toward `2`; it does not prove an asymptotic
limit. Prime endpoint charge remains outside the composite recurrence. If
all endpoints are put into the envelope, (13) at `10^9` is

\[
 {261257535996900303\over72057594037927936}
 =3.625676648\ldots.                                       \tag{14}
\]

The unique-pair seed load also attains exactly `2` (for example at the
missing factor `333331931` in the `10^9` snapshot). Hence this data-dependent
envelope offers no stable coefficient below `2`.

## 5. Exact grounded seed partition

Set

\[
 Y=\left\lfloor{X+1\over2}\right\rfloor,\qquad
 Z=\left\lfloor{X+1\over3}\right\rfloor.
\]

Partition the reducible holes through `X` into:

* `O_X`: odd holes;
* `S_X`: even holes with an admissible seed-3 pair
  `3*((n+1)/3)`;
* `H_X`: all remaining hard holes.

Let their counts be `O,S,H`, and define the grounded seed-2 healing count

\[
 Q(X)=\#\{m\in\mathcal M:m\le Y,\ 2m-1\in G\}.             \tag{15}
\]

**Lemma 3 (exact partition).** For every `X`,

\[
 O(X)+Q(X)=M(Y),\qquad S(X)\le M(Z),                        \tag{16}
\]

and

\[
 R(X)=M(Y)-Q(X)+S(X)+H(X).                                 \tag{17}
\]

**Proof.** For every missing `m <= Y`, the odd child `2m-1` is allowed and
is either a missing odd hole or generated. These alternatives give the
first identity. A seed-3 hole maps injectively to its missing parent
`(n+1)/3 <= Z`, proving the second inequality. The three classes partition
the reducible holes; substitute `O=M(Y)-Q`. QED.

This is where derivation trees enter essentially. If `m` is counted by `Q`,
the generated child `2m-1` cannot use the pair `(2,m)`, because `m` is
missing. It therefore has an alternative generated-generated root pair, and
that pair sits above two strictly lower-rank derivation trees.

Define the rank-truncated capacity

\[
 Q_r(X)=\#\{m\in\mathcal M:m\le Y,\ 2m-1\in G,
                         \ \rho(2m-1)\le r\}.
\]

The exact finite rank census is:

| `X` | `H(X)` | `Q_8(X)` | `Q_9(X)` | `Q(X)` | maximum generated rank |
|---:|---:|---:|---:|---:|---:|
| `10^6` | 45,583 | 47,708 | 59,236 | 67,537 | 17 |
| `10^8` | 3,368,726 | 3,168,848 | 4,798,229 | 5,948,614 | 20 |
| `10^9` | 29,010,146 | 25,425,738 | 43,478,283 | 55,583,430 | 23 |

At all integer cutoffs through `10^9`, `H(X)<=Q_9(X)`. For rank `8`, the
first and last failing cutoffs are `6,989,400` and `1,000,000,000`; the
maximum excess is `3,584,413` at `X=999,999,570`. The true two-scale
inequality `R(X)<=M(Y)+M(Z)` also has no failure through `10^9`, while C22
shows that the same statement is false for forward-closed supersets.

## 6. Weakest noncircular frontier

The unused third-scale capacity is

\[
 B(X)=M(Z)-S(X)\ge0.
\]

For a rank cap `r`, define the positive residual

\[
 D_r(X)=\bigl[H(X)-Q_r(X)-B(X)\bigr]_+.                    \tag{18}
\]

Since `Q_r<=Q`, equations (3) and (17) give the exact upper recurrence

\[
 M(X)\le E(X)+M(Y)+M(Z)+D_r(X).                            \tag{19}
\]

For `r=infinity`, `D_r` is precisely the positive part of the two-scale
contraction excess after all exact seed slack is used. Thus the following is
the weakest scalar residual statement exposed by this partition:

**Frontier lemma.** There is an explicit integer rank schedule `r(X)` for
which

\[
 D_{r(X)}(X)=o(X).                                          \tag{20}
\]

The rank requirement prevents (20) from being certified by unsupported
members of a merely forward-closed superset. Every term counted by `Q_r`
comes with a finite, bounded-height seed-rooted witness tree.

A still more flexible exact target allows additional scales. If fixed
rational numbers `alpha_i >= 0` and integers `q_i >= 2` satisfy

\[
 D_{r(X)}(X)\le
 \sum_i\alpha_i M\!\left(\left\lfloor{X+1\over q_i}\right\rfloor\right)
 +o(X)                                                       \tag{21}
\]

and the rational gate

\[
 {1\over2}+{1\over3}+\sum_i{\alpha_i\over q_i}<1,          \tag{22}
\]

then `M(X)=o(X)`. Indeed, for
`delta=limsup M(X)/X`, equations (19)-(22) and `E(X)=o(X)` give

\[
 \delta\le\left({5\over6}+\sum_i{\alpha_i\over q_i}\right)\delta,
\]

whose coefficient is strictly below `1`. This forces `delta=0`, and since
`A` has density `2/3`,

\[
 |G\cap[1,X]|={2X\over3}+o(X).
\]

Equivalently, the additional exact scale budget in (21) must be strictly
below `1/6`. Establishing (20) or (21) is the remaining proof problem. The
finite rank-9 census is a targeted falsification test, not its proof.

## 7. Reproduction and verification

From the repository root:

```powershell
g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave3/C17_hole_contraction/hole_contraction_redteam.cpp -o problems/424/compute/wave3/C17_hole_contraction/hole_contraction_redteam.exe
g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave3/C17_hole_contraction/hall_audit.cpp -o problems/424/compute/wave3/C17_hole_contraction/hall_audit.exe
problems/424/compute/wave3/C17_hole_contraction/hole_contraction_redteam.exe 1000000000 problems/424/compute/wave3/C17_hole_contraction/result_1e9.json
problems/424/compute/wave3/C17_hole_contraction/hall_audit.exe 54 problems/424/compute/wave3/C17_hole_contraction/hall_54.json
problems/424/compute/wave3/C17_hole_contraction/hall_audit.exe 1000000 problems/424/compute/wave3/C17_hole_contraction/hall_1e6.json
python problems/424/compute/wave3/C17_hole_contraction/grounding_audit.py problems/424/compute/wave3/C22_universal_contraction_sat/result_5000.json problems/424/compute/wave3/C17_hole_contraction/grounding_5000.json
python -m unittest -v problems/424/compute/wave3/C17_hole_contraction/verify_small.py
```

The final `10^9` scan took `161.494` seconds. The independent test suite has
four tests: naive all-pair/rank replay through `2000`, Hall replay through
`2000`, the exact `X=54` Hall witness, and byte-content replay of the C22
grounding audit.

SHA-256:

```text
hole_contraction_redteam.cpp  677CBD65FE1DA2E11C268A7806F95FE4192CDFBC2F8EF09B46ECD878118B94FA
hall_audit.cpp                 1AE77940A8E68146608A1D8415B2D0C0B378ABE01D2CD24DE4E2CF50976DEA79
grounding_audit.py             5EDADB06E66AF9855D82963882A22B7BDFCF7380468C176D5C572D0860405E07
verify_small.py                CD9C459AF809916C3A3BA3B5E49BAEE2DACDC553E83867A405DFC9385D8FE63A
result_1e9.json                00D6ED273487A97C31A01A727629A39F8D808B7BEFAF4853C47C1ECF92371543
hall_54.json                   4C4E4473EF3C851B3729E8E024A36928E9236E59B66885052088297E9FCF4C63
hall_1e6.json                  F5735FA963F41143E509A0CC405F98AAB9817B819C3A5C6EF753B33C02625DF1
grounding_5000.json            810AD17CCB5D02872A861B238B630CB4F5BFEB50E7E4FE3FB3B6DA281A5E4E39
```

The source C22 certificate has SHA-256
`2203EB637EFC1D66F03F77A2CFEEFA88DA70C3D58F37CFF89478616C7500A41B`,
which is also committed inside `grounding_5000.json`.
