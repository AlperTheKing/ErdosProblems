# GPT-Pro prompt — direct bridge audit

Erdős Problem #128 asks whether every finite graph G on n vertices, for which every induced subgraph on at least floor(n/2) vertices has more than n^2/50 edges, must contain a triangle.

We are considering exactly one finite counterexample search at n=20. The proposed terminal certificate is a labelled simple graph G on 20 vertices such that:

1. G is triangle-free; and
2. every 10-vertex induced subgraph has at least 9 edges.

Since 20^2/50=8 and induced edge count is monotone under adding vertices, such a graph would directly disprove the stated problem. The intended exact search has one Boolean variable per edge, clauses forbidding all 1140 triangles, and exact pseudo-Boolean constraints requiring at least 9 of the 45 possible edges in each of the 184756 ten-sets. A second implementation would use lazy violated-ten-set separation and independently enumerate every ten-set in any candidate.

Single question: adversarially audit this direct route. Is the certificate-to-problem bridge completely correct, and is n=20 a mathematically defensible single small-order shot, or is there a rigorous elementary/known obstruction that makes the n=20 instance impossible before SAT? If another single n<=20 is strictly better for a finite counterexample search, identify it and prove why. Give a clear GO or NO-GO verdict, check all integer-rounding and quantifier details, and—if GO—state a sound exact encoding with only provably safe symmetry breaking. Do not replace the task by an asymptotic relaxation, graphon reformulation, or an unbounded search over n.
