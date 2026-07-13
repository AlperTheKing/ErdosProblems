# py1_sanity.py -- exact sanity battery for the pentagon-rounding (polynomial-method) lens.
# All arithmetic exact: integers (energies scaled by 5 or 10) and Fractions.
import numpy as np, itertools, time
from fractions import Fraction

# ---------- graph builders ----------
def petersen():
    E = []
    for i in range(5):
        E.append((i, (i+1) % 5))            # outer C5
        E.append((5+i, 5+((i+2) % 5)))      # inner pentagram
        E.append((i, 5+i))                  # spokes
    return 10, sorted(set(tuple(sorted(e)) for e in E))

def grotzsch():
    # Mycielski of C5: u0..4 = 0..4, shadows v0..4 = 5..9, apex w = 10
    E = []
    for i in range(5):
        E.append((i, (i+1) % 5))
        E.append((5+i, (i+1) % 5))
        E.append((5+i, (i-1) % 5))
        E.append((10, 5+i))
    return 11, sorted(set(tuple(sorted(e)) for e in E))

def c5_blowup(m):
    # classes k*m..k*m+m-1 for k=0..4; complete between consecutive classes
    E = []
    for k in range(5):
        for a in range(m):
            for b in range(m):
                E.append((k*m+a, ((k+1) % 5)*m+b))
    return 5*m, sorted(set(tuple(sorted(e)) for e in E))

def hoffman_singleton():
    # P[h][j] = 5h+j (pentagon h: j~j+1), Q[i][j] = 25+5i+j (pentagram i: j~j+2)
    # cross: P[h][j] ~ Q[i][(h*i+j) mod 5]
    E = []
    for h in range(5):
        for j in range(5):
            E.append((5*h+j, 5*h+((j+1) % 5)))
    for i in range(5):
        for j in range(5):
            E.append((25+5*i+j, 25+5*i+((j+2) % 5)))
    for h in range(5):
        for i in range(5):
            for j in range(5):
                E.append((5*h+j, 25+5*i+((h*i+j) % 5)))
    return 50, sorted(set(tuple(sorted(e)) for e in E))

def clebsch():
    # F2^4, connection set: e1..e4 and (1,1,1,1)
    gens = [1, 2, 4, 8, 15]
    E = []
    for v in range(16):
        for g in gens:
            E.append(tuple(sorted((v, v ^ g))))
    return 16, sorted(set(E))

def triangle_count(n, E):
    A = np.zeros((n, n), dtype=np.int64)
    for u, v in E:
        A[u, v] = A[v, u] = 1
    A3 = A @ A @ A
    return int(np.trace(A3)) // 6, A

# ---------- exact beta (min uncut over all cuts) ----------
def beta_exact(n, E):
    Earr = np.array(E)
    Nc = 1 << n
    best = None
    chunk = 1 << 20
    for s in range(0, Nc, chunk):
        vs = np.arange(s, min(s+chunk, Nc), dtype=np.uint64)
        B = ((vs[:, None] >> np.arange(n, dtype=np.uint64)[None, :]) & 1).astype(np.int8)
        same = (B[:, Earr[:, 0]] == B[:, Earr[:, 1]]).sum(axis=1)
        m = int(same.min())
        best = m if best is None else min(best, m)
    return best

# ---------- pentagon kernel check (exact Fractions) ----------
def kernel_check():
    # scheme: 5 cuts S_j = {j, j+2} of Z5; q(d) = P_j[ 1_{S_j}(a) == 1_{S_j}(a+d) ]
    qs = {}
    for d in range(5):
        vals = set()
        for a in range(5):
            cnt = 0
            for j in range(5):
                Sj = {j, (j+2) % 5}
                if (a in Sj) == (((a+d) % 5) in Sj):
                    cnt += 1
            vals.add(Fraction(cnt, 5))
        assert len(vals) == 1, (d, vals)
        qs[d] = vals.pop()
    return qs  # expect {0:1, 1:1/5, 2:3/5, 3:3/5, 4:1/5}

# ---------- exact Phi (pentagon ground state, no signs), scaled x5 ----------
CT5 = np.array([5, 1, 3, 3, 1], dtype=np.int32)  # 5*q(d)

def phi_exact(n, E, fix_first=True):
    # enumerate labelings V->Z5 with vertex 0 fixed to class 0 (valid: global rotation symmetry)
    Earr = np.array(E)
    total = 5 ** (n - 1) if fix_first else 5 ** n
    nfree = n - 1 if fix_first else n
    best = None
    chunk = 1 << 19
    t0 = time.time()
    for s in range(0, total, chunk):
        ids = np.arange(s, min(s + chunk, total), dtype=np.int64)
        L = np.zeros((len(ids), n), dtype=np.int8)
        x = ids.copy()
        for v in range(nfree):
            L[:, v + (1 if fix_first else 0)] = (x % 5).astype(np.int8)
            x //= 5
        en = np.zeros(len(ids), dtype=np.int32)
        for (u, v) in Earr:
            en += CT5[(L[:, u] - L[:, v]) % 5]
        m = int(en.min())
        best = m if best is None else min(best, m)
    return best, time.time() - t0  # energy*5

def eval_labeling5(E, lab):
    return sum(int(CT5[(lab[u] - lab[v]) % 5]) for u, v in E)  # x5

if __name__ == "__main__":
    out = []
    qs = kernel_check()
    out.append(f"kernel q(d) = {dict((d, str(qs[d])) for d in range(5))}")

    # Petersen
    n, E = petersen()
    t, A = triangle_count(n, E)
    b = beta_exact(n, E)
    out.append(f"Petersen: n={n} e={len(E)} triangles={t} beta={b} bound N^2/25={n*n/25}")

    # C5 blowups m=1,2,3,4
    for m in (1, 2, 3, 4):
        n, E = c5_blowup(m)
        t, _ = triangle_count(n, E)
        b = beta_exact(n, E)
        out.append(f"C5[{m}]: n={n} e={len(E)} triangles={t} beta={b} (expect {m*m}) bound={n*n/25}")

    # Grotzsch
    n, E = grotzsch()
    t, _ = triangle_count(n, E)
    b = beta_exact(n, E)
    out.append(f"Grotzsch: n={n} e={len(E)} triangles={t} beta={b} bound={n*n/25}")

    # Hoffman-Singleton sanity + explicit pentagon labeling value
    n, E = hoffman_singleton()
    t, A = triangle_count(n, E)
    deg = A.sum(axis=1)
    lab = [0]*50
    for h in range(5):
        for j in range(5):
            lab[5*h+j] = j
    for i in range(5):
        for j in range(5):
            lab[25+5*i+j] = (2*j) % 5
    v5 = eval_labeling5(E, lab)
    out.append(f"HoSi: n={n} e={len(E)} triangles={t} degmin/max={deg.min()}/{deg.max()} pentagonLabeling Phi<= {v5}/5 = {v5/5} bound={n*n/25}")

    # Clebsch sanity
    n, E = clebsch()
    t, _ = triangle_count(n, E)
    out.append(f"Clebsch: n={n} e={len(E)} triangles={t} bound={n*n/25}")

    # exact Phi for Petersen and Grotzsch
    n, E = petersen()
    p5, dt = phi_exact(n, E)
    out.append(f"Phi(Petersen) = {p5}/5 = {p5/5}  ({dt:.1f}s)  vs bound 4")
    n, E = grotzsch()
    g5, dt = phi_exact(n, E)
    out.append(f"Phi(Grotzsch) = {g5}/5 = {g5/5}  ({dt:.1f}s)  vs bound 121/25 = 4.84")

    print("\n".join(out))
