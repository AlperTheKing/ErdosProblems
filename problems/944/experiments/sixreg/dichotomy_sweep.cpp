// Conjecture (D) falsify-first sweep (2026-06-12).
// (D): every deficiency-6 shore H (connected, 3-colourable, Delta<=6, Sum b=6) is
//   branch 1: some FULL vertex frozen (no proper 3-col of H-v with <=2 per colour on N(v)), OR
//   branch 2: Avoid(Col(H)) = [3]^6 (every outside trace avoided by some achievable anchor trace).
// A NEITHER graph refutes (D) (subject to a later kappa(X)>=8 axiom check).
// Population: random 6-reg bipartite -3e, random balanced tripartite 6-reg -3e,
// circulants C_{2k}(1,3,5) -3e, Q6 -3e, PG(2,5) -3e (control: branch 2 only).
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <string>
#include <vector>
#include <array>
#include <thread>
#include <atomic>
#include <mutex>
#include <bitset>
using namespace std;

static const int MAXN = 64, NTAU = 729;
static const int POW3[7] = {1,3,9,27,81,243,729};

struct BG {
  int n = 0;
  uint64_t adj[MAXN] = {};
  void addEdge(int a, int b) { adj[a] |= 1ull << b; adj[b] |= 1ull << a; }
  void delEdge(int a, int b) { adj[a] &= ~(1ull << b); adj[b] &= ~(1ull << a); }
  int deg(int x) const { return __builtin_popcountll(adj[x]); }
};

static bool connectedG(const BG& g) {
  uint64_t seen = 1; vector<int> st = {0};
  while (!st.empty()) { int x = st.back(); st.pop_back();
    uint64_t nb = g.adj[x] & ~seen;
    while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1; seen |= 1ull << u; st.push_back(u); } }
  return __builtin_popcountll(seen) == g.n;
}

