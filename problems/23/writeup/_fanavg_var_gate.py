"""Gate Codex's FAN-AVERAGING strengthening (block 140): variance inequality n*(n-row_f) >= var_f
restricted to NONUNIQUE rows (len(cyc[f])>=2). var_f=sum_v p_f(v)(S(v)-row_f/ell_f)^2. The global variance
died at the UNIQUE row K??CB@OBDOAp; restricting to nonunique may survive. Battery beyond Codex's N<=12 census:
census N<=11, Mycielskians N<=23 (ALL-nonunique -> the key test), glued islands, small balanced+unbalanced
blow-ups. Report worst margin + worst ratio (n-row)/var + first violation. Exact Fraction."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn, union_disjoint

def check(n, adj, s, first):
    st=struct_for_side(n,adj,s)
    if st is None: return 0,0,None,None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    nrows=0; nfail=0; wm=None; wr=None
    for f in M:
        if len(cyc[f])<2: continue   # NONUNIQUE only
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
        mean=row/ll; var=sum(d[v]*(S[v]-mean)**2 for v in d)
        margin=F(n)*(F(n)-row)-var
        nrows+=1
        if wm is None or margin<wm: wm=margin
        if var>0:
            ratio=(F(n)-row)/var
            if wr is None or ratio<wr: wr=ratio
        if margin<0:
            nfail+=1
            if first[0] is None: first[0]=(''.join(map(str,s)),f,str(row),str(ll),str(var),n)
    return nrows,nfail,wm,wr

def run(name,n,E,first):
    adj,cuts=gmins(n,E); R=Fl=0; wm=None; wr=None
    for s in cuts:
        r,f,m,rt=check(n,adj,s,first); R+=r; Fl+=f
        if m is not None and (wm is None or m<wm): wm=m
        if rt is not None and (wr is None or rt<wr): wr=rt
    return name,len(cuts),R,Fl,wm,wr

if __name__=="__main__":
    print("=== FAN-AVERAGING variance gate (nonunique rows): n(n-row)>=var (exact) ===",flush=True)
    first=[None]
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        R=Fl=0; wm=None; wr=None
        for g6 in outg:
            n,E=dec(g6); adj,cuts=gmins(n,E)
            for s in cuts:
                r,f,m,rt=check(n,adj,s,first); R+=r; Fl+=f
                if m is not None and (wm is None or m<wm): wm=m
                if rt is not None and (wr is None or rt<wr): wr=rt
        print(f"  census N={nn}: nonuniq-rows={R} FAILS={Fl} worst-margin={wm} worst-ratio(N-row)/var={wr}",flush=True)
    def bridge(b1,b2,u,v):
        n,E=union_disjoint(b1,b2); n1=b1[0]; return n, E+[(u, n1+v)]
    def blowup(parts):
        m=len(parts); off=[0]*(m+1)
        for i in range(m): off[i+1]=off[i]+parts[i]
        nn=off[m]; EE=[]
        for i in range(m):
            j=(i+1)%m
            for a in range(off[i],off[i+1]):
                for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
        return nn,EE
    extra=[("M(C7)",)+mycielski(7,Cn(7)),
           ("M(C9)",)+mycielski(9,Cn(9)),
           ("M(C11)",)+mycielski(11,Cn(11)),
           ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
           ("C7|brg|Grotzsch",)+bridge((7,Cn(7)),mycielski(5,Cn(5)),0,0),
           ("C9|brg|C9",)+bridge((9,Cn(9)),(9,Cn(9)),0,0),
           ("C5[2]",)+blowup([2,2,2,2,2]),
           ("C5[3]",)+blowup([3,3,3,3,3]),
           ("C5unbal",)+blowup([1,5,2,2,5]),
           ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
           ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6])]
    print("  [Mycielskians N<=23 / glued / blow-ups]: name cuts nonuniq-rows FAILS worst-margin worst-ratio",flush=True)
    for it in extra:
        print("   ",run(*it,first),flush=True)
    print(f"\n=== {'FIRST VIOLATION: '+str(first[0]) if first[0] else 'NO VIOLATION (fan-averaging variance holds on battery)'} ===",flush=True)
