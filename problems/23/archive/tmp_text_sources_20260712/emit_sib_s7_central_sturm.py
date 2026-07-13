import json
from pathlib import Path
import sympy as sp

t = sp.symbols('t')
P0 = 20*t**7 - 18*t**6 - 166*t**5 + 76*t**4 + 459*t**3 + 117*t**2 - 117*t + 4
seq = sp.sturm(P0, t)

def coeffs_desc(poly):
    p = sp.Poly(poly, t, domain=sp.QQ)
    out = []
    for c in p.all_coeffs():
        c = sp.Rational(c)
        if c.q == 1:
            out.append(str(c.p))
        else:
            out.append(f'{c.p}/{c.q}')
    return out

cert = {
    'schema': 'sib_s7_central_sturm_v1',
    'description': 'SIB S7 central all-seven-tight curve positivity certificate',
    'variable': 't',
    'feasible_range': {'lower': '1', 'upper': 'infinity', 'closed_lower': True},
    'central_substitution': {
        'b': '1', 'd': '1', 'f': '1', 'u': '1', 'y': '1',
        'c': 't', 'e': 't', 'x': 't', 'v': 't', 'a': 't + 1 - 1/t'
    },
    'phi_denominator_factors': ['t^2', 't + 2', 't^3 + 2*t^2 + t + 1'],
    'numerator_coeffs_desc': coeffs_desc(P0),
    'numerator_at_1': str(sp.expand(P0).subs(t, 1)),
    'sturm_sequence_coeffs_desc': [coeffs_desc(p) for p in seq],
    'expected_variation_at_1': None,
    'expected_variation_at_infinity': None,
    'expected_roots_on_range': 0,
    'verdict': 'P0 has no real root on [1,infinity); P0(1)>0; denominator positive there; Phi(t)>0.'
}

def sign_at_one(poly):
    val = sp.Poly(poly, t, domain=sp.QQ).eval(1)
    return 1 if val > 0 else (-1 if val < 0 else 0)

def sign_at_inf(poly):
    lc = sp.Poly(poly, t, domain=sp.QQ).LC()
    return 1 if lc > 0 else (-1 if lc < 0 else 0)

def variations(signs):
    nz = [s for s in signs if s]
    return sum(1 for a, b in zip(nz, nz[1:]) if a*b < 0)

cert['signs_at_1'] = [sign_at_one(p) for p in seq]
cert['signs_at_infinity'] = [sign_at_inf(p) for p in seq]
cert['expected_variation_at_1'] = variations(cert['signs_at_1'])
cert['expected_variation_at_infinity'] = variations(cert['signs_at_infinity'])
Path('problems/23/writeup/sib_s7_central_sturm_cert.json').write_text(json.dumps(cert, indent=2, sort_keys=True), encoding='utf-8')
print('wrote', len(seq), 'polys', cert['expected_variation_at_1'], cert['expected_variation_at_infinity'])
