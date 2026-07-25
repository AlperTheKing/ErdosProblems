"""AUDIT of G8 sections 1(consequence 2), 3: C5-colourability of induced subgraphs.

Own homomorphism search: CSP with bitmask domains + arc consistency, vertex order
by index (the target used degree-ordered plain backtracking).  Cross-checked on
all subsets of And(3) against brute force over all 5^|W| colourings.

Own isomorphism test against the Wagner graph C8(1,4) by backtracking
(the target used networkx.is_isomorphic).
"""
import sys, itertools
from audit_G8_core import and_circulant, edges_of

C5 = [((1 << ((i + 1) % 5)) | (1 << ((i + 4) % 5))) for i in range(5)]   # nbr masks


def hom_to_C5(verts, adjm_sub):
    """CSP: does the graph (verts, adjacency restricted) admit a hom to C5?"""
    verts = list(verts)
    dom = {v: 0b11111 for v in verts}
    nbr = {v: [u for u in verts if (adjm_sub[v] >> u) & 1] for v in verts}

    def propagate(dom):
        changed = True
        while changed:
            changed = False
            for v in verts:
                if dom[v] == 0:
                    return False
                for u in nbr[v]:
                    allowed = 0
                    d = dom[v]
                    while d:
                        b = d & -d
                        c = b.bit_length() - 1
                        d ^= b
                        allowed |= C5[c]
                    nd = dom[u] & allowed
                    if nd != dom[u]:
                        dom[u] = nd
                        changed = True
                        if nd == 0:
                            return False
        return True

    def rec(dom, i):
        if not propagate(dom):
            return False
        while i < len(verts) and bin(dom[verts[i]]).count("1") == 1:
            i += 1
        if i == len(verts):
            return True
        v = verts[i]
        d = dom[v]
        while d:
            b = d & -d
            d ^= b
            nd = dict(dom)
            nd[v] = b
            if rec(nd, i + 1):
                return True
        return False

    return rec(dom, 0)


def hom_bruteforce(verts, adjm_sub):
    verts = list(verts)
    E = [(u, v) for u in verts for v in verts if u < v and (adjm_sub[u] >> v) & 1]
    for col in itertools.product(range(5), repeat=len(verts)):
        f = dict(zip(verts, col))
        if all((C5[f[u]] >> f[v]) & 1 for (u, v) in E):
            return True
    return False


WAG_E = [(i, (i + 1) % 8) for i in range(8)] + [(i, i + 4) for i in range(4)]
WAGadj = [0] * 8
for (u, v) in WAG_E:
    WAGadj[u] |= 1 << v
    WAGadj[v] |= 1 << u


def iso_to_wagner(S, adjm):
    """backtracking isomorphism test: induced subgraph on S (8 verts) == Wagner?"""
    S = list(S)
    if len(S) != 8:
        return False
    ind = {v: i for i, v in enumerate(S)}
    A = [0] * 8
    for i, v in enumerate(S):
        for j, u in enumerate(S):
            if (adjm[v] >> u) & 1:
                A[i] |= 1 << j
    if sorted(bin(a).count("1") for a in A) != [3] * 8:
        return False
    perm = [-1] * 8
    used = [False] * 8

    def rec(i):
        if i == 8:
            return True
        for c in range(8):
            if used[c]:
                continue
            ok = True
            for j in range(i):
                if ((A[i] >> j) & 1) != ((WAGadj[c] >> perm[j]) & 1):
                    ok = False
                    break
            if ok:
                perm[i] = c
                used[c] = True
                if rec(i + 1):
                    return True
                used[c] = False
                perm[i] = -1
        return False

    return rec(0)


if __name__ == "__main__":
    # ---- section 3: proper induced subgraphs of And(3)
    n, adjm = and_circulant(3)
    print("And(3): induced subgraphs with NO hom to C5 (own CSP), cross-checked vs brute force")
    counts = {}
    mismatch = 0
    for mask in range(1 << n):
        W = [v for v in range(n) if (mask >> v) & 1]
        sub = [adjm[v] & mask for v in range(n)]
        h = hom_to_C5(W, sub) if W else True
        if len(W) <= 8:
            hb = hom_bruteforce(W, sub) if W else True
            if h != hb:
                mismatch += 1
                print("   CSP/BRUTE MISMATCH", W)
        if not h:
            counts.setdefault(len(W), []).append(tuple(W))
    print(f"   CSP-vs-bruteforce mismatches over all 256 subsets: {mismatch}")
    for s in sorted(counts):
        print(f"   |W|={s}: {len(counts[s])} obstructions  e.g. {counts[s][0]}")
    if not counts:
        print("   NONE (would contradict odd girth 5)")
    print()

    # ---- section 3 / obstr2: And(k)[W] -> C5  <=>  W contains no induced Wagner
    for k in (3, 4, 5):
        n, adjm = and_circulant(k)
        wag = [set(S) for S in itertools.combinations(range(n), 8) if iso_to_wagner(S, adjm)]
        bad = nohom = 0
        for mask in range(1 << n):
            W = [v for v in range(n) if (mask >> v) & 1]
            Ws = set(W)
            sub = [adjm[v] & mask for v in range(n)]
            h = hom_to_C5(W, sub) if W else True
            contains = any(A <= Ws for A in wag)
            if not h:
                nohom += 1
            if (not h) != contains:
                bad += 1
        print(f"And({k}) n={n}: induced Wagner copies = {len(wag)}; "
              f"subsets with no hom to C5 = {nohom}/{1<<n}; "
              f"mismatches with 'contains induced Wagner' = {bad}")
        sys.stdout.flush()
