"""Independent exact maxcut certification for larger N via OR-Tools CP-SAT (proven optimality).
Used where pure-Python 2^(N-1) enumeration is too slow. Own decoder, own model."""
import sys
from ortools.sat.python import cp_model
from itertools import combinations

def decode(s):
    n = ord(s[0]) - 63
    bits = []
    for ch in s[1:]:
        v = ord(ch) - 63
        bits.extend((v >> k) & 1 for k in (5,4,3,2,1,0))
    E = []; p = 0
    for j in range(1, n):
        for i in range(j):
            if p < len(bits) and bits[p]: E.append((i, j))
            p += 1
    return n, E

for s in sys.argv[1:]:
    n, E = decode(s)
    adjs = {}
    for u,v in E: adjs.setdefault(u,set()).add(v); adjs.setdefault(v,set()).add(u)
    tf = all(not (adjs.get(a,set()) & adjs.get(b,set())) for a,b in E)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(n)]
    m.Add(x[0] == 0)
    cut = []
    for (u,v) in E:
        y = m.NewBoolVar("")
        m.Add(y <= x[u] + x[v]); m.Add(y <= 2 - x[u] - x[v])
        m.Add(y >= x[u] - x[v]); m.Add(y >= x[v] - x[u])
        cut.append(y)
    m.Maximize(sum(cut))
    sol = cp_model.CpSolver(); sol.parameters.num_search_workers = 16
    st = sol.Solve(m)
    assert st == cp_model.OPTIMAL, sol.StatusName(st)
    mc = int(sol.ObjectiveValue()); bip = len(E) - mc
    flag = "*** VIOLATION ***" if 25*bip > n*n else "consistent"
    print(f"{s} n={n} m={len(E)} maxcut={mc}(CP-SAT proven optimal) bip={bip} trianglefree={tf} 25bip={25*bip} N^2={n*n} {flag}")
