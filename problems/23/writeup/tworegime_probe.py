#!/usr/bin/env python3
"""Two-regime coupling probe for (R). C5[q] gmin cut has two vertex types:
 - 'interior' (parts 0,1,2): degB=2q, R=q  => R = degB/2
 - 'bad-endpoint-adjacent' (parts 3,4): degB=q, R=q  => R = degB
The cycles through w each contribute 2 cut-edge-incidences at w UNLESS w is an endpoint of the bad edge f
(then the cycle uses 1 cut-edge + the 1 bad edge at w). So define for vertex w and the routing:
  inc_cut(w)  = weighted # cut-edge-incidences at w from cycles thru w
  inc_bad(w)  = weighted # bad-edge-incidences at w (w is an endpoint of f, cycle of f thru w)
Each cycle thru w contributes (2 - [w is endpoint of that f]) cut-incidences and [w endpoint] bad-incidences.
So inc_cut(w) + inc_bad(w) = 2 R(w)  (each cycle has 2 edges at w total).
And inc_cut(w) <= degB(w) is FALSE in general (a cut edge can serve many cycles). Measure all these and
seek the true law.  Also test the CD-flavored bound: 2R(w) - inc_bad(w) = inc_cut(w) and relate to degB.
EXACT.
"""
import io, contextlib, subprocess
from fractions import Fraction as F
with contextlib.redirect_stdout(io.StringIO()):
    from census_GPI import dec, maxcut_all, gmin, geos, blow, GENG

def go(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    Mset=set(M)|set((b,a) for a,b in M)
    degB=[sum(1 for v in adj[u] if side[u]!=side[v]) for u in range(n)]
    R=[F(0) for _ in range(n)]; ellmax=[0]*n
    inc_bad=[F(0) for _ in range(n)]      # weighted bad-incidences at w
    inc_cut=[F(0) for _ in range(n)]
    for f in M:
        x,y=f
        Ps=geos(adj,side,x,y); nf=len(Ps)
        if nf==0: return None
        s1=F(1,nf)
        for P in Ps:
            # cycle = P + closing bad edge (P[-1]=y, P[0]=x), edges: consecutive in P are CUT edges,
            # plus the bad edge (x,y).
            cyc=P
            Lp=len(cyc)
            for i,v in enumerate(cyc):
                R[v]+=s1
                if ell[f]>ellmax[v]: ellmax[v]=ell[f]
                # edges of cycle at v: in path, neighbors cyc[i-1],cyc[i+1] (mod, but path endpoints x,y
                # are joined by the bad edge). v=x (i=0): path-edge to cyc[1] (cut) + bad edge to y.
                # v=y (i=Lp-1): path-edge to cyc[Lp-2] (cut) + bad edge to x.
                # interior: 2 path edges (cut).
                if v==x or v==y:
                    inc_cut[v]+=s1; inc_bad[v]+=s1
                else:
                    inc_cut[v]+=2*s1
    K=n+(n*n-G)
    rows=[]
    for w in range(n):
        if R[w]==0: continue
        rows.append((w,R[w],degB[w],ellmax[w],inc_bad[w],inc_cut[w]))
    return n,G,K,rows

if __name__=="__main__":
    # candidates:
    #  C1: inc_cut(w) <= degB(w)   ?
    #  C2: R(w) <= (degB(w)+inc_bad(w))/2   [since 2R = inc_cut+inc_bad <= degB+inc_bad IF C1]
    #  C3: ellmax(w)*R(w) <= K via C2
    acc=dict(C1=0,C2=0,cnt=0,w1=F(-99),a1=None,w2=F(-99),a2=None)
    graphs=[(f"C5[{q}]",blow(q)) for q in (2,3,4)]+[("n8",dec("G?\x60F\x60w"))]
    for nn in range(5,8):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        graphs+=[(g,dec(g)) for g in out]
    for nm,(n,E) in graphs:
        rr=go(n,E)
        if rr is None: continue
        n2,G,K,rows=rr
        for w,Rw,degB,L,ib,ic in rows:
            acc['cnt']+=1
            if ic>degB:
                acc['C1']+=1
                if ic-degB>acc['w1']: acc['w1']=ic-degB; acc['a1']=(nm,w,float(ic),degB,G,n2)
            bd=(F(degB)+ib)/2
            if Rw>bd:
                acc['C2']+=1
                if Rw-bd>acc['w2']: acc['w2']=Rw-bd; acc['a2']=(nm,w,float(Rw),float(bd),G,n2)
    print("vertices:",acc['cnt'])
    print("C1) inc_cut(w) <= degB(w): fails=",acc['C1']," worst=",float(acc['w1']),"at",acc['a1'])
    print("C2) R(w) <= (degB(w)+inc_bad(w))/2: fails=",acc['C2']," worst=",float(acc['w2']),"at",acc['a2'])
