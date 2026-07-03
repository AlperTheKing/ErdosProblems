from __future__ import annotations
import argparse
import json
import subprocess
import sys
from pathlib import Path
sys.path.insert(0, 'problems/23/writeup')
from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string


def dump_rows(path: Path, name: str, n: int, side_int: int, st, gamma: int):
    M, ell, _T, _mu, cyc = st
    rows = []
    for rs in cyc.values():
        denom = len(rs)
        for P in rs:
            mask = 0
            for v in P:
                mask |= 1 << v
            rows.append((mask, denom))
    with path.open('w', encoding='utf-8') as f:
        f.write(f'{name} {n} {side_string(n, side_int)} {gamma} {len(M)} {len(rows)}\n')
        for mask, den in rows:
            f.write(f'{mask} {den}\n')
    return len(M), len(rows), sorted(set(ell.values()))


def run(args):
    exe = Path(args.exe)
    out = {'verdict': 'PASS', 'runs': []}
    tmpdir = Path(args.tmpdir)
    tmpdir.mkdir(parents=True, exist_ok=True)
    wanted = set(args.only.split(',')) if args.only else None
    for name, n, edges in named_graphs(args.max_myc_cycle):
        if wanted and name not in wanted:
            continue
        if n - 2 <= args.skip_free_le:
            continue
        _best, structs = gamma_min_structs(name, n, edges)
        for idx, (side_int, _side, st, gamma) in enumerate(structs):
            dump = tmpdir / f'nch_rows_{name}_cut{idx}.txt'
            bad, rows, ell_values = dump_rows(dump, name, n, side_int, st, gamma)
            cp = subprocess.run([str(exe), str(dump)], text=True, capture_output=True, check=False)
            rec = {
                'name': name,
                'n': n,
                'cut_index': idx,
                'side': side_string(n, side_int),
                'gamma': gamma,
                'bad_edges': bad,
                'rows': rows,
                'ell_values': ell_values,
                'returncode': cp.returncode,
                'stdout': cp.stdout.strip(),
                'stderr': cp.stderr.strip(),
            }
            print(name, 'cut', idx, 'rc', cp.returncode, cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else cp.stderr.strip(), flush=True)
            if cp.returncode != 0 or 'VERDICT PASS' not in cp.stdout:
                out['verdict'] = 'FAIL'
            out['runs'].append(rec)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--exe', default='tmp/nch_t2_hall_checker.exe')
    ap.add_argument('--tmpdir', default='tmp/nch_t2_rows')
    ap.add_argument('--max-myc-cycle', type=int, default=11)
    ap.add_argument('--skip-free-le', type=int, default=14)
    ap.add_argument('--only', default='')
    ap.add_argument('--summary', default='')
    args = ap.parse_args()
    out = run(args)
    print('VERDICT', out['verdict'], 'runs', len(out['runs']))
    if args.summary:
        Path(args.summary).write_text(json.dumps(out, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
