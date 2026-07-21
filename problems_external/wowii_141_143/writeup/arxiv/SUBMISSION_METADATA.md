# arXiv submission metadata - Graffiti.pc Conjectures 141-143

- **Title:** Three Graffiti.pc Conjectures on Largest Induced Trees: Proofs of Conjectures 141, 142, and 143
- **Authors:** Alper Ferudun
- **Primary category:** math.CO
- **MSC 2020:** 05C05, 05C07, 05C12, 05C35
- **Comments:** 16 pages. Complete Lean 4 proofs of all three formal statements are included as ancillary files; see Google DeepMind Formal Conjectures pull requests #4454 and #4457.
- **License:** select in the arXiv UI after author review.

## Abstract

For a finite simple graph $G$, let $t(G)$ be the largest order of an induced tree and let $g(G)$ be the girth. We prove three consecutive conjectures of DeLaVi\~na's Graffiti.pc program. First, writing $\ell(v)$ for the independence number of the subgraph induced by the neighbourhood of $v$, we prove $t(G)\ge \lfloor g(G)/2\rfloor-1+\max_{v\in V(G)}\ell(v)$. Second, if $\operatorname{Per}(G)$ is the periphery and $f(G)=\max_x d(x,\operatorname{Per}(G))$, we prove $t(G)\ge \frac{2}{3}g(G)+f(G)$, and establish the stronger integral bound $t(G)\ge f(G)+\lceil 2g(G)/3\rceil$ when $G$ contains a cycle. Third, if $\delta'(G)$ is the second-smallest degree, counted with multiplicity, then every connected non-tree graph satisfies $t(G)\delta'(G)\ge g(G)+1$. These are Conjectures 141, 142, and 143 of Written on the Wall II. Complete, machine-checked Lean 4 proofs of all three formal statements accompany the manuscript.

## Upload contents

Upload `graffiti_141_143_arxiv_source.zip`. Its root contains the single manuscript source `graffiti_141_143.tex` and the `anc/` directory with eight Lean files, an ancillary README, and the Apache-2.0 license for the Lean sources. The reviewed PDF is `graffiti_141_143.pdf`.