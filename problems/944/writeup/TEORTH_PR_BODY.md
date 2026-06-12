# Summary

This PR adds a short comment to Erdős problem #944 recording verified partial
progress on the remaining `k=4,r=1` Dirac/Erdős case.

The problem remains open. The new comment does **not** change the status field.

# Mathematical Claim

Skottova-Steiner [SkSt25, Problem 5.2] ask whether a 6-regular `(4,1)` graph
exists, where `(4,1)` means a 4-vertex-critical graph with no critical edge.

Verified partial result:

> There is no 6-regular `(4,1)` graph on at most 14 vertices.

Additional verified structural lemmas for any hypothetical 6-regular target:

- every edge lies in at most four triangles;
- every 6-edge cut has exactly two monochromatic cut edges under every gluing
  of fixed 3-colourings of the two shores;
- the corresponding Kempe tether is forced in `G - {e,f}` for the two conflict
  edges `{e,f}`;
- no 6-edge cut has a shore of size `2..8`;
- in the 6-regular case, no nontrivial 6-edge cut has a shore of size `9..14`;
  hence any such graph on at most 29 vertices is super-6-edge-connected.

# Verification

Finite search:

```text
n=11: total=266 threecol=3 notVC=263 vcWithCritEdge=0 TARGET=0
n=12: total=7849 threecol=50 notVC=7799 vcWithCritEdge=0 TARGET=0
n=13: total=367860 threecol=849 notVC=367010 vcWithCritEdge=1 TARGET=0
n=14: total=21609301 threecol=42667 notVC=21566634 vcWithCritEdge=0 TARGET=0 badline=0
```

The C++ checker classifies each SMS stream entry as:

- 3-colourable;
- not 4-vertex-critical;
- 4-vertex-critical but with a critical edge;
- target.

No target appears. The `n=13` stream contains one 6-regular
4-vertex-critical entry, and it has critical edges. The `n=14` check was
run twice with different native chunk partitions (110 and 73 residue classes),
with identical aggregate totals.

For the 9..14-shore exclusions, nauty/C++ enumerations over the connected
candidate shores leave no survivor after the verified cut-matrix, comparable
non-neighbour, and local-multiplicity filters. The a=11 classification has a
full independent Python recount; larger sizes have independent Python spot
checks matching the C++ filter.

The proof package was red-teamed with GPT-5.5 Pro and the wording corrections
were applied: the Kempe tether is global in `G-{e,f}`, not shore-internal, and
the small-shore 3-colourability argument uses monotonicity from `G-v`.

Some Lean 4 cores compile locally with no `sorry`, `admit`, `axiom`, or
`unsafe`: singleton recolouring, the 6-cut matrix support, and the numeric
Turan shore inequality for sizes `2..7`.

# AI Disclosure

This contribution was produced by an autonomous Codex workflow with GPT-5.5 Pro
used for mathematical red-teaming. The computational claims were checked by
local C++ verifiers and the proof steps were independently re-derived before
being included.
