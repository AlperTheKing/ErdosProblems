"""EXACT Fraction gate of Codex block-235 LOAD-PSC (elementary cut-pressure certificate, NO Perron eigenvector):
  R = sum_v T(v)^2 / Gamma,  Gamma=sum ell^2,
  Xi_T = (N/Gamma) * ( sum_{uv cut edge} |T_u-T_v| - sum_{uv bad edge} |T_u-T_v| ),
  LOAD-PSC-c:  R + Xi_T/c + |M| <= N + N^2/25,  i.e. margin_c = N+N^2/25-|M|-R-Xi_T/c >= 0.
Stronger than LRS (Xi_T>=0 by max-cut CD => LOAD-PSC => LRS => Erdos); FULLY EXACT (T rational). Tight at C5[t].
Test c=25 (natural, ell^2>=25) and c=50. Battery: census gamma-min N<=11 + two-lane + dense k-lane + C5/C7/C9[t]
+ non-uniform blow-ups + Mycielskians N<=23 + glued islands + N=22-style blow-up. Report min margins + first
violation + whether Xi_T ever < 0."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    m=len(M); Gamma=sum(ell[f]**2 for f in M); sumT2=sum(t*t for t in T)
    R=F(sumT2,Gamma)
    badset=set((min(a,b),max(a,b)) for a,b in M)
    tvcut=F(0); tvbad=F(0)
    for u in range(n):
        for v in adj[u]:
            if v>u:
                d=abs(T[u]-T[v])
                if side[u]!=side[v]: tvcut+=d
                else:
                    if (u,v) in badset or (min(u,v),max(u,v)) in badset: tvbad+=d
                    else: tvbad+=d   # all monochromatic edges; bad edges are exactly the monochromatic ones
    XiT=F(n,Gamma)*(tvcut-tvbad)
    if XiT<0: acc['xineg']+=1
    rhs=F(n)+F(n*n,25)-m
    for c in (25,50):
        margin=rhs-R-XiT/c
        key='m%d'%c
        if margin<acc[key][0]: acc[key]=(margin,name,n,m,str(R),str(XiT))
        if margin<0:
            acc['v%d'%c]+=1
            if acc['f%d'%c] is None: acc['f%d'%c]=(name,''.join(map(str,side)),n,m,str(R),str(XiT),c)
    acc['n']+=1

def blowup(parts):
    mm=len(parts); off=[0]*(mm+1)
    for i in range(mm): off[i+1]=off[i]+parts[i]
    nn=off[mm]; EE=[]
    for i in range(mm):
        j=(i+1)%mm
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,sorted(set(EE))
def adj_of(n,E):
    a=[set() for _ in range(n)]
    for x,y in E: a[x].add(y); a[y].add(x)
    return a

if __name__=="__main__":
    acc={'n':0,'v25':0,'v50':0,'xineg':0,'f25':None,'f50':None,
         'm25':(F(10**18),'','','','',''),'m50':(F(10**18),'','','','','')}
    print("=== LOAD-PSC EXACT gate (c=25 and c=50): R + Xi_T/c + |M| <= N+N^2/25 ===",flush=True)
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: v25=%d v50=%d minM25=%s xineg=%d"%(acc['v25'],acc['v50'],float(acc['m25'][0]),acc['xineg']),flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        a0=acc['v25']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (v25+%d)"%(nn,acc['v25']-a0),flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:1] if cuts else []): chk("C%d[%d]"%(cyc,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3],[1,6,2,2,6]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:1] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    def bridge(b1,b2,u,v):
        nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u, n1+v)]
    extra=[("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
           ("C7|brg|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|brg|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0))]
    for name,(nn,E) in extra:
        adj,cuts=gmins(nn,E)
        for s in cuts[:2]: chk(name,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done",flush=True)
    print("\n  total configs=%d  LOAD-PSC-25 viol=%d  LOAD-PSC-50 viol=%d  Xi_T<0 count=%d"%(acc['n'],acc['v25'],acc['v50'],acc['xineg']),flush=True)
    print("  MIN margin c=25: %s at %s"%(float(acc['m25'][0]),acc['m25'][1:]),flush=True)
    print("  MIN margin c=50: %s at %s"%(float(acc['m50'][0]),acc['m50'][1:]),flush=True)
    if acc['f25']: print("  first c=25 violation: %s"%(acc['f25'],),flush=True)
    print("  === LOAD-PSC-25 %s ; LOAD-PSC-50 %s (Xi_T>=0: %s) ==="%(
        "HOLDS" if not acc['v25'] else "FAILS","HOLDS" if not acc['v50'] else "FAILS","yes" if not acc['xineg'] else "NO"),flush=True)
