# Multi-coordinate pooled transport report

## Exact theorem

Let I be a finite coordinate type. For each i in I, let Z_i be the CoordinateNewDemandBundle and Q_i the OneCoordinateAlternative type. Let O be OutsideShoreDemand G c omega A and S be ShoreSource G c omega A. Define Z as the disjoint union of the Z_i and T as (the disjoint union of the Q_j) times (O disjoint-union S).

**Pooled complete-eligibility transport theorem.** If

    sum_i |Z_i| <= (sum_j |Q_j|)(|O| + |S|),

then there is an injection Z -> T.

This is finite cardinality (Fintype.card_le_iff). Unlike separate coordinate injections, target coordinate j need not equal source coordinate i, so unused component capacity is borrowable across coordinates. Owner-shore defect is preserved: the old-demand target summand is restricted to owners outside A, while the only A-shore targets are certified scopedOwnerSourceSet free halves.

## Exact tests

Script: test_multicoord.py. Arithmetic: Python fractions.Fraction; no float conversion or tolerance.

Input census artifacts containing componentTransport: 1. Pooled instances tested: 1. Coordinate records tested: 3.

For tmp/fanout/transport_dual/accounting/default.json:

- demands by coordinate: 0, 0, 0;
- capacities (outsideCapacity + sourceCapacity): 51, 85, 85;
- pooled inequality: 0 <= 221, true;
- coordinate inequalities: 3/3 true.

Thus the available artifact passes, but vacuously on the demand side.

## Falsifier search

No falsifier to the stated theorem exists: it is the finite-cardinality injection criterion under complete eligibility.

Exhaustive nonnegative-integer search found the minimal witness falsifying the stronger implication "pooled feasibility implies every separate coordinate injection is feasible":

    demand = (0,1), capacity = (1,0).

Here 1 <= 1 pooled, but coordinate 1 has 1 > 0. It has two coordinates and minimum total mass sum(d_i)+sum(c_i)=2; one coordinate cannot exhibit cross-coordinate borrowing.

## SHA256

- WALL_ATTACK_R29_GPTPRO56.md: FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04
- ActiveScopedCoordinateTransport.lean: 2821EB83265C85DC41F42EDD2B31DAE11FE60256B257E6C129BBB6E882AB5706
- accounting/default.json: F5C3FA45C9E9CCD9743D00FEB3E5B08345EE957BF3F788A4F4216358C9CEE978
- test_multicoord.py: 9BDAEB43AB995C587F39FCC6977D6EC17A6BE1B6D37990E26A1ED10209340F57
- RESULT.json: CE1C1C1886638A269114E07C8B83A182F115C1FE8F146635B8C4B88AB1BEC49B

## Remaining proof gap

The graph-derived ComponentTransportSourceEligible relation is not complete eligibility. To use this pooled theorem in R29 one must prove pooled Hall inequalities for every subset of the disjoint union of Z_i, with edges only to eligible outside-demand/source tokens. The sole available artifact has pooled new demand zero, so it tests accounting but supplies no nontrivial evidence for those Hall inequalities. No Lean production file was edited, and no Lean claim was added.