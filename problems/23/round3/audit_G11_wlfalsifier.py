"""
audit_G11_wlfalsifier.py

G11_verify_andrasfai.py part (D) certifies "Gamma_i iso And_i" by comparing a
WL-1 (degree-refinement) colour certificate.  On VERTEX-TRANSITIVE REGULAR
graphs that certificate carries NO information: every vertex receives the same
colour, so the certificate collapses to (n, |E|, constant, constant).

Falsifier below: the Wagner graph V8 (= Gamma_3 = And_3) and the 3-cube Q3.
Both are 3-regular vertex-transitive graphs on 8 vertices with 12 edges, so the
target's certificate declares them equal; but Q3 is bipartite and V8 is not, so
they are NOT isomorphic.  Hence the target's (D) is an unsound method.

(The CONCLUSION Gamma_i = And_i is nevertheless TRUE -- proved exactly in
audit_G11_core.py part D by the explicit multiplier map x -> 3x mod 3i-1.)
"""
import sys
sys.path.insert(0, r"E:\Projects\ErdosProblems\problems\23\round3")
from audit_G11_core import (moebius_ladder_8, is_bipartite, iso_backtrack,
                            adjmasks, popcount)


def target_certificate(n, E):
    """Verbatim re-implementation of canonical_certificate() in
    G11_verify_andrasfai.py (WL-1 colour refinement + edge colour multiset)."""
    adj = [set() for _ in range(n)]
    for u, v in E:
        adj[u].add(v)
        adj[v].add(u)
    col = [len(adj[x]) for x in range(n)]
    for _ in range(n):
        new = [(col[x], tuple(sorted(col[y] for y in adj[x]))) for x in range(n)]
        remap = {c: i for i, c in enumerate(sorted(set(new)))}
        col = [remap[c] for c in new]
    return (n, len(E), tuple(sorted(col)),
            tuple(sorted((min(col[u], col[v]), max(col[u], col[v])) for u, v in E)))


def cube3():
    E = set()
    for a in range(8):
        for b in range(3):
            c = a ^ (1 << b)
            E.add((min(a, c), max(a, c)))
    return 8, sorted(E)


n1, E1 = moebius_ladder_8()      # Wagner V8 = Gamma_3 = And_3
n2, E2 = cube3()                 # 3-cube Q3
print("V8 : n=%d m=%d degrees=%s bipartite=%s" %
      (n1, len(E1), sorted(popcount(a) for a in adjmasks(n1, E1)), is_bipartite(n1, E1)))
print("Q3 : n=%d m=%d degrees=%s bipartite=%s" %
      (n2, len(E2), sorted(popcount(a) for a in adjmasks(n2, E2)), is_bipartite(n2, E2)))
c1, c2 = target_certificate(n1, E1), target_certificate(n2, E2)
print("target WL certificate equal ? ", c1 == c2)
print("actually isomorphic ?        ", iso_backtrack(n1, E1, n2, E2))
assert c1 == c2, "certificates differ -- falsifier failed"
assert not iso_backtrack(n1, E1, n2, E2), "graphs are isomorphic -- falsifier failed"
print()
print("RESULT: the WL-1 certificate used by G11_verify_andrasfai.py part (D) "
      "declares V8 and Q3 identical although they are not isomorphic "
      "(Q3 bipartite, V8 not). The method proves nothing on regular graphs.")
