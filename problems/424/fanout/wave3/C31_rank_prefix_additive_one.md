# C31: rank-prefix additive-one audit

## Verdict

The proposed additive-one inequality was not proved and was not falsified.
An exact grounded scan through `2,000,000,000` found

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1
\]

at every integer cutoff and every obstruction rank.  The corresponding
online dominance matching leaves exactly one hard source unmatched, namely
`362` of rank `2`.  This is finite evidence only.

The constant `1` is necessary.  The strict inequality

\[
 H_{\le d}(X)\le Q_{\le d}(X)
\]

first fails at `(X,d)=(362,2)`, where the two counts are `11` and `10`.
It fails at exactly three source events through `2*10^9`, at `X=362,1002,1014`,
always with excess one and rank cutoff two.

Three structural statements are proved below: obstruction rank is exactly
death rank in the descending grounded approximants; rank strictly increases
along a missing seed-2 chain; and the additive-one inequalities are exactly
Hall's conditions for a nested dominance graph with one dummy target.  These
statements identify the missing theorem but do not prove its Hall conditions.

A factor-local proof is impossible.  Even after every missing endpoint is
allowed to walk two seed-2 steps, the first zero-degree hard source is `74`.
At `10^6`, this enlarged local graph has `16,451` zero-degree sources and a
maximum matching of only `4,965` among `45,583` hard sources.  Any proof must
therefore use global grounded capacity rather than a bounded local map.

## 1. Definitions pinned to the artifacts

Let

\[
 \mathcal A=\{n\ge2:n\not\equiv1\pmod3\}
\]

and let `G` be the least subset of `mathcal A` containing `2,3` and closed
under `a,b -> ab-1` for distinct `a,b`.  For an allowed `n`, put

\[
 \mathcal P(n)=\{(a,b):2\le a<b,\ a,b\in\mathcal A,\ ab=n+1\}.
\]

Write `M=mathcal A\G`.  The obstruction rank of a hole is defined recursively
by

\[
 \rho(n)=0\quad\hbox{if }\mathcal P(n)=\varnothing,
\]

and, for a reducible hole,

\[
 \rho(n)=1+\max_{(a,b)\in\mathcal P(n)}
 \min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}.              \tag{1}
\]

Every pair in (1) has a missing endpoint, and all endpoints are smaller than
`n`, so this recursion is well founded.

A hard hole is a reducible even hole outside the usable seed-3 class.  Thus a
reducible even hole `n` is hard unless `3 | n+1` and
`q=(n+1)/3` is allowed and different from `3`.

For an integer cutoff `X` and rank cutoff `d`, define

\[
 H_{\le d}(X)=\#\{n\le X:n\text{ is hard},\ \rho(n)\le d\},             \tag{2}
\]

\[
 Q_{\le d}(X)=\#\{q\in\mathcal M:2q-1\le X,\ 2q-1\in G,
                                    \ \rho(q)\le d\}.                    \tag{3}
\]

The event coordinate of a target is its generated child `2q-1`, not its
parent `q`.  This is the convention used in `rank_1e9.json`, the C31 C++
scan, and the independent Python replay.

## 2. Obstruction rank equals death rank

Define descending approximants

\[
 S_0=\mathcal A,
\]

\[
 S_{t+1}=\{2,3\}\cup
 \{ab-1\in\mathcal A:a,b\in S_t,\ 2\le a<b\}.             \tag{4}
\]

Monotonicity of the operator in (4) gives `S_{t+1} subseteq S_t`.

### Lemma 1

For every hole `n`,

\[
 \rho(n)=r
 \quad\Longleftrightarrow\quad
 n\in S_r\setminus S_{r+1}.                               \tag{5}
\]

In particular, obstruction rank is death rank minus one in the convention
where stage one removes the splitless holes.

### Proof

If `P(n)` is empty, `n` lies in `S_0` but not in `S_1`, giving (5) for
rank zero.  Suppose `n` is reducible and put

\[
 R=\max_{(a,b)\in\mathcal P(n)}
   \min\{\rho(x):x\in\{a,b\}\cap\mathcal M\}.
\]

For every admissible pair, choose a missing endpoint of rank at most `R`.
By induction it is absent from `S_{R+1}`.  Hence no pair supports `n` in
`S_{R+1}`, and `n` is absent from `S_{R+2}`.

For a pair attaining the maximum, every missing endpoint has rank at least
`R`; generated endpoints belong to every approximant.  The induction
hypothesis therefore puts both endpoints in `S_R`, so this pair supports
`n` in `S_{R+1}`.  Thus `n` dies between `S_{R+1}` and `S_{R+2}`, while
(1) gives `rho(n)=R+1`.  This is (5).  QED.

Because all factors are strictly smaller than their output, an element that
survives every approximant has a finite seed-rooted derivation; hence
`intersection_t S_t=G`.  This is where the actual least grounded generation,
rather than arbitrary forward closure, enters.

## 3. Seed-2 chain monotonicity

Put `T(q)=2q-1`.

### Lemma 2

If `q` and `T(q)` are both holes, then

\[
 \rho(T(q))\ge \rho(q)+1.                                  \tag{6}
\]

Consequently, along every seed-2 chain the missing ranks strictly increase
until the chain reaches its generated tail.  Each chain has at most one
target counted by (3).

### Proof

The pair `(2,q)` is admissible for `T(q)`.  In this pair the only missing
endpoint is `q`, so its contribution to the maximum in (1) is `rho(q)`.
Equation (6) follows.  If one member of the chain is generated, closure with
the seed `2` generates every later member, proving the second assertion.
QED.

