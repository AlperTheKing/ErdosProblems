# Exact principal chart for the rank-22 block-0 face

Let `K` be the stored `132 x 154` sparse integer matrix whose rows form the
exact kernel of the rank-22 exposing matrix `S`, and put `A = K^T`.  Thus
`A` has shape `154 x 132` and `im(A) = ker(S)`.

Use the following zero-based coordinate set:

```text
P = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,
     20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,
     38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,
     56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,
     74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,
     92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,
     109,110,111,112,113,116,117,118,119,120,121,122,123,124,
     125,126,127,128,129,133,134,135,136,143]
```

For `M = A[P,:] = K[:,P]^T`, exact fraction-free elimination gives

```text
det(M) = -155391480660729280675368894940959473664
       = -2^92 * 3^22 != 0.
```

The gate also obtains rank `132` modulo each of the disjoint primes
`1000151`, `1000159`, and `1000171`.

## Congruence theorem

For every symmetric rational `154 x 154` matrix `Q` satisfying `S Q = 0`,

```text
Q is positive semidefinite  <=>  Q[P,P] is positive semidefinite.
```

Indeed, every column of `Q` lies in `ker(S) = im(A)`.  Since `M` is
invertible, restriction to `P` determines its coefficient vector.  Applying
this to all columns and using symmetry gives the exact factorization

```text
Q = A R A^T,
R = M^(-1) Q[P,P] M^(-T),
Q[P,P] = M R M^T.
```

Both implications now follow by congruence.  The forward implication is also
the standard fact that a principal submatrix of a PSD matrix is PSD.

This is a coordinate theorem on the already exposed face.  It neither searches
for nor imposes any further face.
