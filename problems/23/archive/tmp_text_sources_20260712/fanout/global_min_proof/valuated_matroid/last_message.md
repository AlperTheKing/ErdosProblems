Blocked from delivering `RESULT.md`: the patch service cannot initialize its Windows sandbox for this workspace, despite the assigned directory being ACL-writable. I did not write outside the route directory.

Exact computation completed:

- Valuated-matroid exchange falsifier:
  `f(00)=1, f(01)=2, f(10)=2, f(11)=0`.
  For `x=00`, `y=11`, coordinate `0`:
  `f(x)+f(y)=1 < 4=f(10)+f(01)`.
  Thus the minimization exchange axiom fails. It also exhibits the required barrier: `00` is a strict Hamming-one local minimum but not global.
- Delta-matroid falsifier:
  feasible family `{∅,{0,1,2}}`.
  For `X=∅`, `Y={0,1,2}`, `u=0`, no permitted symmetric exchange produces a feasible set.
- The row-choice domain itself is a partition-matroid base family; the obstruction is the scoped score’s active-connectivity-dependent valuation.
- The 2943 constructor/data was not found. Its claimed results therefore remain ungated by this route.

Relevant hashes:

- `COMMON.md`: `533CD8772B6F0CD8F667E3388B7BABA9A0734F862E41CB01CD6958AC2C296003`
- `MinimumDemandRowSelection.lean`: `E4D216FCE19E96416BE0842F5410BAB0CF8FEE9AF933FF1160A3B77A3A67B11A`
- `ActiveScopedMinimumExchange.lean`: `B916318F53D69B4D9ADFF2C4A79B23C139513640F16550DAEA092CE3A9E77982`
- `ActiveScopedOwnerHallReduction.lean`: `6A4D47533D10E4B04EB19CDA0D0554658ABD434C94C04566A01916708A90E8F0`
- `WALL_ATTACK_R29_GPTPRO56.md`: `FFF06D97F2E574FE2D66B9CEA4F3BC4244037A92EB8ED5BD363ECA73C8591B04`