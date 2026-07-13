# Four-pattern transfer relation: executable specification

## Status and authority

This specification resolves the writeup/code mismatch in favor of the corrected full-obligation implementation in `problems/23/writeup/_codex_r23_outside_attachment_full_obligation_gate.py`.  The original R23 gate explicitly uses collision-only demand and capacity two for every cell (`_claude_r23_outside_attachment_gate.py:86-90,134-145`); the corrected gate identifies the missing active reservations and `HitNeed` (`_codex_r23_outside_attachment_full_obligation_gate.py:1-17`) and implements both.  Thus the original gate is evidence for pattern-4 geometry, not the normative full-bank ledger.

All quantities below are integers in **half-slot units**.  To recover token mass, divide every demand and capacity by `2K`; no floating point is permitted.  This agrees with the terminal mass `1/(2K)` in R20 (`WALL_ATTACK_R20_GPTPRO56.md:26-32`) and R23 (`WALL_ATTACK_R23_GPTPRO56.md:29-32`).

## Inputs and derived objects

Input is `(V,B,M,rows)`, where `B` is the displayed cut/blue edge set, `M` the bad atoms, and `rows` contains one selected length-4 blue path (five vertices) for each bad atom.

Use unordered graph edges `edge(x,y)={x,y}`, but ordered pair cells `(x,y)`.

```text
n[x,y] = number of selected rows containing both x and y
r[x]   = number of selected rows containing x
U      = union of all selected-row vertices
F      = union of consecutive edges of selected rows
I      = { e in B : endpoints(e) subset U and e notin F }
```

These definitions are implemented at `_codex_r23_outside_attachment_full_obligation_gate.py:152-165`.

Form connected components of `(U,I)`.  A component is **active** iff it contains both endpoints of some selected bad atom.  Let `A` be the vertices in active components and `I_A` the edges of `I` in active components.  This is the corrected scope at `_codex_r23_outside_attachment_full_obligation_gate.py:167-197`; in particular, activity is not merely “incident with an active edge.”

For the active-scoped gate:

```text
owners = A
reserved = I_A
degA[v] = degree of v in I_A
collision[v] = 2 * sum_y max(n[v,y]-1,0)
T[v] = 5*r[v]
HitNeed[v] = max(0, degA[v] - max(0, |V|-T[v]))
demand[v] = collision[v] + HitNeed[v]
```

Only positive-demand owners enter the flow.  The formulas and scoping occur at `_codex_r23_outside_attachment_full_obligation_gate.py:190-222`; the standalone active score repeats them at lines 83-145.  `collision[v]` already counts both half-bits, whereas `HitNeed[v]` is one half-slot per residual hit.

## Free cells, reservations, multiplicity, and source identity

A cell `(x,y)` is free iff `x != y` and `n[x,y]=0`.  Its half-slot capacity is

```text
cap(x,y) = 1  if edge(x,y) in reserved
           2  otherwise.
```

The capacity-one case is the active half-zero reservation; all other free ordered cells have two half-bits.  This is stated and implemented at `_codex_r23_outside_attachment_full_obligation_gate.py:267-277`.  R23 also notes that pattern-4 outside pairs cannot be active orientations, hence retain both bits (`WALL_ATTACK_R23_GPTPRO56.md:11-13`).

The atomic source identifier is `(x,y,h)` with integer `h` satisfying `0 <= h < cap(x,y)`.  A cell is created once globally, irrespective of how many patterns or owners witness it.  In code, owner-cell arcs are a set and each cell has one sink arc (`_codex_r23_outside_attachment_full_obligation_gate.py:279-311,313-329`).  Therefore:

- duplicate witnesses do not add capacity;
- membership in several patterns does not add capacity;
- reachability from several owners does not add capacity;
- `(x,y)` and `(y,x)` are distinct ordered cells;
- the two half-bits of an unreserved cell are distinct sources;
- the sink capacity enforces global, cross-owner source deduplication.

This is the executable meaning of R23's “shared eligibility never creates shared capacity” (`WALL_ATTACK_R23_GPTPRO56.md:25-28`) and R20's injective `sourceId` requirement (`WALL_ATTACK_R20_GPTPRO56.md:39-50`).

If an orbit-compressed implementation is used, an orbit `O` has capacity equal to the number of surviving atomic `(x,y,h)` sources in `O`, not the number of witnesses and not the number of adjacent owners.  R20 prescribes source/orbit and free-orbit multiplicities with infinite middle arcs (`WALL_ATTACK_R20_GPTPRO56.md:39-46`).  A safe integer infinity is `1 + sum_v demand[v]`.

## The four predicates

Every predicate below first requires `free(x,y)`.

### 1. `sameFirst(v,x,y)`

```text
sameFirst(v,x,y) := x = v.
```

Equivalently the source cell is `(v,y)`, `y != v`, and `n[v,y]=0`.  See `_codex_r23_outside_attachment_full_obligation_gate.py:281-284`.  “sameOwner” in the scripts and “sameFirst” in R20 refer to this same ordered-first-coordinate rule.

