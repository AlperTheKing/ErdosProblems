// Does the kappa=8 census law ("every connected bipartite Delta<=6 piece with
// e=3m-4 is FrozenFlag", verified m<=18) extend to large m?  (2026-06-12)
//
// Reduction (logged in PROOF_STATE): if a 6-regular bipartite connected graph G
// has EVERY vertex unlockable, then G minus any 4 edges (still connected:
// vertex-transitive 6-regular => 6-edge-connected) is a kappa=8 piece whose
// full vertices all keep their witnesses (edge deletion preserves properness,
// N(v) of full v unchanged) => FrozenFlag=0 => census law fails at that m.
//
// unlockable(v): exists proper 3-colouring of G-v with each colour appearing
// <=2 times on N(v)  (piece_hunt.cpp locked-mode definition).
// Exhaustive verdict uses colour-symmetry canonical pruning (condition is
// colour-symmetric). Node cap => CAPPED (unknown) instead of false verdict.
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <thread>
#include <mutex>
#include <atomic>
using namespace std;

struct BG {
  int n = 0;
  uint64_t adj[64] = {};
  void addEdge(int a, int b) { adj[a] |= 1ull << b; adj[b] |= 1ull << a; }
  int deg(int x) const { return __builtin_popcountll(adj[x]); }
};

enum Verdict { UNLOCKABLE, LOCKED, CAPPED };

static Verdict unlockable(const BG& g, int v, uint64_t cap, bool canon = true) {
  vector<int> order;
  uint64_t nbv = g.adj[v];
  uint64_t seen = 1ull << v;
  for (int x = 0; x < g.n; x++) if (nbv >> x & 1) { order.push_back(x); seen |= 1ull << x; }
  // BFS from N(v) for the rest (locality => early conflicts)
  for (size_t h = 0; h < order.size(); h++) {
    uint64_t nb = g.adj[order[h]] & ~seen;
    while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; order.push_back(u); seen |= 1ull << u; }
  }
  for (int x = 0; x < g.n; x++) if (!(seen >> x & 1)) order.push_back(x);  // other components of G-v
  int m = (int)order.size();
  vector<int8_t> col(g.n, -1);
  vector<int8_t> tryc(m, 0), usedMax(m + 1, 0);
  int cnt[3] = {0, 0, 0};
  uint64_t nodes = 0;
  int pos = 0;
  usedMax[0] = -1;                               // max colour used before pos
  while (pos >= 0) {
    if (pos == m) return UNLOCKABLE;
    if (++nodes > cap) return CAPPED;
    int x = order[pos];
    bool onN = nbv >> x & 1;
    bool adv = false;
    int cmax = canon ? usedMax[pos] + 1 : 2; if (cmax > 2) cmax = 2;   // colour-symmetry canonical
    for (int c = tryc[pos]; c <= cmax; c++) {
      if (onN && cnt[c] == 2) continue;
      bool ok = true;
      uint64_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        if (u != v && col[u] == c) { ok = false; break; } }
      if (!ok) continue;
      col[x] = c; if (onN) cnt[c]++;
      tryc[pos] = c + 1;
      usedMax[pos + 1] = usedMax[pos] > c ? usedMax[pos] : c;
      pos++; if (pos < m) tryc[pos] = 0;
      adv = true; break;
    }
    if (!adv) {
      tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if ((nbv >> y & 1)) cnt[col[y]]--; col[y] = -1; }
    } else continue;
  }
  return LOCKED;
}

static bool bipartite(const BG& g) {
  int side[64]; memset(side, -1, sizeof(side));
  for (int s = 0; s < g.n; s++) {
    if (side[s] >= 0) continue;
    side[s] = 0; vector<int> st = {s};
    while (!st.empty()) { int x = st.back(); st.pop_back();
      uint64_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        if (side[u] < 0) { side[u] = side[x] ^ 1; st.push_back(u); }
        else if (side[u] == side[x]) return false; } }
  }
  return true;
}

