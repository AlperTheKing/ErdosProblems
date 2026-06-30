"""Targeted extremal adversaries for LRS family: C5[t]/C7[t] blowups, Mycielskians.
These are the known-tight / O-nonempty cases. CP-SAT exact max (n>22) or brute (n<=22),
all global-max cuts tested. Exact Fraction."""
import _wf_lrsbreak_4 as W

def blow_g(n,E,t):
    nn=n*t; EE=[]
    for (a,b) in E:
        for i in range(t):
            for j in range(t): EE.append((a*t+i,b*t+j))
    return nn,EE
def Cn(k): return [(i,(i+1)%k) for i in range(k)]
def mycielski(n,E):
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    N2=2*n+1; E2=list(E)
    for u in range(n):
        for v in adj[u]:
            if v>u: E2.append((u,n+v)); E2.append((v,n+u))
    for u in range(n): E2.append((n+u,2*n))
    return N2,E2

cases=[]
for t in (1,2,3,4):
    cases.append((f'C5[{t}]',)+blow_g(5,Cn(5),t))
for t in (1,2):
    cases.append((f'C7[{t}]',)+blow_g(7,Cn(7),t))
cases.append(('Myc(C5)=Grotzsch',)+mycielski(5,Cn(5)))
cases.append(('Myc(C7)',)+mycielski(7,Cn(7)))
cases.append(('Myc(Grotzsch)N23',)+mycielski(*mycielski(5,Cn(5))))

for name,n,E in cases:
    if not W.is_tri_free(n,E):
        print(name,'NOT trifree skip'); continue
    adj=[set() for _ in range(n)]
    for a,b in E: adj[a].add(b); adj[b].add(a)
    tmax = W.cpsat_maxcut(n,E)
    exactmax = (tmax is not None)
    if n<=23:
        bmax,cuts=W.all_maxcuts_bruteforce(n,adj,E)
        if exactmax: assert bmax==tmax, f'{name} cpsat{tmax}!=brute{bmax}'
        tmax=bmax; exactmax=True
    else:
        if not exactmax: print(name,'CPSAT not optimal, skip'); continue
        cuts=None
    nc=0
    if cuts is not None:
        for side in cuts:
            W.process_cut_exactmax(n,E,adj,side,tmax,name); nc+=1
    print(f'{name} N={n} |E|={len(E)} maxcut={tmax} (exact={exactmax}) #maxcuts={nc}',flush=True)

print('\n=== extremal results ===')
for k in ('B2','PATH','ROW','LRS'):
    g=W.GLOB[k]
    print(k,'worst margin',float(g[0]),'N=',g[3],'beta=',g[4],'Gamma=',g[5])
print('BREAKERS',len(W.BREAKERS))
for b in W.BREAKERS[:10]: print(b[0],float(b[1]),'N=',b[4])
