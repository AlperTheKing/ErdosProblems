"""R20 staged transfer-matching gate (L1), fixtures 167 and 311. Exact fractions only.

Stages (R20a section 6): 1 = sameFirst cancellation (collision obligations vs own-first-coordinate
Free half-slots; per-vertex, sources disjoint across owners); 2 = + commonBad pair terminals;
3 = + rowCompanion pair terminals (DETERMINISTIC companions only -- conservative undercount);
4 = prune (not implemented; only reached if stage 3 leaves a deficit).

Masses are totals over Omega in units of K = |Omega| (exact expectations):
  cell (v,z): n(v,z) = det(v,z) + Binom(m,p) with NO mixed det+random cells (asserted);
  E[(n-1)_+] = d-1+mp if d>=1 else mp-(1-q^m);  P[n=0] = 0 if d>=1 else q^m;  E[n] = d+mp.
Per vertex: T(v) = sum_z E[n(v,z)] (= 5 E[#rows through v], asserted);
  F(v) = sum_z P[n=0]; C(v) = sum_z E[(n-1)_+]; identity F-C = N-T asserted for ALL v.
Obligations at v: collision halves 2C(v); HitNeed D_v = max(0, deg_I(v) - max(0, N - T(v))).
Stage-1 residual at v: max(0, 2C-2F) + D_v.
Stage-2 supply at v: sum over ordered pairs (x,z), x!=z, vx,vz bad: 2 P[n(x,z)=0].
Stage-3 supply at v: sum over ordered pairs (x,z), x!=z, both DETERMINISTIC row-companions of v
  (x on a det row through v, or on an attachment fixed slot of a row through v): 2 P[n(x,z)=0].
Contention: with the deficit locus computed first, source sharing is checked (a pair is counted
only once; here deficit locus is a single vertex so the trivial flow is exact).
Expected: 167 stage-1 PASS everywhere; 311 stage-1 FAIL only at v=9 (residual 70 = 68+2),
stage-2 residual 66, stage-3 PASS (P0-pair supply alone 112 > 66).
"""
from fractions import Fraction as F
import hashlib, sys

ok = True
def chk(name, cond):
    global ok
    print(("PASS " if cond else "FAIL ") + name)
    if not cond: ok = False

def build(fixture):
    """returns N, blue set, bad list, det_rows (list of 5-vertex tuples),
    att = None or dict(P0,P1,P3,P4, atoms=[(p4,p0)...], v=9)"""
    blue = set(); bad = []
    def be(a,b): blue.add((min(a,b),max(a,b)))
    for i in range(26): be(i,(i+1)%26)
    be(26,0)
    for i in range(26): bad.append((i,(i+4)%26))
    bad.append((26,3)); bad.append((26,23))
    ip = [0]
    for _ in range(12): ip.append((ip[-1]+9)%26)
    for a,b in zip(ip,ip[1:]): be(a,b)
    nxt = 27
    for (x,y) in bad[:28]:
        ls = list(range(nxt,nxt+5)); nxt += 5
        ch = [x]+ls+[y]
        for a,b in zip(ch,ch[1:]): be(a,b)
    det_rows = []
    for i in range(26): det_rows.append(tuple((i+t)%26 for t in range(5)))
    det_rows.append((26,0,1,2,3))       # w-atom (26,3): unique row w-0-1-2-3
    det_rows.append((26,0,25,24,23))    # w-atom (26,23): unique row w-0-25-24-23
    att = None
    if fixture == 311:
        v = 9
        P0 = list(range(nxt,nxt+8));  nxt += 8
        P1 = list(range(nxt,nxt+64)); nxt += 64
        P3 = list(range(nxt,nxt+64)); nxt += 64
        P4 = list(range(nxt,nxt+8));  nxt += 8
        for a in P0:
            for b in P1: be(a,b)
        for b in P1: be(b,v)
        for c in P3: be(v,c)
        for c in P3:
            for d in P4: be(c,d)
        atoms = [(d,a) for d in P4 for a in P0]
        bad += atoms
        att = dict(P0=set(P0),P1=set(P1),P3=set(P3),P4=set(P4),atoms=atoms,v=v)
    return nxt, blue, bad, det_rows, ip, att

