"""DECISIVE TEST of the strip-uncrossing angle's claim: does PATH-LRS hold at EVERY maximum cut (not just
gamma-MINIMAL ones)? If yes, the proof needs only max-cut (drop Gamma-minimality). Note m=|M|=beta is INVARIANT
across max cuts, so A=N+N^2/25-m is fixed, but T grows at non-gamma-min cuts => PATH-LRS there is STRONGER.
Enumerate ALL maximum cuts via maxcut_all; test PATH-LRS avg_P T <= A on each. Compare gamma-min vs non-gamma-min.
Includes H?AFBo] (where ROWSUM-O is KNOWN to fail at the non-gamma-min max cut Gamma=74)."""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, Bconn, maxcut_all
from _satzmu_conn import struct_for_side

def test_graph(name,n,E,acc):
    adj=[set() for _ in range(n)]
    for x,y in E: adj[x].add(y); adj[y].add(x)
    cuts=maxcut_all(n,adj)   # ALL maximum cuts
    # group by Gamma
    rows=[]
    for side in cuts:
        if not Bconn(n,adj,side): continue
        st=struct_for_side(n,adj,side)
        if st is None: continue
        M,ell,T,mu,cyc=st
        if not M: continue
        rows.append((sum(T),side,M,ell,T,cyc))
    if not rows: return
    gmin=min(r[0] for r in rows)
    for Gam,side,M,ell,T,cyc in rows:
        m=len(M); A=F(n)+F(n*n,25)-m
        is_gmin = (Gam==gmin)
        worst=None
        for f in M:
            for P in cyc[f]:
                avg=sum(T[v] for v in P)/F(ell[f])
                margin=A-avg
                if worst is None or margin<worst: worst=margin
        acc['cuts']+=1
        if not is_gmin: acc['nongmin']+=1
        if worst is not None and worst<0:
            acc['viol']+=1
            tag='GMIN' if is_gmin else 'NON-GMIN'
            if acc['fviol'] is None: acc['fviol']=(name,n,str(Gam),tag,str(worst))
            if not is_gmin: acc['viol_nongmin']+=1

if __name__=="__main__":
    acc=dict(cuts=0,nongmin=0,viol=0,viol_nongmin=0,fviol=None)
    # H?AFBo] explicitly (ROWSUM-O fails at its non-gamma-min max cut)
    n,E=dec('H?AFBo]'); test_graph('H?AFBo]',n,E,acc)
    print("  after H?AFBo]: cuts=%d nongmin=%d viol=%d"%(acc['cuts'],acc['nongmin'],acc['viol']),flush=True)
    for nn in range(5,10):
        outg=subprocess.run([GENG,'-tc',str(nn)],capture_output=True,text=True).stdout.split()
        for g6 in outg:
            n,E=dec(g6); test_graph('cen%s'%g6,n,E,acc)
        print("  census N=%d done (cuts=%d nongmin=%d viol=%d viol_nongmin=%d)"%(nn,acc['cuts'],acc['nongmin'],acc['viol'],acc['viol_nongmin']),flush=True)
    print("\n  PATH-LRS at ALL max cuts: total max-cuts tested=%d (non-gamma-min=%d)"%(acc['cuts'],acc['nongmin']),flush=True)
    print("  violations=%d (of which at non-gamma-min cuts=%d)  %s"%(acc['viol'],acc['viol_nongmin'],acc['fviol'] or ''),flush=True)
    if acc['viol']==0:
        print("  === PATH-LRS HOLDS AT EVERY MAX CUT => Gamma-minimality NOT needed (proof simplifies) ===",flush=True)
    elif acc['viol_nongmin']>0 and acc['viol']==acc['viol_nongmin']:
        print("  === PATH-LRS FAILS only at NON-gamma-min cuts => Gamma-minimality IS REQUIRED (strip-angle claim WRONG) ===",flush=True)
    else:
        print("  === PATH-LRS FAILS even at some gamma-min cut => unexpected, investigate ===",flush=True)
