# Adversarial referee audit of the order-18 counting obstruction

## Verdict

**ACCEPT, with the scope stated exactly as follows.**  The argument in
`CONSTRUCTION_N18.md` proves that there is no oriented graph on 18 vertices
with minimum outdegree at least 8 for which

\[
  |N^{++}(v)|<|N^+(v)|
\]

holds for every vertex (v).  Equivalently, every such graph has a vertex
with at least as many strict second out-neighbours as out-neighbours.

This is a self-contained exact counting obstruction.  It is not, by itself,
a proof of the Second Neighbourhood Conjecture for all oriented graphs, nor
does it handle order-18 graphs whose minimum outdegree is at most 7.  Any
claim that another result supplies the latter case requires a separate audit
of that result.

Throughout this report, (N^{++}(v)) means the **strict/new** second
out-neighbourhood: vertices reached by a directed path of length two after
removing (N^+(v)) (and (v)).  This is the standard SSNC convention and is
the convention required by the source-deficit count below.

## Independent reconstruction

Let (D) be an oriented graph on 18 vertices with
(d^+(v)\geq 8) for every (v).  Let (q) be the number of unordered
nonadjacent vertex pairs.  For each vertex put

\[
 d^+(v)=8+e_v,\qquad \mu_v=|M(v)|,\qquad t_v=e_v+\mu_v,
\]

where (M(v)) is the set of vertices nonadjacent to (v).  Since every
unordered pair supports either one arc or no arc,

\[
 |E(D)|={18\choose2}-q=153-q.
\]

Consequently

\[
 \sum_v e_v=(153-q)-18\cdot8=9-q,
 \qquad
 \sum_v\mu_v=2q,
 \qquad
 \sum_vt_v=9+q.                                      \tag{1}
\]

In particular (q\leq9).  Let

\[
 A=\{v:d^+(v)=8\},\qquad
 b=|\{v:e_v>0\}|.
\]

Here (b) counts positive **outdegree excesses**; it is not the number of
vertices with (t_v>0).  Since every positive integral (e_v) contributes
at least one to its sum,

\[
 b\leq\sum_v e_v=9-q,
 \qquad |A|=18-b\geq9+q.                              \tag{2}
\]

Assume for contradiction that every vertex violates the desired SSNC
inequality strictly.  For (v\in A), set

\[
 C_v=\{v\}\cup N^+(v).
\]

Then (|C_v|=9), while the strict failure gives
(|N^{++}(v)|\leq7).  The sets (C_v) and (N^{++}(v)) are disjoint, so
at least two vertices lie outside their union.  Define the ordered
source-target incidence set

\[
 R=\{(v,u):v\in A,\ u\notin C_v\cup N^{++}(v)\}.
\]

Thus

\[
 |R|\geq2|A|\geq18+2q.                               \tag{3}
\]

The orientation of this incidence is important: (v) is the degree-8
**source**, and (u) is a target unreachable from (v) in zero, one, or two
steps.

## Target-side capacity audit

Fix a target (u), and write

\[
 R_u=\{v\in A:(v,u)\in R\},\qquad r_u=|R_u|.
\]

To avoid confusing this target-side set with the unreachable set of a
source, denote

\[
 T_u=V(D)\setminus(\{u\}\cup N^-(u)).
\]

Because an oriented graph partitions the other vertices into in-neighbours,
out-neighbours, and nonneighbours,

\[
 T_u=N^+(u)\cup M(u),\qquad |T_u|=d^+(u)+\mu_u=8+t_u. \tag{4}
\]

If (v\in R_u), then (u\notin C_v).  Moreover no (x\in C_v) points to
(u): for (x=v) this would put (u) in (N^+(v)), and for
(x\in N^+(v)) it would put (u) in (N^{++}(v)).  Therefore

\[
 C_v\subseteq T_u.                                    \tag{5}
\]

This checks the potentially error-prone reversal of source and target:
(N^-(u)) consists precisely of vertices pointing **into the target** (u).
In fact (5) is an equivalence with ((v,u)\in R), although only the displayed
forward implication is used.

If (t_u=0), (4)--(5) would place the 9-element set (C_v) inside an
8-element set.  Hence

\[
 t_u=0\quad\Longrightarrow\quad r_u=0.                \tag{6}
\]

Suppose now that (t_u\geq1).  For every (v\in R_u), define

\[
 B_v=T_u\setminus C_v,
 \qquad |B_v|=(8+t_u)-9=t_u-1.                         \tag{7}
\]

