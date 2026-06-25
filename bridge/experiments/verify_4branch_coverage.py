#!/usr/bin/env python3
"""
4-BRANCH COVERAGE TEST (Q11 section 7) — honest computational probe.

The 4-branch dichotomy claims CF (tau_K <= (N^2/5 - e)/2 = RHS) follows if EVERY band
triangle-free graph satisfies >=1 of four rooted certificates:
  (1) EDGE-root :  tau_K <= e - (S_u+S_v)/2          [cheap, computed exactly here]
  (2) C5-root   :  tau_K <= F_C                       [cheap, 10-map min, from verify_FC_c5root]
  (3) Petersen-root, (4) Clebsch-root : tau_K <= (3/4) e_inc(B)   [structured, see note]

What this script tests (no fabrication):
  (a) DIRECT CF: tau_K_ub (local search, an UPPER bound on the true tau_K) <= RHS, on every
      band graph. This is the actual conjecture CF; 0 violations = direct evidence CF true.
  (b) CHEAP COVERAGE: does edge-root OR C5-root already give a bound <= RHS? If yes on the
      generic random band graphs, the two cheap templates suffice there.
  (c) MOTIVATION for the 2 extra templates: confirm edge-root AND C5-root BOTH FAIL (bound > RHS)
      on Petersen[t] and Clebsch[t] blowups, even though tau_K = 0 there (so the Petersen/Clebsch
      roots are genuinely needed). The Petersen/Clebsch-root bound (3/4)e_inc(B)=0 on their own
      blowups is witnessed here by tau_K_ub=0 (local search), NOT by reimplementing induced
      10/16-vertex detection (that is the research-grade part, left to the flag-SDP endgame).

Caps: pure single-thread Python, tiny graphs (N<=32). Well under 64 threads / 192 GB.
"""
import itertools, random
random.seed(23)

# ---- Clebsch graph K (16 even subsets of [5], a~b iff |a xor b|=4) ----
labels = [m for m in range(32) if bin(m).count('1') % 2 == 0]
Kadj = [set() for _ in range(16)]
for i in range(16):
    for j in range(16):
        if i != j and bin(labels[i] ^ labels[j]).count('1') == 4:
            Kadj[i].add(j)

def cost(x, y):
    return (4 - bin(x ^ y).count('1')) // 2  # in {0,1,2}

def adj_list(N, E):
    A = [set() for _ in range(N)]
    for u, v in E:
        A[u].add(v); A[v].add(u)
    return A

# ---- tau_K upper bound via labeled local search (same engine as verify_q11_cf_audit) ----
def tau_K_ub(N, A, restarts=60, sweeps=40):
    nbr = [list(A[v]) for v in range(N)]
    best = None
    for _ in range(restarts):
        lab = [random.choice(labels) for _ in range(N)]
        imp, sw = True, 0
        while imp and sw < sweeps:
            imp = False; sw += 1
            for u in range(N):
                bc, bl = None, lab[u]
                for L in labels:
                    c = sum(cost(L, lab[w]) for w in nbr[u])
                    if bc is None or c < bc:
                        bc, bl = c, L
                if bl != lab[u]:
                    lab[u] = bl; imp = True
        tot = sum(cost(lab[u], lab[w]) for u in range(N) for w in nbr[u] if w > u)
        if best is None or tot < best:
            best = tot
    return best

# ---- EDGE-root certificate: tau_K <= e - (S_u+S_v)/2 ; best = e - max_{uv in E}(S_u+S_v)/2 ----
def edge_root_bound(N, A, E):
    deg = [len(A[v]) for v in range(N)]
    S = [sum(deg[z] for z in A[v]) for v in range(N)]   # S_v = sum of neighbor degrees
    e = sum(deg) // 2
    if not E:
        return e, 0
    best_pair = max(S[u] + S[v] for u, v in E)
    return e - best_pair / 2.0, best_pair

