from __future__ import annotations
import argparse
import sys
from pathlib import Path
sys.path.insert(0, 'problems/23/writeup')
from _codex_nch_sanity_gate import named_graphs, gamma_min_structs, side_string


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', required=True)
    ap.add_argument('--cut-index', type=int, default=0)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    for name,n,edges in named_graphs(11):
        if name != args.only:
            continue
        _best, structs = gamma_min_structs(name,n,edges)
        side_int, _side, st, gamma = structs[args.cut_index]
        M, ell, _T, _mu, cyc = st
        rows=[]
        for rs in cyc.values():
            denom=len(rs)
            for P in rs:
                mask=0
                for v in P:
                    mask |= 1 << v
                rows.append((mask, denom))
        with open(args.out,'w',encoding='utf-8') as f:
            f.write(f'{name} {n} {side_string(n,side_int)} {gamma} {len(M)} {len(rows)}\n')
            for mask,den in rows:
                f.write(f'{mask} {den}\n')
        print(args.out, 'rows', len(rows), 'n', n, 'side', side_string(n,side_int), 'gamma', gamma)
        return
    raise SystemExit('graph not found')

if __name__ == '__main__':
    main()
