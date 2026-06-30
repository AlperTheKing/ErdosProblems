"""HARDER stress of rho(O)<=N (Cycle-SM form). Bigger/odder families than _fan_stress: nonuniform C5/C7/C9/C11
blow-ups (random sizes, N up to ~40), single + DOUBLE bridged islands, separate-cycle attachments. For each:
enumerate part-respecting cuts (2^L), take max-cut value, gamma-min among them, verify LOCAL max (no single-vertex
improving flip), exact-test Cycle-SM per bad edge. ANY violation kills rho(O)<=N. Deterministic LCG sizes."""
from itertools import product
from fractions import Fraction as F
from _h import Bconn
from _satzmu_conn import struct_for_side

def cyc_edges(parts):
    L=len(parts); E=set()
    for i in range(L):
        j=(i+1)%L
        for a in parts[i]:
            for b in parts[j]: E.add((min(a,b),max(a,b)))
    return E

def build(sizes_list, bridges):
    # sizes_list: list of cycles (each a list of part sizes). bridges: list of (cycleIdx,partIdx, cycleIdx2,partIdx2)
    off=[]; parts_all=[]; cur=0; cyc_parts=[]
    for sizes in sizes_list:
        L=len(sizes); pl=[]
        for s in sizes:
            pl.append(list(range(cur,cur+s))); cur+=s
        cyc_parts.append(pl); parts_all.append(pl)
    n=cur; E=set()
    for pl in cyc_parts: E|=cyc_edges(pl)
    for (c1,p1,c2,p2) in bridges:
        a=cyc_parts[c1][p1][0]; b=cyc_parts[c2][p2][0]; E.add((min(a,b),max(a,b)))
    return n,sorted(E),cyc_parts

def cut_size(E,side): return sum(1 for x,y in E if side[x]!=side[y])
def local_max(n,adj,side):
    for v in range(n):
        same=sum(1 for w in adj[v] if side[w]==side[v]); diff=len(adj[v])-same
        if same>diff: return False
    return True
def cycle_sm(n,adj,side):
    st=struct_for_side(n,adj,side)
    if st is None: return None
    M,ell,T,mu,cyc=st
    if not M: return ('nobad',)
    worst=F(-1); viol=0
    for f in M:
        Ps=cyc[f]; nf=len(Ps); cnt={}
        for Pp in Ps:
            for v in Pp: cnt[v]=cnt.get(v,0)+1
        num=sum(F(c,nf)*T[v] for v,c in cnt.items()); den=F(n)*ell[f]
        r=num/den
        if r>worst: worst=r
        if num>den: viol+=1
    return ('ok',viol,worst,sum(T),max(T),len(M))

def test_config(sizes_list,bridges,acc,tag):
    n,E,cyc_parts=build(sizes_list,bridges)
    if n>40: return
    # part index list across all cycles
    flat_parts=[p for pl in cyc_parts for p in pl]
    L=len(flat_parts)
    if L>14: return   # keep 2^L enumerable
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    best=-1; cuts=[]
    for combo in product((0,1),repeat=L):
        side=[0]*n
        for pi,p in enumerate(flat_parts):
            for v in p: side[v]=combo[pi]
        c=cut_size(E,side)
        if c>best: best=c; cuts=[combo]
        elif c==best: cuts.append(combo)
    cand=[]
    for combo in cuts:
        side=[0]*n
        for pi,p in enumerate(flat_parts):
            for v in p: side[v]=combo[pi]
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        cand.append((sum(st[2]),side))
    if not cand: return
    gmin=min(c[0] for c in cand)
    for G,side in cand:
        if G!=gmin: continue
        if not local_max(n,adj,side): acc['notlm']+=1; continue
        res=cycle_sm(n,adj,side)
        if res is None or res[0]!='ok': continue
        _,viol,worst,Gam,maxT,m=res
        acc['tested']+=1
        if worst>acc['worst'][0]: acc['worst']=(worst,tag,n,str(Gam),str(maxT))
        if viol>0:
            acc['viol']+=1; acc['vlist'].append((tag,n,viol,str(worst),str(Gam),str(maxT)))

seed=98765
def rnd():
    global seed; seed=(1103515245*seed+12345)%(2**31); return seed

if __name__=="__main__":
    acc=dict(tested=0,viol=0,notlm=0,worst=(F(-1),'',0,'',''),vlist=[])
    configs=[]
    # single nonuniform cycles C5..C11
    for _ in range(120):
        L=[5,7,9,11][rnd()%4]
        sizes=[1+rnd()%7 for _ in range(L)]
        if sum(sizes)<=34: configs.append(([sizes],[],"C%d%s"%(L,sizes)))
    # double-island bridged fans (two cycles + 1 bridge)
    for _ in range(80):
        L1=[5,7][rnd()%2]; L2=[5,7][rnd()%2]
        s1=[1+rnd()%5 for _ in range(L1)]; s2=[1+rnd()%5 for _ in range(L2)]
        if sum(s1)+sum(s2)<=36 and L1+L2<=14:
            configs.append(([s1,s2],[(0,0,1,0)],"D[%s|%s]"%(s1,s2)))
    # structured killers + variants (center=1 fans)
    for c in [[3,9,1,9,3],[9,1,9,1,9],[5,5,1,5,5],[2,10,1,10,2],[1,11,1,11,1],
              [4,4,1,4,4,4,4],[6,1,6,1,6,1,6],[3,3,1,3,3,3,3,3,3]]:
        configs.append(([c],[],"K%s"%c))
    for tag_cfg in configs:
        sizes_list,bridges,tag=tag_cfg
        test_config(sizes_list,bridges,acc,tag)
    print("  configs tested(gamma-min,local-max)=%d  not-local-max=%d"%(acc['tested'],acc['notlm']))
    print("  CYCLE-SM (rho(O)<=N) violations=%d"%acc['viol'])
    w=acc['worst']
    print("  worst ratio=%s=%s @ %s N=%d Gamma=%s maxT=%s"%(str(w[0]),str(float(w[0]))[:7],w[1],w[2],w[3],w[4]))
    if acc['vlist']:
        print("  VIOLATIONS:")
        for d in acc['vlist'][:25]: print("    %s"%(d,))
    print("  === rho(O)<=N BIG STRESS %s ==="%("HOLDS" if acc['viol']==0 else "*** FAILS -- ROUTE A DEAD ***"))
