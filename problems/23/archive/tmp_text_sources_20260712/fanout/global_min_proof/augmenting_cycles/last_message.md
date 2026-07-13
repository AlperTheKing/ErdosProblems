Exact computation succeeded, but artifact creation was blocked by the Windows patch sandbox.

Results:

- Census: orders 5–9
- Connected triangle-free graphs: 1,731
- Eligible cuts: 2,145
- Exact row tuples: 8,903
- Global minimizing tuples: 5,541
- Matcher-failing tuples overall: 702
- Hall-failing global minimizers: 0
- Cuts with Hall-failing global minimizers: 0

Command:

```powershell
python problems/23/writeup/_codex_r20_global_min_all_ties_gate.py --min-order 5 --max-order 9 --workers 1 --max-falsifiers 5
```

The computation uses integer-exact scoring and enumeration. The 2943 constructor was not found; only its prose specification was available, so no 2943 gate result is claimed.

The augmenting-cycle route does not yet close the theorem. The exact remaining gap is:

> Scoped Hall failure at a row tuple implies the existence of a finite simultaneous row trade with strictly smaller `scopedObligationScore`.

Finite-state optimality proves that such a trade contradicts global minimality, but Hall failure itself has not been shown to produce it. No exact falsifier to that implication was found.

Attempts to create `RESULT.md` failed because the patch writer reported:

```text
windows unelevated restricted-token sandbox cannot enforce split writable root sets directly
```

No repository files were modified.