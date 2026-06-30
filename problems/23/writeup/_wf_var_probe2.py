"""Fast structural probe of the variance inequality sub-lemmas. EXACT Fraction.
Mycielskians + blow-ups + small census N<=9. Tests several candidate upper bounds on var_f."""
import subprocess, itertools
from fractions import Fraction as F
from _h import dec, GENG, bdist_restr
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import mycielski, Cn

def per_side(n, adj, s):
    st=struct_for_side(n,adj,s)
    if st is None: return []
    M,ell,T,mu,cyc=st
    S=[F(0)]*n; pf={}
    for g in M:
        Ps=cyc[g]; k=len(Ps); d={}
        for P in Ps:
            for v in P: d[v]=d.get(v,F(0))+F(1,k)
        pf[g]=d
        for v,pv in d.items(): S[v]+=pv
    out=[]
    for f in M:
        if len(cyc[f])<2: continue
        d=pf[f]; ll=sum(d.values()); row=sum(d[v]*S[v] for v in d)
        mean=row/ll; var=sum(d[v]*(S[v]-mean)**2 for v in d)
        Smax=max(S[v] for v in d); Smin=min(S[v] for v in d)
        bd=ll*(Smax-mean)*(mean-Smin)
        cand=ll*(F(n)-mean)*mean
        target=F(n)*(F(n)-row)
        out.append(dict(n=n,f=f,ll=ll,row=row,var=var,mean=mean,target=target,
                        Smax=Smax,Smin=Smin,
                        S_le_N_all=all(sv<=n for sv in S),
                        S_le_N_supp=all(S[v]<=n for v in d),
                        BD_var=(var<=bd), BD_le_target=(bd<=target),
                        cand_le_var=(var<=cand), cand_le_target=(cand<=target),
                        row_le_N=(row<=n)))
    return out

def runset(name,n,E,acc):
    adj,cuts=gmins(n,E)
    for s in cuts:
        for r in per_side(n,adj,s):
            for k in ['S_le_N_all','S_le_N_supp','BD_var','BD_le_target','cand_le_var','cand_le_target','row_le_N']:
                acc.setdefault(k,[0,0]); acc[k][1]+=1; acc[k][0]+=(1 if r[k] else 0)
                if not r[k]:
                    acc.setdefault('FF',{}); acc['FF'].setdefault(k,(name,r['f'],str(r['row']),str(r['var'])))
            acc.setdefault('mneg',[0,0]); acc['mneg'][1]+=1
            if r['target']-r['var']<0: acc['mneg'][0]+=1
            if r['Smax']>acc.get('SmaxN',F(0)): acc['SmaxN']=r['Smax']; acc['SmaxN_n']=n; acc['SmaxN_nm']=name

def blowup(parts):
    m=len(parts); off=[0]*(m+1)
    for i in range(m): off[i+1]=off[i]+parts[i]
    nn=off[m]; EE=[]
    for i in range(m):
        j=(i+1)%m
        for a in range(off[i],off[i+1]):
            for b in range(off[j],off[j+1]): EE.append((min(a,b),max(a,b)))
    return nn,EE

if __name__=="__main__":
    acc={}
    sets=[("Grotzsch",)+mycielski(5,Cn(5)),
          ("M(C7)",)+mycielski(7,Cn(7)),
          ("M(C9)",)+mycielski(9,Cn(9)),
          ("M(C11)",)+mycielski(11,Cn(11)),
          ("M(Grotzsch)N23",)+mycielski(*mycielski(5,Cn(5))),
          ("C5[2]",)+blowup([2,2,2,2,2]),
          ("C5[3]",)+blowup([3,3,3,3,3]),
          ("C5unbal",)+blowup([1,5,2,2,5]),
          ("C7unbal",)+blowup([1,4,2,4,2,4,2]),
          ("C5[1,6,2,2,6]",)+blowup([1,6,2,2,6]),
          ("C5[1,48,6,8,48]",)+blowup([1,48,6,8,48]),
          ("C7[3x7]",)+blowup([3]*7)]
    for it in sets:
        runset(it[0],it[1],it[2],acc); print("done",it[0],flush=True)
    for nn in range(7,10):
        outg=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); runset(g6,n,E,acc)
        print("done census",nn,flush=True)
    print("\n=== RESULTS (pass/total) ===")
    for k in ['S_le_N_all','S_le_N_supp','BD_var','BD_le_target','cand_le_var','cand_le_target','row_le_N','mneg']:
        print(f"  {k}: {acc.get(k)}")
    print("  worst Smax =", acc.get('SmaxN'), " at n=", acc.get('SmaxN_n'), acc.get('SmaxN_nm'))
    print("  FIRST FAILS:", acc.get('FF'))
