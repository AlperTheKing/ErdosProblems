// Adversarial hill-climb against (FK) in the all-singleton shape: minimize the
// number of FROZEN full vertices of H = C + v over the candidate space
// (C: connected bipartite (q,q), Delta<=6, 6q-6 edges, deficiency 1^6 per side;
// apex v -> 4 deficient A + 2 deficient B). Objective 0 = (FK) COUNTEREXAMPLE.
// Moves: double-edge swaps in C (degree/bipartite-preserving, connectivity
// rechecked) + apex re-choice. Strict descent with plateau moves, random
// restarts on stagnation. Independent climbers per thread, shared global best.
// usage: g3_hillclimb.exe q seconds seed [threads]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <vector>
#include <algorithm>
#include <random>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>
using namespace std;

static const int MAXV = 32;

struct G {
  int n;
  uint32_t adj[MAXV];
  void add(int u, int v) { adj[u] |= 1u << v; adj[v] |= 1u << u; }
  void del(int u, int v) { adj[u] &= ~(1u << v); adj[v] &= ~(1u << u); }
  bool has(int u, int v) const { return (adj[u] >> v) & 1; }
  int deg(int u) const { return __builtin_popcount(adj[u]); }
};

static bool connectedG(const G& g) {
  uint32_t seen = 1, stack = 1;
  while (stack) {
    int x = __builtin_ctz(stack); stack &= stack - 1;
    uint32_t nb = g.adj[x] & ~seen;
    seen |= nb; stack |= nb;
  }
  return seen == ((g.n >= 32) ? 0xFFFFFFFFu : (1u << g.n) - 1);
}

static int unfrozenCapped(const G& g, int v, long long cap) {
  int N = g.n;
  int idx[MAXV], m = 0;
  uint32_t nbv = g.adj[v];
  while (nbv) { int u = __builtin_ctz(nbv); nbv &= nbv - 1; idx[m++] = u; }
  int nN = m;
  for (int u = 0; u < N; u++) if (u != v && !((g.adj[v] >> u) & 1)) idx[m++] = u;
  for (int i = nN + 1; i < m; i++) { int k = idx[i], j = i - 1;
    while (j >= nN && g.deg(idx[j]) < g.deg(k)) { idx[j+1] = idx[j]; j--; } idx[j+1] = k; }
  int8_t color[MAXV]; memset(color, -1, sizeof(color));
  int cnt[3] = {0, 0, 0};
  int pos = 0; int8_t tryc[MAXV]; memset(tryc, 0, sizeof(tryc));
  long long nodes = 0;
  while (pos >= 0) {
    if (++nodes > cap) return -1;
    if (pos == m) return 1;
    int x = idx[pos]; bool adv = false;
    int cmax = (pos == 0) ? 1 : 3;
    for (int c = tryc[pos]; c < cmax; c++) {
      if (pos < nN && cnt[c] >= 2) continue;
      bool ok = true; uint32_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctz(nb); nb &= nb - 1;
        if (u == v) continue;
        if (color[u] == c) { ok = false; break; } }
      if (ok) { color[x] = c; if (pos < nN) cnt[c]++;
        tryc[pos] = c + 1; pos++; if (pos < m) tryc[pos] = 0; adv = true; break; }
    }
    if (!adv) { color[x] = -1; tryc[pos] = 0; pos--;
      if (pos >= 0) { int y = idx[pos]; if (pos < nN) cnt[color[y]]--; color[y] = -1; } }
  }
  return 0;
}

static string g6encode(const G& g) {
  string s(1, (char)(g.n + 63));
  int bit = 0; int cur = 0;
  for (int j = 1; j < g.n; j++) for (int i = 0; i < j; i++) {
    cur = (cur << 1) | (g.has(i, j) ? 1 : 0);
    if (++bit % 6 == 0) { s += (char)(cur + 63); cur = 0; }
  }
  if (bit % 6) { cur <<= (6 - bit % 6); s += (char)(cur + 63); }
  return s;
}

