# C120: same-root and canonical-leaf capacity

## DIRECT ROUTE

1. **Exact final deliverable.** Prove constants `A>0`, `B`, and
   `alpha>1/(2 log 2)` such that every hard source with `d(h)` canonical
   blockers reaches at least `A*d(h)^alpha-B` distinct structural leaves by
   an explicitly defined descent whose source-to-leaf incidences have a
   summable global capacity; or give an exact counterexample or capacity
   obstruction that kills this route.
2. **Current frontier.** Bound the maximum multiplicity of one literal
   seed-2 root among the canonical blockers of one hard source, then bound
   collisions after every nonstructural root is recursively sent to a
   deterministic structural splitless leaf.
3. **Logical bridge.** A power lower bound with exponent
   `alpha>1/(2 log 2)`, together with a source-to-leaf capacity no larger
   than the C112 root capacity up to an absolute factor, replaces `s(h)` by
   leaf incidences in C112.1 and closes C99 by the proof of C112.2.  A leaf
   count without that capacity statement is insufficient and will not be
   claimed as a theorem.
4. **Next falsifiable action.** Independently implement the least recursive
   closure, C116 canonical blockers, literal seed roots, and leftmost
   canonical descent.  Exact-test all hard sources through a declared
   prefix and every retained sparse C117 hard record; replay normally and
   under `python -O`.
5. **Exit condition.** Stop on an independently replayed power-law
   falsifier, an unbounded same-leaf/capacity obstruction, or a proved
   uniform collision-and-capacity theorem with the displayed exponent.

## Status

Exact test in progress.  No theorem is claimed in this initial record.

