# C24: derivation-aware matching

## Verdict

The requested healed-missing-factor gate is false at the first hard hole.
For \(n=54\), the only admissible split is

\[
54+1=5\cdot 11.
\]

Here \(5\in G\), \(11\notin G\), and \(2\cdot11-1=21\notin G\).
Thus \(54\) has no missing factor whose seed-2 child is generated. In the
corresponding bipartite graph the singleton \(\{54\}\) has no neighbor.

The smallest surviving member of a nested obstruction-rank Hall family uses
rank offset \(1\). It has no deficit at any cutoff through \(10^6\), but it
is a finite-data conjecture, not a proved lemma.

## Capacity identity

Let \(H_X\) be the hard even reducible holes. Let \(O_X\) be the odd
reducible holes, and put

\[
Q_X=\{q\le\lfloor(X+1)/2\rfloor:q\notin G,\ 2q-1\in G\}.
\]

Every hole \(q\le\lfloor(X+1)/2\rfloor\) has allowed seed-2 child \(2q-1\).
That child is either generated, putting \(q\) in \(Q_X\), or is an odd
reducible hole. The maps \(q\mapsto2q-1\) and
\(n\mapsto(n+1)/2\) are inverse. Hence, exactly,

\[
M(\lfloor(X+1)/2\rfloor)=|O_X|+|Q_X|.                 \tag{1}
\]

The remaining nonhard even reducible holes have the injective missing
seed-3 parent \(q=(n+1)/3\). Therefore

\[
|H_X|\le |Q_X|
\quad\Longrightarrow\quad
R(X)\le M(\lfloor(X+1)/2\rfloor)
       +M(\lfloor(X+1)/3\rfloor).                     \tag{2}
\]

Thus C16's odd+hard<=Mhalf is exactly the assertion that the hard demand
fits into the healed capacity.

## First counterexample

The independent trial-division closure through \(54\) is

    2, 3, 5, 9, 14, 17, 26, 27, 33, 41, 44, 50, 51, 53.

The local facts are forced:

* \(6\) is splitless because \(6+1=7\).
* The only allowed split of \(11+1=12\) is \(2\cdot6\), so \(11\notin G\).
* The only split of \(21+1=22\) is \(2\cdot11\), so \(21\notin G\).
* The only split of \(54+1=55\) is \(5\cdot11\). Since
  \(5=2\cdot3-1\in G\), \(54\) is reducible; it is even and \(55\) is not
  divisible by \(3\), so it is hard.

With splitless obstruction rank \(0\) and

\[
\rho(n)=1+\max_{ab=n+1}\min_{\substack{q\in\{a,b\}\\q\notin G}}\rho(q),
                                                               \tag{3}
\]

the exact ranks are

    rho(6)=0, rho(11)=1, rho(21)=2, rho(54)=2.

At \(X=54\), the ten half-scale holes split into nine seed-2 parents of odd
holes and the one healed hole \(21\):

    half holes: 6, 8, 11, 12, 15, 18, 20, 21, 23, 24
    odd children: 11, 15, 21, 23, 29, 35, 39, 45, 47
    healed holes: 21

The healing witness is grounded:

\[
5=2\cdot3-1,\qquad14=3\cdot5-1,\qquad41=3\cdot14-1=2\cdot21-1.
\]

But \(21\) is unrelated to the factorization of \(55\). The proposed graph
restricts \(54\) to the missing endpoint \(11\), which is not healed.
Consequently

\[
N(\{54\})=\varnothing,\qquad |\{54\}|-|N(\{54\})|=1.             \tag{4}
\]

Least-missing-factor choice, rank priority, and alternating paths cannot
repair a zero-degree left vertex.

## Natural factor matching failures

An independent trial-division oracle built the exact direct missing-endpoint
graph and ran maximum bipartite matching at every cutoff. An alternating
path from every unmatched left vertex supplied the following exact Hall
witnesses.

With one half-scale copy, the first failure is \(X=32\):

    left: 21, 32
    neighbors: (half,11)

Both holes have the sole missing factor \(11\), so the deficit is \(2-1=1\).

Choosing only the least missing endpoint but allowing half and third copies
first fails at \(X=39\):

    left: 15, 23, 39
    neighbors: (half,8), (third,8)

Allowing every direct missing endpoint delays the two-copy failure only to
\(X=54\):

    left: 21, 32, 54
    neighbors: (half,11), (third,11)

Thus an exact alternating-path matcher, and hence any rank-prioritized or
greedy ordering on the same edges, cannot produce the desired injection.

Finally, recursively close each left neighborhood under missing endpoints:
if \(q\) is available, include every missing endpoint in every obstruction
of \(q\), continuing to splitless leaves. Even this transitive obstruction
shadow first fails at \(X=186\):

    left: 11, 21, 32, 54, 186
    neighbors: (half,6), (half,11), (third,6), (third,11)

Here \(11\) descends to splitless \(6\), while the other four holes descend
through \(11\). The two scale copies of \(\{6,11\}\) give only four targets
for five sources. These failures are recorded in natural_2000.json and
independently asserted by verify_small.py.

## Smallest surviving Hall statement

For \(k\ge0\), define a nonlocal grounded graph from \(H_X\) to \(Q_X\) by

\[
n\sim_k q\quad\Longleftrightarrow\quad \rho(q)\le\rho(n)+k.      \tag{5}
\]

Its neighborhoods are nested. Hall's condition is therefore equivalent
to the prefix inequalities

\[
|\{n\in H_X:\rho(n)\le d\}|
\le
|\{q\in Q_X:\rho(q)\le d+k\}| \quad\hbox{for every }d.           \tag{6}
\]

Indeed, a left subset whose largest rank is \(d\) has at most the left side
of (6) and has the right side as its available rank prefix. Conversely,
the full left rank prefix gives necessity. Thus (6) gives a matching
\(H_X\hookrightarrow Q_X\), and (1)-(2) prove the C16 contraction.

Offset \(k=0\) is false. Its first Hall deficit is at \(X=362,d=2\):

    left (11):
    54, 74, 114, 174, 186, 234, 252, 294, 318, 354, 362

    neighbors (10):
    21, 35, 39, 66, 75, 110, 117, 119, 120, 126

Offset \(k=1\) is the smallest member of (5) surviving the exact audit.
Through \(X=10^6\), all \(113120\) event cutoffs pass. These events comprise
all \(45583\) hard-hole arrivals and all \(67537\) healed-hole arrivals, so
the rank prefixes are constant between them and every integer cutoff was
covered. Offsets \(1,\ldots,8\) have zero deficits; offset \(0\) has three,
with first and maximum excess \(1\) at \(X=362,d=2\).

The rank-\(1\) statement (6) is the smallest surviving Hall formulation
found here. No asymptotic proof of it is supplied.

## Census and reproduction

At \(X=10^6\), the C24 least-closure census exactly matches C16:

    generated=457599, missing=209067, splitless=108651
    reducible=100416, hard=45583
    direct healed-factor gate: pass=4336, fail=41247

Run:

    python problems/424/compute/wave3/C24_derivation_matching/healed_factor_gate.py --limit 1000000 --output problems/424/compute/wave3/C24_derivation_matching/result_1e6.json

    python problems/424/compute/wave3/C24_derivation_matching/verify_small.py

    python problems/424/compute/wave3/C24_derivation_matching/natural_matching_scan.py --limit 2000 --output problems/424/compute/wave3/C24_derivation_matching/natural_2000.json

The verifier uses trial division rather than the main oracle's SPF
factorization and reports 16/16 checks pass.
