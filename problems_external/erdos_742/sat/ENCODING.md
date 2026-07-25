# Exact SAT encoding for the order-25 D2C certificate

The generator `generate_d2c_cnf.cpp` uses one variable \(x_{uv}\) for each
unordered vertex pair.  It emits no symmetry breaking.

## Two-step reachability

For every unordered pair \(p=\{s,t\}\) and every
\(k\notin\{s,t\}\), the variable \(c_{p,k}\) is constrained by

\[
c_{p,k}\leftrightarrow (x_{sk}\wedge x_{kt}).
\]

The three emitted clauses are
\((\neg c\vee x_{sk})\), \((\neg c\vee x_{kt})\), and
\((\neg x_{sk}\vee\neg x_{kt}\vee c)\).  Thus both directions are present.
For every \(p\), the clause

\[
x_{st}\vee\bigvee_{k\ne s,t}c_{p,k}
\]

is exactly the assertion that \(s,t\) have distance at most two.  A separate
clause says that at least one \(x_{uv}\) is false, so the resulting diameter
is exactly two.

## Edge-criticality

Fix a possible deleted edge \(e=\{a,b\}\).  If deleting \(e\) destroys all
paths of length at most two between a pair \(p\), then \(p\) contains \(a\)
or \(b\).  Indeed, a length-one path affected by the deletion is \(e\)
itself, while a length-two path containing \(e\) has one endpoint in
\(\{a,b\}\).  A pair disjoint from \(\{a,b\}\) therefore retains every
length-at-most-two path it had before deletion.

Consequently the encoding needs only the \(2n-3\) pairs incident with an
endpoint of \(e\).  For each such pair \(p=\{s,t\}\), \(b_{e,p}\) is
bidirectionally reified as:

\[
x_e\ \wedge\
\neg x_p\quad\text{if }p\ne e\ \wedge\
\bigwedge_{\substack{k\ne s,t\\
\{s,k\}\ne e,\ \{k,t\}\ne e}}\neg c_{p,k}.
\]

The forward clauses make every true \(b_{e,p}\) imply every conjunct.  The
single reverse clause contains the negation of every conjunct and
\(b_{e,p}\), so all conjuncts imply \(b_{e,p}\).  The omitted direct literal
when \(p=e\), and omitted two-step variables whose path uses \(e\), are
exactly the paths removed by the deletion.  Finally,

\[
\neg x_e\vee\bigvee_{p\cap e\ne\varnothing} b_{e,p}
\]

says that every present edge has a witness pair at distance greater than two
after its deletion.

## Edge threshold

The variables \(q_{i,j}\) are fully reified by

\[
q_{i,j}\leftrightarrow
\left(q_{i-1,j}\vee(q_{i-1,j-1}\wedge x_i)\right).
\]

The four standard CNF clauses for this equivalence are emitted.  Constants
\(q_{i,0}=\top\) and \(q_{0,j}=\bot\) are represented by unit-fixed
variables.  The unit clause \(q_{m,K}\), with \(m=\binom n2\), therefore
asserts at least \(K\) edges.  Production uses \(n=25,K=157\).

## Soundness bridge

From any satisfying assignment, the first \(\binom n2\) variables define a
simple graph.  The reachability clauses give diameter exactly two; every
true edge has a reified deletion witness; and the cardinality counter gives
at least 157 edges.  Conversely, any graph with these properties extends
uniquely on the reachability and counter variables and admits at least one
true witness variable per edge, so the encoding is complete as well as
sound.

Pinned calibration instances use a separate edge-pair parser.  Verifier B
uses a strict binary adjacency-matrix parser and independently recomputes
all length-at-most-two paths after every edge deletion.
