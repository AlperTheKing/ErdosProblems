You are tasked with resolving Graham's rearrangement conjecture, listed as
Erdős Problem 475.

For a prime p and a subset A of the nonzero elements of F_p, an ordering
a_1,...,a_t is valid when the nonempty partial sums

s_j = a_1 + ... + a_j mod p, 1 <= j <= t,

are pairwise distinct. The conjecture states that every such A has a valid
ordering.

A complete resolution is either:

1. a proof for every prime p and every subset A; or
2. one explicit prime p and subset A for which every ordering is invalid.

Prioritize direct refutation. A counterexample must be given as a canonical
sorted subset and accepted from raw data by two independently implemented
exhaustive verifiers. The first declared search layer is p=17, |A|=13,
containing exactly C(16,13)=560 subsets. Do not open another finite layer
automatically if this one has no counterexample.

Do not confuse Graham's condition with Alspach's stronger condition:
nonempty partial sums may include 0; they only need to be pairwise distinct.
Preserve the quantifiers, use every element exactly once, and perform all
arithmetic modulo p.

Begin with independent formulations, including direct backtracking,
subset/sum state search, SAT with proof logging, polynomial obstructions,
rainbow paths in Cayley digraphs, zero-sum block analysis, and adversarial
certificate checking. Maintain an explicit approach registry. Each route
must state its final deliverable, frontier, bridge to the full conjecture,
next falsifiable action, and exit condition.

Finite NO_HIT results, unchecked UNSAT output, restricted-family theorems,
or reductions to comparable open statements do not resolve the conjecture.
Stop any route that becomes a bounded cascade or reformulation maze.
