# Certificate Format


## Canonical final system file

A future p >= 5 solution will use `certificate/system.json` with UTF-8/LF canonical JSON:

```json
{
  "schema": "erdos-273-covering-system-v1",
  "problem": 273,
  "congruences": [
    {"residue": 0, "modulus": 4}
  ]
}
```

Requirements enforced by Verifier A:

- root is an object and `congruences` is a nonempty array;
- every residue and modulus is a JSON integer, not Boolean or float;
- `modulus > 0` and `0 <= residue < modulus`;
- moduli are pairwise distinct;
- each `modulus+1` is exactly prime and at least 5;
- the true LCM is computed from the parsed moduli;
- every residue of that true LCM is covered.

`certificate/system.txt` is the human serialization, one canonical `residue modulus` pair per LF-terminated line, in the same order as JSON.

## Independent recursive certificate

Verifier B must not call Verifier A. Its certificate records a parity/CRT tree or sequential residual partition. Every node/leaf stores:

- ambient period or CRT cell;
- before, removed, and after residual representations;
- a selected congruence and exact containment relation;
- cardinalities checked from the representation;
- child partition/disjointness obligations.

The verifier reconstructs masks/cells, checks `removed union after = before`, checks disjointness, ends with empty residual, independently checks distinct moduli and primality, and hashes certificate, verifier, and transcript.

## Baseline separation

`baseline/selfridge_divisors_360.json` is schema-compatible test data but is not a Problem 273 solution: it includes modulus 2 with successor prime 3. Final artifacts must never alias or copy it to `certificate/system.json` unless modulus 2 has been eliminated and every p >= 5 check passes.
