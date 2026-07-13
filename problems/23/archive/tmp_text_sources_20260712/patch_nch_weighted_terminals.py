from pathlib import Path
p = Path('problems/23/writeup/_codex_nch_weighted_blowup_hunt.py')
s = p.read_text(encoding='utf-8')
insert = r'''

def terminal_values(cyc, n: int, weights: tuple[int, ...], terminals: list[int] | None) -> list[tuple[int, Fraction]]:
    if terminals is None:
        return list(enumerate(terminal_contribs(cyc, n, weights)))
    wanted = set(terminals)
    values = {t: Fraction(0) for t in wanted}
    for edge, rows in cyc.items():
        a, b = edge
        prods = [path_product(tuple(path), weights) for path in rows]
        denom = sum(prods)
        if denom <= 0:
            raise ArithmeticError(f"zero denominator for edge {edge}")
        edge_factor = weights[a] * weights[b]
        if a in wanted:
            values[a] += weights[b]
        if b in wanted:
            values[b] += weights[a]
        interior_hits = wanted - {a, b}
        if not interior_hits:
            continue
        for path, prod in zip(rows, prods):
            pset = set(path[1:-1])
            for t in interior_hits & pset:
                values[t] += Fraction(edge_factor * (prod // weights[t]), denom)
    return [(t, values[t]) for t in sorted(values)]
'''
anchor = '\n\ndef scan_cut('
if 'def terminal_values(' not in s:
    s = s.replace(anchor, insert + anchor)
s = s.replace('    term_filter = set(terminals) if terminals is not None else None\n', '')
s = s.replace('        contrib = terminal_contribs(cyc, n, weights)\n        for t, value in enumerate(contrib):\n            if term_filter is not None and t not in term_filter:\n                continue\n', '        for t, value in terminal_values(cyc, n, weights, terminals):\n')
p.write_text(s, encoding='utf-8')
