#!/usr/bin/env python3
"""Exact BC108 search on archived rulers and deterministic named mutations."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable, Sequence

from bc108_core import normalized, reflected, valid_insertions
from search_bc108 import aggregate, canonical_bytes, scan_translation_family, sha256_file


ROOT = Path(__file__).resolve().parents[4]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def archive_bases():
    p86 = load("p86_p116", ROOT / "problems/864/compute/p86/dense_loose_search.py")
    return p86.load_archives()


def named_seeds() -> dict[str, tuple[int, ...]]:
    p108 = load("p108_data_p116", ROOT / "problems/864/compute/p108/audit_sweep_saturation.py")
    seeds = {
        name: tuple(row[0])
        for name, row in p108.mandatory_rows().items()
    }
    p106 = json.loads(
        (ROOT / "problems/864/compute/p106/positive_rm97_falsifier_certificate.json").read_text()
    )
    seeds["P106"] = tuple(p106["B"])
    p110 = json.loads(
        (ROOT / "problems/864/compute/p110/dimension_falsifiers.json").read_text()
    )
    for index, row in enumerate(p110["failures"]):
        seeds[f"P110_{index:02d}"] = tuple(row["B"])
    out: dict[str, tuple[int, ...]] = {}
    for name, values in seeds.items():
        base = normalized(values)
        if len(base) >= 3:
            out[name] = base
            out[name + "_reflected"] = reflected(base)
    return out


def mutation_bases(
    seeds: dict[str, tuple[int, ...]], max_swap_width: int,
) -> tuple[list[tuple[tuple[int, ...], tuple[str, ...]]], dict[str, object]]:
    sources: dict[tuple[int, ...], set[str]] = {}
    counts = {
        "seeds": len(seeds),
        "one_deletion_raw": 0,
        "direct_insertion_raw": 0,
        "one_swap_raw": 0,
    }
    seed_rows = {}
    for name, base in seeds.items():
        local = {"p": len(base), "width": base[-1]}
        for index in range(len(base)):
            row = base[:index] + base[index + 1:]
            if len(row) < 3:
                continue
            row = normalized(row)
            for oriented in (row, reflected(row)):
                sources.setdefault(oriented, set()).add(f"{name}/delete={index}")
                counts["one_deletion_raw"] += 1

        insertions = list(valid_insertions(base, 0, base[-1]))
        local["direct_sidonic_insertions"] = len(insertions)
        for value in insertions:
            row = tuple(sorted(base + (value,)))
            for oriented in (row, reflected(row)):
                sources.setdefault(oriented, set()).add(f"{name}/insert={value}")
                counts["direct_insertion_raw"] += 1

        swaps = 0
        if base[-1] <= max_swap_width:
            for index in range(len(base) - 1):
                deleted = base[index]
                remainder = base[:index] + base[index + 1:]
                for value in valid_insertions(remainder, 0, base[-1]):
                    if value == deleted:
                        continue
                    row = tuple(sorted(remainder + (value,)))
                    for oriented in (row, reflected(row)):
                        sources.setdefault(oriented, set()).add(
                            f"{name}/swap={deleted}->{value}"
                        )
                        counts["one_swap_raw"] += 1
                    swaps += 1
        local["endpoint_one_swaps"] = swaps
        seed_rows[name] = local
    rows = [
        (base, tuple(sorted(labels)))
        for base, labels in sorted(sources.items())
    ]
    return rows, {
        **counts,
        "distinct_mutated_orientations": len(rows),
        "max_swap_width": max_swap_width,
        "seed_rows": seed_rows,
    }


def worker(payload: tuple[int, tuple[int, ...], tuple[str, ...]]) -> dict[str, object]:
    index, base, sources = payload
    digest = hashlib.sha256()
    source = " | ".join(sources[:3])
    if len(sources) > 3:
        source += f" | +{len(sources) - 3}"
    row = scan_translation_family(base, source, digest)
    return {
        "width": base[-1],
        "first_internal_mark": index,
        "base": list(base),
        "sources": list(sources),
        "decision_sha256": digest.hexdigest(),
        **row,
    }


def run_payloads(payloads, workers: int):
    if workers == 1:
        return [worker(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(worker, payloads, chunksize=1))


def compact_aggregate(shards: Sequence[dict[str, object]]) -> dict[str, object]:
    result = aggregate(shards)
    result["shards"] = [
        {
            "base": shard["base"],
            "sources": shard["sources"],
            "decision_sha256": shard["decision_sha256"],
            **{
                key: value for key, value in shard.items()
                if isinstance(value, int)
                and key not in ("width", "first_internal_mark")
            },
        }
        for shard in shards
    ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=48)
    parser.add_argument("--max-swap-width", type=int, default=2000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.workers <= 61:
        raise ValueError("workers must be in [1,61] on Windows ProcessPool")

    bases, archive_manifest = archive_bases()
    archive_payloads = [
        (index, tuple(base.values), tuple(base.sources))
        for index, base in enumerate(bases)
    ]
    archive_rows = run_payloads(archive_payloads, args.workers)

    seeds = named_seeds()
    mutations, mutation_domain = mutation_bases(seeds, args.max_swap_width)
    mutation_payloads = [
        (index, base, sources)
        for index, (base, sources) in enumerate(mutations)
    ]
    mutation_rows = run_payloads(mutation_payloads, args.workers)

    result = {
        "schema_version": 1,
        "arithmetic": "exact Python integers",
        "candidate": "sum_u max(0,t_u-n_u) <= p",
        "source_manifest": {
            "bc108_core.py": sha256_file(Path(__file__).with_name("bc108_core.py")),
            "search_bc108.py": sha256_file(Path(__file__).with_name("search_bc108.py")),
            "search_archives_mutations.py": sha256_file(Path(__file__)),
            "archives": archive_manifest,
        },
        "archive_domain": {
            "distinct_oriented_bases": len(archive_payloads),
            "transform": "all positive-defect endpoint translations, b=1,2, plus positive q=2 parity lifts",
            "result": compact_aggregate(archive_rows),
        },
        "mutation_domain": {
            **mutation_domain,
            "transform": "all positive-defect endpoint translations, b=1,2, plus positive q=2 parity lifts",
            "result": compact_aggregate(mutation_rows),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({
        "archive_bases": len(archive_payloads),
        "archive_totals": {
            k: v for k, v in result["archive_domain"]["result"].items()
            if isinstance(v, int)
        },
        "archive_failure": result["archive_domain"]["result"]["failure"],
        "mutation_domain": mutation_domain,
        "mutation_totals": {
            k: v for k, v in result["mutation_domain"]["result"].items()
            if isinstance(v, int)
        },
        "mutation_failure": result["mutation_domain"]["result"]["failure"],
    }, indent=2))


if __name__ == "__main__":
    main()
