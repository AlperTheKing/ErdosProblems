r"""CLAUDE independent gate for the Codex COMMON-BLUE repair of the 2943 defect-28 (answers the 15:28 ASK).

UNDER TEST (Codex posts 15:15/15:21/15:27):
  CB-1 the 28 keys (x, 2930, h), x=29..42, h in {0,1}, owner 2 each satisfy the compiled
       CheckedC5BaseTransfer.TerminalData.Valid: blueb(x,2) & blueb(2930,2), x != 2930, dM({x,2930})+2 <= dB;
       claimed per-key dB=30, dM=27, adjustedSurplus=1; pairFree n(x,2930)=0; unreserved; NEW (not in old 19925).
  CB-2 the full new-key pool: enumerate ALL Valid+Free+unreserved+NEW keys for owners {0,1,2}; Codex claims 216
       genuinely new global FreeHalf keys (2824 owner-terminal half instances), full-shore reach 20141 (surplus 188).
  CB-3 THE ASK: is there a production condition beyond Valid+FreeHalf+activeOwner+unreserved that can forbid these?
       CANDIDATE = RESERVED-EDGE EXCLUSIVITY: each used pair reserves its TWO blue source->owner edges; all 14 Codex
       pairs SHARE the edge (2930,2). Under the most conservative ledger (each blue edge reservable by at most ONE
       used pair, and reserved halves REMOVED from the old source pool), does an edge-disjoint pair set still close
       the full-shore gap 28? Exact greedy + verification over the whole pool.
All exact/integer. Run from repo root: python problems/23/writeup/_claude_r29_commonblue_gate.py
"""
import importlib.util
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEAD = ROOT / "tmp/fanout/r29_gate/lead/r29_lead_gate.py"
P5G = Path(__file__).with_name("_claude_r29_pattern5_gate.py")
OWNERS = (0, 1, 2)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(u, v):
    return (u, v) if u < v else (v, u)


