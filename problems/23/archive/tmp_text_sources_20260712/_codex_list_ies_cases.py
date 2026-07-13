from concurrent.futures import ProcessPoolExecutor

from _codex_singleton_vertexslack_gate import (
    analyze_graph,
    census_records,
    structured_records,
)


def main() -> None:
    records = census_records(11) + structured_records()
    with ProcessPoolExecutor(max_workers=32) as pool:
        for result in pool.map(analyze_graph, records, chunksize=16):
            if result and result["deficient"]:
                print(result["name"], result["n"], result["deficient"])


if __name__ == "__main__":
    main()
