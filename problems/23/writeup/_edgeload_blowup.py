"""Does mu(e)<=N hold in the BLOW-UP / structured regime (the natural setting for #23 delta=0,
since d_mono is blow-up multilinear)? The small finite mu(e)>N cases (max 1.11N) may be finite artifacts.
Test max mu(e)/N on C(2k+1)[q] blowups, Mycielskians, and the binding graphs' blowups.
Also re-test (L) Sum_A T<=N*dB(A) there."""
from fractions import Fraction as F
from _h import dec, loads
from _edgeload import edge_loads

def Cblow(k,q):
    L=2*k+1; nn=L*q; E=[]
    for i in range(L):
        for a in range(q):
            for b in range(q):
                E.append((i*q+a, ((i+1)%L)*q+b))
    return nn,E

def report(label,n,E):
    if n>20: print(f"  {label:18} N={n}: skip (>20)"); return
    info=loads(n,E)
    if info is None: print(f"  {label:18} N={n}: skip"); return
    mu,Ev=edge_loads(info); N=n
    mx=max(mu.values()) if mu else F(0)
    # (L) check
    T=info['T']; o=[(T[z]-N if T[z]>N else F(0)) for z in range(n)]
    vals=sorted(set(v for v in o if v>0)); Lok=True
    for v in vals:
        A=set(z for z in range(n) if o[z]>=v)
        dB=sum(1 for (a,b) in info['Bset'] if (a in A)!=(b in A))
        if sum(T[z] for z in A) > N*dB: Lok=False
    print(f"  {label:18} N={n} | max mu(e)/N = {float(mx/N):.4f} | (L) holds: {Lok}")

if __name__=="__main__":
    print("=== max mu(e)/N on blowups (expect ->1 if clean in graphon regime) ===")
    for k in (2,3):
        for q in range(1,5):
            n,E=Cblow(k,q)
            if n<=20: report(f"C{2*k+1}[{q}]",n,E)
    print("=== Mycielskians ===")
    n,E=Cblow(2,1)
    # grotzsch via mycielski
    from _stress_sandwich import mycielski
    n2,E2=mycielski(n,E); report("Grotzsch",n2,E2)
    print("=== blow-ups of the binding graph J??CA?{{?]? ===")
    n,E=dec("J??CA?{{?]?")
    for q in (1,2):
        # blow up by q
        nn=n*q; EE=[]
        for (a,b) in E:
            for i in range(q):
                for j in range(q):
                    EE.append((a*q+i,b*q+j))
        report(f"J??CA[{q}]",nn,EE)
