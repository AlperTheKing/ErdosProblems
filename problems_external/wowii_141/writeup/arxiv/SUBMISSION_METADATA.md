# arXiv submission metadata — Conjecture 141

- **Title:** Largest induced trees in graphs of given girth and maximum degree, with a proof of Graffiti.pc's Conjecture 141
- **Authors:** Alper Ferudun
- **Primary category:** math.CO
- **MSC 2020:** 05C35, 05C05
- **Comments:** 5 pages. The main theorem and Conjecture 141 have been formalized and machine-checked in Lean 4; formalization submitted in Google DeepMind Formal Conjectures PR #4454.
- **License:** select in the arXiv UI after author review.

## Abstract

For a finite simple graph G, let t(G) denote the largest number of vertices inducing a tree, g(G) the girth, Delta(G) the maximum degree, and for a vertex v let ell(v) denote the independence number of the subgraph induced by the neighbourhood of v. We prove that every finite connected triangle-free graph containing a cycle satisfies t(G) >= Delta(G)+g(G)-3, with equality for all cycles C_g with g >= 4 and all complete bipartite graphs K_{a,b} with a,b >= 2. As a corollary we prove Conjecture 141 of the conjecture-making program Graffiti.pc (DeLaVina, Written on the Wall II, 2005): every finite connected graph satisfies t(G) >= floor(g(G)/2)-1+max_v ell(v). The proofs are elementary maximality arguments. Both results have been formalized and machine-checked in Lean 4 against the statement of the conjecture in the Google DeepMind Formal Conjectures repository.
