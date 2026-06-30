"""DECISIVE SOS test for crux (A). Three exact-rational claims per row:

 (I)  E_0 == 0 on every gamma-min GLOBAL-max connected-B row?  (structural: endpoint flip neutral)
 (II) DELTA-SPLIT identity:  delta == [(S/L)^2 - mbar^2] + ((h_r-h_{r+1})/2)^2 ,  mbar=(h_r+h_{r+1})/2.
 (III) PSOS (the proposed certificate, E_0-free):
          delta*L^2 + sum_i (h_i - m)^2  <=  (L/5)(N^2 - Gamma),   m = S/L.
      and the WEIGHTED-SOS strengthening with the MAXIMAL constant c found earlier (~3.38):
          delta*L^2 + c*sum_i (h_i-m)^2 + E_0 <= (L/5)(N^2-Gamma).

Battery: census tri-free N=5..9 (ALL gmin cuts), C5[t] balanced+skew, glued C5-C7,
Mycielskians M(C5),M(C7),M(C9) (N<=19, gmins tractable).  Skips N=23 brute force.

Reports: #rows, #E0<0, #E0!=0, #(II) fail, #(III/PSOS) fail + worst ratio,
and the decoupling census: #rows with delta*L^2 > rhs (and there E0 must be <0)."""
import subprocess
from fractions import Fraction as F
from _trunc_verify import chi_profile as endpt_chi
from _wf_deficit_farkas import odd_blowup
from _h import dec, GENG
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _bdef_construct import Cn, union_disjoint

def cycle(n): return n,[(i,(i+1)%n) for i in range(n)]
def mycielskian(n,E):
    M=2*n+1; EE=list(E)
    for a,b in E: EE.append((a,n+b)); EE.append((b,n+a))
    for i in range(n): EE.append((n+i,2*n))
    return M,EE

def run_family(label,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    try: _,cuts=gmins(n,E)
    except Exception as ex:
        acc['skipped'].append((label,str(ex))); return
    rows=0
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
                q=min(prods); r=prods.index(q)
                delta=(S/L)**2 - q
                hr,hr1=h[r],h[(r+1)%L]; mbar=(hr+hr1)/2
                # (II) split identity
                split=((S/L)**2 - mbar*mbar)+((hr-hr1)/2)**2
                if split!=delta: acc['II_fail']+=1
                # E_0
                chiP=[0]*n
                for end in (P[0],P[-1]):
                    ch=endpt_chi(n,adj,side,end,M,n)
                    for rr in range(n): chiP[rr]+=ch[rr]
                E0=sum((2*rr+1)*chiP[rr] for rr in range(n))
                if E0<0: acc['E0neg']+=1
                if E0!=0: acc['E0nz']+=1
                R=F(L,5)*(N*N-Gamma)
                SOS=sum((hi-m)**2 for hi in h)
                # decoupling census
                if delta*L*L>R:
                    acc['disp_exceeds']+=1
                    if E0>=0: acc['disp_exceeds_E0nonneg']+=1
                # (III) PSOS
                lhsP=delta*L*L+SOS
                if lhsP>R:
                    acc['PSOS_fail']+=1
                if R>0:
                    rt=lhsP/R
                    if acc['PSOS_worst'] is None or rt>acc['PSOS_worst'][0]:
                        acc['PSOS_worst']=(rt,label,L,str(E0),str(SOS),str(R))
                # (A) itself
                if E0+delta*L*L>R: acc['A_fail']+=1
                # weighted-SOS with c (binding constant search): record min room/SOS
                room=R-E0-delta*L*L
                if SOS>0:
                    crow=room/SOS
                    if acc['cmax'] is None or crow<acc['cmax']:
                        acc['cmax']=crow; acc['cmax_at']=(label,L,str(room),str(SOS))
                rows+=1; acc['rows']+=1
    print("  [%s] N=%d cuts=%d rows=%d"%(label,n,len(cuts),rows))

def main():
    acc=dict(rows=0,E0neg=0,E0nz=0,II_fail=0,disp_exceeds=0,disp_exceeds_E0nonneg=0,
             PSOS_fail=0,PSOS_worst=None,A_fail=0,cmax=None,cmax_at=None,skipped=[])
    fams=[]
    fams.append(("thw",)+tuple(dec("H?AFBo]")))
    for nn in range(5,10):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            fams.append(("cen%d"%nn,)+tuple(dec(g6)))
    for sizes in [(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),(2,1,2,1,2),(3,2,3,2,3),
                  (2,1,2,1,3),(4,1,4,1,4),(5,1,5,1,5),(1,3,1,3,1),(5,4,3,2,2),(6,2,2,2,2)]:
        fams.append(("C5%s"%(sizes,),)+tuple(odd_blowup(5,list(sizes))))
    for sizes in [(2,2,2,2,2,2,2),(3,1,3,1,3,1,3)]:
        fams.append(("C7%s"%(sizes,),)+tuple(odd_blowup(7,list(sizes))))
    # glued C5-C7
    n5,E5=5,Cn(5); n7,E7=7,Cn(7); n,E=union_disjoint((n5,E5),(n7,E7)); E=E+[(0,n5)]
    fams.append(("gluedC5C7",n,E))
    # Mycielskians up to N=19 (gmins tractable)
    fams.append(("M(C5)N11",)+mycielskian(*cycle(5)))
    fams.append(("M(C7)N15",)+mycielskian(*cycle(7)))
    fams.append(("M(C9)N19",)+mycielskian(*cycle(9)))
    for fam in fams:
        run_family(fam[0],fam[1],fam[2],acc)
    print("="*64)
    print("TOTAL rows=%d"%acc['rows'])
    print("(I)  E_0<0 rows=%d ;  E_0 != 0 rows=%d   (if both 0 => E_0==0 always here)"%(acc['E0neg'],acc['E0nz']))
    print("(II) delta-split identity failures=%d  (0 => identity exact)"%acc['II_fail'])
    print("decoupling regime (delta*L^2 > rhs) rows=%d ; of those with E0>=0: %d"%(acc['disp_exceeds'],acc['disp_exceeds_E0nonneg']))
    print("(A) E_0+delta*L^2<=rhs failures=%d"%acc['A_fail'])
    print("(III/PSOS) delta*L^2+sum(h_i-m)^2 <= rhs failures=%d"%acc['PSOS_fail'])
    if acc['PSOS_worst']:
        w=acc['PSOS_worst']; print("    PSOS worst ratio=%.6f [%s] L=%s E0=%s SOS=%s R=%s"%(float(w[0]),w[1],w[2],w[3],w[4],w[5]))
    print("maximal weighted-SOS constant c (delta*L^2 + c*SOS + E0 <= rhs): cmax=%s ~%.5f at %s"%(acc['cmax'],float(acc['cmax']) if acc['cmax'] else 0,acc['cmax_at']))
    if acc['skipped']: print("skipped:",acc['skipped'])

if __name__=="__main__":
    main()
