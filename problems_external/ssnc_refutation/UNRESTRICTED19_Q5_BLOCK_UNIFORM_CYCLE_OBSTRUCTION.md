# Block-uniform cycle plus one-relocation obstruction

Scope: start from `theory_inputs/unrestricted19-q5-twin-fill-objective9.json` (SHA `32CAB562...B6B6DA`). Reverse all four cross arcs on every quotient edge of one directed cycle in the regular nine-block tournament, then fill one root hole as `12 -> x` and delete one present arc.

A quotient-cycle reversal preserves every quotient outdegree, so the quotient remains a regular tournament. Each high/low block pair retains degrees 9/8. For every reverse quotient arc j->i there is k with i->k->j; otherwise j would dominate i and all four outneighbors of i, contradicting regular outdegree4. Block k supplies two distinct witnesses, so every nonroot second target still has at least two witnesses and the cycle reversal alone retains objective9.

The outward root fill changes no nonroot second row because vertex12 has indegree0. Deleting an arc from a low makes degree7 and is invalid. Deleting from a high makes degree8 while one deletion cannot remove a two-witness target, so all nine lows still fail and the high adds penalty at least1. Deleting from12 leaves the nonroot objective9.

Therefore every domain-valid graph in this named family has objective at least9. This does not cover nonuniform core edits or coupled multi-arc surgery and does not resolve SSNC.
