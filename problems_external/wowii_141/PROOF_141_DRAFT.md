# DRAFT proof — WOWII / Graffiti.pc Conjecture 141

**Status: UNREFEREED DRAFT (2026-07-18). Do not treat as established.**

## Statement (FC form, GraphConjecture141.lean)

For a finite simple connected graph $G$ on a nontrivial vertex type:
$$\lfloor g(G)/2 \rfloor - 1 + \max_v \ell(v) \;\le\; t(G),$$
where $t(G)$ = largest induced tree order (`largestInducedTreeSize`), $g(G)$ =
Mathlib girth (0 if acyclic), and $\ell(v)$ = independence number of the induced
neighborhood of $v$ (`indepNeighborsCard`). The FC statement is over ℤ:
`(G.girth / 2 : ℤ) - 1 + maxL ≤ t`.

Write $L = \max_v \ell(v)$, $k = \lfloor (g-1)/2 \rfloor$ for cyclic $G$.

## Lemma S (star). For every $v$: $t(G) \ge \ell(v) + 1$.

Take an independent set $S \subseteq N(v)$ with $|S| = \ell(v)$ (independent in
the induced neighborhood, hence in $G$). Then $\{v\} \cup S$ induces a star:
edges $v$–$s$ all present; no edges inside $S$. A star is a tree. ∎

## Case 1: $G$ acyclic, or $3 \le g \le 5$.

Then $\lfloor g/2 \rfloor \le 2$, so
$\lfloor g/2\rfloor - 1 + L \le L + 1 \le t(G)$ by Lemma S. ∎
(Acyclic: $g = 0$ gives $-1 + L$ over ℤ, weaker still. Note over ℤ the bound
can be negative; Lemma S covers all of it.)

## Lemma I (isometric girth cycle). A shortest cycle $K$ of $G$ is isometric:
for $u, w \in V(K)$, $d_G(u,w) = d_K(u,w)$.

