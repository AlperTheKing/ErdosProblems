"""AUDIT 2.  C5[n]: verify (a) the profile formula (star) independently, (b) Proposition 3.1's
EXACT tight-profile list (all 10 families) for n = 1..14, (c) the count 10n, (d) the claim
that B(v,2) in C5[n] is V\\V_4 (report Sec.3 bullet 3), (e) the tight-set counts 10/30/70.
sigma is computed from the actual edge list for n<=3 and from an independently derived
profile formula for all n.
"""
import os
import sys
from itertools import product

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aud_core import blowup, sigma_set, sigma_by_recut, adj_of, maxcut_brute

C5_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)]
# canonical maximum cut: parts V1,V3 (idx 0,2) on side 0 ; V2,V4,V5 (idx 1,3,4) on side 1
COL = [0, 1, 0, 1, 1]


def build(n):
    N, E, part, start = blowup(C5_EDGES, [n] * 5)
    side = [COL[part[v]] for v in range(N)]
    return N, E, part, side


def sigma_profile_direct(x, n):
    """Independently derived: sigma(S) = sum over pattern edges of eps_ij*(x_i(n-x_j)+x_j(n-x_i))."""
    tot = 0
    for (i, j) in C5_EDGES:
        eps = 1 if COL[i] != COL[j] else -1
        tot += eps * (x[i] * (n - x[j]) + x[j] * (n - x[i]))
    return tot


def prop31_families(n):
    """The exact list claimed in Proposition 3.1 (indices 0..4 = V_1..V_5)."""
    fams = set()
    for t in range(n + 1):
        fams.add((0, 0, 0, 0, t))
        fams.add((0, 0, 0, t, 0))
        fams.add((0, 0, t, n, 0))
        fams.add((0, t, n, n, 0))
        fams.add((t, n, n, n, 0))
        fams.add((n, n, n, n, t))
        fams.add((n, n, n, t, n))
        fams.add((n, n, t, 0, n))
        fams.add((n, t, 0, 0, n))
        fams.add((t, 0, 0, 0, n))
    return fams


def main():
    print("=== (a) profile formula check against the real graph (n=1,2,3) ===")
    for n in (1, 2, 3):
        N, E, part, side = build(n)
        bad = 0
        for mask in range(1 << N):
            S = {v for v in range(N) if (mask >> v) & 1}
            x = [0] * 5
            for v in S:
                x[part[v]] += 1
            a = sigma_set(S, E, side)
            b = sigma_profile_direct(x, n)
            c = sigma_by_recut(S, E, side)
            if not (a == b == c):
                bad += 1
        print(f"  n={n}: N={N}, all {1<<N} subsets: profile formula == direct == recut  "
              f"({'OK' if bad == 0 else 'MISMATCHES %d' % bad})")

    print("\n=== (b,c) Proposition 3.1 exact tight list, n=1..14 ===")
    for n in range(1, 15):
        tight = set()
        neg = 0
        for x in product(range(n + 1), repeat=5):
            v = sigma_profile_direct(x, n)
            if v == 0:
                tight.add(x)
            elif v < 0:
                neg += 1
        fam = prop31_families(n)
        print(f"  n={n:2d}: #tight={len(tight):3d}  10n={10*n:3d}  "
              f"tight==Prop3.1list: {tight == fam}  "
              f"missing={len(fam - tight)} extra={len(tight - fam)}  #sigma<0 profiles={neg}")
        if tight != fam:
            print("     EXTRA (tight but not in Prop 3.1):", sorted(tight - fam)[:10])
            print("     MISSING (in Prop 3.1 but not tight):", sorted(fam - tight)[:10])

    print("\n=== (d) is B(v,2) in C5[n] equal to V \\ V_4 (report Sec.3 bullet 3)? ===")
    for n in (1, 2, 3):
        N, E, part, side = build(n)
        adj = adj_of(N, E)
        v = 0                                  # v in V_1
        ball = set([v]) | set(adj[v])
        for a in list(adj[v]):
            ball |= adj[a]
        x = [0] * 5
        for u in ball:
            x[part[u]] += 1
        print(f"  n={n}: v in V_1, |B(v,2)|={len(ball)} of N={N};  profile={tuple(x)};  "
              f"report claims (n,n,n,0,n)=({n},{n},{n},0,{n});  ball==V: {len(ball) == N}")

    print("\n=== (e) tight-set counts per maximum cut, n=1,2,3 (independent) ===")
    for n in (1, 2, 3):
        N, E, part, side = build(n)
        best, cuts = maxcut_brute(N, E)
        counts = set()
        for sd in cuts:
            c = 0
            for mask in range(1 << N):
                S = {v for v in range(N) if (mask >> v) & 1}
                if sigma_set(S, E, sd) == 0:
                    c += 1
            counts.add(c)
        print(f"  n={n}: maxcut={best} bip={len(E)-best} (n^2={n*n})  #maxcuts(v0 pinned)={len(cuts)}  "
              f"#tight sets per cut = {sorted(counts)}")


if __name__ == "__main__":
    main()
