# C43: critical-parent forest Euler audit

## Verdict

The proposed componentwise forest/Euler explanation is false. It does not
prove

\[
 H_{\le d}(X)\le Q_{\le d}(X)+1.                         \tag{AO}
\]

There is an exact counterexample at \((X,d)=(114,2)\). In every
critical-parent forest, two components have hard-minus-exit defect \(+1\).
Two other components have defect \(-1\), so the global defect is zero. Thus
the valid global count already uses cancellation between unrelated
components; it is not an Euler bound with one exceptional component.

At the first tight prefix \((362,2)\), even the maximal graph containing
every lower-rank blocker edge has positive component mass \(8\) and
negative component mass \(-7\). The observed global \(+1\) is their
difference, not a single component.

A second necessary-looking forest lemma is also false. For the hard hole
\(774\) of rank \(2\), the unique critical blocker is \(155\) of rank \(1\),
but its seed-2 sibling \(309=2\cdot155-1\) is a hole of rank \(4\). Hence a
hard branch can enter a rank prefix while its distinguished seed-2
continuation lies two death layers beyond that prefix.

These are counterexamples to precise forest lemmas, not to (AO). No density
theorem is claimed.

A different, genuinely global restriction survives exact testing: if only
the first two healed seed-2 exits from each canonical C39 component are
retained, their pooled rank prefixes still satisfy additive-one through
\(2\cdot10^9\). This is finite evidence only and is not derived from an
Euler characteristic.

## 1. Definitions

Let

\[
 {\cal A}=\{n\ge2:n\not\equiv1\pmod3\},
\]

and let \(G\) be the least subset of \({\cal A}\) containing \(2,3\) and
closed under \(a,b\mapsto ab-1\) for distinct \(a<b\). Put
\({\cal M}={\cal A}\setminus G\). For an allowed \(n\), write

\[
 {\cal P}(n)=\{(a,b):2\le a<b,\ a,b\in{\cal A},\ ab=n+1\}.
\]

For a hole, use the C31 obstruction rank

\[
 \rho(n)=0\quad({\cal P}(n)=\varnothing),
\]

\[
 \rho(n)=1+\max_{(a,b)\in{\cal P}(n)}
   \min\{\rho(x):x\in\{a,b\}\cap{\cal M}\}.              \tag{1}
\]

A hard hole is a reducible even hole outside the usable seed-3 class. A
target is a hole \(q\) for which \(2q-1\) is generated; it occurs at child
coordinate \(2q-1\) and has rank \(\rho(q)\).

For a hard hole \(h\) of rank \(r\), call a missing factor \(p\) critical
if some pair in \({\cal P}(h)\) has blocker score \(r-1\) and

\[
                         \rho(p)=r-1.                    \tag{2}
\]

Equation (1) guarantees at least one such \(p\).

## 2. The critical-parent forest

Choose one parent for every nonsplitless hole as follows:

\[
 \pi(n)=\frac{n+1}{2}\quad(n\text{ odd}),                \tag{3}
\]

\[
 \pi(n)=\frac{n+1}{3}\quad(n\text{ seed-3-easy even}),   \tag{4}
\]

and, for a hard \(n\), let \(\pi(n)\) be any critical factor from (2).

### Lemma 1

The directed graph \(\pi(n)\to n\) is a forest rooted at splitless holes.
Every parent is a smaller hole and has strictly lower rank.

### Proof

For (3), if \((n+1)/2\) were generated, the seed pair with \(2\) would
generate \(n\). The pair also gives strict rank increase in (1). The same
argument with seed \(3\) proves the assertion for (4). A critical parent is
missing by definition, is a proper factor of \(n+1\), and has rank
\(\rho(n)-1\). Values strictly increase along every directed edge, so
there is no cycle. Every nonsplitless hole has exactly one chosen parent.
QED.

For fixed \(X,d\), the vertices

\[
 V_{X,d}=\{n\in{\cal M}:n\le X,\ \rho(n)\le d\}
\]

