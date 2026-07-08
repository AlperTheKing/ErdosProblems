r"""R-A arm-landscape gate (2026-07-08): map the born-edge recut Gamma-change over crossing arm-tuples, using the
6-angle workflow's EXACT formula. gap#1 crux reduced to R-A: y-tightness + Gamma-minimality => every crossing is BALANCED
(the {L,L+2}->[L,L] door, dGamma < 0), never the long-arm-absorbing (unbalanced) profile which RAISES Gamma.

Crossing config: bad edges e=(s,t), f=(u,v) with shortest cut-geodesics P_e: s..x..y..t, P_f: u..y..x..v sharing the arc
x..y of length m=d(x,y) in OPPOSITE order. Arms a=|s..x|, b=|y..t| (on P_e), d=|u..y|, g=|x..v| (on P_f). Then
  ell(e) = a + m + b + 1,   ell(f) = d + m + g + 1
and the endpoint-swap born edges pair (a with d) and (b with g), born cut-path lengths a+d and b+g:
  ell(born1) = a + d + 1,   ell(born2) = b + g + 1.
EXACT Gamma change (Gamma(B^W) - Gamma(B), workflow-verified):
  dGamma = 2 * [ (a-g)*(d-b) - m*(a+b+g+d+m+2) ]  ==  (a+d+1)^2 + (b+g+1)^2 - (a+m+b+1)^2 - (d+m+g+1)^2.
BALANCED (the good door, switch strictly drops Gamma): dGamma < 0. UNBALANCED (switch FAILS / raises Gamma): dGamma >= 0.
This gate enumerates valid arm-tuples and reports the landscape, verifying the formula's two forms agree exactly. It does
NOT settle R-A (which needs y-tightness+Gamma-min realizability), but it maps WHICH arm profiles are the dangerous ones.
Run from problems/23/writeup.
"""


def dgamma_formula(a, b, g, d, m):
    return 2 * ((a - g) * (d - b) - m * (a + b + g + d + m + 2))


def dgamma_direct(a, b, g, d, m):
    ell_e = a + m + b + 1
    ell_f = d + m + g + 1
    born1 = a + d + 1
    born2 = b + g + 1
    return born1 ** 2 + born2 ** 2 - ell_e ** 2 - ell_f ** 2, (ell_e, ell_f, born1, born2)


def main():
    print("R-A ARM-LANDSCAPE GATE (born-edge recut dGamma over crossing arm-tuples).")
    print("dGamma < 0 = BALANCED door (switch works); dGamma >= 0 = UNBALANCED (switch fails / raises Gamma).")
    print("=" * 96)
    # verify the two formula forms agree, and classify. Constraints: arms >= 1, m >= 1, ell in [5,23] (short shell),
    # parity so ell odd (a+m+b even, d+m+g even).
    formula_mismatch = 0
    balanced = 0; unbalanced = 0; total = 0
    door_examples = []; unbal_examples = []
    MAX = 24
    for m in range(1, 6):
        for a in range(1, MAX):
            for b in range(1, MAX):
                if (a + m + b) % 2 != 0:
                    continue
                ell_e = a + m + b + 1
                if ell_e < 5 or ell_e > 23:
                    continue
                for d in range(1, MAX):
                    for gg in range(1, MAX):
                        if (d + m + gg) % 2 != 0:
                            continue
                        ell_f = d + m + gg + 1
                        if ell_f < 5 or ell_f > 23:
                            continue
                        f1 = dgamma_formula(a, b, gg, d, m)
                        f2, ells = dgamma_direct(a, b, gg, d, m)
                        if f1 != f2:
                            formula_mismatch += 1
                        # born lengths must also be valid odd cut-cycles (a+d even, b+g even for born ell odd)
                        if (a + d) % 2 != 0 or (b + gg) % 2 != 0:
                            continue
                        total += 1
                        if f1 < 0:
                            balanced += 1
                            if len(door_examples) < 4:
                                door_examples.append(((a, b, gg, d, m), f1, ells))
                        else:
                            unbalanced += 1
                            if len(unbal_examples) < 6:
                                unbal_examples.append(((a, b, gg, d, m), f1, ells))
    print("formula two-form agreement: %s (mismatches %d)" % ("OK" if formula_mismatch == 0 else "FAIL", formula_mismatch))
    print("arm-tuples (parity-valid, ell in [5,23], born odd): total %d | BALANCED (dGamma<0) %d | UNBALANCED (dGamma>=0) %d"
          % (total, balanced, unbalanced))
    print("\nBALANCED door examples ((a,b,g,d,m), dGamma, (ell_e,ell_f,born1,born2)):")
    for ex in door_examples:
        print("  %s" % (ex,))
    print("\nUNBALANCED (switch-FAILS) examples -- these RAISE Gamma; R-A must show they are NOT y-tight-realizable in Gamma-min:")
    for ex in unbal_examples:
        print("  %s" % (ex,))
    # the canonical {L,L+2}->[L,L] door
    print("\nThe {L,L+2}->[L,L] pair-door (symmetric arms a=d, b=g, giving born [L,L]):")
    for L in [5, 7, 13, 23]:
        # symmetric: a=d, b=g, born1=a+d+1=2a+1, born2=b+g+1=2b+1; want born balanced. Take a=b so ells symmetric.
        # door {L,L+2}: e has ell L, f has ell L+2, born both ... illustrate dGamma for a symmetric near-door tuple.
        pass
    print("=" * 96)
    print("VERDICT: %s. The UNBALANCED arm-tuples (dGamma>=0, long-arm-absorbing) are the switch-failure profiles; R-A ="
          " y-tightness + Gamma-minimality must FORBID them as realized y-tight crossings (force every crossing balanced)."
          " This gate maps the landscape via the workflow's exact dGamma formula (two forms agree)."
          % ("formula VALIDATED, landscape mapped" if formula_mismatch == 0 else "FORMULA MISMATCH -- investigate"))


if __name__ == '__main__':
    main()
