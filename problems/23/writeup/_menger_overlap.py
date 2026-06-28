"""Try a Menger/geodesic-interval bound on <p_f,p_g> that sums to give Cycle-SM.
<p_f,p_g> = sum_v p_f(v) p_g(v). Both supported on geodesic intervals Int(f),Int(g).
Candidate (counting): <p_f,p_g> <= |Int(f) cap Int(g)| ? (each p<=1) -- weak but test if Cycle-SM follows:
   sum_g ell(g) |Int(f) cap Int(g)| <= N ell(f)? i.e. sum_g ell(g)|Int(f) cap Int(g)| <= N ell(f).
   = sum_{v in Int(f)} sum_{g: v in Int(g)} ell(g) = sum_{v in Int(f)} (sum over g thru-interval ell(g)) =: sum_{v in Int(f)} Tint(v)
   where Tint(v)=sum_{g: v in Int(g)} ell(g) (interval-load, >= T(v)). Need <= N ell(f). Test.
Better candidate using the layer/uniform structure:
   <p_f,p_g> = sum_i sum_{v in I_i(f)} p_f(v)p_g(v) and per layer sum p_f=1, so <= sum_i max_{v in I_i(f)} p_g(v)
   <= sum_i (p_g mass in layer i of f). Test sum_g ell(g) * [that] vs N ell(f).
Just compute the simplest: is <p_f,p_g> <= |Int(f) cap Int(g)| and does the implied bound hold?
"""
import subprocess
from fractions import Fraction as F
from _h import dec, GENG, loads

def pf_vec(info, f):
    Ps = info['cyc'][f]; nf = len(Ps); cnt = {}
    for P in Ps:
        for v in P: cnt[v] = cnt.get(v,0)+1
    return {v: F(cnt[v], nf) for v in cnt}

def ip(a,b):
    s=F(0)
    for w,av in a.items():
        bv=b.get(w)
        if bv is not None: s+=av*bv
    return s

def run(nmin,nmax,limit=None):
    print("=== Menger/interval overlap bound for Cycle-SM ===")
    # (1) <p_f,p_g> <= |Int(f) cap Int(g)| ?  (should hold, p<=1)
    o1_fail=0
    # (2) sum_{v in Int(f)} Tint(v) <= N ell(f)?  (Tint(v)=sum_{g:v in Int(g)} ell(g))
    o2_worst=F(-10); o2w=None; o2_fail=0
    for nn in range(nmin,nmax+1):
        out=subprocess.run([GENG,"-tc",str(nn)],capture_output=True,text=True).stdout.split()
        if limit: out=out[:limit]
        for g6 in out:
            n,E=dec(g6); info=loads(n,E)
            if info is None: continue
            M=info['M']; ell=info['ell']
            pfs={f:pf_vec(info,f) for f in M}
            Int={f:set(pfs[f].keys()) for f in M}
            Tint={v:F(0) for v in range(n)}
            for g in M:
                for v in Int[g]: Tint[v]+=ell[g]
            for f in M:
                # (1)
                for g in M:
                    if ip(pfs[f],pfs[g]) > len(Int[f]&Int[g]): o1_fail+=1
                # (2)
                lhs=sum(Tint[v] for v in Int[f])
                r=lhs-n*ell[f]
                if r>0: o2_fail+=1
                if r>o2_worst: o2_worst=r; o2w=(g6,f,float(lhs),n*ell[f])
        print(f"  N<={nn}: (1)<p_f,p_g>>|Int cap| fails={o1_fail} | (2) sum_Int Tint > N*ell fails={o2_fail} worst={float(o2_worst):+.3f}@{o2w}",flush=True)

if __name__=="__main__":
    run(7,9,limit=None)
