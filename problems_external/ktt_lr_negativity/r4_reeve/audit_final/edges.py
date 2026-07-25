"""Independent edge extractor -> 99-dim Lambda vector over the fixed r=4 normals.
Validated by reproducing the 72 recorded certificate edge_length vectors."""
import json
from fractions import Fraction as F
from math import gcd
from itertools import combinations

CERT="E:/Projects/ErdosProblems/problems_external/ktt_lr_negativity/r4_reeve/q2_basis_witness_certificate.json"
_c=json.load(open(CERT))
NORMALS=[tuple(n) for n in _c['normals']]
IDXPAIRS=[tuple(p) for p in _c['nonparallel_pairs']]
PAIRIDX={}
for k,(i,j) in enumerate(IDXPAIRS):
    PAIRIDX[frozenset((i,j))]=k

def solve3(A,bb):
    # exact 3x3 solve; return None if singular
    M=[[F(A[r][c]) for c in range(3)]+[F(bb[r])] for r in range(3)]
    for c in range(3):
        piv=None
        for r in range(c,3):
            if M[r][c]!=0: piv=r;break
        if piv is None: return None
        M[c],M[piv]=M[piv],M[c]
        pv=M[c][c]; M[c]=[x/pv for x in M[c]]
        for r in range(3):
            if r!=c and M[r][c]!=0:
                f=M[r][c]; M[r]=[a-f*b for a,b in zip(M[r],M[c])]
    return (M[0][3],M[1][3],M[2][3])

def vertices(normals,b):
    n=len(normals); verts=set()
    for tri in combinations(range(n),3):
        A=[normals[t] for t in tri]; bb=[b[t] for t in tri]
        x=solve3(A,bb)
        if x is None: continue
        ok=True
        for k in range(n):
            s=normals[k][0]*x[0]+normals[k][1]*x[1]+normals[k][2]*x[2]
            if s> F(b[k]): ok=False;break
        if ok: verts.add(x)
    return [tuple(v) for v in verts]

def _rank_rows(rows):
    rows=[list(r) for r in rows]; pr=0
    for c in range(3):
        piv=None
        for i in range(pr,len(rows)):
            if rows[i][c]!=0: piv=i;break
        if piv is None: continue
        rows[pr],rows[piv]=rows[piv],rows[pr]
        pv=rows[pr][c]; rows[pr]=[F(x)/pv for x in rows[pr]]
        for i in range(len(rows)):
            if i!=pr and rows[i][c]!=0:
                f=rows[i][c]; rows[i]=[a-f*b for a,b in zip(rows[i],rows[pr])]
        pr+=1
    return pr

def facet_rows(normals,b,verts):
    """indices of rows whose tight-vertex set is affinely 2-dim -> facets."""
    fac=[]
    for k in range(len(normals)):
        tv=[v for v in verts if normals[k][0]*v[0]+normals[k][1]*v[1]+normals[k][2]*v[2]==F(b[k])]
        if len(tv)>=3:
            base=tv[0]
            dirs=[[v[t]-base[t] for t in range(3)] for v in tv[1:]]
            if _rank_rows(dirs)>=2: fac.append(k)
    return fac

def lattice_len(v,w):
    d=[w[t]-v[t] for t in range(3)]
    # require integer edge
    di=[]
    for x in d:
        assert x.denominator==1, ("non-integer edge",v,w)
        di.append(abs(int(x)))
    g=0
    for x in di: g=gcd(g,x)
    return g

def lambda_vec(normals,b):
    verts=vertices(normals,b)
    fac=set(facet_rows(normals,b,verts))
    Lam=[0]*len(IDXPAIRS)
    for v,w in combinations(verts,2):
        tight=[k for k in range(len(normals))
               if normals[k][0]*v[0]+normals[k][1]*v[1]+normals[k][2]*v[2]==F(b[k])
               and normals[k][0]*w[0]+normals[k][1]*w[1]+normals[k][2]*w[2]==F(b[k])]
        if not tight: continue
        # rank of tight normals must be 2 (edge)
        if _rank_rows([list(normals[k]) for k in tight])!=2: continue
        # facet normals among tight (facet-defining rows)
        facn=[k for k in tight if k in fac]
        # distinct primitive normals
        nn=sorted(set(k for k in facn))
        if len(nn)<2:
            # fall back: use two extreme tight normals spanning rank2
            nn=sorted(set(tight))
        # choose the two normals whose pair is a known nonparallel pair
        assigned=False
        for a,bb in combinations(nn,2):
            key=frozenset((a,bb))
            if key in PAIRIDX:
                Lam[PAIRIDX[key]]+=lattice_len(v,w); assigned=True; break
        if not assigned:
            raise RuntimeError(("edge with no valid normal pair",v,w,tight,facn))
    return Lam, verts

if __name__=="__main__":
    # validate against all 72 recorded witnesses
    c=_c; bad=0
    for wi,w in enumerate(c['witnesses']):
        Lam,verts=lambda_vec(NORMALS,w['b'])
        if Lam!=w['edge_lengths']:
            bad+=1
            if bad<=3:
                print("MISMATCH witness",wi)
                print(" mine:",Lam)
                print(" recd:",w['edge_lengths'])
    print(f"witness_edge_reproduction: {72-bad}/72 exact, mismatches={bad}")
