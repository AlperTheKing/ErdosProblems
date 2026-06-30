"""ZERO-MARGIN PORT CONCENTRATION gate (Codex 378 / GPT-Pro sharpened crux).
   On non-gamma-min connected-B MAX cuts where Tail_k(P)<0, over the parity-completed interval switch
   family U=U(I,tau):
     q(U)=delta_B(U)-delta_M(U)>=0 (maxcut);  d(U)=Gamma(flip U)-Gamma (Bconn required);
     Z(q)=min{d(U): margin(U)=q};  F=min_q (Z(q)+25 q);  Z0=Z(0).
   GATE:  F<0  =>  Z0<0   (a negative finite-price switch concentrates to a neutral one).
   Reports per-witness margin profile Z(q), F, Z0.  ALL exact Fraction.  Straddler completions capped.
"""
import subprocess, itertools
from fractions import Fraction as F
import _crux_extract as cx
from _crux_extract import parity_interval_switches
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

CAP = 1 << 16

def margin_profile(n, adj, side, M, Gamma, P):
    """Return dict q->min d(U) over admissible (Bconn) parity-interval switches U; capped."""
    Zq = {}
    seen = set(); cnt = 0
    for W in parity_interval_switches(n, adj, side, P):
        if not W or W in seen: continue
        seen.add(W); cnt += 1
        if cnt > CAP: return Zq, True
        dB, dM = deltas(n, adj, side, W)
        q = dB - dM
        if q < 0: continue   # not admissible on a max cut
        s2 = flip(side, W)
        if not Bconn(n, adj, s2): continue
        g1 = gamma_of(n, adj, s2)
        if g1 is None: continue
        d = g1 - Gamma
        if q not in Zq or d < Zq[q]: Zq[q] = d
    return Zq, False

def main():
    rows=0; gate_ok=0; gate_fail=0; failex=None; witnesses=[]
    for nn in range(5, 11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            n,E=dec(g6); adj=[set() for _ in range(n)]
            for x,y in E: adj[x].add(y); adj[y].add(x)
            mc,cuts=cx.all_max_cuts(n,adj,E)
            structs=[]
            for side in cuts:
                if not Bconn(n,adj,side): continue
                st=struct_for_side(n,adj,side)
                if st is None: continue
                structs.append((side,st,sum(st[2])))
            if not structs: continue
            gmin=min(g for (_,_,g) in structs)
            for (side,st,G) in structs:
                if G<=gmin: continue   # only non-gamma-min can have Tail<0
                M,ell,T,cyc=st[0],st[1],st[2],st[4]
                if not M: continue
                for f in M:
                    if ell[f]%2==0: continue
                    for P in cyc[f]:
                        if len(P)!=ell[f]: continue
                        _,_,Z,lhs,rhs=Zr_row(n,adj,side,M,ell,T,cyc,f,P)
                        mintail=min(sum((2*r+1)*Z[r] for r in range(k,n)) for k in range(n))
                        if mintail>=0: continue
                        rows+=1
                        Zq, capped = margin_profile(n,adj,side,M,G,P)
                        if not Zq: continue
                        Fval = min(Zq[q] + 25*q for q in Zq)
                        Z0 = Zq.get(0, None)
                        prof = sorted((q, str(Zq[q])) for q in Zq)
                        witnesses.append((g6,n,ell[f],tuple(P),str(mintail),str(Fval),str(Z0) if Z0 is not None else 'none',prof,capped))
                        if Fval < 0:
                            if Z0 is not None and Z0 < 0: gate_ok+=1
                            else:
                                gate_fail+=1
                                if failex is None: failex=(g6,n,tuple(P),str(Fval),str(Z0))
    print("Tail<0 witness rows:", rows)
    print("F<0 => Z0<0  PASS:", gate_ok, " FAIL:", gate_fail, failex or '')
    print("\nper-witness (g6,N,L,P | mintail | F | Z0 | Z(q) profile):")
    for w in witnesses[:20]:
        print("  %s N=%d L=%d P=%s | tail=%s | F=%s Z0=%s | %s%s"
              % (w[0],w[1],w[2],w[3],w[4],w[5],w[6],w[7],' [CAPPED]' if w[8] else ''))
    print("VERDICT:", "ZERO-MARGIN CONCENTRATION HOLDS (F<0 => Z0<0)" if gate_fail==0 and rows>0 else
          ("no witnesses" if rows==0 else "FALSIFIED"))

if __name__=="__main__":
    main()