are parent-closed. For a component \(C\) of the induced forest, let

\[
 h_C=\#\{h\in C:h\le X,\ h\text{ hard},\rho(h)\le d\},
\]

\[
 q_C=\#\{q\in C:2q-1\le X,\ 2q-1\in G,\rho(q)\le d\}.
\]

The precise single-component Euler proposal is

\[
 \boxed{\ \sum_C (h_C-q_C)_+\le1.\ }                    \tag{FE}
\]

This is sufficient for (AO), since

\[
 H_{\le d}(X)-Q_{\le d}(X)
   =\sum_C(h_C-q_C)
   \le\sum_C(h_C-q_C)_+.
\]

It also formalizes the intended interpretation: hard even roots are the
extra branch events, healed seed-2 boundaries are exits, and at most one
unit of component Euler defect remains.

## 3. Exact counterexample to (FE)

At \((X,d)=(114,2)\), exact trial division gives the complete event sets

\[
 \{h:\ h\text{ hard},\rho(h)\le2,h\le114\}
   =\{54,74,114\},                                      \tag{5}
\]

\[
 \{2q-1:\ q\text{ is a target parent},\rho(q)\le2,
                         2q-1\le114\}
   =\{41,69,77\}.                                       \tag{6}
\]

The hard factorizations are

\[
 55=5\cdot11,\qquad75=5\cdot15,\qquad115=5\cdot23.
\]

Each is the unique admissible split, \(5\) is generated, and the other
factor is a rank-one hole. Thus all three critical-parent choices are
forced.

The five components carrying events are:

| splitless anchor | rank-filtered hole vertices carrying the paths | hard events | target children | defect |
|---:|---|---|---|---:|
| \(6\) | \(6,11,21,32,54\) | \(54\) | \(41\), parent \(21\) | \(0\) |
| \(8\) | \(8,15,29,74\) | \(74\) | none | \(+1\) |
| \(12\) | \(12,23,45,68,114\) | \(114\) | none | \(+1\) |
| \(18\) | \(18,35\) | none | \(69\), parent \(35\) | \(-1\) |
| \(20\) | \(20,39\) | none | \(77\), parent \(39\) | \(-1\) |

All other components have defect zero. Consequently

\[
 \sum_C(h_C-q_C)_+=2>1,                                 \tag{7}
\]

while

\[
 H_{\le2}(114)-Q_{\le2}(114)=3-3=0.
\]

This is an exact counterexample to (FE). Since every hard parent in (5) is
forced, changing the critical-parent selection cannot repair it.

## 4. Why the tight \(+1\) is not one component

The counterexample survives a stronger connectivity rule. Let
\(\Gamma_{X,d}\) contain the forced seed-2 and seed-3 edges and, for every
hard hole, an edge to every missing factor of strictly lower rank. Every
critical-parent forest is a subgraph of \(\Gamma\); hence its component
partition refines the component partition of \(\Gamma\).

For signed component totals, refinement cannot decrease

\[
                    \sum_C(h_C-q_C)_+.                  \tag{8}
\]

At the first tight prefix \((X,d)=(362,2)\), the exact component defects in
\(\Gamma\) are

\[
 +5,+1,+1,+1,\quad -1,-1,-1,-1,-1,-1,-1,
\]

with all remaining components zero. Therefore

\[
 \sum_C(h_C-q_C)_+=8,\qquad
 \sum_C\min(h_C-q_C,0)=-7,                              \tag{9}
\]

and only after cross-component cancellation do we obtain

\[
 H_{\le2}(362)-Q_{\le2}(362)=8-7=1.                    \tag{10}
\]

Thus every critical-parent forest has positive component mass at least
eight at this prefix. The additive constant one cannot be identified with
one exceptional death component.

## 5. Rank-truncated sibling obstruction

One might try to recover an Euler argument by requiring every hard branch
to retain its seed-2 sibling in the same rank prefix:

> For every hard \(h\) of rank \(r\), there is a critical parent \(p\)
> such that \(T(p)=2p-1\) is generated, or is a hole of rank exactly \(r\).

