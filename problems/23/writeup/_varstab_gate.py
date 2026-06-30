"""Exact gate for Codex's VAR-STABILITY strengthening (372):
      5 * Tail_0(P) >= VarT,   VarT := sum_{v in V} (T(v)-N)^2,
      Tail_0(P) = sum_r (2r+1) Z_r(P) = B_L(P) - DG(x0) - DG(x_{L-1}).
   gamma-min => DG endpoints >=0 => Tail_0 >= VarT/5 >= 0 => atom.  ALL exact Fraction.
   Reports: #rows, #fails, worst (smallest) ratio Tail0/VarT (VarT>0), any equality Tail0=0 with VarT>0.
"""
import subprocess, random
from fractions import Fraction as F
from _layer_gate import Zr_row
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint, mycielski

def check(n, adj, side, acc):
    st = struct_for_side(n, adj, side)
    if st is None: return
    M, ell, T, cyc = st[0], st[1], st[2], st[4]
    N = F(n)
    VarT = sum((T[v]-N)**2 for v in range(n))
    for f in M:
        if ell[f] % 2 == 0: continue
        for P in cyc[f]:
            if len(P) != ell[f]: continue
            B_L, DGsum, Z, lhs, rhs = Zr_row(n, adj, side, M, ell, T, cyc, f, P)
            Tail0 = sum((2*r+1)*Z[r] for r in range(n))
            acc['rows'] += 1
            if 5*Tail0 - VarT < 0:
                acc['fail'] += 1
                if acc['ex'] is None:
                    acc['ex'] = (n, ell[f], tuple(P), str(5*Tail0), str(VarT))
            if VarT > 0:
                ratio = Tail0/VarT
                if acc['minratio'] is None or ratio < acc['minratio']:
                    acc['minratio'] = ratio; acc['minrow'] = (n, ell[f], tuple(P))
            if Tail0 == 0 and VarT > 0:
                acc['zerotail_posvar'] += 1

def gmins_family(name, n, E, acc):
    adj, cuts = gmins(n, E)
    for side in cuts: check(n, adj, side, acc)

def maxcut_ls(n, adj, seeds=40):
    best=None; bv=-1; rng=random.Random(7)
    for _ in range(seeds):
        side=[rng.randint(0,1) for _ in range(n)]; imp=True
        while imp:
            imp=False
            for v in range(n):
                if sum(1 for w in adj[v] if side[w]==side[v]) > sum(1 for w in adj[v] if side[w]!=side[v]):
                    side[v]^=1; imp=True
        val=sum(1 for v in range(n) for w in adj[v] if w>v and side[v]!=side[w])
        if val>bv: bv=val; best=side[:]
    return best

def main():
    acc = dict(rows=0, fail=0, ex=None, minratio=None, minrow=None, zerotail_posvar=0)
    for nn in range(5, 12):
        for g6 in subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split():
            n, E = dec(g6); gmins_family("cen%d"%nn, n, E, acc)
        print("census N=%d: rows=%d fail=%d"%(nn, acc['rows'], acc['fail']), flush=True)
    for sizes in [(1,1,1,1,1),(2,2,2,2,2),(2,1,2,1,2),(2,1,2,1,3),(3,2,3,2,3),(2,2,2,2,3),
                  (3,3,2,2,2),(3,3,3,3,2),(4,3,4,3,4),(2,3,2,3,4)]:
        if sum(sizes)<=14:
            n,E=odd_blowup(5,list(sizes)); gmins_family("C5",n,E,acc)
    for sizes in [(1,)*7,(2,1,1,1,1,1,1),(2,2,2,1,1,1,1)]:
        if sum(sizes)<=14:
            n,E=odd_blowup(7,list(sizes)); gmins_family("C7",n,E,acc)
    print("blowups: rows=%d fail=%d"%(acc['rows'], acc['fail']), flush=True)
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n9,E9=9,Cn(9); n11,E11=11,Cn(11)
    for (a,b,br) in [((n5,E5),(n7,E7),[(0,5)]), ((n5,E5),(n11,E11),[(0,5)]), ((n7,E7),(n9,E9),[(0,7)])]:
        n,E=union_disjoint(a,b); E=E+br; gmins_family("glue",n,E,acc)
    grN,grE=mycielski(5,Cn(5)); gmins_family("Grotzsch",grN,grE,acc)
    print("glued+Grotzsch: rows=%d fail=%d"%(acc['rows'], acc['fail']), flush=True)
    # Myc(Grotzsch) N=23 heuristic max cut
    n,E=mycielski(grN,grE)
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=maxcut_ls(n,adj)
    if Bconn(n,adj,side): check(n,adj,side,acc)
    print("="*55)
    print("TOTAL rows:", acc['rows'], " FAILS(5*Tail0<VarT):", acc['fail'], acc['ex'] or '')
    print("worst ratio Tail0/VarT:", str(acc['minratio']), float(acc['minratio']) if acc['minratio'] else None, "at", acc['minrow'])
    print("equality Tail0=0 with VarT>0:", acc['zerotail_posvar'])
    print("VERDICT:", "5*Tail0>=VarT HOLDS (min ratio>=1/5)" if acc['fail']==0 else "FAILS")

if __name__ == "__main__":
    main()
