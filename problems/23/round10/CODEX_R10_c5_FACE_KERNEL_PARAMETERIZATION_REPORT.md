# Exact full parameterization of the plateau Gram face

## Exact artifact

`Zq` has shape [8647, 2518], 347912 nonzeros, rank 2518, and satisfies `H Zq=0` exactly.
Its coefficient range is [-106240, 135288], with at most 18 bits.
Full rank was replayed modulo [1000003, 2000003].

## Central block

The central block basis has shape 1946 x 582, 265598 nonzeros, and was selected after 7152 Reynolds candidates.
Its primitive coefficient range is [-106240, 135288].
Raw condition number: 4.351740e+14; column-normalized condition number: 1.388232e+12.

## Numerical solver preconditioner

The archive also stores a blockwise float64 QR basis spanning the exact columns numerically.
It uses 23538464 bytes; maximum block orthogonality error is 2.220e-15, and maximum `H Q` residual is 4.338e-05.

The QR blocks are numerical steering data only. Exact rational reconstruction must return to the integer `Zq`/kernel quotient and pass the exact gates.

## Enumeration

Tested 10517 Reynolds candidates in 26.793 seconds; 11 averaged to zero.

## Scope

No SDP was built or solved. This artifact removes `Hq=0` by exact parameterization but does not itself prove feasibility.