The equality is forced because seed-2 monotonicity already gives
\(\rho(T(p))\ge\rho(p)+1=r\) when \(T(p)\) is a hole. Also \(T(p)<h\):
the other factor in the odd product \(h+1\) is at least three.

The claim first fails at \(h=774\). Its only admissible factorization is

\[
                       775=5\cdot155.
\]

Exact ranks are

\[
 \rho(155)=1,\qquad \rho(774)=2,\qquad \rho(309)=4,
\]

and \(309=2\cdot155-1\) is a hole. Thus the unique critical branch
\(155\to774\) is present at rank cutoff two, but its seed-2 continuation
lies at rank four and is not a healed exit. A rank-filtered Euler count
must carry transient frontier leaves in addition to the \(Q\) exits.

## 6. Exact computation

The primary checker reconstructs the least grounded set in ascending order
using exact divisors, computes (1), and checks every integer cutoff and
every rank through \(100000\). It tests minimum and maximum
critical-parent forests, the graph of all critical edges, and the graph of
all lower-rank blocker edges.

The census is

~~~text
holes        = 26,823
hard         = 5,108
targets      = 6,783
maximum rank = 12
~~~

All four models first violate (FE) at \((114,2)\). Through \(100000\), the
maximum positive component masses are respectively

~~~text
canonical minimum parent  2,625
canonical maximum parent  2,541
all critical edges         2,490
all lower-rank blockers    2,373
~~~

The same run finds \(400\) healed critical sibling choices, \(5493\)
unit-rank hole siblings, and \(99\) larger-rank hole siblings; the first
larger jump is the witness at \(774\).

The independent checker uses literal trial divisors and separately iterates
the descending grounded approximants. Through \(1000\), the approximants
stabilize after seven updates and have zero membership or death-rank
mismatches. It reproduces the first failure \((114,2)\), the full
five-component witness, (9)-(10), and the ranks at \(774\).

These computations do not falsify (AO). The primary sweep still has
maximum global excess one, in agreement with C31/C40.

## 7. Strongest surviving global finite gate

Return here to the canonical C39 forest, in which odd holes have their
seed-2 parent, seed-3-easy even holes have their seed-3 parent, and
splitless and hard holes are roots. Order the healed seed-2 exits in each
canonical component by child coordinate. Let \(Q^{(2)}_{\le d}(X)\) count
only the first two exits of each component whose child is at most \(X\)
and whose parent rank is at most \(d\).

The exact C++ scan found

\[
 H_{\le d}(X)\le Q^{(2)}_{\le d}(X)+1                  \tag{11}
\]

at every integer cutoff and every rank through \(X=2\cdot10^9\). Its
terminal census is

~~~text
hard roots                    55,529,425
all healed seed-2 exits      108,981,513
selected first-two exits     108,888,585
maximum rank                          22
forest decomposition failures          0
maximum rank-prefix excess              1
additive-one failure events             0
~~~

The maximum in (11) first occurs at \((362,2)\). Retaining only the first
exit per component is false: its first additive-one failure is

\[
 (X,d)=(1002,3),\qquad H_{\le3}=35,\qquad Q^{(1)}_{\le3}=33. \tag{12}
\]

The independent trial-divisor implementation through \(5000\) agrees with
the C++ hard, target, root, cap-one, and cap-two fields. It also checks
literal death stages and \(45000\) instances of the corrected odd-parent
seed-3 potential identity.

Statement (11) remains unproved. It pools exits from all components, so
the counterexamples (7) and (9) do not falsify it. Conversely, (9) shows
why (11) cannot follow by bounding each component's positive Euler defect:
at its first tight prefix, at least eight units of positive component mass
must be canceled by seven units transported from other components.

## 8. Relation to the earlier forest lane

C39 supplies the canonical seed-2/seed-3 decomposition. There is one
necessary parity correction to its proposed scalar potential: only odd hole
parents give canonical seed-3 edges. If \(M_d,O_d,E,H_d,Q_d\) count,
respectively, rank-at-most-\(d\) holes, odd such holes, splitless holes,
hard holes, and seed-2 exits, then direct forest Euler counting gives

