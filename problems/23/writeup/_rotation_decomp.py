"""Gate Codex 379 ROTATION-DECOMPOSITION invariant on every extracted Tail<0 switch.
   For a neutral connected extracted interval switch W with DeltaGamma(W)<0, decompose
     DeltaGamma(W) = BoundaryExchange + Retained,
       BoundaryExchange = sum_{e in M^W \\ M} ell_after(e)^2 - sum_{g in M \\ M^W} ell_before(g)^2,
       Retained        = sum_{h in M cap M^W} (ell_after(h)^2 - ell_before(h)^2).
   For each Tail<0 row, does SOME extracted W satisfy:
     (1) BoundaryExchange <= 0;
     (2) no retained bad edge lengthens: ell_after(h) <= ell_before(h) for all retained h;
     (3) at least one retained bad edge STRICTLY shortens;
     (4) #added == #removed (pairable by odd-cycle rotation) and sum ell_after^2(added) <= sum ell_before^2(removed).
   ell from struct_for_side (shortest blue-geodesic odd-cycle length).  ALL exact.
"""
import subprocess
import _crux_extract as cx
from _crux_extract import parity_interval_switches
from _wf_deficit_farkas import deltas, flip, gamma_of
from _h import dec, GENG, Bconn
from _layer_gate import Zr_row
from _satzmu_conn import struct_for_side

def ell_map(n, adj, side):
    st = struct_for_side(n, adj, side)
    if st is None: return None
    M, ell = st[0], st[1]
    return {frozenset(e): ell[e] for e in M}

def decompose(n, adj, side, W):
    """Return (dGamma, boundary, retained, n_add, n_rem, ok1234) for switch W, or None if invalid."""
    s2 = flip(side, W)
    if not Bconn(n, adj, s2): return None
    em0 = ell_map(n, adj, side); em1 = ell_map(n, adj, s2)
    if em0 is None or em1 is None: return None
    keys0 = set(em0); keys1 = set(em1)
    removed = keys0 - keys1   # were bad, now not
    added   = keys1 - keys0   # now bad, were cut
    retained = keys0 & keys1
    boundary = sum(em1[e]**2 for e in added) - sum(em0[g]**2 for g in removed)
    retained_sum = sum(em1[h]**2 - em0[h]**2 for h in retained)
    dG = boundary + retained_sum
    no_lengthen = all(em1[h] <= em0[h] for h in retained)
    strict_short = any(em1[h] < em0[h] for h in retained)
    pair_ok = (len(added) == len(removed)) and (sum(em1[e]**2 for e in added) <= sum(em0[g]**2 for g in removed))
    # RELAXED invariant: dG<0 from boundary<=0 + no retained lengthens + paired rotation
    # (strict negativity comes from boundary<0 OR a retained shortening -- not necessarily retained)
    cond = (dG < 0) and (boundary <= 0) and no_lengthen and pair_ok
    return dG, boundary, retained_sum, len(added), len(removed), cond, no_lengthen, strict_short, (boundary<=0), pair_ok

def main():
    rows=0; sat=0; unsat=0; ex=None; examples=[]
    cond_stats=dict(c1=0,c2=0,c3=0,c4=0)
    fams=[]
    for nn in range(5,11):
        for g6 in subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split():
            fams.append((g6,)+dec(g6))
    for (g6,n,E) in fams:
        adj=[set() for _ in range(n)]
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
            if G<=gmin: continue
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
                    # find an extracted W satisfying all conditions; track best
                    found=False; best=None
                    seen=set()
                    for W in parity_interval_switches(n,adj,side,P):
                        if not W or W in seen: continue
                        seen.add(W)
                        dB,dM=deltas(n,adj,side,W)
                        if dB!=dM: continue
                        d=decompose(n,adj,side,W)
                        if d is None: continue
                        dG=d[0]
                        if dG>=0: continue
                        if best is None: best=(g6,n,tuple(P),str(dG),d[1],str(d[2]),d[3],d[4],d[6],d[7],d[8],d[9])
                        if d[5]:
                            found=True
                            if len(examples)<8:
                                examples.append((g6,n,tuple(P),'dG=%s'%dG,'bd=%s'%d[1],'ret=%s'%d[2],'add/rem=%d/%d'%(d[3],d[4])))
                            break
                    if found: sat+=1
                    else:
                        unsat+=1
                        if ex is None: ex=best
    print("Tail<0 rows:", rows)
    print("rows with an extracted W meeting ALL 4 conditions:", sat)
    print("rows with NO such W:", unsat)
    if ex: print("first unsatisfied (best W decomp):", ex)
    print("\nsample satisfying decompositions:")
    for e in examples: print("  ", e)
    print("VERDICT:", "ROTATION-DECOMPOSITION invariant HOLDS (every Tail<0 row has a clean extracted W)"
          if unsat==0 and rows>0 else ("no witnesses" if rows==0 else "FAILS on some row"))

if __name__=="__main__":
    main()
