import sys
sys.path.insert(0,"E:/Projects/ErdosProblems/problems/23/writeup")
from verify_iii_independent import check
def myc(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E:adj[a].add(b);adj[b].add(a)
    E2=[(min(a,b),max(a,b)) for a,b in E];ap=2*n
    for u in range(n):
        for v in adj[u]:E2.append((min(u,n+v),max(u,n+v)))
    for u in range(n):E2.append((min(n+u,ap),max(n+u,ap)))
    return 2*n+1,sorted(set(E2))
def petersen():
    out=[(i,(i+1)%5) for i in range(5)];inn=[(5+i,5+((i+2)%5)) for i in range(5)]
    return 10,out+inn+[(i,5+i) for i in range(5)]
print("Independent (A')/(LEP)/(iii) min-overshoot check on M(Petersen) N=21 (high-chromatic, choice-essential)...",flush=True)
n,E=myc(*petersen())
r=check(n,E)
if r is None or (isinstance(r,tuple) and r and r[0]=='nopeel'):
    print("result:",r)
else:
    G,n2,iii,Ap,lep,tight,d=r
    print(f"M(Petersen): N={n} Gamma={G} N^2={n2*n2} Gamma>=N^2? {G>=n2*n2}")
    print(f"  min-overshoot peel: h={d['h']} mu={d['mu']} Delta={d['Delta']} L={d['L']} bound={d['bound']} ov={d['ov']}")
    print(f"  (iii) L<=bound: {iii} | (A') A={d['A']}<=2(N-h)={d['Abound']}: {Ap} | (LEP) H={d['H']}<=Delta={d['Delta']}: {lep}")
    print(f"  ALL THREE HOLD: {iii and Ap and lep}  (Step-2 reported L=75<=185, A=10<=32, H=0<=0)")
print("DONE M(Petersen)",flush=True)
