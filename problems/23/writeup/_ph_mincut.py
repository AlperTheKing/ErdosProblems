"""Diagnose the PH min-cut on failing graphs (Step-2). SELF-CONTAINED (the _ph_*.py modules run their census on
import). Settles (a) unfaithful-shadow vs (b) prefix-defect genuinely short, by dumping per-atom two-sided shadows."""
from fractions import Fraction as F
from census_GPI import dec, maxcut_all, gmin, geos

def loads(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    Bset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]!=side[v])
    Mset=set((min(u,v),max(u,v)) for u in range(n) for v in adj[u] if side[u]==side[v])
    T=[F(0)]*0; T=[F(0) for _ in range(n)]; cyc={}
    for f in M:
        Ps=geos(adj,side,f[0],f[1]); cyc[f]=Ps; nf=len(Ps)
        if nf==0: return None
        sh=F(ell[f],nf)
        for P in Ps:
            for v in P: T[v]+=sh
    Uover=sum((t-n) for t in T if t>n); Uunder=sum((n-t) for t in T if t<n)
    return dict(n=n,adj=adj,side=side,M=M,ell=ell,Bset=Bset,Mset=Mset,T=T,cyc=cyc,Uover=Uover,Uunder=Uunder,G=G)

def max_obstruction(n,adj,side,M,C):
    Cset=set(C); K=[v for v in range(n) if v not in Cset]; idx={v:i for i,v in enumerate(K)}; m=len(K); kset=set(K)
    Be=[(u,v) for u in K for v in adj[u] if v>u and v in kset and side[u]!=side[v]]
    Mp=[(a,b) for (a,b) in M if a in kset and b in kset]
    best=0; arg=set()
    for mask in range(1<<m):
        dM=sum(1 for (u,v) in Mp if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        dB=sum(1 for (u,v) in Be if ((mask>>idx[u])&1)!=((mask>>idx[v])&1))
        if dM-dB>best: best=dM-dB; arg=set(u for u in K if (mask>>idx[u])&1)
    return best,arg

def touched(P,D,Bset,Mset):
    Ps=set(P); out=set()
    for (u,v) in Bset|Mset:
        if u in Ps and v in D: out.add(v)
        elif v in Ps and u in D: out.add(u)
    return out

def shadows2(info,C,j):
    n=info['n']; M=info['M']; Bset=info['Bset']; Mset=info['Mset']; T=info['T']
    Cset=set(C); R=set(x for x in range(n) if x not in Cset)
    eta,S=max_obstruction(n,info['adj'],info['side'],M,C); RmS=R-S
    Lj=set(C[:j+1]); CmL=set(C[j+1:]); Rj=set(C[j:]); CmR=set(C[:j])
    shL=touched(CmL,S,Bset,Mset)|touched(Lj,RmS,Bset,Mset)
    shR=touched(CmR,S,Bset,Mset)|touched(Rj,RmS,Bset,Mset)
    return set(z for z in shL if T[z]<n), set(z for z in shR if T[z]<n), eta, S

def diag(g6):
    n,E=dec(g6); info=loads(n,E); N=n
    T=info['T']; M=info['M']; ell=info['ell']; cyc=info['cyc']; G=info['G']
    print(f"\n=== {g6} N={n} Gamma={G} deficit={n*n-G} | Uover={float(info['Uover']):.3f} Uunder={float(info['Uunder']):.3f} COUPLE={info['Uover']<=n*n-G} ===")
    under=[(z,float(N-T[z])) for z in range(n) if T[z]<N]
    over=[(z,float(T[z]-N)) for z in range(n) if T[z]>N]
    print(f"  overloaded (z,T-N): {over}")
    print(f"  underloaded sinks (z,u=N-T): {under}  total={sum(u for _,u in under):.3f}  demand=2Uover={2*float(info['Uover']):.3f}")
    atoms=[]
    for f in M:
        Ps=cyc[f]; nf=len(Ps)
        for C in Ps:
            for j,w in enumerate(C):
                if T[w]>N:
                    m=float((T[w]-N)*F(ell[f],nf)/T[w])
                    shL,shR,eta,S=shadows2(info,C,j)
                    atoms.append(dict(w=w,C=tuple(C),j=j,m=m,shL=shL,shR=shR,eta=eta,S=S))
    eL=sum(1 for a in atoms if not a['shL']); eR=sum(1 for a in atoms if not a['shR'])
    print(f"  #atoms={len(atoms)} | EMPTY shL:{eL} EMPTY shR:{eR}  (empty side => that mass cannot route => PH-as-built infeasible)")
    for a in atoms:
        capL=sum(float(N-T[z]) for z in a['shL']); capR=sum(float(N-T[z]) for z in a['shR'])
        flag='  <<EMPTY' if (not a['shL'] or not a['shR']) else ''
        print(f"   w={a['w']} C={a['C']} j={a['j']} eta={a['eta']} S={sorted(a['S'])} m={a['m']:.3f} shL={sorted(a['shL'])}(c{capL:.2f}) shR={sorted(a['shR'])}(c{capR:.2f}){flag}")

if __name__=="__main__":
    for g6 in ["I?BD@g]Qo","J?AADagROl?"]:
        diag(g6)
