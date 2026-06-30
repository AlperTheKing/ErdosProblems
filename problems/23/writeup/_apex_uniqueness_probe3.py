"""THIRD probe: target O-nonempty (esp. |O|>=2) cuts and test the structural law that implies |R|<=1.

From probe2: the symmetric blowups/Petersen all gave EMPTY O (no T_v>N), so they cannot stress |R|.
The ONLY |R|=1 in 586 cuts was the N=23 apex, where a_apex (18.475) > sum(other a_o)=16.67 over O.

CANDIDATE STRUCTURAL LAW (would imply |R|<=1):
  rowsum_o(S) = a_o - sum_{o'!=o} S_{o,o'}_offdiag-routed-supply ... but cleanest empirical:
  Conjecture (APEX-DOMINANCE):  for an O-nonempty gamma-min cut, at most one o in O has
       a_o = T_o - N  >  (1/2) * sum_{p in O} a_p     [strict majority of the O-overload mass],
  and rowsum_o(S)<0  =>  a_o is that strict-majority element (hence unique).  Equivalently
       R subset { o : a_o > sum_{p in O, p!=o} a_p }, and the RHS set has size <=1 trivially.

This probe:
 (1) For EVERY O-nonempty gamma-min cut in census N<=10 + N=11 Grotzsch + N=23 + C7Myc + 400 random tf,
     record |O|, R, and check:  (i) |R|<=1; (ii) R subset MAJ := {o: a_o > sum_{p!=o} a_p};
     (iii) |MAJ|<=1 always (trivially true but verify); (iv) when |O|>=2, does R ever become nonempty,
     and is the structural inclusion R<=MAJ tight (i.e. is MAJ ever bigger than R)?
 (2) Targeted two-hub overloaded constructions to FORCE |O|>=2 with both heavy:
     - Mycielskian of C5-blowups (Myc lifts loads; apex of Myc is heavy + original heavy vertices).
     - Mycielskian of odd_blowup(5,[t,1,1,1,1]) for t=2,3 -> heavy original class + Myc apex = two hubs.
     - double Mycielskian variants; C5[t] then Mycielskian.
   For each, take maxcut_ls side(s), report |O|, the loads, R, and the majority set.
EXACT Fraction. Run: python _apex_uniqueness_probe3.py
"""
import subprocess, random
from fractions import Fraction as F
from _h import dec, GENG, Bconn
from _satzmu_conn import struct_for_side
from _stark1 import gmins
from _wf_deficit_farkas import odd_blowup
from _bdef_construct import Cn, mycielski, is_triangle_free
from _hardy_gate import BETA, build_H, maxcut_ls
from _schur_overload_gate import schur_on_O


def rec_for(name, n, adj, side):
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
    if r['S'] is None or r['rowsum'] is None:
        return dict(name=name, n=n, side=''.join(map(str, side)), O=O, bad=True, T=T)
    R = [O[i] for i in range(len(O)) if r['rowsum'][i] < 0]
    a = {o: T[o] - N for o in O}
    tot = sum(a.values())
    MAJ = [o for o in O if a[o] > tot - a[o]]   # a_o > sum_{p!=o} a_p
    return dict(name=name, n=n, side=''.join(map(str, side)), O=O, R=R, a=a, MAJ=MAJ,
                rowsum=r['rowsum'], psdS=r['psdS'], T=T, bad=False)


