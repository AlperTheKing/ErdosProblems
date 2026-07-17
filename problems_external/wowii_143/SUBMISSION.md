# Human review notes for WOWII / Graffiti.pc Conjecture 143

> **Policy note.** This is an AI-generated research packet, not text to paste into GitHub. Formal Conjectures adopts Mathlib's AI rules, which require GitHub and Zulip messages to be written in the human contributor's own words. The contributor must understand the proof and independently write any issue or pull-request text.

The current Formal Conjectures file [GraphConjecture143.lean](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/WrittenOnTheWallII/GraphConjecture143.lean) marks this statement as `research open`. I believe the conjecture has the following short proof. I am opening this issue first, in accordance with the contribution guide, so that the mathematical validity and priority can be checked before any status-changing pull request.

## Statement

For a finite simple connected non-tree graph $G$, let:

- $t(G)$ be the largest number of vertices inducing a tree;
- $g(G)$ be the girth; and
- $δ′(G)$ be the second-smallest degree, counted with multiplicity.

Then

$$
t(G)δ′(G) ≥ g(G)+1.
$$

This is equivalent to the fraction form in the original register.

## Two-leaf lemma

**Lemma.** If a finite simple connected cyclic graph $G$ has two distinct leaves, then $t(G) ≥ g(G)+1$.

**Proof.** Let $x,y$ be distinct leaves. A shortest $x$–$y$ path is induced, so there is an induced tree containing both. Choose a maximum-order such induced tree $T=G[S]$.

The set $S$ is proper, because otherwise the cyclic graph $G$ itself would be a tree. Connectivity gives a vertex $z∉S$ adjacent to $S$. The vertex $z$ has at least two neighbors in $S$: if it had exactly one, then $G[S∪{z}]$ would be a larger induced tree still containing $x,y$.

Choose distinct neighbors $a,b∈S$ of $z$, and let $P$ be the unique $a$–$b$ path in $T$. The path $P$, together with $za$ and $zb$, is a cycle of length $|V(P)|+1$. Extra edges from $z$ to $P$ do not destroy that cycle. Hence

$$
g(G) ≤ |V(P)|+1.
$$

Every vertex of $P$ has degree at least two in $G$: internal vertices have two path neighbors, and each endpoint has a path neighbor plus $z$. Thus neither leaf $x$ nor $y$ lies on $P$. Therefore

$$
t(G) ≥ |S| ≥ |V(P)|+2 ≥ g(G)+1.
$$

This proves the lemma.

## Proof of Conjecture 143

Because $G$ is connected and not a tree, it contains a cycle and $g(G)≥3$.

If $δ′(G)≥2$, a shortest cycle is chordless. Removing one cycle vertex leaves an induced path on $g(G)-1$ vertices, so

$$
t(G)δ′(G) ≥ 2(g(G)-1) ≥ g(G)+1.
$$

If $δ′(G)=1$, positivity of all degrees and the definition of the second entry imply that $G$ has at least two leaves. The lemma gives

$$
t(G)δ′(G)=t(G)≥g(G)+1.
$$

The two cases are exhaustive.

## Formal-statement tree case

The current Lean statement also permits connected trees, using Mathlib's convention `girth = 0` for acyclic graphs. This extension is immediate: the whole graph is an induced tree, so $t(G)=|V(G)|≥2$, while $δ′(G)≥1$. Hence $t(G)δ′(G)≥2≥1=g(G)+1$.

## Checks completed

- Three independent line-by-line reviews found no mathematical gap.
- Two independent exact implementations checked all 1,253 unlabeled graph-atlas graphs on at most seven vertices. Among the 971 connected cyclic graphs there were no violations of the theorem or the two-leaf lemma.
- A stronger constrained check covered all 199 unordered leaf pairs across the 129 connected cyclic atlas graphs having at least two leaves and found no violation.
- Two no-`sorry`, no-`native_decide` Lean components compile without warnings:
  - the arithmetic assembly of the two cases;
  - `SimpleGraph.IsTree.induce_insert_of_unique_adj`, formalizing the maximal-tree extension step.
- A full Lean proof of the theorem is not yet claimed. These Lean checks are local-only until their source is placed at a public commit URL.

The computation is only a falsification check and is not used in the proof.

## Priority audit and related work

- [Douglas West's current Graffiti.pc register](https://dwest.web.illinois.edu/regs/graffiti.html) still lists the exact statement as Conjecture 143 (2005).
- DeLaViña's resolved list does not list 143 in the available indexed snapshot; its live server was unavailable during this audit.
- The current Formal Conjectures source still marks the theorem open.
- Erdős, Saks, and Sós, [Maximum Induced Trees in Graphs](https://doi.org/10.1016/0095-8956(86)90028-6) (1986), introduces and studies the invariant but I found no girth/second-smallest-degree result there.
- A close antecedent is DeLaViña–Waller's 2004 induced-forest inequality $f(G)≥g(G)+f_1(G)-1$, documented in Hertz–Marcotte–Schindl, [On the maximum orders of an induced forest, an induced tree, and a stable set](https://doi.org/10.2298/YJOR130402037H) (2014). It does not imply the needed induced-tree bound because the forest may be disconnected.

Exact-formula, synonym, and citation searches located no prior proof. This is not proof of absence. Because the argument is short and may be unpublished folklore, I am deliberately not claiming “first proof”; I would especially appreciate a priority check with the WOWII/Graffiti.pc maintainers.

## Request

Could maintainers please check:

1. whether the proof above is valid;
2. whether a prior solution is known; and
3. if both checks are favorable, whether the next step should be a pull request changing the category to `research solved`, alongside the reusable Lean API lemma and continuing full formalization?

