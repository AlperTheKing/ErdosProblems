# Exact `Z_31` compatible-starter supplier

`z31_supplier.cpp` supplies pairs of starters for Wolfe's merger.  It does not
test the `2^15` high/low assignments.

## Definitions and enumeration

A normalized starter has hole `0`, uses every vertex `1,...,30` exactly once,
and has exactly one edge of every unsigned cyclic difference `1,...,15`.
The deterministic DFS chooses the least uncovered vertex and pairs it with an
uncovered vertex whose difference is unused.  Consequently each emitted pool
starter is an exact-cover solution and no pool starter is repeated.

For pool indices `i < j` and `delta in 1,...,30`, the supplier compares
starter `i` with starter `j + delta`.  These have holes `0` and `delta`.
They are compatible exactly when their alternating union, followed from hole
`0`, visits all 31 vertices once and terminates at `delta`.  Every enumerated
triple `(i,j,delta)` is a distinct concrete ordered starter pair.

Warm-up deduplication is stronger.  An ordered pair with holes `a,b` is sent by
the unique affine map `x -> (x-a)/(b-a)` to holes `0,1`; all unordered edges
of each starter are sorted.  The lexicographically smaller encoding obtained
before or after swapping the two starters is its 60-byte canonical key.  Thus
the warm-up records are distinct modulo common `AGL(1,31)` maps and starter
swap.  Individual starters are canonically encoded by taking the minimum over
the 30 multipliers after translating their hole to zero.

## GPU input format

The file is ASCII text with byte `0A` line endings; there is no byte-order
issue.  Its first line is the decimal record count `R`.  The next `R` lines
have exactly 60 decimal integers separated by one ASCII space:

```
S1_x(1) S1_y(1) ... S1_x(15) S1_y(15)
S2_x(1) S2_y(1) ... S2_x(15) S2_y(15)
```

The notation is displayed on two lines above only for readability; one record
occupies one physical line.  The pair at slot `d` has unsigned cyclic
difference `d`.  `S1` has hole 0 and `S2` has a nonzero hole.  The global
`pair_id` is the zero-based record position.  A consumer must still validate
both starters and their single alternating Hamilton path before evaluating
masks.

The generated warm-up is `z31_supplier.warmup.txt`: 65,536 records plus its
header, SHA-256
`A68A13321EFE4C0AAA8ECA8390C1B1AA7CDB5692B63318FFF6FAFB21690383E8`.

## Reproduction

Warning-clean release build:

```text
g++ -std=c++20 -O3 -march=native -DNDEBUG -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror problems_external\p1f_k64\z31_supplier.cpp -o problems_external\p1f_k64\z31_supplier.exe
```

Tests and warm-up:

```text
problems_external\p1f_k64\z31_supplier.exe --self-test
problems_external\p1f_k64\z31_supplier.exe --pool 4096 --count 65536 --emit problems_external\p1f_k64\z31_supplier.warmup.txt
```

The self-test validates Pike's published compatible `Z_27` pair, 128 generated
`Z_31` starters, multiplier-invariance of starter canonicalization, and all
1,860 common affine images and swaps of a compatible pair.

On the current host, warm-up production took 0.052 seconds (1.271 million
affine/swap-distinct records/s).  A 64-thread, 32,768-starter run exhausted all
16,105,635,840 distinct candidate triples in 9.892 seconds and materialized
4,019,285,332 compatible records (406.3 million records/s).  The sustained
benchmark intentionally does not perform the warm-up's affine-isomorphism
deduplication; its candidate triples themselves are exact and nonrepeating.
