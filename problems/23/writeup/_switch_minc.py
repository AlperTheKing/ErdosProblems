"""Gate Codex 347 SWITCH IMPLICATION (the proof target for the C_inc path-load atom):
for any connected-B MAX cut, ell=5 bad edge f, geodesic P, with M(P)=F(P)-C_inc/25 < 0, there EXISTS |U|<=2 with
flip neutral (delta_B(U)=delta_M(U)), B connected, Gamma(switched)<Gamma. => gamma-min cut has M>=0 => F>=C_inc/25
=> (C_inc>=0 AM-GM) PATH-GAMMA for ell=5.
Test on ALL max cuts: census N<=9 (maxcut_all) + non-gamma-min perturbations (neutral flips) of structured
gamma-min cuts (blowups, glued islands, Mycielskians, two-lane) + H?AFBo]. Report M<0 rows, implication failures."""
import subprocess
from itertools import combinations
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane

def cut_size(n,E,side): return sum(1 for x,y in E if side[x]!=side[y])
def margins(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    G=sum(T); rows=[]
    for f in M:
        if ell[f]!=5: continue
        for P in cyc[f]:
            if len(P)!=5: continue
            h=[F(T[P[i]],n) for i in range(5)]; S=sum(h)
            pr=[h[i]*h[(i+1)%5] for i in range(5)]
            Cinc=S*S-25*min(pr)
            FP=F(5,25)*(F(n*n)-G)-sum(T[P[i]]-F(n) for i in range(5))
            rows.append((FP-Cinc/25, P))
    return G,rows
def gamma_of(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    return sum(st[2])
def find_switch(n,E,adj,side,maxcut,G0):
    for k in (1,2):
        for U in combinations(range(n),k):
            nb=side[:]
            for v in U: nb[v]^=1
            if cut_size(n,E,nb)!=maxcut: continue
            if not Bconn(n,adj,nb): continue
            g=gamma_of(n,adj,nb)
            if g is not None and g<G0: return U,g
    return None
def test(name,n,E,adj,side,acc):
    mc=cut_size(n,E,side)
    r=margins(n,adj,side)
    if r is None: return
    G0,rows=r
    neg=[m for m,P in rows if m<0]
    if not neg: return
    acc['negcuts']+=1; acc['negrows']+=len(neg)
    sw=find_switch(n,E,adj,side,mc,G0)
    if sw is None:
        acc['fail']+=1
        if acc['ffail'] is None: acc['ffail']=(name,n,str(min(neg)))
    else: acc['ksizes'][len(sw[0])]=acc['ksizes'].get(len(sw[0]),0)+1

def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a
def blowup(parts):
    off=[0]
    for s in parts: off.append(off[-1]+s)
    nn=off[-1]; EE=[]; L=len(parts)
    for i in range(L):
        j=(i+1)%L
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def bridge_g(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

def neutral_perturbations(n,E,adj,base,maxcut,r=2):
    out=[base]; seen={tuple(base)}
    for k in range(1,r+1):
        for U in combinations(range(n),k):
            nb=base[:]
            for v in U: nb[v]^=1
            if cut_size(n,E,nb)==maxcut and Bconn(n,adj,nb):
                t=tuple(nb)
                if t not in seen: seen.add(t); out.append(nb)
    return out

if __name__=="__main__":
    acc=dict(negcuts=0,negrows=0,fail=0,ffail=None,ksizes={})
    # all max cuts census N<=9
    for nn in range(5,10):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj=adj_of(n,E)
            for s in maxcut_all(n,adj): test('cen%s'%g6,n,E,adj,s,acc)
        print("  allcut census N=%d done (negcuts=%d fail=%d)"%(nn,acc['negcuts'],acc['fail']),flush=True)
    # non-gamma-min perturbations of structured gamma-min cuts
    fams=[("C5[2]",blowup([2,2,2,2,2])),("C5[3]",blowup([3,3,3,3,3])),("fan",blowup([2,1,2,1,2])),
          ("fan2",blowup([3,2,3,2,3])),("Grotzsch",mycielski(5,Cn(5))),("C5|C7",bridge_g((5,Cn(5)),(7,Cn(7)),0,0)),
          ("C7|Grotzsch",bridge_g((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C5|C5",bridge_g((5,Cn(5)),(5,Cn(5)),0,0))]
    for name,(nn,E) in fams:
        adj,cuts=gmins(nn,E)
        if not cuts: continue
        mc=cut_size(nn,E,cuts[0])
        for base in cuts[:2]:
            for s in neutral_perturbations(nn,E,adj,base,mc,r=2):
                test(name+"-pert",nn,E,adj,s,acc)
    for L in (8,12):
        n,E,side,bad=build_two_lane(L); adj=adj_of(n,E); mc=cut_size(n,E,side)
        for s in neutral_perturbations(n,E,adj,side,mc,r=2): test("tl%d-pert"%L,n,E,adj,s,acc)
    print("\n  SWITCH IMPLICATION (M(P)<0 => |U|<=2 neutral Gamma-decreasing switch):")
    print("  cuts with a negative-M row=%d  total negative rows=%d"%(acc['negcuts'],acc['negrows']))
    print("  implication FAILURES (no |U|<=2 Gamma-decreasing switch)=%d %s"%(acc['fail'],acc['ffail'] or ''))
    print("  switch sizes used: %s"%acc['ksizes'])
    print("  === SWITCH IMPLICATION %s ==="%("HOLDS (every M<0 cut has a |U|<=2 Gamma-decreasing switch) => proof target alive" if acc['fail']==0 else "FAILS"))