int main(int argc, char** argv) {
  int q = argc > 1 ? atoi(argv[1]) : 15;
  int seconds = argc > 2 ? atoi(argv[2]) : 120;
  uint64_t seed = argc > 3 ? strtoull(argv[3], nullptr, 10) : 944;
  int nthreads = argc > 4 ? atoi(argv[4]) : 32;
  const long long CAP = 100000000LL;
  atomic<int> globalBest(1000);
  atomic<long long> totalMoves(0), restarts(0);
  atomic<bool> found(false);
  mutex outMtx;
  auto deadline = chrono::steady_clock::now() + chrono::seconds(seconds);
  auto worker = [&](int tid) {
    mt19937_64 rng(seed * 31337ULL + tid);
    while (chrono::steady_clock::now() < deadline && !found.load()) {
      // ---- fresh start
      G c; c.n = 2 * q;
      memset(c.adj, 0, sizeof(c.adj));
      for (int a = 0; a < q; a++)
        for (int j = 0; j < 6; j++) c.add(a, q + (a + j) % q);
      int perm[64];
      for (int x = 0; x < q; x++) perm[x] = x;
      for (int x = q - 1; x > 0; x--) { int y = rng() % (x + 1); swap(perm[x], perm[y]); }
      int defA[6], defB[6];
      for (int t = 0; t < 6; t++) { int a = perm[t]; c.del(a, q + a); defA[t] = a; defB[t] = q + a; }
      long long sw = 60LL * (6 * q - 6);
      for (long long s = 0; s < sw; s++) {
        int a1 = rng() % q, a2 = rng() % q;
        if (a1 == a2) continue;
        uint32_t n1 = c.adj[a1], n2 = c.adj[a2];
        if (!n1 || !n2) continue;
        int k1 = rng() % __builtin_popcount(n1), k2 = rng() % __builtin_popcount(n2);
        uint32_t t1 = n1, t2 = n2;
        while (k1--) t1 &= t1 - 1;
        int b1 = __builtin_ctz(t1);
        while (k2--) t2 &= t2 - 1;
        int b2 = __builtin_ctz(t2);
        if (b1 == b2 || c.has(a1, b2) || c.has(a2, b1)) continue;
        c.del(a1, b1); c.del(a2, b2); c.add(a1, b2); c.add(a2, b1);
      }
      if (!connectedG(c)) continue;
      restarts++;
      int selA = 0xF, selB = 0x3;            // bitmask over defA/defB indices (4 of 6, 2 of 6)
      auto buildH = [&](const G& cc, int sa, int sb, G& h) {
        h = cc; h.n = 2 * q + 1;
        int v = 2 * q;
        h.adj[v] = 0;
        for (int t = 0; t < 6; t++) { if ((sa >> t) & 1) h.add(v, defA[t]); if ((sb >> t) & 1) h.add(v, defB[t]); }
      };
      auto objective = [&](const G& cc, int sa, int sb) -> int {
        G h; buildH(cc, sa, sb, h);
        int fr = 0;
        for (int x = 0; x <= 2 * q; x++) {
          if (h.deg(x) != 6) continue;
          int r = unfrozenCapped(h, x, CAP);
          if (r != 1) fr++;                  // capped counts as frozen (conservative for descent)
        }
        return fr;
      };
      int cur = objective(c, selA, selB);
      int stale = 0;
      const int STALE_LIMIT = 4000;
      while (chrono::steady_clock::now() < deadline && !found.load() && stale < STALE_LIMIT) {
        totalMoves++;
        // move: 85% edge swap, 15% apex re-choice
        if (rng() % 100 < 85) {
          int a1 = rng() % q, a2 = rng() % q;
          if (a1 == a2) { stale++; continue; }
          uint32_t n1 = c.adj[a1], n2 = c.adj[a2];
          if (!n1 || !n2) { stale++; continue; }
          int k1 = rng() % __builtin_popcount(n1), k2 = rng() % __builtin_popcount(n2);
          uint32_t t1 = n1, t2 = n2;
          while (k1--) t1 &= t1 - 1;
          int b1 = __builtin_ctz(t1);
          while (k2--) t2 &= t2 - 1;
          int b2 = __builtin_ctz(t2);
          if (b1 == b2 || c.has(a1, b2) || c.has(a2, b1)) { stale++; continue; }
          c.del(a1, b1); c.del(a2, b2); c.add(a1, b2); c.add(a2, b1);
          if (!connectedG(c)) { c.del(a1, b2); c.del(a2, b1); c.add(a1, b1); c.add(a2, b2); stale++; continue; }
          int nv = objective(c, selA, selB);
          if (nv <= cur) { if (nv < cur) stale = 0; else stale++; cur = nv; }
          else { c.del(a1, b2); c.del(a2, b1); c.add(a1, b1); c.add(a2, b2); stale++; }
        } else {
          // apex re-choice: random 4-of-6 and 2-of-6 masks
          int sa = 0, sb = 0;
          while (__builtin_popcount(sa) != 4) sa = rng() % 64;
          while (__builtin_popcount(sb) != 2) sb = rng() % 64;
          int nv = objective(c, sa, sb);
          if (nv <= cur) { if (nv < cur) stale = 0; else stale++; cur = nv; selA = sa; selB = sb; }
          else stale++;
        }
        int gb = globalBest.load();
        while (cur < gb && !globalBest.compare_exchange_weak(gb, cur)) {}
        if (cur < gb || (cur <= 2 && cur < 1000)) {
          if (cur <= 2) {
            G h; buildH(c, selA, selB, h);
            lock_guard<mutex> lk(outMtx);
            printf("LOW frozen=%d q=%d g6=%s\n", cur, q, g6encode(h).c_str());
            fflush(stdout);
          }
        }
        if (cur == 0) {
          found = true;
          G h; buildH(c, selA, selB, h);
          lock_guard<mutex> lk(outMtx);
          printf("COUNTEREXAMPLE_ALL_UNFROZEN q=%d g6=%s\n", q, g6encode(h).c_str());
          fflush(stdout);
        }
      }
    }
  };
  vector<thread> th;
  for (int t = 0; t < nthreads; t++) th.emplace_back(worker, t);
  for (auto& t : th) t.join();
  printf("q=%d time=%ds moves=%lld restarts=%lld GLOBAL_MIN_FROZEN=%d found0=%d\n",
         q, seconds, totalMoves.load(), restarts.load(), globalBest.load(), found.load() ? 1 : 0);
  return 0;
}
