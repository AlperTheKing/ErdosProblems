"""DECISIVE realizability test of Codex's stretched L=7 nested core (R_local=-29/4 abstract).
Build the concrete 12-vertex graph mirroring the construction and run MY full deficient-cap machinery:
if it has a deficient cap with R[v]<0, the deficient-cap SIGN ATOM is REFUTED (the cap-side approach breaks).
If defcap=0 or fail=0, the abstract stretched core is NOT realizable as a real deficient configuration => L=5 forced.

Construction (Codex): f0 ell=7 rows s-a_i-c0-c1-c2-b_j-t (i,j in {0,1}); f1 ell=9 rows u-a1-c0-c1-c2-b_j-t-x-v.
Vertices: 0=s 1=u 2=x 3=v 4=a0 5=a1 6=c0 7=c1 8=c2 9=b0 10=b1 11=t. Bad edges f0=(s,t)=(0,11), f1=(u,v)=(1,3)."""
from collections import Counter
from _bdef_construct import is_triangle_free
from _defcap_sign_mine import scan_graph as sign_scan
from _defcap_component_mine import scan_graph as comp_scan, new_acc as comp_new, report as comp_report

E = [(0, 4), (0, 5), (4, 6), (5, 6), (6, 7), (7, 8), (8, 9), (8, 10), (9, 11), (10, 11),
     (1, 5), (11, 2), (2, 3), (0, 11), (1, 3)]
n = 12

print("triangle-free:", is_triangle_free(n, E))

# Full max-cut-based deficient-cap sign scan (my machinery)
acc = Counter(); acc['first'] = None; acc['first_global'] = None; acc['templates'] = Counter()
sign_scan('strL7', n, E, acc)
print("=" * 60)
print("SIGN scan (my machinery, real max cuts):")
print("  two_cap_positive=%d defcap=%d fail_inS=%d global_fail=%d" %
      (acc['two_cap_positive'], acc['defcap'], acc['fail'], acc['global_fail']))
print("  deficient templates:", dict(acc['templates']))
print("  first inS-fail (deficient cap WITH R<0 vertex in S):", acc['first'] or 'NONE')
print("  first global-fail:", acc['first_global'] or 'NONE')

cacc = comp_new()
comp_scan('strL7', n, E, cacc)
comp_report('STRETCHED L=7 (real graph)', cacc)

print("=" * 60)
if acc['defcap'] == 0:
    print("VERDICT: stretched L=7 core has NO deficient cap as a real max-cut configuration => NOT realizable => L=5 not contradicted.")
elif acc['fail'] > 0 or acc['global_fail'] > 0 or cacc['rlocal_neg'] > 0:
    print("VERDICT: *** SIGN ATOM REFUTED *** -- realizable L=7 deficient core with R<0. Cap-side approach BREAKS.")
else:
    print("VERDICT: deficient cap exists but R>=0 (real graph differs from abstract; R_full saved by N term).")
