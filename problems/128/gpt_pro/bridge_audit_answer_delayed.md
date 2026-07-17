## Verdict

**GO for the proposed (n=20) search.** The certificate-to-problem bridge is exact, not merely sufficient. I found no elementary obstruction, nor a consequence of the currently recorded sparse-half results, that makes the (n=20) instance provably unsatisfiable before an exact finite search. The current problem entry still records only partial results of the conjecture. ([[erdosproblems.com](https://www.erdosproblems.com/latex/128)][1])

There is one qualification: **if the order is still freely selectable and only one order (n\le20) will be searched, (n=14) is a better arithmetic and computational one-shot than (n=20)**. That is not a logical reduction between the two orders; a counterexample at (20) need not induce one at (14).

## 1. The (n=20) certificate bridge is completely correct

Let (V=[20]). Then

[
\left\lfloor \frac{20}{2}\right\rfloor=10,
\qquad
\frac{20^2}{50}=8.
]

Since an edge count is integral,

[
e(G[S])>8 \quad\Longleftrightarrow\quad e(G[S])\ge 9.
]

Moreover, checking only the (10)-sets is both necessary and sufficient:

* Necessity is immediate because the original quantifier includes all induced subgraphs on exactly (10) vertices.
* Conversely, if every (10)-set (S) has (e(S)\ge9), then for every (U\subseteq V) with (|U|\ge10), choose any (S\subseteq U) with (|S|=10). Since (E(G[S])\subseteq E(G[U])),

[
e(G[U])\ge e(G[S])\ge9>8.
]

The right-hand side is (n^2/50) for the ambient (20)-vertex graph, not (|U|^2/50). Thus no changing threshold is hidden in the monotonicity argument. This matches the current statement of Problem #128. ([[erdosproblems.com](https://www.erdosproblems.com/latex/128)][1])

The instance counts are also right:

[
\binom{20}{2}=190,\qquad
\binom{20}{3}=1140,\qquad
\binom{20}{10}=184756,\qquad
\binom{10}{2}=45.
]

Therefore a satisfying labelled graph would, by itself, be a finite counterexample to the universal statement.

## 2. Strong pre-SAT restrictions—but no contradiction

Several useful restrictions can be proved before search.

### The graph has at least (39) edges

Write (M=e(G)). For a uniformly random (10)-set (S),

[
\mathbb E e(G[S])
=M\frac{\binom{18}{8}}{\binom{20}{10}}
=\frac{9M}{38}.
]

Since every such set has at least (9) edges, initially (M\ge38).

In fact (M=38) is impossible. Fix a vertex (v) of degree (d_v).

For a random (10)-set avoiding (v),

[
\mathbb E e(S)=\frac5{19}(M-d_v)\ge9,
]

so (M-d_v\ge35). If (M=38), this gives (d_v\le3).

For a random (10)-set containing (v), an incident edge is present with probability (9/19), while a nonincident edge is present with probability (4/19). Hence

[
\frac{9d_v+4(M-d_v)}{19}
=\frac{4M+5d_v}{19}\ge9.
]

For (M=38), this gives (d_v\ge4), a contradiction. Therefore

[
\boxed{e(G)\ge39.}
]

### The maximum degree is at most (7)

Let (v) have degree (d), and put (A=N(v)). Since (G) is triangle-free, (A) is independent.

If (d\ge10), any ten neighbors of (v) form an independent (10)-set, immediately impossible.

If (d=9), put

[
R=V\setminus\bigl(A\cup{v}\bigr),\qquad |R|=10.
]

For (x\in R), the (10)-set (A\cup{x}) has exactly (d_A(x)) edges, so (d_A(x)=9). Thus every (x\in R) is complete to (A). Consequently (R) is independent—an edge in (R) would form triangles with every vertex of (A)—contradicting the condition on (R).

Suppose (d=8). Now (|A|=8) and (|R|=11). Define

[
a_x=|N(x)\cap A|\qquad(x\in R).
]

The set (A\cup{v,x}) has (8+a_x) edges, so (a_x\ge1). For (x,y\in R),

[
e\bigl(A\cup{x,y}\bigr)=a_x+a_y+\mathbf1_{xy}\ge9.
]

Vertices with (a_x\le4) must be pairwise adjacent, since otherwise their sum is at most (8). Triangle-freeness therefore allows at most two such vertices. At least nine vertices of (R) have (a_x\ge5). No two of those nine can be adjacent, because adjacent vertices have disjoint neighborhoods in (A), which would imply (a_x+a_y\le8). Those nine vertices together with (v) form an independent (10)-set.

Hence

[
\boxed{\Delta(G)\le7.}
]

### What the known sparse-half theorems add

Razborov proved the conjecture for triangle-free graphs whose independence number is at least (2n/5), and also for graphs of girth at least (5). Thus an (n=20) candidate must satisfy

[
\alpha(G)\le7
]

and must contain a (4)-cycle. Since (R(3,6)=18), every triangle-free graph on (20) vertices has an independent (6)-set, so necessarily

[
\boxed{\alpha(G)\in{6,7}.}
]

Razborov’s general bound only guarantees a (10)-set with at most

[
\frac{27}{1024},20^2=10.546875
]

edges, hence at most (10) edges after integrality; that does not contradict a minimum of (9). ([[arXiv](https://arxiv.org/abs/2104.09406)][2])

Bedenknecht, Mota, Reiher and Schacht proved the sparse-half assertion when

[
\delta(G)>\frac{10n}{29}.
]

At (n=20), this excludes (\delta(G)\ge7). Therefore a candidate has (\delta(G)\le6). Together with (\Delta(G)\le7),

[
2e(G)\le 19\cdot7+6=139.
]

The degree sum is even, so

[
\boxed{e(G)\le69.}
]

Thus every candidate lies in the nonempty-looking window

[
\boxed{39\le e(G)\le69,\quad
\Delta\le7,\quad\delta\le6,\quad
\alpha\in{6,7},\quad C_4\subseteq G.}
]

The Keevash–Sudakov edge-density cases do not close this interval: their recorded theorem handles (e(G)\le n^2/12), which here means (e\le33), and (e(G)\ge n^2/5=80). ([[erdosproblems.com](https://www.erdosproblems.com/history/128)][3])

These restrictions are strong search cuts, but they are not contradictory.

### The recent (n^2/25) max-cut result does not settle this instance

A very recent, computer-assisted June 2026 preprint states that every triangle-free graph on (20) vertices can be made bipartite by deleting at most (16) edges. Equivalently, there is some partition (V=A\cup B) such that

[
e(A)+e(B)\le16.
]

But that partition need not be (10+10). ([[arXiv](https://arxiv.org/html/2606.28041v1)][4])

Indeed, let (|A|=a\le b=|B|). Every (10)-subset of (B) has at least (9) edges, so averaging gives

[
e(B)\ge
\left\lceil
9\frac{\binom b2}{\binom{10}2}
\right\rceil
============

\left\lceil\frac{\binom b2}{5}\right\rceil.
]

A balanced (10+10) partition would have at least (9+9=18) internal edges, and (b\ge14) would force (e(B)\ge19). The max-cut theorem therefore narrows the possible partition sizes to

[
\begin{array}{c|c}
(a,b)&\text{remaining numerical possibility}\ \hline
(7,13)&e(A)=0,\ e(B)=16,\
(8,12)&e(A)\le2,\ e(B)\ge14,\
(9,11)&e(A)\le5,\ e(B)\ge11.
\end{array}
]

It does not by itself eliminate these residual cases. Thus even this newest finite consequence is not a pre-SAT refutation of the proposed instance.

## 3. If the order is free, (n=14) is the better single shot

For general (n), put

[
m_n=\left\lfloor\frac n2\right\rfloor,
\qquad
q_n=\left\lfloor\frac{n^2}{50}\right\rfloor+1.
]

At (n=20),

[
m_{20}=10,\qquad q_{20}=9,
]

so the required density within a tested set is

[
\frac{q_{20}}{\binom{m_{20}}2}
=\frac9{45}
=\frac15.
]

The strict inequality has imposed a full one-edge rounding penalty:

[
9-\frac{20^2}{50}=1.
]

At (n=14),

[
m_{14}=7,\qquad
\frac{14^2}{50}=3.92,\qquad
q_{14}=4.
]

The corresponding quantities are

[
\frac{q_{14}}{\binom72}
=\frac4{21}
\approx0.190476<0.2,
]

and

[
4-\frac{14^2}{50}=\frac2{25}=0.08.
]

The ambient normalized threshold is also closer to the conjectured (1/50):

[
\frac4{14^2}=\frac1{49}
<\frac9{20^2}=\frac9{400}.
]

A direct check of the nontrivial orders through (20) shows that (4/21) is the unique minimum of (q_n/\binom{m_n}{2}) in that range. The (n=14) exact instance is also much smaller:

[
\begin{array}{c|c|c}
&n=14&n=20\ \hline
\text{edge variables}&91&190\
\text{triangle constraints}&364&1140\
\text{tested subsets}&3432&184756\
\text{variables per subset constraint}&21&45.
\end{array}
]

There is an additional exact structural advantage. Razborov’s independence-number result implies that an (n=14) candidate has (\alpha\le5), while (R(3,5)=14) gives (\alpha\ge5). Hence

[
\alpha(G)=5.
]

Every candidate is therefore a Ramsey((3,6,14))-graph. McKay’s complete Ramsey graph data contain exactly (263,520) such catalogued graphs, so the (n=14) experiment can be implemented as an exhaustive scan of an existing complete finite family, checking the (3432) seven-sets of each graph. ([[arXiv](https://arxiv.org/abs/2104.09406)][2])

It also has simple pruning:

[
e(G)\ge18,\qquad \Delta(G)\le5,\qquad\delta(G)\le4,
\qquad e(G)\le34.
]

For example, (\Delta\le5) follows because degree at least (7) supplies seven independent neighbors, while if (d(v)=6), every nonneighbor (x) must have at least four neighbors in (N(v)). Two such nonneighbors cannot be adjacent, so the seven nonneighbors form an independent seven-set.

Thus:

* **Operationally:** (n=14) is strictly better than (n=20) in rounding distortion, normalized local threshold, instance size, and availability of a complete Ramsey catalogue.
* **Logically:** neither order dominates the other. An (n=20) counterexample need not yield an (n=14) counterexample.

## 4. Sound exact (n=20) encoding

Introduce

[
x_{ij}\in{0,1}\qquad(1\le i<j\le20),
]

where (x_{ij}=1) means (ij\in E(G)).

### Core constraints

For every (i<j<k),

[
x_{ij}+x_{ik}+x_{jk}\le2.
]

In CNF this is

[
\neg x_{ij}\lor\neg x_{ik}\lor\neg x_{jk}.
]

For every (S\in\binom{[20]}{10}),

[
\sum_{{i,j}\in\binom S2}x_{ij}\ge9.
]

Equivalently,

[
\sum_{{i,j}\in\binom S2}(1-x_{ij})\le36.
]

These are the entire necessary-and-sufficient core.

### Provably safe redundant constraints

The elementary deductions above justify adding

[
\sum_{i<j}x_{ij}\ge39
]

and, for every vertex (v),

[
\sum_{u\ne v}x_{\min{u,v},\max{u,v}}\le7.
]

If the cited known theorems are admitted as preprocessing, one may also add:

[
\sum_{{i,j}\in\binom T2}x_{ij}\ge1
\qquad
\text{for every }T\in\binom{[20]}8,
]

encoding (\alpha(G)\le7).

It is also existence-preserving to restrict to **maximal triangle-free graphs**. Starting from any candidate, repeatedly add an edge whenever doing so creates no triangle. Triangle-freeness is preserved and every induced edge count can only increase.

Maximal triangle-freeness says that every nonedge (ij) has a common neighbor. With auxiliary variables (y_{ijk}), it can be encoded by

[
x_{ij}\ \lor\ \bigvee_{k\ne i,j}y_{ijk},
]

together with

[
y_{ijk}\rightarrow x_{ik},
\qquad
y_{ijk}\rightarrow x_{jk}.
]

No assumption of regularity, vertex-transitivity, circulancy, connectedness without the maximal-extension argument, or a (C_5)/Petersen blow-up is safe.

### Provably safe symmetry breaking

The simplest one-instance symmetry constraint is degree ordering. Define

[
d_i=\sum_{j\ne i}x_{\min{i,j},\max{i,j}}
]

and impose

[
d_1\ge d_2\ge\cdots\ge d_{20}.
]

Every graph has at least one relabelling with nonincreasing degrees, so this removes no isomorphism class. With this convention one may add (d_1\le7) and, using the minimum-degree theorem, (d_{20}\le6).

A stronger exhaustive alternative is to branch over

[
\Delta(G)\in{4,5,6,7},
]

where the lower bound (4) follows from (e(G)\ge39). In the branch (\Delta=d), safely label a maximum-degree vertex as (1), fix

[
x_{1j}=1\quad(2\le j\le d+1),
\qquad
x_{1j}=0\quad(d+2\le j\le20),
]

and impose (d_v\le d) for every (v). Vertices may then be degree-sorted separately inside (N(1)) and its complement. All four branches must be searched; equivalently they may be combined using selector variables in one PB instance.

One should not simultaneously fix, for example, vertices (1,\dots,6) as an independent set and vertex (1) as a maximum-degree vertex without branching over their possible incidence: each choice is separately safe, but their conjunction need not represent every isomorphism class.

## 5. Lazy separation is exact

The proposed lazy implementation is sound:

1. Solve the current triangle-free PB/SAT master.
2. For the returned (190)-bit graph, enumerate all (184756) ten-sets.
3. For every set (S) with (e(S)\le8), add the original exact constraint
   [
   \sum_{\binom S2}x_{ij}\ge9.
   ]
4. Repeat.

Every added cut belongs to the full formulation. No valid candidate is removed. Since a model cannot violate an already-enforced cut, at most (184756) distinct separation cuts can be added. If a model has no violation, its edge vector is the required terminal certificate.

For proof-grade computation:

* A satisfying edge list should be checked independently by enumerating all (1140) triples and all (184756) ten-sets.
* An unsatisfiability claim should use an exact CNF cardinality encoding with LRAT/DRAT output, or an exact PB proof format such as VeriPB. Floating-point MILP infeasibility is not an adequate mathematical certificate.
* Symmetry-broken UNSAT requires either one proven orbit-covering formulation or UNSAT in every exhaustive symmetry branch.

## Bottom line

[
\boxed{\textbf{GO at }n=20.}
]

The bridge, rounding, quantifiers, clause counts and lazy-separation logic are all correct. The best known finite and structural results sharply restrict a candidate but do not presently force impossibility.

If the single order is not already fixed, the better exact finite experiment is

[
\boxed{n=14:\quad \text{triangle-free and every seven-set has at least four edges}.}
]

That recommendation is based on exact arithmetic, exact instance size and the complete Ramsey((3,6,14)) catalogue—not on a claimed implication between orders.

[1]: https://www.erdosproblems.com/latex/128 "https://www.erdosproblems.com/latex/128"
[2]: https://arxiv.org/abs/2104.09406 "https://arxiv.org/abs/2104.09406"
[3]: https://www.erdosproblems.com/history/128 "https://www.erdosproblems.com/history/128"
[4]: https://arxiv.org/html/2606.28041v1 "https://arxiv.org/html/2606.28041v1"
