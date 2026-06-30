"""Gate Codex 418 SINGLETON-CORE SIGN THEOREM on the full battery (PURE form, no relaxed-invariant decoration):
     min_k Tail_k(P) < 0  ==>  min_i H_i(P) < 0      (equiv: all H_i>=0 ==> Tail_k>=0 for all k).
   Tail_k via existing _layer_gate.Zr_row length-threshold Z[r]; H_i via _singleton_core.Hi_and_best.
   Enumerate ALL connected-B max cuts where feasible (the Tail<0 rows live on NON-gamma-min cuts);
   for large families use gamma-min supplied cuts (Tail>=0, exercises the contrapositive's no-port end).
   Exact Fraction.  Usage: python _singleton_sign_battery.py <family>
     families: theta | blowups | chains | grotzsch | cen11 | bigsupplied
"""
import sys, subprocess, itertools
from fractions import Fraction as F
import _crux_extract as cx
from _singleton_core import ell_map, Hi_and_best
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, mycielski
from _Klocal_gate import glued_c5_chain

def scan_cut(tag,n,adj,side,Lam,acc):
    if not Bconn(n,adj,side): return
    st=struct_for_side(n,adj,side)
    if st is None: return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    if not M: return
    em0=ell_map(n,adj,side)
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f]: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            minTail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
            L=len(P)
            minH=None; Hs=[]
            for i in range(L):
                Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                Hs.append(Hi)
                if Hi is None: continue
                if minH is None or Hi<minH: minH=Hi
            # endpoint ports H_0, H_{L-1}
            ends=[h for h in (Hs[0],Hs[L-1]) if h is not None]
            minEnd=min(ends) if ends else None
            # endpoint MAGNITUDE theorem (Codex 421): TailMin >= H0^- + Hlast^-,  H_i^-=min(H_i,0), None->0
            H0m = min(Hs[0],0) if Hs[0] is not None else 0
            Hlm = min(Hs[L-1],0) if Hs[L-1] is not None else 0
            magrhs = H0m + Hlm
            if minTail < magrhs:
                acc['magfail']+=1
                if acc['magex'] is None: acc['magex']=(tag,n,''.join(map(str,side)),f,tuple(P),str(minTail),str(Hs[0]),str(Hs[L-1]))
            mgn = minTail - magrhs
            if acc['magmin'] is None or mgn<acc['magmin']: acc['magmin']=mgn
            acc['rows']+=1
            if minTail<0:
                acc['neg']+=1
                if minH is None or minH>=0:
                    acc['fail']+=1
                    if acc['ex'] is None: acc['ex']=(tag,n,''.join(map(str,side)),f,tuple(P),str(minTail),str(minH))
                else:
                    acc['ok']+=1
                # endpoint version
                if minEnd is None or minEnd>=0:
                    acc['efail']+=1
                    if acc['eex'] is None: acc['eex']=(tag,n,''.join(map(str,side)),f,tuple(P),str(minTail),str(Hs[0]),str(Hs[L-1]),[str(h) for h in Hs])
                else:
                    acc['eok']+=1
                if acc['minH_on_neg'] is None or (minH is not None and minH<acc['minH_on_neg']):
                    acc['minH_on_neg']=minH