def run(fixture):
    print("="*20 + " FIXTURE %d " % fixture + "="*20)
    N, blue, bad, det_rows, ip, att = build(fixture)
    chk("N = %d" % fixture, N == fixture)
    # det co-occurrence matrix from det rows + attachment fixed slots
    det = {}
    def bump(a,b):
        det[(a,b)] = det.get((a,b),0)+1
    for row in det_rows:
        for a in row:
            for b in row: bump(a,b)
    fixcnt = {}   # v -> number of attachment rows in which v is a FIXED member
    P1s = P3s = set()
    if att:
        P1s, P3s = att['P1'], att['P3']
        for (d,a) in att['atoms']:
            for u in (d, att['v'], a):
                fixcnt[u] = fixcnt.get(u,0)+1
            for x in (d, att['v'], a):
                for y in (d, att['v'], a): bump(x,y)
    q64 = F(63,64); p64 = F(1,64); p4096 = F(1,4096); q4096 = F(4095,4096)
    def cell(vv, zz):
        """(d, m, p): n(v,z) = d + Binom(m,p)"""
        d = det.get((vv,zz),0)
        m, p = 0, F(0)
        if att:
            vfix, zfix = fixcnt.get(vv,0), fixcnt.get(zz,0)
            vP1, vP3 = vv in P1s, vv in P3s
            zP1, zP3 = zz in P1s, zz in P3s
            if vv == zz:
                if vP1 or vP3: m,p = 64, p64
            elif vfix and (zP1 or zP3): m,p = vfix, p64
            elif zfix and (vP1 or vP3): m,p = zfix, p64
            elif (vP1 and zP3) or (vP3 and zP1): m,p = 64, p4096
            # P1-P1', P3-P3' distinct: 0 (one slot per row)
            if d and m: raise AssertionError("mixed det+random cell %r %r" % (vv,zz))
        return d, m, p
    # per-vertex aggregates
    from collections import defaultdict
    Tb = [F(0)]*N; Fb = [F(0)]*N; Cb = [F(0)]*N
    powq = {}
    def q_m(m,p):
        if (m,p) not in powq: powq[(m,p)] = (1-p)**m
        return powq[(m,p)]
    for vv in range(N):
        t = F(0); f = F(0); c = F(0)
        for zz in range(N):
            d,m,p = cell(vv,zz)
            En = d + m*p
            t += En
            if d >= 1:
                c += d-1+m*p
            else:
                qm = q_m(m,p) if m else F(1)
                f += qm
                c += m*p - (1-qm)
        Tb[vv], Fb[vv], Cb[vv] = t, f, c
    # cross-checks
    rows_thru = [0]*N
    for row in det_rows:
        for u in row: rows_thru[u] += 1
    id_ok = True; t_ok = True
    for vv in range(N):
        if Fb[vv]-Cb[vv] != N-Tb[vv]: id_ok = False
        er = F(rows_thru[vv])
        if att:
            if vv == att['v'] or fixcnt.get(vv,0):
                er += fixcnt.get(vv,0) if vv != att['v'] else 64
            elif vv in P1s or vv in P3s:
                er += F(1)   # 64 * 1/64
        if Tb[vv] != 5*er: t_ok = False
    chk("identity F(v)-C(v) = N-T(v) for ALL %d vertices (exact)" % N, id_ok)
    chk("T(v) = 5*E[#rows through v] for ALL v (exact)", t_ok)
    # HitNeed
    degI = defaultdict(int)
    for a,b in zip(ip,ip[1:]):
        degI[a] += 1; degI[b] += 1
    def hitneed(vv):
        slack = max(F(0), F(N)-Tb[vv])
        return max(F(0), F(degI.get(vv,0)) - slack)
    # ---- stage 1 ----
    resid = {}
    for vv in range(N):
        r = max(F(0), 2*Cb[vv]-2*Fb[vv]) + hitneed(vv)
        if r > 0: resid[vv] = r
    chk("stage-1 deficit locus = %s" % ("{} (PASS)" if not resid else str(sorted(resid))),
        (fixture == 167 and not resid) or (fixture == 311 and sorted(resid) == [9]))
    if not resid:
        print("VERDICT %d: STAGE-1 PASS (sameFirst suffices; no HitNeed)" % fixture)
        return
    if fixture == 311:
        chk("stage-1 residual at 9 = 70 (= 2(T-N) + deg_I = 68+2)", resid.get(9) == 70)
    badnb = defaultdict(set)
    for (a,b) in bad:
        badnb[a].add(b); badnb[b].add(a)
    def free_mass(x,z):
        d,m,p = cell(x,z)
        return F(0) if d >= 1 else (q_m(m,p) if m else F(1))
    # ---- stage 2 ----
    used = set()
    resid2 = {}
    for vv, r in resid.items():
        supply = F(0)
        for x in badnb[vv]:
            for z in badnb[vv]:
                if x != z and (x,z) not in used:
                    fm = free_mass(x,z)
                    if fm > 0:
                        supply += 2*fm; used.add((x,z))
        r2 = max(F(0), r - supply)
        if r2 > 0: resid2[vv] = r2
        print("  stage-2 v=%d: commonBad supply %s, residual %s" % (vv, supply, r2))
    chk("stage-2 residual = {9: 66}" if fixture == 311 else "stage-2", resid2 == {9: F(66)})
    # ---- stage 3 ----
    comp = defaultdict(set)   # deterministic companions
    for row in det_rows:
        for u in row:
            for w in row:
                if w != u: comp[u].add(w)
    if att:
        for (d,a) in att['atoms']:
            for u in (d,a): comp[att['v']].add(u)
            comp[d].add(att['v']); comp[a].add(att['v'])
            comp[d].add(a); comp[a].add(d)
    resid3 = {}
    for vv, r in resid2.items():
        cands = sorted(comp[vv])
        supply = F(0); pair_ct = 0
        for x in cands:
            for z in cands:
                if x != z and (x,z) not in used:
                    fm = free_mass(x,z)
                    if fm > 0:
                        supply += 2*fm; pair_ct += 1; used.add((x,z))
        r3 = max(F(0), r - supply)
        if r3 > 0: resid3[vv] = r3
        print("  stage-3 v=%d: %d det-companion Free ordered pairs, supply %s, residual %s"
              % (vv, pair_ct, supply, r3))
    chk("stage-3 residual EMPTY (rowCompanion completes; ZERO prune)", not resid3)
    # sanity vs prior analytic gate
    if fixture == 311:
        p0 = sorted(att['P0'])
        p0supply = sum(2*free_mass(x,z) for x in p0 for z in p0 if x != z)
        chk("P0-pair supply alone = 112 >= 66 (matches R20a)", p0supply == 112)
    print("VERDICT %d: STAGE-3 PASS" % fixture)

run(167)
print()
run(311)
print()
print("OVERALL:", "ALL CHECKS PASS" if ok else "SOME CHECKS FAILED")
h = hashlib.sha256(open(__file__,'rb').read()).hexdigest()
print("gate script SHA-256:", h)
sys.exit(0 if ok else 1)