This monotonicity is not enough for a prefix injection: the final boundary
of the chain can occur after the hard source cutoff, and many hard sources
can depend on the same missing chain.

## 4. Exact nested-Hall formulation

For fixed `X`, form a bipartite graph with left side the hard holes through
`X`, right side the targets in (3) through `X` together with one dummy
vertex `star`, and edges

\[
 n\sim q\quad\Longleftrightarrow\quad \rho(q)\le\rho(n),
 \qquad n\sim\star\quad\hbox{for every }n.                 \tag{7}
\]

### Lemma 3

The graph (7) has a matching saturating every hard source if and only if

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1                            \tag{8}
\]

for every `d`.

### Proof

Necessity follows by applying Hall to the full left rank prefix.  Conversely,
take any left subset and let `d` be its largest rank.  Its size is at most
`H_{<=d}(X)`, while its neighborhood contains all `Q_{<=d}(X)` targets and
the dummy.  Equation (8) gives Hall's inequality.  QED.

Ordering all events by their integer coordinate gives an equivalent online
test.  Keep the available targets by rank; when a hard source of rank `r`
arrives, use the largest available target rank at most `r`, or use the dummy
once.  The largest-compatible choice is exchange-optimal because replacing
it by a smaller target can only reduce the options for a later lower-rank
source.  Hence this greedy process leaves at most one source unmatched at
every time exactly when (8) holds at every integer cutoff.

Lemma 3 is a reformulation, not a proof of (8).  In particular, the complete
dominance edges in (7) have no known derivation-local realization.

## 5. Exact local obstruction

The independent verifier tested the following enlarged local graph.  For a
hard source `n`, take every missing endpoint in every admissible factor pair.
From such an endpoint `q`, allow its first generated seed-2 boundary either
at `T(q)` or at `T^2(q)`, provided the target has arrived by `n` and its rank
does not exceed `rho(n)`.

This graph already has a zero-degree source at `n=74`.  Indeed,

\[
 74+1=5\cdot15,
\]

and `15,T(15)=29,T^2(15)=57` are all holes.  Thus even the two-step closure
of every direct missing endpoint supplies no target at this source.

At `X=10^6` the exact results are:

| graph | matched hard sources | unmatched | zero degree | edges |
|---|---:|---:|---:|---:|
| critical endpoints, two steps | 4,333 | 41,250 | 21,332 | 25,976 |
| all endpoints, two steps | 4,965 | 40,618 | 16,451 | 39,426 |

Therefore neither critical-factor choice, all-factor choice, nor a bounded
two-step seed-2 completion can prove (8).  The target capacity observed by
the dominance matching is genuinely global.

## 6. Exact census

The C++ scan reconstructs the least grounded set in ascending order, computes
generation and obstruction ranks, and checks every rank prefix whenever a
hard source arrives.  Targets are inserted at their child coordinates.  At
`X=2,000,000,000` it reports

```text
maximum generation depth  = 24
maximum obstruction depth = 22
hard sources              = 55,529,425
healed targets            = 108,981,513
strict failure events     = 3
additive-one failures     = 0
offset-one failures       = 0
greedy unmatched          = 1
```

The independent Python implementation through `10^6` obtains

```text
hard sources          = 45,583
healed targets        = 67,537
maximum excess        = 1 at X=362, d=2
strict failures       = (362,2), (1002,2), (1014,2)
additive-one failures = 0
greedy unmatched      = 362, rank 2
```

Since the `2*10^9` scan still has exactly three strict failures, no new
strict failure occurs after `1014` in that finite range.

This census cannot be extrapolated.  In particular, the global theorem (8)
would imply `H(X)<=Q(X)+1`, which inserted in C16's exact partition and C13's
splitless estimate would close the density problem.  It is therefore a
load-bearing theorem, not a routine consequence of the finite pattern.

## 7. Reproduction and hashes

From the repository root:

```powershell
python problems/424/compute/wave3/C31_rank_prefix_additive_one/verify_rank_prefix.py `
  --limit 1000000 `
  --output problems/424/compute/wave3/C31_rank_prefix_additive_one/result_1e6.json

g++ -O3 -std=c++20 -Wall -Wextra -pedantic `
  problems/424/compute/wave3/C31_rank_prefix_additive_one/rank_switch_2e9.cpp `
  -o problems/424/compute/wave3/C31_rank_prefix_additive_one/rank_switch_2e9.exe

problems/424/compute/wave3/C31_rank_prefix_additive_one/rank_switch_2e9.exe `
  2000000000 `
  problems/424/compute/wave3/C31_rank_prefix_additive_one/rank_2e9.json
```

SHA-256:

```text
verify_rank_prefix.py  6BBB739DD62537E7FDF42EEDA496019317C5B2763D313247B18E212E6725457D
result_1e6.json        B8FD175F46613B26FB75AC82EE350D452E993C76ACBBEF341ADA0E8FABFD7B0F
rank_switch_2e9.cpp    198EC134C7659EA43CF2807F1646A6023FB336AE0D8B1B1D0B5297EE04598581
rank_2e9.json          5BB139CDFDDC5E6FE3EE31133C5C143CBDEC7FBB62D3FDBC0893D0B68344BE19
```

## 8. Final status

There is no grounded counterexample through `2*10^9`, but there is also no
rigorous induction establishing the additive-one Hall condition.  The
smallest exact counterexample is to the zero-additive strengthening, at
`(362,2)`, and the additive constant one is the minimal surviving repair.
The requested asymptotic conclusion is not claimed.
