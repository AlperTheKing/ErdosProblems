import numpy as np, math
from _h import dec, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup

def build_GH_float(n, M, ell, T, cyc):
    GH = np.zeros((n, n))
    for v in range(n):
        GH[v][v] = float(n) - float(T[v])
    for f in M:
        Qs = cyc[f]; L = ell[f]; w = 1.0 / len(Qs)
        beta = L/(2+2*math.cos(math.pi/L))
        for Q in Qs:
            Ql = list(Q)
            for i in range(L):
                a = Ql[i]; b = Ql[(i+1)%L]
                GH[a][a]+=w*beta; GH[b][b]+=w*beta; GH[a][b]-=w*beta; GH[b][a]-=w*beta
    return GH

n, E = odd_blowup(5, [2,2,2,2,2])
adj, cuts = gmins(n, E)
st = struct_for_side(n, adj, cuts[0])
M, ell, T, mu, cyc = st
GH = build_GH_float(n, M, ell, T, cyc)
print("T =", [float(t) for t in T], "N =", n)
print("N-T =", [n-float(t) for t in T])
ones = np.ones(n)
print("GH @ 1 =", np.round(GH@ones,6))
ev, evec = np.linalg.eigh(GH)
v0 = evec[:,0]
print("kernel vec (raw) =", np.round(v0,4))
print("GH @ v0 =", np.round(GH@v0,8), " eig0=", ev[0])
print("is v0 constant?", np.allclose(v0, v0[0]))
print("sum(N-T) =", sum(n-float(t) for t in T), " = N^2-Gamma =", n*n - sum(float(t) for t in T))