\[
\begin{aligned}
H_d(X)-Q_d(X)
={}&M_d(X)-E(X)-M_d(\lfloor(X+1)/2\rfloor)\\
 &-O_d(\lfloor(X+1)/3\rfloor)+R_{3,d}(X)
   +A_{2,d}(X)+A_{3,d}(X),                              \tag{13}
\end{aligned}
\]

where \(R_{3,d}\) counts generated seed-3 exits and \(A_{j,d}\) counts
edges from rank at most \(d\) to holes above rank \(d\); the seed-3 terms
use odd parents only. The independent verifier checks (13) at all \(45000\)
cutoff-rank pairs through \(5000\).

Using all seed-3 parents is false already at \((X,d)=(23,1)\):
\(23=T_2(12)=T_3(8)\) is a hole of rank one. The unrestricted two-map graph
therefore has a second parent and is a DAG, not a forest.

C39's source \(74\) shows that compatible credit can come from unrelated
canonical components. C43 allows hard roots to attach to critical
lower-rank blockers, which is the natural additional edge needed to turn
hard roots into branch events.

The exact counterexample (7) shows that this enlargement is still
insufficient. Even the maximal lower-rank blocker graph needs positive and
negative component cancellation. The remaining statement must carry
global transport between components; a component Euler characteristic,
with or without a single exceptional component, cannot prove it.

The official Problem 424 page remains open and lists no partial solution.
No claim of (AO), \(H(X)\le Q(X)+1\), or \(H(X)\le Q(X)+o(X)\) is made
here.

## 9. Reproduction and hashes

From the repository root:

~~~powershell
python problems/424/compute/wave4/C43_forest_euler/audit_forest.py --limit 100000 --output problems/424/compute/wave4/C43_forest_euler/result_100k.json

python problems/424/compute/wave4/C43_forest_euler/verify_trial.py --limit 1000 --output problems/424/compute/wave4/C43_forest_euler/verify_trial_1000.json

g++ -O3 -std=c++20 -Wall -Wextra -pedantic problems/424/compute/wave4/C43_forest_euler/forest_exit_cap.cpp -o problems/424/compute/wave4/C43_forest_euler/forest_exit_cap.exe

problems/424/compute/wave4/C43_forest_euler/forest_exit_cap.exe 2000000000 problems/424/compute/wave4/C43_forest_euler/forest_exit_cap_2e9.json

python problems/424/compute/wave4/C43_forest_euler/verify_forest_euler.py --limit 5000 --cpp-json problems/424/compute/wave4/C43_forest_euler/forest_exit_cap_5000.json --output problems/424/compute/wave4/C43_forest_euler/verify_forest_5000.json
~~~

SHA-256:

~~~text
audit_forest.py        C3035A65EF6B47D42DF8BAFA030A858AAC8429DDF5F98D9914E508655A9A5D34
result_100k.json       968243D3C4C251968C2288DCED1386DFED892CFAE084EE9ACE95E2A15F73C304
verify_trial.py        13A0683A5ABAABD754CC97207E9F4A320C300BE2210F81527034EFB5C9626A95
verify_trial_1000.json 09AD4C7B835F329BADAA9E642B1F9FF33659D9A08FCE57A2AD5870B546400807
forest_exit_cap.cpp    620D2C00ADC2A7C435D81F5C9553632D080FD96139F589ADF75CC4DE9B32E828
forest_exit_cap_2e9.json B021FC80A1961ED4E8B1FEBFE6533D0D0E19E155B2610EE40B2344DAEA1DDDA5
verify_forest_euler.py 8589E428CE3D6B6762651A2DAACF086AF35297966D4EF3CE0C3971447860F6D6
verify_forest_5000.json 7A2B4FB4381F2EA4F9F87C9E19E633D7CCE29FCFACBD8F85D27EF29B7A2EA442
~~~
