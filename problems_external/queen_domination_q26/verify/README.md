# Q26 certificate verification

Both checkers accept zero-based `[row,column]` coordinates in JSON, or a text
file containing `n = ...` followed by one coordinate pair per line.

```powershell
python scalar_verify.py fixtures/q26_ostergard_weakley_14.json --expect 14 --require-independent
python bitset_verify.py fixtures/q26_ostergard_weakley_14.json --expect 14 --require-independent
python -m unittest -v test_verifiers.py
```

`scalar_verify.py` directly compares each board square with every queen.
`bitset_verify.py` independently constructs closed queen neighborhoods by
walking eight rays and unions integer bitboards. Both reject duplicate,
out-of-range, wrong-cardinality, undominating, or (when required) attacking
placements.

The two valid fixtures are transcriptions of Section 5, page 8 of:

P. R. J. Ostergard and W. D. Weakley, *Values of Domination Numbers of the
Queen's Graph*, Electronic Journal of Combinatorics 8 (2001), R29,
https://doi.org/10.37236/1573.

The paper lists the Q25 construction in centered `(x,y)=(column,row)`
coordinates and obtains the independent Q26 upper witness by adding
`(-9,13)`. The fixture metadata records the exact source sequences and the
normalization to zero-based `[row,column]` coordinates.