# ---- C5-root F_C: min over induced C5 of min over 10 maps phi_{eps,j} (from verify_FC_c5root) ----
def label_R(j):      return 31 ^ (1 << j)
def label_S(i, eps): return (1 << i) | (1 << ((i + eps) % 5))
def label_D(i):      return (1 << ((i - 1) % 5)) | (1 << ((i + 1) % 5))

def FC_of_cycle(N, A, E, C):
    typ = [None] * N
    for v in range(N):
        P = sorted(i for i in range(5) if C[i] in A[v])
        if len(P) == 0:    typ[v] = ('R',)
        elif len(P) == 1:  typ[v] = ('S', P[0])
        elif len(P) == 2:
            a, b = P
            if   (b - a) % 5 == 2: typ[v] = ('D', (a + 1) % 5)
            elif (a - b) % 5 == 2: typ[v] = ('D', (b + 1) % 5)
            else:                  typ[v] = ('X',)
        else:              typ[v] = ('X',)
    best = None
    for eps in (2, 3):
        for j in range(5):
            lab = [0] * N
            for v in range(N):
                t = typ[v]
                if   t[0] == 'R': lab[v] = label_R(j)
                elif t[0] == 'S': lab[v] = label_S(t[1], eps)
                elif t[0] == 'D': lab[v] = label_D(t[1])
                else:             lab[v] = label_R(j)
            tot = sum(cost(lab[u], lab[w]) for (u, w) in E)
            if best is None or tot < best:
                best = tot
    return best

def min_FC(N, A, E):
    best = None
    for combo in itertools.combinations(range(N), 5):
        sub = [(a, b) for a, b in itertools.combinations(combo, 2) if b in A[a]]
        if len(sub) != 5:
            continue
        d = {v: 0 for v in combo}
        for a, b in sub:
            d[a] += 1; d[b] += 1
        if any(d[v] != 2 for v in combo):
            continue
        start = combo[0]; cyc = [start]; prev = None; cur = start
        ok = True
        for _ in range(4):
            cand = [w for w in A[cur] if w in d and w != prev]
            if not cand:
                ok = False; break
            nxt = cand[0]; cyc.append(nxt); prev, cur = cur, nxt
        if not ok:
            continue
        fc = FC_of_cycle(N, A, E, tuple(cyc))
        if best is None or fc < best:
            best = fc
    return best

# ---- graph families ----
def c5_blowup(n):
    parts = [list(range(i*n, i*n+n)) for i in range(5)]
    E = [(u, v) for p in range(5) for u in parts[p] for v in parts[(p+1) % 5]]
    return 5*n, E

def clebsch_blowup(t):
    base = [(i, j) for i in range(16) for j in range(i+1, 16) if j in Kadj[i]]
    E = [(a*t+x, b*t+y) for (a, b) in base for x in range(t) for y in range(t)]
    return 16*t, E

def petersen_blowup(t):
    two = list(itertools.combinations(range(5), 2))         # 10 vertices
    base = [(i, j) for i in range(10) for j in range(i+1, 10)
            if not (set(two[i]) & set(two[j]))]              # adjacency = disjointness
    E = [(a*t+x, b*t+y) for (a, b) in base for x in range(t) for y in range(t)]
    return 10*t, E

def rand_band(N, elo, ehi):
    for _ in range(300):
        A = [set() for _ in range(N)]
        pairs = [(u, v) for u in range(N) for v in range(u+1, N)]
        random.shuffle(pairs); e = 0; E = []
        tgt = random.randint(elo, ehi)
        for u, v in pairs:
            if e >= tgt:
                break
            if A[u] & A[v]:
                continue
            A[u].add(v); A[v].add(u); E.append((u, v)); e += 1
        if elo <= e <= ehi:
            return N, E
    return None

# ---- report ----
def dedup(E):
    return sorted({(min(u, v), max(u, v)) for u, v in E})

