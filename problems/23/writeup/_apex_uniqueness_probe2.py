"""DEEPER probe of apex uniqueness |R|<=1, after _apex_uniqueness_gate found:
  - |R|<=1 on 586 cuts (only N=23 Myc-Grotzsch apex has a negative Schur row sum, R=[22]),
  - the 'negdiag' structural guess is FALSE (at N=23 the raw diagonal H[22][22]>=0; negativity is off-diagonal).

Here we (A) dissect the N=23 apex: print O, supply a_o=T_o-N, full S, rowsums, diag(S), diag(H_OO),
to see WHY exactly one row sum is negative and find the true structural signature.
(B) Build genuinely SYMMETRIC two-apex graphs and enumerate ALL gamma-min cuts to try to force |R|=2:
    - C5 blowup with TWO equal heavy classes in symmetric positions ([t,1,t,1,1]) -- two would-be apexes by symmetry.
    - disjoint-union of two identical odd cores sharing the SAME cut (so two equal max-load vertices) joined minimally.
    - Petersen graph (triangle-free, vertex-transitive, N=10) -- many tied loads.
    - C5-blowup [t,t,t,t,t] uniform (all 5 classes equal) at t=3,4 -- 5-fold symmetric loads.
(C) The cleanest correct structural statement candidate:
    r_o = rowsum_o(S) = a_o - (effective conductance leaving o through S).  Test:
       r_o<0  <=>  a_o = T_o-N  is the UNIQUE STRICT maximum of the *supply* over O,
       and moreover a_o > sum_{o'!=o in O} a_{o'} ??? (apex carries more than half the total O-overload).
    Record, for the apex o*: a_{o*} vs sum of other a, and a_{o*} vs max other a (strict gap).
EXACT Fraction. Run: python _apex_uniqueness_probe2.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, union_disjoint, is_triangle_free
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import schur_on_O


def full_record(name, n, adj, side):
    if not Bconn(n, adj, side):
        return None
    st = struct_for_side(n, adj, side)
    if st is None:
        return None
    M, ell, T, mu, cyc = st
    if not M:
        return None
    N = F(n)
    H = build_H(n, M, ell, T, cyc, BETA)
    r = schur_on_O(H, n, T, N)
    O = r['O']
    if not O:
        return None
    rec = dict(name=name, n=n, side=''.join(map(str, side)), O=O, T=T, H=H,
               S=r['S'], rowsum=r['rowsum'], supply=r['supply'], psdS=r['psdS'], UU_PD=r['UU_PD'])
    return rec


def Rset(rec):
    if rec is None or rec['rowsum'] is None:
        return []
    return [rec['O'][i] for i in range(len(rec['O'])) if rec['rowsum'][i] < 0]


def dissect(rec):
    O = rec['O']; S = rec['S']
    print("    name=%s N=%d side=%s" % (rec['name'], rec['n'], rec['side']))
    print("    O = %s" % O)
    print("    supply a_o=T_o-N : %s" % [str(x) for x in rec['supply']])
    print("    S rowsums        : %s" % [str(x) for x in rec['rowsum']])
    print("    diag(S)          : %s" % [str(S[i][i]) for i in range(len(O))])
    print("    diag(H_OO)       : %s" % [str(rec['H'][o][o]) for o in O])
    print("    R (rowsum<0)     : %s" % Rset(rec))
    print("    full S:")
    for i, o in enumerate(O):
        print("      o=%2d : %s" % (o, [str(x) for x in S[i]]))


def main():
    print("=" * 74)
    print("DEEPER apex-uniqueness probe")
    print("=" * 74)

    # ---- (A) dissect N=23 Myc-Grotzsch apex ----
    print("\n--- (A) N=23 Myc(Grotzsch) apex dissection ---", flush=True)
    grN, grE = mycielski(5, Cn(5))
    m2N, m2E = mycielski(grN, grE)
    adj23 = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj23[x].add(y); adj23[y].add(x)
    s23 = maxcut_ls(m2N, adj23)
    rec = full_record("MycGrotzsch_N23", m2N, adj23, s23)
    dissect(rec)
    # supply ranking
    O = rec['O']; T = rec['T']; N = rec['n']
    sup = sorted(((float(T[o] - N), o) for o in O), reverse=True)
    print("    sorted (a_o, o): %s" % [(round(a, 3), o) for a, o in sup])
    a_sorted = sorted((T[o] - N for o in O), reverse=True)
    print("    a_max=%s  sum(other a)=%s  a_max > sum_other? %s"
          % (str(a_sorted[0]), str(sum(a_sorted[1:])), a_sorted[0] > sum(a_sorted[1:])))

    # ---- (B) symmetric two-apex stress, full gamma-min enumeration ----
    print("\n--- (B) symmetric multi-apex stress (full gmins enumeration) ---", flush=True)
    acc = dict(n=0, R0=0, R1=0, Rge2=0, ex=None, apex_mismatch=0, apexex=None,
               half_fail=0, halfex=None)

    def scan_family(name, n, E):
        if not is_triangle_free(n, E):
            print("    %s NOT triangle-free, skip" % name, flush=True)
            return
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        try:
            _, cuts = gmins(n, E)
        except Exception as e:
            print("    %s gmins err %s" % (name, e), flush=True)
            return
        loc_R1 = 0; loc_Rge2 = 0
        for side in cuts:
            rec = full_record(name, n, adj, side)
            if rec is None:
                continue
            acc['n'] += 1
            R = Rset(rec)
            if len(R) == 0:
                acc['R0'] += 1
            elif len(R) == 1:
                acc['R1'] += 1; loc_R1 += 1
                o = R[0]; T = rec['T']; nn = rec['n']
                # apex = unique global argmax T?
                Tmax = max(T)
                if [v for v in range(nn) if T[v] == Tmax] != [o]:
                    acc['apex_mismatch'] += 1
                    if acc['apexex'] is None:
                        acc['apexex'] = (name, rec['side'], R, [v for v in range(nn) if T[v] == Tmax])
                # 'carries more than half' structural test among O
                a_o = T[o] - nn
                other = sum((T[o2] - nn) for o2 in rec['O'] if o2 != o)
                if not (a_o > other):
                    acc['half_fail'] += 1
                    if acc['halfex'] is None:
                        acc['halfex'] = (name, rec['side'], float(a_o), float(other))
            else:
                acc['Rge2'] += 1; loc_Rge2 += 1
                if acc['ex'] is None:
                    T = rec['T']; nn = rec['n']
                    acc['ex'] = (name, rec['side'], R, {o: float(T[o] - nn) for o in R},
                                 [float(x) for x in rec['rowsum']])
        print("    %-22s N=%2d cuts=%3d : R1=%d Rge2=%d" % (name, n, len(cuts), loc_R1, loc_Rge2), flush=True)

    # symmetric C5 blowups (two equal heavy classes in symmetric position 0 and 2)
    for t in (2, 3, 4):
        scan_family("C5sym[%d,1,%d,1,1]" % (t, t), *odd_blowup(5, [t, 1, t, 1, 1]))
    # uniform C5 blowups (5-fold symmetric loads)
    for t in (2, 3, 4):
        n, E = odd_blowup(5, [t] * 5)
        if n <= 20:
            scan_family("C5uni[%d]" % t, n, E)
    # all-pairs heavy [t,t,1,1,1] adjacency-heavy
    for t in (2, 3):
        scan_family("C5adj[%d,%d,1,1,1]" % (t, t), *odd_blowup(5, [t, t, 1, 1, 1]))
    # Petersen graph N=10 (triangle-free, vertex-transitive)
    pet = [(0,1),(1,2),(2,3),(3,4),(4,0),       # outer C5
           (5,7),(7,9),(9,6),(6,8),(8,5),        # inner pentagram
           (0,5),(1,6),(2,7),(3,8),(4,9)]        # spokes
    scan_family("Petersen_N10", 10, pet)
    # C7 (N=7) and C7-blowup symmetric
    scan_family("C7uni[2]", *odd_blowup(7, [2]*7))
    # two C5's sharing structure: C5 + C5 joined by single edge (still tf), symmetric two cores
    n2, E2 = union_disjoint((5, Cn(5)), (5, Cn(5)))
    E2j = E2 + [(0, 5)]   # join vertex 0 of each
    scan_family("twoC5_edge_N10", n2, E2j)
    # two C5 blowups [2,1,1,1,1] joined -> two equal would-be hubs
    nb, Eb = union_disjoint((6, odd_blowup(5,[2,1,1,1,1])[1]), (6, odd_blowup(5,[2,1,1,1,1])[1]))
    Ebj = Eb + [(0, 6)]
    scan_family("two_C5b_N12", nb, Ebj)

    print("\n" + "=" * 74)
    print("(B) RESULTS")
    print("  cuts tested        :", acc['n'])
    print("  |R|=0 / |R|=1 / >=2:", acc['R0'], acc['R1'], acc['Rge2'])
    print("  |R|>=2 case        :", acc['Rge2'], acc['ex'] or '(none)')
    print("  apex!=argmaxT      :", acc['apex_mismatch'], acc['apexex'] or '')
    print("  a_apex>sum_other O fail:", acc['half_fail'], acc['halfex'] or '(holds)')
    print("\n  NOTE: a_apex>sum(other a_o over O) is the 'apex carries >half the O-overload' test.")


if __name__ == "__main__":
    main()
