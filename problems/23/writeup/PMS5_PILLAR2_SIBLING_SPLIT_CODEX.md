# PMS-5 Pillar-2 Sibling Split

Status: exact diagnostic, not a proof.

Claude's 2026-07-01 Pillar-2 survey showed that all census L=5-multi
overloaded rows occur in two N=10 seeds:

```text
I?BD@g]Qo    20 rows
I?`FAo]]?    16 rows
```

with three component fingerprints.  The seven-cut algebra currently covers
the equality seed `I?BD@g]Qo`.  This note records the first structural split
for the sibling seed.

## Exact Seed Relation

The sibling seed contains the equality seed as a spanning subgraph plus one
extra edge.

One embedding is:

```text
0 -> 7
1 -> 5
2 -> 0
3 -> 2
4 -> 3
5 -> 1
6 -> 4
7 -> 6
8 -> 9
9 -> 8
```

Under this embedding:

```text
E(I?BD@g]Qo) maps into E(I?`FAo]]?)
extra edge = (3,7)
```

For the equality row

```text
side = 0001111000
P    = (7,5,8,6,9)
M    = {(1,9),(2,7),(7,9)}
```

the image is the sibling row

```text
side = 0111100000
P    = (6,1,9,4,8)
M    = {(5,8),(0,6),(6,8)}
extra edge (3,7) is blue
```

## Row-by-Row Embedding Gate

Script:

```text
python problems/23/writeup/_codex_ocpms_sibling_embedding.py
```

Result:

```text
eq_rows 20 sib_rows 16 embeddings 10
matched 14 failures 2
VERDICT FAIL
```

Meaning: 14 of the 16 sibling overloaded rows are exactly equality-atom
overloaded rows with one additional blue edge in the sibling graph.  For
these rows, the desired proof target is a monotonicity lemma:

```text
adding blue edges while preserving the bad set and distinguished row cannot
increase the row-overlap I(P).
```

If that monotonicity is proved, the seven-cut equality-atom certificate
dominates these 14 sibling rows.

## Residual Low Atom

The two rows not covered by strict bad-set-preserving embeddings are:

```text
side 1111000010
P    (4,8,6,1,7)
M    {(3,8),(4,7),(4,9)}
I    152/15

side 1110000110
P    (3,8,6,1,9)
M    {(1,7),(3,9),(4,9)}
I    152/15
```

Script:

```text
python problems/23/writeup/_codex_ocpms_sibling_embedding_relaxed.py
```

Result:

```text
ROW side 1111000010 P (4, 8, 6, 1, 7) I 152/15 M [(3, 8), (4, 7), (4, 9)] relaxed 0
ROW side 1110000110 P (3, 8, 6, 1, 9) I 152/15 M [(1, 7), (3, 9), (4, 9)] relaxed 0
```

These are not row/cut images of equality-atom rows even under the relaxed
embedding test.  They are easier numerically:

```text
I = 152/15 < 32/3
margin = 40
```

Attachment classifier signatures for these residual rows:

```text
on-row contribution: 13/3
off contribution:    14/5
off contribution:    3
total:               152/15
```

So the Pillar-2 structure now splits into two concrete proof subtargets:

1. Equality-supergraph monotonicity for the 14 strict sibling rows.
2. A separate residual-low atom for the 2 rows with contribution profile
   `(13/3, 14/5, 3)`.

## Current Proof-Relevant Interpretation

The sibling seed is not wholly a quotient of the equality atom, but most of
its overloaded rows are blue-edge supergraphs of equality-atom rows.  The
remaining rows have strictly smaller overlap and should be certified by a
small separate inequality, not by forcing them into the seven-cut equality
template.

## Contribution Delta for Supergraph Rows

Script:

```text
python problems/23/writeup/_codex_ocpms_sibling_delta.py
```

Result:

```text
matched 14
delta_multisets
8 (0, 1/6, 1/3)
6 (0, 0, 1/3)
total_deltas
8 1/2
6 1/3
```

So in every strict supergraph match, the extra blue edge changes the per-bad-edge row-capture contributions by a nonnegative vector. The total drop in `I(P)` is either `1/2` or `1/3`.

This suggests an even smaller finite proof target for the supergraph class: show that the extra blue edge only adds shortest rows whose average overlap with the distinguished row is no larger than the pre-existing average, edge-by-edge.

## Residual-Low Denominator Dump

Script:

```text
python problems/23/writeup/_codex_ocpms_residual_low_dump.py
```

Both residual rows have the same contribution profile:

```text
14/5 + 3 + 13/3 = 152/15
32/3 - 152/15 = 8/15
```

Representative row:

```text
side 1111000010
P    (4,8,6,1,7)
M    ((3,8),(4,9),(4,7))

(3,8): denominator 5, overlaps [2,3,3,4,2], contribution 14/5
(4,9): denominator 5, overlaps [3,4,3,2,3], contribution 3
(4,7): denominator 3, overlaps [4,5,4], contribution 13/3
```

The second residual row is symmetric.  Thus the residual-low atom is not merely positive-margin by black-box enumeration; it is the explicit denominator pattern `(5,5,3)` with overlap profiles above.
