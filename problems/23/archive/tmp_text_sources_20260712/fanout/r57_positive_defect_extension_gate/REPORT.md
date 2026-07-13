# R57 positive-defect extension gate

## Verdict

The literal 16-vertex same-atom fork is **not** an R55 positive-unit-defect
saturated exclusive-fork rotor.  Either selected `s-t` row has no collision
obligations, hence exact grouped defect zero, no unmatched root, and no local
unit core.

No realization exists in any exhaustively tested minimal extension class:

- fixed blue graph, every compatible simple bad atom: 27 candidates;
  27 singleton systems survive and all have lex defect zero;
  no pair preserves maximum-cut optimality;
- one legal blue edge on the same vertices: 42 blue additions,
  1092 one-atom and
  772 two-atom systems survive, all lex defect zero;
  no three-atom system survives;
- one new private blue leaf: 16 attachments,
  496 one-atom and
  24 two-atom systems survive, all lex defect zero;
  no three-atom system survives.

Thus a realization, if one exists, needs a genuinely larger protection gadget:
at least two non-pendant blue-edge edits or a more general multi-edge vertex
extension.  This is a finite lower bound in the stated extension universe, not
a universal proof of `noPositiveDefectSaturatedExclusiveForkRotor`.

## Exact checks

The base graph replay exhausts 32768 cuts modulo
complementation.  Its maximum is 16, displayed Gamma is
25, and the complete shortest `s-t` row family has
2 rows.  All corrected global soft-cap flows
use the six R53 relation families, literal key capacity one, and active-edge
group capacity two.

R55 local unit defect is checked separately from global defect: start at the
least unmatched obligation of an exact optimal integral flow, traverse the
full obligation/key/group residual network, and verify
`obligationCount = sourceCapacity + 1`, where active four-key blocks contribute
at most two.  The first positive non-lex control occurs at 7 duplicate atoms with global defect 28; its least-root residual core has |O_K|=97 and cap(S_K)=96.  It is not lex-minimal, so it is not an R55 state.

TICK-117 leaves the successor and sink bodies checker-defined.  This gate makes
that instantiation explicit: successors are the two matched obligations reached
by reversing the saturated divergence keys; the sink is their full residual
BFS closure; noSimultaneous means one selected row per bad atom.

All arithmetic is integer arithmetic.  No floating point, randomized search,
or tolerance is used.  Integrality of this finite grouped network gives the
same optimum as its rational relaxation.

## Replay

From `E:\Projects\ErdosProblems`:

```powershell
python -B tmp/fanout/r57_positive_defect_extension_gate/check_gate.py
```

The command rewrites `result.json` and `REPORT.md` deterministically and prints
their SHA-256 digests.

## Digests

```text
check_gate.py       323AA8AA45C4F51D1E829D0E38E81D28E644E99D90C1DA2580D82E03D12B3DFA
global_softcap.py   32C7F9BC0C4D2921D3B1FA5D8557ADA0088EEE8A024FDB90330023060101AC13
result.json         9CF4F5902F789E504C85FD7AF13061DD83F4FAF56CA17A1D02335C79370C6044
```
