from pathlib import Path
p=Path('problems/23/writeup/_codex_eq_cert2_chart_sos_2x2.py')
s=p.read_text(encoding='utf-8')
start=s.index('def selected_atoms(')
end=s.index('\n\ndef main()', start)
new_func=r'''def selected_atoms(target12, max_atoms: int, mode: str):
    all_deg6 = list(sos.weak_compositions(6, lp.SX_DIM))
    seed = (6,) + (0,) * (lp.SX_DIM - 1)
    atoms = []
    neg_rows = sorted((exp, coeff) for exp, coeff in target12.items() if coeff < 0)
    for row, coeff in neg_rows:
        best = None
        all_for_row = []
        for a in all_deg6:
            b = sos.sub_exp(row, a)
            if b is None or sum(b) != 6 or a > b or a == seed or b == seed:
                continue
            da = tuple(2 * x for x in a)
            db = tuple(2 * x for x in b)
            ca = target12.get(da, Fraction(0))
            cb = target12.get(db, Fraction(0))
            if ca > 0 and cb > 0:
                score = min(ca, cb)
                cand = (score, a, b, row)
                all_for_row.append((a, b, row))
                if best is None or cand > best:
                    best = cand
        if mode == "best":
            if best is not None:
                _score, a, b, row = best
                atoms.append((a, b, row))
        elif mode == "all":
            atoms.extend(all_for_row)
        else:
            raise ValueError(f"unknown atom mode {mode!r}")
        if max_atoms and len(atoms) >= max_atoms:
            return atoms[:max_atoms]
    return atoms
'''
s=s[:start]+new_func+s[end:]
s=s.replace('    ap.add_argument("--max-atoms", type=int, default=500)\\n    ap.add_argument("--atom-mode", choices=["best", "all"], default="best")','    ap.add_argument("--max-atoms", type=int, default=500)\n    ap.add_argument("--atom-mode", choices=["best", "all"], default="best")')
p.write_text(s, encoding='utf-8')
