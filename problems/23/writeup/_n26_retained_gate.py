"""Validate ALL closing lemmas on the N26 RETAINED-phase witness (Codex lab) -- the long ell=13 corridor
   case absent from my census battery.  Gates on the N26 parity cut: closing bound Tail_k>=sum H_i^-,
   factorization A (port prefix<=0) + B (Tail_k>=sum Suf_i), and pairwise PW (sort(added)<=sort(removed)).
"""
from fractions import Fraction as F
from _codex_interval_failure_switch_lab import n26_graph
from _singleton_core import ell_map, Hi_and_best
from _factor_gate import chi_profile
from _wf_deficit_farkas import flip
from _h import Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def main():
    n,E=n26_graph()
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    side=[v%2 for v in range(n)]
    Lam=len(E)*n*n+1
    if not Bconn(n,adj,side):
        print("parity cut B disconnected; aborting"); return
    st=struct_for_side(n,adj,side)
    if st is None:
        print("struct None on parity cut"); return
    M,ell,T,cyc=st[0],st[1],st[2],st[4]
    em0=ell_map(n,adj,side)
    print("N26 parity cut: |M|=%d bad edges, ell:"%len(M),[(tuple(sorted(e)),ell[e]) for e in M])
    rows=0; neg_rows=0
    pw_fail=0; A_fail=0; B_fail=0; bound_fail=0; retained_phase=0
    for f in M:
        if ell[f]%2==0: continue
        for P in cyc[f]:
            if len(P)!=ell[f]: continue
            _,_,Z,_,_=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
            mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
            rows+=1
            # negative ports
            profs=[]; sumHneg=0
            for i in range(len(P)):
                Hi,W,dec_=Hi_and_best(n,adj,side,em0,P,i,Lam)
                if Hi is None or Hi>=0 or W is None: continue
                em1=ell_map(n,adj,flip(side,W))
                if em1 is None: continue
                sumHneg+=Hi
                chi=chi_profile(em0,em1,n)
                profs.append((i,chi,em1))
                # pairwise PW
                k0=set(em0);k1=set(em1);added=k1-k0;removed=k0-k1;ret=k0&k1
                al=sorted(em1[e] for e in added); rl=sorted(em0[g] for g in removed)
                if not((len(al)==len(rl)) and all(al[j]<=rl[j] for j in range(len(al)))): pw_fail+=1
                if not all(em1[h]<=em0[h] for h in ret): pw_fail+=1
                if any(em1[h]<em0[h] for h in ret): retained_phase+=1   # retained-shortening present
                # Lemma A prefix
                pref=0
                for kk in range(1,len(chi)+1):
                    if kk-1<len(chi): pref+=(2*(kk-1)+1)*chi[kk-1]
                    if pref>0: A_fail+=1; break
            if mintail<0: neg_rows+=1
            # Lemma B + closing bound, all k
            for k in range(n):
                tk=sum((2*r+1)*Z[r] for r in range(k,n))
                sufsum=sum(sum((2*r+1)*ch[r] for r in range(k,len(ch))) for (_,ch,_) in profs)
                if tk-sufsum<0: B_fail+=1
                if tk-sumHneg<0: bound_fail+=1   # H_i^- = Hi for neg ports
    print("rows:%d  Tail<0 rows:%d  retained-shortening ports:%d"%(rows,neg_rows,retained_phase))
    print("PAIRWISE PW failures:",pw_fail)
    print("LEMMA A (prefix<=0) failures:",A_fail)
    print("LEMMA B (Tail_k>=sum Suf) failures:",B_fail)
    print("CLOSING BOUND (Tail_k>=sum H_i^-) failures:",bound_fail)
    ok = (pw_fail==0 and A_fail==0 and B_fail==0 and bound_fail==0)
    print("VERDICT:", "ALL LEMMAS HOLD on N26 retained phase" if ok else "FAIL on N26")

if __name__=="__main__":
    main()
