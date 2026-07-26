# Reduced plateau SDP: canonicalization-only result

PASS. CVXPY canonicalized the corrected 3,045-variable model for
Clarabel. No SDP solver was called.

- affine equalities: `388`
- nonnegative cone: `543`
- PSD cone orders: `[154, 32, 35, 40, 5, 32, 6, 8, 33, 6, 6, 7, 6, 4, 7, 8, 6, 5, 4, 4, 6, 5, 4, 4, 6, 11]`
- canonical `A`: `[16369, 3045]`, nnz `8574476`
- canonicalization: `5.797887` seconds
- sampled peak RSS: `1245442048` bytes
- 192 GiB cap respected: `True`

The numerical direct-H basis is steering data only. Exact replay
must use the separately sealed exact-Z artifact.
