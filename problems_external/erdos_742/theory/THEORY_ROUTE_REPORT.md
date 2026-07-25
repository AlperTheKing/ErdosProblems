# Erdős 742: theorem-route audit

Date: 2026-07-23

## Scope

This report concerns the non-bipartite diameter-2-edge-critical (D2C)
case and its complement formulation.  It does not prove the Murty--Simon
conjecture, does not close order 25, and contains no computational
counterexample to the conjecture.

For a non-bipartite D2C graph \(G\), let \(H=\overline G\).  The standard
complement formulation makes \(H\) a 3-total-domination-edge-critical
graph: \(\gamma_t(H)=3\), and adding any missing edge lowers
\(\gamma_t\) to 2.  At order 25,

\[
 |E(G)|\ge157\quad\Longleftrightarrow\quad |E(H)|\le143,
\]

while a non-bipartite equality graph with \(|E(G)|=156\) would have
\(|E(H)|=144\).

The already settled order 26 gives the following usable strict statement:
the complement of a non-bipartite D2C graph of order 26 has more than
\(26(26-2)/4=156\) edges.

## Literature constraints used

- Fan's minimum-degree argument proves the required complement edge bound
  when \(\delta(H)\le 0.3n\).  Hence an order-25 obstruction must have
  \(\delta(H)\ge8\).
- The maximum-degree theorem for 3-total-domination-edge-critical graphs
  gives \(\Delta(H)\ge\lceil n/2\rceil\), hence \(\Delta(H)\ge13\) at
  order 25.
- The diameter-three/dominating-edge case is already settled, so the
  surviving complement case may be restricted to diameter two.
- Published special-case results also remove complement connectivity at
  most three, the claw-free and bull-free classes, and several
  dominating-pair classes.
- The 2025 characterization of dense \(C_5\)-free D2C graphs is stated for
  sufficiently large order and does not close order 25.

Sources:

- W. Goddard et al., maximum degree in total-domination-edge-critical
  graphs:
  <https://d-nb.info/1372516379/34>
- A. Dailly, F. Foucaud, A. Hansberg, the dominating-edge case:
  <https://perso.limos.fr/ffoucaud/Publications/Papers/J31_Murty-Simon_DM_2019.pdf>
- Q. Lin and X. Wang, dense \(C_5\)-free D2C graphs (2025):
  <https://www.sciencedirect.com/science/article/pii/S0166218X25003439>
- Total-domination-edge-critical graphs with many dominating pairs:
  <https://pure.uj.ac.za/en/publications/total-domination-edge-critical-graphs-with-total-domination-numbe/>

## Proved conditional bridge: true-twin transfer

Call a vertex \(v\) of a 3-total-domination-edge-critical graph \(H\)
**handler-cloneable** when, for every nonneighbor \(u\) of \(v\), the graph
\(H+uv\) has a total-dominating pair containing \(v\).

