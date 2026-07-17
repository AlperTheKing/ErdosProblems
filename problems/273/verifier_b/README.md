# Verifier B: reduced odd-fiber proof

This directory contains an independent exact verifier for the reconstructed
`p >= 3` baseline.  It imports only the Python standard library and neither
imports nor invokes Verifier A.

Its proof representation differs from a direct union of the twelve classes
modulo 360:

1. partition the full period into even and odd fibers;
2. cover the even fiber by `0 (mod 2)`;
3. identify the odd fiber with `n mod 180` through `x=2n+1`;
4. verify eleven sequential residual-set transitions as 180-bit masks;
5. verify algebraically and pointwise that each reduced class lies in its
   stated lifted class;
6. verify pairwise distinctness, the true LCM, and complete exact
   trial-division certificates for every `m+1`.

Run from this directory with:

```powershell
python -B verifier_b.py baseline_half_cover_certificate.json --log verifier.log
python -B -m unittest -v test_verifier_b.py
```

`verifier.log` is deterministic.  `SHA256SUMS.txt` records hashes after the
successful run; `test_verifier_b.log` records the adversarial mutation tests.
