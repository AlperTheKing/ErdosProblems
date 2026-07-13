# R29 D-invariance audit — d04

## Verdict

The claimed all-anchor contribution `2600` and total `19925` are **not auditable from the supplied material**. This directory contains only the task prompt and empty logging files. In particular, it contains no mathematical definition or machine-readable data for `rowCompanion`, `sameOwner`, `sameFirst`, arbitrary selectors, anchors, reservations, or ordered halves.

The only exact numerical consequence available is

```text
19925 - 2600 = 17325.
```

This arithmetic identity neither proves structural invariance nor validates either claimed count.

## Why no selector falsifier can be certified

A “smallest exact selector falsifier” requires, at minimum, a specified selector domain, a total order defining “smallest,” and an exact evaluator for the reachable pool. None is supplied. Different definitions consistent with the names can realize both outcomes:

- an invariant model, by making every admissible selector have the same `rowCompanion` image;
- a non-invariant model, by allowing two selectable rows with different companion images.

Thus neither invariance nor a falsifier follows logically from the prompt alone.

## Required conventions

An exact audit must state and encode all of the following.

1. The R29 ground set and incidence data for `N=2943`.
2. Selector domain, admissibility, and the order used to minimize a falsifier.
3. Whether `rowCompanion` is directed, whether the selected row itself is included, and whether the pool is a set or multiset.
4. The exact `sameOwner` and `sameFirst` maps/relations.
5. Reservations: the reserved elements and whether removal occurs before or after reachability and union.
6. Ordered half: orientation, endpoint/tie convention, and whether reversal represents the same object.
7. Anchor set and the precise per-anchor contribution being summed.
8. Disjointness criterion for the union with `sameOwner`/`sameFirst` (literal element identity, tagged provenance, or another convention).

Without these conventions, even the phrase “disjoint union” has multiple inequivalent exact interpretations.

## Reproduction

Run `python checker.py` from this directory. `checker.out` is the exact captured stdout. `hashes.sha256` records SHA-256 hashes of the prompt, checker, output, and this report. The checker uses integer arithmetic only and sorts all emitted keys and file names.
