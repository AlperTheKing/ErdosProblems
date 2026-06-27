import subprocess, sys
sys.path.insert(0,"E:/Projects/ErdosProblems/problems/23/writeup")
from verify_iii_independent import dec, maxcut_all, gmin, min_overshoot_peel
GENG="E:/Projects/ErdosProblems/tools/nauty2_8_9/geng.exe"
# (ST): h*(A - 2(N-h))_+ + (H - Delta)_+  <=  (N^2 - Gamma)_+   at the min-overshoot peel.
def st_check(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:adj[a].add(b);adj[b].add(a)
    r=gmin(n,adj,maxcut_all(n,adj))
    if r is None: return None
    side,G,M,ell=r
    d=min_overshoot_peel(n,adj,side,M,ell)
    if d is None: return None
    h=d['h']; A=d['A']; H=d['H']; Delta=d['Delta']
    lhs=h*max(0,A-2*(n-h)) + max(0,H-Delta)
    rhs=max(0,n*n-G)
    return (G,n,lhs,rhs,lhs<=rhs)
def blow(t):
    n=5*t;E=[]
    for i in range(5):
        for a in range(t):
            for b in range(t):E.append((i*t+a,((i+1)%5)*t+b))
    return n,E
print("=== (ST) exact-check: h(A-2(N-h))_+ + (H-Delta)_+ <= (N^2-Gamma)_+ at min-overshoot peel ===")
print("--- C5[q] (deficit 0; LHS must be 0) ---")
for q in (2,3,4):
    r=st_check(*blow(q)); print(f"  C5[{q}] N={r[1]}: Gamma={r[0]} LHS={r[2]} RHS={r[3]} (ST) holds={r[4]}")
print("--- census N<=11 ---")
viol=0; tot=0; worst=None
for nn in range(5,12):
    out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
    nv=0; ncfg=0; exs=[]
    for g6 in out:
        n,E=dec(g6); r=st_check(n,E)
        if r is None: continue
        ncfg+=1; tot+=1
        if not r[4]:
            nv+=1; viol+=1
            if len(exs)<3: exs.append((g6,r[0],r[2],r[3]))
    print(f"  N={nn}: configs={ncfg} | (ST) violations={nv}",flush=True)
    for e in exs: print(f"     VIOL g6={e[0]} Gamma={e[1]} LHS={e[2]} RHS={e[3]}")
print(f"\nTOTAL N<=11: configs={tot}, (ST) violations={viol}")
print("If 0 violations => GPT round-8's conditional certificate (ST) is VALIDATED as the precise open target")
print("(the excess in A'/LEP is bounded by the Gamma-deficit; Gamma>=N^2 forces A'/LEP).")
