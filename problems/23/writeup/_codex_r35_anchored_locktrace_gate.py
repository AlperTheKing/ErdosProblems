"""Exact checker for the corrected anchored R35 lock-trace interface.

This module deliberately proves no geometric progress theorem.  It checks a
finite trace context, explores its complete typed transition relation, and
returns one of the four honest terminal certificates: augment, trade,
closedCycle, or deadEnd.  In particular, cursor repetition is never promoted
to a trade.

The graph adapter at the bottom reconstructs the pinned N=12 collision
falsifier from the existing exact census implementation.  The 2943 check is
an integrity/ledger audit of the existing exact certificate; rebuilding its
8,363,362-source relation is intentionally outside this small trace gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[3]
R32 = ROOT / "tmp" / "fanout" / "r32_n12_fullbank"
P5 = ROOT / "tmp" / "fanout" / "p5_n12_census"
PHT = ROOT / "tmp" / "fanout" / "pht_n12_direct"
sys.path[:0] = [str(R32), str(P5), str(PHT), str(Path(__file__).parent)]


Atom = tuple[int, int]
Row = tuple[int, ...]


def canonical_sha(value: object) -> str:
    raw = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True, order=True)
class CollisionObligation:
    owner: int
    other: int
    producer_atom: int
    occurrence: int
    copy: int
    half: int
    component: int


@dataclass(frozen=True, order=True)
class Source:
    source_x: int
    source_y: int
    half: int
    component: int

    @property
    def base(self) -> tuple[int, int]:
        return self.source_x, self.source_y


@dataclass(frozen=True, order=True)
class RowOccurrence:
    atom: int
    row: int
    position: int


class CursorKind(str, Enum):
    OBLIGATION = "obligation"
    SOURCE = "source"
    ROW_OCCURRENCE = "rowOccurrence"


@dataclass(frozen=True, order=True)
class LockTraceCursor:
    kind: CursorKind
    value: CollisionObligation | Source | RowOccurrence

    @staticmethod
    def obligation(value: CollisionObligation) -> "LockTraceCursor":
        return LockTraceCursor(CursorKind.OBLIGATION, value)

    @staticmethod
    def source(value: Source) -> "LockTraceCursor":
        return LockTraceCursor(CursorKind.SOURCE, value)

    @staticmethod
    def row_occurrence(value: RowOccurrence) -> "LockTraceCursor":
        return LockTraceCursor(CursorKind.ROW_OCCURRENCE, value)


class StepKind(str, Enum):
    ELIGIBLE_SOURCE = "eligibleSource"
    MATCHED_OBLIGATION = "matchedObligation"
    PRODUCER_OCCURRENCE = "producerOccurrence"
    OCCURRENCE_OBLIGATION = "occurrenceObligation"
    OCCURRENCE_SOURCE = "occurrenceSource"


@dataclass(frozen=True)
class LockTraceStep:
    kind: StepKind
    before: LockTraceCursor
    after: LockTraceCursor


Matching = Mapping[CollisionObligation, Source]


@dataclass(frozen=True)
class AugmentCertificate:
    new_matching: tuple[tuple[CollisionObligation, Source], ...]


@dataclass(frozen=True)
class TradeCertificate:
    new_obligations: tuple[CollisionObligation, ...]
    new_eligible: tuple[tuple[CollisionObligation, Source], ...]
    new_matching: tuple[tuple[CollisionObligation, Source], ...]
    new_row_rank: int
    strict_defect_drop: bool


@dataclass(frozen=True)
class AugmentResult:
    terminal: str
    cursor: LockTraceCursor
    path: tuple[LockTraceStep, ...]
    certificate: AugmentCertificate


@dataclass(frozen=True)
class TradeResult:
    terminal: str
    cursor: LockTraceCursor
    path: tuple[LockTraceStep, ...]
    certificate: TradeCertificate


@dataclass(frozen=True)
class ClosedCycleResult:
    terminal: str
    prefix: tuple[LockTraceStep, ...]
    cycle: tuple[LockTraceStep, ...]


@dataclass(frozen=True)
class DeadEndResult:
    terminal: str
    reachable: tuple[LockTraceCursor, ...]
    explored_steps: tuple[LockTraceStep, ...]


SearchResult = AugmentResult | TradeResult | ClosedCycleResult | DeadEndResult


@dataclass
class LockTraceContext:
    atoms: tuple[Atom, ...]
    rows_by_atom: tuple[tuple[Row, ...], ...]
    obligations: frozenset[CollisionObligation]
    sources: frozenset[Source]
    eligible: frozenset[tuple[CollisionObligation, Source]]
    matching: dict[CollisionObligation, Source]
    root: CollisionObligation
    row_obligations: dict[RowOccurrence, tuple[CollisionObligation, ...]]
    row_sources: dict[RowOccurrence, tuple[Source, ...]]
    augment_terminals: dict[LockTraceCursor, AugmentCertificate]
    trade_terminals: dict[LockTraceCursor, TradeCertificate]
    row_rank: int = 0

    def validate(self) -> None:
        if len(self.atoms) != len(self.rows_by_atom):
            raise AssertionError("atom/row-family arity mismatch")
        normalized_atoms = [tuple(sorted(atom)) for atom in self.atoms]
        if len(set(normalized_atoms)) != len(normalized_atoms):
            raise AssertionError("atom endpoint pairs are not injective")
        all_rows: set[Row] = set()
        for atom_index, (atom, family) in enumerate(
            zip(self.atoms, self.rows_by_atom)
        ):
            if not family:
                raise AssertionError(f"atom {atom_index} has no rows")
            for row in family:
                if len(row) < 2 or tuple(sorted((row[0], row[-1]))) != tuple(
                    sorted(atom)
                ):
                    raise AssertionError(
                        f"row {row} is not endpoint-anchored at atom {atom}"
                    )
                if len(set(row)) != len(row):
                    raise AssertionError(f"row {row} is not vertex-simple")
                if row in all_rows:
                    raise AssertionError("distinct atoms/families share a row")
                all_rows.add(row)
        if self.root not in self.obligations:
            raise AssertionError("root is not an obligation")
        if self.root in self.matching:
            raise AssertionError("root must be unmatched")
        check_matching(self, self.matching)
        for obligation, source in self.eligible:
            if obligation not in self.obligations or source not in self.sources:
                raise AssertionError("eligibility escapes the finite carriers")
            if obligation.component != source.component:
                raise AssertionError("eligibility changes the global component label")
        for occurrence, obligations in self.row_obligations.items():
            self._check_occurrence(occurrence)
            if any(item not in self.obligations for item in obligations):
                raise AssertionError("row occurrence points outside obligations")
        for occurrence, sources in self.row_sources.items():
            self._check_occurrence(occurrence)
            if any(item not in self.sources for item in sources):
                raise AssertionError("row occurrence points outside sources")
        for cursor, certificate in self.augment_terminals.items():
            check_augment_terminal(self, cursor, certificate)
        for cursor, certificate in self.trade_terminals.items():
            check_trade_terminal(self, cursor, certificate)

    def _check_occurrence(self, occurrence: RowOccurrence) -> None:
        if not 0 <= occurrence.atom < len(self.rows_by_atom):
            raise AssertionError("row occurrence atom out of range")
        family = self.rows_by_atom[occurrence.atom]
        if not 0 <= occurrence.row < len(family):
            raise AssertionError("row occurrence row out of range")
        if not 0 <= occurrence.position < len(family[occurrence.row]):
            raise AssertionError("row occurrence position out of range")


def check_matching(ctx: LockTraceContext, matching: Matching) -> None:
    if not set(matching) <= ctx.obligations:
        raise AssertionError("matching contains a non-obligation")
    used: set[Source] = set()
    base_component: dict[tuple[int, int], int] = {}
    for obligation, source in matching.items():
        if source not in ctx.sources:
            raise AssertionError("matching uses a non-source")
        if (obligation, source) not in ctx.eligible:
            raise AssertionError("matching uses an ineligible source")
        if source in used:
            raise AssertionError("matching spends a source twice")
        used.add(source)
        previous = base_component.setdefault(source.base, obligation.component)
        if previous != obligation.component or source.component != obligation.component:
            raise AssertionError("baseOwner/component coherence violation")


def _tuple_matching(
    pairs: Sequence[tuple[CollisionObligation, Source]],
) -> dict[CollisionObligation, Source]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise AssertionError("certificate assigns an obligation twice")
    return result


def check_augment_terminal(
    ctx: LockTraceContext,
    cursor: LockTraceCursor,
    certificate: AugmentCertificate,
) -> None:
    if cursor.kind not in set(CursorKind):
        raise AssertionError("bad terminal cursor")
    new_matching = _tuple_matching(certificate.new_matching)
    check_matching(ctx, new_matching)
    if len(new_matching) <= len(ctx.matching):
        raise AssertionError("augmentation does not increase matched cardinality")
    if not set(ctx.matching) <= set(new_matching):
        raise AssertionError("augmentation loses an old covered obligation")


def check_trade_terminal(
    ctx: LockTraceContext,
    cursor: LockTraceCursor,
    certificate: TradeCertificate,
) -> None:
    del cursor
    obligations = frozenset(certificate.new_obligations)
    eligible = frozenset(certificate.new_eligible)
    matching = _tuple_matching(certificate.new_matching)
    if not set(matching) <= obligations:
        raise AssertionError("trade matching escapes new obligations")
    if any(pair not in eligible for pair in matching.items()):
        raise AssertionError("trade matching uses an ineligible pair")
    if len(set(matching.values())) != len(matching):
        raise AssertionError("trade matching spends a source twice")
    base_component: dict[tuple[int, int], int] = {}
    for obligation, source in matching.items():
        previous = base_component.setdefault(source.base, obligation.component)
        if previous != obligation.component or source.component != obligation.component:
            raise AssertionError("trade violates baseOwner/component coherence")
    old_defect = len(ctx.obligations) - len(ctx.matching)
    new_defect = len(obligations) - len(matching)
    if certificate.strict_defect_drop:
        if not new_defect < old_defect:
            raise AssertionError("claimed strict trade does not lower defect")
    elif not (new_defect <= old_defect and certificate.new_row_rank < ctx.row_rank):
        raise AssertionError("lex trade lacks explicit nonincrease and rank decrease")


def check_lock_trace_step(ctx: LockTraceContext, step: LockTraceStep) -> None:
    before, after = step.before, step.after
    if step.kind is StepKind.ELIGIBLE_SOURCE:
        if before.kind is not CursorKind.OBLIGATION or after.kind is not CursorKind.SOURCE:
            raise AssertionError("eligibleSource has wrong cursor sorts")
        if (before.value, after.value) not in ctx.eligible:
            raise AssertionError("eligibleSource is not graph-realized")
    elif step.kind is StepKind.MATCHED_OBLIGATION:
        if before.kind is not CursorKind.SOURCE or after.kind is not CursorKind.OBLIGATION:
            raise AssertionError("matchedObligation has wrong cursor sorts")
        if ctx.matching.get(after.value) != before.value:
            raise AssertionError("matchedObligation disagrees with matching cursor")
    elif step.kind is StepKind.PRODUCER_OCCURRENCE:
        if before.kind is not CursorKind.OBLIGATION or after.kind is not CursorKind.ROW_OCCURRENCE:
            raise AssertionError("producerOccurrence has wrong cursor sorts")
        obligation = before.value
        occurrence = after.value
        ctx._check_occurrence(occurrence)
        if occurrence.atom != obligation.producer_atom or occurrence.position != obligation.occurrence:
            raise AssertionError("producer occurrence lost atom/occurrence identity")
    elif step.kind is StepKind.OCCURRENCE_OBLIGATION:
        if before.kind is not CursorKind.ROW_OCCURRENCE or after.kind is not CursorKind.OBLIGATION:
            raise AssertionError("occurrenceObligation has wrong cursor sorts")
        if after.value not in ctx.row_obligations.get(before.value, ()):
            raise AssertionError("unchecked occurrence-to-obligation transition")
    elif step.kind is StepKind.OCCURRENCE_SOURCE:
        if before.kind is not CursorKind.ROW_OCCURRENCE or after.kind is not CursorKind.SOURCE:
            raise AssertionError("occurrenceSource has wrong cursor sorts")
        if after.value not in ctx.row_sources.get(before.value, ()):
            raise AssertionError("unchecked occurrence-to-source transition")
    else:  # pragma: no cover - Enum makes this defensive only.
        raise AssertionError("unknown lock-trace step")


def outgoing_steps(ctx: LockTraceContext, cursor: LockTraceCursor) -> tuple[LockTraceStep, ...]:
    out: list[LockTraceStep] = []
    if cursor.kind is CursorKind.OBLIGATION:
        obligation = cursor.value
        for source in sorted(s for d, s in ctx.eligible if d == obligation):
            out.append(LockTraceStep(
                StepKind.ELIGIBLE_SOURCE, cursor, LockTraceCursor.source(source)
            ))
        occurrence = RowOccurrence(
            obligation.producer_atom, 0, obligation.occurrence
        )
        try:
            ctx._check_occurrence(occurrence)
        except AssertionError:
            pass
        else:
            out.append(LockTraceStep(
                StepKind.PRODUCER_OCCURRENCE,
                cursor,
                LockTraceCursor.row_occurrence(occurrence),
            ))
    elif cursor.kind is CursorKind.SOURCE:
        for obligation, source in sorted(ctx.matching.items()):
            if source == cursor.value:
                out.append(LockTraceStep(
                    StepKind.MATCHED_OBLIGATION,
                    cursor,
                    LockTraceCursor.obligation(obligation),
                ))
    else:
        occurrence = cursor.value
        for obligation in sorted(ctx.row_obligations.get(occurrence, ())):
            out.append(LockTraceStep(
                StepKind.OCCURRENCE_OBLIGATION,
                cursor,
                LockTraceCursor.obligation(obligation),
            ))
        for source in sorted(ctx.row_sources.get(occurrence, ())):
            out.append(LockTraceStep(
                StepKind.OCCURRENCE_SOURCE,
                cursor,
                LockTraceCursor.source(source),
            ))
    result = tuple(out)
    for step in result:
        check_lock_trace_step(ctx, step)
    return result


def lock_trace_search(ctx: LockTraceContext) -> SearchResult:
    """Explore the complete reachable finite state graph deterministically."""
    ctx.validate()
    root = LockTraceCursor.obligation(ctx.root)
    queue = deque([root])
    parent: dict[LockTraceCursor, LockTraceStep | None] = {root: None}
    adjacency: dict[LockTraceCursor, tuple[LockTraceStep, ...]] = {}
    explored: list[LockTraceStep] = []

    def path_to(cursor: LockTraceCursor) -> tuple[LockTraceStep, ...]:
        reverse: list[LockTraceStep] = []
        while parent[cursor] is not None:
            step = parent[cursor]
            assert step is not None
            reverse.append(step)
            cursor = step.before
        return tuple(reversed(reverse))

    while queue:
        cursor = queue.popleft()
        if cursor in ctx.augment_terminals:
            certificate = ctx.augment_terminals[cursor]
            check_augment_terminal(ctx, cursor, certificate)
            return AugmentResult("augment", cursor, path_to(cursor), certificate)
        if cursor in ctx.trade_terminals:
            certificate = ctx.trade_terminals[cursor]
            check_trade_terminal(ctx, cursor, certificate)
            return TradeResult("trade", cursor, path_to(cursor), certificate)
        steps = outgoing_steps(ctx, cursor)
        adjacency[cursor] = steps
        explored.extend(steps)
        for step in steps:
            if step.after not in parent:
                parent[step.after] = step
                queue.append(step.after)

    # No checked progress terminal exists.  Classify the reachable graph
    # honestly: a repeat is closedCycle, otherwise the finite search is deadEnd.
    color: dict[LockTraceCursor, int] = {}
    stack: list[LockTraceCursor] = []
    stack_steps: list[LockTraceStep] = []

    def cycle_from(cursor: LockTraceCursor) -> ClosedCycleResult | None:
        color[cursor] = 1
        stack.append(cursor)
        for step in adjacency.get(cursor, ()):
            target = step.after
            if color.get(target, 0) == 0:
                stack_steps.append(step)
                found = cycle_from(target)
                if found is not None:
                    return found
                stack_steps.pop()
            elif color[target] == 1:
                start = stack.index(target)
                cycle = tuple(stack_steps[start:] + [step])
                return ClosedCycleResult("closedCycle", path_to(target), cycle)
        stack.pop()
        color[cursor] = 2
        return None

    found = cycle_from(root)
    if found is not None:
        return found
    return DeadEndResult(
        "deadEnd", tuple(sorted(parent)), tuple(explored)
    )


def _self_test() -> dict:
    atoms = ((0, 4),)
    rows = (((0, 1, 2, 3, 4),),)
    d0 = CollisionObligation(1, 2, 0, 1, 0, 0, 7)
    d1 = CollisionObligation(1, 2, 0, 1, 0, 1, 7)
    s0 = Source(5, 6, 0, 7)
    occurrence = RowOccurrence(0, 0, 1)

    def context(*, matching=(), row_back=True, augment=None, trade=None):
        return LockTraceContext(
            atoms=atoms,
            rows_by_atom=rows,
            obligations=frozenset((d0, d1)),
            sources=frozenset((s0,)),
            eligible=frozenset(((d0, s0), (d1, s0))),
            matching=dict(matching),
            root=d0,
            row_obligations={occurrence: (d0,)} if row_back else {},
            row_sources={},
            augment_terminals=augment or {},
            trade_terminals=trade or {},
            row_rank=9,
        )

    augment_cursor = LockTraceCursor.source(s0)
    augment_cert = AugmentCertificate(((d0, s0),))
    assert lock_trace_search(context(
        row_back=False, augment={augment_cursor: augment_cert}
    )).terminal == "augment"

    trade_cursor = LockTraceCursor.row_occurrence(occurrence)
    trade_cert = TradeCertificate(
        (d0,), ((d0, s0),), ((d0, s0),), 8, True
    )
    assert lock_trace_search(context(
        row_back=False, trade={trade_cursor: trade_cert}
    )).terminal == "trade"
    assert lock_trace_search(context(matching=((d1, s0),))).terminal == "closedCycle"
    assert lock_trace_search(context(row_back=False)).terminal == "deadEnd"

    # The payload fields omitted by R34 really distinguish cursors.
    variants = {
        LockTraceCursor.obligation(d0),
        LockTraceCursor.obligation(d1),
        LockTraceCursor.row_occurrence(occurrence),
        LockTraceCursor.source(s0),
    }
    assert len(variants) == 4
    return {"terminals": ["augment", "trade", "closedCycle", "deadEnd"],
            "distinctCursorPayloads": len(variants)}


def _n12_artifact_test() -> dict:
    from _codex_r19_global_base_census import dec, loads
    from _codex_r20_two_row_exchange_gate import shortest_row_families
    from _codex_r23_heavy_alltuple_descent_gate import rows_for_choice
    from collision_only_core import analyze_collision_only
    from p5_core import make_graph_context

    artifact = json.loads((R32 / "census_n12.json").read_text())
    record = artifact["bands"]["heavy"]["first"]["firstTupleFalsifier"]
    n, edges = dec(record["g6"])
    info = loads(n, edges)
    assert info is not None
    families = shortest_row_families(info)
    rows = rows_for_choice(families, tuple(record["choice"]))
    graph_ctx = make_graph_context(n, info["Bset"], info["Mset"])
    analysis = analyze_collision_only(graph_ctx, rows, details=True)
    assert analysis["collisionDemand"] == record["collisionDemand"] == 64
    assert analysis["collisionDefect"] == record["collisionDefect"] == 18

    atoms = tuple(tuple(edge) for edge in info["M"])
    selected_families = tuple((tuple(row),) for row in rows)
    components: dict[int, int] = {}
    for component in analysis["state"]["selectedComponents"]:
        label = min(component)
        for vertex in component:
            components[vertex] = label
    occurrence_atoms: dict[tuple[int, int], list[int]] = defaultdict(list)
    for atom_index, row in enumerate(rows):
        for owner in row:
            for other in row:
                occurrence_atoms[owner, other].append(atom_index)
    obligations: list[CollisionObligation] = []
    for owner in analysis["owners"]:
        pair = analysis["state"]["pair"][owner]
        for other, multiplicity in enumerate(pair):
            for copy in range(max(0, multiplicity - 1)):
                producer = occurrence_atoms[owner, other][copy + 1]
                for half in (0, 1):
                    obligations.append(CollisionObligation(
                        owner, other, producer, copy + 1, copy, half,
                        components[owner],
                    ))
    assert len(obligations) == analysis["collisionDemand"]

    assignment_lookup = {
        tuple(item["obligation"]): tuple(item["source"])
        for item in analysis["collisionAssignment"]
    }
    by_short = {(d.owner, d.other, d.copy, d.half): d for d in obligations}
    matching: dict[CollisionObligation, Source] = {}
    sources: set[Source] = set()
    eligible: set[tuple[CollisionObligation, Source]] = set()
    for short, raw_source in assignment_lookup.items():
        obligation = by_short[short]
        source = Source(*raw_source, obligation.component)
        sources.add(source)
        eligible.add((obligation, source))
        matching[obligation] = source
    assert len(matching) == analysis["collisionMatched"] == 46
    root = next(d for d in obligations if d not in matching)
    trace_ctx = LockTraceContext(
        atoms=atoms,
        rows_by_atom=selected_families,
        obligations=frozenset(obligations),
        sources=frozenset(sources),
        eligible=frozenset(eligible),
        matching=matching,
        root=root,
        row_obligations={},
        row_sources={},
        augment_terminals={},
        trade_terminals={},
    )
    result = lock_trace_search(trace_ctx)
    # The exported certificate lists only used eligibility arcs, so the root
    # has no outgoing source arc.  Its valid producer occurrence is retained;
    # without a checked return arc the honest result is deadEnd.
    assert result.terminal == "deadEnd"
    return {
        "g6": record["g6"], "order": n,
        "demand": len(obligations), "matched": len(matching),
        "defect": len(obligations) - len(matching),
        "terminalOnExportedArcs": result.terminal,
        "anchoredRows": len(rows),
    }


def _fixture_2943_test() -> dict:
    path = R32 / "fixture_battery_result.json"
    raw = path.read_bytes()
    payload = json.loads(raw)
    fixture = next(
        item for item in payload["fixtures"]
        if item.get("checked_certificate", {}).get("label")
        == "2943_active_certificate"
    )
    cert = fixture["checked_certificate"]
    assert cert["all_owner_shores_enumerated"] is True
    assert cert["owner_shores_checked"] == (1 << cert["owner_count"]) - 1
    assert cert["full"] is True
    assert cert["max_flow"] == sum(cert["demand_by_owner"].values()) == 23108
    assert cert["minimum_shore_slack"] == 3
    assert len(cert["selected_p5_keys"]) == 28
    return {
        "available": True,
        "fileSha256": hashlib.sha256(raw).hexdigest(),
        "owners": cert["owner_count"],
        "shores": cert["owner_shores_checked"],
        "demand": cert["max_flow"],
        "minimumShoreSlack": cert["minimum_shore_slack"],
        "selectedP5Keys": len(cert["selected_p5_keys"]),
        "note": "certificate audit; full 8,363,362-key relation not rebuilt",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-n12", action="store_true")
    parser.add_argument("--skip-2943", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be in 1..8")
    result = {"selfTest": _self_test(), "exactIntegerOnly": True,
              "workers": args.workers}
    if not args.skip_n12:
        result["n12"] = _n12_artifact_test()
    if not args.skip_2943:
        result["fixture2943"] = _fixture_2943_test()
    result["canonicalSha256"] = canonical_sha(result)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="ascii")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
