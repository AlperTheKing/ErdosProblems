"""Exact (integer/finite-set) ActiveScoped invariance audit checks.

These are contract-level R29 states: every state has exactly vertices 0..28.
No claim is made that every state is geometrically realizable by an unstaged
R29 implementation; report.md separates exact interface witnesses from the
remaining realization obligations.
"""

from dataclasses import dataclass, replace
from typing import FrozenSet, Tuple

V = frozenset(range(29))
Pair = Tuple[int, int]


@dataclass(frozen=True)
class State:
    U: FrozenSet[int]
    active_component: Tuple[int, ...]
    attachment_component: Tuple[int, ...]
    attachment_boundary: FrozenSet[int]
    rows: FrozenSet[Pair]
    reserved: FrozenSet[Pair]
    legal: FrozenSet[Tuple[str, int]]
    capacity: Tuple[Tuple[str, int, int], ...]
    first: Tuple[int, ...]
    owner: Tuple[int, ...]
    bad: FrozenSet[int]


BASE = State(
    U=V,
    active_component=tuple(range(29)),
    attachment_component=tuple(range(29)),
    attachment_boundary=frozenset(),
    rows=frozenset(),
    reserved=frozenset(),
    legal=frozenset((k, 0) for k in ("Door", "vertexSlack", "c5Base", "prune")),
    capacity=tuple((k, 0, 1) for k in ("Door", "vertexSlack", "c5Base", "prune")),
    first=tuple(range(29)),
    owner=tuple(range(29)),
    bad=frozenset(),
)


def same_first(s: State, a: int, b: int) -> bool:
    return s.first[a] == s.first[b]


def same_owner(s: State, a: int, b: int) -> bool:
    return s.owner[a] == s.owner[b]


def common_bad(s: State, a: int, b: int) -> bool:
    return a in s.bad and b in s.bad


def row_companion(s: State, a: int, b: int) -> bool:
    return (min(a, b), max(a, b)) in s.rows


def outside_attachment(s: State, a: int) -> bool:
    return a not in s.attachment_component or a in s.attachment_boundary


def source_available(s: State, kind: str, x: int) -> bool:
    cap = dict(((k, y), n) for k, y, n in s.capacity).get((kind, x), 0)
    return (kind, x) in s.legal and cap > 0 and (x, x) not in s.reserved


def flip(field: str, before: State, after: State, pred, *args) -> None:
    changed = [f for f in State.__dataclass_fields__ if getattr(before, f) != getattr(after, f)]
    assert changed == [field], (field, changed)
    assert pred(before, *args) != pred(after, *args), (field, args)


def run() -> None:
    assert len(V) == 29 and min(V) == 0 and max(V) == 28

    # Exact interface witnesses, all on the R29 carrier.
    f = list(BASE.first); f[1] = 0
    flip("first", BASE, replace(BASE, first=tuple(f)), same_first, 0, 1)
    o = list(BASE.owner); o[1] = 0
    flip("owner", BASE, replace(BASE, owner=tuple(o)), same_owner, 0, 1)
    flip("bad", BASE, replace(BASE, bad=frozenset({0, 1})), common_bad, 0, 1)
    flip("rows", BASE, replace(BASE, rows=frozenset({(0, 1)})), row_companion, 0, 1)
    ac = tuple(1 if x == 0 else x for x in BASE.attachment_component)
    flip("attachment_component", BASE, replace(BASE, attachment_component=ac), outside_attachment, 0)
    flip("attachment_boundary", BASE,
         replace(BASE, attachment_boundary=frozenset({0})), outside_attachment, 0)

    for kind in ("Door", "vertexSlack", "c5Base", "prune"):
        legal = BASE.legal - {(kind, 0)}
        flip("legal", BASE, replace(BASE, legal=legal), source_available, kind, 0)
        caps = tuple((k, x, 0 if (k, x) == (kind, 0) else n)
                     for k, x, n in BASE.capacity)
        flip("capacity", BASE, replace(BASE, capacity=caps), source_available, kind, 0)
        flip("reserved", BASE, replace(BASE, reserved=frozenset({(0, 0)})),
             source_available, kind, 0)

    print("PASS carrier=R29 predicate_witnesses=6 source_witnesses=12 floats=0")


if __name__ == "__main__":
    run()
