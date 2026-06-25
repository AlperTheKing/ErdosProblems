// Sparse-regime test of the (FK) all-singleton extreme (potential refutation).
// For large q the cross-graph is a SPARSE near-6-regular bipartite graph; the
// q<=8 exhaustive searches covered only the dense regime. Sample random
// candidates H = C + v and test whether EVERY full vertex is deletion-unfrozen.
// A single certified all-unfrozen H refutes (FK) as stated.
//
// Construction per sample:
//   C: bipartite A x B, |A|=|B|=q; start from the 6-regular circulant
//      a_i ~ b_{(i+j) mod q}, j=0..5; delete the j=0 edges (a_i, b_i) for a
//      random 6-subset I of indices => six degree-5 vertices per side
//      (deficiency pattern 1^6, total 6 per side); randomize by R double-edge
//      swaps (keep simple bipartite, degrees preserved); require connected.
//   v: adjacent to a random 4-subset of the six deg-5 A-vertices and a random
//      2-subset of the six deg-5 B-vertices. Then deficiency(H): 2 on A, 4 on
//      B, 0 at v; Delta(H)=6; H connected, 3-colourable (bipartite + apex).
//   Test: v and every degree-6 vertex must have a (2,2,2) deletion witness.
//   Witness search uses the census backtracker with a node cap: witness found
//   -> unfrozen (certified); search exhausted -> FROZEN (graph dies); cap hit
//   -> inconclusive (graph discarded, counted separately).
// usage: g3_random.exe q samples seed [threads] [swapsFactor]
#include <cstdio>
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <random>
#include <thread>
#include <atomic>
#include <mutex>
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
  return seen == (g.n >= 32 ? 0xFFFFFFFFu : (1u << g.n) - 1);
}

// witness search: does H-v admit a proper 3-colouring with N(v) counts (2,2,2)?
// returns 1 = yes (unfrozen), 0 = no (frozen, exhausted), -1 = node cap hit.
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
  int q = argc > 1 ? atoi(argv[1]) : 12;
  long long samples = argc > 2 ? atoll(argv[2]) : 1000;
  uint64_t seed = argc > 3 ? strtoull(argv[3], nullptr, 10) : 944;
  int nthreads = argc > 4 ? atoi(argv[4]) : 32;
  int swapsFactor = argc > 5 ? atoi(argv[5]) : 60;
  const long long CAP = 200000000LL;     // witness-search node cap
  atomic<long long> done(0), frozenG(0), capped(0), disconnected(0), candidates(0);
  atomic<long long> minFrozenSeen(1000);
  mutex outMtx;
  auto worker = [&](int tid) {
    mt19937_64 rng(seed * 1000003ULL + tid);
    for (;;) {
      long long i = done.fetch_add(1);
      if (i >= samples) break;
      // build circulant minus matching
      G c; c.n = 2 * q;            // A = 0..q-1, B = q..2q-1
      memset(c.adj, 0, sizeof(c.adj));
      for (int a = 0; a < q; a++)
        for (int j = 0; j < 6; j++) c.add(a, q + (a + j) % q);
      // deficiency creation: matching mode (1^6 pattern) or general mode
      // (delete 6 random edges -> arbitrary deficiency patterns per side)
      vector<int> defA, defB;
      if (swapsFactor >= 0) {       // matching mode (default): random 6-subset I, delete (a_i, b_i)
        int perm[64];
        for (int x = 0; x < q; x++) perm[x] = x;
        for (int x = q - 1; x > 0; x--) { int y = rng() % (x + 1); swap(perm[x], perm[y]); }
        for (int t = 0; t < 6; t++) {
          int a = perm[t];
          c.del(a, q + a);
          defA.push_back(a); defB.push_back(q + a);
        }
      } else {                      // general mode (negative swapsFactor flag)
        for (int t = 0; t < 6; t++) {
          for (;;) {
            int a = rng() % q;
            uint32_t na = c.adj[a];
            if (!na) continue;
            int k = rng() % __builtin_popcount(na);
            uint32_t tt = na;
            while (k--) tt &= tt - 1;
            int b = __builtin_ctz(tt);
            c.del(a, b);
            break;
          }
        }
        for (int x = 0; x < q; x++) if (c.deg(x) < 6) defA.push_back(x);
        for (int x = q; x < 2 * q; x++) if (c.deg(x) < 6) defB.push_back(x);
        if ((int)defA.size() < 4 || (int)defB.size() < 2) { disconnected++; continue; }
        // pad shuffles below expect >= 6 slots only in matching mode; shuffle generically here
      }
      // randomize: double-edge swaps preserving bipartite degrees & simplicity
      long long swaps = (long long)(swapsFactor < 0 ? -swapsFactor : swapsFactor) * (6 * q - 6);
      for (long long s = 0; s < swaps; s++) {
        int a1 = rng() % q, a2 = rng() % q;
        if (a1 == a2) continue;
        uint32_t n1 = c.adj[a1], n2 = c.adj[a2];
        if (!n1 || !n2) continue;
        // pick random neighbours
        int k1 = rng() % __builtin_popcount(n1), k2 = rng() % __builtin_popcount(n2);
        int b1 = -1, b2 = -1; uint32_t t1 = n1, t2 = n2;
        while (k1--) t1 &= t1 - 1;
        b1 = __builtin_ctz(t1);
        while (k2--) t2 &= t2 - 1;
        b2 = __builtin_ctz(t2);
        if (b1 == b2 || c.has(a1, b2) || c.has(a2, b1)) continue;
        c.del(a1, b1); c.del(a2, b2); c.add(a1, b2); c.add(a2, b1);
      }
      if (!connectedG(c)) { disconnected++; continue; }
      // apex: 4 of defA, 2 of defB (size-aware shuffles)
      for (int x = (int)defA.size() - 1; x > 0; x--) { int y = rng() % (x + 1); swap(defA[x], defA[y]); }
      for (int x = (int)defB.size() - 1; x > 0; x--) { int y = rng() % (x + 1); swap(defB[x], defB[y]); }
      G h = c; h.n = 2 * q + 1;
      int v = 2 * q;
      h.adj[v] = 0;
      for (int t = 0; t < 4; t++) h.add(v, defA[t]);
      for (int t = 0; t < 2; t++) h.add(v, defB[t]);
      // test all full vertices
      int frozenCnt = 0; bool wasCapped = false;
      for (int x = 0; x <= 2 * q; x++) {
        if (h.deg(x) != 6) continue;
        int r = unfrozenCapped(h, x, CAP);
        if (r == -1) { wasCapped = true; break; }
        if (r == 0) { frozenCnt++; if (frozenCnt >= 1) break; }   // one frozen kills
      }
      if (wasCapped) { capped++; continue; }
      if (frozenCnt > 0) {
        frozenG++;
        long long cur = minFrozenSeen.load();
        while (frozenCnt < cur && !minFrozenSeen.compare_exchange_weak(cur, frozenCnt)) {}
      } else {
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
  printf("q=%d samples=%lld frozen=%lld capped=%lld disconnected=%lld CANDIDATES=%lld\n",
         q, samples, frozenG.load(), capped.load(), disconnected.load(), candidates.load());
  return 0;
}
