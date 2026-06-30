"""Localize the Dout credit to a NEIGHBORHOOD of the geodesic.  B_L = L*Dout + (L+25)*Din - disp,
Dout>=0 verified.  Test: can Dout be replaced by underload concentrated near P?
Define for radius-r B-ball around path P (B = cut graph):
   Dnb(r) = sum_{v in B-ball_r(P), v notin P} (N - T_v)
and test  (CLAIM-r):  L*Dnb(r) + (L+25)*Din - disp >= 0.
r=0 is path-only (FAILS). Find smallest r that suffices on census.  Also verify Dout>=0 on N=23.
ALL exact.
"""
import sys, subprocess
from collections import deque
from fractions import Fraction as F
from _h import dec, GENG, Bconn, geos
from _bdef_construct import Cn, mycielski

def adjof(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    return adj
def cutsize(n,adj,side):
    return sum(1 for u in range(n) for v in adj[u] if v>u and side[u]!=side[v])
def all_maxcuts(n,adj):
    best=-1; cuts=[]
    for mask in range(1<<n):
        side=[(mask>>i)&1 for i in range(n)]; c=cutsize(n,adj,side)
        if c>best: best=c; cuts=[side]
        elif c==best: cuts.append(side)
    return cuts
def greedy_maxcut(n,adj):
    import random; best=None
    for trial in range(30):
        random.seed(trial); side=[random.randint(0,1) for _ in range(n)]
        imp=True
        while imp:
            imp=False
            for v in range(n):
                s=sum(1 for w in adj[v] if side[w]==side[v]); d=len(adj[v])-s
                if s>d: side[v]^=1; imp=True
        cs=cutsize(n,adj,side)
        if best is None or cs>best[0]: best=(cs,side)
    return best[1]
def struct(n,adj,side):
    M=[(u,v) for u in range(n) for v in adj[u] if v>u and side[u]==side[v]]
    if not M or not Bconn(n,adj,side): return None
    T=[F(0)]*n; ell={}; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1])
        if not Ps: return None
        cyc[f]=Ps; ell[f]=len(Ps[0]); sh=F(ell[f],len(Ps))
        T=[T[i]+(sh*sum(1 for P in Ps if i in P)) for i in range(n)]
    return M,ell,T,cyc

def bball(adj,side,Pset,r):
    # B-graph (cut edges only) ball of radius r around P
    seen=set(Pset); frontier=set(Pset)
    for _ in range(r):
        nxt=set()
        for u in frontier:
            for v in adj[u]:
                if side[v]!=side[u] and v not in seen:
                    nxt.add(v); seen.add(v)
        frontier=nxt
    return seen

def run(n,E,allcuts):
    adj=adjof(n,E)
    cuts=all_maxcuts(n,adj) if allcuts else [greedy_maxcut(n,adj)]
    out=dict(rows=0,minDout=None,failr={0:0,1:0,2:0,3:0},minB=None)
    for side in cuts:
        st=struct(n,adj,side)
        if st is None: continue
        M,ell,T,cyc=st; N=F(n); Gamma=sum(T); Tall=N*N-Gamma
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                out['rows']+=1
                Pset=set(P)
                Ti=[T[i] for i in P]
                Din=sum(N-t for t in Ti)
                Dout=Tall-Din
                if out['minDout'] is None or Dout<out['minDout']: out['minDout']=Dout
                h=[t/N for t in Ti]; S=sum(h)
                q=min(h[i]*h[(i+1)%L] for i in range(L))
                disp=S*S-(L*L)*q
                B=L*Dout+(L+25)*Din-disp
                if out['minB'] is None or B<out['minB']: out['minB']=B
                for r in (0,1,2,3):
                    ball=bball(adj,side,Pset,r)
                    Dnb=sum(N-T[v] for v in ball if v not in Pset)
                    if L*Dnb+(L+25)*Din-disp<0: out['failr'][r]+=1
    return out

def main():
    agg=dict(rows=0,minDout=None,failr={0:0,1:0,2:0,3:0})
    for nn in range(5,11):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); r=run(n,E,True)
            agg['rows']+=r['rows']
            if r['minDout'] is not None and (agg['minDout'] is None or r['minDout']<agg['minDout']):
                agg['minDout']=r['minDout']
            for k in (0,1,2,3): agg['failr'][k]+=r['failr'][k]
    print("CENSUS N<=10 all max cuts: rows=%d minDout=%s"%(agg['rows'],agg['minDout']))
    for k in (0,1,2,3):
        print("  CLAIM-r=%d (ball-%d underload credit)  fails=%d"%(k,k,agg['failr'][k]))
    # N=23 Dout>=0 + B_L>=0 single greedy cut
    g=mycielski(*mycielski(5,Cn(5)))
    r=run(g[0],g[1],False)
    print("Myc(Grotzsch) N=23 (greedy cut): rows=%d minDout=%s minB=%s"%(r['rows'],r['minDout'],r['minB']))

if __name__=="__main__":
    main()
