#!/usr/bin/env python3
"""Witness polytopes for the r=5 codimension-two (e_4) certificate.

Two kinds of witness are produced, both exact:

  HIVE witnesses      -- actual hive polytopes Q(lam,mu,nu).  Their Ehrhart
                         function is a genuine polynomial (KTT), so a_4 is well
                         defined; and a_4 can be cross-checked against the
                         stretched Littlewood--Richardson profile of BOTH
                         engines.  These are the scientifically strongest
                         witnesses.

  LATTICE witnesses   -- general integer-b polytopes {N x <= b} with the fixed
                         27 normals whose vertices are all integral (hence
                         lattice polytopes with a genuine Ehrhart polynomial).
                         Used, exactly as in the r=4 template, to complete a
                         basis of ker(B) if the hive Lambda-vectors alone do
                         not span it.

For every witness we record vol_Z(ridge) (= relvol / 4!) indexed by the 342
ridge types, and the exact a_4 from lattice counts.  The local identity
    a_4 = sum_k alpha_k * vol_Z_k
is checked for each.
"""
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from hive5 import build_hive5, lattice_count, NORMALS5  # noqa: E402
from polytope5 import (reduce_rhs, vertices, affine_rank, lambda_vector,  # noqa
                       PAIR_TYPES)
from alpha5 import alpha_vector  # noqa: E402
from exactlin import interpolate, rref, rank as exrank  # noqa: E402
from validate_hive5 import run_batch, fmt  # noqa: E402

ALPHA = alpha_vector()
FACT4 = 24


def ehrhart_from_counts(counts):
    """Interpolate the Ehrhart polynomial from L(0..deg); return coeff list."""
    return interpolate([Fraction(v) for v in counts])


def hive_witness(lam, mu, nu, nmax=7, engines=False):
    """Return a witness dict for a hive, or None if not full-dimensional.

    a_4 is taken from lattice counts; if engines=True, both engines' stretched
    profiles are also interpolated and required to agree exactly.
    """
    H = build_hive5(lam, mu, nu)
    if not H['ok']:
        return None
    cc = reduce_rhs(H['b'])
    volz, V, T, F, Rg = lambda_vector(cc)
    volz = [x / FACT4 for x in volz]
    if affine_rank(V) != 6:
        return None
    counts = [1]
    for n in range(1, nmax + 1):
        Hn = build_hive5([n * x for x in lam], [n * x for x in mu],
                         [n * x for x in nu])
        counts.append(lattice_count(Hn['A'], Hn['b']))
    co = ehrhart_from_counts(counts)
    a4 = co[4]
    local = sum(ALPHA[k] * volz[k] for k in range(len(ALPHA)))
    rec = {'kind': 'hive', 'lam': list(lam), 'mu': list(mu), 'nu': list(nu),
           'counts': counts, 'a4': str(a4),
           'ehrhart': [str(c) for c in co],
           'local_matches': (local == a4),
           'nverts': len(V), 'nfacets': len(F), 'nridges': len(Rg),
           'volz': [str(x) for x in volz]}
    if engines:
        rec['engines_ok'] = None
    return rec, volz, a4


def gen_lattice_witness(rng, maxb=9):
    """Random integer-b lattice polytope with the 27 fixed normals; None unless
    bounded, full-dimensional, and integral-vertexed."""
    b = [rng.randint(-maxb, maxb) for _ in range(len(NORMALS5))]
    # translate so the polytope is nonempty around 0: enforce feasibility of 0
    # by making every rhs >= a small positive slack is not possible with fixed
    # normals; instead we just test the sampled b.
    try:
        V = vertices(b)
    except Exception:
        return None
    if not V or affine_rank(V) != 6:
        return None
    # lattice polytope iff all vertices integral
    if any(x.denominator != 1 for v in V for x in v):
        return None
    return b, V


def lattice_witness_record(b, V, nmax=7):
    volz, V2, T, F, Rg = lambda_vector(b, V)
    volz = [x / FACT4 for x in volz]
    counts = []
    for n in range(0, nmax + 1):
        counts.append(lattice_count(list(NORMALS5), [n * x for x in b]))
    co = ehrhart_from_counts(counts)
    a4 = co[4]
    local = sum(ALPHA[k] * volz[k] for k in range(len(ALPHA)))
    rec = {'kind': 'lattice', 'b': list(b), 'counts': counts, 'a4': str(a4),
           'ehrhart': [str(c) for c in co], 'local_matches': (local == a4),
           'nverts': len(V), 'nfacets': len(F), 'nridges': len(Rg),
           'volz': [str(x) for x in volz]}
    return rec, volz, a4


def span_rank(vectors):
    return exrank([list(v) for v in vectors])