static bool connectedG(const BG& g) {
  uint64_t seen = 1; vector<int> st = {0};
  while (!st.empty()) { int x = st.back(); st.pop_back();
    uint64_t nb = g.adj[x] & ~seen;
    while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; seen |= 1ull << u; st.push_back(u); } }
  return __builtin_popcountll(seen) == g.n;
}

static void report(const char* name, const BG& g, bool oneVertexOnly, uint64_t cap, bool canon = true) {
  int e = 0, maxd = 0, mind = 99;
  for (int x = 0; x < g.n; x++) { e += g.deg(x); if (g.deg(x) > maxd) maxd = g.deg(x); if (g.deg(x) < mind) mind = g.deg(x); }
  e /= 2;
  printf("%s: m=%d e=%d reg=[%d,%d] bip=%d conn=%d%s\n", name, g.n, e, mind, maxd,
         bipartite(g), connectedG(g), oneVertexOnly ? " (vertex-transitive: testing v=0 only)" : "");
  fflush(stdout);
  int nv = oneVertexOnly ? 1 : g.n;
  atomic<int> next(0), nUnl(0), nLock(0), nCap(0);
  mutex mu; string lockedList, capList;
  auto worker = [&]() {
    for (;;) { int v = next.fetch_add(1); if (v >= nv) break;
      Verdict w = unlockable(g, v, cap, canon);
      if (w == UNLOCKABLE) nUnl++;
      else if (w == LOCKED) { nLock++; lock_guard<mutex> lk(mu); lockedList += " " + to_string(v); }
      else { nCap++; lock_guard<mutex> lk(mu); capList += " " + to_string(v); } }
  };
  vector<thread> th; int nt = nv < 8 ? nv : 8;
  for (int i = 0; i < nt; i++) th.emplace_back(worker);
  for (auto& t : th) t.join();
  printf("  unlockable=%d locked=%d capped=%d%s%s%s%s\n", nUnl.load(), nLock.load(), nCap.load(),
         nLock ? " lockedV:" : "", lockedList.c_str(), nCap ? " cappedV:" : "", capList.c_str());
  printf("  -> %s\n", (nLock == 0 && nCap == 0)
      ? "ALL UNLOCKABLE => minus-4-edges is a FREE kappa=8 piece at this m (census law fails here)"
      : (nLock > 0 ? "has locked vertex (law-consistent)" : "INCONCLUSIVE (cap hit)"));
  fflush(stdout);
}

static BG circulant(int n, int o1, int o2, int o3) {
  BG g; g.n = n;
  for (int i = 0; i < n; i++) { g.addEdge(i, (i + o1) % n); g.addEdge(i, (i + o2) % n); g.addEdge(i, (i + o3) % n); }
  return g;
}

// find a witness for v (proper 3-col of G-v, <=2 per colour on N(v)) and print it
static bool witnessPrint(const BG& g, int v) {
  vector<int> order; uint64_t nbv = g.adj[v], seen = 1ull << v;
  for (int x = 0; x < g.n; x++) if (nbv >> x & 1) { order.push_back(x); seen |= 1ull << x; }
  for (size_t h = 0; h < order.size(); h++) { uint64_t nb = g.adj[order[h]] & ~seen;
    while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; order.push_back(u); seen |= 1ull << u; } }
  for (int x = 0; x < g.n; x++) if (!(seen >> x & 1)) order.push_back(x);
  int m = (int)order.size();
  vector<int8_t> col(g.n, -1), tryc(m, 0), usedMax(m + 1, 0);
  int cnt[3] = {0,0,0}; int pos = 0; usedMax[0] = -1;
  while (pos >= 0 && pos < m) {
    int x = order[pos]; bool onN = nbv >> x & 1; bool adv = false;
    int cmax = usedMax[pos] + 1; if (cmax > 2) cmax = 2;
    for (int c = tryc[pos]; c <= cmax; c++) {
      if (onN && cnt[c] == 2) continue;
      bool ok = true; uint64_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        if (u != v && col[u] == c) { ok = false; break; } }
      if (!ok) continue;
      col[x] = c; if (onN) cnt[c]++; tryc[pos] = c + 1;
      usedMax[pos + 1] = usedMax[pos] > c ? usedMax[pos] : c;
      pos++; if (pos < m) tryc[pos] = 0; adv = true; break;
    }
    if (!adv) { tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = order[pos]; if (nbv >> y & 1) cnt[col[y]]--; col[y] = -1; } }
  }
  if (pos != m) { printf("WITNESS v=%d NONE (locked)\n", v); return false; }
  printf("WITNESS v=%d:", v);
  for (int x = 0; x < g.n; x++) printf(" %d", x == v ? -1 : col[x]);
  printf("\n");
  return true;
}

