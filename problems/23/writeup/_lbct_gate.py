"""EXACT gate of Codex block-254 LBCT (Low-Band Corridor Transport): a max-flow certificate that implies
FULL-LOW-INTERNAL-LOAD min-free. For each full-low band (2b<=N), H={T>a}, O_H={v in H:T>N}, D_H={v in H:T<N}.
Corridor intervals = maximal CYCLIC runs of P cap H along each geodesic P of cyc[f] (P+f closes to a cycle;
merge first/last runs across the bad edge), weight w(I)=ell[f]/|cyc[f]|.
Network: s->o cap T[o]-N; o->I cap w(I) for I containing o; I->u cap INF for u in D_H cap I; u->t cap N-T[u].
CLAIM: maxflow == sum_{o in O_H}(T[o]-N) (source saturation) => T(H)<=N*h. Full battery; report failures."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords
from _level_transport import Dinic

def cyclic_intervals(P,Hset):
    L=len(P); inH=[P[i] in Hset for i in range(L)]
    if all(inH): return [list(P)]
    if not any(inH): return []
    start=next(i for i in range(L) if not inH[i])
    ivs=[]; cur=[]
    for k in range(L):
        i=(start+k)%L
        if inH[i]: cur.append(P[i])
        else:
            if cur: ivs.append(cur); cur=[]
    if cur: ivs.append(cur)
    return ivs

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,mu,cyc=st
    if not M: return
    levs=[F(0)]+sorted(set(v for v in T if v>0))
    for j in range(len(levs)-1):
        a=levs[j]; b=levs[j+1]
        if 2*b>n: continue
        Hset=set(v for v in range(n) if T[v]>a)
        if not Hset: continue
        OH=[v for v in Hset if T[v]>n]; DH=set(v for v in Hset if T[v]<n)
        demand=sum(T[o]-F(n) for o in OH)
        acc['nb']+=1
        if not OH or demand==0: continue
        # collect intervals (only those that contain >=1 O_H vertex and >=1 D_H vertex are useful, but include all)
        ivs=[]
        for f in M:
            w=F(ell[f],len(cyc[f]))
            for P in cyc[f]:
                for I in cyclic_intervals(P,Hset):
                    Iset=set(I)
                    if Iset & set(OH) and (Iset & DH):
                        ivs.append((w,Iset))
        # build flow network
        S=0; Tn=1; nid=2
        onode={o:nid for nid,o in zip(range(nid,nid+len(OH)),OH)}; nid+=len(OH)
        dnode={u:nid for nid,u in zip(range(nid,nid+len(DH)),DH)}; nid+=len(DH)
        ivnode=[]
        for (w,Iset) in ivs: ivnode.append(nid); nid+=1
        din=Dinic(nid)
        for o in OH: din.add(S,onode[o],T[o]-F(n))
        for u in DH: din.add(dnode[u],Tn,F(n)-T[u])
        INF=demand+1
        for k,(w,Iset) in enumerate(ivs):
            for o in (Iset & set(OH)): din.add(onode[o],ivnode[k],w)
            for u in (Iset & DH): din.add(ivnode[k],dnode[u],INF)
        fl=din.maxflow(S,Tn)
        if fl!=demand:
            acc['fail']+=1
            if acc['first'] is None: acc['first']=(name,''.join(map(str,side)),n,str(a),len(OH),len(DH),str(demand),str(fl))

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
def bridge(b1,b2,u,v):
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn, E+[(u,n1+v)]

if __name__=="__main__":
    acc={'nb':0,'fail':0,'first':None}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L); chk("two-lane-L%d"%L,n,adj_of(n,E),side,acc)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad); chk("klane-L%dk%d"%(Ll,k),n,adj_of(n,E),side,acc)
    print("  two-lane+k-lane: fail=%d"%acc['fail'],flush=True)
    for c in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*c)
            if n>26: continue
            adj,cuts=gmins(n,E)
            for s in (cuts[:2] if cuts else []): chk("C%d[%d]"%(c,t),n,adj,s,acc)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        for s in (cuts[:2] if cuts else []): chk("nu%s"%parts,n,adj,s,acc)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [("Grotzsch",grot),("Myc(Grotzsch)",mycg),("M(C7)",mycielski(7,Cn(7))),("M(C9)",mycielski(9,Cn(9))),
                      ("C7|Grotzsch",bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),("C9|C9",bridge((9,Cn(9)),(9,Cn(9)),0,0)),
                      ("C5|C7",bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        for s in cuts[:3]: chk(nm,nn,adj,s,acc)
    print("  blow-ups + Mycielskians + glued done (fail=%d)"%acc['fail'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        v0=acc['fail']
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts: chk("cen%s"%g6,n,adj,s,acc)
        print("  census N=%d (fail+%d)"%(nn,acc['fail']-v0),flush=True)
    print("\n  full-low bands with O_H nonempty checked; LBCT saturation FAILURES=%d"%acc['fail'],flush=True)
    if acc['first']: print("  first failure: %s"%(acc['first'],),flush=True)
    print("  === LBCT (corridor transport saturates sources) %s ==="%("HOLDS => proves FULL-LOW-INTERNAL min-free" if not acc['fail'] else "FAILS"),flush=True)
