# Span-Capacity Lemma (PROVED) — for the direct unique-path UPO proof

**Setup.** Triangle-free G, a maximum cut with cut graph B (the cross/cut edges). f a bad edge with a UNIQUE
shortest B-geodesic P=(x_0,...,x_{L-1}) (len(cyc[f])=1). Delete V(P) from B; let C be a connected component of
B[V \ V(P)], with attachment positions A(C)={i : some u in C has a B-edge to x_i}, lo=min A(C), hi=max A(C),
cap=|C|.

## Lemma.  cap >= hi - lo + 1.

## Proof.
If lo=hi the claim is cap>=1, true since C is nonempty. Assume lo<hi, so x_lo != x_hi.

Pick u_lo, u_hi in C with B-edges x_lo–u_lo and x_hi–u_hi (exist by definition of lo,hi in A(C)). Since C is a
connected component of B, there is a simple B-path pi inside C from u_lo to u_hi, all of whose vertices lie in C.
Form
        W : x_lo — u_lo — (pi) — u_hi — x_hi.
Every edge of W is a B-edge (the two end edges by attachment, the interior edges because pi lies in the
B-component C). W is a SIMPLE path: pi is simple and contained in C, while x_lo,x_hi lie on P, hence not in C, so
W has no repeated vertex. Writing |W| for its number of edges, its interior vertices are exactly those of pi, so
        (#interior vertices of W) = |W| - 1,  and all interior vertices lie in C, hence  cap >= |W| - 1.   (*)

Now bound |W| below. P is a shortest B-geodesic, so its subpath from x_lo to x_hi is a shortest x_lo–x_hi path
in B; thus d_B(x_lo,x_hi) = hi - lo. Since W is an x_lo–x_hi path, |W| >= hi - lo. Two refinements:
 (i) |W| != hi - lo: otherwise W is a SECOND shortest x_lo–x_hi B-path (W passes through C, off P, so W differs
     from P's segment), and replacing P's [x_lo,x_hi] segment by W yields a second shortest a–b B-geodesic for f
     — contradicting len(cyc[f])=1.
 (ii) B is bipartite (a cut graph), so every x_lo–x_hi walk has length congruent to hi-lo (mod 2). Hence
      |W| ≡ hi-lo (mod 2).
From |W| >= hi-lo, |W| != hi-lo, and |W| ≡ hi-lo (mod 2): |W| >= hi - lo + 2.

Substituting into (*):  cap >= |W| - 1 >= hi - lo + 1.  ∎

## Remarks.
- Uniqueness of P alone gives only cap >= hi-lo (|W|>=hi-lo+1 from (i)); the BIPARTITE PARITY (ii) supplies the
  extra +1 to reach cap >= hi-lo+1, matching the exact census (0 violations).
- Exact-confirmed 0 violations on the full battery (_span_capacity_gate.py): census N<=11 (component counts
  match Codex's scan: N10=7125), structured witnesses, glued islands N=18, Mycielskians up to N=23.
- Role: this is the "detour capacity dominates span" fact powering the direct whole-path packing proof
  sum_i (S(x_i)-1) <= |V \ V(P)|. Each off-path component can absorb demand across its whole attachment span
  because its vertex count is at least the span length (+1).
