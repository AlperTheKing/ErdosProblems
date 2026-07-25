You are tasked with resolving Erdős Problem 617, the Erdős–Gyárfás balanced
colouring conjecture.

For an integer r >= 3, consider an edge-colouring of the complete graph
K_(r^2+1) with r colours. The conjecture states that there always exist r+1
vertices such that at least one colour is absent from the edges induced by
those vertices.

A complete resolution must be either:

1. a proof for every integer r >= 3; or
2. one explicit r-colouring of K_(r^2+1) in which every set of r+1 vertices
   contains every colour.

Prioritize direct refutation at the first open case r=5. A valid
counterexample must include a canonical list assigning one colour to each of
the 325 edges of K_26, a complete audit of all C(26,6)=230230 vertex sets,
and acceptance by two independently implemented exhaustive verifiers.

Begin with genuinely independent routes: algebraic constructions, exact SAT,
incremental native local search, structural extremal analysis, and
adversarial encoding review. Preserve independence of encodings and
assumptions. Require concrete colourings, equations, clauses, code,
counterexamples to proposed lemmas, or exact failure certificates.

The known affine-plane construction gives a valid colouring on 25 vertices
for r=5. Treat it as a calibration fixture and a possible construction seed,
not as a solution on 26 vertices.

Audit in particular:

- exactly-one colour semantics on unordered edges;
- the requirement that every six-set contain all five colours;
- equivalence with each colour graph having independence number at most five;
- the distinction between balanced colouring and equal colour-class sizes;
- soundness of every symmetry breaker;
- agreement of parsers and independent verifiers;
- replay of any proposed certificate from raw edge data.

A timeout, NO_HIT, approximate score, unchecked SAT assignment, restricted
construction theorem, or proof-checked UNSAT result for r=5 does not resolve
the full conjecture. Do not open r=6 automatically after a failed r=5 search.

If a candidate is found, stop the associated searches, replay it through both
verifiers, produce the complete six-set audit summary, and repeat the live
novelty search before making a discovery claim.