def main():
    lead = load("r29_lead", LEAD)
    p5 = load("r29_p5gate", P5G)
    data = lead.build()
    start = data["selectorStart"]
    rows = [tuple(r) for r in data["rows"]]
    for j in range(676):
        rows[start + j] = tuple(data["selectorMeta"][j]["anchorRow"])
    st = p5.full_state(data, tuple(rows))
    n, blue, bad = st["n"], st["blue"], st["bad"]
    pair, av, active_edges, masks, demand = st["pair"], st["av"], st["active_edges"], st["masks"], st["demand"]
    badj = defaultdict(set)
    for u, v in blue:
        badj[u].add(v)
        badj[v].add(u)
    madj = defaultdict(set)
    for u, v in bad:
        madj[u].add(v)
        madj[v].add(u)

    def dB2(x, y):
        return len(badj[x]) + len(badj[y]) - 2 * (y in badj[x])

    def dM2(x, y):
        return len(madj[x]) + len(madj[y]) - 2 * (y in madj[x])

    # CB-1: the specific 28 Codex keys
    print("=== CB-1: Codex 28 keys (x,2930,h), x=29..42, owner 2 ===")
    cb1_ok = True
    for x in range(29, 43):
        y, o = 2930, 2
        valid = (x != y and norm(x, o) in blue and norm(y, o) in blue and dM2(x, y) + 2 <= dB2(x, y))
        free = pair[x, y] == 0
        newk = all((x, y, h) not in masks and (y, x, h) not in masks for h in (0, 1))
        unres = all(not (h == 0 and norm(x, y) in active_edges and x in av) for h in (0, 1))
        row = (x, dB2(x, y), dM2(x, y), dB2(x, y) - dM2(x, y) - 2, valid, free, newk, unres)
        if not (valid and free and newk and unres and dB2(x, y) == 30 and dM2(x, y) == 27):
            cb1_ok = False
            print("  x=%d dB=%d dM=%d adjSur=%d valid=%s free=%s new=%s unres=%s  <-- MISMATCH" % row)
    print("  all 14 pairs: dB=30 dM=27 adjSurplus=1 valid+free+new+unreserved: %s" % cb1_ok)

    # CB-2: full pool enumeration
    print("=== CB-2: full new-key pool (owners 0,1,2) ===")
    pool = {}   # (x,y) unordered pair -> set of owners for which Valid+free; halves counted separately
    for o in OWNERS:
        cands = sorted(badj[o])
        for i, x in enumerate(cands):
            for y in cands[i + 1:]:
                if pair[x, y] != 0:
                    continue
                if dM2(x, y) + 2 <= dB2(x, y):
                    pool.setdefault((x, y), set()).add(o)
    # new keys = ordered halves not already in old masks and unreserved
    new_keys = {}
    for (x, y), owners in pool.items():
        for (a, b) in ((x, y), (y, x)):
            for h in (0, 1):
                if (a, b, h) in masks:
                    continue
                if h == 0 and norm(a, b) in active_edges and a in av:
                    continue
                m = 0
                for o in owners:
                    m |= 1 << o
                new_keys[(a, b, h)] = m
    hist = Counter(new_keys.values())
    full_reach_old = sum(v for m, v in Counter(masks.values()).items() if m & 7)
    full_reach_new = len(new_keys)
    print("  candidate pairs (unordered, Valid+free some owner): %d | new ordered-half keys: %d | owner-mask hist: %s"
          % (len(pool), full_reach_new, dict(hist)))
    print("  full-shore reach old %d + new %d = %d (Codex claim 20141; demand 19953)"
          % (full_reach_old, full_reach_new, full_reach_old + full_reach_new))

    # CB-3: conservative exclusivity ledger
    print("=== CB-3: reserved-edge-EXCLUSIVE ledger test ===")
    # deficits per owner after old flow (d05: singles 5775 each, shared 2600 => total 19925 vs 19953)
    # conservative model: each used unordered pair (x,y) w/ owner o consumes blue edges (x,o),(y,o); each blue edge
    # used at most once across ALL used pairs; reserved halves (x,o,h)/(o,x,h)/(y,o,h)/(o,y,h) removed from old pool.
    # gain: 2 halves (the pair's two ordered... conservative: the pair contributes its available new halves, cap 2).
    # greedy: prefer pairs whose reserved edges do not intersect old sources and are edge-disjoint.
    old_keys = set(masks.keys())
    used_edges = set()
    removed_old = 0
    gained = 0
    chosen = []
    # sort pairs: fewest old-source collisions first, then lexicographic
    def pair_cost(p):
        (x, y) = p
        o = min(pool[p])
        rem = sum(1 for k in ((x, o), (o, x), (y, o), (o, y)) for h in (0, 1) if (k[0], k[1], h) in old_keys)
        return (rem, p)
    for p in sorted(pool.keys(), key=pair_cost):
        if gained - removed_old >= 28:
            break
        (x, y) = p
        o = min(pool[p])
        e1, e2 = norm(x, o), norm(y, o)
        if e1 in used_edges or e2 in used_edges:
            continue
        halves = [k for k in ((x, y, 0), (x, y, 1), (y, x, 0), (y, x, 1)) if k in new_keys][:2]
        if not halves:
            continue
        rem = sum(1 for k in ((x, o), (o, x), (y, o), (o, y)) for h in (0, 1) if (k[0], k[1], h) in old_keys)
        used_edges.add(e1)
        used_edges.add(e2)
        removed_old += rem
        gained += len(halves)
        chosen.append((p, o, len(halves), rem))
    net = gained - removed_old
    print("  greedy edge-disjoint selection: pairs used %d | halves gained %d | old halves removed %d | NET %+d (need +28)"
          % (len(chosen), gained, removed_old, net))
    ok3 = net >= 28
    print("  conservative-exclusive ledger closes the gap: %s" % ok3)

    print("=" * 76)
    verdict_ok = cb1_ok and full_reach_new >= 28 and ok3
    print("VERDICT: CB-1 %s | pool %d new keys | CB-3 exclusive-ledger closes: %s" % (cb1_ok, full_reach_new, ok3))
    if verdict_ok:
        print("=> Codex common-blue repair is ROBUST even under the most conservative (edge-exclusive, pool-deducting)")
        print("   adapter semantics; ANSWER to ASK: no compiled condition forbids it, and the one UNCOMPILED candidate")
        print("   (reserved-edge exclusivity) does NOT break it either -- P5 stays as adversarial fallback for R29.")
    else:
        print("=> under edge-exclusive reservation the 14-pair (shared 2930) family alone is insufficient/pool too")
        print("   small: the missing adapter condition IS load-bearing; state in reply.")
    sys.exit(0 if verdict_ok else 1)


if __name__ == "__main__":
    main()