struct Solver {
  const BG* g; int del; uint64_t nbv;
  uint8_t dom[MAXN]; int8_t col[MAXN];
  int cnt[3];
  vector<pair<int,uint8_t>> trail;
  uint64_t nodes = 0, cap = 300000000ull;
  bool shrink(int u, uint8_t bit) {
    if (!(dom[u] & bit)) return true;
    trail.push_back({u, dom[u]});
    dom[u] &= ~bit;
    return dom[u] != 0;
  }
  int solve() {                                  // 1 found / 0 none / 2 capped
    if (++nodes > cap) return 2;
    int x = -1, best = 4;
    for (int u = 0; u < g->n; u++)
      if (col[u] < 0) { int p = __builtin_popcount(dom[u]);
        if (p < best) { best = p; x = u; if (p <= 1) break; } }
    if (x < 0) return 1;
    for (int c = 0; c < 3; c++) {
      if (!(dom[x] >> c & 1)) continue;
      bool ok = true;
      size_t mark = trail.size();
      col[x] = c;
      bool onN = del >= 0 && (nbv >> x & 1);
      if (onN) {
        cnt[c]++;
        if (cnt[c] == 2) {
          uint64_t nb = nbv;
          while (nb) { int w = __builtin_ctzll(nb); nb &= nb - 1;
            if (w != x && col[w] < 0 && !shrink(w, 1 << c)) { ok = false; break; } }
        }
      }
      if (ok) {
        uint64_t nb = g->adj[x];
        while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
          if (col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
      }
      if (ok) { int r = solve(); if (r) return r; }
      while (trail.size() > mark) { dom[trail.back().first] = trail.back().second; trail.pop_back(); }
      if (onN) cnt[c]--;
      col[x] = -1;
    }
    return 0;
  }
};

// del=-1: plain colouring with anchor trace fixed; del=v: witness query (<=2 counts)
static int query(const BG& g, const int* anch, int del, const int* fixTrace) {
  Solver s; s.g = &g; s.del = del; s.nbv = del >= 0 ? g.adj[del] : 0;
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  if (fixTrace)
    for (int i = 0; i < 6; i++)
      if (anch[i] != del) s.dom[anch[i]] = 1 << fixTrace[i];
  if (del >= 0) s.col[del] = 3;
  return s.solve();
}

static int canon6(int t0) {
  static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
  int best = 99999;
  for (auto& p : P) { int h = 0, t = t0;
    for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
    if (h < best) best = h; }
  return best;
}

static uint64_t RNG = 0x9E3779B97F4A7C15ull;
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

static bool randMatchUnion(BG& g, const vector<int>& A, const vector<int>& B, int reps) {
  int k = (int)A.size();
  for (int r = 0; r < reps; r++) {
    for (int tries = 0;; tries++) {
      if (tries > 4000) return false;
      vector<int> perm(k); for (int i = 0; i < k; i++) perm[i] = i;
      for (int i = k - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(perm[i], perm[j]); }
      bool ok = true;
      for (int i = 0; i < k; i++) if (g.adj[A[i]] >> B[perm[i]] & 1) { ok = false; break; }
      if (!ok) continue;
      for (int i = 0; i < k; i++) g.addEdge(A[i], B[perm[i]]);
      break;
    }
  }
  return true;
}

static bool minus3disjoint(BG& g) {              // delete 3 vertex-disjoint edges, keep connected
  uint64_t used = 0;
  for (int d = 0; d < 3; d++) {
    for (int tries = 0; tries < 2000; tries++) {
      int a = rnd() % g.n;
      if (used >> a & 1) continue;
      uint64_t nb = g.adj[a] & ~used;
      if (!nb) continue;
      int cnt = __builtin_popcountll(nb), pick = rnd() % cnt, b = -1;
      while (pick-- >= 0) { b = __builtin_ctzll(nb); nb &= nb - 1; }
      BG h = g; h.delEdge(a, b);
      if (!connectedG(h)) continue;
      g = h; used |= (1ull << a) | (1ull << b);
      break;
    }
  }
  int sb = 0; for (int x = 0; x < g.n; x++) sb += 6 - g.deg(x);
  return sb == 6;
}

struct Result { string name; int m, lockedFull, colSz, avoidCov; bool neither; };

static Result analyze(const string& name, const BG& g) {
  int anch[6], na = 0;
  for (int x = 0; x < g.n; x++) if (g.deg(x) == 5) { if (na < 6) anch[na] = x; na++; }
  Result R{name, g.n, 0, 0, 0, false};
  if (na != 6) { R.name += " [BAD deficiency]"; return R; }
  // branch 1: locked full vertices (parallel over v)
  vector<int> fulls;
  for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
  atomic<int> nextV(0), locked(0);
  { vector<thread> th;
    for (int i = 0; i < 32; i++) th.emplace_back([&]() {
      for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
        if (query(g, anch, fulls[i2], nullptr) == 0) locked++; } });
    for (auto& t : th) t.join(); }
  R.lockedFull = locked.load();
  // branch 2: Col table + Avoid coverage (parallel over canonical traces)
  static thread_local int dummy;
  bitset<NTAU> Col;
  mutex mu;
  vector<int> canonTau;
  for (int t = 0; t < NTAU; t++) if (canon6(t) == t) canonTau.push_back(t);
  atomic<int> nextT(0);
  { vector<thread> th;
    for (int i = 0; i < 32; i++) th.emplace_back([&]() {
      static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
      for (;;) { int i2 = nextT.fetch_add(1); if (i2 >= (int)canonTau.size()) break;
        int t0 = canonTau[i2], fix[6], tt = t0;
        for (int s = 0; s < 6; s++) { fix[s] = tt % 3; tt /= 3; }
        if (query(g, anch, -1, fix) == 1) {
          lock_guard<mutex> lk(mu);
          for (auto& p : P) { int h = 0, t = t0;
            for (int s = 0; s < 6; s++) { h += p[t % 3] * POW3[s]; t /= 3; }
            Col.set(h); } } } });
    for (auto& t : th) t.join(); }
  R.colSz = (int)Col.count();
  bitset<NTAU> av;
  for (int t = 0; t < NTAU; t++) {
    if (!Col[t]) continue;
    int ch[6][2];
    for (int s = 0; s < 6; s++) { int c = (t / POW3[s]) % 3, k = 0;
      for (int x = 0; x < 3; x++) if (x != c) ch[s][k++] = x; }
    for (int msk = 0; msk < 64; msk++) { int gg = 0;
      for (int s = 0; s < 6; s++) gg += ch[s][msk >> s & 1] * POW3[s];
      av.set(gg); }
  }
  R.avoidCov = (int)av.count();
  R.neither = (R.lockedFull == 0) && (R.avoidCov < NTAU);
  return R;
}

