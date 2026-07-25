# Erdős 742: bounded construction-family audit

## Acceptance predicate

Every graph tested by the programs in this directory was checked directly:

- order 25;
- simple and noncomplete;
- every vertex reaches every other vertex in at most two steps; and
- after each individual edge deletion, some unordered vertex pair is no
  longer reachable within two steps.

The programs do not infer D2C from a family label.

## 1. Cayley graphs of order 25

There are two groups of order 25: \(C_{25}\) and \(C_5\times C_5\).  In
either group, the 24 nonidentity elements form 12 inverse pairs.  Thus
`audit_cayley25.cpp` exhausts all \(2^{12}=4096\) undirected simple Cayley
graphs on each group.

Exact output:

```text
FAMILY C25 total=4096 d2c=12 maximum=125 mask=1321
FAMILY C5xC5 total=4096 d2c=12 maximum=125 mask=124
```

Therefore both complete Cayley families are **DEAD** for the 157-edge
certificate.  Their exact D2C maximum is 125.

## 2. One-level twin substitutions of small D2C bases

For each unlabeled D2C base \(B\), each base vertex \(i\) is replaced by a
nonempty class of size \(a_i\), where \(\sum a_i=25\).  Each class is chosen
independently to induce either a clique or an independent set.  Two distinct
classes are joined completely exactly when their base vertices are adjacent.

This also covers, after complementation, all one-level nonuniform true/false
twin-class expansions of the corresponding total-domination-critical
complements.  It does not claim to cover arbitrary hierarchical twin
operations.

`audit_small_base_blowups.cpp` enumerates every labeled graph through order 6,
keeps exactly the D2C graphs, canonically quotients by all vertex
permutations, and then exhausts every ordered positive composition of 25 and
every clique/independent type mask.

Exact output:

```text
BASES n=3 unlabeled_d2c=1
BASES n=4 unlabeled_d2c=2
BASES n=5 unlabeled_d2c=3
BASES n=6 unlabeled_d2c=5
SUMMARY max_base_n=6 compositions=248722 substitutions=14688352 above_current_best_tested=6797513 maximum=156 best_base_n=3 best_base_mask=3 best_types=0 best_sizes=12,1,12
```

The 156-edge lower bound is the \(P_3\) substitution giving
\(K_{12,13}\).  Since every substitution with more than 156 edges was
replayed through the direct D2C checker, this is an exact maximum, not a
bounded search score.

For order-7 bases, `enumerate_unlabeled_d2c7.cpp` checks all
\(2^{21}=2097152\) labeled graphs and obtains 8883 labeled D2C graphs in
exactly 10 isomorphism classes.  `audit_blowups7.cpp` then exhausts the 10
classes:

```text
n=7 labeled_d2c=8883 unlabeled_d2c=10
SUMMARY base_n=7 unlabeled_d2c=10 compositions=1345960 substitutions=172282880 above_current_best_tested=54375247 maximum_with_K12_13_baseline=156
```

Thus the complete base-order-\(\le7\) one-level mixed twin-substitution
family is **DEAD** for a 157-edge certificate.  Its exact maximum is 156.

## 3. Direct-route status

No raw order-25 graph with at least 157 edges was produced.  Hence there is no
candidate to pass to verifiers A and B.

The result closes only the two complete families above.  It neither proves
nor refutes the Murty--Simon conjecture, and it gives no UNSAT conclusion for
the unrestricted order-25 instance.
