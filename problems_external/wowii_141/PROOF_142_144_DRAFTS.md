# DRAFT proof material — WOWII Conjectures 142 and 144

**Status: UNREFEREED WORKING DRAFTS (2026-07-18). Known gaps marked ⛳.**

Notation: $t$ = `largestInducedTreeSize`, $g$ = Mathlib girth (0 if acyclic),
$d(v,S)$ = `distToSet` (min distance), $C$ = center (min-eccentricity set),
$B$ = periphery `maxEccentricityVertices` (max-eccentricity set),
$e := \mathrm{ecc}\,G\,C = \max_{v\notin C} d(v,C)$ (0 if $C$=univ),
$f := \mathrm{eccSet}\,G\,B = \max_{v} d(v,B)$, $r$ = radius, $D$ = diameter.

**FC statements.**
- **144**: connected $G$: $(g : ℝ) - 1 + e \le t$.
- **142**: connected $G$: $(2/3)\,g + f \le t$.

## Common tools (T1–T4)

**T1 (geodesic).** Any geodesic induces a tree, so $t \ge D + 1$, and
$t \ge \mathrm{eccent}(v) + 1$ for every $v$. *(Lean: already have
`Walk.induce_support_isTree_of_length_eq_dist`.)*

**T2 (cycle).** Cyclic $G$: $t \ge g - 1$. *(Lean: done,
`girth_sub_one_le_largestInducedTreeSize`.)*

**T3 (isometry).** A shortest cycle $K$ is isometric; in particular every arc
of $K$ of length $\le \lfloor g/2\rfloor$ is a geodesic, and $K$ is chordless.

**T4 (cycle-with-tail, CT).** Let $G$ be cyclic with $g \ge 5$, $K$ a shortest
cycle, $x$ any vertex, $m := d(x, K)$. Then
$$t \;\ge\; (g - 1) + m.$$
*Proof sketch.* Let $Q = x q_1 \cdots q_{m-1} u$ be a geodesic from $x$ to the
set $V(K)$ ($u \in K$). Then $d(q_i, K) = m - i$ (prefix optimality), so $Q$ is
an induced path and no $q_i$ with $i \le m-2$ has a neighbour on $K$. Let $w$
be a $K$-antipode of $u$ and $P := K - w$ (an induced path on $g-1$ vertices,
by T3). Chords from $q_{m-1}$ to $P - u$: an edge $q_{m-1} p_j$ ($p_j \ne u$)
closes the cycle $q_{m-1}\,u \cdots p_j\,q_{m-1}$ through the shorter $K$-arc,
of length $d_K(u, p_j) + 2 \le \lfloor g/2 \rfloor + 2 < g$ for $g \ge 5$ —
impossible. Also $x \ldots q_{m-1} \notin K$ (positive distance). Hence
$V(P) \cup V(Q)$ induces a tree (path $P$ + tail $Q$ attached only at $u$) with
$(g-1) + m$ vertices. ∎ *(⛳ referee: the "antipode deletion leaves an induced
path" and the arc-length bound $d_K(u,p_j) \le \lfloor g/2\rfloor$ when $w$ is
deleted — check indices; also the disjointness $V(Q)\cap V(K) = \{u\}$.)*

**T4 is FALSE for $g = 3$** (do not "fix" it silently). Counterexample family:
path $x q_1 \cdots q_{m-1}$ attached to a triangle $u a b$ with $q_{m-1}$
adjacent to **all three** of $u, a, b$. Then $g = 3$, $d(x, \{u,a,b\}) = m$,
but $t = m + 1 < (g-1) + m$: any induced tree contains at most one vertex of
$\{u, a, b\}$ (two of them + $q_{m-1}$ or the third close a triangle/cycle),
and adding one to the $Q$-path gives exactly $m+1$… *(⛳ verify this $t$ value
computationally; if correct, any use of CT must assume $g \ge 5$, or $g \ge 4$
with a repaired constant — test $g=4$ analogue too: $q_{m-1}$ adjacent to all
of a $C_4$ forces a $C_3$? $q$ adjacent to two adjacent $C_4$-vertices makes a
triangle, contradicting $g=4$; so for $g = 4$, $q_{m-1}$ attaches to at most
two OPPOSITE $C_4$ vertices — cycle $q,u,p,\!q$ length 4 allowed! So CT can
fail at $g=4$ too via double attachment to an antipodal pair; check.)*

---

## Conjecture 144: $t \ge g - 1 + e$

**Case A: acyclic.** $g = 0$; $t = n$ (spanning tree is induced ⟺ $G$ tree —
here $G$ IS a tree, $t = n$); $e \le r \le n - 1$, so $-1 + e \le n$. ✓ (large
slack; Lean: $e \le$ … any crude bound works, e.g. $e \le n$ and $t = n$
— needs `largestInducedTreeSize = card` for trees: small new lemma.)

**Case B: cyclic, $e = 0$.** Exactly T2: $t \ge g - 1$. ✓ **Closed.**

**Case C: cyclic, $e \ge 1$.** ⛳ **Open bridge.** Have (for $g \ge 5$) CT:
$t \ge g - 1 + \max_x d(x, K)$. It would suffice to prove:

> **Bridge 144-Q1.** For every connected cyclic $G$ there is a shortest cycle
> $K$ and a vertex $x$ with $d(x, K) \ge e = \mathrm{ecc}(G, C)$.

Intuition: the center cannot be much "deeper" than a girth cycle; the vertex
realizing $e$ is at the end of a long branch, and long branches are far from
every cycle… **This is not proved and might be false** — the oracle must test
Q1 directly (all graphs $n \le 7$ + structured families, incl. graphs whose
center sits inside a dense cluster while a *different* far cluster contains
all shortest cycles).

Auxiliary candidate (would give a different route via T1):

