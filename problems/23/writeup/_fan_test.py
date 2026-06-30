"""URGENT: does the GPT-Pro/Codex C5-fan (nonuniform blowup 3,9,1,9,3, N=30) that breaks net_H<=3 ALSO break
my leg CYCLE-SM (rho(O)<=N)? Build Codex's exact construction; test on explicit sides S0,S1 via struct_for_side.
  Cycle-SM per bad edge:  Sum_v p_f(v) T(v) <= N*ell(f)   [<=> rho(O)<=N => Gamma<=N^2].
  net_H per high vtx:     net_H(v)=B_out-M_out on H={T>t}, 2t>=N.
Sanity vs Codex: S0 cut=77, |M|=10, Gamma=250, maxT=45, net_H(c)=18; S1 net_H(c)=0."""
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side, kcomponents

def build_fan(sizes=(3,9,1,9,3), sep_c5=True, bridge=True):
    # cyclic complete-bipartite blowup of C5 with given part sizes
    off=[0];
    for s in sizes: off.append(off[-1]+s)
    nfb=off[-1]            # first block vertex count
    parts=[list(range(off[i],off[i+1])) for i in range(5)]
    E=set()
    for i in range(5):
        j=(i+1)%5
        for a in parts[i]:
            for b in parts[j]: E.add((min(a,b),max(a,b)))
    n=nfb
    sepnodes=[]
    if sep_c5:
        base=n; sepnodes=[base+k for k in range(5)]
        for k in range(5):
            a=sepnodes[k]; b=sepnodes[(k+1)%5]; E.add((min(a,b),max(a,b)))
        n+=5
    if bridge and sep_c5:
        # bridge from an A4 vertex (not center) to a sep-C5 vertex
        a=parts[4][0]; b=sepnodes[1]; E.add((min(a,b),max(a,b)))
    return n,sorted(E),parts,sepnodes

def make_side(n,parts,sepnodes,fb_sides,sep_sides):
    side=[0]*n
    for i in range(5):
        for v in parts[i]: side[v]=fb_sides[i]
    for k,v in enumerate(sepnodes): side[v]=sep_sides[k]
    return side

def analyze(tag,n,E,side):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    bc=Bconn(n,adj,side)
    cut=sum(1 for x,y in E if side[x]!=side[y])
    st=struct_for_side(n,adj,side)
    if st is None:
        print("  %s: struct_for_side None (Bconn=%s cut=%d)"%(tag,bc,cut)); return
    M,ell,T,mu,cyc=st
    Gamma=sum(T)
    maxT=max(T) if T else F(0)
    # p_f, Cycle-SM
    Pf={}
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        Pf[f]={v:F(c,nf) for v,c in cnt.items()}
    csm_viol=0; csm_max=F(-1); csm_arg=None
    for f in M:
        num=sum(pv*T[v] for v,pv in Pf[f].items())
        den=F(n)*ell[f]
        r=num/den
        if r>csm_max: csm_max=r; csm_arg=(f,str(num),str(den))
        if num>den: csm_viol+=1
    # net_H worst
    levs=sorted(set([F(0)]+[t for t in set(T) if t>0]))
    netmax=-10**9; netarg=None
    for j in range(len(levs)-1):
        tj=levs[j]
        if 2*tj<F(n): continue
        H=set(v for v in range(n) if T[v]>tj)
        for v in H:
            B_out=sum(1 for w in adj[v] if w not in H and side[v]!=side[w])
            M_out=sum(1 for w in adj[v] if w not in H and side[v]==side[w])
            net=B_out-M_out
            if net>netmax: netmax=net; netarg=(j,v,str(T[v]))
    print("  %s: Bconn=%s cut=%d |M|=%d ellset=%s Gamma=%s maxT=%s"%(tag,bc,cut,len(M),sorted(set(ell.values())),Gamma,maxT))
    print("     CYCLE-SM: viol=%d  max ratio=%s=%s  arg=%s"%(csm_viol,str(csm_max),str(float(csm_max))[:7],csm_arg))
    print("     net_H max=%s @ %s   => rho(O)<=N %s"%(netmax,netarg,"HOLDS" if csm_viol==0 else "*** FAILS ***"))
    return csm_viol

if __name__=="__main__":
    n,E,parts,sep=build_fan()
    print("Fan N=%d, parts sizes=%s, sep=%s"%(n,[len(p) for p in parts],sep))
    # S0: fb sides (0,1,0,1,0) bad=A4-A0 ; sep alternating
    sepA=[0,1,0,1,0]   # C5 alternating, bad edge present
    s0=make_side(n,parts,sep,[0,1,0,1,0],sepA)
    s1=make_side(n,parts,sep,[1,0,0,1,0],sepA)   # bad=A1-A2
    analyze("S0(bad A4-A0)",n,E,s0)
    analyze("S1(bad A1-A2)",n,E,s1)
