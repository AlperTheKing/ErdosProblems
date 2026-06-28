"""Exact census scan + targeted constructions for the WORST Q-only K-component (boundary-deficit lemma).
Finds: minimum slack (deficit-dB) over Q-only K-components carrying a bad edge, minimum deficit, any violation,
any critical (deficit=0, O nonempty) Q-only component. EXACT Fraction throughout.
Run from E:/Projects/ErdosProblems/problems/23/writeup."""
from fractions import Fraction as F
import subprocess
from _h import dec, GENG, loads
from _bdef_construct import build_K_T, Kcomponents, analyze

def scan_one(info):
    """Return list of (kind, size, deficit, dB, mass, critical, violation) for Q-only comps carrying a bad edge,
    plus overall worst-slack record."""
    K,T,M,ell,n=build_K_T(info); N=n
    O=set(v for v in range(n) if T[v]>N)
    Bset=info['Bset']
    comps=Kcomponents(K,n)
    res=[]
    for C in comps:
        Cs=set(C)
        if Cs & O: continue
        badC=[f for f in M if f[0] in Cs and f[1] in Cs]
        if not badC: continue  # only bad-carrying Q-only comps matter for the lemma's force
        mass=sum(T[v] for v in C)
        deficit=F(N*len(C))-mass
        dB=sum(1 for (a,b) in Bset if (a in Cs)^(b in Cs))
        res.append((len(C),deficit,dB,mass,len(O)>0 and deficit==0,deficit<dB,tuple(C)))
    return res, len(O)>0

def run(Nmin,Nmax,stride=1,limit=None):
    global_min_slack=None; gms_w=None
    global_min_deficit=None; gmd_w=None
    any_violation=[]; any_critical=[]
    nontriv_with_O=0  # Q-only bad-carrying comps that coexist with nonempty O
    total_qcomp=0
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        out=out[::stride]
        if limit: out=out[:limit]
        cnt=0; fails=0; nm=None
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            cnt+=1
            res,hasO=scan_one(info)
            for (sz,deficit,dB,mass,crit,viol,C) in res:
                total_qcomp+=1
                if hasO: nontriv_with_O+=1
                slack=deficit-dB
                if global_min_slack is None or slack<global_min_slack:
                    global_min_slack=slack; gms_w=(g6,n,sz,float(deficit),dB,hasO,C)
                if global_min_deficit is None or deficit<global_min_deficit:
                    global_min_deficit=deficit; gmd_w=(g6,n,sz,float(deficit),dB,hasO)
                if viol: any_violation.append((g6,n,sz,float(deficit),dB,C)); fails+=1
                if crit: any_critical.append((g6,n,sz,float(deficit),dB,C))
                if nm is None or slack<nm: nm=slack
        print(f"  N={nn}(str{stride}): cfg={cnt} bad-Q-comps so far... fails={fails} minslack_thisN={float(nm) if nm is not None else 'na'}",flush=True)
    print(f"\nSUMMARY N={Nmin}..{Nmax} stride={stride}:")
    print(f"  total bad-carrying Q-only comps = {total_qcomp}; of those coexisting with O nonempty = {nontriv_with_O}")
    print(f"  GLOBAL min slack (deficit-dB) = {float(global_min_slack) if global_min_slack is not None else 'na'} @ {gms_w}")
    print(f"  GLOBAL min deficit = {float(global_min_deficit) if global_min_deficit is not None else 'na'} @ {gmd_w}")
    print(f"  VIOLATIONS = {len(any_violation)}  {any_violation[:5]}")
    print(f"  CRITICAL (deficit=0, O nonempty) = {len(any_critical)}  {any_critical[:5]}")

if __name__=="__main__":
    import sys
    a=sys.argv[1:]
    Nmin=int(a[0]) if len(a)>0 else 5
    Nmax=int(a[1]) if len(a)>1 else 12
    stride=int(a[2]) if len(a)>2 else 1
    print(f"=== exact census scan N={Nmin}..{Nmax} stride={stride} ===")
    run(Nmin,Nmax,stride)
