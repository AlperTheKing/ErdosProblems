"""Verify GPT-Pro's TRUNCATED resource decomposition equals Tail_k = sum_{r>=k}(2r+1)Z_r.
   Claimed:  Tail_k = L*(N^2-k^2-Gamma_k) + 25*(L*(N-k)-A_k(P)) - phi_k(L)*delta_P - E_k(P),
     phi_k(t)=max(t^2-k^2,0); Gamma_k=sum_{g in M} phi_k(L_g);
     A_k(P)=sum_{g in M} a_g(P)*max(L_g-k,0);
     E_k(P)=sum_{r>=k}(2r+1)*chi_P(r) = DG_k(x0)+DG_k(x_{L-1});
     delta_P=(S/L)^2-q.
   If this matches Tail_k for every k on every row, GPT's resource identification (the proof's premise) is exact.
"""
import subprocess
from fractions import Fraction as F
from _dgamma_formula import bfs_H, Dport
from _wf_deficit_farkas import deltas, flip, gamma_of, odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint
INF = 10**9

def chi_profile(n, adj, side, v, M, Nl):
    s2 = flip(side, [v])
    if not Bconn(n, adj, s2): return [0]*Nl
    dB, dM = deltas(n, adj, side, {v})
    if dB != dM: return [0]*Nl
    if gamma_of(n, adj, s2) is None: return [0]*Nl
    A = [w for w in adj[v] if side[w] != side[v]]
    C = [w for w in adj[v] if side[w] == side[v]]
    need = set(A) | set(C)
    for e in M: need.add(e[0]); need.add(e[1])
    distfrom = {s: bfs_H(n, adj, side, v, s) for s in need}
    chi = [0]*Nl
    def add(t, sgn):
        for r in range(min(t, Nl)): chi[r] += sgn
    for (x, y) in M:
        if x == v or y == v: continue
        DC = Dport(x, y, distfrom, C); DA = Dport(x, y, distfrom, A)
        if DC >= INF or DA >= INF: return [0]*Nl
        add(DC+1, +1); add(DA+1, -1)
    for a in A:
        mn = min((distfrom[c][a] for c in C), default=INF)
        if mn >= INF: return [0]*Nl
        add(2+mn, +1)
    for c in C:
        mn = min((distfrom[a][c] for a in A), default=INF)
        if mn >= INF: return [0]*Nl
        add(2+mn, -1)
    return chi

def verify_row(n, adj, side, M, ell, T, cyc, f, P):
    L = ell[f]; N = F(n); Gamma = sum(T); x = P
    # p_g, a_g
    a_g = {}
    for g in M:
        Q = cyc[g]; cnt = {}
        for path in Q:
            for v in path: cnt[v] = cnt.get(v, 0)+1
        k = len(Q)
        a_g[g] = sum(F(cnt.get(x[i], 0), k) for i in range(L))
    Lg = {g: ell[g] for g in M}
    h = [T[x[i]]/N for i in range(L)]; S = sum(h); q = min(h[i]*h[(i+1) % L] for i in range(L))
    deltaP = (S/L)**2 - q
    chiP = [0]*n
    for end in (x[0], x[-1]):
        ch = chi_profile(n, adj, side, end, M, n)
        for r in range(n): chiP[r] += ch[r]
    # m_r,a_r,Z_r,Tail_k (my form)
    m = [sum(1 for g in M if Lg[g] > r) for r in range(n)]
    a = [sum(a_g[g] for g in M if Lg[g] > r) for r in range(n)]
    Z = [L*(1-m[r]) + F(25*(L-a[r]), 2*r+1) - chiP[r] - (deltaP if r < L else F(0)) for r in range(n)]
    def Tail_mine(k): return sum((2*r+1)*Z[r] for r in range(k, n))
    # truncated form
    def phi(t, k): return max(t*t - k*k, 0)
    def trunc(k):
        Gamma_k = sum(phi(Lg[g], k) for g in M)
        A_k = sum(a_g[g]*max(Lg[g]-k, 0) for g in M)
        E_k = sum((2*r+1)*chiP[r] for r in range(k, n))
        phikL = phi(L, k)
        return L*(N*N - k*k - Gamma_k) + 25*(L*(N-k) - A_k) - phikL*deltaP - E_k
    return all(Tail_mine(k) == trunc(k) for k in range(n))

def main():
    fams = []
    for nn in range(5, 9):
        for g6 in subprocess.run([GENG, "-tc", str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6); fams.append((n, E))
    for sizes in [(2,1,2,1,2),(2,1,2,1,3)]:
        n, E = odd_blowup(5, list(sizes)); fams.append((n, E))
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n,E=union_disjoint((n5,E5),(n7,E7)); E=E+[(0,n5)]; fams.append((n,E))
    tot = 0; bad = 0
    for (n, E) in fams:
        adj, cuts = gmins(n, E)
        for side in cuts:
            st = struct_for_side(n, adj, side)
            if st is None: continue
            M, ell, T, cyc = st[0], st[1], st[2], st[4]
            for f in M:
                if ell[f] % 2 == 0: continue
                for P in cyc[f]:
                    if len(P) != ell[f]: continue
                    tot += 1
                    if not verify_row(n, adj, side, M, ell, T, cyc, f, P): bad += 1
    print("rows checked:", tot, " truncated-form mismatches:", bad)
    print(">>> GPT truncated resource decomposition EXACT" if bad == 0 else ">>> MISMATCH")

if __name__ == "__main__":
    main()
