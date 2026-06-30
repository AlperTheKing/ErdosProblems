"""Gate Codex block-311 SELECTABLE-CUT replacement for the false bare net_H<=3.
Among gamma-min connected-B max cuts, select by lexicographic profile:
  P0 = sorted-descending T-vector (minimize: prefer smaller top loads).
  P1 = sorted-descending list over scoped high bands H_j (2t_j>=N, multi-pos-K-comp) of (sigma(H),maxnet(H),|H|,t_j),
       minimize. sigma(H)=sum_{v in H}(B_out-M_out), maxnet=max net.
Check: do SELECTED cuts satisfy net_H(v)<=3 on every scoped high-band vertex?
Census N<=11 (gmins gives ALL gamma-min cuts) + the explicit C5-fan S0/S1 pair (N=30, can't enumerate)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins

def profile_and_net(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return None
    P0=tuple(sorted((T[v] for v in range(n)),reverse=True))
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    multi = len(set(cid[v] for v in range(n) if T[v]>0))>=2
    levs=sorted(set([F(0)]+[t for t in set(T) if t>0]))
    bands=[]; scoped_net=[]   # (sigma,maxnet,|H|,t)
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        sig=0; mx=-10**9
        for v in H:
            B_out=sum(1 for w in adj[v] if w not in H and side[v]!=side[w])
            M_out=sum(1 for w in adj[v] if w not in H and side[v]==side[w])
            net=B_out-M_out; sig+=net; mx=max(mx,net)
            if multi: scoped_net.append((j,v,net,str(T[v])))
        bands.append((sig,mx,len(H),tj))
    P1=tuple(sorted(bands,reverse=True))
    return P0,P1,scoped_net,multi

def select_and_check(name,n,adj,cuts,acc):
    rows=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        pr=profile_and_net(n,adj,side)
        if pr is None: continue
        rows.append((pr[0],pr[1],side,pr[2],pr[3]))
    if not rows: return
    acc['graphs_multi_cut'] += (1 if len(rows)>1 else 0)
    # P0 lex-min (Fractions: smaller descending tuple) -- compare elementwise
    p0min=min(r[0] for r in rows)
    r1=[r for r in rows if r[0]==p0min]
    p1min=min(r[1] for r in r1)
    sel=[r for r in r1 if r[1]==p1min]
    for r in sel:
        acc['selected']+=1
        for (j,v,net,Tv) in r[3]:
            acc['scoped']+=1
            if net>3:
                acc['viol']+=1
                if acc['fviol'] is None: acc['fviol']=(name,n,j,v,net,Tv)

def build_fan(sizes=(3,9,1,9,3)):
    off=[0]
    for s in sizes: off.append(off[-1]+s)
    nfb=off[-1]; parts=[list(range(off[i],off[i+1])) for i in range(5)]
    E=set()
    for i in range(5):
        j=(i+1)%5
        for a in parts[i]:
            for b in parts[j]: E.add((min(a,b),max(a,b)))
    n=nfb; sep=[n+k for k in range(5)]
    for k in range(5):
        a=sep[k]; b=sep[(k+1)%5]; E.add((min(a,b),max(a,b)))
    n+=5
    E.add((parts[4][0],sep[1]))
    adj=[set() for _ in range(n)]
    for x,y in sorted(E): adj[x].add(y); adj[y].add(x)
    return n,adj,parts,sep

if __name__=="__main__":
    acc=dict(graphs_multi_cut=0,selected=0,scoped=0,viol=0,fviol=None)
    for nn in range(5,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            if cuts: select_and_check("cen%s"%g6,n,adj,cuts,acc)
        print("  census N=%d done (selected=%d scoped=%d viol=%d)"%(nn,acc['selected'],acc['scoped'],acc['viol']),flush=True)
    # explicit fan: S0 vs S1 are the two competing gamma-min cuts
    n,adj,parts,sep=build_fan()
    sepA=[0,1,0,1,0]
    def mk(fb):
        side=[0]*n
        for i in range(5):
            for v in parts[i]: side[v]=fb[i]
        for k,v in enumerate(sep): side[v]=sepA[k]
        return side
    S0=mk([0,1,0,1,0]); S1=mk([1,0,0,1,0])
    print("\n  FAN pair (S0,S1) as candidate gamma-min cuts:",flush=True)
    accf=dict(graphs_multi_cut=0,selected=0,scoped=0,viol=0,fviol=None)
    select_and_check("C5fan(3,9,1,9,3)",n,adj,[S0,S1],accf)
    print("    selected=%d scoped=%d viol=%d (selected cut should be S1 with net_H=0)"%(accf['selected'],accf['scoped'],accf['viol']),flush=True)
    print("    fan first-viol=%s"%(accf['fviol'],),flush=True)
    print("\n  census: graphs w/multiple gamma-min cuts=%d selected cuts tested=%d scoped pts=%d net_H>3 viol=%d %s"%(
        acc['graphs_multi_cut'],acc['selected'],acc['scoped'],acc['viol'],acc['fviol'] or ''),flush=True)
    ok = acc['viol']==0 and accf['viol']==0
    print("  === SELECTABLE-CUT net_H<=3 %s ==="%("HOLDS on census+fan" if ok else "FAILS"),flush=True)
