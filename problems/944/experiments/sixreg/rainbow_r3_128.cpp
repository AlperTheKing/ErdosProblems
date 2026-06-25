// FAIR (R3) test (2026-06-12): diamond rainbow-gadget attached to the flexible
// PG(2,5) incidence bulk. m = 68 > 64 => 128-bit adjacency engine.
// Gadget {a,b,u,t,v,w}: diamond a,b,u,t (forces psi(u)=psi(t)) + u-v, v-w, t-w
// => {u,v,w} rainbow in every proper 3-colouring; no K4.
// Pads: a+3, b+3, u+2, t+3, v+3, w+3 = 17 edges into 17 distinct capacity-1 PG
// vertices (10 vertex-disjoint PG edges deleted => 20 slots; 3 leftover = stubs).
// Anchors: u, v, w (b=1) + 3 leftover PG vertices (b=1). Sum b = 6, Delta <= 6.
// Measure: Col rainbow-rigidity on (u,v,w)-stubs + lockedFull.
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

static const int MAXN = 128, NTAU = 729;
static const int POW3[7] = {1,3,9,27,81,243,729};

struct BS {
  uint64_t w[2] = {0, 0};
  void set(int i) { w[i >> 6] |= 1ull << (i & 63); }
  void clr(int i) { w[i >> 6] &= ~(1ull << (i & 63)); }
  bool test(int i) const { return w[i >> 6] >> (i & 63) & 1; }
  int count() const { return __builtin_popcountll(w[0]) + __builtin_popcountll(w[1]); }
};

struct BG {
  int n = 0;
  BS adj[MAXN];
  void addEdge(int a, int b) { adj[a].set(b); adj[b].set(a); }
  void delEdge(int a, int b) { adj[a].clr(b); adj[b].clr(a); }
  int deg(int x) const { return adj[x].count(); }
};

template <class F>
static void forNbr(const BG& g, int x, F f) {
  for (int wd = 0; wd < 2; wd++) {
    uint64_t nb = g.adj[x].w[wd];
    while (nb) { int u = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1; if (!f(u)) return; }
  }
}

static bool connectedG(const BG& g) {
  BS seen; seen.set(0); vector<int> st = {0};
  while (!st.empty()) { int x = st.back(); st.pop_back();
    forNbr(g, x, [&](int u) { if (!seen.test(u)) { seen.set(u); st.push_back(u); } return true; }); }
  return seen.count() == g.n;
}

struct Solver {
  const BG* g; int del; BS nbv;
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
      bool onN = del >= 0 && nbv.test(x);
      if (onN) {
        cnt[c]++;
        if (cnt[c] == 2) {
          for (int wd = 0; wd < 2 && ok; wd++) {
            uint64_t nb = nbv.w[wd];
            while (nb) { int v2 = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1;
              if (v2 != x && col[v2] < 0 && !shrink(v2, 1 << c)) { ok = false; break; } }
          }
        }
      }
      if (ok) {
        for (int wd = 0; wd < 2 && ok; wd++) {
          uint64_t nb = g->adj[x].w[wd];
          while (nb) { int u = 64 * wd + __builtin_ctzll(nb); nb &= nb - 1;
            if (u != del && col[u] < 0 && !shrink(u, 1 << c)) { ok = false; break; } }
        }
      }
      if (ok) { int r = solve(); if (r) return r; }
      while (trail.size() > mark) { dom[trail.back().first] = trail.back().second; trail.pop_back(); }
      if (onN) cnt[c]--;
      col[x] = -1;
    }
    return 0;
  }
};

