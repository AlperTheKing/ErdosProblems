from fractions import Fraction as F
from _h import dec, Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side,kcomponents

def boundary(n,adj,side,H):
    dB=dM=0
    for u in H:
        for v in adj[u]:
            if v in H: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

g6='G?bF`w'
n,E=dec(g6)
adj,cuts=gmins(n,E)
print('n',n,'edges',len(E),'cuts',len(cuts))
for ci,side in enumerate(cuts):
    if not Bconn(n,adj,side): continue
    st=struct_for_side(n,adj,side)
    if not st: continue
    M,ell,T,mu,cyc=st
    if len(M)!=2: continue
    eta=F(n*n,25)-len(M)
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]; comps=sorted(set(cid))
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    Apre={c:F(0) for c in comps}
    bands=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=set(v for v in range(n) if T[v]>tj)
        h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
        cnt={c:0 for c in comps}
        for v in H: cnt[cid[v]]+=1
        Aj=wj*(F(n)+eta-tj-tn)*h
        Bj=25*Aj-F(n)*wj*sig
        if 2*tj<F(n):
            coef=wj*(F(n)+eta-tj-tn)
            for c in comps: Apre[c]+=coef*cnt[c]
        bands.append((j,tj,tn,wj,H,h,sig,Aj,Bj,cnt))
    A=sum(Apre.values())
    W=sum(-Bj for j,tj,tn,wj,H,h,sig,Aj,Bj,cnt in bands if 2*tj>=F(n) and Bj<0)
    if A and W/A==F(8305,559):
        print('SIDE',ci,''.join(map(str,side)))
        print('M',M,'ell',ell,'eta',eta)
        print('T',list(enumerate(T)))
        print('components', {c:[v for v in range(n) if cid[v]==c] for c in comps})
        print('Apre',Apre,'A',A,'W',W,'ratio',W/A)
        for b in bands:
            j,tj,tn,wj,H,h,sig,Aj,Bj,cnt=b
            print('band',j,'[',tj,tn,']','pre',2*tj<F(n),'highneg',2*tj>=F(n) and Bj<0,'H',sorted(H),'h',h,'sig',sig,'Aj',Aj,'Bj',Bj,'cnt',cnt)
            if 2*tj>=F(n) and Bj<0:
                for c in comps:
                    print('  share C',c,F(cnt[c],h),'Ashare',Apre[c]/A if A else None)
