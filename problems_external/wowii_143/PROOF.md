# A proof of WOWII / Graffiti.pc Conjecture 143

**Date:** 2026-07-17  
**Status:** complete mathematical proof; independent computation and referee review completed; Lean verification in progress.

## Statement

Let $G$ be a finite simple connected graph that is not a tree. Write

- $t(G)$ for the largest order of an induced subgraph of $G$ that is a tree;
- $g(G)$ for the girth of $G$; and
- $δ′(G)$ for the second entry, with multiplicity, in the nondecreasing degree sequence of $G$.

Then

$$
t(G) δ′(G) ≥ g(G)+1.
$$

Equivalently,

$$
t(G) ≥ (g(G)+1)/δ′(G).
$$

## Lemma (two leaves)

Let $G$ be a finite simple connected graph that contains a cycle and has two distinct leaves. Then

$$
t(G) ≥ g(G)+1.
$$

### Proof

Let $x$ and $y$ be distinct leaves. A shortest $x$–$y$ path is induced, so at least one induced tree of $G$ contains both $x$ and $y$. Since $G$ is finite, among all such induced trees choose one, say $T=G[S]$, for which $|S|$ is maximum.

The set $S$ is a proper subset of $V(G)$. Indeed, if $S=V(G)$, then $G=G[S]=T$ would be a tree, contrary to the assumption that $G$ contains a cycle. Because $G$ is connected, there is a vertex $z∉S$ having a neighbor in $S$.

The vertex $z$ has at least two neighbors in $S$. Otherwise it has exactly one such neighbor, and the induced graph $G[S∪{z}]$ is obtained from the tree $T$ by attaching one new leaf. It is therefore a larger induced tree containing $x$ and $y$, contradicting the choice of $T$.

Choose distinct neighbors $a,b∈S$ of $z$, and let $P$ be the unique $a$–$b$ path in the tree $T$. The edges of $P$, together with $za$ and $zb$, form a simple cycle of length $|V(P)|+1$. Possible additional edges from $z$ to vertices of $P$ do not affect the existence of this cycle (and can only provide shorter cycles). Hence

$$
g(G) ≤ |V(P)|+1.
$$

Neither $x$ nor $y$ lies on $P$. Every internal vertex of $P$ has its two path neighbors, while each endpoint $a,b$ has a path neighbor and the additional neighbor $z$. Thus every vertex of $P$ has degree at least two in $G$, whereas $x$ and $y$ have degree one. Consequently $V(P)$, $x$, and $y$ are pairwise disjoint subsets of $S$, and

$$
t(G) ≥ |S| ≥ |V(P)|+2 ≥ g(G)+1.
$$

This proves the lemma.

## Proof of the conjecture

A connected graph that is not a tree contains a cycle, so $g(G)≥3$; every one of its vertices has positive degree.

First suppose that $δ′(G)≥2$. Let $C$ be a shortest cycle. It has no chord, since a chord would produce a shorter cycle. Deleting one vertex from $C$ therefore leaves an induced path on $g(G)-1$ vertices. Hence

$$
t(G) ≥ g(G)-1.
$$

It follows that

$$
t(G)δ′(G) ≥ 2(g(G)-1) ≥ g(G)+1,
$$

where the last inequality is equivalent to $g(G)≥3$.

Now suppose that $δ′(G)=1$. Since the degrees are positive and the second entry of the degree sequence is one, $G$ has at least two leaves. The lemma gives

$$
t(G) ≥ g(G)+1.
$$

Multiplying by $δ′(G)=1$ proves the desired inequality. The two cases exhaust all possibilities.

## Formal-statement addendum

Mathlib defines the girth of an acyclic graph to be $0$, and the current Formal Conjectures statement also permits connected trees on a nontrivial vertex type. Under that convention the extension is immediate: the whole tree is an induced tree, so $t(G)=|V(G)|≥2$, while $δ′(G)≥1$. Therefore

$$
t(G)δ′(G) ≥ 2 ≥ 0+1.
$$

Thus the proof also covers that harmless extension of the original conjecture.

## Sharpness

For every $g≥3$, take a cycle $C_g$ and attach two pendant vertices to arbitrary cycle vertices. The resulting graph has $δ′=1$. At most two cycle vertices support the leaves, so choose a cycle vertex supporting neither leaf and delete it. The remaining induced graph is a tree on $g+1$ vertices. No induced tree can contain all $g+2$ vertices, because the full induced graph contains the cycle. Hence $t=g+1$, and equality holds.

