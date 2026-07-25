# Unrestricted K26 exact CNF

For every unordered edge `e` of `K_26` and colour `c in {0,...,4}`, Boolean
variable `x(e,c)` states that `e` has colour `c`. One positive five-literal
clause and ten pairwise negative binary clauses impose exactly one colour on
each edge.

For every six-set `S` and colour `c`, one 15-literal clause

`OR_{e in E(S)} x(e,c)`

requires colour `c` to occur in the induced `K_6`. Thus any SAT model is
exactly a counterexample certificate for the `r=5` instance.

The only symmetry normalization is `x({0,1},0)`. It preserves satisfiability:
in any total five-colouring, edge `{0,1}` has some colour `d`; globally
permuting colour labels to send `d` to `0` preserves every six-set coverage
condition. No vertex normalization or other symmetry breaker is used.

Expected counts:

- 1,625 variables;
- 325 edge at-least-one clauses;
- 3,250 edge at-most-one clauses;
- one colour-normalization unit clause;
- `230230*5 = 1,151,150` coverage clauses;
- 1,154,726 clauses total.

`audit_full_cnf.cpp` independently decodes each variable through a separately
constructed edge table, checks every exactly-one block, reconstructs all
230,230 six-set identities by six nested loops, and marks every
six-set/colour pair exactly once.

A SAT model must be decoded with `decode_model.cpp` and replayed from the raw
edge list with the exhaustive verifiers. Timeout or interrupted search is
only `NO_HIT`, never UNSAT.
