# R29 generic global-optimization gate: INDETERMINATE

## Decision

The actual GLOBAL R29 optimization cannot be decided from the workspace artifacts. The R29 archive does not contain the 2,943-vertex graph, the 676 lists of 680 rows, the baseline tuple, a deterministic constructor, or a complete arbitrary-tuple score/component rule. It records only aggregate facts and the non-identifying SHA prefix `00186166...`.

Consequently, `30811 is globally minimal` is neither proved nor disproved for the claimed instance, and actual hub/descendant deactivation is undecidable from the supplied data.

## Exact generic certificate

`audit.py` uses a generic binary branch-and-bound over 676 selector decisions, with an integer lower bound checked against every possible completion count at each visited subcube. It verifies two landscapes consistent with every archived selector-optimization fact:

- Model A: `S(k)=30811+2k`. Exact global minimum: `30811`, explicit best tuple `(0,...,0)` (676 zeros); hubs and descendants never deactivate.
- Model B: `S(k)=30811+2k` for `k<676`, and `S(676)=0`. Exact global minimum: `0`, explicit best tuple `(1,...,1)` (676 ones); the simultaneous trade deactivates hubs and all scored descendants.

Both models have 676 selectors, 679 nonbaseline choices per selector, exactly `676*679=459004` Hamming-one replacements, baseline score `30811`, and exact Hamming-one minimum `30813`. Thus all archived local facts admit opposite global answers.

Run `python tmp/fanout/r29_gate/d09/audit.py`; it emits `certificate.json`. All acceptance arithmetic is integer-only.

## Falsifiers

This indeterminacy result is falsified by any available artifact that uniquely defines the claimed instance and arbitrary simultaneous trades: a canonical graph plus complete row lists and baseline tuple; a deterministic constructor matching a full SHA256; or a complete exact score/component transition function.

Model B's explicit tuple is a logical countermodel tuple, not asserted to be a valid descending tuple of the missing R29 instance.

## Proof gaps

- No instance-level global minimum or deactivation statement is certified.
- The archived SHA is truncated and cannot authenticate a reconstruction.
- No exact arbitrary-multi-row scoped-score semantics are present in the R29 archive.

## SHA256

Exact source and output hashes are recorded in `certificate.json` and `hashes.txt`.
