"""Task F2(ii): EXACT census of tight switch sets of the extremal graph C5[n].

For n = 1,2,3 we
  * enumerate every maximum cut of C5[n] (brute force over all 2^(N-1) bipartitions),
  * for each maximum cut enumerate every S subset V with sigma(S) = 0,
  * classify the tight sets by their part-profile.
Everything is integer arithmetic.
Run:  python c5_tight_sets.py
"""
from collections import Counter, defaultdict


def c5n(n):
    N = 5 * n
    part = [v // n for v in range(N)]
    E = []
    for i in range(5):
        j = (i + 1) % 5
        for a in range(i * n, i * n + n):
            for b in range(j * n, j * n + n):
                E.append((min(a, b), max(a, b)))
    return N, E, part


def masks(N, E):
    adj = [0] * N
    for (u, v) in E:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def popcount(x):
    return bin(x).count('1')


def analyse(n, verbose=True):
    N, E, part = c5n(n)
    adj = masks(N, E)
    # --- all maximum cuts ---
    best = -1
    cuts = []
    for mask in range(1 << (N - 1)):       # vertex 0 fixed to side 0
        sidemask = mask << 1               # bit v set  <=>  v on side 1
        c = 0
        for (u, v) in E:
            if ((sidemask >> u) & 1) != ((sidemask >> v) & 1):
                c += 1
        if c > best:
            best, cuts = c, [sidemask]
        elif c == best:
            cuts.append(sidemask)
    bip = len(E) - best
    print(f"C5[{n}]: N={N} |E|={len(E)} maxcut={best} bip={bip} (= n^2 = {n*n}) "
          f"#maximum cuts (vertex 0 fixed) = {len(cuts)}")

    profiles = Counter()          # part-profile of tight sets, over all max cuts
    per_cut_counts = []
    for sidemask in cuts:
        # adjacency split into B / M for this cut
        adjB = [0] * N
        adjM = [0] * N
        for u in range(N):
            for v in range(N):
                if (adj[u] >> v) & 1:
                    if ((sidemask >> u) & 1) != ((sidemask >> v) & 1):
                        adjB[u] |= 1 << v
                    else:
                        adjM[u] |= 1 << v
        tight = []
        for S in range(1 << N):
            s = 0
            T = S
            while T:
                v = (T & -T).bit_length() - 1
                T &= T - 1
                s += popcount(adjB[v] & ~S) - popcount(adjM[v] & ~S)
            if s == 0:
                tight.append(S)
        per_cut_counts.append(len(tight))
        for S in tight:
            prof = [0] * 5
            for v in range(N):
                if (S >> v) & 1:
                    prof[part[v]] += 1
            profiles[tuple(prof)] += 1
    print(f"   #tight sets per maximum cut: {sorted(set(per_cut_counts))} "
          f"(total over all max cuts: {sum(per_cut_counts)})")
    if verbose:
        print("   part-profiles of tight sets (profile -> multiplicity over all max cuts):")
        for prof, cnt in sorted(profiles.items()):
            print("     ", prof, cnt)
    return cuts, per_cut_counts, profiles


def structure_check(n):
    """For the CANONICAL maximum cut  V0 = V1 u V3, V1side = V2 u V4 u V5  (M = V4 x V5),
    verify the claimed characterisation: sigma(S)=0  iff  S or its complement is
    contained in a single part of the monochromatic complete bipartite graph M."""
    N, E, part = c5n(n)
    side = [0] * N
    for v in range(N):
        p = part[v]
        side[v] = 0 if p in (0, 2) else 1          # parts 0,2 -> side 0 ; 1,3,4 -> side 1
    adjB = [0] * N
    adjM = [0] * N
    adj = masks(N, E)
    for u in range(N):
        for v in range(N):
            if (adj[u] >> v) & 1:
                if side[u] != side[v]:
                    adjB[u] |= 1 << v
                else:
                    adjM[u] |= 1 << v
    M = [(u, v) for (u, v) in E if side[u] == side[v]]
    assert len(M) == n * n, (len(M), n * n)
    bad = []
    full = (1 << N) - 1
    for S in range(1 << N):
        s = 0
        T = S
        while T:
            v = (T & -T).bit_length() - 1
            T &= T - 1
            s += popcount(adjB[v] & ~S) - popcount(adjM[v] & ~S)
        prof = [0] * 5
        for v in range(N):
            if (S >> v) & 1:
                prof[part[v]] += 1
        C = full ^ S
        profC = [n - x for x in prof]
        # predicate: S (or complement) lives inside part 3 alone or part 4 alone
        def inside_one_M_part(p):
            return (p[0] == p[1] == p[2] == 0) and (p[3] == 0 or p[4] == 0)
        pred = inside_one_M_part(prof) or inside_one_M_part(profC)
        if (s == 0) != pred:
            bad.append((S, prof, s, pred))
    print(f"   canonical cut of C5[{n}]: characterisation "
          f"{'CONFIRMED' if not bad else 'FAILS on %d sets' % len(bad)}"
          + ("" if not bad else f"   first 5 exceptions: {bad[:5]}"))
    return bad


if __name__ == "__main__":
    for n in (1, 2, 3):
        analyse(n, verbose=(n <= 2))
        structure_check(n)
        print()
