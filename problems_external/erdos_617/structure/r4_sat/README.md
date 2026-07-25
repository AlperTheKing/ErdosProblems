# Exact R4 permutation-packing formulation

The first of the five copies is fixed to the identity permutation. This is
WLOG: given permutations `pi_0,...,pi_4`, relabel every host vertex by
`pi_0^{-1}`. The first image becomes canonical `G_61`, and all edge
intersections are preserved. No other symmetry breaker is used.

For free copies `c=1,...,4`:

- `p(c,i,u)` means source vertex `i` maps to host vertex `u`;
- `a(c,e,h,o)` means source edge `e` maps to host edge `h` in orientation
  `o`; and
- `y(c,h)` means copy `c` occupies host edge `h`.

Every `p` matrix is constrained to be a permutation by bidirectional row and
column exactly-one clauses. Each auxiliary variable has the full definition

`a <-> (p_endpoint_1 AND p_endpoint_2)`.

Each occupancy variable has the full definition

`y(c,h) <-> OR_(e,o) a(c,e,h,o)`.

Units forbid the four free copies from using an edge of the fixed identity
copy. Pairwise negative `y` clauses forbid collisions among free copies.
Thus SAT is equivalent to five pairwise edge-disjoint permutations, not only
a relaxation.

Exact expected counts:

```
p variables       2,704
a variables     158,600
y variables       1,300
total variables 162,604

permutation ALO                  208
permutation AMO               67,600
a bidirectional definitions  475,800
a implies y                  158,600
y reverse definitions          1,300
fixed-copy exclusion units        244
free-copy edge AMO              1,950
total clauses                 705,702
```

`audit_r4_packing_cnf.cpp` parses every clause independently, reconstructs
the source and host edge tables, checks both directions of every auxiliary
definition, and rejects missing, duplicate, or extraneous clauses.

`decode_r4_model.cpp` extracts five permutations from a SAT witness.
`verify_r4_packing.cpp` then ignores all SAT auxiliaries, maps the raw
canonical graph through the permutations, checks all 305 packed edges for
collisions, assigns the 20 uncovered edges colour zero, and exhausts all
230,230 six-sets.

## Calibration plan

1. Re-run `verify_r4_g61.exe` on the frozen graph and require
   `n=26,e=61,alpha=5,omega=5`.
2. Compile the generator and independent auditor with warnings enabled.
3. Generate the full CNF and require the exact counts above.
4. Run the auditor; mutate one clause from each semantic family in disposable
   copies and require rejection.
5. Feed `verify_r4_packing` an all-identity five-row fixture and require an
   overlap rejection.
6. Only after the aggregate worker cap has room, run one proof-producing SAT
   solver. SAT must pass decoder, raw packing checker, and both unrestricted
   colour verifiers. UNSAT is accepted only after independent proof checking;
   timeout is only `NO_HIT`.