// xorshift rng, fixed seed (reproducible)
static uint64_t RNG = 88172645463325252ull;
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

// random simple 6-regular bipartite on k+k via 6 random perfect matchings
static bool rand6reg(BG& g, int k) {
  g = BG(); g.n = 2 * k;
  for (int rep = 0; rep < 6; rep++) {
    for (int tries = 0;; tries++) {
      if (tries > 2000) return false;
      vector<int> perm(k); for (int i = 0; i < k; i++) perm[i] = i;
      for (int i = k - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(perm[i], perm[j]); }
      bool ok = true;
      for (int i = 0; i < k; i++) if (g.adj[i] >> (k + perm[i]) & 1) { ok = false; break; }
      if (!ok) continue;
      for (int i = 0; i < k; i++) g.addEdge(i, k + perm[i]);
      break;
    }
  }
  return connectedG(g);
}

static void delEdge(BG& g, int a, int b) { g.adj[a] &= ~(1ull << b); g.adj[b] &= ~(1ull << a); }

// delete 4 random edges keeping connectivity => kappa=8 piece
static bool make_kappa8(BG& g) {
  for (int d = 0; d < 4; d++) {
    for (int tries = 0; tries < 500; tries++) {
      int a = rnd() % g.n; uint64_t nb = g.adj[a];
      if (!nb) continue;
      int cntb = __builtin_popcountll(nb), pick = rnd() % cntb, b = -1;
      while (pick-- >= 0) { b = __builtin_ctzll(nb); nb &= nb - 1; }
      BG h = g; delEdge(h, a, b);
      if (connectedG(h)) { g = h; break; }
      if (tries == 499) return false;
    }
  }
  return true;
}

