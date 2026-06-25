#!/usr/bin/env python3
"""
k-colored flag engine (Phase F): generalizes flag_engine_col from {0,1} to {0,...,ncolors-1}.
The primitives in flag_engine_col (canonical_col, relabel_col, sig_col, induced_col,
induced_density_col) are already color-agnostic (work for any integer colors); only the
enumerator hardcodes 2 colors. We add k-color enumeration via the Aut(G)-orbit method.

Margin-color convention for the max-cut margin lift (ncolors=4):
   color 0 = A_L, 1 = A_H, 2 = B_L, 3 = B_H ;  side(c)=c//2 (A=0,B=1);  mark(c)=c%2 (L=0,H=1).
   mono edge  = same side (both A* or both B*) -> counts toward beta.
   cut  edge  = different side.
"""
import itertools
import flag_engine as fe
import flag_engine_col as fc


def enumerate_kcolored(n, ncolors, triangle_free=True):
    """All ncolors-colored triangle-free graphs on n vertices up to colored iso (Aut-orbit method)."""
    out = []
    for (_, A) in fe.enumerate_graphs(n, triangle_free=triangle_free):
        auts = fc._aut_group(n, A)
        seen = set()
        for cbits in itertools.product(range(ncolors), repeat=n):
            best = None
            for perm in auts:
                cprime = [0]*n
                for i in range(n):
                    cprime[perm[i]] = cbits[i]
                t = tuple(cprime)
                if best is None or t < best:
                    best = t
            if best not in seen:
                seen.add(best)
                out.append((n, list(A), list(best)))
    return out


# side / mark helpers for the 4-color margin lift
def side(c): return c // 2          # 0=A, 1=B
def mark(c): return c % 2           # 0=L, 1=H
def is_mono_edge(cu, cv): return side(cu) == side(cv)


if __name__ == "__main__":
    print("=== k-color engine self-test ===")
    # ncolors=2 must reproduce flag_engine_col counts
    for n in range(1, 5):
        a = len(enumerate_kcolored(n, 2, True))
        b = len(fc.enumerate_colored(n, True))
        print(f"  n={n} ncolors=2: kcol={a} col={b}  {'OK' if a==b else 'MISMATCH'}")
    # ncolors=4 counts (sanity: grows)
    for n in range(1, 5):
        print(f"  n={n} ncolors=4: {len(enumerate_kcolored(n,4,True))} states")
    # density sanity: a 4-colored path, mono vs cut by side
    P3 = (3, fe.adj_from_edges(3, [(0,1),(1,2)]), [0, 2, 1])   # A_L - B_L - A_H : both edges are cut
    e = fe.edges_of(3, P3[1])
    mono = sum(1 for (i,j) in e if side(P3[2][i])==side(P3[2][j]))
    print(f"  P3 colored [A_L,B_L,A_H]: mono edges={mono} (expect 0, both cut)")
    P3b = (3, fe.adj_from_edges(3, [(0,1),(1,2)]), [0, 1, 2])  # A_L - A_H - B_L : edge1 mono(A-A), edge2 cut
    mono_b = sum(1 for (i,j) in fe.edges_of(3,P3b[1]) if side(P3b[2][i])==side(P3b[2][j]))
    print(f"  P3 colored [A_L,A_H,B_L]: mono edges={mono_b} (expect 1: A_L-A_H mono, A_H-B_L cut)")
    print("DONE")
