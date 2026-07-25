"""Q4: exact rational solution of a linear system, via one big prime + rational reconstruction,
followed by an EXACT Fraction re-check (so a failed reconstruction can never go unnoticed)."""
from fractions import Fraction as F


P = (1 << 521) - 1  # Mersenne prime 2^521-1: the reconstruction bound 2^260 covers the
                    # denominators produced by the exact projectors (~10^22) with room to spare


def _inv(a, p=P):
    return pow(a % p, p - 2, p)


def solve_mod(A, b, p=P):
    """A: list of rows of ints (mod p), b: list of ints.  Returns one solution or None.
    Handles rank deficiency by setting non-pivot variables to 0."""
    m, n = len(A), len(A[0])
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    piv = []
    r = 0
    for c in range(n):
        if r >= m:
            break
        sel = None
        for i in range(r, m):
            if M[i][c] % p:
                sel = i
                break
        if sel is None:
            continue
        M[r], M[sel] = M[sel], M[r]
        iv = _inv(M[r][c], p)
        M[r] = [(v * iv) % p for v in M[r]]
        for i in range(m):
            if i != r and M[i][c] % p:
                f = M[i][c]
                M[i] = [(vi - f * vr) % p for vi, vr in zip(M[i], M[r])]
        piv.append(c)
        r += 1
    for i in range(r, m):
        if M[i][n] % p:
            return None                     # inconsistent mod p
    x = [0] * n
    for i, c in enumerate(piv):
        x[c] = M[i][n] % p
    return x


def rat_recon(a, p=P, bound=None):
    """Rational reconstruction of a mod p."""
    if bound is None:
        bound = __import__('math').isqrt(p // 2)
    r0, r1 = p, a % p
    s0, s1 = 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    if s1 == 0:
        return None
    return F(r1 if s1 > 0 else -r1, abs(s1))


MERSENNE = [521, 1279, 2203, 4253]   # exponents of Mersenne primes, escalating


def solve_exact(rows, rhs, primes=None):
    """rows: list of lists of Fractions; rhs: list of Fractions.  Returns exact solution or None.
    Escalates the modulus until the exact re-check passes (rational reconstruction needs the
    modulus to exceed twice the square of the largest numerator/denominator in the answer)."""
    for e in (primes or MERSENNE):
        x = _solve_once(rows, rhs, (1 << e) - 1)
        if x is not None:
            return x
    return None


def _solve_once(rows, rhs, P):
    # clear denominators row by row
    Ai, bi = [], []
    for row, b in zip(rows, rhs):
        den = 1
        for v in row + [b]:
            den = den * v.denominator // __import__('math').gcd(den, v.denominator)
        Ai.append([int(v * den) % P for v in row])
        bi.append(int(b * den) % P)
    xm = solve_mod(Ai, bi, P)
    if xm is None:
        print("      [modsolve] system is INCONSISTENT mod p")
        return None
    x = []
    for v in xm:
        f = rat_recon(v, P)
        if f is None:
            print("      [modsolve] rational reconstruction failed")
            return None
        x.append(f)
    # exact re-check
    for i, (row, b) in enumerate(zip(rows, rhs)):
        if sum(c * xi for c, xi in zip(row, x) if xi) != b:
            print(f"      [modsolve] exact re-check failed at row {i} "
                  f"(reconstruction bound too small: raise the prime)")
            return None
    return x
