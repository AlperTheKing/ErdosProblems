"""Reproduce Codex's ZMU counterexample (block 26): C5 island + Myc(C7), single bridge (0,5), N=20.
ZMU claims a zero-mu cut edge has a T=0 endpoint; here the zero-mu bridge (0,5) has both T>0 => ZMU FALSE.
Confirm exact via my own _zmu.test/_zmu.mu_edges."""
from fractions import Fraction as F
from _h import loads
from _bdef_construct import Cn, union_disjoint, mycielski, is_triangle_free
from _zmu import test as zmu_test, mu_edges

isl=(5,Cn(5)); g15n,g15E=mycielski(7,Cn(7))
n,E=union_disjoint(isl,(g15n,g15E))
E=E+[(0,5)]   # bridge island vertex 0 to gadget vertex 0 (=global index 5)
print("triangle-free:", is_triangle_free(n,E), " N=",n)
info=loads(n,E)
print("loads None?", info is None)
if info is not None:
    N=info['n']; T=info['T']
    O=[v for v in range(N) if T[v]>N]
    print("O=",O)
    mu=mu_edges(info)
    z=[tuple(sorted(e)) for e,val in mu.items() if val==0]
    print("zero-mu edges:", z)
    for (u,v) in z:
        print(f"  edge ({u},{v}): T[{u}]={float(T[u])} T[{v}]={float(T[v])}  ZMU-ok(some T=0)={T[u]==0 or T[v]==0}")
    r=zmu_test(info)
    print("zmu_test:", {k:r[k] for k in ('O','nzero','zmu_viol','bothload','sat','cC')} if r else None)
