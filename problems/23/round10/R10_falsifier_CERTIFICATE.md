# R10 exact falsifier certificate for `Gamma_11`

## Result and scope

No strict rational counterexample to

`25 * ARCBOUND_Gamma_11(x) <= (sum x)^2`

exists among nonnegative rational weightings whose primitive cleared integer
vector has total mass `q <= 50`.

This is a finite exact partial certificate. It is not a proof of the inequality
for all real weightings.

The search also gives an exact support reduction for the unresolved real
problem:

- 1474 of the 2047 nonempty supports have an arc containing no
  monochromatic support edge, hence `ARCBOUND=0`.
- The remaining 573 supports form 38 `D_22` orbits.
- Their 33 inclusion-minimal members are exactly the 33 induced `C5`s of
  `Gamma_11`.
- These induced `C5`s form three `D_22` orbits, represented by
  `{0,1,4,5,8}`, `{0,1,4,6,8}`, and `{0,2,4,6,8}`.

Thus any unresolved strict falsifier must have support containing one of those
three representative pentagons after a dihedral automorphism, and its
primitive cleared total denominator must be at least 51.

## Exactness argument

For integer `x` with `sum x=q`, strict violation is equivalent to every one of
the 56 distinct cyclic-interval monochromatic forms being at least

`T = floor(q^2/25) + 1`.

Positive `ARCBOUND` forces the support to hit a monochromatic edge in every arc
form. Exhaustive enumeration of all `2^11-1` nonempty supports proves that the
minimal supports with this property are exactly the 33 induced pentagons.
Dihedral orbit enumeration reduces these to the three representatives above.
The branch-and-bound searches all nonnegative integer vectors containing each
representative with all five designated coordinates positive.

At a partial assignment, fix one arc form. Let `r` be the unassigned mass,
`c_j` the assigned monochromatic-neighbour mass seen by future vertex `j`, and
`H` the monochromatic graph induced by the future vertices. The remaining
contribution is

`F(y) = sum_j c_j y_j + sum_{uv in E(H)} y_u y_v`, with `sum y_j=r`.

If two support vertices of `y` are nonadjacent in `H`, holding their total mass
fixed makes `F` affine in the split. Moving all their integer mass to one
endpoint therefore does not decrease `F`. Repetition leaves a clique-supported
maximizer. Every `H` is a subgraph of the triangle-free `Gamma_11`, so a
maximizer uses either one vertex or one edge. The code checks every such vertex
and edge and maximizes the edge's one-variable integer concave quadratic
exactly. This gives the exact upper bound for that arc at the node. A subtree is
pruned only if one arc's exact upper bound is below `T`.

All graph construction, support enumeration, orbit reduction, branch values,
quadratic evaluations, and pruning comparisons use integers.

## Replay

Support/orbit gate:

`python .\problems\23\round10\R10_falsifier_supports.py`

Build:

`C:\msys64\mingw64\bin\clang++.exe -O3 -march=native -std=c++17 .\problems\23\round10\R10_falsifier_bnb.cpp -o .\problems\23\round10\R10_falsifier_bnb.exe`

Finite search:

`.\problems\23\round10\R10_falsifier_bnb.exe 5 50 16`

The executable rejects thread counts above 64.

Recorded outputs are in `R10_falsifier_supports.log` and
`R10_falsifier_q5_q50.log`.

## Toolchain and SHA-256

Compiler: clang 22.1.4, target `x86_64-w64-windows-gnu`.

- `R10_falsifier_bnb.cpp`:
  `DB68FC0CBDD4709A726B0CB3B452EB4B76AFEFC9A64571192754831DAF15FAA5`
- `R10_falsifier_bnb.exe`:
  `3420FD3ED7FF5EB7A0FB3B302CBAEACD21B77EA72B15FF0FD0A2DE6A7F03935E`
- `R10_falsifier_supports.py`:
  `03C0DECABD5B88244F9EC1F900D844D47B5F5F6B3B985396B0E522F4B6330F90`

## Independent cross-check boundary

For `q=5,...,22`, the no-strict-falsifier verdict agrees with the independent
raw-composition maxima in `round3/audit_G8_int_k4.txt`. That earlier engine
recomputes every arc value directly and does not use this branch-and-bound.
