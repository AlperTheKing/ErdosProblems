# P114: abstract endpoint-plus-span Hall counterexample

A linear family of 20 ordered triples on 13 vertices, each with a proper
middle vertex, has maximum matching 19 when a triple may use only its two
outer vertices or its span length.  The exact verifier and triple list are
in `compute/p114/verify_abstract_span_hall_counterexample.py`.

Matching to all three supporting vertices and all three pairwise difference
lengths succeeds on this abstract row.  Thus the reduced span-only proof is
false, while P113's broader arithmetic Hall candidate is not affected.