Let \(H^v\) be obtained by adjoining a true twin \(v'\) of \(v\), so
\(N_{H^v}[v']=N_{H^v}[v]\).

**Lemma (true-twin transfer).**  If \(H\) is
3-total-domination-edge-critical and \(v\) is handler-cloneable, then
\(H^v\) is 3-total-domination-edge-critical.

**Proof.**

1. A total-dominating triple of \(H\) also dominates \(v'\): because it
   dominates \(v\), one of its vertices lies in \(N_H(v)\), and that
   vertex is adjacent to \(v'\).  Thus \(\gamma_t(H^v)\le3\).
2. A total-dominating pair entirely in \(H\) would also total-dominate
   \(H\), which is impossible.  If a pair is \(\{v',x\}\) with
   \(x\ne v\), replacing \(v'\) by \(v\) gives a total-dominating pair of
   \(H\).  The remaining pair \(\{v,v'\}\) could dominate only if \(v\)
   were universal, which would itself force \(\gamma_t(H)=2\).  Hence
   \(\gamma_t(H^v)=3\).
3. An old missing edge not incident with \(v\) keeps its old
   total-dominating pair; that pair dominates \(v'\) because it already
   dominates \(v\) through a neighbor of \(v\).
4. For a missing edge \(vu\), choose by hypothesis a total-dominating
   pair of \(H+vu\) containing \(v\).  It remains a witness after adding
   \(vu\) in \(H^v\), and replacing \(v\) by \(v'\) gives the
   corresponding witness after adding the new missing edge \(v'u\).
   These are all missing edges of \(H^v\).

Therefore every missing-edge addition lowers the total domination number
of \(H^v\) to 2.  \(\square\)

**Exact order-25 consequence.**  If an order-25 obstruction \(H\) with
\(|E(H)|\le143\) had a handler-cloneable vertex of degree at most 12,
then

\[
 |E(H^v)|=|E(H)|+d_H(v)+1\le156,
\]

contradicting the settled strict non-bipartite order-26 result.  Thus the
following finite lemma would close the strict order-25 bound:

> Every diameter-two, 3-total-domination-edge-critical graph \(H\) of
> order 25 with \(|E(H)|\le143\) and \(\delta(H)\ge8\) has a
> handler-cloneable vertex of degree at most 12.

This lemma is not proved here.  It also does not settle equality
uniqueness: for \(|E(H)|=144\), the same transfer needs degree at most 11,
or an additional rigidity argument for the degree-12 case.

## Falsified charging rule

The natural maximum-cut rule

> every internal edge of a maximum cut has a cross nonedge for which
> that internal edge is critical

is false.  The independently replayed graph below is D2C:

```text
0:[4,7]
1:[2,4]
2:[1,4,5,7]
3:[4,6,7]
4:[0,1,2,3,5,6]
5:[2,4]
6:[3,4]
7:[0,2,3]
```

For the maximum cut \(X=\{2,3,4\}\),
\(Y=\{0,1,5,6,7\}\), the internal edge \(0-7\) is critical only for its
own pair \(0-7\), which is not a cross nonedge.  The verifier reports:

```text
VERIFIED D2C n=8 m=12 max_cut=9 max_cut_count_up_to_complement=12
partition X={2,3,4} Y={0,1,5,6,7}
internal_edge=0-7 critical_pairs=0-7 cross_missing_critical=0
internal_edge=2-4 critical_pairs=2-6 cross_missing_critical=1
internal_edge=3-4 critical_pairs=1-3,3-5 cross_missing_critical=1
CHARGING_LEMMA_FALSE
```

Artifact:
`verify_charging_counterexample.cpp`.

This kills the rule for an arbitrary maximum-cut certificate.  It does
not logically exclude a different, graph-dependent partition or a
nonlocal charging invariant.  No such replacement with a theorem-closing
bridge was obtained.

## Falsified low-degree cloneability rules

Exhaustive enumeration through order seven suggested cloneability but did
not support its low-degree forms:

```text
n=5 labeled_3t_critical=12
n=6 labeled_3t_critical=540
n=7 labeled_3t_critical=8820
SUMMARY total_3t=9372 no_cloneable=0
        no_cloneable_min_degree=6660
        no_cloneable_at_most_average=4140
```

A definition-level verifier then checked the following stronger
counterexample in the Fan-hard minimum-degree range.  It is a
diameter-two 3-total-domination-edge-critical graph with \(n=12\),
\(m=41\), \(\delta=4\), and average degree \(82/12\).  Its only cloneable
vertices have degree 8:

```text
0:[2,3,4,6,9,11]
1:[4,5,7,10]
2:[0,6,7,10,11]
3:[0,5,6,7,8,9,10,11]
4:[0,1,5,6,8,11]
5:[1,3,4,7,8,9,10,11]
6:[0,2,3,4,8,9,10]
7:[1,2,3,5,8,9]
8:[3,4,5,6,7,9,10,11]
9:[0,3,5,6,7,8,10,11]
10:[1,2,3,5,6,8,9,11]
11:[0,2,3,4,5,8,9,10]
```

Verifier output:

```text
VERIFIED n=12 m=41 diameter=2 gamma_t_edge_critical=3
         min_degree=4 average_degree=82/12
cloneable_vertices=3(d=8),5(d=8),8(d=8),9(d=8),10(d=8),11(d=8)
AVERAGE_PLUS_ONE_CLONEABILITY_FALSE
```

Thus the statements “a minimum-degree vertex is cloneable”, “a
cloneable vertex has degree at most the average”, and even “at most the
average plus one” are false in general.  Artifact:
`verify_average_plus_one_counterexample.cpp`.

A separate deterministic random audit of 53,809 hard-range generated
instances found no 3-total-domination-edge-critical graph without any
cloneable vertex, but found 469 instances without a cloneable vertex of
degree at most average plus one.  This is bounded evidence only.

## Route status

- The simple maximum-cut local charging rule is **DEAD** by the verified
  order-eight counterexample.
- The unrestricted low-degree true-twin induction rule is **DEAD** by the
  verified order-twelve counterexample.
- The true-twin transfer lemma itself is valid and gives an exact bridge,
  but its density-sensitive order-25 frontier lemma remains unproved.
- Neither order 25 nor the full Murty--Simon conjecture is resolved by
  this route.

