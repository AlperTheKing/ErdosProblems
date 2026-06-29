"""Stress gate for the remaining B* obstruction.

Build path+detour+bad-edge chord layouts.  For each parity cut, find
unique-row interval-Hall failures.  If a failing row has no shared-endpoint
P-contained bracket vertex, test whether some path interval flip strictly
increases cutsize.  Such a failure cannot occur in a global maximum cut.

This is not a proof; it isolates the exact max-cut pressure needed for B*.
"""

from itertools import combinations
from fractions import Fraction as F

from _h import Bconn
from _satzmu_conn import struct_for_side


def build(pend, chords):
    edges = [(i, i + 1) for i in range(pend)]
    nint = pend + 1
    ext = list(range(pend + 1, pend + 1 + nint))
    det = [0] + ext + [pend]
    for a, b in zip(det, det[1:]):
        edges.append((min(a, b), max(a, b)))
    for a, b in chords:
        edges.append((min(a, b), max(a, b)))
    edges.append((0, pend))
    n = pend + 1 + nint
    edges = sorted(set((min(a, b), max(a, b)) for a, b in edges))
    adj = [set() for _ in range(n)]
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    return n, adj


def tri_free(n, adj):
    for u in range(n):
        for v in adj[u]:
            if v > u and (adj[u] & adj[v]):
                return False
    return True


def cutsize(n, adj, side):
    return sum(1 for u in range(n) for v in adj[u] if v > u and side[u] != side[v])


def path_interval_gain(n, adj, side, pend):
    base = cutsize(n, adj, side)
    best = (0, None)
    for a in range(pend + 1):
        for b in range(a, pend + 1):
            side2 = side[:]
            for v in range(a, b + 1):
                side2[v] ^= 1
            gain = cutsize(n, adj, side2) - base
            if gain > best[0]:
                best = (gain, (a, b))
    return best


def interval_failures(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None:
        return []
    M, _elld, _T, _mu, cyc = st
    S = [F(0)] * n
    for g in M:
        denom = len(cyc[g])
        for path in cyc[g]:
            for v in path:
                S[v] += F(1, denom)

    failures = []
    for f in M:
        if len(cyc[f]) != 1:
            continue
        P = cyc[f][0]
        L = len(P)
        pos = {x: i for i, x in enumerate(P)}
        Pset = set(P)
        demand_vec = [S[v] - 1 for v in P]

        pcontained = set()
        for g in M:
            if g == f:
                continue
            for Q in cyc[g]:
                if set(Q) <= Pset:
                    pcontained.add((min(g), max(g)))
                    break

        rest = [v for v in range(n) if v not in Pset]
        parent = {v: v for v in rest}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        for u in rest:
            for w in adj[u]:
                if w not in Pset and side[u] != side[w]:
                    parent[find(u)] = find(w)

        comps = {}
        for v in rest:
            comps.setdefault(find(v), set()).add(v)
        spans = []
        for comp in comps.values():
            attaches = set(pos[x] for u in comp for x in adj[u] if x in Pset and side[u] != side[x])
            if attaches:
                spans.append((min(attaches), max(attaches), len(comp)))

        for a in range(L):
            for b in range(a, L):
                demand = sum(demand_vec[i] for i in range(a, b + 1))
                cap = sum(c for lo, hi, c in spans if not (hi < a or lo > b))
                if demand <= cap:
                    continue

                bracket = False
                for i, x in enumerate(P):
                    inc = []
                    for w in adj[x]:
                        e = (min(x, w), max(x, w))
                        if side[w] == side[x] and w in pos and e in pcontained:
                            inc.append(w)
                    if any(pos[w] < i for w in inc) and any(pos[w] > i for w in inc):
                        bracket = True
                        break
                failures.append((f, (a, b), demand, cap, bracket))
    return failures


def chord_candidates(pend):
    cands = []
    for a in range(pend + 1):
        for b in range(a + 4, pend + 1, 2):
            cands.append((a, b))
    return cands


def run():
    total = 0
    no_bracket = 0
    no_gain = 0
    first = None

    manual = [
        ("chain-c4-k3", 12, [(0, 4), (4, 8), (8, 12)]),
        ("nested-c4", 12, [(0, 8), (2, 6)]),
        ("nested2", 16, [(0, 12), (2, 10), (4, 8)]),
        ("overlap-noshare", 12, [(0, 6), (4, 10)]),
        ("chain-c6", 18, [(0, 6), (6, 12), (12, 18)]),
    ]

    generated = []
    for pend in (8, 10, 12):
        cands = chord_candidates(pend)
        for k in (1, 2, 3):
            for chords in combinations(cands, k):
                generated.append((f"gen-p{pend}-k{k}", pend, list(chords)))

    for name, pend, chords in manual + generated:
        n, adj = build(pend, chords)
        if not tri_free(n, adj):
            continue
        side = [v % 2 for v in range(n)]
        if not Bconn(n, adj, side):
            continue
        fails = interval_failures(n, adj, side)
        if not fails:
            continue
        gain, interval = path_interval_gain(n, adj, side, pend)
        for f, I, demand, cap, bracket in fails:
            total += 1
            if bracket:
                continue
            no_bracket += 1
            if gain <= 0:
                no_gain += 1
                if first is None:
                    first = (name, pend, chords, f, I, demand, cap)
            if name.startswith("nested") or name.startswith("overlap"):
                print(
                    f"  {name} chords={chords} f={f} I={I} bracket={bracket} "
                    f"path_gain={gain} interval={interval}",
                    flush=True,
                )

    print("=== NONJUNCTION PREFIX-GAIN gate ===", flush=True)
    print(f"  interval-Hall failures = {total}", flush=True)
    print(f"  failures without bracket hub = {no_bracket}", flush=True)
    print(f"  no-bracket failures without path-interval cut gain = {no_gain}", flush=True)
    print(f"  first obstruction = {first}", flush=True)


if __name__ == "__main__":
    run()
