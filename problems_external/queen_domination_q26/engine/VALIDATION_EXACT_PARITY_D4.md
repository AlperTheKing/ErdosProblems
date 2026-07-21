# Exact, parity, and D4 validation

## Certified parity condition

`--balanced-parity` is accepted by the CLI only together with
`--exact --n 26 --k 13`. The exact constraint gives 13 queens. The two
checkerboard parity constraints each impose an upper bound of 7, hence the
only possible counts are 6 and 7. Its mathematical basis is the target
registry's cited combination of Weakley (2022), Proposition 11 and Theorem 18.

## D4 lex-leader argument

For each of the seven nonidentity board symmetries, the encoder adds the clause
scheme from `TahaRostami/Gamma/AddSymBreak.py`, existentially encoding
`X <=lex g(X)` on primary square variables. Queen domination and exact
cardinality are D4 invariant. The two parity caps are invariant as a pair,
because a symmetry can at most exchange the two color classes. Every finite
D4 orbit therefore contains a lexicographically least representative.

When the prefix variable before a position is true, the three clauses have
these effects: equal bits force the next prefix true; `X=0,Y=1` permits it to
become false; and `X=1,Y=0` is impossible. Once false, the remaining prefix
variables can remain false, except for the harmless final unit variable.
Thus the auxiliary variables have an extension exactly when `X <=lex Y`.

## Computational checks

- All seven generated D4 orderings agree with the official script for every
  board size from 1 through 8.
- On the Q13 Hilbert/mtotalizer calibration formula, the complete formula with
  D4 clauses has the same normalized clause multiset as the official script:
  2,188 variables and 7,581 clauses.
- Exhaustive fixed-primary tests covered 16,768 assignments on Q2 and Q3,
  across both cardinality encodings, both literal orders, exact/at-most modes,
  balanced-parity cases, and D4 on/off. PySAT extension existence agreed with
  the direct semantic predicate in every case.

## Q26 encode-only artifact

Command (no SAT solver was invoked):

```text
python engine/pysat_search.py --n 26 --k 13 --encoding mtotalizer --ordering hilbert --exact --balanced-parity --d4-lex --encode-only --dimacs engine/cnf/q26_k13_exact_balanced_hilbert_mtotalizer_d4.cnf --model-json engine/cnf/q26_k13_exact_balanced_hilbert_mtotalizer_d4.json
```

The DIMACS header is `p cnf 16963 92509`. It contains 676 primary variables,
7,908 global-cardinality auxiliaries, 3,640 parity auxiliaries, and 4,739 D4
auxiliaries. Its SHA-256 is
`B21DDD5909880752D8F41EBC515083BD5B35350CEEB49BA1224AB46E4A4C643E`.
