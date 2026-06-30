"""Gate Codex 374 PATH-DEFICIT STABILITY (PDS) reformulation of VAR-STABILITY.
   d_v=T_v-N, R=N^2-Gamma=-sum_v d_v, D_P=sum_{i} d_{x_i}, h_i=T_{x_i}/N, S=sum h_i,
   q=min_i h_i h_{i+1}, C_L=S^2-L^2 q, E_P=R-(25/L) D_P.   Identity: B_L = L*E_P - C_L.
   Sub-gates (L general; 25/L and 5L use L):
     (1) E_P >= 0                    [= PATH-GAMMA per-path]
     (2) VarT <= 5*L*E_P             [C-free variance-vs-deficit]
     (3) VarT + 5*C_L <= 5*L*E_P     [full PDS == 5*B_L>=VarT]
   Equality diagnostics: E_P=0 => VarT=0 & C_L=0?  nonflat equality in PDS?
   ALL exact Fraction.  Full battery: census N<=11 + blowups + glued + Grotzsch + Myc(Grotzsch) N=23.
"""
import subprocess, random
from fractions import Fraction as F
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def check(n, adj, side, acc):
    st = struct_for_side(n, adj, side)
    if st is None: return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    N = F(n); Gamma = sum(T); R = N*N - Gamma
    VarT = sum((T[v]-N)**2 for v in range(n))
    for f in M:
        L = ell[f]
        if L % 2 == 0: continue
        for P in cyc[f]:
            if len(P) != L: continue
            x = P
            D_P = sum(T[x[i]]-N for i in range(L))
            h = [T[x[i]]/N for i in range(L)]; S = sum(h); q = min(h[i]*h[(i+1)%L] for i in range(L))
            C_L = S*S - (L*L)*q
            E_P = R - F(25, L)*D_P
            B_L = L*E_P - C_L
            acc['rows'] += 1
            if E_P < 0:
                acc['e_fail'] += 1; acc['e_ex'] = acc['e_ex'] or (n, L, tuple(x), str(E_P))
            if VarT - 5*L*E_P > 0:
                acc['cfree_fail'] += 1; acc['cf_ex'] = acc['cf_ex'] or (n, L, tuple(x), str(VarT), str(5*L*E_P))
            if VarT + 5*C_L - 5*L*E_P > 0:
                acc['pds_fail'] += 1; acc['pds_ex'] = acc['pds_ex'] or (n, L, tuple(x))
            # equality diagnostics
            if E_P == 0 and (VarT != 0 or C_L != 0):
                acc['ep0_nonflat'] += 1; acc['ep0_ex'] = acc['ep0_ex'] or (n, L, tuple(x), str(VarT), str(C_L))
            if VarT + 5*C_L == 5*L*E_P and VarT != 0:
                acc['pds_eq_nonflat'] += 1; acc['eq_ex'] = acc['eq_ex'] or (n, L, tuple(x), str(VarT))
            # track worst C-free ratio
            if E_P > 0:
                rt = VarT/(5*L*E_P)
                if acc['cfree_max'] is None or rt > acc['cfree_max']:
                    acc['cfree_max'] = rt; acc['cfree_row'] = (n, L, tuple(x))

def fam(name, n, E, acc):
    adj, cuts = gmins(n, E)
    for side in cuts: check(n, adj, side, acc)

def maxcut_ls(n, adj, seeds=40):
    best=None; bv=-1; rng=random.Random(3)
    for _ in range(seeds):
        s=[rng.randint(0,1) for _ in range(n)]; imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if s[w]==s[v])>sum(1 for w in adj[v] if s[w]!=s[v]): s[v]^=1; imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and s[v]!=s[w])
        if val>bv: bv=val; best=s[:]
    return best

def main():
    acc = dict(rows=0, e_fail=0, cfree_fail=0, pds_fail=0, ep0_nonflat=0, pds_eq_nonflat=0,
               e_ex=None, cf_ex=None, pds_ex=None, ep0_ex=None, eq_ex=None, cfree_max=None, cfree_row=None)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n, E = dec(g6); fam("cen%d"%nn, n, E, acc)
        print("census N=%d: rows=%d e_fail=%d cfree_fail=%d pds_fail=%d"
              % (nn, acc['rows'], acc['e_fail'], acc['cfree_fail'], acc['pds_fail']), flush=True)
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,3),
                  (3,3,2,2,2),(3,3,3,3,2),(4,3,4,3,4),(2,3,2,3,4)]:
        if sum(sizes)<=14:
            n,E=odd_blowup(5,list(sizes)); fam("C5",n,E,acc)
    for sizes in [(1,)*7,(2,1,1,1,1,1,1),(2,2,2,1,1,1,1)]:
        if sum(sizes)<=14:
            n,E=odd_blowup(7,list(sizes)); fam("C7",n,E,acc)
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9); n11,E11=11,Cn(11)
    for (a,b,br) in [((n5,E5),(n7,E7),[(0,5)]), ((n5,E5),(n11,E11),[(0,5)]), ((n7,E7),(n9,E9),[(0,7)])]:
        n,E=union_disjoint(a,b); E=E+br; fam("glue",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); fam("Grotzsch",grN,grE,acc)
    n,E=mycielski(grN,grE); adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): check(n,adj,side,acc)
    print("="*55)
    print("TOTAL rows:", acc['rows'])
    print("(1) E_P>=0 fails:", acc['e_fail'], acc['e_ex'] or '')
    print("(2) VarT<=25*E_P (C-free) fails:", acc['cfree_fail'], acc['cf_ex'] or '')
    print("(3) PDS VarT+5C_L<=25E_P fails:", acc['pds_fail'], acc['pds_ex'] or '')
    print("E_P=0 with (VarT,C_L) not both 0:", acc['ep0_nonflat'], acc['ep0_ex'] or '')
    print("PDS equality with VarT>0 (nonflat):", acc['pds_eq_nonflat'], acc['eq_ex'] or '')
    print("worst C-free ratio VarT/(25 E_P):", str(acc['cfree_max']), float(acc['cfree_max']) if acc['cfree_max'] else None, "at", acc['cfree_row'])

if __name__ == "__main__":
    main()