For two distinct roots (v,w\in R_u), both vertices lie in (T_u), since
(v\in C_v\subseteq T_u) and (w\in C_w\subseteq T_u).  If neither
(w\in B_v) nor (v\in B_w) held, then (w\in C_v) and (v\in C_w).
As the roots are distinct, these inclusions say respectively (v\to w) and
(w\to v), a forbidden digon.  Therefore every unordered pair
({v,w}\subseteq R_u) contributes at least one ordered exclusion
(w\in B_v) or (v\in B_w).  It follows that

\[
 {r_u\choose2}
 \leq \sum_{v\in R_u}|B_v\cap R_u|
 \leq r_u(t_u-1).                                     \tag{8}
\]

There is no injectivity assumption hidden in (8): an unordered pair may be
excluded in both directions, which only increases the middle count.  If
(r_u>0), division by (r_u) gives

\[
 r_u\leq2t_u-1.                                       \tag{9}
\]

For (r_u=0), (9) is also true whenever (t_u\geq1).  Thus (6) and (9)
cover every target, including the edge cases (t_u=0), (t_u=1), and
(r_u\in\{0,1\}).

## Global summation and strictness

Let (S=\{u:t_u>0\}) and (s=|S|).  Equation (1) gives
(s\geq1).  Double-counting the ordered incidences and applying (6), (9),
and (1) yields

\[
 |R|=\sum_u r_u
     =\sum_{u\in S}r_u
 \leq\sum_{u\in S}(2t_u-1)
     =2(9+q)-s
 \leq17+2q
 <18+2q.                                               \tag{10}
\]

This contradicts (3).  The strict global gap comes solely from
(s\geq1); no unspoken claim that every positive-(t) target is used is
needed.

## Quantifier and hypothesis audit

- The assumed strict SSNC failure is universal over all vertices, but the
  lower bound uses it only for the degree-8 source set (A).
- The target-capacity lemma is proved separately for every target (u).
  Targets with (t_u=0) are not passed through the formula with a negative
  right-hand side; they are handled by (6).
- Minimum outdegree 8 is used to make every (e_v) a nonnegative integer.
- The absence of digons is used exactly once, in the pair-cover step (8).
- Simplicity and orientation are used in the arc count and in the partition
  behind (4).
- No regularity, strong connectivity, tournament assumption, or solver
  output is used.
- The constants 18 and 8 are load-bearing.  The report makes no asymptotic or
  all-orders extrapolation.

## Countermodel attempts

An abstract incidence countermodel would have to satisfy simultaneously:

1. at least (9+q) roots;
2. at least two incidences from each root;
3. nonnegative target budgets (t_u) summing to (9+q);
4. (r_u=0) for zero-budget targets; and
5. for every positive-budget target, 9-subsets (C_v\subseteq T_u) obeying
   the no-mutual-containment condition forced by the absence of digons.

Condition 5 is exactly the pair-cover lemma (8), so it forces
(r_u\leq2t_u-1).  Summing then gives (10), whereas conditions 1--2 give
(3).  Hence no abstract countermodel respecting all graph-derived axioms
exists; a purported one must violate at least one of the five listed
conditions.  The most tempting invalid countermodels reverse the incidence
orientation or allow both (v\to w) and (w\to v).

As a separate implementation/edge-case check, a fixed-seed Python random-walk
auditor was run as `python -` with parameters
`n=18`, `seed=0xC011A17` (decimal `201398807`), 25,000 audited states, and
seven minimum-outdegree-preserving mutation steps per state (175,000 mutation
steps).  For every state it independently recomputed all degree, missing-pair,
source-deficit, target-inclusion, pair-cover, and global-sum identities.  The
observed (q)-histogram was

```
q=0: 0, q=1: 0, q=2: 9, q=3: 61, q=4: 412,
q=5: 1541, q=6: 3993, q=7: 7406, q=8: 7747, q=9: 3831.
```

The run returned `AUDIT_PASS`; the maximum observed (r_u) was 2 and the
maximum observed value of (r_u-(2t_u-1)) was 0.  This finite randomized
check is corroboration only; the proof above is the certificate.

## Editorial note

The mathematics in `CONSTRUCTION_N18.md` survives the adversarial audit.
For publication, renaming its target-side set (U_u) to (T_u) would avoid
collision with common notation for a source's unreachable set, but this is
expositional and does not affect the proof.
