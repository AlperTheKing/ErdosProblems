"""Probe: does high-negative component share <= every prehalf-band component share?
If true, component-share dominance is a weighted-average corollary. Stops at first failure.
"""
import subprocess, sys
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side, kcomponents
from _stark1 import gmins
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
    if st is None: return True
    M,ell,T,mu,cyc=st
    if not M: return True
    m=len(M); eta=F(n*n,25)-m
    comp_map,find=kcomponents(n,cyc); cid=[find(u) for u in range(n)]; comps=sorted(set(cid))
    levs=sorted(set([F(0)]+[v for v in set(T) if v>0]))
    pre=[]; highneg=[]
    for j in range(len(levs)-1):
        tj=levs[j]; tn=levs[j+1]; wj=tn-tj
        H=set(v for v in range(n) if T[v]>tj)
        if not H: continue
        h=len(H); dB,dM=boundary(n,adj,side,H); sig=dB-dM
        cnt={c:0 for c in comps}
        for v in H: cnt[cid[v]]+=1
        if 2*tj<F(n):
            coef=wj*(F(n)+eta-tj-tn)
            if coef>0:
                pre.append((j,tj,tn,h,cnt))
        else:
            Bj=wj*(25*(F(n)+eta-tj-tn)*h - F(n)*sig)
            if Bj<0:
                highneg.append((j,tj,tn,h,cnt,Bj))
    for hj,htj,htn,hh,hcnt,Bj in highneg:
        for c in comps:
            lhs=F(hcnt[c],hh)
            for pj,ptj,ptn,ph,pcnt in pre:
                rhs=F(pcnt[c],ph)
                acc['rows']+=1
                if lhs>rhs:
                    print('FAIL',name,''.join(map(str,side)),n,m,'comp',c,'high',hj,str(htj),str(htn),hcnt[c],hh,'pre',pj,str(ptj),str(ptn),pcnt[c],ph,'lhs',lhs,'rhs',rhs)
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
    adj=adj_of(n,E) if (isinstance(E,list) and (not E or isinstance(E[0], tuple))) else E
    for side in sides:
        if not chk(name,n,adj,side,acc): return False
    return True

if __name__=='__main__':
    acc={'rows':0}
    for L in range(8,21,2):
        n,E,side,_=build_two_lane(L)
        if not run_case('two-lane-L%d'%L,n,E,[side],acc): sys.exit(0)
    for (Ll,k,gap) in [(12,4,6),(14,4,8),(16,5,8)]:
        bad=greedy_chords(Ll,k,gap); n,E,side,bad=build_k_lane(Ll,k,bad)
        if not run_case('klane-L%dk%d'%(Ll,k),n,E,[side],acc): sys.exit(0)
    print('structured rows',acc['rows'],flush=True)
    for cyc in (5,7,9):
        for t in range(1,6):
            n,E=blowup([t]*cyc)
            if n>26: continue
            adj,cuts=gmins(n,E)
            if not run_case('C%d[%d]'%(cyc,t),n,adj,cuts[:1],acc): sys.exit(0)
    for nn in range(7,12):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            if not run_case('cen%s'%g6,n,adj,cuts,acc): sys.exit(0)
        print('census N',nn,'rows',acc['rows'],flush=True)
    print('NO FAIL rows',acc['rows'])


