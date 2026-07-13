"""Exact countermodel to the turnover-plus-coherence inference in R42.

This is an abstract matching-state model, not a real graph cage.  It uses the
literal production physical-key identity (ordered base, half), reserves half
zero on every active edge orientation, and checks all coherent matchings.
"""

from hashlib import sha256
from itertools import permutations
import json


X, Y, M, V = "x", "y", "m", "v"
OBLIGATIONS = tuple(f"o{i}" for i in range(5))
COMPONENT = {obligation: 0 for obligation in OBLIGATIONS}


def ordered_active_bases(middle):
    return (
        (middle, X), (X, middle),
        (middle, Y), (Y, middle),
    )


def raw_keys(middle):
    return tuple((base, half) for base in ordered_active_bases(middle)
                 for half in (0, 1))


def scoped_reserved(key):
    # Both endpoints of each active edge are ActiveOwner in the SCC component.
    return key[1] == 0


def usable_keys(middle):
    return tuple(key for key in raw_keys(middle) if not scoped_reserved(key))


def coherent(matching):
    # All obligations have component 0.  This directly checks the production
    # BaseKeyComponentCoherent implication on every pair of assignments.
    items = tuple(matching.items())
    for obligation_a, key_a in items:
        for obligation_b, key_b in items:
            if key_a[0] == key_b[0]:
                if COMPONENT[obligation_a] != COMPONENT[obligation_b]:
                    return False
    return True


def all_maximum_matchings(middle):
    sources = usable_keys(middle)
    matchings = []
    for chosen_obligations in permutations(OBLIGATIONS, len(sources)):
        matching = dict(zip(chosen_obligations, sources))
        assert len(set(matching.values())) == len(matching)
        assert coherent(matching)
        matchings.append(matching)
    return matchings


def encode_key(key):
    (a, b), half = key
    return f"{a}>{b}:{half}"


def main():
    states = {}
    for name, middle in (("omega_m", V), ("omega_v", M)):
        raw = raw_keys(middle)
        usable = usable_keys(middle)
        maximum = all_maximum_matchings(middle)
        assert len(raw) == 8
        assert sum(scoped_reserved(key) for key in raw) == 4
        assert len(usable) == 4
        assert len(maximum) == 120
        assert all(len(matching) == 4 for matching in maximum)
        states[name] = {
            "rawFreeKeys": sorted(map(encode_key, raw)),
            "reservedHalfZero": sorted(
                encode_key(key) for key in raw if scoped_reserved(key)
            ),
            "usableHalfOne": sorted(map(encode_key, usable)),
            "obligations": len(OBLIGATIONS),
            "maximumMatchingSize": 4,
            "optimalCoherentMatchings": len(maximum),
            "defect": 1,
        }

    transitions = []
    for source, target in (("omega_m", "omega_v"), ("omega_v", "omega_m")):
        old = set(states[source]["usableHalfOne"])
        new = set(states[target]["usableHalfOne"])
        gained = sorted(new - old)
        lost = sorted(old - new)
        assert len(gained) == len(lost) == 4
        # Every newly gained key occurs in an optimal target matching because
        # the target has exactly four usable keys and maximum size four.
        transitions.append({
            "source": source,
            "target": target,
            "usableLost": lost,
            "usableGained": gained,
            "allGainedConsumedByEveryOptimalTargetMatching": True,
        })

    payload = {
        "schema": "R42_ABSTRACT_SOURCE_SWAP_V1",
        "physicalKey": "(ordered sourceX, ordered sourceY, half)",
        "component": 0,
        "states": states,
        "transitions": transitions,
        "verdict": (
            "TURNOVER_PLUS_BASE_KEY_COMPONENT_COHERENCE_DOES_NOT_IMPLY_"
            "AUGMENTATION_OR_STRICT_TRADE"
        ),
        "scope": "abstract matching-state countermodel; not a real graph cage",
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    print(json.dumps(payload, indent=2, sort_keys=True))
    print("canonical_sha256=" + sha256(canonical.encode("ascii")).hexdigest())


if __name__ == "__main__":
    main()
