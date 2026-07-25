"""AUDIT by-product: the Andrasfai chain is an INDUCED chain, with a one-line proof.

CLAIM.  For every k >= 2 the identity map on {0,1,...,3k-2} is an induced embedding
        And(k)  ->  And(k+1)
when both are written as circulants with connection set {c : c = 1 mod 3}.

PROOF.  For 0 <= i < j <= 3k-2 put t = j-i, so 1 <= t <= 3k-2.  In And(k) (mod 3k-1)
the residue of t is t itself, so i~j iff t = 1 mod 3.  In And(k+1) (mod 3k+2) the
residue of t is again t (t < 3k+2), and the connection set is {1,4,...,3k+1}, so
i~j iff t = 1 mod 3.  The two conditions coincide.  []

CONSEQUENCES (both stronger / cleaner than what G8.md states)
 (1) A(k) = max_x psi(And(k),x) is nondecreasing DIRECTLY by accepted fact 3
     (induced-subgraph monotonicity); the quoted Bondy-Hell circular-chromatic
     theorem is not needed.
 (2) And(4) is an induced subgraph of And(k) for every k >= 4, so the section 6.3
     blocking lemma (verified only at k = 4,5 in G8.md) propagates to EVERY k >= 4:
     a cut of And(k) active at all induced C5s of And(k) would restrict to a cut of
     the induced And(4) active at all 33 induced C5s of that And(4), which is empty.
"""
import sys
from audit_G8_core import and_circulant


def identity_is_induced_embedding(k):
    nA, adjA = and_circulant(k)
    nB, adjB = and_circulant(k + 1)
    for i in range(nA):
        for j in range(i + 1, nA):
            if (((adjA[i] >> j) & 1) != ((adjB[i] >> j) & 1)):
                return False, (i, j)
    return True, None


if __name__ == "__main__":
    for k in range(2, 30):
        ok, wit = identity_is_induced_embedding(k)
        if not ok:
            print(f"And({k}) -> And({k+1}) identity embedding FAILS at {wit}")
            sys.exit(1)
    print("identity map {0,...,3k-2} is an induced embedding And(k) -> And(k+1) "
          "for every k = 2..29 : VERIFIED")
    # and therefore And(4) sits inside every And(k), k >= 4
    n4, adj4 = and_circulant(4)
    for k in range(5, 30):
        nk, adjk = and_circulant(k)
        ok = all((((adj4[i] >> j) & 1) == ((adjk[i] >> j) & 1))
                 for i in range(n4) for j in range(i + 1, n4))
        if not ok:
            print(f"And(4) NOT induced in And({k}) on {{0..10}}")
            sys.exit(1)
    print("And(4) = And(k)[{0,...,10}] for every k = 4..29 : VERIFIED")
