// 64-bit port of g3_random.cpp + g3_hillclimb.cpp for the deep-sparse regime
// (q up to 30, |V| = 2q+1 up to 61). Same construction and tests, validated
// against the 32-bit tools at q<=15.
//   sample mode: g3_sparse64.exe sample q samples seed [threads] [swapsFactor]
//                (negative swapsFactor => general deficiency patterns)
//   hill mode:   g3_sparse64.exe hill q seconds seed [threads]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <thread>
#include <atomic>
#include <mutex>
#include <chrono>
using namespace std;

static const int MAXV = 64;

struct G {
  int n;
  uint64_t adj[MAXV];
  void add(int u, int v) { adj[u] |= 1ull << v; adj[v] |= 1ull << u; }
  void del(int u, int v) { adj[u] &= ~(1ull << v); adj[v] &= ~(1ull << u); }
  bool has(int u, int v) const { return (adj[u] >> v) & 1; }
  int deg(int u) const { return __builtin_popcountll(adj[u]); }
};

static bool connectedG(const G& g) {
  uint64_t seen = 1, stack = 1;
  uint64_t full = (g.n >= 64) ? ~0ull : ((1ull << g.n) - 1);
  while (stack) {
    int x = __builtin_ctzll(stack); stack &= stack - 1;
    uint64_t nb = g.adj[x] & ~seen;
    seen |= nb; stack |= nb;
  }
  return seen == full;
}

