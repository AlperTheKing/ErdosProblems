// Invariant probe for the all-singleton freezing law: for random sparse
// candidates H = C + v (same generator as g3_random.cpp), pick full vertices x
// and determine WHICH colour-count multisets {c0,c1,c2} (c0+c1+c2=6, sorted
// descending) are achievable as N(x) colour counts over proper 3-colourings of
// H - x. Aggregates an achievability profile per vertex type
// (A-side / B-side / apex v). If exactly the multisets with max >= 3 are
// achievable, the freezing law is a "majority lemma".
// usage: g3_counts.exe q samples seed [threads]
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

// achievability of EXACT ordered target counts (t0,t1,t2) on N(v) over proper
// 3-colourings of G - v. No colour-symmetry fix (targets break symmetry).
static bool achievable(const G& g, int v, const int tgt[3], long long cap) {
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
    if (++nodes > cap) return false;          // cap: treat as unachievable (report caps separately if needed)
    if (pos == m) return true;
    int x = idx[pos]; bool adv = false;
    for (int c = tryc[pos]; c < 3; c++) {
      if (pos < nN && cnt[c] >= tgt[c]) continue;   // exact-target pruning
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
  return false;
}

// multiset achievable: try ordered targets over distinct permutations
static bool multisetAchievable(const G& g, int v, int a, int b, int c, long long cap) {
  int vals[3] = {a, b, c};
  sort(vals, vals + 3);
  do {
    if (achievable(g, v, vals, cap)) return true;
  } while (next_permutation(vals, vals + 3));
  return false;
}

static const int NMS = 7;
static const int MS[NMS][3] = {{6,0,0},{5,1,0},{4,2,0},{4,1,1},{3,3,0},{3,2,1},{2,2,2}};

int main(int argc, char** argv) {
  int q = argc > 1 ? atoi(argv[1]) : 12;
  long long samples = argc > 2 ? atoll(argv[2]) : 200;
  uint64_t seed = argc > 3 ? strtoull(argv[3], nullptr, 10) : 944;
  int nthreads = argc > 4 ? atoi(argv[4]) : 32;
  const long long CAP = 50000000LL;
  // profile[type][multiset] = (achievable count, tested count); type 0=A,1=B,2=v
  atomic<long long> ach[3][NMS], tot[3][NMS];
  for (int t = 0; t < 3; t++) for (int s = 0; s < NMS; s++) { ach[t][s] = 0; tot[t][s] = 0; }
  atomic<long long> done(0);
  auto worker = [&](int tid) {
    mt19937_64 rng(seed * 7777ULL + tid);
    for (;;) {
      long long i = done.fetch_add(1);
      if (i >= samples) break;
      G c; c.n = 2 * q;
      memset(c.adj, 0, sizeof(c.adj));
      for (int a2 = 0; a2 < q; a2++)
        for (int j = 0; j < 6; j++) c.add(a2, q + (a2 + j) % q);
      int perm[64];
      for (int x = 0; x < q; x++) perm[x] = x;
      for (int x = q - 1; x > 0; x--) { int y = rng() % (x + 1); swap(perm[x], perm[y]); }
      vector<int> defA, defB;
      for (int t = 0; t < 6; t++) { int a2 = perm[t]; c.del(a2, q + a2); defA.push_back(a2); defB.push_back(q + a2); }
      long long swaps = 60LL * (6 * q - 6);
      for (long long s = 0; s < swaps; s++) {
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
      for (int x = 5; x > 0; x--) { int y = rng() % (x + 1); swap(defA[x], defA[y]); swap(defB[x], defB[y]); }
      G h = c; h.n = 2 * q + 1;
      int v = 2 * q;
      h.adj[v] = 0;
      for (int t = 0; t < 4; t++) h.add(v, defA[t]);
      for (int t = 0; t < 2; t++) h.add(v, defB[t]);
      // probe: one full A vertex (not adj v), one full B vertex (not adj v), and v
      int xa = -1, xb = -1;
      for (int x = 0; x < q; x++) if (h.deg(x) == 6 && !h.has(v, x)) { xa = x; break; }
      for (int x = q; x < 2 * q; x++) if (h.deg(x) == 6 && !h.has(v, x)) { xb = x; break; }
      int targets[3] = {xa, xb, v};
      for (int t = 0; t < 3; t++) {
        int x = targets[t];
        if (x < 0) continue;
        for (int s = 0; s < NMS; s++) {
          tot[t][s]++;
          if (multisetAchievable(h, x, MS[s][0], MS[s][1], MS[s][2], CAP)) ach[t][s]++;
        }
      }
    }
  };
  vector<thread> th;
  for (int t = 0; t < nthreads; t++) th.emplace_back(worker, t);
  for (auto& t : th) t.join();
  const char* tname[3] = {"A-full", "B-full", "apex-v"};
  printf("q=%d samples=%lld; achievability profile (achieved/tested):\n", q, samples);
  for (int t = 0; t < 3; t++) {
    printf("  %s :", tname[t]);
    for (int s = 0; s < NMS; s++)
      printf("  {%d%d%d}=%lld/%lld", MS[s][0], MS[s][1], MS[s][2], ach[t][s].load(), tot[t][s].load());
    printf("\n");
  }
  return 0;
}
