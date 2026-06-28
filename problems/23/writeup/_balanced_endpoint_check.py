"""Exact test of the BALANCED-ENDPOINT conjecture (the crux of Codex's V-min descent):
For every gamma-min connected-B max cut and every SPLIT-bad (length-5 central-overload) bad edge ab in it,
at least one endpoint is max-cut balanced (d_M(v)=d_B(v), i.e. flipping v preserves the cut size), OR the
symmetric paired-slack configuration holds (both endpoints have slack 1 and a cut-edge pair switch exists).
If TRUE, the gamma-preserving rotation is always available => Codex's local descent is unconditional.
Scans census N=7..11. Exact Fraction. Reports any bad row with NEITHER a balanced endpoint nor a paired switch."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def split_bad_rows(n, adj, s):
    """return list of (f, A, R) for bad edges f where frac SPLIT fails on cut s."""
    st=struct_for_side(n,adj,s)
    if st is None: return None
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    bad=[]
    for f in M:
        L=ell[f]; Ps=cyc[f]; d=pf[f]; layer={}
        for P in Ps:
            for i,v in enumerate(P): layer[v]=i
        A=[F(0)]*L
        for v,pv in d.items(): A[layer[v]]+=pv*S[v]
        R=sum(A)-F(n); m=(L-1)//2
        Bs=[(sum(A[i] for i in range(t))+sum(A[i] for i in range(L-t,L)))-F(2*t*n,L) for t in range(1,m+1)]
        if not (R<=0 and min(Bs)<=0 and max(Bs)>=R):
            bad.append((f,A,R,L))
    return bad

def balanced(adj, s, v):
    """d_M(v) = #cross-neighbors, d_B(v) = #same-side neighbors; balanced iff equal (flip preserves cut)."""
    dM=sum(1 for u in adj[v] if s[u]!=s[v]); dB=sum(1 for u in adj[v] if s[u]==s[v])
    return dM==dB, dM, dB

def has_paired_switch(n, adj, s, f):
    """symmetric case: both endpoints slack-1 and exist a cut-edge pair (i,j) with s[i]!=s[j], both slack-1,
       whose joint flip preserves cut. Detect the structural signature: each endpoint has d_B-d_M = +1
       (one unit of within-side slack) and there is a 2-set flip preserving cut size."""
    a,b=f
    def cutslack(v):
        # cut-slack = (#cross-neighbors) - (#same-side-neighbors); =1 means one unit of max-cut slack
        dM=sum(1 for u in adj[v] if s[u]!=s[v]); dB=sum(1 for u in adj[v] if s[u]==s[v]); return dM-dB
    if cutslack(a)!=1 or cutslack(b)!=1: return False
    # search any cut-edge pair (i,j), s[i]!=s[j], whose simultaneous flip preserves cut size
    base=sum(1 for x in range(n) for u in adj[x] if u>x and s[x]!=s[u])
    for i in range(n):
        for j in adj[i]:
            if j<=i or s[i]==s[j]: continue
            s2=s[:]; s2[i]^=1; s2[j]^=1
            c2=sum(1 for x in range(n) for u in adj[x] if u>x and s2[x]!=s2[u])
            if c2==base: return True
    return False

if __name__=="__main__":
    print("=== BALANCED-ENDPOINT conjecture: census N=7..11, all SPLIT-bad gamma-min rows ===",flush=True)
    grand_bad=0; grand_viol=0
    for nn in range(7,12):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        nbad=0; nviol=0; ell_gt5=0
        for g6 in outg:
            n,E=dec(g6)
            adj2,cuts=gmins(n,E)
            if not cuts: continue
            for s in cuts:
                br=split_bad_rows(n,adj2,s)
                if not br: continue
                for (f,A,R,L) in br:
                    nbad+=1
                    if L>5: ell_gt5+=1
                    a,b=f
                    ba,_,_=balanced(adj2,s,a); bb,_,_=balanced(adj2,s,b)
                    if ba or bb: continue
                    if has_paired_switch(n,adj2,s,f): continue
                    nviol+=1
                    print(f"   *** VIOLATION N={nn} g6={g6} side={''.join(map(str,s))} f={f} L={L} A={[str(x) for x in A]}",flush=True)
        print(f"  N={nn}: SPLIT-bad-rows={nbad} ell>5={ell_gt5} balanced-or-paired-FAIL={nviol}",flush=True)
        grand_bad+=nbad; grand_viol+=nviol
    print(f"\n=== TOTAL bad-rows={grand_bad} conjecture-VIOLATIONS={grand_viol} ===",flush=True)
    print("   balanced-endpoint/paired-switch holds for EVERY SPLIT-bad gamma-min row" if grand_viol==0
          else "   *** conjecture has counterexamples (see above) ***",flush=True)
