"""SOS probe 3: run the crux-(A) pure-SOS certificate on the HIGH-DISPERSION battery
(Mycielskians, two-lane) where E_0<0 is supposed to occur, using the SAME
struct_for_side + gmins pipeline as the crux verification.

Pure-SOS certificate to falsify:
   (PSOS)  delta*L^2 + sum_i (h_i - m)^2  <=  (L/5)(N^2 - Gamma),   m=S/L.
This is STRICTLY STRONGER than (A) wherever E_0<=0, and is E_0-free (no endpoint term).
If it survives the E_0<0 families, it proves (A) on them WITHOUT any switch/coarea.
We ALSO report E_0 to confirm whether these families actually realize E_0<0.
"""
import subprocess
from fractions import Fraction as F
from collections import deque
from _trunc_verify import chi_profile as endpt_chi
from _h import GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def cycle(n): return n,[(i,(i+1)%n) for i in range(n)]
def mycielskian(n,E):
    # vertices 0..n-1 original, n..2n-1 shadows, 2n apex
    M=2*n+1; EE=list(E)
    for a,b in E:
        EE.append((a,n+b)); EE.append((b,n+a))
    for i in range(n): EE.append((n+i,2*n))
    return M,EE
def gen_mycielskian(n,E,r):
    cn,cE=n,E
    for _ in range(r): cn,cE=mycielskian(cn,cE)
    return cn,cE

def two_lane(L):
    # x-path x0..x_{L-1}, two lanes A,B each a path, connect to make C5-blowup-like.
    # Use the team's odd_blowup of a long odd cycle as a stand-in high-dispersion family.
    from _wf_deficit_farkas import odd_blowup
    return odd_blowup(L,[1]*L)

def rows_for(n,E,label,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception as ex:
        print("  [%s] gmins failed: %s"%(label,ex)); return
    nc=0
    for side in cuts:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        N=F(n); Gamma=sum(T)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]
                S=sum(h); m=S/L
                prods=[h[i]*h[(i+1)%L] for i in range(L)]
                q=min(prods); delta=(S/L)**2 - q
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for rr in range(n): chiP[rr]+=ch[rr]
                E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
                R=F(L,5)*(N*N-Gamma)
                SOS=sum((hi-m)**2 for hi in h)
                lhsA=E0+delta*L*L
                lhsPSOS=delta*L*L+SOS
                nc+=1; acc['rows']+=1
                if E0<0: acc['e0neg']+=1
                if lhsA>R:
                    acc['Afail']+=1
                if lhsPSOS>R:
                    acc['PSOSfail']+=1
                    if acc['PSOSworst'] is None or (R>0 and lhsPSOS/R>acc['PSOSworst'][0]):
                        acc['PSOSworst']=(lhsPSOS/R if R>0 else F(99),label,L,str(E0),str(delta*L*L),str(SOS),str(R))
                # track worst PSOS ratio overall (even when <1)
                if R>0:
                    rr2=lhsPSOS/R
                    if acc['PSOSmaxratio'] is None or rr2>acc['PSOSmaxratio'][0]:
                        acc['PSOSmaxratio']=(rr2,label,L,str(E0),str(SOS),str(R))
                if E0<0 and acc['e0neg_ex'] is None:
                    acc['e0neg_ex']=(label,L,str(E0),str(delta*L*L),str(SOS),str(R),str(lhsA),str(lhsPSOS))
    print("  [%s] N=%d cuts=%d rows=%d"%(label,n,len(cuts),nc))

def main():
    acc=dict(rows=0,e0neg=0,Afail=0,PSOSfail=0,PSOSworst=None,PSOSmaxratio=None,e0neg_ex=None)
    fams=[]
    fams.append(("M(C5)=Grotzsch N=11",)+mycielskian(*cycle(5)))
    fams.append(("M(C7) N=15",)+mycielskian(*cycle(7)))
    fams.append(("M(C9) N=19",)+mycielskian(*cycle(9)))
    fams.append(("M(C11) N=23",)+mycielskian(*cycle(11)))
    for L in (7,9,11):
        n,E=two_lane(L); fams.append(("C%d-blowup-unit N=%d"%(L,n),n,E))
    for label,n,E in fams:
        rows_for(n,E,label,acc)
    print("="*60)
    print("TOTAL rows=%d  rows with E0<0: %d"%(acc['rows'],acc['e0neg']))
    print("(A) violations: %d"%acc['Afail'])
    print("(PSOS) delta*L^2+sum(h_i-m)^2 <= (L/5)(N^2-Gamma): violations=%d"%acc['PSOSfail'])
    if acc['PSOSworst']:
        w=acc['PSOSworst']; print("   PSOS WORST VIOLATION ratio=%.5f [%s] L=%s E0=%s deltaL2=%s SOS=%s R=%s"%(float(w[0]),w[1],w[2],w[3],w[4],w[5],w[6]))
    if acc['PSOSmaxratio']:
        w=acc['PSOSmaxratio']; print("   PSOS max ratio (incl <1)=%.5f [%s] L=%s E0=%s SOS=%s R=%s"%(float(w[0]),w[1],w[2],w[3],w[4],w[5]))
    if acc['e0neg_ex']:
        print("   example E0<0 row:",acc['e0neg_ex'])
    else:
        print("   NO E0<0 row found on this battery.")

if __name__=="__main__":
    main()
