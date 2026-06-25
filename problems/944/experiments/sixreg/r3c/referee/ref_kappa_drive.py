# Driver: feeds an instance JSON to ref_kappa.exe; also brute-force checks
# kappa(X) >= 8 for all small/large X directly, and validates the flow
# reduction itself on random small graphs (brute force vs flow).
import json, subprocess, sys, random, itertools

def emit(path):
    d = json.load(open(path)); inst = d['inst']; n = inst['n']
    E = sorted({(min(int(a),int(b)), max(int(a),int(b))) for a, b in inst['edges']})
    deg = [0]*n
    for a, b in E: deg[a] += 1; deg[b] += 1
    stubs = [(v, 6 - deg[v]) for v in range(n) if deg[v] < 6]
    lines = [f"{n} {len(E)}"] + [f"{a} {b}" for a, b in E] + [str(len(stubs))] + [f"{v} {b}" for v, b in stubs]
    return "\n".join(lines) + "\n", n, E, deg

def kappa_of(X, E, deg, n):
    Xs = set(X)
    e_in = sum(1 for a, b in E if a in Xs and b in Xs)
    return 6*len(X) - 2*e_in

def brute_small(n, E, deg, kmax=4):
    """check kappa >= 8 for all X with |X|<=kmax or |X^c|<=kmax (2<=|X|<=n-2)"""
    worst = 10**9; warg = None
    for k in range(2, kmax+1):
        for X in itertools.combinations(range(n), k):
            v = kappa_of(X, E, deg, n)
            if v < worst: worst, warg = v, ('X', X)
            # complement
            Xc = [u for u in range(n) if u not in set(X)]
            v2 = kappa_of(Xc, E, deg, n)
            if v2 < worst: worst, warg = v2, ('Xc-of', X)
    return worst, warg

def random_mid(n, E, deg, trials=200000, seed=7):
    rng = random.Random(seed)
    worst = 10**9; warg = None
    for _ in range(trials):
        k = rng.randint(5, n-5)
        X = rng.sample(range(n), k)
        v = kappa_of(X, E, deg, n)
        if v < worst: worst, warg = v, sorted(X)
    return worst, warg

def reduction_crosscheck(exe, ntests=40, seed=11):
    """Random small graphs with Delta<=6: brute-force min kappa over X where
    both sides span an edge, vs the flow program's answer (capped at 8 -> compare min(bf,8))."""
    rng = random.Random(seed)
    bad = []
    for t in range(ntests):
        n = rng.randint(8, 13)
        E = set()
        # random graph, max degree 6
        deg = [0]*n
        attempts = rng.randint(int(1.2*n), 3*n)
        for _ in range(attempts):
            a, b = rng.sample(range(n), 2)
            key = (min(a,b), max(a,b))
            if key in E or deg[a] >= 6 or deg[b] >= 6: continue
            E.add(key); deg[a] += 1; deg[b] += 1
        E = sorted(E)
        if len(E) < 4: continue
        # connectivity not required for the flow identity; keep as is
        stubs = [(v, 6 - deg[v]) for v in range(n) if deg[v] < 6]
        # brute force over all X, 2<=|X|<=n-2, X and Xc both spanning an edge
        bf = 10**9
        for mask in range(1, 1 << n):
            X = [v for v in range(n) if mask >> v & 1]
            if not (2 <= len(X) <= n - 2): continue
            Xs = set(X)
            if not any(a in Xs and b in Xs for a, b in E): continue
            if not any(a not in Xs and b not in Xs for a, b in E): continue
            e_in = sum(1 for a, b in E if a in Xs and b in Xs)
            stub_in = sum(b for v, b in stubs if v in Xs)
            # kappa = 6|X| - 2 e(X). Note: with general deficiency this still
            # equals e(X,Xc) + stub_in  (degrees sum identity); use definition:
            kap = 6*len(X) - 2*e_in
            assert kap == sum(1 for a, b in E if (a in Xs) != (b in Xs)) + stub_in
            bf = min(bf, kap)
        inp = [f"{n} {len(E)}"] + [f"{a} {b}" for a, b in E] + [str(len(stubs))] + [f"{v} {b}" for v, b in stubs]
        out = subprocess.run([exe], input="\n".join(inp) + "\n", capture_output=True, text=True).stdout
        flow = int(out.split("minflow(cap8)=")[1].split()[0])
        if min(bf, 8) != min(flow, 8):
            bad.append((t, n, E, bf, flow))
    return bad

if __name__ == '__main__':
    exe = sys.argv[1]
    if sys.argv[2] == 'crosscheck':
        bad = reduction_crosscheck(exe)
        print("reduction crosscheck mismatches:", bad if bad else "NONE (40 random graphs)")
    else:
        path = sys.argv[2]
        inp, n, E, deg = emit(path)
        ws, wa = brute_small(n, E, deg, kmax=4 if n < 100 else 3)
        print(f"{path}: brute small/large |X| min kappa = {ws} at {wa}")
        wm, _ = random_mid(n, E, deg, trials=100000 if n < 100 else 30000)
        print(f"{path}: random mid-size sample min kappa = {wm}")
        r = subprocess.run([exe], input=inp, capture_output=True, text=True)
        print(f"{path}: flow exact -> {r.stdout.strip()}")
