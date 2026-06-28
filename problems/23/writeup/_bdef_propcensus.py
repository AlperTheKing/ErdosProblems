"""Census of PROPER nontrivial Q-only K-components (C != V, O nonempty, C disjoint from O,
not a trivial T=0 isolated singleton). Report deficit, dB, local per-vertex charge, allT0,
and the tightest (min deficit-dB) witness."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads
from _bdef_theory import build, components, analyze_one

def run(Nmin,Nmax,stride=1):
    for nn in range(Nmin,Nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()[::stride]
        ncase=0; locfail=0; bdfail=0; mins=None
        n1sz=0  # singleton-with-T>0 count
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            B=build(info); O=B['O']; T=B['T']; N=B['N']; Bset=B['Bset']
            if not O: continue
            comps=components(B['K'],B['n'])
            for C in comps:
                Cs=set(C)
                if Cs&O: continue
                if len(C)==B['n']: continue
                d=analyze_one(B,C)
                allT0=all(T[v]==0 for v in C)
                if d['sz']==1 and allT0: continue
                if d['sz']==1: n1sz+=1
                deg_cross={v:0 for v in C}
                for (a,b) in Bset:
                    if (a in Cs)^(b in Cs):
                        x=a if a in Cs else b; deg_cross[x]+=1
                slack={v:F(N)-T[v] for v in C}
                local_ok=all(slack[v]>=deg_cross[v] for v in C)
                if not d['bd_ok']: bdfail+=1
                if not local_ok: locfail+=1
                s=d['deficit']-d['dB']
                if mins is None or s<mins[0]:
                    mins=(float(s),g6,tuple(C),float(d['deficit']),d['dB'],local_ok,allT0,d['nFC'])
                ncase+=1
        print(f"N={nn}(str{stride}): proper-nontriv-Qcomps={ncase} singleton(T>0)={n1sz} bd_FAIL={bdfail} LOCAL_FAIL={locfail} min(deficit-dB)={mins}",flush=True)

if __name__=="__main__":
    run(5,11,1)