def report(tag, N, E):
    E = dedup(E)
    A = adj_list(N, E)
    e = len(E)
    rhs = (N*N/5.0 - e) / 2.0
    tk = tau_K_ub(N, A)
    er, _ = edge_root_bound(N, A, E)
    fc = min_FC(N, A, E)
    cf_ok = (tk <= rhs + 1e-9)
    er_ok = (er <= rhs + 1e-9)
    fc_ok = (fc is not None) and (fc <= rhs + 1e-9)
    cheap_ok = er_ok or fc_ok
    fcs = "n/a" if fc is None else f"{fc}"
    print(f"  {tag:14s} N={N:3d} e={e:4d} x={e/(N*N):.4f} RHS={rhs:7.1f} | "
          f"tauK_ub={tk:4d} CF_ok={int(cf_ok)} | edge={er:7.1f}({int(er_ok)}) "
          f"C5_FC={fcs:>4}({int(fc_ok)}) cheapOK={int(cheap_ok)}")
    return dict(tag=tag, N=N, e=e, rhs=rhs, tk=tk, cf_ok=cf_ok,
                er_ok=er_ok, fc_ok=fc_ok, cheap_ok=cheap_ok)

def main():
    print("=== 4-BRANCH COVERAGE TEST (Q11 sec 7) ===")
    print("CF_ok = tau_K_ub<=RHS (direct conjecture). cheapOK = edge-root OR C5-root covers it.")
    print("Band density window x in [0.2486, 0.3197].\n")
    rows = []
    print("-- extremal / structured templates --")
    for n in (2, 3, 4):
        rows.append(report(f"C5[{n}]", *c5_blowup(n)))
    for t in (1, 2):
        rows.append(report(f"Petersen[{t}]", *petersen_blowup(t)))
    for t in (1, 2):
        rows.append(report(f"Clebsch[{t}]", *clebsch_blowup(t)))
    print("\n-- random band graphs --")
    for N in (15, 18, 20, 22):
        C2 = N*(N-1)/2.0
        lo, hi = int(0.2486*C2) + 1, int(0.3197*C2)
        for _ in range(6):
            r = rand_band(N, lo, hi)
            if r:
                rows.append(report(f"rand{N}", r[0], r[1]))

    print("\n=== SUMMARY ===")
    cf_viol = [r for r in rows if not r['cf_ok']]
    print(f"CF (tau_K_ub<=RHS) violations: {len(cf_viol)} / {len(rows)}"
          + ("" if not cf_viol else "  <-- INVESTIGATE: " + ", ".join(r['tag'] for r in cf_viol)))
    rand = [r for r in rows if r['tag'].startswith('rand')]
    rand_cheapfail = [r for r in rand if not r['cheap_ok']]
    print(f"Random band: cheap (edge OR C5) coverage = {len(rand)-len(rand_cheapfail)}/{len(rand)}"
          + ("" if not rand_cheapfail else "  cheap-FAILS: " + ", ".join(r['tag'] for r in rand_cheapfail)))
    struct = [r for r in rows if r['tag'].startswith(('Petersen', 'Clebsch'))]
    motiv = [r for r in struct if not r['cheap_ok'] and r['tk'] == 0]
    print(f"Petersen/Clebsch motivating cases (cheap FAILS but tau_K=0, so extra root needed): "
          f"{len(motiv)}/{len(struct)}")
    print("\nINTERPRETATION:")
    print("  * CF violations 0  -> direct evidence CF holds on all sampled band graphs.")
    print("  * random cheap coverage high -> edge+C5 templates suffice generically.")
    print("  * Petersen/Clebsch cheap-fail+tauK=0 -> the 2 extra root templates are genuinely needed.")
    print("  * A flag-SDP coverage PROOF (band+tri-free => >=1 branch) remains UNPROVEN (research-grade).")
    print("DONE")

if __name__ == "__main__":
    main()