def allmaxcut_family(tag,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    Lam=len(E)*n*n+1
    mc,cuts=cx.all_max_cuts(n,adj,E)
    for side in cuts: scan_cut(tag,n,adj,side,Lam,acc)

def gmins_family(tag,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    Lam=len(E)*n*n+1
    _,cuts=gmins(n,E)
    for side in cuts: scan_cut(tag,n,adj,side,Lam,acc)

def run(family,acc):
    if family=="theta":
        for g6 in ["H?AFBo]"]:
            n,E=dec(g6); allmaxcut_family("thw_%s"%g6,n,E,acc)
    elif family=="blowups":
        for sizes in [(2,1,2,1,2),(2,1,2,1,1),(2,2,2,1,1),(1,1,1,1,1),(2,1,1,1,1),(3,1,1,1,1),(2,2,1,1,1)]:
            nn,EE=odd_blowup(5,list(sizes))
            if nn<=12: allmaxcut_family("C5%s"%(sizes,),nn,EE,acc)
    elif family=="chains":
        for q in [2,3]:
            n,E,side=glued_c5_chain(q)
            if n<=15: allmaxcut_family("chain_q%d"%q,n,E,acc)
    elif family=="grotzsch":
        grN,grE=mycielski(5,Cn(5)); allmaxcut_family("Grotzsch",grN,grE,acc)  # N=11, 2^10 cuts
    elif family=="cen11":
        for g6 in subprocess.run([GENG,'-tc','11'],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); allmaxcut_family("cen11",n,E,acc)
    elif family=="cen10":
        for nn in range(5,11):
            for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
                n,E=dec(g6); allmaxcut_family("cen%d"%nn,n,E,acc)
    elif family=="bigsupplied":
        # gamma-min supplied cuts on large families: Tail>=0 expected (no-port end of contrapositive)
        grN,grE=mycielski(5,Cn(5)); m2N,m2E=mycielski(grN,grE)  # Myc(Grotzsch) N=23
        gmins_family("MycGrotzsch_N23",m2N,m2E,acc)
        for q in range(2,12):
            n,E,side=glued_c5_chain(q)
            adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            if Bconn(n,adj,side): scan_cut("chain_q%d"%q,n,adj,side,len(E)*n*n+1,acc)
    elif family.startswith("rand:"):
        import random
        from _bdef_construct import is_triangle_free
        _,seed,count,maxn=family.split(":"); seed=int(seed); count=int(count); maxn=int(maxn)
        rng=random.Random(seed); made=0; tries=0
        while made<count and tries<count*200:
            tries+=1
            nn=rng.randint(8,maxn)
            if nn>12: continue   # all_max_cuts 2^(n-1) feasibility
            p=rng.uniform(0.16,0.40)
            E=[(a,b) for a in range(nn) for b in range(a+1,nn) if rng.random()<p]
            if not E or not is_triangle_free(nn,E): continue
            adj=[set() for _ in range(nn)]
            for a,b in E: adj[a].add(b); adj[b].add(a)
            if any(len(adj[v])==0 for v in range(nn)): continue
            made+=1
            allmaxcut_family("rand_s%d_%d"%(seed,made),nn,E,acc)
        acc['rand_made']=made
    else:
        print("unknown family",family); sys.exit(2)

def main():
    family=sys.argv[1] if len(sys.argv)>1 else "theta"
    acc=dict(rows=0,neg=0,ok=0,fail=0,ex=None,minH_on_neg=None,eok=0,efail=0,eex=None,
             magfail=0,magex=None,magmin=None)
    run(family,acc)
    print("FAMILY=%s rows=%d  Tail<0 rows=%d"%(family,acc['rows'],acc['neg']))
    print("  ALL-i SIGN THEOREM (Tail<0 => minH<0): ok=%d fail=%d %s"%(acc['ok'],acc['fail'],acc['ex'] or ''))
    print("  ENDPOINT SIGN THEOREM (Tail<0 => min(H0,Hlast)<0): ok=%d fail=%d %s"%(acc['eok'],acc['efail'],acc['eex'] or ''))
    print("  ENDPOINT MAGNITUDE (TailMin >= H0^- + Hlast^-): fail=%d  minmargin=%s %s"%(acc['magfail'],str(acc['magmin']),acc['magex'] or ''))
    print("  min(minH) over Tail<0 rows =",acc['minH_on_neg'])
    print("  VERDICT_%s: %s"%(family,"PASS" if acc['fail']==0 and acc['efail']==0 and acc['magfail']==0 else "FAIL"))

if __name__=="__main__":
    main()
