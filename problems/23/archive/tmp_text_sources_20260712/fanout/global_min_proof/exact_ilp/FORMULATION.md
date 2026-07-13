# Exact 0-1 formulation

For bad edge i and literal row r in R_i, binary z[i,r] selects exactly one row: sum_r z[i,r]=1.
For ordered (x,y), c[x,y]=sum_{i,r:x,y in r}z[i,r], q[x,y]=[c>=1], and e[x,y]=max(c-1,0), using integral big-M M=|bads|.
For vertex v, p[v] is the OR of selected rows containing v. For blue edge a={u,v}, s[a] is the OR of selected rows using a, and h[a]=p[u] AND p[v] AND NOT s[a].
The exact objective is min 2 sum_(x,y)e[x,y] + 2 sum_(a in B)h[a], literally Lean obligationScore.

Hall failure: binary w[x] selects a nonempty owner shore. Demand D=sum_x w[x]*2 sum_y e[x,y], using exact binary-times-bounded-integer linearization. Directed source half (a,b,k), a!=b, is free iff q[a,b]=0; half k=0 is unavailable when {a,b} is active. It is eligible iff w[a]=1, or some x has w[x]=q[x,a]=q[x,b]=1 AND the graph-constant integer predicate sigma([a,b])>=0. Let A[a,b,k] be freeness AND non-reservation AND eligibility. Strict failure is D >= 1 + sum A.

Finite reduction theorem: integral minimization assignments biject with RowChoice and preserve obligationScore. At a fixed proved optimum, augmented assignments biject with (globally minimal omega, nonempty strict scoped-Hall witness W). Hence augmented UNSAT proves every global minimizer has scoped Hall; SAT plus independent literal replay is a counterexample. This is a finite reduction, not the uniform graph theorem.

Audit finding: problems/23/writeup/_codex_r20_c5_nonuniform_global_cpsat.py omits sigma>=0 in its symbolic RowCompanion eligibility. Therefore its Hall-failure model is a relaxation. Its independent evaluate_rows replay can validate returned witnesses; UNSAT of the relaxation is still sound for absence of true failures.
