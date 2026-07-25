#!/usr/bin/env python3
"""Finite exact proof of the saturated codimension-three Gram lemma.

Let n1,n2,n3 be independent saturated integer vectors with entries 0,+-1
and squared norms at most four.  Put G=(<ni,nj>) and M=G^{-1}.  The primitive
generators of the polar feasible cone have Gram matrix M.  Lee--Liu Lemma 3.2
therefore gives

 alpha = 1/8 + (1/24) sum_{i<j} Mij(1/Mii+1/Mjj).

Every possible G is among the positive-definite integral symmetric matrices
enumerated below: diagonal entries 1..4 and off-diagonal entries -4..4.  This
is a finite, rank-independent superset of all rhombus overlap types.
"""

from fractions import Fraction
import hashlib
import json


def alpha(a, b, c, p, q, r):
    # G = [[a,p,q],[p,b,r],[q,r,c]].  In the BV expression det(G)
    # cancels, so only cofactors are needed.
    A, B, C = b * c - r * r, a * c - q * q, a * b - p * p
    det = a * b * c + 2 * p * q * r - a * r * r - b * q * q - c * p * p
    if min(A, B, C, det) <= 0:
        return None
    cof = ((A, q * r - p * c, p * r - b * q),
           (q * r - p * c, B, p * q - a * r),
           (p * r - b * q, p * q - a * r, C))
    ans = Fraction(1, 8)
    for i, j in ((0, 1), (0, 2), (1, 2)):
        ans += Fraction(cof[i][j], 24) * (
            Fraction(1, cof[i][i]) + Fraction(1, cof[j][j])
        )
    return ans


def main():
    records = []
    for a in range(1, 5):
        for b in range(1, 5):
            for c in range(1, 5):
                for p in range(-4, 5):
                    for q in range(-4, 5):
                        for r in range(-4, 5):
                            value = alpha(a, b, c, p, q, r)
                            if value is not None:
                                records.append(((a, b, c, p, q, r), value))
    minimum = min(v for _, v in records)
    minimizers = [g for g, v in records if v == minimum]
    canonical = "\n".join(
        ",".join(map(str, g)) + ":" + str(v) for g, v in records
    ).encode("ascii")
    out = {
        "positive_definite_gram_matrices": len(records),
        "nonpositive": sum(v <= 0 for _, v in records),
        "minimum": str(minimum),
        "minimizers": minimizers,
        "sha256_records": hashlib.sha256(canonical).hexdigest(),
        "status": "PASS" if len(records) == 4320 and minimum == Fraction(1, 264) else "FAIL",
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
