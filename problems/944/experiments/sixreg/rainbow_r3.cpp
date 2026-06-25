// (R3) falsify-first (2026-06-12 evening).
// (R3): a deficiency-6 shore whose EVERY proper 3-colouring is rainbow on 3
// prescribed stub-anchors has a frozen full vertex.
// Construction: triangle-free-rainbow... rather K4-FREE rainbow forcing:
//   diamond D = {a,b,u,t} (a~b, u,t ~ both a,b; u,t nonadjacent) forces
//   psi(u)=psi(t) in every proper 3-colouring; edges u-v, v-w, t-w then force
//   {u,v,w} rainbow. Anchors: u,v,w (b=1 each) + 3 bulk vertices (b=1).
//   Bulk = random 6-regular bipartite (12+12), 9 vertex-disjoint edges removed
//   => 18 capacity-1 vertices: 15 receive gadget pads (distinct => no K4),
//   3 keep stubs. Total m = 30, Sum b = 6, Delta <= 6, connected.
// Measured per instance: (i) machine check that ALL Col traces are rainbow on
// the (u,v,w) stubs; (ii) lockedFull. lockedFull==0 => (R3) REFUTED.
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

static int query(const BG& g, const int* stubV, int del, const int* fixTrace) {
  Solver s; s.g = &g; s.del = del; s.nbv = del >= 0 ? g.adj[del] : 0;
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

static uint64_t RNG = 0xDEADBEEFCAFE1234ull;
static uint64_t rnd() { RNG ^= RNG << 13; RNG ^= RNG >> 7; RNG ^= RNG << 17; return RNG; }

static bool rand6regBip(BG& g, int k, int base) {  // vertices base..base+2k-1
  for (int rep = 0; rep < 6; rep++) {
    for (int tries = 0;; tries++) {
      if (tries > 3000) return false;
      vector<int> perm(k); for (int i = 0; i < k; i++) perm[i] = i;
      for (int i = k - 1; i > 0; i--) { int j = rnd() % (i + 1); swap(perm[i], perm[j]); }
      bool ok = true;
      for (int i = 0; i < k; i++) if (g.adj[base + i] >> (base + k + perm[i]) & 1) { ok = false; break; }
      if (!ok) continue;
      for (int i = 0; i < k; i++) g.addEdge(base + i, base + k + perm[i]);
      break;
    }
  }
  return true;
}

int main() {
  // gadget vertices 0..5: a=0 b=1 u=2 t=3 v=4 w=5; bulk 6..37 (16+16 bipartite)
  for (int inst = 0; inst < 5; inst++) {
    BG g; g.n = 38;
    int A = 0, B = 1, U = 2, T = 3, V = 4, W = 5;
    g.addEdge(A, B);
    g.addEdge(A, U); g.addEdge(B, U);
    g.addEdge(A, T); g.addEdge(B, T);
    g.addEdge(U, V); g.addEdge(V, W); g.addEdge(T, W);
    if (!rand6regBip(g, 16, 6)) { printf("inst %d: bulk fail\n", inst); continue; }
    // remove 10 vertex-disjoint bulk edges -> 20 distinct capacity-1 vertices
    vector<int> capv;
    {
      uint64_t used = 0;
      int got = 0;
      for (int tries = 0; tries < 5000 && got < 10; tries++) {
        int x = 6 + rnd() % 32;
        if (used >> x & 1) continue;
        uint64_t nb = g.adj[x] & ~used;
        nb &= ~63ull;                            // bulk-bulk edges only
        if (!nb) continue;
        int cnt = __builtin_popcountll(nb), pick = rnd() % cnt, y = -1;
        while (pick-- >= 0) { y = __builtin_ctzll(nb); nb &= nb - 1; }
        BG h = g; h.delEdge(x, y);
        // bulk-only connectivity (gadget attaches later via pads)
        uint64_t seen = 1ull << 6; vector<int> st = {6};
        while (!st.empty()) { int z = st.back(); st.pop_back();
          uint64_t nb2 = h.adj[z] & ~seen & ~63ull;
          while (nb2) { int q = __builtin_ctzll(nb2); nb2 &= nb2 - 1; seen |= 1ull << q; st.push_back(q); } }
        if (__builtin_popcountll(seen) != 32) continue;
        g = h; used |= (1ull << x) | (1ull << y);
        capv.push_back(x); capv.push_back(y); got++;
      }
      if (got < 10) { printf("inst %d: capacity fail\n", inst); continue; }
    }
    // pads: a+3, b+3, u+2, t+3, v+3, w+3 = 17 distinct capacity vertices; 3 left = stubs
    {
      int padNeed[6] = {3, 3, 2, 3, 3, 3};       // A B U T V W
      int idx = 0; bool ok = true;
      for (int gv = 0; gv < 6 && ok; gv++)
        for (int p = 0; p < padNeed[gv]; p++) {
          if (idx >= (int)capv.size()) { ok = false; break; }
          if (g.adj[gv] >> capv[idx] & 1) { ok = false; break; }   // avoid doubled pad
          g.addEdge(gv, capv[idx]); idx++;
        }
      if (!ok) { printf("inst %d: pad fail\n", inst); continue; }
    }
    if (!connectedG(g)) { printf("inst %d: disconnected\n", inst); continue; }
    // stub map: stubs 0,1,2 at U,V,W; stubs 3,4,5 at the 3 leftover capacity vertices
    int stubV[6] = {U, V, W, 0, 0, 0};
    { int k = 3;
      for (int x = 6; x < 38 && k < 6; x++) if (g.deg(x) == 5) {
        bool isPad = false;
        // capacity vertices used as pads are now degree 6; leftover are degree 5
        stubV[k++] = x;
      }
      if (k != 6) { printf("inst %d: stub count fail\n", inst); continue; }
    }
    int sumb = 0; for (int x = 0; x < g.n; x++) sumb += 6 - g.deg(x);
    int maxd = 0; for (int x = 0; x < g.n; x++) if (g.deg(x) > maxd) maxd = g.deg(x);
    printf("inst %d: m=%d sum_b=%d Delta=%d conn=1 stubs at {%d,%d,%d,%d,%d,%d}\n",
           inst, g.n, sumb, maxd, stubV[0], stubV[1], stubV[2], stubV[3], stubV[4], stubV[5]);
    if (sumb != 6 || maxd > 6) { printf("inst %d: INVALID shore, skip\n", inst); continue; }
    // Col + rainbow check on stubs 0,1,2 (= u,v,w)
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
    if (nonRainbow || !colSz) continue;
    // lockedFull
    vector<int> fulls;
    for (int x = 0; x < g.n; x++) if (g.deg(x) == 6) fulls.push_back(x);
    atomic<int> nextV(0), locked(0);
    mutex mu2; string lockedList;
    { vector<thread> th;
      for (int i = 0; i < 32; i++) th.emplace_back([&]() {
        for (;;) { int i2 = nextV.fetch_add(1); if (i2 >= (int)fulls.size()) break;
          if (query(g, stubV, fulls[i2], nullptr) == 0) { locked++;
            lock_guard<mutex> lk(mu2); lockedList += " " + to_string(fulls[i2]); } } });
      for (auto& t : th) t.join(); }
    printf("inst %d: lockedFull=%d%s%s -> %s\n", inst, locked.load(),
           locked ? " at:" : "", lockedList.c_str(),
           locked ? "(R3)-consistent" : "** (R3) REFUTED — rainbow-rigid yet unfrozen **");
    fflush(stdout);
  }
  return 0;
}
