from __future__ import annotations

from itertools import product
import numpy as np
import sympy as sp
from scipy.optimize import linprog
from scipy.sparse import coo_matrix


def poly_dict(expr, vars_):
    P = sp.Poly(sp.expand(expr), *vars_)
    return {tuple(m): float(c) for m, c in P.terms()}


def add(a, b):
    return tuple(x+y for x,y in zip(a,b))


def monoms(n, deg):
    def rec(i, left, cur):
        if i == n:
            yield tuple(cur); return
        for k in range(left+1):
            cur.append(k)
            yield from rec(i+1, left-k, cur)
            cur.pop()
    yield from rec(0, deg, [])


def total(m):
    return sum(m)


def cone_probe(branch: str, cap_name: str, max_deg: int):
    a,b,c,d,e,f = sp.symbols('a b c d e f', positive=True)
    vars_ = (a,b,c,d,e,f)
    x = sp.Integer(1); y = sp.Integer(1)
    S = a+b+c+d+e+f
    Y = a*c+b*f+c*f
    Z = e*Y + d*f*(b+c)
    A = b*d+c*d+d*f+a*c+a*e+b*f+b*e+c*f+c*e+e*f
    B = a*c+a*e+b*f+b*e+c*f+c*e+e*f
    caps = {
        's4': Y,
        's5': a*e+b*f+c*f,
        's6': a*c+d*f+e*f,
        's7': a*e+d*f+e*f,
    }
    Mj = caps[cap_name]
    if branch == 'u1':
        u = sp.Integer(1)
        v = sp.Rational(1,2)*(Mj - 1)
    elif branch == 's2':
        v = d + e - Mj
        u = 2*Mj - d - e
    else:
        raise ValueError(branch)
    m = x*u + x*v + y*v
    N = S + x+y+u+v
    Phi = 2*(N*N - 25*m) - 75*(x*(u+v)*A/Z + y*v*B/(e*Y) - S)
    num = sp.together(Phi).as_numer_denom()[0]
    shift = {var: var+1 for var in vars_}
    target = poly_dict(num.subs(shift), vars_)
    slacks = {
        'u': u-1,
        'v': v-1,
        's1': e-v,
        's2': d+e-(u+v),
        's3': b+c-2,
    }
    for oname, om in caps.items():
        if oname != cap_name:
            slacks[oname] = om - Mj
    if branch == 'u1':
        slacks.pop('u', None)
    if branch == 's2':
        slacks.pop('s2', None)
    slack_polys = []
    for name, expr in slacks.items():
        pd = poly_dict(sp.expand(expr.subs(shift)), vars_)
        if all(abs(v) < 1e-12 for v in pd.values()):
            continue
        slack_polys.append((name, pd))
    candidates = [(i, mono) for i in range(len(slack_polys)) for mono in monoms(6, max_deg)]
    touched = set(target)
    for i, mono in candidates:
        for sm in slack_polys[i][1]:
            touched.add(add(mono, sm))
    touched = sorted(touched, key=lambda m:(total(m),m))
    rid = {m:i for i,m in enumerate(touched)}
    rows=[]; cols=[]; vals=[]
    for j,(si,mono) in enumerate(candidates):
        for sm, coeff in slack_polys[si][1].items():
            rows.append(rid[add(mono,sm)]); cols.append(j); vals.append(coeff)
    A_mat = coo_matrix((vals,(rows,cols)), shape=(len(touched), len(candidates))).tocsr()
    rhs = np.array([target.get(m,0.0) for m in touched], dtype=float)
    res = linprog(np.zeros(len(candidates)), A_ub=A_mat, b_ub=rhs, bounds=(0,None), method='highs')
    print(branch, cap_name, 'deg', max_deg, 'slacks', [n for n,_ in slack_polys], 'rows', len(touched), 'cand', len(candidates), 'minrhs', rhs.min(), 'success', res.success, 'status', res.status)
    if res.success:
        nz = [(slack_polys[si][0], mono, res.x[j]) for j,(si,mono) in enumerate(candidates) if res.x[j] > 1e-8]
        print(' nz', len(nz), 'first', nz[:30])


def main():
    for branch in ['u1','s2']:
        for deg in [3,4,5]:
            for cap in ['s4','s5','s6','s7']:
                cone_probe(branch, cap, deg)

if __name__ == '__main__':
    main()
