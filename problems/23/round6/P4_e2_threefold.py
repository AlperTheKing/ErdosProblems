"""(e) continued - item 6's sentence about 3-fold measures.

Item 6 of the brief: "Also 1far^(n) = (-1)^n sin(pi n/3)/(pi n) vanishes for 3 | n, so a purely
3-fold measure has g constant and no adjacent pairs at all."

Two separate claims, and they cannot both be right: g constant = 1/3 forces W = 1/6 (lots of
adjacent pairs), while "no adjacent pairs" forces g == 0.  The truth, for a measure invariant
under rotation by 1/3:

        g(x) = 1/3 - mu({x})        for every x,

because the three arcs (x, x+1/3), (x+1/3, x+2/3), (x+2/3, x+1) have equal mass and together miss
exactly the three atoms x, x+1/3, x+2/3, which carry 3*mu({x}).  So
  * atomless 3-fold measure : g == 1/3, W = 1/6, MANY adjacent pairs;
  * the 3-atom measure      : g == 0,   W = 0,   no adjacent pairs;
and the quoted sentence is only correct in the second case, which is not the generic one.
"""
from fractions import Fraction as F
from P4_core import (adjacency, sort_cyclic, W_of, g_of, A_of, normalise, circdist)


def show(name, pos, wt):
    pos, wt = sort_cyclic(*normalise(pos, wt))
    adj = adjacency(pos)
    g = g_of(pos, wt, adj)
    W = W_of(pos, wt, adj)
    A = A_of(pos, wt, adj)
    pred = [F(1, 3) - w for w in wt]
    print(f"  {name}")
    print(f"    atoms   {[str(p) for p in pos]}")
    print(f"    x       {[str(t) for t in wt]}")
    print(f"    g       {[str(t) for t in g]}")
    print(f"    1/3-x   {[str(t) for t in pred]}   matches g: {g == pred}")
    print(f"    W = {W} = {float(W):.6f}   A = {A} = {float(A):.6f}   "
          f"{'NO adjacent pairs' if W == 0 else 'adjacent pairs PRESENT'}")


if __name__ == '__main__':
    print("=" * 92)
    print("(e/item 6) purely 3-fold measures: g is NOT constant 1/3 in general, and they do NOT")
    print("           generally lack adjacent pairs")
    print("=" * 92)
    show("3 atoms at 0, 1/3, 2/3 (the only case the brief's sentence fits)",
         [F(0), F(1, 3), F(2, 3)], [1, 1, 1])
    show("6 atoms: {0,1/3,2/3} + {1/6,1/2,5/6}, equal weights (3-fold invariant)",
         [F(0), F(1, 6), F(1, 3), F(1, 2), F(2, 3), F(5, 6)], [1] * 6)
    show("9 atoms, 3-fold invariant, unequal weights",
         [F(0), F(1, 9), F(2, 9), F(1, 3), F(4, 9), F(5, 9), F(2, 3), F(7, 9), F(8, 9)],
         [3, 1, 2, 3, 1, 2, 3, 1, 2])
    show("12 atoms, 3-fold invariant (uniform on Gamma_12)",
         [F(i, 12) for i in range(12)], [1] * 12)
    print("\n  => the brief's sentence is right only for the single 3-atom measure;")
    print("     for every other 3-fold invariant measure g = 1/3 - mu({x}) > 0 and W > 0.")