static int query(const BG& g, const int* stubV, int del, const int* fixTrace) {
  Solver s; s.g = &g; s.del = del;
  if (del >= 0) s.nbv = g.adj[del];
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  if (fixTrace)
    for (int i = 0; i < 6; i++) {
      if (stubV[i] == del) continue;
      uint8_t bit = 1 << fixTrace[i];
      if (!(s.dom[stubV[i]] & bit)) return 0;
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

// exists proper 3-col of g minus del with col[a] = col[b] = 0 (canonical equality)
static int queryEq(const BG& g, int del, int a, int b) {
  Solver s; s.g = &g; s.del = del;
  if (del >= 0) s.nbv = BS();                    // no count condition: plain colouring
  s.cnt[0] = s.cnt[1] = s.cnt[2] = 0;
  memset(s.col, -1, sizeof(s.col));
  for (int u = 0; u < g.n; u++) s.dom[u] = 7;
  s.dom[a] = 1; s.dom[b] = 1;
  if (del >= 0) s.col[del] = 3;
  return s.solve();
}

static uint64_t RNG = 0xABCDEF9876543210ull;
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

int main(int argc, char** argv) {
  // PG(2,5) incidence on 0..61
  vector<array<int,3>> reps;
  for (int a = 0; a < 5; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 5; c++) {
    if (!a && !b && !c) continue;
    if ((a && a != 1) || (!a && b && b != 1) || (!a && !b && c != 1)) continue;
    reps.push_back({a, b, c});
  }
  if (argc > 1 && string(argv[1]) == "b2") {
    // CONSTRAINED-STUB variant (workflow-recommended decisive test): all six
    // stubs on the z-triple U,V,W (b=2 each, degree 4); A,B,T full; PARITY-rule
    // pads (gadget vertex's pads go to the bulk side whose phi0-colour differs
    // from its intended colour; intended (A,B,U,T,V,W)=(1,2,3,3,1,2), points=1,
    // lines=2; U,T colour-3 pads split evenly).
    // Pad demand: A->3 lines, B->3 points, V->2 lines, W->2 points, U->1+T->3
    // split 2 lines + 2 points. 7 deleted bulk edges = 7 point + 7 line slots.
    for (int inst = 0; inst < 6; inst++) {
      BG g; g.n = 68;
      for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
        int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
        if (dot % 5 == 0) g.addEdge(i, 31 + j);
      }
      int A = 62, B = 63, U = 64, T = 65, V = 66, W = 67;
      g.addEdge(A, B);
      g.addEdge(A, U); g.addEdge(B, U);
      g.addEdge(A, T); g.addEdge(B, T);
      g.addEdge(U, V); g.addEdge(V, W); g.addEdge(T, W);
      vector<int> capP, capL;                    // point-side / line-side capacity
      { BS used; int got = 0;
        for (int tries = 0; tries < 40000 && got < 7; tries++) {
          int x = rnd() % 31;                    // pick a point, delete one edge
          if (used.test(x)) continue;
          vector<int> cand;
          forNbr(g, x, [&](int u) { if (u >= 31 && u < 62 && !used.test(u)) cand.push_back(u); return true; });
          if (cand.empty()) continue;
          int y = cand[rnd() % cand.size()];
          BG h = g; h.delEdge(x, y);
          BS seen; seen.set(0); vector<int> st = {0};
          while (!st.empty()) { int z = st.back(); st.pop_back();
            forNbr(h, z, [&](int q) { if (q < 62 && !seen.test(q)) { seen.set(q); st.push_back(q); } return true; }); }
          int cc = 0; for (int q = 0; q < 62; q++) if (seen.test(q)) cc++;
          if (cc != 62) continue;
          g = h; used.set(x); used.set(y);
          capP.push_back(x); capL.push_back(y); got++;
        }
        if (got < 7) { printf("b2 inst %d: capacity fail\n", inst); continue; }
      }
      for (int i = 6; i > 0; i--) { int j = rnd() % (i + 1); swap(capP[i], capP[j]); }
      for (int i = 6; i > 0; i--) { int j = rnd() % (i + 1); swap(capL[i], capL[j]); }
      // pads per parity rule
      int li = 0, pi = 0;
      for (int p = 0; p < 3; p++) g.addEdge(A, capL[li++]);     // A(1) -> lines
      for (int p = 0; p < 2; p++) g.addEdge(V, capL[li++]);     // V(1) -> lines
      for (int p = 0; p < 3; p++) g.addEdge(B, capP[pi++]);     // B(2) -> points
      for (int p = 0; p < 2; p++) g.addEdge(W, capP[pi++]);     // W(2) -> points
      g.addEdge(U, capL[li++]);                                  // U(3): 1 line
      g.addEdge(T, capL[li++]); g.addEdge(T, capP[pi++]); g.addEdge(T, capP[pi++]); // T(3): 1 line + 2 points
      if (!connectedG(g)) { printf("b2 inst %d: disconnected\n", inst); continue; }
      int stubV[6] = {U, U, V, V, W, W};
      int sumb = 0, maxd = 0;
      for (int x = 0; x < g.n; x++) { sumb += 6 - g.deg(x); if (g.deg(x) > maxd) maxd = g.deg(x); }
      printf("b2 inst %d: m=%d sum_b=%d Delta=%d degU=%d degV=%d degW=%d\n",
             inst, g.n, sumb, maxd, g.deg(U), g.deg(V), g.deg(W));
      if (sumb != 6 || maxd > 6 || g.deg(U) != 4 || g.deg(V) != 4 || g.deg(W) != 4) {
        printf("b2 inst %d: INVALID profile\n", inst); continue; }
      // rainbow-rigidity check on (U,V,W) via Col: trace components 0,2,4
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
      int colSz = (int)Col.count(), nonRainbow = 0;
      for (int t = 0; t < NTAU; t++) {
        if (!Col[t]) continue;
        int cU = t % 3, cV = (t / 9) % 3, cW = (t / 81) % 3;
        if (cU == cV || cV == cW || cU == cW) nonRainbow++;
      }
      printf("b2 inst %d: |Col|=%d nonRainbow=%d -> rainbow-rigid: %s\n",
             inst, colSz, nonRainbow, nonRainbow == 0 && colSz > 0 ? "YES" : "NO");
      fflush(stdout);
      if (nonRainbow || !colSz) continue;
      vector<int> fulls;
      for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
      atomic<int> nextV(0), locked(0);
      { vector<thread> th;
        for (int i = 0; i < 64; i++) th.emplace_back([&]() {
          for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
            if (query(g, stubV, fulls[i2], nullptr) == 0) locked++; } });
        for (auto& t : th) t.join(); }
      printf("b2 inst %d: fulls=%d lockedFull=%d -> %s\n", inst, (int)fulls.size(), locked.load(),
             locked ? "FROZEN VERTICES EXIST — (R3'') with (2,2,2)-stub profile is the corrected target"
                    : "0-frozen — freezing route FULLY dead; (D-prime) must go through table tension");
      fflush(stdout);
      if (argc > 2 && string(argv[2]) == "scan") {
        // hypo-rigidity scan: x is UNBLOCKING iff K-x admits a non-rainbow trace
        // on (U,V,W) (some pair equal; canonical colour 0). Hypo-rigid <=> all x unblock.
        atomic<int> nextX(0), blocked(0);
        mutex mu3; string blockedList;
        vector<thread> th;
        for (int i = 0; i < 64; i++) th.emplace_back([&]() {
          for (;;) { int x = nextX.fetch_add(1); if (x >= g.n) break;
            if (x == U || x == V || x == W) continue;
            bool unb = queryEq(g, x, U, V) == 1 || queryEq(g, x, V, W) == 1 || queryEq(g, x, U, W) == 1;
            if (!unb) { blocked++; lock_guard<mutex> lk(mu3); blockedList += " " + to_string(x); } } });
        for (auto& t : th) t.join();
        printf("b2 inst %d HYPO-SCAN: blocked (deletion keeps rigidity) = %d / %d%s%s\n",
               inst, blocked.load(), g.n - 3, blocked ? " at:" : "", blockedList.c_str());
        printf("  -> %s\n", blocked ? "NOT hypo-rigid (cannot be a critical-graph shore)"
                                    : "HYPO-RIGID — every deletion unblocks (criticality-compatible!)");
        fflush(stdout);
      }
    }
    return 0;
  }
  if (argc > 1 && string(argv[1]) == "tri") {
    // TRIANGLE-anchored scope test: z1,z2,z3 = bare triangle (rainbow forced
    // trivially, NO equality-gadget leak), 3 pads each into PG; m = 65.
    for (int inst = 0; inst < 6; inst++) {
      BG g; g.n = 65;
      for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
        int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
        if (dot % 5 == 0) g.addEdge(i, 31 + j);
      }
      int Z1 = 62, Z2 = 63, Z3 = 64;
      g.addEdge(Z1, Z2); g.addEdge(Z2, Z3); g.addEdge(Z1, Z3);
      vector<int> capv;
      { BS used; int got = 0;
        for (int tries = 0; tries < 20000 && got < 6; tries++) {
          int x = rnd() % 62;
          if (used.test(x)) continue;
          vector<int> cand;
          forNbr(g, x, [&](int u) { if (u < 62 && !used.test(u)) cand.push_back(u); return true; });
          if (cand.empty()) continue;
          int y = cand[rnd() % cand.size()];
          BG h = g; h.delEdge(x, y);
          BS seen; seen.set(0); vector<int> st = {0};
          while (!st.empty()) { int z = st.back(); st.pop_back();
            forNbr(h, z, [&](int q) { if (q < 62 && !seen.test(q)) { seen.set(q); st.push_back(q); } return true; }); }
          int cc = 0; for (int q = 0; q < 62; q++) if (seen.test(q)) cc++;
          if (cc != 62) continue;
          g = h; used.set(x); used.set(y);
          capv.push_back(x); capv.push_back(y); got++;
        }
        if (got < 6) { printf("tri inst %d: capacity fail\n", inst); continue; }
      }
      for (int i = (int)capv.size() - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(capv[i], capv[j]); }
      for (int k = 0; k < 3; k++)
        for (int p = 0; p < 3; p++) g.addEdge(62 + k, capv[3 * k + p]);
      if (!connectedG(g)) { printf("tri inst %d: disconnected\n", inst); continue; }
      int stubV[6] = {Z1, Z2, Z3, capv[9], capv[10], capv[11]};
      int sumb = 0, maxd = 0;
      for (int x = 0; x < g.n; x++) { sumb += 6 - g.deg(x); if (g.deg(x) > maxd) maxd = g.deg(x); }
      printf("tri inst %d: m=%d sum_b=%d Delta=%d\n", inst, g.n, sumb, maxd);
      if (sumb != 6 || maxd > 6) { printf("tri inst %d: INVALID\n", inst); continue; }
      vector<int> fulls;
      for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
      atomic<int> nextV(0), locked(0);
      { vector<thread> th;
        for (int i = 0; i < 64; i++) th.emplace_back([&]() {
          for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
            if (query(g, stubV, fulls[i2], nullptr) == 0) locked++; } });
        for (auto& t : th) t.join(); }
      printf("tri inst %d: fulls=%d lockedFull=%d -> %s\n", inst, (int)fulls.size(), locked.load(),
             locked ? "(R3)-broad consistent" : "** triangle case UNFROZEN — (R3) must exclude anchor-triangles **");
      fflush(stdout);
    }
    return 0;
  }
  for (int inst = 0; inst < 12; inst++) {
    BG g; g.n = 68;
    for (int i = 0; i < 31; i++) for (int j = 0; j < 31; j++) {
      int dot = reps[i][0]*reps[j][0] + reps[i][1]*reps[j][1] + reps[i][2]*reps[j][2];
      if (dot % 5 == 0) g.addEdge(i, 31 + j);
    }
    int A = 62, B = 63, U = 64, T = 65, V = 66, W = 67;
    g.addEdge(A, B);
    g.addEdge(A, U); g.addEdge(B, U);
    g.addEdge(A, T); g.addEdge(B, T);
    g.addEdge(U, V); g.addEdge(V, W); g.addEdge(T, W);
    // 10 vertex-disjoint PG edge deletions, PG stays connected
    vector<int> capv;
    {
      BS used;
      int got = 0;
      for (int tries = 0; tries < 20000 && got < 10; tries++) {
        int x = rnd() % 62;
        if (used.test(x)) continue;
        vector<int> cand;
        forNbr(g, x, [&](int u) { if (u < 62 && !used.test(u)) cand.push_back(u); return true; });
        if (cand.empty()) continue;
        int y = cand[rnd() % cand.size()];
        BG h = g; h.delEdge(x, y);
        BS seen; seen.set(0); vector<int> st = {0};
        while (!st.empty()) { int z = st.back(); st.pop_back();
          forNbr(h, z, [&](int q) { if (q < 62 && !seen.test(q)) { seen.set(q); st.push_back(q); } return true; }); }
        int cc = 0; for (int q = 0; q < 62; q++) if (seen.test(q)) cc++;
        if (cc != 62) continue;
        g = h; used.set(x); used.set(y);
        capv.push_back(x); capv.push_back(y); got++;
      }
      if (got < 10) { printf("inst %d: capacity fail\n", inst); continue; }
    }
    // shuffle capacity vertices, then pads a+3 b+3 u+2 t+3 v+3 w+3
    for (int i = (int)capv.size() - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(capv[i], capv[j]); }
    {
      int padNeed[6] = {3, 3, 2, 3, 3, 3};       // A B U T V W
      int gvs[6] = {A, B, U, T, V, W};
      int idx = 0;
      for (int k = 0; k < 6; k++)
        for (int p = 0; p < padNeed[k]; p++) g.addEdge(gvs[k], capv[idx++]);
    }
    if (!connectedG(g)) { printf("inst %d: disconnected\n", inst); continue; }
    int stubV[6] = {U, V, W, capv[17], capv[18], capv[19]};
    int sumb = 0, maxd = 0;
    for (int x = 0; x < g.n; x++) { sumb += 6 - g.deg(x); if (g.deg(x) > maxd) maxd = g.deg(x); }
    printf("inst %d: m=%d sum_b=%d Delta=%d stubs {%d,%d,%d,%d,%d,%d}\n",
           inst, g.n, sumb, maxd, stubV[0], stubV[1], stubV[2], stubV[3], stubV[4], stubV[5]);
    if (sumb != 6 || maxd > 6) { printf("inst %d: INVALID, skip\n", inst); continue; }
    // Col + rainbow check on stubs 0,1,2
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
    int colSz = (int)Col.count(), nonRainbow = 0;
    for (int t = 0; t < NTAU; t++) {
      if (!Col[t]) continue;
      int c0 = t % 3, c1 = (t / 3) % 3, c2 = (t / 9) % 3;
      if (c0 == c1 || c1 == c2 || c0 == c2) nonRainbow++;
    }
    printf("inst %d: |Col|=%d nonRainbowTraces=%d -> rainbow-rigid: %s\n",
           inst, colSz, nonRainbow, nonRainbow == 0 && colSz > 0 ? "YES" : "NO");
    fflush(stdout);
    if (nonRainbow || !colSz) continue;
    vector<int> fulls;
    for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
    atomic<int> nextV(0), locked(0);
    mutex mu2; string lockedList;
    { vector<thread> th;
      for (int i = 0; i < 64; i++) th.emplace_back([&]() {
        for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
          if (query(g, stubV, fulls[i2], nullptr) == 0) { locked++;
            lock_guard<mutex> lk(mu2); lockedList += " " + to_string(fulls[i2]); } } });
      for (auto& t : th) t.join(); }
    printf("inst %d: fulls=%d lockedFull=%d%s%s -> %s\n", inst, (int)fulls.size(), locked.load(),
           locked ? " at:" : "", lockedList.c_str(),
           locked ? "(R3)-consistent (note WHERE: gadget=62..67, pads)"
                  : "** (R3) REFUTED — rainbow-rigid yet everywhere-unfrozen **");
    fflush(stdout);
  }
  return 0;
}

