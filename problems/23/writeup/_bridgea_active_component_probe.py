"""Exact gate: high-negative BRIDGE-A bands have a unique K-component, and every prehalf positive-bank superlevel lies in that same component.
This would make monotone component-share dominance immediate.
"""
import subprocess, sys
from fractions import Fraction as F
from _h import dec,GENG,Bconn
from _stark1 import gmins
from _satzmu_conn import struct_for_side,kcomponents
from _bdef_construct import mycielski, Cn, union_disjoint
from _verify_two_lane import build_two_lane
from _wf_lrsbreak_0 import build_k_lane
from _wf_lrsbreak_0c import greedy_chords

def boundary(n,adj,side,H):
    dB=dM=0
    for u in H:
        for v in adj[u]:
            if v in H: continue
            if side[u]!=side[v]: dB+=1
            else: dM+=1
    return dB,dM

def chk(name,n,adj,side,acc):
    if not Bconn(n,adj,side): return True
    st=struct_for_side(n,adj,side)
    if not st: return True
    M,ell,T,mu,cyc=st
    if not M: return True
    eta=F(n*n,25)-len(M)
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    pre=[]; high=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        comps=set(cid[v] for v in H)
        if 2*tj<F(n) and wj*(F(n)+eta-tj-tn)>0:
            pre.append((j,tj,tn,H,comps))
        if 2*tj>=F(n):
            h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
            Bj=wj*(25*(F(n)+eta-tj-tn)*h - F(n)*sig)
            if Bj<0:
                high.append((j,tj,tn,H,comps,Bj))
    for hj,htj,htn,HH,hcomps,Bj in high:
        acc['high']+=1
        if len(hcomps)!=1:
            acc['viol']+=1
            print('FAIL high multi',name,''.join(map(str,side)),n,len(M),hj,str(htj),str(htn),sorted(HH),hcomps,str(Bj))
            return False
        c=next(iter(hcomps))
        for pj,ptj,ptn,PH,pcomps in pre:
            acc['rows']+=1
            if not pcomps <= {c}:
                acc['viol']+=1
                print('FAIL pre not same comp',name,''.join(map(str,side)),n,len(M),'high',hj,str(htj),str(htn),'hc',c,'pre',pj,str(ptj),str(ptn),'precomps',pcomps,'PH',sorted(PH),'HH',sorted(HH))
                return False
    return True

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
    nn,E=union_disjoint(b1,b2); n1=b1[0]; return nn,E+[(u,n1+v)]
def run_case(name,n,E,sides,acc):
    adj=adj_of(n,E) if (isinstance(E,list) and (not E or isinstance(E[0],tuple))) else E
    for side in sides:
        if not chk(name,n,adj,side,acc): return False
    return True

if __name__=='__main__':
    acc={'rows':0,'high':0,'viol':0}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L)
        if not run_case('two-lane-L%d'%L,n,E,[side],acc): sys.exit(0)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad)
        if not run_case('klane-L%dk%d'%(Ll,k),n,E,[side],acc): sys.exit(0)
    print('structured high',acc['high'],'rows',acc['rows'],flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            if not run_case('C%d[%d]'%(cyc,t),n,adj,cuts[:1],acc): sys.exit(0)
    for parts in [[2,2,2,2,3],[1,5,2,2,5],[1,4,2,4,2,4,2],[3,3,3,3,2],[1,3,2,2,3]]:
        n,E=blowup(parts)
        if n>26: continue
        adj,cuts=gmins(n,E)
        if not run_case('nu%s'%parts,n,adj,cuts[:1],acc): sys.exit(0)
    grot=mycielski(5,Cn(5)); mycg=mycielski(grot[0],grot[1])
    for nm,(nn,E) in [('Grotzsch',grot),('Myc(Grotzsch)',mycg),('M(C7)',mycielski(7,Cn(7))),('M(C9)',mycielski(9,Cn(9))),('C7|Grotzsch',bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0)),('C9|C9',bridge((9,Cn(9)),(9,Cn(9)),0,0)),('C5|C7',bridge((5,Cn(5)),(7,Cn(7)),0,0))]:
        adj,cuts=gmins(nn,E)
        if not run_case(nm,nn,adj,cuts[:2],acc): sys.exit(0)
    print('families high',acc['high'],'rows',acc['rows'],flush=True)
    for nn in range(7,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            if not run_case('cen%s'%g6,n,adj,cuts,acc): sys.exit(0)
        print('census N',nn,'high',acc['high'],'rows',acc['rows'],flush=True)
    print('NO FAIL high',acc['high'],'rows',acc['rows'])
