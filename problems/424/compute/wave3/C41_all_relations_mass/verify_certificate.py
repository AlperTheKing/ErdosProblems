#!/usr/bin/env python3
"""Independent exact replay of the C41 finite-congruence certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter, deque
from pathlib import Path


LETTERS = "235"
INDEX = {letter: index for index, letter in enumerate(LETTERS)}
ADD = {"2": 0, "3": 1, "5": 3}
TARGET = (15, 10, 6)
Q = 2**15 * 3**10 * 5**6


def offset(word: str) -> int:
    answer = 0
    multiplier = 1
    for letter in word:
        answer += multiplier * ADD[letter]
        multiplier *= int(letter)
    return answer


class Matcher:
    """A separate Aho--Corasick implementation for forbidden factors."""

    def __init__(self, patterns: list[str]):
        children: list[dict[str, int]] = [{}]
        failure = [0]
        terminal = [False]
        for pattern in patterns:
            node = 0
            for letter in pattern:
                child = children[node].get(letter)
                if child is None:
                    child = len(children)
                    children[node][letter] = child
                    children.append({})
                    failure.append(0)
                    terminal.append(False)
                node = child
            terminal[node] = True

        go = [[0, 0, 0] for _ in children]
        queue: deque[int] = deque()
        for letter in LETTERS:
            child = children[0].get(letter)
            if child is None:
                go[0][INDEX[letter]] = 0
            else:
                go[0][INDEX[letter]] = child
                queue.append(child)
        while queue:
            node = queue.popleft()
            if terminal[failure[node]]:
                terminal[node] = True
            for letter in LETTERS:
                index = INDEX[letter]
                child = children[node].get(letter)
                if child is None:
                    go[node][index] = go[failure[node]][index]
                else:
                    failure[child] = go[failure[node]][index]
                    go[node][index] = child
                    queue.append(child)

        self.go = go
        self.terminal = terminal
        safe = [node for node in range(len(children)) if not terminal[node]]
        renumber = {old: new for new, old in enumerate(safe)}
        self.safe_go = [[-1, -1, -1] for _ in safe]
        for old in safe:
            source = renumber[old]
            for index in range(3):
                target = go[old][index]
                if not terminal[target]:
                    self.safe_go[source][index] = renumber[target]
        self.root = renumber[0]
        self.trie_states = len(children)

    def hits(self, word: str) -> bool:
        node = 0
        for letter in word:
            node = self.go[node][INDEX[letter]]
            if self.terminal[node]:
                return True
        return False


def relation_replay(max_length: int):
    minimal: list[str] = []
    digest = hashlib.sha256()
    rows = []
    for length in range(1, max_length + 1):
        representatives: dict[tuple[int, int, int], str] = {}
        fibers: dict[tuple[int, int, int], list[str]] = {}
        for tuple_word in itertools.product(LETTERS, repeat=length):
            word = "".join(tuple_word)
            twos = word.count("2")
            threes = word.count("3")
            key = twos, threes, offset(word)
            first = representatives.get(key)
            if first is None:
                representatives[key] = word
            elif key in fibers:
                fibers[key].append(word)
            else:
                fibers[key] = [first, word]

        matcher = Matcher(minimal)
        sides = [word for words in fibers.values() for word in words]
        additions = sorted(word for word in sides if not matcher.hits(word))
        minimal.extend(additions)

        pair_count = 0
        maximum = 1
        for key in sorted(fibers):
            words = fibers[key]
            size = len(words)
            pair_count += size * (size - 1) // 2
            maximum = max(maximum, size)
            twos, threes, value = key
            fives = length - twos - threes
            digest.update(
                (
                    f"{length}:{twos},{threes},{fives}:{value}:"
                    + ",".join(words)
                    + "\n"
                ).encode("ascii")
            )
        rows.append(
            {
                "length": length,
                "formal_words": 3**length,
                "affine_classes": len(representatives),
                "collision_excess": 3**length - len(representatives),
                "relation_fibers": len(fibers),
                "relation_pairs": pair_count,
                "relation_side_words": len(sides),
                "singleton_words": len(representatives) - len(fibers),
                "maximum_fiber": maximum,
                "new_minimal_sides": len(additions),
            }
        )
    return rows, minimal, digest.hexdigest()


def accepted_counts(matcher: Matcher, maximum: int) -> list[int]:
    current = [0] * len(matcher.safe_go)
    current[matcher.root] = 1
    answer = []
    for _ in range(maximum):
        following = [0] * len(current)
        for state, number in enumerate(current):
            if not number:
                continue
            for target in matcher.safe_go[state]:
                if target >= 0:
                    following[target] += number
        current = following
        answer.append(sum(current))
    return answer


def reachable(start: int, adjacency: list[list[int]], active: set[int]) -> set[int]:
    seen = {start}
    stack = [start]
    while stack:
        state = stack.pop()
        for target in adjacency[state]:
            if target in active and target not in seen:
                seen.add(target)
                stack.append(target)
    return seen


def factor(value: int, exponents: Counter[int], scale: int) -> None:
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor:
            divisor = 3 if divisor == 2 else divisor + 2
            continue
        power = 0
        while value % divisor == 0:
            value //= divisor
            power += 1
        exponents[divisor] += scale * power
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        exponents[value] += scale


def bytes_hash(value: int) -> str:
    encoded = value.to_bytes((value.bit_length() + 7) // 8, "big")
    return hashlib.sha256(encoded).hexdigest()


def verify_edges(certificate: dict, matcher: Matcher):
    transitions = matcher.safe_go
    incoming = [0] * len(transitions)
    outgoing = [0] * len(transitions)
    letter_counts = [0, 0, 0]
    edge_counts: list[int] = []
    adjacency = [[] for _ in transitions]
    reverse = [[] for _ in transitions]
    edge_digest = hashlib.sha256()

    for row in certificate["edges"]:
        source = int(row["source"])
        index = INDEX[row["letter"]]
        target = int(row["target"])
        number = int(row["multiplicity"])
        assert number > 0
        assert transitions[source][index] == target
        outgoing[source] += number
        incoming[target] += number
        letter_counts[index] += number
        edge_counts.append(number)
        adjacency[source].append(target)
        reverse[target].append(source)
        edge_digest.update(
            f"{source},{row['letter']},{target},{number}\n".encode("ascii")
        )

    assert incoming == outgoing
    total = sum(letter_counts)
    assert total % 31 == 0
    ray = total // 31
    assert letter_counts == [value * ray for value in TARGET]
    assert ray == certificate["canonical_k"]
    assert letter_counts == certificate["letter_counts"]
    assert edge_digest.hexdigest() == certificate["edge_sha256"]

    active = {state for state, degree in enumerate(outgoing) if degree}
    start = next(iter(active))
    assert reachable(start, adjacency, active) == active
    assert reachable(start, reverse, active) == active
    assert len(active) == certificate["support_states"]
    assert len(edge_counts) == certificate["support_edges"]

    exponents: Counter[int] = Counter()
    for degree in outgoing:
        if degree:
            factor(degree, exponents, degree)
    for number in edge_counts:
        factor(number, exponents, -number)
    exponents[2] -= TARGET[0] * ray
    exponents[3] -= TARGET[1] * ray
    exponents[5] -= TARGET[2] * ray
    exponents = Counter(
        {prime: exponent for prime, exponent in exponents.items() if exponent}
    )
    stored = [
        [int(prime), int(exponent)]
        for prime, exponent in certificate["entropy_comparison"][
            "prime_exponents"
        ]
    ]
    assert [[p, e] for p, e in sorted(exponents.items())] == stored

    reduced_numerator = 1
    reduced_denominator = 1
    for prime, exponent in exponents.items():
        if exponent > 0:
            reduced_numerator *= prime**exponent
        else:
            reduced_denominator *= prime ** (-exponent)
    assert reduced_numerator > reduced_denominator
    comparison = certificate["entropy_comparison"]
    assert comparison["exact_above_Q"]
    assert bytes_hash(reduced_numerator) == comparison["numerator_sha256"]
    assert bytes_hash(reduced_denominator) == comparison["denominator_sha256"]

    # This direct unreduced product is deliberately independent of the
    # prime-exponent comparison used by the constructor.
    direct_numerator = math.prod(
        degree**degree for degree in outgoing if degree
    )
    direct_denominator = Q**ray * math.prod(
        number**number for number in edge_counts
    )
    assert direct_numerator > direct_denominator
    return {
        "balanced_states": len(transitions),
        "support_states": len(active),
        "support_edges": len(edge_counts),
        "strongly_connected": True,
        "canonical_k": ray,
        "letter_counts": letter_counts,
        "edge_sha256": edge_digest.hexdigest(),
        "prime_exponents_match": True,
        "reduced_product_above_Q": True,
        "direct_product_above_Q": True,
        "direct_numerator_bits": direct_numerator.bit_length(),
        "direct_denominator_bits": direct_denominator.bit_length(),
        "direct_numerator_sha256": bytes_hash(direct_numerator),
        "direct_denominator_sha256": bytes_hash(direct_denominator),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--relations", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    relations = json.loads(args.relations.read_text(encoding="ascii"))
    circulation = json.loads(args.certificate.read_text(encoding="ascii"))
    levels, minimal, fiber_hash = relation_replay(
        relations["max_relation_length"]
    )
    assert fiber_hash == relations["relation_fibers_sha256"]
    assert minimal == relations["minimal_sides"]
    assert hashlib.sha256(
        "".join(word + "\n" for word in minimal).encode("ascii")
    ).hexdigest() == relations["minimal_sides_sha256"]

    matcher = Matcher(minimal)
    accepted = accepted_counts(matcher, len(levels))
    for replay, stored, accepted_words in zip(
        levels, relations["relation_levels"], accepted
    ):
        for key, value in replay.items():
            assert stored[key] == value, (key, stored[key], value)
        assert accepted_words == replay["singleton_words"]
        assert stored["accepted_words"] == accepted_words
    assert matcher.trie_states == relations["automaton"]["trie_states"]
    assert len(matcher.safe_go) == relations["automaton"]["safe_states"]

    edge_result = verify_edges(circulation["certificate"], matcher)
    assert circulation["minimal_sides_sha256"] == relations[
        "minimal_sides_sha256"
    ]
    assert circulation["relation_fibers_sha256"] == relations[
        "relation_fibers_sha256"
    ]

    payload = {
        "schema_version": 1,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "relations_sha256": hashlib.sha256(args.relations.read_bytes()).hexdigest(),
        "certificate_sha256": hashlib.sha256(
            args.certificate.read_bytes()
        ).hexdigest(),
        "relation_replay": {
            "max_length": len(levels),
            "formal_words_at_max_length": 3 ** len(levels),
            "relation_fibers_at_max_length": levels[-1]["relation_fibers"],
            "relation_sides_at_max_length": levels[-1][
                "relation_side_words"
            ],
            "minimal_sides": len(minimal),
            "fiber_sha256": fiber_hash,
            "minimal_sides_sha256": relations["minimal_sides_sha256"],
            "singleton_checks": len(levels),
        },
        "circulation_replay": edge_result,
        "all_checks_passed": True,
    }
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.output.write_text(rendered + "\n", encoding="ascii")
    print(rendered)


if __name__ == "__main__":
    main()