// 1 = unfrozen (witness found), 0 = frozen (exhausted), -1 = node cap.
static int unfrozenCapped(const G& g, int v, long long cap) {
  int N = g.n;
  int idx[MAXV], m = 0;
  uint64_t nbv = g.adj[v];
  while (nbv) { int u = __builtin_ctzll(nbv); nbv &= nbv - 1; idx[m++] = u; }
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
      bool ok = true; uint64_t nb = g.adj[x];
      while (nb) { int u = __builtin_ctzll(nb); nb &= nb - 1;
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

// build random cross-graph C; returns false if rejected. defA/defB = deficient lists.
template <class RNG>
static bool buildCross(int q, RNG& rng, bool generalMode, long long swaps,
                       G& c, vector<int>& defA, vector<int>& defB) {
  c.n = 2 * q;
  memset(c.adj, 0, sizeof(c.adj));
  for (int a = 0; a < q; a++)
    for (int j = 0; j < 6; j++) c.add(a, q + (a + j) % q);
  defA.clear(); defB.clear();
  if (!generalMode) {
    int perm[64];
    for (int x = 0; x < q; x++) perm[x] = x;
    for (int x = q - 1; x > 0; x--) { int y = rng() % (x + 1); swap(perm[x], perm[y]); }
    for (int t = 0; t < 6; t++) { int a = perm[t]; c.del(a, q + a); defA.push_back(a); defB.push_back(q + a); }
  } else {
    for (int t = 0; t < 6; t++) {
      for (;;) {
        int a = rng() % q;
        uint64_t na = c.adj[a];
        if (!na) continue;
        int k = rng() % __builtin_popcountll(na);
        uint64_t tt = na;
        while (k--) tt &= tt - 1;
        c.del(a, __builtin_ctzll(tt));
        break;
      }
    }
    for (int x = 0; x < q; x++) if (c.deg(x) < 6) defA.push_back(x);
    for (int x = q; x < 2 * q; x++) if (c.deg(x) < 6) defB.push_back(x);
    if ((int)defA.size() < 4 || (int)defB.size() < 2) return false;
  }
  for (long long s = 0; s < swaps; s++) {
    int a1 = rng() % q, a2 = rng() % q;
    if (a1 == a2) continue;
    uint64_t n1 = c.adj[a1], n2 = c.adj[a2];
    if (!n1 || !n2) continue;
    int k1 = rng() % __builtin_popcountll(n1), k2 = rng() % __builtin_popcountll(n2);
    uint64_t t1 = n1, t2 = n2;
    while (k1--) t1 &= t1 - 1;
    int b1 = __builtin_ctzll(t1);
    while (k2--) t2 &= t2 - 1;
    int b2 = __builtin_ctzll(t2);
    if (b1 == b2 || c.has(a1, b2) || c.has(a2, b1)) continue;
    c.del(a1, b1); c.del(a2, b2); c.add(a1, b2); c.add(a2, b1);
  }
  return connectedG(c);
}

int main(int argc, char** argv) {
  if (argc < 3) { fprintf(stderr, "usage: g3_sparse64 sample|hill q ...\n"); return 1; }
  string mode = argv[1];
  int q = atoi(argv[2]);
  const long long CAP = 500000000LL;
  if (mode == "sample") {
    long long samples = argc > 3 ? atoll(argv[3]) : 10000;
    uint64_t seed = argc > 4 ? strtoull(argv[4], nullptr, 10) : 944;
    int nthreads = argc > 5 ? atoi(argv[5]) : 32;
    int swapsFactor = argc > 6 ? atoi(argv[6]) : 60;
    bool general = swapsFactor < 0;
    long long swaps = (long long)(general ? -swapsFactor : swapsFactor) * (6 * q - 6);
    atomic<long long> done(0), frozenG(0), capped(0), rejected(0), candidates(0);
    mutex outMtx;
    auto worker = [&](int tid) {
      mt19937_64 rng(seed * 1000003ULL + tid);
      for (;;) {
        long long i = done.fetch_add(1);
        if (i >= samples) break;
        G c; vector<int> defA, defB;
        if (!buildCross(q, rng, general, swaps, c, defA, defB)) { rejected++; continue; }
        for (int x = (int)defA.size() - 1; x > 0; x--) { int y = rng() % (x + 1); swap(defA[x], defA[y]); }
        for (int x = (int)defB.size() - 1; x > 0; x--) { int y = rng() % (x + 1); swap(defB[x], defB[y]); }
        G h = c; h.n = 2 * q + 1;
        int v = 2 * q;
        h.adj[v] = 0;
        for (int t = 0; t < 4; t++) h.add(v, defA[t]);
        for (int t = 0; t < 2; t++) h.add(v, defB[t]);
        int frozenCnt = 0; bool wasCapped = false;
        for (int x = 0; x <= 2 * q; x++) {
          if (h.deg(x) != 6) continue;
          int r = unfrozenCapped(h, x, CAP);
          if (r == -1) { wasCapped = true; break; }
          if (r == 0) { frozenCnt++; break; }
        }
        if (wasCapped) { capped++; continue; }
        if (frozenCnt > 0) frozenG++;
        else {
          candidates++;
          lock_guard<mutex> lk(outMtx);
          printf("ALL_UNFROZEN_CANDIDATE q=%d g6=%s\n", q, g6encode(h).c_str());
          fflush(stdout);
        }
      }
    };
    vector<thread> th;
    for (int t = 0; t < nthreads; t++) th.emplace_back(worker, t);
    for (auto& t : th) t.join();
    printf("mode=sample q=%d samples=%lld frozen=%lld capped=%lld rejected=%lld CANDIDATES=%lld\n",
           q, samples, frozenG.load(), capped.load(), rejected.load(), candidates.load());
    return 0;
  }
  if (mode == "hill") {
    int seconds = argc > 3 ? atoi(argv[3]) : 300;
    uint64_t seed = argc > 4 ? strtoull(argv[4], nullptr, 10) : 944;
    int nthreads = argc > 5 ? atoi(argv[5]) : 32;
    atomic<int> globalBest(1000);
    atomic<long long> totalMoves(0), restarts(0);
    atomic<bool> found(false);
    mutex outMtx;
    auto deadline = chrono::steady_clock::now() + chrono::seconds(seconds);
    auto worker = [&](int tid) {
      mt19937_64 rng(seed * 31337ULL + tid);
      while (chrono::steady_clock::now() < deadline && !found.load()) {
        G c; vector<int> defAv, defBv;
        if (!buildCross(q, rng, false, 60LL * (6 * q - 6), c, defAv, defBv)) continue;
        restarts++;
        int defA[6], defB[6];
        for (int t = 0; t < 6; t++) { defA[t] = defAv[t]; defB[t] = defBv[t]; }
        int selA = 0xF, selB = 0x3;
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
            if (unfrozenCapped(h, x, CAP) != 1) fr++;
          }
          return fr;
        };
        int cur = objective(c, selA, selB);
        int stale = 0;
        const int STALE_LIMIT = 3000;
        while (chrono::steady_clock::now() < deadline && !found.load() && stale < STALE_LIMIT) {
          totalMoves++;
          if (rng() % 100 < 85) {
            int a1 = rng() % q, a2 = rng() % q;
            if (a1 == a2) { stale++; continue; }
            uint64_t n1 = c.adj[a1], n2 = c.adj[a2];
            if (!n1 || !n2) { stale++; continue; }
            int k1 = rng() % __builtin_popcountll(n1), k2 = rng() % __builtin_popcountll(n2);
            uint64_t t1 = n1, t2 = n2;
            while (k1--) t1 &= t1 - 1;
            int b1 = __builtin_ctzll(t1);
            while (k2--) t2 &= t2 - 1;
            int b2 = __builtin_ctzll(t2);
            if (b1 == b2 || c.has(a1, b2) || c.has(a2, b1)) { stale++; continue; }
            c.del(a1, b1); c.del(a2, b2); c.add(a1, b2); c.add(a2, b1);
            if (!connectedG(c)) { c.del(a1, b2); c.del(a2, b1); c.add(a1, b1); c.add(a2, b2); stale++; continue; }
            int nv = objective(c, selA, selB);
            if (nv <= cur) { if (nv < cur) stale = 0; else stale++; cur = nv; }
            else { c.del(a1, b2); c.del(a2, b1); c.add(a1, b1); c.add(a2, b2); stale++; }
          } else {
            int sa = 0, sb = 0;
            while (__builtin_popcount(sa) != 4) sa = rng() % 64;
            while (__builtin_popcount(sb) != 2) sb = rng() % 64;
            int nv = objective(c, sa, sb);
            if (nv <= cur) { if (nv < cur) stale = 0; else stale++; cur = nv; selA = sa; selB = sb; }
            else stale++;
          }
          int gb = globalBest.load();
          while (cur < gb && !globalBest.compare_exchange_weak(gb, cur)) {}
          if (cur <= 2) {
            G h; buildH(c, selA, selB, h);
            lock_guard<mutex> lk(outMtx);
            printf("LOW frozen=%d q=%d g6=%s\n", cur, q, g6encode(h).c_str());
            fflush(stdout);
            if (cur == 0) found = true;
          }
        }
      }
    };
    vector<thread> th;
    for (int t = 0; t < nthreads; t++) th.emplace_back(worker, t);
    for (auto& t : th) t.join();
    printf("mode=hill q=%d time=%ds moves=%lld restarts=%lld GLOBAL_MIN_FROZEN=%d found0=%d\n",
           q, seconds, totalMoves.load(), restarts.load(), globalBest.load(), found.load() ? 1 : 0);
    return 0;
  }
  fprintf(stderr, "unknown mode\n");
  return 1;
}
