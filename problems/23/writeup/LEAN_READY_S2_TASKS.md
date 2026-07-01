# Lean-Ready S2 Tasks

This file translates the current S2 reduced-theta proof target into small
formalization tasks.  It is not a Lean proof yet.

The frozen theorem package is `S2_FROZEN_STATEMENT.md`.  Treat that file as
the source of truth for the first Lean implementation.

## Formalization Scope

Do not start with the whole Erdős #23 statement.  First formalize the reusable
graph/path facts behind S2:

```text
Path-splice lemma,
two-row equal-segment lemma,
strict reduced-theta shortcut lemma.
```

These are independent of the ROWSUM-O matrix reduction and should be
formalized before the cap/row applications.

## Task 1: Shortest Walk Subpath

Lean target:

```text
If W is a shortest G.Walk from a to b, then every contiguous subwalk of W is
shortest between its endpoints.
```

Mathematical proof:

```text
replace the subwalk by a shorter walk and concatenate, contradicting
minimality of W.
```

Expected dependencies:

```text
SimpleGraph.Walk,
walk length,
walk append/concat,
Nat arithmetic.
```

## Task 2: Two-Row Segment Equality

Lean target:

```text
Let P and Q be shortest walks for bad-edge endpoints h and g.  If P and Q
meet at vertices r,s, and the P[r,s] and Q[r,s] subwalks are internally
disjoint, then unequal segment lengths imply one of P or Q is not shortest.
```

This may be easier to state contrapositive:

```text
If both P and Q are shortest, then the two segments have equal length unless
splicing one segment into the other is invalid because it repeats vertices.
```

The invalid repeated-vertex case is exactly where the reduced-theta
hypothesis is used.

## Task 3: Strict Reduced-Theta Shortcut

Lean target:

```text
In a reduced theta with no intermediate terminal door and with arm length
difference at least 2, there is a blue walk between the endpoints of one
involved bad edge with length at most ell(h)-3.
```

This task should be stated using explicit walk concatenations, not geometric
language.  Inputs should include:

```text
row walk prefix,
theta replacement arm,
row walk suffix,
replacement length <= original length - 2.
```

Then the proof is arithmetic plus walk concatenation.

## Task 4: Triangle Degeneracy

Lean target:

```text
If the strict reduced-theta splice degenerates to a two-edge blue replacement
plus the bad edge, then G contains a triangle.
```

This should be separated from Task 3 so that the main shortcut lemma can say:

```text
either the concatenated replacement is a valid shorter walk, or the
degenerate obstruction is a triangle.
```

## Task 5: Application Hypothesis Bundles

Once Tasks 1-4 are formalized, define proposition bundles for:

```text
CapTerminalProductHyp,
RowEndpointHingeHyp,
RowRareMonotonicityHyp.
```

Each bundle should expose exactly the inputs Task 3 needs:

```text
terminal-prefix rows,
chosen split/rejoin vertices,
replacement arm length saving >= 2,
no intermediate terminal door,
triangle-free.
```

The cap and row applications should then become short theorem invocations of
Task 3 plus max-cut/gamma/min-cost arguments.

## Current Risk

The only formal risk visible now is hidden in the phrase "reduced theta":
we must avoid encoding it too weakly.  In prose, reducedness supplies both:

```text
the replacement arm is a valid walk/simple path;
the strict saving is at least 2 rather than 0.
```

Lean should keep these as explicit hypotheses first, then later prove them
from the cap/row corridor definitions.
