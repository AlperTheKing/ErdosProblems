# ActiveScoped REACH selector audit

## Verdict

The production definitions do **not** imply selector invariance. For hub shore `W={0,1,2}`, a half-source `s=(x,y,h)` is in REACH exactly when

```text
F(x,y) AND (x in W OR C_W(x,y))
       AND NOT(h=0 AND E_active(x,y) AND A(x)).                 (Q)
```

`F` is `pairCount(x,y)=0`; `C_W` is the disjunction over owners in `W` of the two positive owner-pair counts and the selector-independent `sigma>=0` test; `E_active` is adjacency in `activeGraph`; and `A` is `ActiveOwner(x)`. Source owner and source pair disappear except through these Boolean coordinates.

## Decomposition

For each ordered pair `(x,y)`, half 1 contributes `F*(Own_W(x) OR C_W(x,y))`. Half 0 contributes the same indicator multiplied by `NOT(E_active(x,y) AND A(x))`. Reservation never affects half 1. Active-component membership affects REACH only jointly with an active edge and half 0. Since `sigma>=0` is fixed, the smallest selector-dependent atoms are `F`, `C_W`, and `E_active AND A`.

No cancellation is forced: toggling any one atom has a one-source witness changing REACH, while toggling `F` or `C_W` can change both halves. Cardinality equality occurs only if the signed gains and losses from (Q), summed over ordered pairs, cancel.

## R29-specific conclusion

The permitted archival R29 specification supplies aggregate family counts and the all-anchor value, but not the incidence/row database needed to evaluate the three selector-dependent atoms. The only reconstruction located by the archival structural gate imports a path that `COMMON.md` explicitly forbids. Thus neither universal invariance nor an R29 selector counterexample is independently established from permitted inputs. Extrapolating the all-anchor count `19925` to all `680^676` choices is unsupported.

## Exact checker

```powershell
python tmp/fanout/r29_fullbank_referee/child_03/reach_quotient.py
```

It exhausts all 64 Boolean states of (Q), checks minimal witnesses, uses no floats, and imports no R29 fixture.
