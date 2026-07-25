"""ROOT-AGENT GATE: the sharp star lemma — PROVED, then verified exhaustively.

Round-1 family F2 claimed, at a maximum cut of a triangle-free graph, for every vertex v:

        sum over a in N_B(v) of  max(2 - sigma(a), 0)   <=   sigma(v),                     (SHARP)

and called it strictly stronger than the star inequality of the accepted base,
        sum over a in N_B(v) of sigma(a)  >=  2 d_B(v) - sigma(v).                          (BASE)
No verifier agent ever ran on it. Here it is proved outright, and then checked exhaustively.

PROOF. Write sigma(S) = |boundary_B S| - |boundary_M S| for S subset V. Counting degrees over S,
    sum_{u in S} d_B(u) = |boundary_B S| + 2 e_B(S),   likewise for M,
so    sigma(S) = sum_{u in S} sigma(u) - 2 e_B(S) + 2 e_M(S).
Fix v and any T subset N_B(v). Triangle-freeness makes N_B(v) independent, so T carries no edges at
all; every edge inside S = {v} u T therefore joins v to a member of T, and each such edge is a
crossing edge by definition of N_B(v). Hence e_B(S) = |T| and e_M(S) = 0, giving

        sigma({v} u T) = sigma(v) + sum_{a in T} sigma(a) - 2|T|.

At a maximum cut sigma(S) >= 0 for every S (switching S cannot decrease the monochromatic count),
so for EVERY T subset N_B(v):

        sigma(v)  >=  sum_{a in T} (2 - sigma(a)).                                     (GENERAL)

Choosing T = {a in N_B(v) : sigma(a) < 2} maximises the right-hand side and yields (SHARP). []

(BASE) is the special case T = N_B(v), so (SHARP) implies it and is strictly stronger whenever some
neighbour has sigma(a) > 2. Both are verified below over ALL maximum cuts, not just one.
"""

import subprocess

GENG = r"E:\Projects\ErdosProblems\tools\nauty2_8_9\geng.exe"


def g6_decode(s):
    b = [ord(c) - 63 for c in s]
    n = b[0]
    bits = []
    for byte in b[1:]:
        for k in range(5, -1, -1):
            bits.append((byte >> k) & 1)
    adj = [0] * n
    idx = 0
    m = 0
    for j in range(1, n):
        for i in range(j):
            if bits[idx]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
                m += 1
            idx += 1
    return n, adj, m


def all_max_cuts(n, adj, m):
    """returns (maxcut, [list of cut bitmasks attaining it]) over all 2^(n-1) cuts"""
    deg = [bin(a).count("1") for a in adj]
    best = -1
    winners = []
    for mask in range(1 << (n - 1)):
        S = (mask << 1) | 1
        c = 0
        for u in range(n):
            if (S >> u) & 1:
                c += bin(adj[u] & ~S & ((1 << n) - 1)).count("1")
        if c > best:
            best, winners = c, [S]
        elif c == best:
            winners.append(S)
    return best, winners


def check_graph(n, adj, m):
    """returns (sharp_ok, base_ok, sharp_tight_count, strictly_stronger_count)"""
    _, cuts = all_max_cuts(n, adj, m)
    sharp_ok = base_ok = True
    tight = 0
    stronger = 0
    FULL = (1 << n) - 1
    for S in cuts:
        sigma = [0] * n
        NB = [0] * n
        for v in range(n):
            same = adj[v] & (S if (S >> v) & 1 else ~S & FULL)
            cross = adj[v] & ((~S & FULL) if (S >> v) & 1 else S)
            sigma[v] = bin(cross).count("1") - bin(same).count("1")
            NB[v] = cross
        for v in range(n):
            nb = [a for a in range(n) if (NB[v] >> a) & 1]
            lhs_sharp = sum(max(2 - sigma[a], 0) for a in nb)
            if lhs_sharp > sigma[v]:
                sharp_ok = False
            if lhs_sharp == sigma[v]:
                tight += 1
            # base form
            if sum(sigma[a] for a in nb) < 2 * len(nb) - sigma[v]:
                base_ok = False
            if any(sigma[a] > 2 for a in nb):
                stronger += 1
    return sharp_ok, base_ok, tight, stronger


print("=" * 74)
print("exhaustive check of (SHARP) and (BASE) over ALL maximum cuts")
print("=" * 74)
grand_sharp = grand_base = True
for n in range(4, 11):
    out = subprocess.run([GENG, "-t", "-c", "-q", str(n)], capture_output=True, text=True).stdout
    graphs = [ln for ln in out.split() if ln]
    bad_sharp = bad_base = 0
    tight_tot = stronger_tot = 0
    for ln in graphs:
        nn, adj, m = g6_decode(ln)
        s_ok, b_ok, tight, stronger = check_graph(nn, adj, m)
        if not s_ok:
            bad_sharp += 1
            print(f"   *** SHARP FAILS on {ln}")
        if not b_ok:
            bad_base += 1
            print(f"   *** BASE FAILS on {ln}")
        tight_tot += tight
        stronger_tot += stronger
    grand_sharp &= (bad_sharp == 0)
    grand_base &= (bad_base == 0)
    print(f"   n={n:2d}: {len(graphs):6d} connected triangle-free graphs   "
          f"SHARP failures {bad_sharp}   BASE failures {bad_base}   "
          f"tight instances {tight_tot}   instances where SHARP is strictly stronger {stronger_tot}")

print()
print(f"   (SHARP) holds everywhere: {grand_sharp}")
print(f"   (BASE)  holds everywhere: {grand_base}")
print("   Both are proved above; this is an independent exhaustive confirmation over every")
print("   maximum cut of every connected triangle-free graph with at most 10 vertices.")