int main(int argc, char** argv) {
  if (argc > 1 && string(argv[1]) == "pg") {
    // incidence graph of PG(2,5): 31 points + 31 lines, 6-regular bipartite, GIRTH 6
    // (locally tree-like to depth 2 => maximal colouring freedom; extreme C1 stress test)
    vector<array<int,3>> reps;                   // canonical 1-dim subspaces of F5^3
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
      if (!a && !b && !c) continue;
      if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
      reps.push_back({a, b, c});
    }
    BG g; g.n = 62;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g.addEdge(i, 31 + j);
    }
    report("PG(2,5) incidence m=62 girth-6 (flag-transitive: v=0)", g, true, 1ull << 40);
    for (int k : {18, 20}) {
      BG h; if (!rand6reg(h, k)) continue;
      char nm[64]; snprintf(nm, 64, "rand 6-reg bip m=%d (big)", 2 * k);
      report(nm, h, false, 1ull << 40);
    }
    return 0;
  }
  if (argc > 1 && string(argv[1]) == "fk") {
    // (FK) COUNTEREXAMPLE TEST: H* = PG(2,5) incidence minus 3 vertex-disjoint
    // edges: connected, bipartite (3-col), Delta<=6, Sum b = 6, |V|=62>=9.
    // (FK) claims a frozen FULL vertex exists. Test all 62 vertices directly.
    // Then hunt kappa(X)=6|X|-2e(X)<8 violations (minimal-shore hypothesis) by
    // steepest-ascent hill-climb on f(X)=e(X)-3|X| (violation iff f>=-3) over
    // 2<=|X|<=60, 4000 random restarts.
    vector<array<int,3>> reps;
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
      if (!a && !b && !c) continue;
      if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
      reps.push_back({a, b, c});
    }
    BG g; g.n = 62;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g.addEdge(i, 31 + j);
    }
    int delv[3] = {0, 7, 15};
    for (int t = 0; t < 3; t++) {
      int a = delv[t]; uint64_t nb = g.adj[a]; int b = -1;
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        if (g.deg(u) == 6) { b = u; break; } }       // partner still full => 6 distinct endpoints
      delEdge(g, a, b);
      printf("deleted edge (%d,%d)\n", a, b);
    }
    int sumb = 0; for (int x = 0; x < g.n; x++) sumb += 6 - g.deg(x);
    printf("H*: connected=%d bipartite=%d sum_b=%d (need 6)\n", connectedG(g), bipartite(g), sumb);
    report("H* = PG(2,5) - 3 disjoint edges, ALL 62 vertices", g, false, 1ull << 40);
    int nFull = 0; for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) nFull++;
    printf("full vertices: %d (the 6 deficient ones are irrelevant to (FK))\n", nFull);
    // kappa hunt on H* (and implicitly PG: e_H<=e_PG so kappa_H>=kappa_PG... hunt H* directly)
    int bestF = -1000; uint64_t bestX = 0;
    for (int rs = 0; rs < 4000; rs++) {
      uint64_t X = 0; int x = 0, eX = 0;
      int target = 2 + (int)(rnd() % 59);
      while (x < target) { int u = rnd() % 62; if (!(X >> u & 1)) {
        eX += __builtin_popcountll(g.adj[u] & X); X |= 1ull << u; x++; } }
      for (;;) {                                  // steepest ascent on f = e - 3x
        int bd = -1000, bu = -1;
        for (int u = 0; u < 62; u++) {
          int d;
          if (X >> u & 1) { if (x <= 2) continue; d = -((int)__builtin_popcountll(g.adj[u] & X)) + 3; }
          else { if (x >= 60) continue; d = (int)__builtin_popcountll(g.adj[u] & X) - 3; }
          if (d > bd) { bd = d; bu = u; }
        }
        if (bd <= 0) break;
        if (X >> bu & 1) { X &= ~(1ull << bu); x--; eX -= __builtin_popcountll(g.adj[bu] & X); }
        else { eX += __builtin_popcountll(g.adj[bu] & X); X |= 1ull << bu; x++; }
      }
      int f = eX - 3 * x;
      if (f > bestF) { bestF = f; bestX = X; }
    }
    printf("kappa hunt: max f(X)=e-3|X| over hill-climbs = %d (|X|=%d) => min kappa found = %d (violation iff <8)\n",
           bestF, __builtin_popcountll(bestX), -2 * bestF);
    for (int v = 0; v < g.n; v++) witnessPrint(g, v);   // full certificate set
    return 0;
  }
  if (argc > 1 && string(argv[1]) == "pgdel") {
    // DIRECT refutation: PG(2,5) incidence minus 4 spread-out edges = kappa=8 piece;
    // test ALL 62 vertices; FrozenFlag analogue = some FULL (deg-6) vertex locked.
    vector<array<int,3>> reps;
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
      if (!a && !b && !c) continue;
      if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
      reps.push_back({a, b, c});
    }
    BG g; g.n = 62;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g.addEdge(i, 31 + j);
    }
    // delete 4 edges with 8 distinct endpoints, far apart; assert still connected
    int delv[4] = {0, 7, 15, 23};
    for (int t = 0; t < 4; t++) {
      int a = delv[t]; uint64_t nb = g.adj[a]; int b = -1;
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        bool used = false;
        for (int s = 0; s < t; s++) if (u == delv[s]) used = true;
        if (!used && g.deg(u) == 6) { b = u; break; } }
      delEdge(g, a, b);
      printf("deleted edge (%d,%d)\n", a, b);
    }
    printf("connected after deletions: %d\n", connectedG(g));
    report("PG(2,5) minus 4 edges = kappa8 piece m=62 ALL vertices", g, false, 1ull << 40);
    // witness print for the 6-regular graph, v=0 (independent verification artifact)
    BG g2; g2.n = 62;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g2.addEdge(i, 31 + j);
    }
    {
      int v = 0;
      vector<int> order; uint64_t nbv = g2.adj[v], seen = 1ull << v;
      for (int x = 0; x < g2.n; x++) if (nbv >> x & 1) { order.push_back(x); seen |= 1ull << x; }
      for (size_t h = 0; h < order.size(); h++) { uint64_t nb = g2.adj[order[h]] & ~seen;
        while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; order.push_back(u); seen |= 1ull << u; } }
      for (int x = 0; x < g2.n; x++) if (!(seen >> x & 1)) order.push_back(x);
      int m = (int)order.size();
      vector<int8_t> col(g2.n, -1); vector<int8_t> tryc(m, 0); vector<int8_t> usedMax(m + 1, 0);
      int cnt[3] = {0,0,0}; int pos = 0; usedMax[0] = -1;
      while (pos >= 0 && pos < m) {
        int x = order[pos]; bool onN = nbv >> x & 1; bool adv = false;
        int cmax = usedMax[pos] + 1; if (cmax > 2) cmax = 2;
        for (int c = tryc[pos]; c <= cmax; c++) {
          if (onN && cnt[c] == 2) continue;
          bool ok = true; uint64_t nb = g2.adj[x];
          while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
            if (u != v && col[u] == c) { ok = false; break; } }
          if (!ok) continue;
          col[x] = c; if (onN) cnt[c]++; tryc[pos] = c + 1;
          usedMax[pos + 1] = usedMax[pos] > c ? usedMax[pos] : c;
          pos++; if (pos < m) tryc[pos] = 0; adv = true; break;
        }
        if (!adv) { tryc[pos] = 0; pos--;
          if (pos >= 0) { int y = order[pos]; if (nbv >> y & 1) cnt[col[y]]--; col[y] = -1; } }
      }
      if (pos == m) {
        printf("WITNESS v=0 colouring (vertex:colour):");
        for (int x = 0; x < g2.n; x++) printf(" %d:%d", x, x == v ? -1 : col[x]);
        printf("\n");
      } else printf("NO WITNESS (locked)\n");
    }
    return 0;
  }
  { BG g; g.n = 8;                               // POSITIVE control: K44 must be unlockable
    for (int a = 0; a < 4; a++) for (int b = 0; b < 4; b++) g.addEdge(a, 4 + b);
    report("K44 (positive control, expect UNLOCKABLE)", g, false, 1ull << 40); }
  { BG g; g.n = 12;
    for (int a = 0; a < 6; a++) for (int b = 0; b < 6; b++) g.addEdge(a, 6 + b);
    report("K66 (control, expect locked)", g, true, 1ull << 40); }
  // cross-validation: canonical pruning OFF (independent of the symmetry argument)
  report("C20(1,3,5) NOCANON xval", circulant(20, 1, 3, 5), true, 1ull << 40, false);
  report("C24(1,3,5) NOCANON xval", circulant(24, 1, 3, 5), true, 1ull << 40, false);
  // random non-symmetric 6-regular bipartite, ALL vertices
  for (int k : {10, 12, 14}) {
    for (int rep = 0; rep < 3; rep++) {
      BG g; if (!rand6reg(g, k)) { printf("rand6reg k=%d rep=%d: FAILED to build\n", k, rep); continue; }
      char nm[64]; snprintf(nm, 64, "rand 6-reg bip m=%d #%d", 2 * k, rep);
      report(nm, g, false, 1ull << 40);
    }
  }
  // actual kappa=8 pieces: random 6-reg minus 4 edges, ALL vertices (full-vertex locking is the law)
  for (int k : {10, 12, 14}) {
    for (int rep = 0; rep < 3; rep++) {
      BG g; if (!rand6reg(g, k)) continue;
      if (!make_kappa8(g)) { printf("kappa8 build failed k=%d\n", k); continue; }
      char nm[64]; snprintf(nm, 64, "rand kappa8 piece m=%d #%d (e=3m-4)", 2 * k, rep);
      report(nm, g, false, 1ull << 40);
    }
  }
  return 0;
}