### 2. `commonBad(v,x,y)`

```text
commonBad(v,x,y) := edge(v,x) in M and edge(v,y) in M.
```

The historical implementation also explicitly checks `loss({x,y}) >= 0` (`_claude_r23_outside_attachment_gate.py:111-115`).  On a certified maximum cut this inequality is automatic for every switch set (`WALL_ATTACK_R20_GPTPRO56.md:22-25`), but an executable checker should retain the exact check unless maximum-cut certification is an input invariant.

In the corrected code `commonBad` is not separately inserted because it is a subcase of positive row co-occurrence/`rowCompanion` (`_codex_r23_outside_attachment_full_obligation_gate.py:286-295`).  It remains a named explanatory pattern, not extra capacity.

### 3. `rowCompanion(v,x,y)`

```text
rowCompanion(v,x,y) := n[v,x] > 0 and n[v,y] > 0
                       and loss({x,y}) >= 0.
```

Here `x != v`, `y != v`, and `x != y` follow from the source enumeration/free-cell requirement.  Positive co-occurrence means that each coordinate lies on at least one selected row through owner `v`; freeness forces the two witnesses to be distinct selected rows.  This matches R20's definition (`WALL_ATTACK_R20_GPTPRO56.md:26-32`) and corrected code (`_codex_r23_outside_attachment_full_obligation_gate.py:286-295`).

### 4. `outsideAttachment(v,x,y)`

Build connected components `K` of the induced blue graph `B[V-U]`.  For each component,

```text
Att(K) = { a in U : exists z in K with edge(a,z) in B }.
eligible(v,K) := exists a in Att(K), n[v,a] > 0.
outsideAttachment(v,x,y) := x,y in V-U
  and eligible(v,K(x)) and eligible(v,K(y))
  and loss(K(x) union K(y)) >= 0.
```

The component/attachment construction is implemented at `_codex_r23_outside_attachment_full_obligation_gate.py:229-259`, and the relation at lines 297-311.  The original definition and its non-local intent are at `WALL_ATTACK_R23_GPTPRO56.md:7-15`.  `K(x)=K(y)` is allowed; union is set union, so the loss is computed once on that component.  Attachment witnesses may differ by coordinate.  No separate `comp(a)=comp(v)` test appears in the corrected executable code; the writeup's component-equality phrase (`WALL_ATTACK_R23_GPTPRO56.md:9-11`) is therefore treated as terminal bookkeeping, not an additional eligibility filter.

Exact switch loss is

```text
loss(S) = |{e in B : e crosses S}| - |{e in M : e crosses S}|.
```

See `_codex_r23_outside_attachment_full_obligation_gate.py:261-265`.  Loss magnitude never creates capacity (`WALL_ATTACK_R23_GPTPRO56.md:11-12`).

## Relation, flow, shore reach, and verdict

Define

```text
R(v,(x,y)) := free(x,y) and
  (sameFirst(v,x,y) or commonBad(v,x,y) or
   rowCompanion(v,x,y) or outsideAttachment(v,x,y)).
```

Construct the integral network:

```text
source -> owner v       capacity demand[v]
owner v -> cell (x,y)   capacity cap(x,y), iff R(v,(x,y))
cell (x,y) -> sink      capacity cap(x,y)
```

The tuple passes iff max-flow equals `sum_v demand[v]` (`_codex_r23_outside_attachment_full_obligation_gate.py:313-353`).

For an owner shore `W`, its reach is the **deduplicated capacity union**

```text
Reach(W) = sum_{cell c : exists v in W, R(v,c)} cap(c).
D(W) = sum_{v in W} demand[v].
```

Hall requires `D(W) <= Reach(W)` for every `W`.  Never add per-pattern reach totals unless their atomic source sets were explicitly made disjoint first.  The R28 reported hub shore includes three reservations and has `D=19950`, reach `17235+2600=19835`, gap `115` (`WALL_ATTACK_R28_GPTPRO56.md:13-17`).  The corrected R29 three-hub shore has demand `19953` including three `HitNeed`, reach `17325+2600=19925`, gap `28` (`WALL_ATTACK_R29_GPTPRO56.md:17-20`).  These are half-slot counts.

## Audit conclusions

1. The full-bank executable semantics are **active-scoped collision plus HitNeed**, not collision-only and not all-owner scope.
2. Reservations reduce an active ordered cell from two half sources to one; they do not delete the whole cell.
3. The four patterns are eligibility predicates over one shared source bank.  They never mint separate pattern capacity.
4. Source deduplication is by `(ordered cell, half-bit)` globally across owners and witnesses.
5. Orbit capacity is atomic surviving-source multiplicity; shore reach is the capacity of the union of reachable orbits/cells.
6. `commonBad` is semantically retained but is subsumed by `rowCompanion` in the corrected implementation.
7. The extra component-equality wording in R23 is not enforced by the existing corrected gate and must not silently be added to a reproduction of its numerical claims.

