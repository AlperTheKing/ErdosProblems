"""Measure worst-case ratio of DECOUPLED bound delta*L^2 <= (L/5)(N^2-Gamma)
on the same battery, plus the PSOS worst ratio, to quantify slack.
Lean battery (census 5..8 + key blowups + M(C5),M(C7)) for speed."""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins

def cycle(n): return n,[(i,(i+1)%n) for i in range(n)]
def mycielskian(n,E):
    M=2*n+1; EE=list(E)
    for a,b in E: EE.append((a,n+b)); EE.append((b,n+a))
    for i in range(n): EE.append((n+i,2*n))
    return M,EE

def run(label,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception: return
    for side in cuts:
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st; N=F(n); Gamma=sum(T)
        for f in M:
            L=ell[f]
            if L%2==0: continue
            for P in cyc[f]:
                if len(P)!=L: continue
                h=[T[P[i]]/N for i in range(L)]; S=sum(h); m=S/L
                q=min(h[i]*h[(i+1)%L] for i in range(L))
                delta=(S/L)**2-q
                R=F(L,5)*(N*N-Gamma)
                acc['rows']+=1
                if R>0:
                    dec_r=(delta*L*L)/R
                    if acc['dec_worst'] is None or dec_r>acc['dec_worst'][0]:
                        acc['dec_worst']=(dec_r,label,L)
                    if delta*L*L>R: acc['dec_fail']+=1

def main():
    acc=dict(rows=0,dec_worst=None,dec_fail=0)
    fams=[("thw",)+tuple(dec("H?AFBo]"))]
    for nn in range(5,9):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            fams.append(("cen%d"%nn,)+tuple(dec(g6)))
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),(2,1,2,1,3),(6,2,2,2,2),(5,4,3,2,2)]:
        fams.append(("C5%s"%(sizes,),)+tuple(odd_blowup(5,list(sizes))))
    fams.append(("M(C5)N11",)+mycielskian(*cycle(5)))
    fams.append(("M(C7)N15",)+mycielskian(*cycle(7)))
    for fam in fams: run(fam[0],fam[1],fam[2],acc)
    print("rows=%d"%acc['rows'])
    print("DECOUPLED delta*L^2<=(L/5)(N^2-Gamma): failures=%d"%acc['dec_fail'])
    w=acc['dec_worst']
    print("DECOUPLED worst ratio (delta*L^2)/(L/5)(N^2-Gamma) = %s ~%.5f at [%s] L=%s"%(w[0],float(w[0]),w[1],w[2]))

if __name__=="__main__": main()
