// Conjecture (D) sweep v2: STACKED deficiency profiles (2026-06-12 evening).
// v1 only sampled spread deficiency (six b=1 anchors). Hand analysis found that
// branch 2 (Avoid-completeness) can FAIL for stacked bipartite shores:
//   three b=2 anchors x1,x2,x3 on one side with banned lists {1,2},{0,2},{0,1}
//   force colours 0,1,2; a common neighbour w is then uncolourable => that gamma
//   is unavoidable. (D) then requires such shores to be branch 1 (frozen).
// This sweep tests stacked profiles + the crafted blocker instance.
// Stubs: vertex x carries 6-deg(x) stubs; trace tau in [3]^6 indexed by stubs,
// same-vertex stubs share the anchor colour (traces violating that are skipped).
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
#include <algorithm>
using namespace std;

static const int MAXN = 64, NTAU = 729;
static const int POW3[7] = {1,3,9,27,81,243,729};

struct BG {
  int n = 0;
  uint64_t adj[MAXN] = {};
  void addEdge(int a, int b) { adj[a] |= 1ull << b; adj[b] |= 1ull << a; }
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
  int solve() {
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

// stubV[6] = stub -> vertex (with multiplicity). fixTrace: per-stub colour or null.
static int query(const BG& g, const int* stubV, int del, const int* fixTrace) {
  Solver s; s.g = &g; s.del = del; s.nbv = del >= 0 ? g.adj[del] : 0;
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  if (fixTrace)
    for (int i = 0; i < 6; i++) {
      if (stubV[i] == del) continue;
      uint8_t bit = 1 << fixTrace[i];
      if (!(s.dom[stubV[i]] & bit)) return 0;     // same-vertex stub colour conflict
      s.dom[stubV[i]] = bit;
    }
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

static uint64_t RNG = 0xC0FFEE123456789ull;
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

// bipartite graph from degree sequences: Havel-Hakimi build + edge-swap MCMC
static bool bipFromDegrees(BG& g, const vector<int>& degP, const vector<int>& degQ) {
  int kP = (int)degP.size(), kQ = (int)degQ.size();
  for (int attempt = 0; attempt < 40; attempt++) {
    g = BG(); g.n = kP + kQ;
    vector<pair<int,int>> rem;                   // (remaining degree, Q index)
    vector<int> remP = degP, remQ = degQ;
    bool ok = true;
    for (int step = 0; step < kP && ok; step++) {
      int i = -1;
      for (int x = 0; x < kP; x++) if (remP[x] > 0 && (i < 0 || remP[x] > remP[i])) i = x;
      if (i < 0) break;
      rem.clear();
      for (int j = 0; j < kQ; j++) if (remQ[j] > 0 && !(g.adj[i] >> (kP + j) & 1)) rem.push_back({remQ[j], j});
      if ((int)rem.size() < remP[i]) { ok = false; break; }
      sort(rem.begin(), rem.end(), [](auto& a, auto& b) { return a.first > b.first; });
      int need = remP[i];
      for (int t = 0; t < need; t++) { int j = rem[t].second;
        g.addEdge(i, kP + j); remQ[j]--; }
      remP[i] = 0;
    }
    if (!ok) return false;                       // degree sequence infeasible
    // randomize with double-edge swaps
    vector<pair<int,int>> edges;
    for (int i = 0; i < kP; i++) { uint64_t nb = g.adj[i];
      while (nb) { int j = __builtin_ctzll(nb); nb &= nb - 1; edges.push_back({i, j}); } }
    for (int s = 0; s < 8000; s++) {
      int e1 = rnd() % edges.size(), e2 = rnd() % edges.size();
      auto [a, b] = edges[e1]; auto [c, d] = edges[e2];
      if (a == c || b == d) continue;
      if ((g.adj[a] >> d & 1) || (g.adj[c] >> b & 1)) continue;
      g.adj[a] &= ~(1ull << b); g.adj[b] &= ~(1ull << a);
      g.adj[c] &= ~(1ull << d); g.adj[d] &= ~(1ull << c);
      g.addEdge(a, d); g.addEdge(c, b);
      edges[e1] = {a, d}; edges[e2] = {c, b};
    }
    if (connectedG(g)) return true;
  }
  return false;
}

struct Result { string name; int m, lockedFull, colSz, avoidCov; bool neither; };

static Result analyze(const string& name, const BG& g) {
  int stubV[6], ns = 0;
  for (int x = 0; x < g.n; x++) for (int d = g.deg(x); d < 6; d++) { if (ns < 6) stubV[ns] = x; ns++; }
  Result R{name, g.n, 0, 0, 0, false};
  if (ns != 6) { R.name += " [BAD deficiency]"; return R; }
  vector<int> fulls;
  for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
  atomic<int> nextV(0), locked(0);
  { vector<thread> th;
    for (int i = 0; i < 64; i++) th.emplace_back([&]() {
      for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
        if (query(g, stubV, fulls[i2], nullptr) == 0) locked++; } });
    for (auto& t : th) t.join(); }
  R.lockedFull = locked.load();
  bitset<NTAU> Col;
  mutex mu;
  vector<int> canonTau;
  for (int t = 0; t < NTAU; t++) if (canon6(t) == t) canonTau.push_back(t);
  atomic<int> nextT(0);
  { vector<thread> th;
    for (int i = 0; i < 64; i++) th.emplace_back([&]() {
      static const int P[6][3] = {{0,1,2},{0,2,1},{1,0,2},{1,2,0},{2,0,1},{2,1,0}};
      for (;;) { int i2 = nextT.fetch_add(1); if (i2 >= (int)canonTau.size()) break;
        int t0 = canonTau[i2], fix[6], tt = t0;
        for (int s = 0; s < 6; s++) { fix[s] = tt % 3; tt /= 3; }
        if (query(g, stubV, -1, fix) == 1) {
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

int main(int argc, char** argv) {
  vector<Result> results;
  auto run = [&](const string& nm, BG& g) {
    Result r = analyze(nm, g);
    results.push_back(r);
    printf("%-36s m=%2d lockedFull=%2d |Col|=%3d avoid=%3d/729 -> %s\n",
           r.name.c_str(), r.m, r.lockedFull, r.colSz, r.avoidCov,
           r.neither ? "** NEITHER (REFUTES D?) **"
                     : (r.lockedFull ? (r.avoidCov == NTAU ? "B1+B2" : "B1") : "B2"));
    fflush(stdout);
  };

  if (argc > 1 && string(argv[1]) == "pg") {
    // decisive flexible-stacked instances: PG(2,5) minus star-3 / minus P4-path
    vector<array<int,3>> reps;
    for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
      if (!a && !b && !c) continue;
      if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
      reps.push_back({a, b, c});
    }
    auto buildPG = [&](BG& g) {
      g = BG(); g.n = 62;
      for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
        int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
        if (dot % 5 == 0) g.addEdge(i, 31 + j);
      }
    };
    { BG g; buildPG(g);                            // star-3 at vertex 0: profile (3,1,1,1)
      uint64_t nb = g.adj[0]; int k = 0;
      while (nb && k < 3) { int u = __builtin_ctzll(nb); nb &= nb - 1;
        g.adj[0] &= ~(1ull << u); g.adj[u] &= ~(1ull << 0); k++; }
      printf("PG-star3: conn=%d\n", connectedG(g));
      run("PG(2,5)-star3 (3,1,1,1)", g); }
    { BG g; buildPG(g);                            // P4 path: edges (a,y),(y,c): profile (2,2,1,1)? -> (1,2,1) +1 edge
      int y = 32;                                  // a line vertex
      uint64_t nb = g.adj[y]; int a = __builtin_ctzll(nb); nb &= nb - 1; int c = __builtin_ctzll(nb);
      g.adj[y] &= ~(1ull << a); g.adj[a] &= ~(1ull << y);
      g.adj[y] &= ~(1ull << c); g.adj[c] &= ~(1ull << y);
      // one more disjoint edge far away: (30, x) with x a full neighbour
      uint64_t nb2 = g.adj[30]; int d = -1;
      while (nb2) { int u = __builtin_ctzll(nb2); nb2 &= nb2 - 1;
        if (u != y && u != a && u != c && g.deg(u) == 6) { d = u; break; } }
      g.adj[30] &= ~(1ull << d); g.adj[d] &= ~(1ull << 30);
      printf("PG-P3+e: conn=%d (y=%d a=%d c=%d, extra (30,%d))\n", connectedG(g), y, a, c, d);
      run("PG(2,5)-P3+e (2,1,1,1,1)", g); }
    int nN = 0;
    for (auto& r : results) if (r.neither) nN++;
    printf("\nPG-STACKED DONE: NEITHER = %d -> %s\n", nN,
           nN ? "(D)-as-stated REFUTED (pairing-level (D') becomes the target)" : "(D) holds even here");
    return 0;
  }
  // CRAFTED BLOCKER: three b=2 P-vertices x1,x2,x3 + common Q-neighbour w.
  // P = {0..t}, Q = {t+1 .. t+t'}; degrees: x_i = 4, rest 6.
  for (int rep = 0; rep < 10; rep++) {
    int kP = 11, kQ = 10;                        // P-side deficiency 6: 6*11-6 = 60 = 6*10
    vector<int> degP(kP, 6); degP[0] = degP[1] = degP[2] = 4;
    vector<int> degQ(kQ, 6);
    BG g;
    if (!bipFromDegrees(g, degP, degQ)) { printf("crafted #%d: build fail\n", rep); continue; }
    // force w = kP (first Q vertex) adjacent to x0,x1,x2: rewire if needed
    int w = kP;
    bool ok = true;
    for (int xi = 0; xi < 3 && ok; xi++) {
      if (g.adj[xi] >> w & 1) continue;
      // find y in N(xi)\{w}, u in N(w)\{xi} with u not~y... swap edges (xi,y),(w... ) -> (xi,w),(u,y)
      ok = false;
      uint64_t ny = g.adj[xi];
      while (ny && !ok) { int y = __builtin_ctzll(ny); ny &= ny - 1;
        uint64_t nu = g.adj[w];
        while (nu) { int u = __builtin_ctzll(nu); nu &= nu - 1;
          if (u == xi || (g.adj[u] >> y & 1)) continue;
          g.adj[xi] &= ~(1ull << y); g.adj[y] &= ~(1ull << xi);
          g.adj[w] &= ~(1ull << u); g.adj[u] &= ~(1ull << w);
          g.addEdge(xi, w); g.addEdge(u, y);
          ok = true; break; }
      }
    }
    if (!ok || !connectedG(g)) { printf("crafted #%d: rewire fail\n", rep); continue; }
    char nm[64]; snprintf(nm, 64, "CRAFTED 3x(b=2)+commonNbr #%d", rep);
    run(nm, g);
  }
  // random stacked profiles (deficiency all on P side unless noted)
  struct Prof { const char* nm; vector<int> defP, defQ; };
  vector<Prof> profs = {
    {"(2,2,2)P",   {2,2,2},     {}},
    {"(2,2,1,1)P", {2,2,1,1},   {}},
    {"(3,1,1,1)P", {3,1,1,1},   {}},
    {"(3,3)P",     {3,3},       {}},
    {"(2,2)P(1,1)Q",{2,2},      {1,1}},
    {"(3)P(3)Q",   {3},         {3}},
    {"(2,1)P(2,1)Q",{2,1},      {2,1}},
  };
  for (auto& pr : profs) {
    int dP = 0, dQ = 0;
    for (int d : pr.defP) dP += d;
    for (int d : pr.defQ) dQ += d;
    for (int tQ : {10, 16}) {
      for (int rep = 0; rep < 12; rep++) {
        // sizes: 6*kP - dP = 6*kQ - dQ  =>  kP = kQ + (dP-dQ)/6
        if ((dP - dQ) % 6) continue;
        int kQ2 = tQ, kP2 = kQ2 + (dP - dQ) / 6;
        vector<int> degP(kP2, 6), degQ(kQ2, 6);
        for (size_t i = 0; i < pr.defP.size(); i++) degP[i] = 6 - pr.defP[i];
        for (size_t j = 0; j < pr.defQ.size(); j++) degQ[j] = 6 - pr.defQ[j];
        BG g;
        if (!bipFromDegrees(g, degP, degQ)) continue;
        char nm[64]; snprintf(nm, 64, "%s m=%d #%d", pr.nm, kP2 + kQ2, rep);
        run(nm, g);
      }
    }
  }
  int nNeither = 0;
  for (auto& r : results) if (r.neither) nNeither++;
  printf("\nSWEEP2 DONE: %d graphs, NEITHER = %d -> %s\n", (int)results.size(), nNeither,
         nNeither ? "(D) REFUTED in the stacked class — keystone needs repair"
                  : "(D) survives stacked profiles too");
  return 0;
}

