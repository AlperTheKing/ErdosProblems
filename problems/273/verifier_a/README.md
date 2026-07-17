# Verifier A: exhaustive LCM check

Run from the repository root:

```powershell
python problems/273/verifier_a/verify.py `
  problems/273/baseline/selfridge_divisors_360.json `
  --output problems/273/verifier_a/verification.json `
  --hashes problems/273/verifier_a/verification.sha256
```

The verifier uses exact integer arithmetic throughout. It checks canonical
integer residues, positive pairwise-distinct moduli, and primality of every
`m+1` by exhaustive trial division through `isqrt(m+1)`. It derives the true
LCM and tests every residue in a complete period. The output includes the
coverage multiplicity at every residue and a separate exact check after
removing modulus 2.