Standard: if $d_G(u,w) < d_K(u,w) \le \lfloor g/2\rfloor$ for some pair, take
the pair minimizing $d_G$; a $G$-geodesic $P$ from $u$ to $w$ meets $K$ only at
its ends (else a shorter violating pair exists), and $|P| < d_K(u,w)$; $P$
together with the longer $K$-arc... — take the SHORTER arc $A$ ($|A| = d_K(u,w)$):
$P \cup A$ is a closed walk of length $< 2 d_K(u,w) \le g$ containing a cycle
(P internally disjoint from $K \supseteq A$, and $P \ne A$ since shorter), of
length $\le |P| + |A| < g$. Contradiction. ∎ (Referee: check the "meets $K$ only
at ends" reduction carefully.)

## Case 2: $g \ge 6$.

$G$ is triangle-free ($g \ge 4$), so every $N(v)$ is independent and
$\ell(v) = \deg(v)$; hence $L = \Delta(G)$. It suffices to prove
$$t(G) \;\ge\; \Delta + k, \qquad k = \lfloor (g-1)/2 \rfloor,$$
since $k \ge \lfloor g/2 \rfloor - 1$ (equality for even $g$).

**Construction.** Let $v$ be a max-degree vertex, $K$ a shortest cycle,
$m = d(v, K)$, and $Q$ a geodesic from $v$ to a nearest cycle vertex $u_0$
($m$ edges; $m = 0$ means $v = u_0 \in K$). Continue from $u_0$ along $K$ in
one direction for $k - m$ further edges (requires $k - m \ge 0$; see Claim D).
Let $P = v, q_1, \dots, q_{m-1}, u_0, c_1, \dots, c_{k-m}$ — a path with $k$
edges, $k+1$ vertices. Let
$$ S \;=\; V(P) \,\cup\, N(v). $$
Note $|S| = (k+1) + (\Delta - 1) = \Delta + k$ provided the only overlap
between $N(v)$ and $P \setminus \{v\}$ is the first path vertex ($q_1$, or
$c_1$ when $m=0$) — Claim A.

**Claim A (no unexpected overlaps).** No vertex of $P$ at path-position
$\ge 2$ lies in $N(v)$. Such a vertex $p_j$ ($j \ge 2$) adjacent to $v$ closes
a cycle of length $j + 1 \le k + 1 < g$ — provided the closing uses the path
$v \to p_j$ (subpath of $P$, internally avoiding the edge $v p_j$), giving an
honest cycle. Contradiction with girth. (Also needs $P$ itself to be a path,
i.e. its vertices distinct: $Q$ is a geodesic; the $K$-arc is a path; a
coincidence $q_i = c_j$ would shortcut $d(v, K) = m$ or close a short cycle —
Claim B.)

**Claim B ($P$ is a path).** $Q$'s vertices are distinct (geodesic). Arc
vertices are distinct (sub-path of a cycle of length $g > k-m$). A coincidence
$q_i = c_j$ ($i < m$, $j \ge 1$) puts $q_i$ on $K$ closer to $v$ than $u_0$:
$d(v, K) \le i < m$, contradiction. ∎

**Claim C (no chords; $S$ induces a tree).** The intended tree on $S$: star
edges $v$–$w$ for $w \in N(v)$, plus the path edges of $P$. Any OTHER $G$-edge
between two vertices of $S$ closes a cycle of length at most
$(\text{tree-distance} \le k+2) + 1 \le k + 3 \le g - 1$ (for $g \ge 6$:
$g - k - 3 = \lceil (g+1)/2 \rceil - 3 \ge 0$ with equality only at $g = 5$;
for $g \ge 6$, $k+3 < g$ ⟺ true: even $g$: $k+3 = g/2+2 < g$ ⟺ $g > 4$;
odd $g$: $(g-1)/2 + 3 < g$ ⟺ $g > 5$). Enumerate chord types:
star-leaf–star-leaf (triangle, $g \ge 6$ kills), star-leaf–path-vertex,
path–path (non-consecutive). Each closes a cycle through tree edges of length
$\le k+3 - 1$... (referee: recompute the exact worst case; the tree has
diameter $\le k + 2$: leaf–$v$–along $P$ ($k$) is $k+1$; leaf–$v$–leaf is 2;
so chord cycle length $\le (k+1) + 1 = k+2 < g$ ✓ even safer). So the graph
induced on $S$ is exactly star ∪ path = a tree (connected: all reach $v$). ∎

**Claim D ($k - m \ge 0$, i.e. $d(v,K) \le k$).** Suppose $m > k$. [GAP RISK —
this is the weakest point.] Argument: take $w \in K$; $d(v, w) \ge m > k$.
Then the geodesic from $v$ to $w$ has length $\ge k+1$; take its prefix $R$ of
length exactly $k$... then use $S' = V(R) \cup N(v)$ with the same claims A–C
(no cycle needed for the path — any geodesic prefix works!). Indeed the
construction NEVER needs the path to end on or follow $K$; it only needs SOME
induced path of length $k$ starting at $v$ whose internal vertices avoid
$N(v)$-conflicts — and a geodesic from $v$ of length $k$ has all the claimed
properties (Claims A–C hold verbatim with $P$ = geodesic prefix: geodesic ⟹
no shortcuts). So split: if $\mathrm{ecc}(v) \ge k$, use a geodesic of length
$k$ from $v$; else $\mathrm{ecc}(v) < k$ and... every vertex of $K$ is within
$k - 1$ of $v$ — then $d(v,K) \le k-1 \le k$ and the mixed construction
applies. Either way a suitable $P$ exists. ∎ (Referee: verify the mixed-path
chord bounds again under $m \le k - 1$.)

**Conclusion.** $S$ induces a tree with $\Delta + k$ vertices, so
$t \ge \Delta + k \ge L + \lfloor g/2 \rfloor - 1$. ∎

## Sharpness

$C_4$: $L = 2$, $g = 4$: bound $= 3 = t(C_4)$. More equality cases to be
harvested from the atlas sweep.

## Referee focus points

1. Lemma I (isometry) — the internal-disjointness reduction.
2. Claim C chord-cycle length accounting (each chord type, exact lengths,
   including chords incident to $v$ — impossible since all $S$-neighbors of
   $v$ are tree edges... verify: a chord at $v$ would be an edge $v$–$s$ with
   $s \in S$, but every such edge IS a star/path edge — fine).
3. Claim D case split and whether Claims A–C survive for both path choices.
4. ℤ-form edge cases: acyclic ($g=0$), tiny graphs, $L = 0$ (isolated-ish
   vertex — connected nontrivial ⟹ $\deg \ge 1$ ⟹ $\ell(v) \ge 1$).
5. FC-def fidelity: `indepNeighborsCard` on `induce (neighborSet v)`;
   Mathlib `girth`; ℤ division `(G.girth / 2 : ℤ)`.