> **Bridge 144-Q2.** $\mathrm{eccent}(v) \ge r + d(v, C)$ for every $v$?

(True in trees. If true in general: $t \ge \mathrm{eccent}(x^*) + 1 \ge r + e
+ 1$, which combined with T2/CT covers 144 whenever $r \ge g - 2$ or the CT
side covers the rest — partial, but worth the test.) Known folklore warns the
center of a general graph is badly behaved (Buckley: every graph is the center
of some graph), so Q2 is *suspect* — test it.

**Tightness (for whichever proof lands):** $C_g$ ($e=0$, T2 tight);
$C_6$+pendant: $e = 1$, $t = 6 = g - 1 + e$; the path-to-cycle family
$C_g + P_L$ ($L \le \lfloor g/2 \rfloor$): $e = L$, $t = g + L - 1$ — tight.
The bound is tight for **every** $g$ and every $0 \le e \le \lfloor g/2
\rfloor$ (conjecturally; oracle: harvest equality cases).

## Conjecture 142: $t \ge \tfrac23 g + f$

**Case A: acyclic.** $g = 0$: need $f \le t = n$: trivial ($f \le D \le n-1$). ✓

**Case B: cyclic, $f = 0$.** T2: $t \ge g - 1 \ge \tfrac23 g \iff g \ge 3$. ✓
**Closed.** (Equality chain forces $g = 3$: check $C_3$: $t = 2 = \tfrac23
\cdot 3$ ✓ tight.)

**Case C: cyclic, $f \ge 1$.** ⛳ **Open bridge.** CT-route needs:

> **Bridge 142-Q3.** Some shortest cycle $K$ and vertex $x$ with
> $d(x, K) \ge f - \tfrac13 g + 1$.

The $\tfrac23$ coefficient smells like a tradeoff: if a peripheral pair is
$D$ apart, T1 gives $t \ge D + 1$; and $D \ge$ (distance between far $B$-parts)
relates to $f$… Facts to exploit: the far partner of a peripheral vertex is
peripheral ($d(b, w) = D = \mathrm{eccent}(w) \Rightarrow w \in B$); hence $B$
contains a diametral pair, and the $f$-realizing vertex $x^*$ has
$d(x^*, b) \ge f$ for ALL $b \in B$, in particular to both ends of a diametral
geodesic: so $D \le d(b, x^*) + d(x^*, w)$… (upper-bounding $D$ is the wrong
direction; instead: the diametral geodesic $P_{bw}$ passes within…?)
Candidate: $t \ge D + 1 + (\text{tail toward } x^*)$: a geodesic tree $P_{bw}
\cup$ (geodesic from $x^*$ to $P_{bw}$) — two geodesics: their union is
generally NOT induced, but a maximality argument à la 143 might rescue a
$D + 1 + d(x^*, P_{bw})$-vertex induced tree:

> **Bridge 142-Q4 (double-tail).** For a diametral geodesic $P$ and any $x$:
> $t \ge |P| + d(x, V(P)) = D + 1 + d(x, V(P))$?

*(⛳ suspect — same chord dangers as CT at small girth; but for a GEODESIC
base instead of a cycle base, the tail-attachment analysis may go through at
ALL girths: the geodesic prefix-optimality kills chords except at the last
tail vertex, and a last-vertex double attachment to $P$ at distance-$\ge 2$
positions would shortcut $P$'s geodesy — i.e. attachment points on $P$ are
within distance… CHECK: last tail vertex $q$ adjacent to $p_i, p_j$, $i<j$:
then $j - i \le 2$ (else $P$ not geodesic). Both $j-i \in \{1,2\}$ possible
without violating anything ($j-i=1$ makes a triangle, needs $g=3$; $j-i=2$
makes a $C_4$, needs $g \le 4$). For $g \ge 5$: unique attachment ⟹ Q4 holds
with the same CT-style proof. For $g \le 4$: drop the offending $p$-vertices
or reroute — possibly lose 1 vertex; but for $g \le 4$ the constant
$\tfrac23 g \le \tfrac83 < 3 \le g - 1 + \ldots$ — small-girth cases may close
by T1/T2 + slack: check whether $\tfrac23 g + f \le \max(g-1, D+1, \ell+1
\ldots)$ suffices when $g \in \{3,4\}$.)*

Then 142 would need: $\tfrac23 g + f \le D + 1 + d(x^*, P_{bw})$, i.e.

> **Bridge 142-Q5.** $d(x^*, P_{bw}) \ge \tfrac23 g + f - D - 1$ for a
> diametral geodesic $P_{bw}$?

With $D \ge \lfloor g/2 \rfloor$ (isometric girth cycle): $\tfrac23 g - D - 1
\le \tfrac23 g - \tfrac{g}{2} - 1 = \tfrac{g}{6} - 1$… so Q5 needs
$d(x^*, P_{bw}) \ge f + g/6 - 1$-ish — plausible when the periphery is spread
(the $P_{bw}$ endpoints are in $B$, $x^*$ is $f$-far from $B$… but $x^*$ can be
CLOSE to $P$'s middle!). ⛳ Honest status: no complete route; oracle must test
Q3, Q4, Q5 and hunt 142 counterexamples hard (the $\tfrac23$ constant may
encode a genuinely different extremal structure — find all equality cases in
the atlas and reverse-engineer).

## Priority of effort (given gate outcomes)

1. If the oracle falsifies 142 or 144 outright → instant-disproof pivot.
2. Else: 141 first (proof nearly closed). 144 second (single clean bridge
   Q1; CT already half-Lean-ready: T1/T2 done, T4 needs the g≥5 chord
   analysis = same machinery as 143's cycle certificate). 142 third (worst
   understood; the $\tfrac23$ constant needs the equality-case data).
