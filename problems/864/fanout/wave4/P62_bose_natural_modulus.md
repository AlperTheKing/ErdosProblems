# P62: Bose-Chowla natural-modulus carry audit

## Question

Let `Z` be an endpoint-normalized affine lift of a Bose-Chowla Sidon set of
size `p=q` in `Z/(q^2-1)Z`. Put

    h=q^2-1, gamma=h-1-max(Z), B=gamma+Z.

For `b` in `{1,2}`, the literal condition

    -b notin 3B-B

gives a fully reflected admissible construction. Since Bose-Chowla pair sums
and differences are injective modulo `h`, these profiles have

    C_S=C_D=0,
    delta=(3p^2-p+2)/2-h=(p^2-p+4)/2.

An infinite sequence of such holes would have positive quadratic defect and
would disprove the proposed constant in Problem 864.

## Exact result

The verifier exhausts every unit-multiplier class and every cyclic cut for

    q=3,4,5,7,8,9,11,13,16,17,19,23,25,27,29,31,32,
      37,41,43,47,49,53,59,61,64.

Literal holes occur for every tested `q<=23`. The final counts are one hole
at `q=19` and one at `q=23`. For all tested prime powers `25<=q<=64`, the
audit checks 115,130 distinct affine lifts and finds no literal hole.

This is a finite exact classification only. It does not prove eventual
nonexistence and does not provide an infinite counterfamily.

## Reproduction

All arithmetic is exact integer or finite-field arithmetic.

```powershell
python -B problems/864/compute/p62/audit_bose_natural_modulus.py `
  --parameters 3 4 5 7 8 9 11 13 16 17 19 `
  --output problems/864/compute/p62/bose_natural_modulus_small.json

python -B problems/864/compute/p62/audit_bose_natural_modulus.py `
  --parameters 23 25 27 29 31 32 37 41 43 47 49 53 59 61 64 `
  --output problems/864/compute/p62/bose_natural_modulus_large.json
```

The program reconstructs the Bose-Chowla set, all affine lifts, all
diagonal-inclusive unordered sums, all positive differences, modular fold
counts, and both literal targets `b=1,2`.
