"""Exact tight-set census for the canonical maximum cut of C5[n], via part counts.

Parts V1..V5 in cyclic order (indices 0..4).  Canonical maximum cut:
    side 0 = V1 u V3      side 1 = V2 u V4 u V5
so B-pairs are (1,2),(2,3),(3,4),(5,1) and the unique monochromatic pair is (4,5).
For S with s_i = |S n V_i|,
    sigma(S) = f12 + f23 + f34 + f51 - f45 ,  f_ij = s_i(n-s_j) + s_j(n-s_i).
(Valid because consecutive parts induce complete bipartite graphs, so sigma only
depends on the profile.)  All arithmetic integer.
"""


def sigma_prof(s, n):
    def f(i, j):
        return s[i] * (n - s[j]) + s[j] * (n - s[i])
    return f(0, 1) + f(1, 2) + f(2, 3) + f(4, 0) - f(3, 4)


def census(n):
    tight, neg = [], []
    for s0 in range(n + 1):
        for s1 in range(n + 1):
            for s2 in range(n + 1):
                for s3 in range(n + 1):
                    for s4 in range(n + 1):
                        v = sigma_prof((s0, s1, s2, s3, s4), n)
                        if v == 0:
                            tight.append((s0, s1, s2, s3, s4))
                        elif v < 0:
                            neg.append(((s0, s1, s2, s3, s4), v))
    return tight, neg


def predicted(s, n):
    """Claimed characterisation of tight profiles (see report)."""
    s0, s1, s2, s3, s4 = s
    def core(a, b, c, d, e):
        # (i)  S inside V4 :  profile (0,0,0,t,0)
        # (ii) S inside V5 :  profile (0,0,0,0,t)
        # (iii) S = V4 u (subset of V3) with V4 full ... general form below
        return None
    # family 1 : s0=s1=s2=0, s4=0 (any s3)          [S contained in V4]
    if s0 == s1 == s2 == 0 and s4 == 0:
        return True
    # family 2 : s0=s1=s2=0, s3=0 (any s4)          [S contained in V5]
    if s0 == s1 == s2 == 0 and s3 == 0:
        return True
    # family 3 : V4 full, V5 empty, V1,V2 empty, any s2  [S = V4 u (subset of V3)]
    if s3 == n and s4 == 0 and s0 == s1 == 0:
        return True
    # family 4 : V5 full, V4 empty, V2,V3 empty, any s0  [S = V5 u (subset of V1)]
    if s4 == n and s3 == 0 and s1 == s2 == 0:
        return True
    return False


if __name__ == "__main__":
    for n in range(1, 8):
        tight, neg = census(n)
        assert not neg, f"negative sigma at n={n}: {neg[:3]}"     # the cut IS maximum
        pred = [s for s in tight if predicted(s, n)]
        missing = [s for s in tight if not predicted(s, n)]
        extra = []       # profiles predicted tight but not tight
        for s0 in range(n + 1):
            for s1 in range(n + 1):
                for s2 in range(n + 1):
                    for s3 in range(n + 1):
                        for s4 in range(n + 1):
                            s = (s0, s1, s2, s3, s4)
                            if predicted(s, n) and sigma_prof(s, n) != 0:
                                extra.append(s)
        comp = [tuple(n - x for x in s) for s in tight]
        closed = all(sigma_prof(c, n) == 0 for c in comp)
        print(f"n={n}: #tight profiles={len(tight)}  "
              f"predicted-covers={len(pred)}  missed={len(missing)}  false-positives={len(extra)}  "
              f"complement-closed={closed}")
        if n <= 3:
            print("   tight profiles:", tight)
        if missing:
            print("   MISSED:", missing[:20])