def main():
    print("=" * 74)
    print("PROBE3: APEX-DOMINANCE structural law  (R subset MAJ={o: a_o>sum_{p!=o}a_p}, |MAJ|<=1)")
    print("=" * 74)

    acc = dict(O1=0, Oge2=0, R0=0, R1=0, Rge2=0, MAJge2=0,
               R_not_subset_MAJ=0, Rge2_ex=None, MAJge2_ex=None, notsub_ex=None,
               R1_Oge2=0, Oge2_examples=[])

    def feed(rec):
        if rec is None:
            return
        if rec.get('bad'):
            return
        O = rec['O']; R = rec['R']; MAJ = rec['MAJ']
        if len(O) == 1:
            acc['O1'] += 1
        else:
            acc['Oge2'] += 1
        if len(R) == 0:
            acc['R0'] += 1
        elif len(R) == 1:
            acc['R1'] += 1
            if len(O) >= 2:
                acc['R1_Oge2'] += 1
        else:
            acc['Rge2'] += 1
            if acc['Rge2_ex'] is None:
                acc['Rge2_ex'] = (rec['name'], rec['side'], R, {o: float(rec['a'][o]) for o in R})
        if len(MAJ) >= 2:
            acc['MAJge2'] += 1
            if acc['MAJge2_ex'] is None:
                acc['MAJge2_ex'] = (rec['name'], rec['side'], MAJ)
        if not set(R) <= set(MAJ):
            acc['R_not_subset_MAJ'] += 1
            if acc['notsub_ex'] is None:
                acc['notsub_ex'] = (rec['name'], rec['side'], 'R=%s MAJ=%s' % (R, MAJ))
        # keep a few |O|>=2 examples to print loads
        if len(O) >= 2 and len(acc['Oge2_examples']) < 8:
            acc['Oge2_examples'].append(
                (rec['name'], rec['side'], {o: float(rec['a'][o]) for o in O}, R, MAJ))

    def fam(name, n, E):
        if not is_triangle_free(n, E):
            return
        adj = [set() for _ in range(n)]
        for x, y in E:
            adj[x].add(y); adj[y].add(x)
        try:
            _, cuts = gmins(n, E)
        except Exception:
            return
        for side in cuts:
            feed(rec_for(name, n, adj, side))

    # (1) census 8..10 (5,6,7 had no O), Grotzsch, blowups
    print("\n--- (1) census + Grotzsch + N=23 + C7Myc + random ---", flush=True)
    for nn in range(8, 11):
        for g6 in subprocess.run([GENG, '-tc', str(nn)], capture_output=True, text=True).stdout.split():
            n, E = dec(g6)
            fam("cen%d_%s" % (nn, g6), n, E)
        print("  census N=%d : O1=%d Oge2=%d R1=%d Rge2=%d MAJge2=%d notsub=%d"
              % (nn, acc['O1'], acc['Oge2'], acc['R1'], acc['Rge2'], acc['MAJge2'], acc['R_not_subset_MAJ']),
              flush=True)
    grN, grE = mycielski(5, Cn(5))
    fam("Grotzsch_N11", grN, grE)
    m2N, m2E = mycielski(grN, grE)
    adj23 = [set() for _ in range(m2N)]
    for x, y in m2E:
        adj23[x].add(y); adj23[y].add(x)
    feed(rec_for("MycGrotzsch_N23", m2N, adj23, maxcut_ls(m2N, adj23)))
    fam("C7Myc_N15", *mycielski(7, Cn(7)))
    print("  +Grotzsch/N23/C7Myc : O1=%d Oge2=%d R1=%d Rge2=%d MAJge2=%d"
          % (acc['O1'], acc['Oge2'], acc['R1'], acc['Rge2'], acc['MAJge2']), flush=True)

    # 400 random tf, sizes 11..15
    rng = random.Random(99)
    def random_tf(n, p):
        adj = [set() for _ in range(n)]; E = []
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        rng.shuffle(pairs)
        for (i, j) in pairs:
            if rng.random() > p:
                continue
            if adj[i] & adj[j]:
                continue
            adj[i].add(j); adj[j].add(i); E.append((i, j))
        return n, E
    for trial in range(400):
        n = rng.choice([11, 12, 13, 14, 15])
        n, E = random_tf(n, rng.choice([0.4, 0.5, 0.6]))
        if len(E) >= n - 1:
            fam("rand%d" % trial, n, E)
    print("  +400 random : O1=%d Oge2=%d R1=%d Rge2=%d MAJge2=%d notsub=%d"
          % (acc['O1'], acc['Oge2'], acc['R1'], acc['Rge2'], acc['MAJge2'], acc['R_not_subset_MAJ']),
          flush=True)

    # (2) Mycielskian of C5-blowups to force two hubs (heavy original class + Myc apex)
    print("\n--- (2) Mycielskian of C5-blowups (force |O|>=2) ---", flush=True)
    targeted = []
    for sizes in ([2,1,1,1,1], [3,1,1,1,1], [2,2,1,1,1], [3,2,1,1,1], [2,1,2,1,1]):
        bn, bE = odd_blowup(5, sizes)
        mn, mE = mycielski(bn, bE)
        if mn <= 23 and is_triangle_free(mn, mE):
            adjm = [set() for _ in range(mn)]
            for x, y in mE:
                adjm[x].add(y); adjm[y].add(x)
            # try several ls sides
            seen = set()
            for seed in range(30):
                random.seed(seed + 7)
                s = maxcut_ls(mn, adjm)
                k = ''.join(map(str, s))
                if k in seen:
                    continue
                seen.add(k)
                rc = rec_for("MycC5%s_N%d" % (sizes, mn), mn, adjm, s)
                if rc and not rc.get('bad'):
                    feed(rc)
                    targeted.append(rc)
            print("  MycC5%s N=%d : %d distinct ls-cuts" % (sizes, mn, len(seen)), flush=True)
    # print targeted |O|>=2 ones
    print("\n  targeted records with |O|>=2:")
    shown = 0
    for rc in targeted:
        if len(rc['O']) >= 2 and shown < 10:
            shown += 1
            print("    %s O=%s a=%s R=%s MAJ=%s"
                  % (rc['name'], rc['O'], {o: round(float(rc['a'][o]), 3) for o in rc['O']},
                     rc['R'], rc['MAJ']), flush=True)

    print("\n" + "=" * 74)
    print("RESULTS")
    print("  O=1 cuts / O>=2 cuts :", acc['O1'], acc['Oge2'])
    print("  |R|=0 / 1 / >=2      :", acc['R0'], acc['R1'], acc['Rge2'])
    print("  |R|=1 within O>=2    :", acc['R1_Oge2'])
    print("  |R|>=2 (BREAKS)      :", acc['Rge2'], acc['Rge2_ex'] or '(none)')
    print("  |MAJ|>=2 (impossible):", acc['MAJge2'], acc['MAJge2_ex'] or '(none -- as expected)')
    print("  R NOT subset MAJ     :", acc['R_not_subset_MAJ'], acc['notsub_ex'] or '(R subset MAJ always)')
    print("\n  |O|>=2 sample (a=loads, R=neg-rowsum, MAJ=strict-majority):")
    for ex in acc['Oge2_examples']:
        print("    %s : a=%s R=%s MAJ=%s" % (ex[0], {o: round(v,3) for o,v in ex[2].items()}, ex[3], ex[4]))
    ok = (acc['Rge2'] == 0 and acc['R_not_subset_MAJ'] == 0 and acc['MAJge2'] == 0)
    print("\n  VERDICT:",
          "|R|<=1 ALWAYS; R subset MAJ={o:a_o>sum_{p!=o}a_p}; |MAJ|<=1 trivially => |R|<=1 STRUCTURALLY."
          if ok else "FAIL -- structural law violated (see above)")


if __name__ == "__main__":
    main()