int main() {
  vector<Result> results;
  auto run = [&](const string& nm, BG& g) {
    if (!connectedG(g)) { printf("%s: DISCONNECTED, skip\n", nm.c_str()); return; }
    Result r = analyze(nm, g);
    results.push_back(r);
    printf("%-34s m=%2d lockedFull=%2d |Col|=%3d avoid=%3d/729 -> %s\n",
           r.name.c_str(), r.m, r.lockedFull, r.colSz, r.avoidCov,
           r.neither ? "** NEITHER (REFUTES D?) **"
                     : (r.lockedFull ? (r.avoidCov == NTAU ? "B1+B2" : "B1") : "B2"));
    fflush(stdout);
  };

  // PG(2,5) - 3e control
  {
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
    g.delEdge(0, 32); g.delEdge(7, 41); g.delEdge(15, 33);
    run("PG(2,5)-3e (control)", g);
  }
  // Q6 - 3e
  { BG g; g.n = 64;
    for (int i = 0; i < 64; i++) for (int b = 0; b < 6; b++) { int j = i ^ (1 << b); if (j > i) g.addEdge(i, j); }
    BG h = g; h.delEdge(0, 1); h.delEdge(2, 6); h.delEdge(8, 24);
    run("Q6-3e", h); }
  // circulants - 3e
  for (int m : {20, 32, 44, 56}) {
    BG g; g.n = m;
    for (int i = 0; i < m; i++) { g.addEdge(i, (i + 1) % m); g.addEdge(i, (i + 3) % m); g.addEdge(i, (i + 5) % m); }
    BG h = g; h.delEdge(0, 1); h.delEdge(7, 10); h.delEdge(14, 17);
    char nm[48]; snprintf(nm, 48, "C%d(1,3,5)-3e", m);
    run(nm, h);
  }
  // random 6-regular bipartite - 3e
  for (int k : {10, 14, 18, 22, 26, 30}) {
    for (int rep = 0; rep < 6; rep++) {
      BG g; g.n = 2 * k;
      vector<int> A, B;
      for (int i = 0; i < k; i++) { A.push_back(i); B.push_back(k + i); }
      if (!randMatchUnion(g, A, B, 6)) continue;
      if (!connectedG(g) || !minus3disjoint(g)) continue;
      char nm[48]; snprintf(nm, 48, "randBip m=%d #%d -3e", 2 * k, rep);
      run(nm, g);
    }
  }
  // random balanced tripartite 6-regular - 3e (3 parts, 3-regular between each pair)
  for (int t : {7, 10, 14, 18, 21}) {
    for (int rep = 0; rep < 4; rep++) {
      BG g; g.n = 3 * t;
      vector<int> P0, P1, P2;
      for (int i = 0; i < t; i++) { P0.push_back(i); P1.push_back(t + i); P2.push_back(2 * t + i); }
      if (!randMatchUnion(g, P0, P1, 3) || !randMatchUnion(g, P1, P2, 3) || !randMatchUnion(g, P0, P2, 3)) continue;
      if (!connectedG(g) || !minus3disjoint(g)) continue;
      char nm[48]; snprintf(nm, 48, "randTri m=%d #%d -3e", 3 * t, rep);
      run(nm, g);
    }
  }

  int nNeither = 0;
  for (auto& r : results) if (r.neither) nNeither++;
  printf("\nSWEEP DONE: %d graphs, NEITHER count = %d -> %s\n", (int)results.size(), nNeither,
         nNeither ? "(D) REFUTATION CANDIDATES FOUND — check shore axioms next"
                  : "(D) SURVIVES the sweep");
  return 0;
}
