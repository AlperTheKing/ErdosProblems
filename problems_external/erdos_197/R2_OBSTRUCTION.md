# R2 obstruction certificate

The universal extension lemma in route R2 is false.

Take the ordered two-colouring of `[10]`

- colour 0: `1, 6, 7, 3`;
- colour 1: `2, 4, 9, 10, 8, 5`.

It is valid. Colour 0 has no three-term arithmetic progression. The only
three-term arithmetic progressions in colour 1 are `(2,5,8)` and `(8,9,10)`;
their position triples are `(0,5,4)` and `(4,2,3)`, so neither is monotone.

If 11 receives colour 0, `(1,6,11)` requires `11` before `6`, while
`(3,7,11)` requires `7` before `11`; this contradicts `6` before `7`.
If 11 receives colour 1, `(5,8,11)` requires `8` before `11`, while
`(9,10,11)` requires `11` before `10`; this contradicts `10` before `8`.
Thus 11 cannot be inserted in either colour order.

Both independent C++ verifiers reject every one of the 12 possible insertions.
The candidate files are `engine/calibration/extend11_c*_p*.txt`.

This kills only the statement that every valid prefix has a one-point (or
block) extension. It does not address invariant-restricted prefixes and does
not resolve Erdős Problem 197.
